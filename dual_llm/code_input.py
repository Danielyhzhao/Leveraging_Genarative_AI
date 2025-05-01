from typing import List


class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        m, n = len(word1), len(word2)

        if m == 0:
            return n

        if n == 0:
            return m

        dp = [[0] * n for _ in range(m)]

        for i in range(m):
            dp[i][0] = 1

        for j in range(n):
            dp[0][j] = 2

        for i in range(m):
            for j in range(n):
                if word1[i] == word2[j]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    delete = dp[i - 1][j] + 1
                    insert = dp[i][j - 1] + 1
                    replace = dp[i - 1][j - 1] + 1

                    dp[i][j] = min(delete, insert, replace)
        return dp[m - 1][n - 1]
