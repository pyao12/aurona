"""兼容 OpenAI 的聊天补全接口封装。"""

from openai import OpenAI, OpenAIError


def build_temp_history(message: str) -> list:
    """为补全请求构建单条历史消息列表。"""
    return [{"role": "user", "content": message}]


class OpenAIConnection:  # pylint: disable=too-few-public-methods
    """兼容 OpenAI 的聊天补全端点封装。"""

    def __init__(self, url: str, key: str):
        try:
            self._openai_client = OpenAI(api_key=key, base_url=url)
        except OpenAIError as exc:
            raise RuntimeError(f"Failed to create OpenAI client: {exc}") from exc

    def get_completions(self, messages_history: list, model: str):
        """根据 *messages_history* 获取助手回复。"""
        return (
            self._openai_client.chat.completions.create(
                model=model, messages=messages_history
            )
            .choices[0]
            .message
        )
