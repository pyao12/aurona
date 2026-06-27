from . import __version__

import sys
import signal
from openai import OpenAIError
from aurona.provider import openai
import aurona.config as config
from aurona.logger import info, warn, error
from aurona.im.weixin_oc import login
from aurona.im.weixin_oc.common import notify_start, notify_stop
from aurona.im.weixin_oc.receive import run_long_poll_loop
from aurona.im.weixin_oc.send import send_text

client: openai.OpenAIConnection | None = None
model: str | None = None
history = []


def loop():
    # 程序的主循环，将一直监听消息并回答
    def generate_answer(
        history: list, client: openai.OpenAIConnection, model: str
    ) -> list:
        try:
            answer = client.get_completions(history, model)
            return [True, answer]
        except OpenAIError as e:
            return [False, e]

    def on_message(msg):
        global history
        text = ""
        for item in msg.get("item_list", []):
            ti = item.get("text_item")
            if ti:
                text = ti.get("text", "")
                break
        user_id = msg.get("from_user_id", "")
        if user_id and text:
            if text == "/new":
                history = []
                send_text(user_id, f"Reset conversation history.")
                return

            if client is None or model is None:
                warn("Client or model not initialized")
                return
            info(f"Received msg: {text}")
            history.append({"role": "user", "content": text})
            try:
                answer = client.get_completions(history, model)
                history.append(answer)
            except OpenAIError as e:
                warn(str(e))
                send_text(user_id, f"API Request Failed: {e}")
                return
            send_text(user_id, answer.content)
            # send_text(user_id, f"Hello: {text}")
            info(f"Replied to {user_id}: {answer.content}")
        else:
            warn(f"Skipping msg: user_id={user_id} text={text!r}")

    try:
        resp = notify_start()
        info(f"notifyStart: ret={resp.get('ret')}")
    except Exception as e:
        warn(f"notifyStart failed (ignored): {e}")

    def shutdown(sig, frame):
        info("Shutting down...")
        try:
            notify_stop()
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    info("Starting message loop...")
    run_long_poll_loop(on_message=on_message)


def main():
    global client, model
    info(f"Welcome to Aurona (version {__version__})")

    if len(sys.argv) <= 1:
        warn("Nothing to do!")
        return 1

    if sys.argv[1] == "connect":
        login.connect()
    elif sys.argv[1] == "run":
        conf = config.load_config()
        if isinstance(conf, int):
            error("File not found!")
            return 1

        if not config.check_schema(conf):
            error("Invalid config file")
            return 1

        client = openai.OpenAIConnection(
            conf["provider"]["baseurl"], conf["provider"]["apikey"]
        )
        model = conf["provider"]["model"]
        loop()
