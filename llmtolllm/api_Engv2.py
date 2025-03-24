import requests

# API Configuration
url = "https://api.siliconflow.cn/v1/chat/completions"
headers = {
    "Authorization": "Bearer sk-obprxkhbxdlntmxsuwdchgtxjnuhdpoqhbiysjadslmzpltq",  # Replace with your valid API key
    "Content-Type": "application/json"
}

problem_description = """
Given two sorted arrays nums1 and nums2 of sizes m and n respectively, return the median of the two sorted arrays. 
The overall run time complexity should be O(log (m + n)).
"""

# Define constraints (optional)
constraints = """
- nums1.length == m
- nums2.length == n
- 0 <= m <= 1000
- 0 <= n <= 1000
- 1 <= m + n <= 2000
- -10^6 <= nums1[i], nums2[i] <= 10^6
"""

# Code to analyze
code_to_analyze = """
class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        len1 = len(nums1)
        len2 = len(nums2)
        if ((len1 + len2) % 2 == 1):
            if (len1 % 2 == 1 and nums1[int((len1 - 1) / 2)] >= nums2[int(len2 / 2)]):
                return nums1[int((len1 - 1) / 2)]
            elif (len2 % 2 == 1 and nums2[int((len2 - 1) / 2)] >= nums1[int(len1 / 2)]):
                return nums2[int((len2 - 1) / 2)]
            else:
                if (len1 % 2 == 1):
                    return nums1[int((len1 - 1) / 2)]
                else:
                    return nums2[int((len2 - 1) / 2)]
        elif ((len1 + len2) % 2 == 0):
            if (len1 % 2 == 1 and len2 % 2 == 1):
                if (nums1[int((len1 - 1) / 2)] >= nums2[int((len2 - 1) / 2)]):
                    if (nums1[int((len1 - 1) / 2)] >= nums2[int(len2 / 2)]):
                        return (nums1[int((len1 - 1) / 2)] + nums2[int((len2 - 1) / 2)]) / 2
                    else:
                        return (nums1[int((len1 - 1) / 2)] + nums2[int(len2 / 2)]) / 2
                else:
                    if (nums2[int((len2 - 1) / 2)] >= nums1[int(len1 / 2)]):
                        return (nums1[int(len1 / 2)] + nums2[int((len2 - 1) / 2)]) / 2
                    else:
                        return (nums1[int(len1 / 2)] + nums2[int(len1 / 2)]) / 2
            else:
                if (nums1[int(len1 / 2)] >= nums2[int(len2 / 2) - 1]):
                    if (nums1[int(len1 / 2)] >= nums2[int(len2 / 2)]):
                        return (nums1[int(len1 / 2) - 1] + nums1[int(len1 / 2)]) / 2
                    else:
                        return (nums1[int(len1 / 2) - 1] + nums2[int(len2 / 2)]) / 2
                else:
                    if (nums2[int(len2 / 2)] >= nums1[int(len1 / 2) - 1]):
                        return (nums2[int(len2 / 2) - 1] + nums2[int(len2 / 2)]) / 2
"""

# Design Prompt for API to analyze the code, return logical errors, approximate code regions, and test cases
prompt = f"""
You are a code analysis expert. Based on the following code, directly list possible logical errors, the approximate code regions where these errors occur, and test cases that can detect these errors. Requirements:

1. Only output clear error descriptions, approximate code regions, and test cases
2. Do not use Markdown format
3. If there are fewer than 4 logical errors, list only the errors found
4. For each logical error, specify the approximate code region (e.g., 'Lines 5-10' or 'if block at line 15')
5. Strictly provide 4 test cases covering boundary conditions

Problem Description: 
{problem_description}

Constraints: 
{constraints}

Code:
{code_to_analyze}

Please strictly follow this format for output:

【Logical Errors】
1. [Error description] - Approximate region: [code region]
2. [Error description] - Approximate region: [code region]
... (if more errors are found)

【Test Cases】
Input: [nums1], [nums2]
Expected: [value]
Input: [nums1], [nums2]
Expected: [value]
Input: [nums1], [nums2]
Expected: [value]
Input: [nums1], [nums2]
Expected: [value]
"""

# API request payload
payload = {
    "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",  # Specify the model to use
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ]
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