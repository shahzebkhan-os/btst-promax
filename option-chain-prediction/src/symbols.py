import requests
import pandas as pd
from .nse import BASE, _HEADERS, SYMBOLS_URL


def fetch_symbols():
    s = requests.Session()
    s.headers.update(_HEADERS)
    s.get(BASE, timeout=10)
    r = s.get(SYMBOLS_URL, timeout=10)
    r.raise_for_status()
    data = r.json().get("data", {})
    indices = [x["symbol"] for x in data.get("IndexList", [])]
    stocks = [x["symbol"] for x in data.get("UnderlyingList", [])]
    return pd.DataFrame({"symbol": indices + stocks, "type": ["Index"]*len(indices)+["Stock"]*len(stocks)})
