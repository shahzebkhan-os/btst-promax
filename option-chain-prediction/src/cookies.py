import json
import os
from typing import Dict


def load_cookies() -> Dict[str, str]:
    """Load cookies from env NSE_COOKIES_JSON or file NSE_COOKIES_FILE."""
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
