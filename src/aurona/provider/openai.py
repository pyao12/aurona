# OpenAI Compatible接口

import aurona.logger as logger
from openai import OpenAI


# 因为completions请求必须传递整个history，所以有这么个函数构建临时的消息列表
# responses请求就不用了
def build_temp_history(message: str) -> list:
    return [{"role": "user", "content": message}]


class OpenAIConnection:
    # OpenAI Compatible接口的连接实例，方便同时连接多个providers

    def __init__(self, url: str, key: str):
        self._openai_client = OpenAI(api_key=key, base_url=url)

    def get_completions(self, messages_history: list, model: str) -> str:
        completion = self._openai_client.chat.completions.create(
            model=model, messages=messages_history
        )
        return completion.choices[0].message.content
