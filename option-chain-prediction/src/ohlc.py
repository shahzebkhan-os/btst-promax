import requests
import pandas as pd
from datetime import datetime, timedelta

BASE = "https://www.nseindia.com"
HIST_URL = BASE + "/api/historical/cm/equity"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "*/*",
    "Connection": "keep-alive",
}


def fetch_ohlc(symbol: str, days: int = 60) -> pd.DataFrame:
    s = requests.Session()
    s.headers.update(_HEADERS)
    s.get(BASE)
    to_date = datetime.utcnow().date()
    from_date = to_date - timedelta(days=days)
    params = {
        "symbol": symbol,
        "from": from_date.strftime("%d-%m-%Y"),
        "to": to_date.strftime("%d-%m-%Y"),
        "series": "EQ",
    }
    r = s.get(HIST_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json().get("data", [])
    df = pd.DataFrame(data)
    if df.empty:
        return df
    df = df.rename(columns={
        "CH_TIMESTAMP": "date",
        "CH_OPENING_PRICE": "open",
        "CH_TRADE_HIGH_PRICE": "high",
        "CH_TRADE_LOW_PRICE": "low",
        "CH_CLOSING_PRICE": "close",
        "CH_TOT_TRADED_QTY": "volume",
    })
    df["date"] = pd.to_datetime(df["date"], format="%d-%b-%Y")
    return df[["date","open","high","low","close","volume"]].sort_values("date")
