from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Allow frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

class Query(BaseModel):
    session_id: str
    query: str
    approved: bool

@app.post("/run")  # ✅ MUST BE POST
async def run_agent(q: Query):

    async def stream():
        async for chunk in llm.astream(q.query):
            yield chunk.content

    return StreamingResponse(stream(), media_type="text/plain")
