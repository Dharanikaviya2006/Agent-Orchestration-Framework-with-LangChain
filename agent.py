from config import get_llm
from rag.vector_store import retrieve_context
from tools.search_tool import web_search

llm = get_llm()

async def researcher_agent(state):
    query = state["plan"]

    web_data = web_search.invoke(query)

    vector_store = state["vector_store"]
    context = retrieve_context(vector_store, query)

    prompt = f"""
    Context from vector DB:
    {context}

    Live Web Data:
    {web_data}

    Provide refined research summary.
    """

    response = await llm.ainvoke(prompt)

    return {"research_data": response.content}
