# utils.py
# Deterministic Functions/Tools
#
# 该模块完全保留原始实现的公共契约:
#   - TestResult 数据类
#   - run_unittest(code, test_cases) -> TestResult
#   - syntax_check(code) -> str
# 仅在异常处理上做了少量健壮性增强,不改变任何输入输出结构。

import ast
import unittest
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import dataclass, field


@dataclass
class TestResult:
    passed: bool
    summary: str
    failures: str
    pass_rate: float


def run_unittest(code: str, test_cases: str) -> TestResult:
    """Deterministic test execution (PDF p.12).

    将学生代码与 LLM 生成的测试用例拼接为一个 unittest.TestCase,
    在隔离的全局命名空间中执行并返回结构化结果。输入/输出结构不变。
    """
    # 将每条 assert 生成为独立的 test 方法,使 unittest 能逐条计数与隔离失败
    # (原实现把所有 assert 放进单个 test_cases 方法,unittest 只计为 1 个测试,
    #  且首个 assert 失败后其余不再执行,会低估问题规模)。
    # 跳过空行与独立注释行(如规则引擎的说明性注释 / LLM 可能生成的注释),
    # 避免被误当成空方法体。
    test_lines = [
        ln for ln in test_cases.splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    methods_src = "\n".join(
        f"    def test_case_{idx}(self):\n        {ln}" for idx, ln in enumerate(test_lines)
    )
    test_class = f"""
import unittest

{code}

class TestCode(unittest.TestCase):
{methods_src}
"""
    f = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(f), redirect_stderr(err):
        try:
            exec_globals = {}
            exec(test_class, exec_globals)
            loader = unittest.TestLoader()
            suite = unittest.TestSuite()
            found = False
            for name, obj in exec_globals.items():
                if isinstance(obj, type) and issubclass(obj, unittest.TestCase):
                    suite.addTests(loader.loadTestsFromTestCase(obj))
                    found = True
            if not found:
                msg = "No test class could be built from provided code."
                return TestResult(False, msg, msg, 0.0)
            runner = unittest.TextTestRunner(stream=f, verbosity=2)
            result = runner.run(suite)
            output = f.getvalue() + err.getvalue()
            tests_run = result.testsRun
            failures_num = len(result.failures) + len(result.errors)
            passed = failures_num == 0
            pass_rate = (tests_run - failures_num) / tests_run if tests_run > 0 else 0.0
            summary = f"Tests: {tests_run}, Passed: {tests_run - failures_num}, Failed: {failures_num}"
            failures = "\n".join([str(fl) for fl in result.failures + result.errors])
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
