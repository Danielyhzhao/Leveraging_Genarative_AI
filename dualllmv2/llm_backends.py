# llm_backends.py
# Pluggable LLM backends (refactored core)
#
# 设计目标:把"LLM 调用"这层从 pipeline 中解耦,提供两种实现:
#   - APIBackend   : 真实调用 DeepSeek(两个 LLM 均用,进行对抗式分析;保留原 prompts 与格式)
#   - RuleEngineBackend: 离线规则引擎,无需任何 API key 即可运行,
#                        用于本地调试与网页演示。
#
# 两个 backend 都返回与原始相同的纯文本格式:
#   llm1_text -> "ISSUES:\n...\n\nTESTS:\n..."
#   llm2_text -> "SUGGESTIONS:\n...\n\nREFLECTIONS:\n..."
# 因此 pipeline.py 与 parsers.py 完全无需改动。
#
# 本次改进(相对初版):
#   * RuleEngineBackend.llm1 现在能产出"多条、分维度"的 ISSUES:
#       - 静态启发式扩展到 8+ 类(裸 except / 宽异常 / 死循环 / float== /
#         可变默认参数 / 递归缺基线 / 部分路径无返回 / 二次复杂度隐患)
#       - 无结构性问题时,给出 4 条"分析型"建议(边界覆盖 / 基线初始化 /
#         复杂度 / 返回值一致性),而不是 1 句兜底。
#   * 测试用例(oracle)题库从 1 类扩展到 6+ 类常见算法(two sum / palindrome /
#     anagram / LCS / reverse int / climb stairs 等),每类生成 5~7 个边界+通用用例。
#   * 对未注册 oracle 的题目,智能通用回退会按参数名推断类型,生成多个
#     "属性/鲁棒性"测试(确定性、多样输入不崩溃),而非单个占位测试。

import ast
import re
import random
import time
from typing import Optional, Callable, Tuple, List

import config


# ---------------------------------------------------------------------------
# 离线规则引擎:参考解(oracle)注册表
# 针对常见问题内置参考答案,用于在离线模式下生成"有正确答案"的测试用例。
# 当学生代码存在 bug 时,oracle 计算出的 expected 与错误输出不同 -> 测试失败
# -> 触发 LLM-2 阶段,从而完整演示双 LLM 流程。
# ---------------------------------------------------------------------------

def _levenshtein(a: str, b: str) -> int:
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[m][n]


def _ref_twosum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i
    return []


def _ref_palindrome(s):
    return s == s[::-1]


def _ref_anagram(a, b):
    return sorted(a) == sorted(b)


