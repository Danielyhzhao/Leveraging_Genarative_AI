# pipeline.py
# Optimization Pipeline

from utils import syntax_check, run_unittest, TestResult
from llms import llm1_direct_call, llm2_direct_call
from parsers import parse_llm1_output, parse_llm2_output
from metrics import OptimizationMetrics


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

    for iteration in range(max_iterations):
        if iteration > 0 and not student_reflection:
            return {"final": "Reflection required before next iteration.", "history": history,
                    "metrics": metrics.get_stats()}

        # Optional: Syntax check (auxiliary)
        syntax_result = syntax_check(current_code)
        if "error" in syntax_result.lower():
            history.append({"iteration": iteration + 1, "syntax_error": syntax_result})
            return {"final": syntax_result, "history": history, "metrics": metrics.get_stats()}

        # Phase 1: LLM-1 direct call
        llm1_output = llm1_direct_call(current_code, problem_desc)
        try:
            issues, test_cases = parse_llm1_output(llm1_output)
        except ValueError as e:
            return {"final": f"LLM-1 output invalid: {e}", "history": history, "metrics": metrics.get_stats()}

        # Phase 2: Deterministic validation
        test_result = run_unittest(current_code, test_cases)
        metrics.track_pass_rate(test_result)

        history.append({
            "iteration": iteration + 1,
            "issues": issues,
            "test_result": test_result.summary,
            "reflection_required": not test_result.passed
        })

        if test_result.passed:
            return {"final": "All logical issues resolved. Logic verified.", "history": history,
                    "metrics": metrics.get_stats()}

        # Phase 3: LLM-2 only if failed
        llm2_output = llm2_direct_call(current_code, problem_desc, issues, test_result.failures)
        try:
            suggestions, reflections = parse_llm2_output(llm2_output)
        except ValueError as e:
            return {"final": f"LLM-2 output invalid: {e}", "history": history, "metrics": metrics.get_stats()}

        history[-1]["suggestions"] = suggestions
        history[-1]["reflections"] = reflections

        # Ethical: Require reflection for next iter
        return {
            "final": "Review suggestions and provide reflection to continue.",
            "history": history,
            "metrics": metrics.get_stats(),
            "reflection_required": True
        }

    return {"final": "Max iterations reached. Review history.", "history": history, "metrics": metrics.get_stats()}