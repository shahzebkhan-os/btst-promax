import os, time
import pandas as pd
import yfinance as yf
import requests
from pathlib import Path
from .cookies import load_cookies

NSE_BASE = "https://www.nseindia.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "Origin": "https://www.nseindia.com",
}


def _session():
    s = requests.Session()
    s.headers.update(HEADERS)
    s.get(NSE_BASE, timeout=10)
    cookies = load_cookies()
    if cookies:
        s.cookies.update(cookies)
    return s


def normalize_yahoo_symbol(symbol: str):
    if symbol.startswith("^") or symbol.endswith(".NS") or symbol.endswith(".NSE"):
        return symbol
    return symbol + ".NS"


def fetch_yahoo_ohlc(symbol: str, period="10y", interval="1d"):
    symbol = normalize_yahoo_symbol(symbol)
    data = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)
    return data.reset_index()


def fetch_kite_ltp(symbols):
    """Fetch live LTP from Kite for a list of NSE symbols. Returns dict symbol->ltp."""
    api_key = os.getenv("KITE_API_KEY")
    access_token = os.getenv("KITE_ACCESS_TOKEN")
    if not api_key or not access_token or not symbols:
        return {}
    url = "https://api.kite.trade/quote/ltp"
    headers = {"Authorization": f"token {api_key}:{access_token}"}
    out = {}
    # Kite supports multiple instruments via repeated i= param
    for i in range(0, len(symbols), 100):
        chunk = symbols[i:i+100]
        params = [("i", f"NSE:{s}") for s in chunk]
        try:
            r = requests.get(url, headers=headers, params=params, timeout=10)
            if r.status_code != 200:
                continue
            data = (r.json() or {}).get("data", {})
            for k, v in data.items():
                sym = k.split(":", 1)[-1]
                ltp = v.get("last_price") if isinstance(v, dict) else None
                if ltp is not None:
                    out[sym] = ltp
        except Exception:
            continue
    return out


def fetch_nse_option_chain(symbol: str, expiry: str = ""):
    s = _session()
    url = NSE_BASE + "/api/option-chain-v3"
    params = {"symbol": symbol, "type": "Indices" if symbol in ["NIFTY","BANKNIFTY","FINNIFTY"] else "Equity"}
    if expiry:
        params["expiry"] = expiry
    for _ in range(3):
        r = s.get(url, params=params, timeout=10)
        if r.status_code == 401:
            s = _session()
            continue
        if r.status_code == 503:
            time.sleep(1)
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()


def fetch_historical_fo(symbol: str, instrument: str, from_date: str, to_date: str,
                        expiry_date: str = "", strike: str = "", option_type: str = ""):
    """Fetch NSE historical contract-wise data (FO). Dates are dd-mm-yyyy."""
    s = _session()
    url = NSE_BASE + "/api/historical/fo/derivatives"
    params = {
        "from": from_date,
        "to": to_date,
        "instrumentType": instrument,
        "symbol": symbol,
    }
    if expiry_date:
        params["expiryDate"] = expiry_date
    if strike:
        params["strikePrice"] = strike
    if option_type:
        params["optionType"] = option_type
    for _ in range(3):
        r = s.get(url, params=params, timeout=10)
        if r.status_code == 401:
            s = _session()
            continue
        if r.status_code == 503:
            time.sleep(1)
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()


def fetch_historical_fo_range(symbol: str, instrument: str, ranges: list,
                              expiry_date: str = "", strike: str = "", option_type: str = ""):
    """Fetch FO data in chunks (NSE limit ~90 days). ranges=[("01-01-2024","31-03-2024"), ...]"""
    out = []
    for f, t in ranges:
        data = fetch_historical_fo(symbol, instrument, f, t, expiry_date, strike, option_type)
        out.extend(data.get("data", []))
    return out


def save_parquet(df: pd.DataFrame, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
