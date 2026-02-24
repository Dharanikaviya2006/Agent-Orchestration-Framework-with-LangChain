from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from dotenv import load_dotenv
import os

from prompts import basic_prompt, reasoning_prompt

load_dotenv()

# -------------------------
# 1. LLM Setup
# -------------------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5
)

# -------------------------
# 2. LLM Chain (Prompt + LLM)
# -------------------------
basic_chain = LLMChain(
    llm=llm,
    prompt=basic_prompt
)

reasoning_chain = LLMChain(
    llm=llm,
    prompt=reasoning_prompt
)

# -------------------------
# 3. Custom Tool Example
# -------------------------
def calculator_tool(query: str) -> str:
    """Useful for simple math calculations."""
    try:
        return str(eval(query))
    except:
        return "Invalid mathematical expression."

calculator = Tool(
    name="Calculator",
    func=calculator_tool,
    description="Performs basic math calculations."
)

# -------------------------
# 4. Agent Initialization
# -------------------------
agent = initialize_agent(
    tools=[calculator],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# -------------------------
# 5. Public Functions
# -------------------------
def run_basic_chain(user_input: str):
    return basic_chain.run(user_input=user_input)

def run_reasoning_chain(user_input: str):
    return reasoning_chain.run(user_input=user_input)

def run_agent(user_input: str):
    return agent.run(user_input)
