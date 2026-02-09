import requests
import pandas as pd

BASE = "https://www.nseindia.com"
FO_URL = BASE + "/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "*/*",
    "Connection": "keep-alive",
}


def fetch_optionable_universe() -> pd.DataFrame:
    # primary: NSE F&O list
    s = requests.Session()
    s.headers.update(_HEADERS)
    s.get(BASE)
    r = s.get(FO_URL, timeout=10)
    r.raise_for_status()
    data = r.json().get("data", [])
    df = pd.DataFrame(data)
    if not df.empty:
        return df[["symbol", "identifier", "lastPrice", "pChange"]].dropna()
    # fallback: underlying-information
    return fetch_symbols()
