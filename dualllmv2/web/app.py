# web/app.py
# Flask 后端:为可视化网页提供 API,并托管静态页面。
# 使用 Anaconda DA 环境的 Python 解释器运行(已安装 Flask / langchain 系列)。

import os
import sys

# 确保能 import 到上级目录的 pipeline / config 等模块
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, request, jsonify, render_template
from pipeline import dual_llm_pipeline
import config

app = Flask(__name__, template_folder="templates", static_folder="static")

SAMPLE_CODE = '''class Solution:
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
'''

SAMPLE_DESC = "LeetCode 72. Edit Distance: Minimum operations to convert word1 to word2."


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/sample")
def sample():
    return jsonify({"code": SAMPLE_CODE, "problem_desc": SAMPLE_DESC})


@app.route("/api/config")
def api_config():
    """返回当前后端模式、模型与两个 LLM 的连接状态,供网页展示状态徽标。"""
    return jsonify({
        "backend_mode": config.BACKEND_MODE,
        "llm1_model": getattr(config, "LLM1_MODEL", None),
        "llm2_model": getattr(config, "LLM2_MODEL", None),
        "llm1_key_set": bool(getattr(config, "LLM1_API_KEY", "")) and not getattr(config, "KEY1_IS_PLACEHOLDER", False),
        "llm2_key_set": bool(getattr(config, "LLM2_API_KEY", "")) and not getattr(config, "KEY2_IS_PLACEHOLDER", False),
    })


@app.route("/api/run", methods=["POST"])
def run():
    data = request.get_json(force=True, silent=True) or {}
    code = data.get("code", "")
    problem_desc = data.get("problem_desc", "")
    reflection = data.get("student_reflection", "")
    try:
        max_iter = int(data.get("max_iterations", 3))
    except (TypeError, ValueError):
        max_iter = 3
    result = dual_llm_pipeline(code, problem_desc, reflection, max_iter)
    result["backend_mode"] = config.BACKEND_MODE
    result["llm1_model"] = getattr(config, "LLM1_MODEL", None)
    result["llm2_model"] = getattr(config, "LLM2_MODEL", None)
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[Dual-LLM Web] backend={config.BACKEND_MODE}  ->  http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
