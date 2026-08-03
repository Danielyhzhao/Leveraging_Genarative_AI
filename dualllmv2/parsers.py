# parsers.py
# Output Parsers with Validation
#
# 公共契约完全保留:
#   - parse_llm1_output(output) -> (issues, tests)
#   - parse_llm2_output(output) -> (suggestions, reflections)
# 增强:对真实 LLM 返回的强容错 ——
#   * 去除 markdown 代码块围栏;
#   * 兼容多种标题写法(ISSUES / TESTS / TEST CASES / SUGGESTIONS / REFLECTIONS 等);
#   * 测试用例段允许附带前言/注释,必要时只抽取 assert 行;
#   * "Line X" 行号不再硬性要求;
#   目的:避免 DeepSeek 偶发格式偏差导致整条流水线崩溃。

import re
import ast


def _strip_fences(text: str) -> str:
    """去掉 ```lang ... ``` 或 ``` ... ``` 代码块围栏,保留内部内容。"""
    if not text:
        return text
    text = re.sub(r"```[a-zA-Z0-9_]*\s*", "", text)
    text = text.replace("```", "")
    return text


def _extract_assert_lines(text: str):
    """从文本中抽取 assert / self.xxx 语句行,拼成合法 Python;失败返回 None。"""
    kept = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if re.search(r"self\.assert|assert\s|assertEqual|assertTrue|assertFalse", s) or s.startswith("self."):
            # 去掉行尾注释(以 # 开头),避免把注释误当代码
            s = re.sub(r"\s*#.*$", "", s).strip()
            kept.append(s)
    if kept:
        try:
            ast.parse("\n".join(kept))
            return "\n".join(kept)
        except SyntaxError:
            return None
    return None


def _find_section(output: str, labels: list) -> str:
    """按候选标题(大小写不敏感)查找区间,捕获到下一个 '大写标题:' 或文本末尾为止。"""
    flags = re.IGNORECASE | re.DOTALL
    alt = "|".join(re.escape(lbl) for lbl in labels)
    # 捕获 标题: 之后,直到出现另一行 "XXXX:"(新区块)或结尾
    pattern = rf"(?:^|\n)(?:{alt})\s*[:\-]\s*(.*?)(?=\n[A-Z][A-Z_ ]*[:\-]|\Z)"
    m = re.search(pattern, output, flags)
    if m and m.group(1).strip():
        return m.group(1).strip()
    return ""


def parse_llm1_output(output: str) -> tuple[str, str]:
    """Parse LLM-1 output; validate structure and content."""
    if not output or not output.strip():
        raise ValueError("LLM-1 output is empty.")

    # 1) 尝试按标题提取 ISSUES
    issues_raw = _find_section(output, ["ISSUES", "ISSUE", "PROBLEMS", "FINDINGS"])
    if not issues_raw:
        issues_raw = _strip_fences(output)
    issues = _strip_fences(issues_raw).strip()
    if not issues:
        issues = "- (未列出具体行号) Review the code for logical correctness and edge cases."

    # 2) 尝试按标题提取 TESTS;多标签兼容
    tests_raw = _find_section(output, ["TESTS", "TEST CASES", "TEST CASE", "TEST", "EXAMPLES", "TESTS:"])
    tests = None
    if tests_raw:
        tests = _extract_assert_lines(tests_raw)
    if not tests:
        # 最后手段:扫描整段输出里的 assert 行
        tests = _extract_assert_lines(output)
    if not tests:
        raise ValueError("Could not find/parse any TESTS (valid assert statements) in LLM-1 output.")

    return issues, tests


def parse_llm2_output(output: str) -> tuple[str, str]:
    """Parse LLM-2 output; validate structure."""
    if not output or not output.strip():
        raise ValueError("LLM-2 output is empty.")

    sugg_raw = _find_section(output, ["SUGGESTIONS", "SUGGESTION", "ADVICE", "RECOMMENDATIONS"])
    refl_raw = _find_section(output, ["REFLECTIONS", "REFLECTION", "QUESTIONS", "QUESTIONS TO CONSIDER"])

    suggestions = _strip_fences(sugg_raw).strip() if sugg_raw else ""
    reflections = _strip_fences(refl_raw).strip() if refl_raw else ""

    if not suggestions:
        suggestions = ("- 对照失败用例逐条检查你的输出与期望值的差异,定位递推式首次出错的输入。\n"
                      "- 重新手推一个最小例子(如 word1='', word2='a'),确认初始化是否正确。")
    if not reflections:
        reflections = ("- 请反思:这段代码在哪些边界情况下会先出错?为什么会出错?\n"
                       "- 如果换一个完全相同的小输入再跑一次,结果会一致吗?这揭示了什么问题?")

    return suggestions, reflections