def _ref_lcs(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = dp[i - 1][j - 1] + 1 if a[i - 1] == b[j - 1] else max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


def _ref_reverse(x):
    sign = -1 if x < 0 else 1
    r = int(str(abs(x))[::-1])
    return sign * r if -(2 ** 31) <= sign * r < 2 ** 31 else 0


def _ref_climb(n):
    if n <= 1:
        return 1
    a, b = 1, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


# ---- 用例生成器:每个返回 [(args_tuple, reason), ...] ----

def _cases_str2():
    samples = [
        ("", ""), ("", "a"), ("a", ""), ("a", "a"), ("abc", "abc"),
        ("kitten", "sitting"), ("horse", "ros"), ("intention", "execution"),
        ("", "abc"), ("abc", ""), ("sunday", "saturday"), ("distance", "instinct"),
    ]
    out = []
    for a, b in samples:
        out.append(((a, b), _reason(a, b)))
    return out


def _cases_str1():
    return [
        (("",), "empty string -> True"),
        (("a",), "single char -> True"),
        (("aba",), "odd-length palindrome -> True"),
        (("abba",), "even-length palindrome -> True"),
        (("abc",), "non-palindrome -> False"),
        (("racecar",), "long palindrome -> True"),
        (("abca",), "near-miss -> False"),
    ]


def _cases_anagram():
    return [
        (("", ""), "both empty -> True"),
        (("a", "a"), "single same -> True"),
        (("anagram", "nagaram"), "rearranged -> True"),
        (("rat", "car"), "different letters -> False"),
        (("a", "b"), "single diff -> False"),
        (("listen", "silent"), "anagram -> True"),
    ]


def _cases_lcs():
    return [
        (("", ""), "both empty -> 0"),
        (("abc", "abc"), "identical -> 3"),
        (("abc", "def"), "no common -> 0"),
        (("abcde", "ace"), "subsequence -> 3"),
        (("abc", "acb"), "crossing -> 2"),
        (("AGGTAB", "GXTXAYB"), "classic -> 4"),
    ]


def _cases_twosum():
    return [
        (([2, 7, 11, 15], 9), "classic -> [0,1]"),
        (([3, 2, 4], 6), "two distinct -> [1,2]"),
        (([3, 3], 6), "duplicate values -> [0,1]"),
        (([1], 2), "single element -> no solution []"),
        (([], 0), "empty array -> []"),
        (([0, 4, 3, 0], 0), "zeros as target -> [0,3]"),
    ]


def _cases_reverse():
    return [
        ((123,), "positive -> 321"),
        ((-123,), "negative -> -321"),
        ((120,), "trailing zero -> 21"),
        ((0,), "zero -> 0"),
        ((1534236469,), "overflow -> 0"),
    ]


def _cases_climb():
    return [
        ((1,), "n=1 -> 1"),
        ((2,), "n=2 -> 2"),
        ((3,), "n=3 -> 3"),
        ((5,), "n=5 -> 8"),
        ((10,), "n=10 -> 89"),
    ]


# 以方法名(小写,去非字母)为键 -> (oracle, 用例生成器)
_ORACLES: dict = {
    "mindistance": (_levenshtein, _cases_str2),
    "editdistance": (_levenshtein, _cases_str2),
    "levenshtein": (_levenshtein, _cases_str2),
    "twosum": (_ref_twosum, _cases_twosum),
    "twosumii": (_ref_twosum, _cases_twosum),
    "ispalindrome": (_ref_palindrome, _cases_str1),
    "isvalidpalindrome": (_ref_palindrome, _cases_str1),
    "validpalindrome": (_ref_palindrome, _cases_str1),
    "isanagram": (_ref_anagram, _cases_anagram),
    "validanagram": (_ref_anagram, _cases_anagram),
    "longestcommonsubsequence": (_ref_lcs, _cases_lcs),
    "reverse": (_ref_reverse, _cases_reverse),
    "reverseint": (_ref_reverse, _cases_reverse),
    "climbstairs": (_ref_climb, _cases_climb),
    "climbstair": (_ref_climb, _cases_climb),
}

# 以问题描述关键词为键
_ORACLE_KEYWORDS: dict = {
    "edit distance": (_levenshtein, _cases_str2),
    "levenshtein": (_levenshtein, _cases_str2),
    "two sum": (_ref_twosum, _cases_twosum),
    "palindrome": (_ref_palindrome, _cases_str1),
    "anagram": (_ref_anagram, _cases_anagram),
    "longest common subsequence": (_ref_lcs, _cases_lcs),
    "reverse integer": (_ref_reverse, _cases_reverse),
    "climb stairs": (_ref_climb, _cases_climb),
}


def _reason(a: str, b: str) -> str:
    if a == "" or b == "":
        return "empty-string boundary"
    if a == b:
        return "identical strings -> distance 0"
    if len(a) == 1 or len(b) == 1:
        return "single-character boundary"
    return "general case"


def _extract_callable(code: str):
    """从代码 AST 提取首个可调用单元:优先类方法,其次顶层函数。"""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [m for m in node.body if isinstance(m, ast.FunctionDef) and not m.name.startswith("_")]
            if methods:
                method = methods[0]
                args = [a.arg for a in method.args.args if a.arg != "self"]
                return {"class_name": node.name, "method_name": method.name, "args": args, "lineno": method.lineno}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
            args = [a.arg for a in node.args.args]
            return {"class_name": None, "method_name": node.name, "args": args, "lineno": node.lineno}
    return None


def _pick_oracle(callable_meta, problem_desc: str):
    """返回 (oracle, case_gen) 或 None。"""
    if callable_meta:
        pick = _ORACLES.get(_norm(callable_meta["method_name"]))
        if pick:
            return pick
    low = problem_desc.lower()
    for kw, pick in _ORACLE_KEYWORDS.items():
        if kw in low:
            return pick
    return None


def _norm(name: str) -> str:
    return re.sub(r"[^a-z]", "", name.lower())


# ---------------------------------------------------------------------------
# AST 启发式:生成 ISSUES(多条、分维度)
# ---------------------------------------------------------------------------

def _has_guard(node: ast.AST) -> bool:
    """递归函数是否含有基线/终止保护(if / assert / 常量返回)。"""
    for n in ast.walk(node):
        if isinstance(n, (ast.If, ast.Assert)):
            return True
        if isinstance(n, ast.Return) and isinstance(n.value, ast.Constant):
            return True
    return False


def _ends_with_return(node: ast.FunctionDef) -> bool:
    body = node.body
    if not body:
        return False
    last = body[-1]
    if isinstance(last, ast.Return):
        return True
    if isinstance(last, ast.If):
        return _ends_with_return(last) and (last.orelse and _ends_with_return(last.orelse[-1]) if last.orelse else False)
    return False


def _may_miss_return(node: ast.FunctionDef) -> bool:
    has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
    if not has_return:
        return False
    return not _ends_with_return(node)


def _is_dp(node: ast.FunctionDef) -> bool:
    """函数是否为 DP 表格递推(如 dp[i][j] = ...),属正当的二维结构。"""
    for n in ast.walk(node):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Subscript):
                    return True
    return False


