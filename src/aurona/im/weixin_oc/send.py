import time
import random
from aurona.logger import info, error
from aurona.im.weixin_oc.common import _load_auth, _post


def _generate_client_id() -> str:
    ts = int(time.time() * 1000)
    hex_part = format(random.getrandbits(32), "08x")
    return f"aurona:{ts}-{hex_part}"


def send_text(to_user_id: str, text: str):
    auth = _load_auth()

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

    data = _post("ilink/bot/sendmessage", body, auth["token"])
    if data.get("ret") and data["ret"] != 0:
        error(f"sendMessage failed: ret={data.get('ret')} errmsg={data.get('errmsg')}")
    else:
        info(f"Message sent to {to_user_id}")
