import requests
import pandas as pd

BASE = "https://www.nseindia.com"
CHAIN_URL = BASE + "/api/option-chain-indices"
EQ_CHAIN_URL = BASE + "/api/option-chain-equities"
OHLC_URL = BASE + "/api/quote-equity?symbol={symbol}"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "*/*",
    "Connection": "keep-alive",
}


def _get_session():
    s = requests.Session()
    s.headers.update(_HEADERS)
    s.get(BASE)  # prime cookies
    return s


def fetch_option_chain(symbol: str, is_index: bool = True) -> dict:
    s = _get_session()
    url = CHAIN_URL if is_index else EQ_CHAIN_URL
    r = s.get(url, params={"symbol": symbol}, timeout=10)
    r.raise_for_status()
    return r.json()


def parse_chain_to_df(chain_json: dict) -> pd.DataFrame:
    data = chain_json.get("records", {}).get("data", [])
    rows = []
    for row in data:
        ce = row.get("CE", {})
        pe = row.get("PE", {})
        strike = row.get("strikePrice")
        expiry = row.get("expiryDate")
        if ce:
            rows.append({
                "type": "CE",
                "strike": strike,
                "expiry": expiry,
                "iv": ce.get("impliedVolatility"),
                "oi": ce.get("openInterest"),
                "oi_change": ce.get("changeinOpenInterest"),
                "volume": ce.get("totalTradedVolume"),
                "bid": ce.get("bidprice"),
                "ask": ce.get("askPrice"),
                "ltp": ce.get("lastPrice"),
            })
        if pe:
            rows.append({
                "type": "PE",
                "strike": strike,
                "expiry": expiry,
                "iv": pe.get("impliedVolatility"),
                "oi": pe.get("openInterest"),
                "oi_change": pe.get("changeinOpenInterest"),
                "volume": pe.get("totalTradedVolume"),
                "bid": pe.get("bidprice"),
                "ask": pe.get("askPrice"),
                "ltp": pe.get("lastPrice"),
            })
    return pd.DataFrame(rows)
