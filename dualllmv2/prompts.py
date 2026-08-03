# prompts.py
# Prompt Templates
#
# 公共契约完全保留: llm1_prompt / llm2_prompt (langchain PromptTemplate)。
# 该模块是"api"后端模式的依赖;离线(offline)后端不导入本模块。

from langchain_core.prompts import PromptTemplate

# LLM-1 Prompt: Forced structured output with issues (line numbers) and tests
llm1_prompt = PromptTemplate(
    input_variables=["code", "problem_desc"],
    template="""
    Analyze the code line by line for logical errors, syntax issues, and improvements.
    Code: {code}
    Problem Description: {problem_desc}

    Output EXACTLY in this format (no extra text):
    ISSUES:
    - Line X-Y: [Issue 1, e.g., Incorrect DP initialization for empty strings]
    - Line A-B: [Issue 2, e.g., Off-by-one in loop bound]
    - Line P-Q: [Issue 3, e.g., Missing early-return for trivial case]
    - Line R-S: [Issue 4, e.g., Suboptimal O(n^2) where O(n) is possible]
    - Line T-U: [Issue 5, e.g., Unhandled None / negative input]

    TESTS:
    self.assertEqual(func(args), expected)  # Reason: [Empty boundary]
    self.assertEqual(func(args), expected)  # Reason: [Single element]
    self.assertEqual(func(args), expected)  # Reason: [Identical inputs]
    self.assertEqual(func(args), expected)  # Reason: [General case]
    self.assertEqual(func(args), expected)  # Reason: [Large / stress case]
    self.assertEqual(func(args), expected)  # Reason: [Another edge case]

    Requirements:
    1. Produce AT LEAST 5 ISSUES across different dimensions: correctness, edge cases,
       efficiency (time/space), readability/style, and robustness. If the code is mostly
       correct, still list the 5 most important things a student should double-check.
    2. Produce AT LEAST 6 TESTS covering boundaries (empty, single, identical, max) and
       at least 2 general/stress cases. Use a reference (known-correct) implementation to
       compute expected values; do NOT guess.
    3. Every ISSUE MUST include line numbers (Line X-Y:).
    4. TESTS MUST be valid Python unittest asserts using self.assertEqual / self.assertTrue.
    5. Each test Reason should encourage reflection on WHY that case matters.
    """
)

# LLM-2 Prompt: 对抗式评审(ADVERSARIAL reviewer)
# 作为"对抗者 / 导师",既要给学生可执行的建议,也要审视 LLM-1(分析者)的结论是否扎实。
llm2_prompt = PromptTemplate(
    input_variables=["code", "problem_desc", "issues", "failures"],
    template="""
    You are an ADVERSARIAL code reviewer (LLM-2). Your job is to critically challenge
    the student's solution AND scrutinize the findings of the first analyst (LLM-1).
    Be rigorous: do not accept weak justifications; push the student to truly understand.

    Student Code: {code}
    Problem: {problem_desc}
    Issues found by LLM-1 (the first analyst): {issues}
    Failed Tests: {failures}

    Output EXACTLY in this format:
    SUGGESTIONS:
    - For Line X-Y: [Actionable suggestion WITHOUT giving full code, e.g., Add the missing base case for empty input]
    - For Line A-B: [Another, challenging the student's assumption]

    REFLECTIONS:
    - [A pointed question that exposes a likely misconception]
    - [A question forcing the student to compare their own trace against the expected value]

    Requirements:
    1. Suggestions ONLY (no full code; promote thinking). At least 2.
    2. Reference line numbers from the issues.
    3. At least 2 reflection questions, phrased to surface misunderstanding.
    4. If LLM-1's issues/tests look incomplete or wrong, say so explicitly and point out what is missing.
    5. Encourage the student to re-derive the expected value by hand before revising.
    """
)
