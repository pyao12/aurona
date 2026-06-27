from . import __version__

import sys
from aurona.provider import openai
import aurona.config as config
from aurona.logger import info, warn, error
from aurona.im.weixin_oc import login


def main():
    info(f"Welcome to Aurona (version {__version__})")

    if len(sys.argv) <= 1:
        warn("Nothing to do!")
        return 1

    if sys.argv[1] == "ask":
        conf = config.load_config()
        if conf == -1:
            error("Configuration file not found.")
            return 1

        if type(conf) != dict:
            error("Invalid config format!")
            return 1

        if not config.check_schema(conf):
            error("Invalid config format!")
            return 1

        try:
            QUESTION = sys.argv[1]
        except IndexError:
            error("Please give your question!")
            return 1

        info(f"Question: {QUESTION}")

        connection = openai.OpenAIConnection(
            conf["provider"]["baseurl"], conf["provider"]["apikey"]
        )

        # 作者用的Deepseek作为测试，当然只是测试啦，后面会有更优秀的数据存储
        answer = connection.get_completions(
            openai.build_temp_history(QUESTION), "deepseek-v4-flash"
        )
        info("")
        info(answer)
        info("")
    elif sys.argv[1] == "connect":
        login.connect()

    return 0  # C++写多了哈哈
