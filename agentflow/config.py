# config.py
# Configuration and API Setup

import os

# Set API keys (replace with your actual keys)
os.environ["DEEPSEEK_API_KEY"] = "your-deepseek-api-key"
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

from langchain_openai import ChatOpenAI

# Primary LLM: DeepSeek as LLM-1
llm1 = ChatOpenAI(
    model="deepseek-coder",
    temperature=0.2,
    openai_api_key=os.environ.get("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com/v1",
)

# Secondary LLM: OpenAI as LLM-2
llm2 = ChatOpenAI(
    model="gpt-4o",
    temperature=0.1,
    openai_api_key=os.environ.get("OPENAI_API_KEY"),
)