"""基于二维码的微信 OC 登录流程。"""

import json
import time

import requests

from aurona.im.weixin_oc.common import BASE_URL, _build_headers
from aurona.logger import error, info, warn

QR_LONG_POLL_TIMEOUT_MS = 35_000
AUTH_FILE = "data/auth_weixin_oc.json"


def _save_auth(data: dict):
    """将认证数据持久化到磁盘并设置受限权限。"""
    try:
        with open(AUTH_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except (PermissionError, OSError) as exc:
        error(f"Failed to save auth file: {exc}")
        return
    info(f"Credentials saved to {AUTH_FILE}")


def fetch_qrcode() -> str | None:
    """向微信 OC API 请求新的二维码。"""
    info("Fetching QRCode...")
    url = f"{BASE_URL}/ilink/bot/get_bot_qrcode?bot_type=3"
    try:
        resp = requests.post(
            url, headers=_build_headers(), json={"local_token_list": []}, timeout=10
        )
    except requests.Timeout:
        error("QRCode request timed out")
        return None
    except requests.RequestException as exc:
        error(f"QRCode request failed: {exc}")
        return None
    if resp.ok:
        data = resp.json()
        if data.get("ret") == 0:
            qrcode_url = data.get("qrcode_img_content", "")
            info(f"Visit, and scan the QRCode: {qrcode_url}")
            return data.get("qrcode")
        error(f"API error: ret={data.get('ret')}")
        return None
    error(f"Failed: {resp.text}")
    return None


def poll_qr_status(qrcode: str) -> dict:
    """轮询二维码的扫码/确认状态。"""
    url = f"{BASE_URL}/ilink/bot/get_qrcode_status?qrcode={qrcode}"
    try:
        resp = requests.get(
            url, headers=_build_headers(), timeout=QR_LONG_POLL_TIMEOUT_MS / 1000
        )
        if resp.ok:
            return resp.json()
    except requests.Timeout:
        pass
    except requests.RequestException as exc:
        error(f"Poll QR status failed: {exc}")
    return {"status": "wait"}


def connect():
    """执行完整的二维码登录流程，成功后保存凭证。"""
    qrcode = fetch_qrcode()
    if not qrcode:
        return

    info("Waiting for scan...")
    deadline = time.time() + 480

    while time.time() < deadline:
        try:
            status_resp = poll_qr_status(qrcode)
            status = status_resp.get("status")

            if status == "scaned":
                info("Scanned. Waiting for confirmation...")
            elif status == "confirmed":
                bot_token = status_resp.get("bot_token")
                bot_id = status_resp.get("ilink_bot_id")
                baseurl = status_resp.get("baseurl")
                user_id = status_resp.get("ilink_user_id")

                info(f"Login confirmed! bot_id={bot_id}")

                _save_auth(
                    {
                        "token": bot_token,
                        "bot_id": bot_id,
                        "baseurl": baseurl,
                        "user_id": user_id,
                        "saved_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    }
                )
                return
            elif status == "expired":
                error("QR code expired. Please run `aurona connect` again.")
                return
            elif status == "need_verifycode":
                warn("Verification code required (not yet supported in CLI)")
            elif status == "binded_redirect":
                info("Already connected.")
                return
        except requests.Timeout:
            pass
        except requests.RequestException as exc:
            error(f"Polling error: {exc}")
            return

        time.sleep(1)

    error("Login timed out.")
