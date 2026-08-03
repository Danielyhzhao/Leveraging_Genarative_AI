# pipeline.py
# Optimization Pipeline
#
# 公共契约完全保留:
#   dual_llm_pipeline(student_code, problem_desc, student_reflection="", max_iterations=3)
#       -> dict { "final", "history", "metrics", ["reflection_required"] }
# 仅增强:对 LLM 调用异常做了兜底,避免单次调用失败导致整条流水线崩溃;
#        并在 history 中附加每次 LLM 调用的元数据(角色/模型/prompt/返回/耗时)与测试耗时,
#        用于在网页上直观证明"是否真的调用了 API"。

import time

from utils import syntax_check, run_unittest, TestResult
from llms import llm1_direct_call, llm2_direct_call
from parsers import parse_llm1_output, parse_llm2_output
from metrics import OptimizationMetrics
from llm_backends import get_backend


def dual_llm_pipeline(student_code: str, problem_desc: str, student_reflection: str = "",
                      max_iterations: int = 3) -> dict:
    """
    Deterministic pipeline with ethical checks (PDF workflow).
    - Requires student_reflection for iterations >1 to enforce verification.
    - No auto-replacement; returns suggestions for manual revision.
    """
    current_code = student_code
    history = []
    metrics = OptimizationMetrics(problem_desc)  # Classify difficulty
    backend = get_backend()  # 同一实例(pipeline 与 llms 共用),用于读取调用元数据

    for iteration in range(max_iterations):
        if iteration > 0 and not student_reflection:
            return {"final": "Reflection required before next iteration.", "history": history,
                    "metrics": metrics.get_stats()}

        # Optional: Syntax check (auxiliary)
        # 注意:必须用精确前缀判断,避免 "No syntax errors." 中的 "error" 子串被误判。
        syntax_result = syntax_check(current_code)
        if syntax_result.lower().startswith("syntax error"):
            history.append({"iteration": iteration + 1, "syntax_error": syntax_result})
            return {"final": syntax_result, "history": history, "metrics": metrics.get_stats()}

        # Phase 1: LLM-1 direct call
        try:
            llm1_output = llm1_direct_call(current_code, problem_desc)
        except Exception as e:
            return {"final": f"LLM-1 call failed: {e}", "history": history,
                    "metrics": metrics.get_stats()}
        llm1_call = backend.last_call  # 捕获本次 LLM-1 调用的元数据(角色/模型/prompt/返回/耗时)
        try:
            issues, test_cases = parse_llm1_output(llm1_output)
        except ValueError as e:
            return {"final": f"LLM-1 output invalid: {e}", "history": history, "metrics": metrics.get_stats()}

        # Phase 2: Deterministic validation
        t_test = time.time()
        test_result = run_unittest(current_code, test_cases)
        test_ms = (time.time() - t_test) * 1000
        metrics.track_pass_rate(test_result)

        history.append({
            "iteration": iteration + 1,
            "issues": issues,
            "test_result": test_result.summary,
            "reflection_required": not test_result.passed,
            "llm1_call": llm1_call,
            "test_duration_ms": test_ms,
        })

        if test_result.passed:
            return {"final": "All logical issues resolved. Logic verified.", "history": history,
                    "metrics": metrics.get_stats()}

        # Phase 3: LLM-2 only if failed
        try:
            llm2_output = llm2_direct_call(current_code, problem_desc, issues, test_result.failures)
        except Exception as e:
            return {"final": f"LLM-2 call failed: {e}", "history": history,
                    "metrics": metrics.get_stats()}
        llm2_call = backend.last_call  # 捕获本次 LLM-2 调用的元数据
        try:
            suggestions, reflections = parse_llm2_output(llm2_output)
        except ValueError as e:
            return {"final": f"LLM-2 output invalid: {e}", "history": history, "metrics": metrics.get_stats()}

        history[-1]["suggestions"] = suggestions
        history[-1]["reflections"] = reflections
        history[-1]["llm2_call"] = llm2_call

        # Ethical: Require reflection for next iter
        return {
            "final": "Review suggestions and provide reflection to continue.",
            "history": history,
            "metrics": metrics.get_stats(),
            "reflection_required": True
        }

    return {"final": "Max iterations reached. Review history.", "history": history, "metrics": metrics.get_stats()}
