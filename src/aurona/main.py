from . import __version__

import sys
from aurona.provider import openai
import aurona.config as config


def main():
    print(f"Welcome to Aurona (version {__version__})")

    conf = config.load_config()
    if conf == -1:
        print("Configuration file not found.")
        return 1

    if type(conf) != dict:
        print("Invalid config format!")
        return 1

    if not config.check_schema(conf):
        print("Invalid config format!")
        return 1

    try:
        QUESTION = sys.argv[1]
    except IndexError:
        print("Please give your question!")
        return 1

    print(f"Question: {QUESTION}")

    connection = openai.OpenAIConnection(
        conf["provider"]["baseurl"], conf["provider"]["apikey"]
    )

    # 作者用的Deepseek作为测试，当然只是测试啦，后面会有更优秀的数据存储
    answer = connection.get_completions(
        openai.build_temp_history(QUESTION), "deepseek-v4-flash"
    )
    print("=" * 20)
    print(answer)
    print("=" * 20)

    return 0  # C++写多了哈哈