def _has_quadratic_hint(node: ast.FunctionDef) -> bool:
    # DP 表格构建属正当的二维递推,不算 O(n^2) 隐患
    if _is_dp(node):
        return False
    fors = [n for n in ast.walk(node) if isinstance(n, ast.For)]
    if len(fors) >= 2:
        return True
    for f in fors:
        for c in ast.walk(f):
            if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr in ("index", "find", "count"):
                return True
    return False


def _heuristic_issues(code: str) -> list:
    issues: list = []
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [f"- Line {getattr(e, 'lineno', 1)}: Code could not be parsed ({getattr(e, 'msg', 'syntax error')}); fix syntax before analysis."]

    for node in ast.walk(tree):
        # 过宽的 except
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                issues.append(f"- Line {node.lineno}: Avoid bare `except:`; catch specific exceptions to avoid hiding real errors.")
            elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
                issues.append(f"- Line {node.lineno}: Catching broad `Exception` may mask logic errors; narrow the exception type where possible.")
        # while 循环可能无进展
        if isinstance(node, ast.While):
            assigned = set()
            for n in ast.walk(node):
                if isinstance(n, ast.Assign):
                    for t in n.targets:
                        for tgt in (t.elts if isinstance(t, (ast.Tuple, ast.List)) else [t]):
                            if isinstance(tgt, ast.Name):
                                assigned.add(tgt.id)
            cond = set()
            for n in ast.walk(node.test):
                if isinstance(n, ast.Name):
                    cond.add(n.id)
            if cond and not (cond & assigned):
                issues.append(f"- Line {node.lineno}: `while` loop condition uses variables that are never reassigned in the body; risk of infinite loop.")
        # 浮点数相等比较
        if isinstance(node, ast.Compare) and any(isinstance(op, ast.Eq) for op in node.ops):
            for v in node.comparators + [node.left]:
                if isinstance(v, ast.Constant) and isinstance(v.value, float):
                    issues.append(f"- Line {node.lineno}: Avoid `==` on floats; use math.isclose() to handle precision.")

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # 可变默认参数
            for d in node.args.defaults:
                if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                    issues.append(f"- Line {node.lineno}: Mutable default argument may cause shared-state bugs; use None then initialize inside.")
            # 递归缺基线
            calls_self = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == node.name for n in ast.walk(node))
            if calls_self and not _has_guard(node):
                issues.append(f"- Line {node.lineno}: Recursive function `{node.name}` may lack a base case; ensure a terminating condition returns before the recursive call.")
            # 部分路径无返回
            if _may_miss_return(node):
                issues.append(f"- Line {node.lineno}: Function `{node.name}` has code paths that may not return a value; ensure all branches (including edge cases) return.")
            # 二次复杂度隐患
            if _has_quadratic_hint(node):
                issues.append(f"- Line {node.lineno}: Nested loops or `list.index` inside a loop can be O(n^2); consider a hash map / two-pointer approach for better efficiency.")

    return issues


def _analytical_issues() -> list:
    """无结构性问题时,给出多条"分析型"建议,模拟 LLM-1 的深度审查。"""
    return [
        "- Line 1: No obvious structural issues detected by static analysis. Verify edge-case coverage: empty/None inputs, single-element, and maximum-size inputs.",
        "- Line 1: Confirm the recurrence / base cases are initialized correctly for boundary inputs (e.g., length-0 cases).",
        "- Line 1: Consider the time/space complexity of your approach against the problem constraints; a brute-force solution may time out on large inputs.",
        "- Line 1: Ensure every code path returns a value of the expected type, including early-exit branches.",
    ]


# ---------------------------------------------------------------------------
# Base backend
# ---------------------------------------------------------------------------

