"""微信 OC 长轮询消息接收器。"""

import json
import time
import requests

from aurona.im.weixin_oc.common import _load_auth, _post
from aurona.logger import error, info

LONG_POLL_TIMEOUT_S = 35


def get_updates(buf: str = "") -> dict:
    """从微信 OC 服务器拉取待处理的更新。"""
    try:
        auth = _load_auth()
    except (FileNotFoundError, json.JSONDecodeError, PermissionError, OSError) as exc:
        raise RuntimeError(f"Failed to load auth for polling: {exc}") from exc
    body = {
        "get_updates_buf": buf,
        "base_info": {"channel_version": "aurona", "bot_agent": "aurona"},
    }
    return _post(
        "ilink/bot/getupdates", body, auth["token"], timeout=LONG_POLL_TIMEOUT_S
    )


def receive_latest_message(buf: str = "") -> dict | None:
    """返回最近一条消息，无消息时返回 ``None``。"""
    try:
        data = get_updates(buf)
        msgs = data.get("msgs", [])
        if msgs:
            return msgs[-1]
    except (RuntimeError, requests.RequestException, ValueError) as exc:
        error(f"Failed to receive latest message: {exc}")
    return None


def run_long_poll_loop(buf: str = "", on_message=None, max_rounds: int = 0):
    """持续轮询新消息，每收到一条调用 *on_message*。"""
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
        except Exception as exc:  # pylint: disable=broad-exception-caught
            error(f"Poll #{rounds} error: {exc}")
        rounds += 1
        if 0 < max_rounds <= rounds:
            break
        time.sleep(1)
