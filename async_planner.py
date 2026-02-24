async def planner_agent(state):
    llm = get_llm()
    prompt = f"Break down task: {state['user_input']}"
    response = await llm.ainvoke(prompt)
    return {"plan": response.content}
