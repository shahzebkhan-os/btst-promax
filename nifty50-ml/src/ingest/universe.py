import requests

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


def fetch_nifty_components():
    """Fetch NIFTY 50 constituents; fallback to static list if NSE API fails."""
    s = _session()
    try:
        r = s.get(NSE_BASE + "/api/equity-stockIndices", params={"index": "NIFTY 50"}, timeout=10)
        r.raise_for_status()
        data = r.json()
        return [x.get("symbol") for x in data.get("data", []) if x.get("symbol")]
    except Exception:
        return [
            "ADANIPORTS","ASIANPAINT","AXISBANK","BAJAJ-AUTO","BAJFINANCE","BAJAJFINSV",
            "BPCL","BHARTIARTL","BRITANNIA","CIPLA","COALINDIA","DIVISLAB","DRREDDY",
            "EICHERMOT","GRASIM","HCLTECH","HDFCBANK","HDFCLIFE","HEROMOTOCO",
            "HINDALCO","HINDUNILVR","ICICIBANK","INDUSINDBK","INFY","ITC",
            "JSWSTEEL","KOTAKBANK","LT","M&M","MARUTI","NESTLEIND",
            "NTPC","ONGC","POWERGRID","RELIANCE","SBIN","SHREECEM",
            "SUNPHARMA","TATAMOTORS","TATASTEEL","TCS","TECHM","TITAN",
            "ULTRACEMCO","UPL","WIPRO","ADANIENT","APOLLOHOSP"
        ]


def sector_indices():
    """Yahoo tickers for NSE sector indices."""
    return [
        "^NSEI",
        "^NSEBANK",
        "^CNXIT",
        "^CNXFMCG",
        "^CNXAUTO",
        "^CNXMETAL",
        "^CNXPHARMA",
        "^CNXFIN",
        "^CNXPSUBANK",
        "^CNXREALTY",
        "^CNXENERGY",
        "^CNXMEDIA",
        "^CNXINFRA",
    ]


def fetch_optionable_universe():
    s = _session()
    # NSE underlying-information endpoint (F&O underlyings)
    r = s.get(NSE_BASE + "/api/underlying-information", timeout=10)
    r.raise_for_status()
    data = r.json().get("data", {})
    stocks = [x["symbol"] for x in data.get("UnderlyingList", [])]
    nifty = fetch_nifty_components()
    indices = sector_indices()
    combined = sorted({*stocks, *nifty, *indices})
    return combined
