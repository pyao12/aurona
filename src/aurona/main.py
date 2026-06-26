from . import __version__

import json
import sys
from aurona.provider import openai


def main():
    print(f"Welcome to Aurona (version {__version__})")

    try:
        with open("data/providers.json", "r", encoding="utf-8") as f:
            providers = json.loads(f.read())
    except FileNotFoundError:
        print("No providers found!")
        return 1

    try:
        test_provider = providers[0]
    except IndexError:
        print("No providers found!")
        return 1

    # 太不优雅了 (
    if (
        not test_provider.get("name")
        or not test_provider.get("display")
        or not test_provider.get("api-key")
        or not test_provider.get("baseurl")
    ):
        print("Providers didn't configured correctly!")
        return 1

    print(f"Test with {test_provider.get("display")}")
    print("Creating client...")
    connection = openai.OpenAIConnection(
        test_provider.get("baseurl"), test_provider.get("api-key")
    )

    try:
        QUESTION = sys.argv[1]
    except IndexError:
        print("Please give your question!")
        return 1

    print(f"Question: {QUESTION}")

    # 作者用的Deepseek作为测试，当然只是测试啦，后面会有更优秀的数据存储
    answer = connection.get_completions(
        openai.build_temp_history(QUESTION), "deepseek-v4-flash"
    )
    print("=" * 20)
    print(answer)
    print("=" * 20)

    return 0  # C++写多了哈哈
