import requests

NSE_BASE = "https://www.nseindia.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_optionable_universe():
    s = requests.Session()
    s.headers.update(HEADERS)
    s.get(NSE_BASE, timeout=10)
    # NSE underlying-information endpoint
    r = s.get(NSE_BASE + "/api/underlying-information", timeout=10)
    r.raise_for_status()
    data = r.json().get("data", {})
    stocks = [x["symbol"] for x in data.get("UnderlyingList", [])]
    return stocks
