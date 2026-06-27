import time
from aurona.logger import info, error
from aurona.im.weixin_oc.common import _load_auth, _post

LONG_POLL_TIMEOUT_S = 35


def get_updates(buf: str = "") -> dict:
    auth = _load_auth()
    body = {
        "get_updates_buf": buf,
        "base_info": {"channel_version": "aurona", "bot_agent": "aurona"},
    }
    return _post(
        "ilink/bot/getupdates", body, auth["token"], timeout=LONG_POLL_TIMEOUT_S
    )


def receive_latest_message(buf: str = "") -> dict | None:
    data = get_updates(buf)
    msgs = data.get("msgs", [])
    if msgs:
        return msgs[-1]
    return None


def run_long_poll_loop(buf: str = "", on_message=None, max_rounds: int = 0):
    rounds = 0
    while True:
        try:
            data = get_updates(buf)
            buf = data.get("get_updates_buf", buf)
            msgs = data.get("msgs", [])
            info(f"Poll #{rounds}: msgs={len(msgs)}")
            for msg in msgs:
                if on_message:
                    on_message(msg)
        except Exception as e:
            error(f"Poll #{rounds} error: {e}")
        rounds += 1
        if max_rounds > 0 and rounds >= max_rounds:
            break
        time.sleep(1)
