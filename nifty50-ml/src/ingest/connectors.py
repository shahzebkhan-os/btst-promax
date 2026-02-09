import os, time
import pandas as pd
import yfinance as yf
import requests
from pathlib import Path

NSE_BASE = "https://www.nseindia.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}


def _session():
    s = requests.Session()
    s.headers.update(HEADERS)
    s.get(NSE_BASE, timeout=10)
    return s


def fetch_yahoo_ohlc(symbol: str, period="60d", interval="15m"):
    data = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)
    return data.reset_index()


def fetch_nse_option_chain(symbol: str, expiry: str = ""):
    s = _session()
    url = NSE_BASE + "/api/option-chain-v3"
    params = {"symbol": symbol, "type": "Indices" if symbol in ["NIFTY","BANKNIFTY","FINNIFTY"] else "Equity"}
    if expiry:
        params["expiry"] = expiry
    r = s.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


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
    r = s.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def save_parquet(df: pd.DataFrame, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
