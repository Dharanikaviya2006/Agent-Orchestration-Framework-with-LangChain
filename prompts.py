from langchain.prompts import PromptTemplate

# Basic Prompt Template
basic_prompt = PromptTemplate(
    input_variables=["user_input"],
    template="""
You are a helpful AI assistant.

Answer the following question clearly and concisely:

Question: {user_input}

Answer:
"""
)

# Reasoning Prompt Template
reasoning_prompt = PromptTemplate(
    input_variables=["user_input"],
    template="""
You are an intelligent reasoning assistant.

Think step by step before answering.

Question: {user_input}

Step-by-step reasoning:
"""
)
