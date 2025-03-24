import requests
import dashscope
from code_input import Solution
from problem_description import problem_description, constraints
import inspect

# API Configuration
url = "https://api.siliconflow.cn/v1/chat/completions"
headers = {
    "Authorization": "Bearer sk-obprxkhbxdlntmxsuwdchgtxjnuhdpoqhbiysjadslmzpltq",  # Replace with your valid API key
    "Content-Type": "application/json"
}

def call_with_messages():
    code_to_analyze = inspect.getsource(Solution.findMedianSortedArrays)
    prompt = f"""
    You are a code analysis expert with strict formatting requirements. Your task is to analyze the given code and identify logical errors. Your output format must EXACTLY match the template given at the end.

    IMPORTANT FORMATTING RULES:
    1. You MUST use the EXACT formatting structure shown in the template.
    2. Do NOT add any explanations, introduction, or conclusions outside the specified format.
    3. Do NOT use Markdown formatting like triple backticks, headings (#, ##, ###, ####), bold (**), italics (*), or code blocks.
    4. Each test case MUST follow the exact pattern shown in the template.
    5. Each test case MUST include nums1, nums2, expected, and actual values.
    6. Your output MUST begin with "【Logical Errors】" and contain nothing before this.
    7. Ensure the response is plain text only, with no Markdown symbols (e.g., **, *, #, ```) anywhere.

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

    2. [Error description] - Approximate region: [code region (like in which line)]
       Test Case 2.1: nums1 = [values], nums2 = [values]
       Expected: [value]
       Test Case 2.2: nums1 = [values], nums2 = [values]
       Expected: [value]
       Test Case 2.3: nums1 = [values], nums2 = [values]
       Expected: [value]
       Test Case 2.4: nums1 = [values], nums2 = [values]
       Expected: [value]

    ... (repeat for each error found)
    """

    # API request payload
    payload = {
        "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",  # Specify the model to use
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,  # Use a low temperature for more predictable formatting
        "top_p": 0.95  # Adjust for more predictable outputs
    }

    # Send request to API
    response = requests.post(url, json=payload, headers=headers)

    # Check response status and handle results
    if response.status_code == 200:
        # Save response to file for later review
        with open("response_text.txt", "w", encoding="utf-8") as file:
            file.write(response.text)
        print("Response saved to response_text.txt")
        # Extract and print analysis results
        response_json = response.json()
        result = response_json["choices"][0]["message"]["content"].strip()
        print("\nAnalysis Result:")
        print(result)
    else:
        print(f"API request failed with status code: {response.status_code}")
        print(response.text)

# Call the function to execute it
call_with_messages()