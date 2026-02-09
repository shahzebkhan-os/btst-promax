import json
import os

def load_cookies():
    raw = os.environ.get("NSE_COOKIES_JSON")
    if raw:
        try:
            data = json.loads(raw)
            return {c.get("name"): c.get("value") for c in data if c.get("name")}
        except Exception:
            return {}
    path = os.environ.get("NSE_COOKIES_FILE")
    if path and os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
            return {c.get("name"): c.get("value") for c in data if c.get("name")}
        except Exception:
            return {}
    return {}
