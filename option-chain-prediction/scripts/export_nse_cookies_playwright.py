from playwright.sync_api import sync_playwright
import json
from pathlib import Path

OUT = Path("data/nse_cookies.json")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.nseindia.com/option-chain", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    cookies = page.context.cookies()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(cookies, indent=2))
    print("Saved", OUT)
    browser.close()
