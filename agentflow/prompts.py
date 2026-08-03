# prompts.py
# Prompt Templates

from langchain.prompts import PromptTemplate

# LLM-1 Prompt: Forced structured output with issues (line numbers) and tests
llm1_prompt = PromptTemplate(
    input_variables=["code", "problem_desc"],
    template="""
    Analyze the code line by line for logical errors, syntax issues, and improvements.
    Code: {code}
    Problem Description: {problem_desc}

    Output EXACTLY in this format (no extra text):
    ISSUES:
    - Line X-Y: [Description of issue, e.g., Incorrect DP initialization for empty strings]
    - Line A-B: [Another issue]

    TESTS:
    self.assertEqual(func(args), expected)  # Reason: [Brief reason, e.g., Empty to single char]
    self.assertEqual(func(args), expected)  # Reason: [Another]

    Requirements:
    1. At least 3-5 tests, including boundaries (empty, single, max).
    2. Issues MUST include line numbers.
    3. Tests MUST be valid Python unittest asserts.
    4. Encourage reflection in reasons.
    """
)

# LLM-2 Prompt: Suggestions with reflections (no full code)
llm2_prompt = PromptTemplate(
    input_variables=["code", "problem_desc", "issues", "failures"],
    template="""
    Provide suggestions based on detected issues and failed tests.
    Student Code: {code}
    Problem: {problem_desc}
    Issues: {issues}
    Failed Tests: {failures}

    Output EXACTLY in this format:
    SUGGESTIONS:
    - For Line X-Y: [Actionable suggestion, e.g., Add check for len=0, without code]
    - For Line A-B: [Another]

    REFLECTIONS:
    - Why might empty strings cause issues in this algorithm?
    - How does this edge case affect the overall logic?

    Requirements:
    1. Suggestions ONLY (no full code; promote thinking).
    2. At least 2 reflection questions.
    3. Reference line numbers from issues.
    """
)