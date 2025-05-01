from typing import List
import os
from code_input import Solution
from problem_description import problem_description, constraints
import inspect
from openai import OpenAI

# Get the student's code
code_to_analyze = inspect.getsource(Solution.minDistance)

# Updated LLM analysis result
last_llm_result = """
Analysis Result:
【Logical Errors】
1. Incorrect initialization of dp array - Approximate region: lines 9-14
       Test Case 1.1: word1 = "a", word2 = "b"
       Expected: 1
       Test Case 1.2: word1 = "ab", word2 = "c"
       Expected: 2
       Test Case 1.3: word1 = "", word2 = "abc"
       Expected: 3
       Test Case 1.4: word1 = "abc", word2 = ""
       Expected: 3

2. Out of bounds error in dp array access - Approximate region: lines 19-24
       Test Case 2.1: word1 = "a", word2 = "bc"
       Expected: 2
       Test Case 2.2: word1 = "ab", word2 = "cd"
       Expected: 2
       Test Case 2.3: word1 = "abc", word2 = "d"
       Expected: 3
       Test Case 2.4: word1 = "a", word2 = "bcd"
       Expected: 3

3. Incorrect calculation of minimum operations - Approximate region: lines 25-30
       Test Case 3.1: word1 = "ab", word2 = "ba"
       Expected: 2
       Test Case 3.2: word1 = "abc", word2 = "bca"
       Expected: 2
       Test Case 3.3: word1 = "abcd", word2 = "dcba"
       Expected: 4
       Test Case 3.4: word1 = "abcde", word2 = "edcba"
       Expected: 4

4. Missing base case for when both strings are empty - Approximate region: lines 5-8
       Test Case 4.1: word1 = "", word2 = ""
       Expected: 0
       Test Case 4.2: word1 = "a", word2 = ""
       Expected: 1
       Test Case 4.3: word1 = "", word2 = "a"
       Expected: 1
       Test Case 4.4: word1 = "ab", word2 = ""
       Expected: 2
"""

# Updated test results
test_results = """
Test Results

Failed Tests:
Test: test_dp_initialization_case1
Category: Category 1: Incorrect initialization of dp array
Status: Failed
Logical Error Type: Error in initializing the dynamic programming array, leading to incorrect base cases for edit distance calculation (e.g., handling empty strings or initial rows/columns)
Error Details: AssertionError: 3 != 1

Test: test_min_operations_case2
Category: Category 3: Incorrect calculation of minimum operations
Status: Failed
Logical Error Type: Incorrectly computing the minimum cost of insert, delete, or replace operations in the dp array, leading to wrong edit distance values
Error Details: AssertionError: 1 != 2

Test: test_min_operations_case3
Category: Category 3: Incorrect calculation of minimum operations
Status: Failed
Logical Error Type: Incorrectly computing the minimum cost of insert, delete, or replace operations in the dp array, leading to wrong edit distance values
Error Details: AssertionError: 3 != 4

Test: test_out_of_bounds_case1
Category: Category 2: Out of bounds error in dp array access
Status: Failed
Logical Error Type: Accessing the dp array out of bounds, causing index errors or incorrect edit distance calculations for strings of different lengths
Error Details: AssertionError: 3 != 2

Test: test_out_of_bounds_case3
Category: Category 2: Out of bounds error in dp array access
Status: Failed
Logical Error Type: Accessing the dp array out of bounds, causing index errors or incorrect edit distance calculations for strings of different lengths
Error Details: AssertionError: 2 != 3

Passed Tests:
Test: test_dp_initialization_case4
Category: Category 1: Incorrect initialization of dp array
Status: Passed

Test: test_min_operations_case4
Category: Category 3: Incorrect calculation of minimum operations
Status: Passed

Test: test_empty_strings_case2
Category: Category 4: Missing base case for when both strings are empty
Status: Passed

Test: test_out_of_bounds_case4
Category: Category 2: Out of bounds error in dp array access
Status: Passed

Test: test_min_operations_case1
Category: Category 3: Incorrect calculation of minimum operations
Status: Passed

Test: test_empty_strings_case4
Category: Category 4: Missing base case for when both strings are empty
Status: Passed

Test: test_dp_initialization_case2
Category: Category 1: Incorrect initialization of dp array
Status: Passed

Test: test_empty_strings_case1
Category: Category 4: Missing base case for when both strings are empty
Status: Passed

Test: test_out_of_bounds_case2
Category: Category 2: Out of bounds error in dp array access
Status: Passed

Test: test_dp_initialization_case3
Category: Category 1: Incorrect initialization of dp array
Status: Passed

Test: test_empty_strings_case3
Category: Category 4: Missing base case for when both strings are empty
Status: Passed

Summary
Total Tests: 16
Passed: 11
Failed: 5
Total Reported: 16
"""

# Updated prompt with explicit instruction to focus only on provided logical errors
prompt = f"""
You are a code analysis expert reviewing a student's implementation of the "Longest Substring Without Repeating Characters" problem. Below are the student's code (with line numbers), the identified logical errors, and the test results. Your task is to analyze these inputs and provide suggestions for improvement.

IMPORTANT: Focus ONLY on the logical errors already identified in the 'last_llm_result'. DO NOT introduce or discuss any additional logical errors. Limit your analysis strictly to:
1. Incorrect handling of duplicate characters
2. Incorrect calculation of current length
3. Incorrect handling of edge case for empty string
4. Incorrect update of character dictionary

ONLY report logical errors that have at least one failing test case in the test results. If all test cases for a logical error category pass (e.g., all tests for incorrect handling of edge case for empty string), explicitly state that the error is resolved and do not include it in the suggestions for improvement.

Follow these guidelines:
1. Do NOT provide a complete corrected code solution. Offer only suggestions and insights.
2. For each logical error with failing tests, specify the exact line number(s) where the issue occurs.
3. Map test cases from 'last_llm_result' to 'test_results' to determine which pass or fail.
4. Provide actionable advice focusing only on logical errors with failing tests.
5. If a logical error category has all tests passing, state: "The [error name] error is resolved as all related test cases passed."
6. Format your response as plain text only. Do NOT use Markdown notation or any other formatting symbols.
7. If test results and error reports are inconsistent (e.g., a category with all tests passing is still reported as an error), analyze possible reasons (e.g., outdated report, tool bug, static analysis false positive).

Problem Description:
{problem_description}

Constraints:
{constraints}

Student's Code (with Line Numbers):
{code_to_analyze}

Identified Logical Errors:
{last_llm_result}

Test Results:
{test_results}

Instructions:
- Analyze ONLY the four logical errors already identified.
- For each issue with failing tests, indicate specific line number(s) causing the problem.
- Provide specific suggestions for improvement, referencing these lines.
- For each logical error category with all tests passing, confirm the error is resolved and exclude it from improvement suggestions.
- If inconsistencies are found between test results and reported errors, suggest possible causes and verification steps.
"""

# Set up the OpenAI client with DeepSeek API
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY") or "sk-REDACTED",
    base_url="https://api.deepseek.com"
)

# Create chat completion request (non-streaming for structured output)
try:
    completion = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a code analysis expert."},
            {"role": "user", "content": prompt}
        ],
        stream=False
    )

    # Print the raw analysis result without additional text
    print(completion.choices[0].message.content.strip())
except Exception as e:
    print(f"Error occurred: {str(e)}")
    print("Please check your API key, network connection, or try again later.")