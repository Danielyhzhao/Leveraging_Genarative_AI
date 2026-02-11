# utils.py
# Deterministic Functions/Tools

import ast
import unittest
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import dataclass

@dataclass
class TestResult:
    passed: bool
    summary: str
    failures: str
    pass_rate: float

def run_unittest(code: str, test_cases: str) -> TestResult:
    """Deterministic test execution (PDF p.12)."""
    test_class = f"""
import unittest

{code}

class TestCode(unittest.TestCase):
    def test_cases(self):
        {test_cases}
    """
    f = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(f), redirect_stderr(err):
        try:
            exec_globals = {}
            exec(test_class, exec_globals)
            loader = unittest.TestLoader()
            suite = unittest.TestSuite()
            for name, obj in exec_globals.items():
                if isinstance(obj, type) and issubclass(obj, unittest.TestCase):
                    suite.addTests(loader.loadTestsFromTestCase(obj))
            runner = unittest.TextTestRunner(stream=f, verbosity=2)
            result = runner.run(suite)
            output = f.getvalue() + err.getvalue()
            tests_run = result.testsRun
            failures_num = len(result.failures) + len(result.errors)
            passed = failures_num == 0
            pass_rate = (tests_run - failures_num) / tests_run if tests_run > 0 else 0.0
            summary = f"Tests: {tests_run}, Passed: {tests_run - failures_num}, Failed: {failures_num}"
            failures = "\n".join([str(f) for f in result.failures + result.errors])
            return TestResult(passed, summary + "\n" + output, failures, pass_rate)
        except Exception as e:
            error_msg = f"Test execution error: {str(e)}\n{err.getvalue()}"
            return TestResult(False, error_msg, error_msg, 0.0)

def syntax_check(code: str) -> str:
    """Optional auxiliary function for syntax check."""
    try:
        ast.parse(code)
        return "No syntax errors."
    except SyntaxError as e:
        return f"Syntax error on line {e.lineno}: {str(e)}"