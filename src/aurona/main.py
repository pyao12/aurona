"""Aurona 机器人入口。"""

import signal
import sys

from openai import OpenAIError

from aurona import __version__
from aurona.im.weixin_oc import login
from aurona.im.weixin_oc.common import notify_start, notify_stop
from aurona.im.weixin_oc.receive import run_long_poll_loop
from aurona.im.weixin_oc.send import send_text
from aurona.logger import error, info, warn
from aurona.provider import openai

CLIENT: openai.OpenAIConnection | None = None
MODEL: str | None = None
HISTORY: list = []


def loop():
    """主消息循环：持续监听消息并回复。"""

    def _on_message(msg):
        global HISTORY  # pylint: disable=global-statement
        text = ""
        for item in msg.get("item_list", []):
            ti = item.get("text_item")
            if ti:
                text = ti.get("text", "")
                break
        user_id = msg.get("from_user_id", "")
        if user_id and text:
            if text == "/new":
                HISTORY = []
                send_text(user_id, "Reset conversation history.")
                return

            if CLIENT is None or MODEL is None:
                warn("Client or model not initialized")
                return
            info(f"Received msg: {text}")
            HISTORY.append({"role": "user", "content": text})
            try:
                answer = CLIENT.get_completions(HISTORY, MODEL)
                HISTORY.append(answer)
            except OpenAIError as exc:
                warn(str(exc))
                send_text(user_id, f"API Request Failed: {exc}")
                return
            if answer.content:
                send_text(user_id, answer.content or "")
                info(f"Replied to {user_id}: {answer.content}")

        else:
            warn(f"Skipping msg: user_id={user_id} text={text!r}")

    try:
        resp = notify_start()
        info(f"notifyStart: ret={resp.get('ret')}")
    except (RuntimeError, OpenAIError) as exc:
        warn(f"notifyStart failed (ignored): {exc}")

    def _shutdown(_sig, _frame):
        info("Shutting down...")
        try:
            notify_stop()
        except RuntimeError, OpenAIError:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    info("Starting message loop...")
    run_long_poll_loop(on_message=_on_message)


def main() -> int:
    """主入口：连接或启动机器人。"""
    global CLIENT, MODEL  # pylint: disable=global-statement
    info(f"Welcome to Aurona (version {__version__})")

    if len(sys.argv) <= 1:
        warn("Nothing to do!")
        return 1

    if sys.argv[1] == "connect":
        try:
            login.connect()
        except Exception as exc:  # pylint: disable=broad-exception-caught
            error(f"Connect failed: {exc}")
            return 1
    elif sys.argv[1] == "run":
        from aurona import config  # pylint: disable=import-outside-toplevel

        conf = config.load_config()
        if isinstance(conf, int):
            error("Cannot read file! ")
            return 1

        if not config.check_schema(conf):
            error("Invalid config file!")
            return 1

        try:
            CLIENT = openai.OpenAIConnection(
                conf["provider"]["baseurl"], conf["provider"]["apikey"]
            )
        except RuntimeError as exc:
            error(f"Failed to initialize provider: {exc}")
            return 1
        MODEL = conf["provider"]["model"]
        loop()

    return 0