class BaseBackend:
    def __init__(self):
        # 记录最近一次 LLM 调用的元数据(角色/模型/发送给模型的 prompt/返回/耗时),
        # 供 pipeline 透传到网页,用于直观证明"是否真的调用了 API"以及耗时。
        self.last_call = None

    def llm1_text(self, code: str, problem_desc: str) -> str:
        raise NotImplementedError

    def llm2_text(self, code: str, problem_desc: str, issues: str, failures: str) -> str:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Offline rule-engine backend
# ---------------------------------------------------------------------------

class RuleEngineBackend(BaseBackend):
    """无需任何 API key 的确定性后端,用于本地调试与网页演示。"""

    def __init__(self):
        super().__init__()

    def llm1_text(self, code: str, problem_desc: str) -> str:
        t0 = time.time()
        issues = _heuristic_issues(code)
        issues_text = "\n".join(issues) if issues else "\n".join(_analytical_issues())
        tests_text = self._generate_tests(code, problem_desc)
        text = f"ISSUES:\n{issues_text}\n\nTESTS:\n{tests_text}"
        self.last_call = {
            "role": "LLM-1 (离线规则引擎)",
            "model": "offline",
            "prompt": "(离线规则引擎:静态启发式 + oracle 题库,无网络调用)",
            "response": text,
            "elapsed_ms": (time.time() - t0) * 1000,
        }
        return text

    # ---- 测试生成 ----

    def _call_expr(self, meta, args: tuple) -> str:
        args_repr = ", ".join(repr(a) for a in args)
        if meta and meta.get("class_name"):
            return f'{meta["class_name"]}().{meta["method_name"]}({args_repr})'
        return f'{meta["method_name"]}({args_repr})'

    def _format_oracle_tests(self, meta, oracle, case_gen) -> str:
        lines = []
        for args, reason in case_gen():
            try:
                expected = oracle(*args)
            except Exception:
                continue
            lines.append(f'self.assertEqual({self._call_expr(meta, args)}, {repr(expected)})  # Reason: {reason}')
        if not lines:
            lines.append("self.assertTrue(True)  # No reference cases generated")
        return "\n".join(lines)

    def _generate_tests(self, code: str, problem_desc: str) -> str:
        meta = _extract_callable(code)
        pick = _pick_oracle(meta, problem_desc) if meta else None
        if pick:
            return self._format_oracle_tests(meta, pick[0], pick[1])
        return self._generic_tests(meta, problem_desc)

    def _generic_tests(self, meta, problem_desc: str) -> str:
        if not meta:
            return ("# Could not locate a callable (class method or top-level function) in the code.\n"
                    "self.assertTrue(True)  # Placeholder: add structure to enable analysis")
        args = meta["args"]

        def sample_value(name: str, idx: int):
            low = name.lower()
            if any(k in low for k in ("word", "text", "string")) and "nums" not in low and low not in ("n",):
                return ["", "a", "aba", "hello"][idx % 4]
            if any(k in low for k in ("nums", "arr", "list", "array", "vec")):
                return [[], [1], [1, 2, 3], [3, 2, 1]][idx % 4]
            if any(k in low for k in ("target", "k", "val", "num", "idx", "index", "n")) and "name" not in low and "word" not in low:
                return [0, 1, -1, 7][idx % 4]
            return [0, "", [], "x"][idx % 4]

        lines = [
            "# No reference solution registered for this problem; the following are property/robustness tests.",
            "# They check determinism and that the function runs on varied inputs (not correctness vs an oracle).",
            "# Tip: register an oracle in llm_backends._ORACLES to enable assertion tests.",
        ]
        # 确定性 + 多样输入,生成多个测试
        variants = [
            tuple(sample_value(a, 0) for a in args),
            tuple(sample_value(a, 1) for a in args),
            tuple(sample_value(a, 2) for a in args),
            tuple(sample_value(a, 3) for a in args),
        ]
        seen = set()
        for i, vals in enumerate(variants, 1):
            key = repr(vals)
            if key in seen:
                continue
            seen.add(key)
            ce = self._call_expr(meta, vals)
            # 确定性:同输入两次调用结果应一致;若崩溃则记为失败(信息量更大)
            lines.append(f'self.assertEqual({ce}, {ce})  # Reason: determinism & runs on input variant {i}')
        if not seen:
            lines.append("self.assertTrue(True)  # No inputs generated")
        return "\n".join(lines)

    # ---- LLM-2 (离线) ----

    def llm2_text(self, code: str, problem_desc: str, issues: str, failures: str) -> str:
        t0 = time.time()
        suggestions = self._build_suggestions(issues, failures)
        reflections = self._build_reflections(failures)
        text = f"SUGGESTIONS:\n{suggestions}\n\nREFLECTIONS:\n{reflections}"
        self.last_call = {
            "role": "LLM-2 (离线规则引擎)",
            "model": "offline",
            "prompt": "(离线规则引擎:基于失败用例生成建议与反思,无网络调用)",
            "response": text,
            "elapsed_ms": (time.time() - t0) * 1000,
        }
        return text

    def _build_suggestions(self, issues: str, failures: str) -> str:
        lines = []
        lines.append("- Review the failing assertions above: compare your output to the expected value for each case.")
        if "empty" in (failures + issues).lower():
            lines.append("- Line 1: Add explicit handling for empty inputs (length 0) — DP base cases must initialize row/col 0 correctly.")
        if "index" in failures.lower() or "IndexError" in failures:
            lines.append("- Line 1: Check array/string indexing for off-by-one; ensure loops bound matches the DP table dimensions.")
        if "NoneType" in failures or "None" in failures:
            lines.append("- Line 1: Guard against None or uninitialized variables before use.")
        if "determinism" in failures.lower():
            lines.append("- Line 1: A function returning different results for identical inputs suggests hidden state or randomness; make it pure.")
        if len(lines) < 3:
            lines.append("- Trace the recurrence step by hand on a small example to locate where the count diverges from expected.")
            lines.append("- Add a print/assert on an intermediate value to inspect where the result first goes wrong.")
        return "\n".join(lines)

    def _build_reflections(self, failures: str) -> str:
        lines = [
            "- Why might your result differ from the expected value on these inputs?",
            "- Which edge case (empty / identical / single-char) breaks your logic first, and why?",
            "- If you re-ran the same input, would you get the same answer? What does that tell you about your approach?",
        ]
        if "empty" in failures.lower():
            lines.append("- How should an empty string be handled by the initialization of your DP table?")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Real API backend (preserves original prompts/format)
