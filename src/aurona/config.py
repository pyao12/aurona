"""配置文件加载与校验。"""

import json


def load_config(config_path="data/config.json") -> dict | int:
    """从 *config_path* 加载 JSON 配置；文件不存在时返回 -1。"""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return -1
    except json.JSONDecodeError:
        return -1
    except PermissionError:
        return -1
    except OSError:
        return -1


def check_schema(handle: dict) -> bool:
    """校验配置是否包含必需的 provider 字段。"""
    if not handle.get("provider"):
        return False
    if (
        not handle["provider"].get("name")
        or not handle["provider"].get("baseurl")
        or not handle["provider"].get("apikey")
        or not handle["provider"].get("model")
    ):
        return False
    return True
