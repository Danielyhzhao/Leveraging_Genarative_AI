# parsers.py
# Output Parsers with Validation

import re
import ast


def parse_llm1_output(output: str) -> tuple[str, str]:
    """Parse LLM-1 output; validate structure and content."""
    issues_match = re.search(r"ISSUES:\n(.*?)\n\nTESTS:", output, re.DOTALL)
    tests_match = re.search(r"TESTS:\n(.*)", output, re.DOTALL)

    if not issues_match or not tests_match:
        raise ValueError("LLM-1 output not in required format.")

    issues = issues_match.group(1).strip()
    tests = tests_match.group(1).strip()

    # Validate issues: Must have line numbers
    if not re.search(r"- Line \d+.*:", issues):
        raise ValueError("Issues must include line numbers.")

    # Validate tests: Must be valid Python
    try:
        ast.parse(tests)
    except SyntaxError as e:
        raise ValueError(f"Generated tests not valid Python: {e}")

    return issues, tests


def parse_llm2_output(output: str) -> tuple[str, str]:
    """Parse LLM-2 output; validate structure."""
    suggestions_match = re.search(r"SUGGESTIONS:\n(.*?)\n\nREFLECTIONS:", output, re.DOTALL)
    reflections_match = re.search(r"REFLECTIONS:\n(.*)", output, re.DOTALL)

    if not suggestions_match or not reflections_match:
        raise ValueError("LLM-2 output not in required format.")

    suggestions = suggestions_match.group(1).strip()
    reflections = reflections_match.group(1).strip()

    return suggestions, reflections