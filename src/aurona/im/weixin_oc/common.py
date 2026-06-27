"""微信 OC 公共工具函数（基础 URL、认证、HTTP 请求）。"""

import base64
import json
import random

import requests

BASE_URL = "https://ilinkai.weixin.qq.com"
AUTH_FILE = "data/auth_weixin_oc.json"


def _random_wechat_uin() -> str:
    """返回随机生成的 Base64 编码微信 UIN。"""
    return base64.encodebytes(str(random.getrandbits(32)).encode()).decode().strip()


def _build_headers() -> dict:
    """构建微信 OC 请求的默认 HTTP 头。"""
    return {
        "Content-Type": "application/json",
        "AuthorizationType": "ilink_bot_token",
        "X-WECHAT-UIN": _random_wechat_uin(),
        "iLink-App-Id": "bot",
        "iLink-App-ClientVersion": "0",
    }


def _load_auth() -> dict:
    """从磁盘加载已保存的认证数据。"""
    try:
        with open(AUTH_FILE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise
    except (json.JSONDecodeError, PermissionError, OSError) as exc:
        raise OSError(f"Failed to load auth file: {exc}") from exc


def _post(
    endpoint: str, body: dict, token: str | None = None, timeout: int = 10
) -> dict:
    """向 *endpoint* 发送 POST 请求，可携带 Bearer *token*。"""
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
    """通知微信 OC 服务器：机器人即将启动。"""
    try:
        auth = _load_auth()
    except (FileNotFoundError, json.JSONDecodeError, PermissionError, OSError) as exc:
        raise RuntimeError(f"notify_start auth failed: {exc}") from exc
    try:
        return _post(
            "ilink/bot/msg/notifystart",
            {"base_info": {"channel_version": "aurona", "bot_agent": "aurona"}},
            auth["token"],
        )
    except (requests.RequestException, requests.Timeout, ValueError) as exc:
        raise RuntimeError(f"notify_start failed: {exc}") from exc


def notify_stop():
    """通知微信 OC 服务器：机器人即将停止。"""
    try:
        auth = _load_auth()
    except (FileNotFoundError, json.JSONDecodeError, PermissionError, OSError) as exc:
        raise RuntimeError(f"notify_stop auth failed: {exc}") from exc
    try:
        return _post(
            "ilink/bot/msg/notifystop",
            {"base_info": {"channel_version": "aurona", "bot_agent": "aurona"}},
            auth["token"],
        )
    except (requests.RequestException, requests.Timeout, ValueError) as exc:
        raise RuntimeError(f"notify_stop failed: {exc}") from exc
