# main.py
# Example Usage and Input Handling
#
# 默认以 offline 模式运行(无需 API key)。
# 如需真实 LLM:设置环境变量 DUAL_LLM_BACKEND=api 并填入 DEEPSEEK_API_KEY / OPENAI_API_KEY。

from pipeline import dual_llm_pipeline
import config  # noqa: F401  (确保后端模式已加载)


if __name__ == "__main__":
    # Sample code from PDF (LeetCode 72. Edit Distance)
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

    print(f"[backend mode] {config.BACKEND_MODE}")
    result = dual_llm_pipeline(sample_code, problem_desc)
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 交互模式示例(接入网页后由前端驱动):
    # while result.get("reflection_required", False):
    #     student_reflection = input("Provide your reflection on the suggestions: ")
    #     revised_code = input("Provide your revised code: ")
    #     result = dual_llm_pipeline(revised_code, problem_desc, student_reflection)
