import random
import base64
import json
import requests

BASE_URL = "https://ilinkai.weixin.qq.com"
AUTH_FILE = "data/auth_weixin_oc.json"


def _random_wechat_uin() -> str:
    return base64.encodebytes(str(random.getrandbits(32)).encode()).decode().strip()


def _build_headers() -> dict:
    return {
        "Content-Type": "application/json",
        "AuthorizationType": "ilink_bot_token",
        "X-WECHAT-UIN": _random_wechat_uin(),
        "iLink-App-Id": "bot",
        "iLink-App-ClientVersion": "0",
    }


def _load_auth() -> dict:
    with open(AUTH_FILE) as f:
        return json.load(f)


def _post(
    endpoint: str, body: dict, token: str | None = None, timeout: int = 10
) -> dict:
    headers = _build_headers()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.post(
        f"{BASE_URL}/{endpoint}",
        headers=headers,
        json=body,
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()


def notify_start():
    auth = _load_auth()
    return _post(
        "ilink/bot/msg/notifystart",
        {"base_info": {"channel_version": "aurona", "bot_agent": "aurona"}},
        auth["token"],
    )


def notify_stop():
    auth = _load_auth()
    return _post(
        "ilink/bot/msg/notifystop",
        {"base_info": {"channel_version": "aurona", "bot_agent": "aurona"}},
        auth["token"],
    )
