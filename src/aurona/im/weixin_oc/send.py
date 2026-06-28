"""通过微信 OC API 发送消息。"""

import json
import random
import time
import requests

from aurona.im.weixin_oc.common import _load_auth, _post
from aurona.logger import error, info


def _generate_client_id() -> str:
    """为出站消息生成唯一客户端 ID。"""
    ts = int(time.time() * 1000)
    hex_part = format(random.getrandbits(32), "08x")
    return f"aurona:{ts}-{hex_part}"


def send_text(to_user_id: str, text: str):
    """向 *to_user_id* 发送纯文本消息。"""
    try:
        auth = _load_auth()
    except (FileNotFoundError, json.JSONDecodeError, PermissionError, OSError) as exc:
        error(f"Failed to load auth: {exc}")
        return

    msg = {
        "from_user_id": "",
        "to_user_id": to_user_id,
        "client_id": _generate_client_id(),
        "message_type": 2,
        "message_state": 2,
        "item_list": [{"type": 1, "text_item": {"text": text}}],
    }
    body = {
        "msg": msg,
        "base_info": {"channel_version": "aurona", "bot_agent": "aurona"},
    }

    try:
        data = _post("ilink/bot/sendmessage", body, auth["token"])
    except (requests.RequestException, requests.Timeout, ValueError) as exc:
        error(f"sendMessage request failed: {exc}")
        return

    if data.get("ret") and data["ret"] != 0:
        error(f"sendMessage failed: ret={data.get('ret')} errmsg={data.get('errmsg')}")
    else:
        info(f"Message sent to {to_user_id}")
