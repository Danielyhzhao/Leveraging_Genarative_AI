# llms.py
# Direct LLM Calls (refactored)
#
# 公共契约完全保留:
#   - llm1_direct_call(code, problem_desc) -> str
#   - llm2_direct_call(code, problem_desc, issues, failures) -> str
# 内部改为委托给可插拔 backend(offline 规则引擎 或 真实 API),
# 返回文本格式与原始一致,因此 pipeline.py / parsers.py 无需改动。

from llm_backends import get_backend


def llm1_direct_call(code: str, problem_desc: str) -> str:
    """Direct call to LLM-1 with prompt engineering (PDF p.10-11)."""
    return get_backend().llm1_text(code, problem_desc)


def llm2_direct_call(code: str, problem_desc: str, issues: str, failures: str) -> str:
    """Direct call to LLM-2 (PDF p.13)."""
    return get_backend().llm2_text(code, problem_desc, issues, failures)