# ---------------------------------------------------------------------------

class APIBackend(BaseBackend):
    def __init__(self):
        super().__init__()

    def _invoke(self, llm, prompt: str, model: str = ""):
        from langchain_core.messages import HumanMessage
        t0 = time.time()
        try:
            resp = llm.invoke([HumanMessage(content=prompt)]).content
        except Exception as e:
            msg = str(e)
            if "402" in msg or "Insufficient Balance" in msg:
                raise RuntimeError(
                    "DeepSeek 账户余额不足(402 Insufficient Balance)。代码与 API Key 均无误——"
                    "请到 https://platform.deepseek.com 给账户充值后重试。"
                )
            if "401" in msg or "Authentication" in msg or "invalid" in msg.lower():
                raise RuntimeError(
                    "DeepSeek API Key 无效或未授权(401)。请检查 .env 中对应 LLM 的 Key 是否完整、正确。"
                )
            raise RuntimeError(f"调用 DeepSeek API 失败({model}):{msg}")
        elapsed = (time.time() - t0) * 1000
        return resp, elapsed

    def llm1_text(self, code: str, problem_desc: str) -> str:
        from prompts import llm1_prompt
        from langchain_core.messages import HumanMessage
        llm1, _ = config._ensure_llms()
        formatted = llm1_prompt.format(code=code, problem_desc=problem_desc)
        resp, elapsed = self._invoke(llm1, formatted, config.LLM1_MODEL)
        self.last_call = {
            "role": "LLM-1 (分析者/考官)",
            "model": config.LLM1_MODEL,
            "prompt": formatted,
            "response": resp,
            "elapsed_ms": elapsed,
        }
        return resp

    def llm2_text(self, code: str, problem_desc: str, issues: str, failures: str) -> str:
        from prompts import llm2_prompt
        from langchain_core.messages import HumanMessage
        _, llm2 = config._ensure_llms()
        formatted = llm2_prompt.format(code=code, problem_desc=problem_desc, issues=issues, failures=failures)
        resp, elapsed = self._invoke(llm2, formatted, config.LLM2_MODEL)
        self.last_call = {
            "role": "LLM-2 (对抗者/导师)",
            "model": config.LLM2_MODEL,
            "prompt": formatted,
            "response": resp,
            "elapsed_ms": elapsed,
        }
        return resp


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_backend_instance: Optional[BaseBackend] = None


def get_backend() -> BaseBackend:
    global _backend_instance
    if _backend_instance is not None:
        return _backend_instance
    if config.BACKEND_MODE == "api":
        _backend_instance = APIBackend()
    else:
        _backend_instance = RuleEngineBackend()
    return _backend_instance
