import os
from typing import List
from code_input import Solution
from problem_description import problem_description, constraints
import inspect
from openai import OpenAI

# Get the student's code
code_to_analyze = inspect.getsource(Solution.findMedianSortedArrays)

# Updated LLM analysis result
last_llm_result = """
Analysis Result:
【Logical Errors】
1. Incorrect handling of edge cases when one of the arrays is empty - Approximate region: lines 3-6
       Test Case 1.1: nums1 = [1, 2, 3], nums2 = []
       Expected: 2.0
       Test Case 1.2: nums1 = [], nums2 = [1, 2, 3]
       Expected: 2.0
       Test Case 1.3: nums1 = [1], nums2 = []
       Expected: 1.0
       Test Case 1.4: nums1 = [], nums2 = [1]
       Expected: 1.0

2. Incorrect calculation of the median when the total length of the arrays is even - Approximate region: lines 15-20
       Test Case 2.1: nums1 = [1, 2], nums2 = [3, 4]
       Expected: 2.5
       Test Case 2.2: nums1 = [1, 3], nums2 = [2, 4]
       Expected: 2.5
       Test Case 2.3: nums1 = [1, 2, 3, 4], nums2 = []
       Expected: 2.5
       Test Case 2.4: nums1 = [], nums2 = [1, 2, 3, 4]
       Expected: 2.5

3. Incorrect handling of cases where the median is not at the midpoint of either array - Approximate region: lines 7-14
       Test Case 3.1: nums1 = [1, 3, 5], nums2 = [2, 4]
       Expected: 3.0
       Test Case 3.2: nums1 = [1, 2, 3], nums2 = [4, 5]
       Expected: 3.0
       Test Case 3.3: nums1 = [1, 2], nums2 = [3, 4, 5]
       Expected: 3.0
       Test Case 3.4: nums1 = [1, 2, 3], nums2 = [4]
       Expected: 2.5

4. Incorrect calculation of the median when the total length of the arrays is odd - Approximate region: lines 21-26
       Test Case 4.1: nums1 = [1, 2, 3], nums2 = [4, 5]
       Expected: 3.0
       Test Case 4.2: nums1 = [1, 2], nums2 = [3, 4, 5]
       Expected: 3.0
       Test Case 4.3: nums1 = [1, 2, 3, 4], nums2 = [5]
       Expected: 3.0
       Test Case 4.4: nums1 = [1], nums2 = [2, 3, 4, 5]
       Expected: 3.0
"""

