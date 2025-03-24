# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI
from code_input import Solution
from problem_description import problem_description, constraints
import inspect

# Set up the OpenAI client with DeepSeek API
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY") or "sk-5642f30943364e10b56b4253920e6881",
    base_url="https://api.deepseek.com"
)

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

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",  # Using deepseek-chat instead of deepseek-r1
            messages=[
                {"role": "system", "content": "You are a code analysis expert."},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )

        result = response.choices[0].message.content.strip()
        print("\nAnalysis Result:")
        print(result)

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print("Please check your API key, network connection, or try again later.")

if __name__ == '__main__':
    call_with_messages()