import json


def load_config(config_path="data/config.json"):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return -1


def check_schema(handle: dict) -> bool:
    if not handle.get("provider"):
        return False
    if (
        not handle["provider"].get("name")
        or not handle["provider"].get("baseurl")
        or not handle["provider"].get("apikey")
    ):
        return False
    return True
