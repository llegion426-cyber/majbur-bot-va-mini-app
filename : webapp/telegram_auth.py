import hashlib
import hmac
import json
from urllib.parse import parse_qsl

from config import config


def validate_init_data(init_data: str) -> dict | None:
    """Telegram WebApp initData imzosini tekshiradi.
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
    Muvaffaqiyatli bo'lsa, {"user": {...}, ...} lug'atini qaytaradi, aks holda None."""
    if not init_data or not config.BOT_TOKEN:
        return None

    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        return None

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        return None

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", config.BOT_TOKEN.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return None

    if "user" in parsed:
        parsed["user"] = json.loads(parsed["user"])
    return parsed


def is_admin_init_data(init_data: str) -> bool:
    data = validate_init_data(init_data)
    if not data or "user" not in data:
        return False
    return data["user"].get("id") in config.ADMIN_IDS
