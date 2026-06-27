import json
import os
import random
import base64
import time

import requests
from aurona.logger import info, warn, error

BASE_URL = "https://ilinkai.weixin.qq.com"
QR_LONG_POLL_TIMEOUT_MS = 35_000
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


def _save_auth(data: dict):
    with open(AUTH_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.chmod(AUTH_FILE, 0o600)
    info(f"Credentials saved to {AUTH_FILE}")


def fetch_qrcode() -> str | None:
    info("Fetching QRCode...")
    url = f"{BASE_URL}/ilink/bot/get_bot_qrcode?bot_type=3"
    resp = requests.post(url, headers=_build_headers(), json={"local_token_list": []})
    # print(resp.status_code)
    if resp.ok:
        data = resp.json()
        if data.get("ret") == 0:
            qrcode_url = data.get("qrcode_img_content", "")
            info(f"Scan this QR code or visit: {qrcode_url}")
            return data.get("qrcode")
        else:
            error(f"API error: ret={data.get('ret')}")
    else:
        error(f"Failed: {resp.text}")
    return None


def poll_qr_status(qrcode: str) -> dict:
    url = f"{BASE_URL}/ilink/bot/get_qrcode_status?qrcode={qrcode}"
    resp = requests.get(
        url, headers=_build_headers(), timeout=QR_LONG_POLL_TIMEOUT_MS / 1000
    )
    if resp.ok:
        return resp.json()
    return {"status": "wait"}


def connect():
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
        except Exception as e:
            error(f"Polling error: {e}")
            return

        time.sleep(1)

    error("Login timed out.")
