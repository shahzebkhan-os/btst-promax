#!/usr/bin/env python3
"""
Bulk NSE option chain scraper for all F&O stocks.
- 2 expiries (nearest + next)
- 5 strikes up/down around ATM
- API first, fallback stub for browser DOM (OpenClaw) if API returns {}
Saves CSV in workspace.
"""
import csv
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests

BASE = "https://www.nseindia.com"
OC_PAGE = f"{BASE}/option-chain"
FNO_LIST_URL = f"{BASE}/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O"

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en,gu;q=0.9,hi;q=0.8",
    "referer": OC_PAGE,
}


def init_session() -> requests.Session:
    sess = requests.Session()
    sess.headers.update(HEADERS)
    # visit option-chain page to set cookies
    sess.get(OC_PAGE)
    return sess


def get_fno_symbols(sess: requests.Session) -> List[str]:
    # refresh cookies
    sess.get(OC_PAGE)
    resp = sess.get(FNO_LIST_URL)
    if resp.status_code != 200:
        raise RuntimeError(f"F&O list status {resp.status_code}")
    try:
        data = resp.json()
    except Exception:
        # try once more after cookie refresh
        sess.get(OC_PAGE)
        resp = sess.get(FNO_LIST_URL)
        data = resp.json()
    symbols = []
    for item in data.get("data", []):
        sym = item.get("symbol")
        if sym:
            symbols.append(sym)
    return sorted(set(symbols))


def safe_get_contract_info(sess: requests.Session, symbol: str) -> Optional[Dict]:
    url = f"{BASE}/api/option-chain-contract-info?symbol={symbol}"
    try:
        resp = sess.get(url, timeout=5)
        if resp.status_code != 200:
            return None
        if resp.text.strip() == "{}":
            return {}
        return resp.json()
    except Exception:
        return None


def safe_get_chain_v3(sess: requests.Session, symbol: str, expiry: str) -> Optional[Dict]:
    url = f"{BASE}/api/option-chain-v3?type=Equities&symbol={symbol}&expiry={expiry}"
    try:
        resp = sess.get(url, timeout=5)
        if resp.status_code != 200:
            return None
        if resp.text.strip() == "{}":
            return {}
        return resp.json()
    except Exception:
        return None


def fallback_chain_via_browser(symbol: str) -> Optional[Dict]:
    """
    Placeholder for OpenClaw browser DOM fallback.
    In subagent context, actual fallback should be performed by main agent
    using OpenClaw browser tool if API returns {} for a symbol.
    """
    return None


def pick_expiries(contract_info: Dict) -> List[str]:
    expiries = contract_info.get("expiryDates", [])
    return expiries[:2]


def extract_strikes_for_expiry(chain: Dict, expiry: str) -> List[Dict]:
    data = chain.get("records", {}).get("data", [])
    # v3 uses key expiryDates
    return [d for d in data if d.get("expiryDates") == expiry or d.get("expiryDate") == expiry]


def get_atm_strike(strike_prices: List[float], underlying: float) -> float:
    return min(strike_prices, key=lambda s: abs(s - underlying))


def slice_strikes_around_atm(strikes_sorted: List[float], atm: float, depth: int = 5) -> List[float]:
    idx = strikes_sorted.index(atm)
    start = max(0, idx - depth)
    end = min(len(strikes_sorted) - 1, idx + depth)
    return strikes_sorted[start : end + 1]


def flatten_row(
    symbol: str,
    expiry: str,
    underlying: float,
    strike: float,
    ce: Optional[Dict],
    pe: Optional[Dict],
    timestamp: str,
) -> Dict:
    def g(side: Optional[Dict], key: str):
        return "" if side is None else side.get(key, "")

    return {
        "timestamp": timestamp,
        "symbol": symbol,
        "expiry": expiry,
        "underlying": underlying,
        "strike": strike,
        "ce_openInterest": g(ce, "openInterest"),
        "ce_changeinOI": g(ce, "changeinOpenInterest"),
        "ce_totalTradedVolume": g(ce, "totalTradedVolume"),
        "ce_impliedVolatility": g(ce, "impliedVolatility"),
        "ce_lastPrice": g(ce, "lastPrice"),
        "ce_change": g(ce, "change"),
        "ce_bidQty": g(ce, "bidQty"),
        "ce_bidprice": g(ce, "bidprice"),
        "ce_askPrice": g(ce, "askPrice"),
        "ce_askQty": g(ce, "askQty"),
        "pe_openInterest": g(pe, "openInterest"),
        "pe_changeinOI": g(pe, "changeinOpenInterest"),
        "pe_totalTradedVolume": g(pe, "totalTradedVolume"),
        "pe_impliedVolatility": g(pe, "impliedVolatility"),
        "pe_lastPrice": g(pe, "lastPrice"),
        "pe_change": g(pe, "change"),
        "pe_bidQty": g(pe, "bidQty"),
        "pe_bidprice": g(pe, "bidprice"),
        "pe_askPrice": g(pe, "askPrice"),
        "pe_askQty": g(pe, "askQty"),
    }


def main():
    sess = init_session()
    try:
        symbols = get_fno_symbols(sess)
    except Exception as e:
        print(f"Failed to fetch F&O list: {e}")
        sys.exit(1)

    timestamp = datetime.utcnow().isoformat()
    rows: List[Dict] = []
    missing_symbols: List[str] = []

    for i, symbol in enumerate(symbols, 1):
        if i % 20 == 0:
            print(f"Progress {i}/{len(symbols)}: {symbol}")

        contract_info = safe_get_contract_info(sess, symbol)
        if contract_info == {}:
            missing_symbols.append(symbol)
            continue
        if not contract_info or "expiryDates" not in contract_info:
            missing_symbols.append(symbol)
            continue

        expiries = pick_expiries(contract_info)
        if not expiries:
            missing_symbols.append(symbol)
            continue

        for expiry in expiries:
            chain = safe_get_chain_v3(sess, symbol, expiry)
            if chain == {} or not chain or "records" not in chain:
                missing_symbols.append(symbol)
                continue

            underlying = chain.get("records", {}).get("underlyingValue")
            if underlying is None:
                missing_symbols.append(symbol)
                continue

            exp_data = extract_strikes_for_expiry(chain, expiry)
            if not exp_data:
                continue
            strikes = sorted({d.get("strikePrice") for d in exp_data if d.get("strikePrice") is not None})
            if not strikes:
                continue
            atm = get_atm_strike(strikes, underlying)
            use_strikes = slice_strikes_around_atm(strikes, atm, depth=5)

            # map strike->entry
            by_strike = {d.get("strikePrice"): d for d in exp_data}

            for strike in use_strikes:
                entry = by_strike.get(strike, {})
                ce = entry.get("CE")
                pe = entry.get("PE")
                rows.append(flatten_row(symbol, expiry, underlying, strike, ce, pe, timestamp))

        # light throttle to avoid blocks
        if i % 10 == 0:
            time.sleep(0.5)

    out_path = f"/Users/aayan/.openclaw/workspace/nse_fno_option_chain_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    if rows:
        with open(out_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    summary = {
        "symbols_total": len(symbols),
        "rows": len(rows),
        "missing_symbols": missing_symbols,
        "csv_path": out_path if rows else "",
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
