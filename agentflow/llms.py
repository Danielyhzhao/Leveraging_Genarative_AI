# llms.py
# Direct LLM Calls

from langchain_core.messages import HumanMessage
from prompts import llm1_prompt, llm2_prompt
from config import llm1, llm2

def llm1_direct_call(code: str, problem_desc: str) -> str:
    """Direct call to LLM-1 with prompt engineering (PDF p.10-11)."""
    formatted_prompt = llm1_prompt.format(code=code, problem_desc=problem_desc)
    response = llm1.invoke([HumanMessage(content=formatted_prompt)])
    return response.content

def llm2_direct_call(code: str, problem_desc: str, issues: str, failures: str) -> str:
    """Direct call to LLM-2 (PDF p.13)."""
    formatted_prompt = llm2_prompt.format(code=code, problem_desc=problem_desc, issues=issues, failures=failures)
    response = llm2.invoke([HumanMessage(content=formatted_prompt)])
    return response.content