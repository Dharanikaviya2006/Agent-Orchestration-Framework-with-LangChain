import os
import json
import asyncio
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from tenacity import retry, stop_after_attempt, wait_exponential
import redis

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langgraph.graph import StateGraph
from duckduckgo_search import DDGS

load_dotenv()

# ---------------- CONFIG ----------------
app = FastAPI()
templates = Jinja2Templates(directory="templates")

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings()

engine = create_async_engine("sqlite+aiosqlite:///agent.db")

# ---------------- DATABASE ----------------

async def save_message(session_id, role, content):
    async with engine.begin() as conn:
        await conn.execute(
            text("INSERT INTO messages(session_id, role, content) VALUES(:s, :r, :c)"),
            {"s": session_id, "r": role, "c": content}
        )

# ---------------- RAG ----------------

def build_vector_store():
    docs = [
        Document(page_content="Tesla is a global EV leader."),
        Document(page_content="AI adoption is growing worldwide."),
        Document(page_content="Stock markets fluctuate daily.")
    ]
    return FAISS.from_documents(docs, embeddings)

def retrieve_context(vs, query):
    docs = vs.similarity_search(query, k=2)
    return "\n".join([d.page_content for d in docs])

# ---------------- RETRY ----------------

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
async def safe_llm(prompt):
    return await llm.ainvoke(prompt)

# ---------------- AGENTS ----------------

async def planner(state):
    response = await safe_llm(f"Break task into steps: {state['input']}")
    return {"plan": response.content}

async def human_node(state):
    if not state.get("approved"):
        raise Exception("Plan not approved by user")
    return {}

async def researcher(state):
    with DDGS() as ddgs:
        results = [r["body"] for r in ddgs.text(state["plan"], max_results=3)]
    web_data = "\n".join(results)

    context = retrieve_context(state["vector_store"], state["plan"])

    prompt = f"Context:\n{context}\nWeb:\n{web_data}\nSummarize."
    response = await safe_llm(prompt)

    return {"research": response.content}

async def reporter(state):
    prompt = f"""
    Task: {state['input']}
    Plan: {state['plan']}
    Research: {state['research']}
    Create final report.
    """
    return {"final": prompt}

# ---------------- GRAPH ----------------

workflow = StateGraph(dict)

workflow.add_node("planner", planner)
workflow.add_node("human", human_node)
workflow.add_node("researcher", researcher)
workflow.add_node("reporter", reporter)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "human")
workflow.add_edge("human", "researcher")
workflow.add_edge("researcher", "reporter")
workflow.set_finish_point("reporter")

graph = workflow.compile()

# ---------------- ROUTES ----------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class Query(BaseModel):
    session_id: str
    query: str
    approved: bool

@app.post("/run")
async def run_agent(q: Query):

    vs = build_vector_store()

    state = {
        "input": q.query,
        "plan": "",
        "research": "",
        "final": "",
        "approved": q.approved,
        "vector_store": vs
    }

    result = await graph.ainvoke(state)

    await save_message(q.session_id, "user", q.query)
    await save_message(q.session_id, "assistant", result["final"])

    async def stream():
        async for chunk in llm.astream(result["final"]):
            yield chunk.content

    return StreamingResponse(stream(), media_type="text/plain")
