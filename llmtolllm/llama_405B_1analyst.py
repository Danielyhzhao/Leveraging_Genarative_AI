from http import HTTPStatus
import dashscope
from code_input import Solution
from problem_description import problem_description, constraints
import inspect

dashscope.save_api_key('sk-1b76c8467e5a4ec1be14acfecf4559d0')

def call_with_messages():
    code_to_analyze = inspect.getsource(Solution.findMedianSortedArrays)
    prompt = f"""
    You are a code analysis expert with strict formatting requirements. Your task is to analyze the given code and identify logical errors. Your output format must EXACTLY match the template given at the end.

    IMPORTANT FORMATTING RULES:
    1. You MUST use the EXACT formatting structure shown in the template.
    2. Do NOT add any explanations, introduction, or conclusions outside the specified format.
    3. Do NOT use Markdown formatting like triple backticks, headings, or code blocks.
    4. Each test case MUST follow the exact pattern shown in the template.
    5. Each test case MUST include nums1, nums2, expected, and actual values.
    6. Your output MUST begin with "【Logical Errors】" and contain nothing before this.

    ANALYSIS GUIDELINES:
    1. Identify up to 4 logical errors in the code.
    2. For each error, specify the code region where it occurs.
    3. For each error, provide exactly 4 test cases that reveal the error.
    4. Make test cases concise and directly related to the error they demonstrate.
    5. Include test cases for edge cases and common scenarios.

    Problem Description:
    {problem_description}

    Constraints:
    {constraints}

    Code:
    {code_to_analyze}

    YOUR RESPONSE MUST EXACTLY FOLLOW THIS TEMPLATE:

    【Logical Errors】
    1. [Error description] - Approximate region: [code region (like in which line)]
       Test Case 1.1: nums1 = [values], nums2 = [values]
       Expected: [value]
       Test Case 1.2: nums1 = [values], nums2 = [values]
       Expected: [value]
       Test Case 1.3: nums1 = [values], nums2 = [values]
       Expected: [value]
       Test Case 1.4: nums1 = [values], nums2 = [values]
       Expected: [value]
       (no need the actual output)

    2. [Error description] - Approximate region: [code region (like in which line)]
       Test Case 2.1: nums1 = [values], nums2 = [values]
       Expected: [value]
       Test Case 2.2: nums1 = [values], nums2 = [values]
       Expected: [value]
       Test Case 2.3: nums1 = [values], nums2 = [values]
       Expected: [value]
       Test Case 2.4: nums1 = [values], nums2 = [values]
       Expected: [value]
       (no need the actual output)

    ... (repeat for each error found)
    """

    messages = [
        {'role': 'system', 'content': 'You are a code analysis expert.'},
        {'role': 'user', 'content': prompt}
    ]

    response = dashscope.Generation.call(
        model='llama3.1-405b-instruct',
        messages=messages,
        result_format='message',
    )

    if response.status_code == HTTPStatus.OK:
        result = response.output.choices[0].message.content.strip()
        print("\nAnalysis Result:")
        print(result)
    else:
        print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))

if __name__ == '__main__':
    call_with_messages()