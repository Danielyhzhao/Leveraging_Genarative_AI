# main.py
# Example Usage and Input Handling

import os
from pipeline import dual_llm_pipeline
from config import llm1, llm2  # Ensure imports if needed

if __name__ == "__main__":
    # Set API keys for demo if not set in config
    os.environ["DEEPSEEK_API_KEY"] = "sk-REDACTED"  # Replace
    os.environ["OPENAI_API_KEY"] = "sk-REDACTED"  # Replace

    # Sample code from PDF
    sample_code = """
class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        m, n = len(word1), len(word2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if word1[i - 1] == word2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1
        return dp[m][n]
    """
    problem_desc = "LeetCode 72. Edit Distance: Minimum operations to convert word1 to word2."

    # Initial run
    result = dual_llm_pipeline(sample_code, problem_desc)
    print("Optimization Result:\n", result)

    # To simulate interactive mode:
    # while result.get("reflection_required", False):
    #     student_reflection = input("Provide your reflection on the suggestions: ")
    #     revised_code = input("Provide your revised code: ")
    #     result = dual_llm_pipeline(revised_code, problem_desc, student_reflection)

# Usage: Run python main.py
# For production, integrate with UI for student input (code, reflection).