import requests
from .nse import BASE, _HEADERS, CONTRACT_INFO_URL


def fetch_expiries(symbol: str) -> list:
    s = requests.Session()
    s.headers.update(_HEADERS)
    s.get(BASE, timeout=10)
    r = s.get(CONTRACT_INFO_URL, params={"symbol": symbol}, timeout=10)
    r.raise_for_status()
    data = r.json()
    expiries = data.get("expiryDates") or data.get("records", {}).get("expiryDates") or []
    return expiries
