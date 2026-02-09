import requests
import pandas as pd
from .cookies import load_cookies

BASE = "https://www.nseindia.com"
CHAIN_URL = BASE + "/api/option-chain-v3"
OHLC_URL = BASE + "/api/quote-equity?symbol={symbol}"
SYMBOLS_URL = BASE + "/api/underlying-information"
CONTRACT_INFO_URL = BASE + "/api/option-chain-contract-info"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.nseindia.com/option-chain",
}


def _get_session():
    s = requests.Session()
    s.headers.update(_HEADERS)
    s.get(BASE, timeout=10)  # prime cookies
    # optional browser cookies
    cookies = load_cookies()
    if cookies:
        s.cookies.update(cookies)
    return s


def fetch_option_chain(symbol: str, is_index: bool = True, expiry: str = "", retries: int = 3) -> dict:
    s = _get_session()
    params = {"symbol": symbol, "type": "Indices" if is_index else "Equity"}
    if expiry:
        params["expiry"] = expiry

    last_err = None
    for _ in range(retries):
        try:
            r = s.get(CHAIN_URL, params=params, timeout=10)
            if r.status_code == 401:
                s = _get_session()
                r = s.get(CHAIN_URL, params=params, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e
            continue
    raise last_err


def parse_chain_to_df(chain_json: dict) -> pd.DataFrame:
    records = chain_json.get("records", {}) or chain_json.get("data", {})
    data = records.get("data", []) if isinstance(records, dict) else chain_json.get("data", [])
    underlying = records.get("underlyingValue") if isinstance(records, dict) else None
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
                "underlying": underlying,
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
                "underlying": underlying,
            })
    return pd.DataFrame(rows)
