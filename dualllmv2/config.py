# config.py
# Configuration and API Setup (refactored)
#
# 设计要点(本版):
#   1. 两个 LLM(LLM-1 分析者/考官 与 LLM-2 对抗者/导师)**各自使用独立的 DeepSeek API Key**,
#      实现真正的"双账户对抗":LLM-1 用 LLM1_API_KEY,LLM-2 用 LLM2_API_KEY。
#      原 LLM-2 使用的 OpenAI 已移除,统一走 DeepSeek 的 OpenAI 兼容接口。
#   2. 新增 .env 独立配置文件(含 API Key),通过 python-dotenv 加载;
#      .env 已被 .gitignore 忽略,不会上传到 GitHub。
#   3. 后端模式开关 DUAL_LLM_BACKEND: "offline"(默认无需 Key) 或 "api"(真实 DeepSeek)。
#   4. ChatOpenAI 实例延迟初始化,且仅 api 模式才需要网络 / Key。

import os


# ---------------------------------------------------------------------------
# 加载 .env(本地配置,含 API Key,禁止提交到 GitHub)
# 优先使用 python-dotenv;若未安装则手动解析 .env,保证离线也能跑。
# ---------------------------------------------------------------------------
def _load_dotenv():
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return
    except Exception:
        pass
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                os.environ.setdefault(k, v)


_load_dotenv()

# 后端模式: "offline" (默认,无需 Key) 或 "api" (真实 DeepSeek 调用)
BACKEND_MODE = os.environ.get("DUAL_LLM_BACKEND", "offline").lower()

# 占位符:便于运行时/网页区分"未配置"与"已配置但无效"
PLACEHOLDER = "your_deepseek_api_key_here"

# ---------------------------------------------------------------------------
# 两个 LLM 各自的 DeepSeek API Key(独立账户 / 独立配额,便于"对抗")
#   优先级:LLMx_API_KEY > 统一的 DEEPSEEK_API_KEY(兼容旧配置)
# ---------------------------------------------------------------------------
LLM1_API_KEY = os.environ.get("LLM1_API_KEY") or os.environ.get("DEEPSEEK_API_KEY", "")
LLM2_API_KEY = os.environ.get("LLM2_API_KEY") or os.environ.get("DEEPSEEK_API_KEY", "")

# DeepSeek OpenAI 兼容接口地址(两个 LLM 共用)
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

# 两个 LLM 的模型(都用 DeepSeek;可设不同模型增强"对抗性",如 LLM-2 用 deepseek-reasoner)
LLM1_MODEL = os.environ.get("LLM1_MODEL", "deepseek-chat")  # 角色:分析者 / 考官
LLM2_MODEL = os.environ.get("LLM2_MODEL", "deepseek-chat")  # 角色:对抗者 / 导师


def _is_placeholder(k: str) -> bool:
    return (not k) or (k.strip() == PLACEHOLDER)


def mask_key(k: str) -> str:
    """仅保留标准前缀与末 4 位,用于前端展示"本次调用用的是哪个 Key",不泄露任何密钥字节。

    设计:DeepSeek Key 形如 sk-<32位十六进制>。这里只展示已知的 "sk-" 前缀 +
    末 4 位(例如 sk-…3c63)。既不暴露任何 secret 字节,又能区分两个独立 Key
    (LLM-1 末 4 位与 LLM-2 末 4 位不同,足以证明"双 Key 对抗"确实发生)。
    """
    if not k:
        return ""
    k = k.strip()
    if len(k) <= 7:
        return "***"  # 异常短值直接隐藏,避免泄露
    return f"sk-…{k[-4:]}"


# 占位符检测:便于网页/运行时给出清晰提示,而不是返回一个难懂的 401
KEY1_IS_PLACEHOLDER = _is_placeholder(LLM1_API_KEY)
KEY2_IS_PLACEHOLDER = _is_placeholder(LLM2_API_KEY)
KEY1_MASK = mask_key(LLM1_API_KEY)
KEY2_MASK = mask_key(LLM2_API_KEY)

# 兼容原始代码的全局占位(实际实例在 _ensure_llms 中创建)
llm1 = None
llm2 = None

_initialized = False


def _ensure_llms():
    """延迟创建两个 ChatOpenAI 实例(仅 api 模式需要),分别使用各自的 DeepSeek Key。"""
    global llm1, llm2, _initialized
    if _initialized:
        return llm1, llm2
    if _is_placeholder(LLM1_API_KEY):
        raise RuntimeError(
            "LLM-1 的 DeepSeek API Key 未配置(请在 .env 设置 LLM1_API_KEY)。"
            "或将 DUAL_LLM_BACKEND 设为 offline 以使用本地规则引擎。"
        )
    if _is_placeholder(LLM2_API_KEY):
        raise RuntimeError(
            "LLM-2 的 DeepSeek API Key 未配置(请在 .env 设置 LLM2_API_KEY)。"
            "或将 DUAL_LLM_BACKEND 设为 offline 以使用本地规则引擎。"
        )
    from langchain_openai import ChatOpenAI

    # LLM-1:分析者 / 考官,使用 LLM1_API_KEY
    llm1 = ChatOpenAI(
        model=LLM1_MODEL,
        temperature=0.2,
        openai_api_key=LLM1_API_KEY,
        openai_api_base=DEEPSEEK_BASE_URL,
    )
    # LLM-2:对抗者 / 导师,使用 LLM2_API_KEY(独立账户,真正实现"双模型对抗")
    llm2 = ChatOpenAI(
        model=LLM2_MODEL,
        temperature=0.3,
        openai_api_key=LLM2_API_KEY,
        openai_api_base=DEEPSEEK_BASE_URL,
    )
    _initialized = True
    return llm1, llm2
