"""大模型服务层：封装 OpenAI 兼容接口（默认 DeepSeek）。

通过 `openai` 官方 SDK 调用 `https://api.deepseek.com`，
接入模型由环境变量 LLM_MODEL 指定（默认 deepseek-chat）。
支持同步与流式两种生成方式。
"""

from collections.abc import Iterator

from openai import OpenAI

from app.core.config import settings

# 系统提示词：塑造助手角色与回复格式
DEFAULT_SYSTEM_PROMPT = (
    "你是 QueryAgentService 的智能助手，一个友好、专业、可靠的中文 AI 助手。"
    "请用 Markdown 格式组织回答（可以使用标题、列表、代码块、引用等），"
    "代码块请标注语言类型。回答要准确、简洁、有条理。"
)

# 传给模型的最近历史消息条数上限（每条 user/assistant 计 1 条），防止上下文超长
MAX_HISTORY_MESSAGES = 20


class LLMError(Exception):
    """大模型调用失败（网络错误、鉴权失败、超时、空回复等）。"""


def build_messages(history: list[dict]) -> list[dict]:
    """构造发送给模型的 messages：系统提示 + 最近历史（超长时截断）。

    history 形如 [{"role": "user" | "assistant", "content": "..."}, ...]，
    按时间正序传入。
    """
    messages: list[dict] = [
        {"role": "system", "content": DEFAULT_SYSTEM_PROMPT}
    ]
    messages.extend(history[-MAX_HISTORY_MESSAGES:])
    return messages


def chat_completion(messages: list[dict]) -> str:
    """调用大模型生成回复，返回纯文本内容（同步非流式）。

    Raises:
        LLMError: 未配置 API Key、网络异常、模型返回空内容等情况。
    """
    if not settings.LLM_API_KEY:
        raise LLMError("未配置 LLM_API_KEY，请在 server/.env 中设置 API Key")

    try:
        client = OpenAI(
            base_url=settings.LLM_BASE_URL,
            api_key=settings.LLM_API_KEY,
            timeout=settings.LLM_TIMEOUT,
        )
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )
    except Exception as exc:  # noqa: BLE001 统一封装为 LLMError
        raise LLMError(f"大模型调用失败: {exc}") from exc

    content = response.choices[0].message.content
    if not content or not content.strip():
        raise LLMError("模型返回了空内容，请重试")
    return content.strip()


def chat_completion_stream(messages: list[dict]) -> Iterator[str]:
    """调用大模型以流式方式生成回复，逐段产出文本增量。

    使用方式：
        for delta in chat_completion_stream(messages):
            ...  # delta 为一段文本增量，按序拼接即完整回复

    Raises:
        LLMError: 未配置 API Key、网络异常、流式读取中断等情况。
    """
    if not settings.LLM_API_KEY:
        raise LLMError("未配置 LLM_API_KEY，请在 server/.env 中设置 API Key")

    try:
        client = OpenAI(
            base_url=settings.LLM_BASE_URL,
            api_key=settings.LLM_API_KEY,
            timeout=settings.LLM_TIMEOUT,
        )
        stream = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
    except Exception as exc:  # noqa: BLE001 统一封装为 LLMError
        raise LLMError(f"大模型调用失败: {exc}") from exc