# Updated test results
test_results = """
Debug: All Test Names in Suite
Total Loaded Tests: 0

Test Results

Failed Tests:
Test: test_even_total_length_case1
Category: Category 2: Incorrect calculation of the median when the total length of the arrays is even
Status: Failed
Logical Error Type: Incorrect calculation of the median when the total length of the arrays is even
Error Details: AssertionError: 3.5 != 2.5

Test: test_median_not_midpoint_case2
Category: Category 3: Incorrect handling of cases where the median is not at the midpoint of either array
Status: Failed
Logical Error Type: Incorrect handling of cases where the median is not at the midpoint of either array
Error Details: AssertionError: 2 != 3.0

Test: test_median_not_midpoint_case3
Category: Category 3: Incorrect handling of cases where the median is not at the midpoint of either array
Status: Failed
Logical Error Type: Incorrect handling of cases where the median is not at the midpoint of either array
Error Details: AssertionError: 4 != 3.0

Test: test_median_not_midpoint_case4
Category: Category 3: Incorrect handling of cases where the median is not at the midpoint of either array
Status: Failed
Logical Error Type: Incorrect handling of cases where the median is not at the midpoint of either array
Error Details: AssertionError: 3.0 != 2.5

Test: test_odd_total_length_case1
Category: Category 4: Incorrect calculation of the median when the total length of the arrays is odd
Status: Failed
Logical Error Type: Incorrect calculation of the median when the total length of the arrays is odd
Error Details: AssertionError: 2 != 3.0

Test: test_odd_total_length_case2
Category: Category 4: Incorrect calculation of the median when the total length of the arrays is odd
Status: Failed
Logical Error Type: Incorrect calculation of the median when the total length of the arrays is odd
Error Details: AssertionError: 4 != 3.0

Test: test_odd_total_length_case3
Category: Category 4: Incorrect calculation of the median when the total length of the arrays is odd
Status: Failed
Logical Error Type: Incorrect calculation of the median when the total length of the arrays is odd
Error Details: AssertionError: 5 != 3.0

Test: test_odd_total_length_case4
Category: Category 4: Incorrect calculation of the median when the total length of the arrays is odd
Status: Failed
Logical Error Type: Incorrect calculation of the median when the total length of the arrays is odd
Error Details: AssertionError: 1 != 3.0

Test: test_empty_array_case1
Category: Category 1: Incorrect handling of edge cases when one of the arrays is empty
Status: Failed
Logical Error Type: Incorrect handling of edge cases when one of the arrays is empty
Error Details: IndexError: list index out of range

Test: test_empty_array_case2
Category: Category 1: Incorrect handling of edge cases when one of the arrays is empty
Status: Failed
Logical Error Type: Incorrect handling of edge cases when one of the arrays is empty
Error Details: IndexError: list index out of range

Test: test_empty_array_case3
Category: Category 1: Incorrect handling of edge cases when one of the arrays is empty
Status: Failed
Logical Error Type: Incorrect handling of edge cases when one of the arrays is empty
Error Details: IndexError: list index out of range

Test: test_empty_array_case4
Category: Category 1: Incorrect handling of edge cases when one of the arrays is empty
Status: Failed
Logical Error Type: Incorrect handling of edge cases when one of the arrays is empty
Error Details: IndexError: list index out of range

Test: test_even_total_length_case3
Category: Category 2: Incorrect calculation of the median when the total length of the arrays is even
Status: Failed
Logical Error Type: Incorrect calculation of the median when the total length of the arrays is even
Error Details: IndexError: list index out of range

Test: test_even_total_length_case4
Category: Category 2: Incorrect calculation of the median when the total length of the arrays is even
Status: Failed
Logical Error Type: Incorrect calculation of the median when the total length of the arrays is even
Error Details: IndexError: list index out of range

Passed Tests:
Test: test_median_not_midpoint_case1
Category: Category 3: Incorrect handling of cases where the median is not at the midpoint of either array
Status: Passed

Test: test_even_total_length_case2
Category: Category 2: Incorrect calculation of the median when the total length of the arrays is even
Status: Passed

Summary
Total Tests: 16
Passed: 2
Failed: 14
Total Reported: 16
"""

# Updated prompt with explicit no-Markdown instruction
prompt = f"""
You are a code analysis expert reviewing a student's implementation of finding the median of two sorted arrays. Below are the student's code (with line numbers), the previous LLM analysis, and the test results. Your task is to analyze these inputs and provide suggestions for improvement based on the identified logical errors and test failures. Follow these guidelines:

1. Do NOT provide a complete corrected code solution. Offer only suggestions and insights.
2. Base your analysis on 'last_llm_result' and 'test_results' to confirm or refine issues.
3. For each logical error or test failure, specify the exact line number(s) where the issue likely occurs (e.g., 'Line 6' or 'Lines 19-21').
4. Map test cases from 'last_llm_result' to 'test_results' to determine which pass or fail.
5. Provide actionable advice focusing on logical errors, edge cases, and algorithmic improvements.
6. Ensure suggestions align with the O(log(m + n)) time complexity requirement.
7. Format your response as plain text only. Do NOT use Markdown notation (e.g., #, ##, ###, ####, *, **, ```) or any other formatting symbols. Use simple indentation and line breaks for structure.

Problem Description:
{problem_description}

Constraints:
{constraints}

Student's Code (with Line Numbers)
{code_to_analyze}

Previous LLM Analysis
{last_llm_result}

Test Results
{test_results}

Instructions
- Analyze logical errors and test failures.
- Map test cases to results (e.g., Test Case 3.1 -> test_empty_array_case1).
- For each issue, indicate specific line number(s) causing the problem.
- Provide specific suggestions for improvement, referencing these lines.
"""

# Initialize OpenAI client with Dashscope API
client = OpenAI(
    api_key="sk-1b76c8467e5a4ec1be14acfecf4559d0",  # Use the actual API key directly
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# Create chat completion request (non-streaming for structured output)
completion = client.chat.completions.create(
    model="qwen-max-latest",  # Corrected model name
    messages=[
        {"role": "system", "content": "You are a code analysis expert."},
        {"role": "user", "content": prompt}
    ]
)

# Print the raw analysis result without additional text
print(completion.choices[0].message.content.strip())