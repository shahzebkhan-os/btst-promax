import requests
import json
from datetime import datetime

def get_nse_data_alternative():
    """
    Try alternative approaches to get NSE data
    """
    # Headers with more realistic browser settings
    headers = {
        'authority': 'www.nseindia.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    # Start a session
    sess = requests.Session()
    sess.headers.update(headers)
    
    try:
        # First visit the main page to establish session
        main_page = sess.get("https://www.nseindia.com", timeout=10)
        print(f"Main page status: {main_page.status_code}")
        
        # Then visit the option chain page
        oc_page = sess.get("https://www.nseindia.com/option-chain", timeout=10)
        print(f"Option chain page status: {oc_page.status_code}")
        
        # Now try to get the API data
        api_headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'referer': 'https://www.nseindia.com/option-chain',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        
        # Try different symbols
        symbols = ['NIFTY', 'BANKNIFTY']
        for symbol in symbols:
            url = f'https://www.nseindia.com/api/option-chain-indices?symbol={symbol}'
            print(f"\nTrying {symbol}...")
            
            response = sess.get(url, headers=api_headers, timeout=10)
            print(f"Response status: {response.status_code}")
            print(f"Response length: {len(response.text)}")
            
            if len(response.text) > 2:  # Not just "{}"
                try:
                    data = response.json()
                    print(f"Success! Got data with keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    if 'records' in data and 'data' in data['records']:
                        print(f"Found {len(data['records']['data'])} options records")
                        return data
                    else:
                        print(f"Data structure: {data}")
                except json.JSONDecodeError:
                    print(f"Not JSON: {response.text[:200]}")
            else:
                print("Empty response received")
        
        # If the above doesn't work, try using requests with session cookies manually
        print("\n--- Trying with manual cookie handling ---")
        
        # Get cookies from initial request
        cookies = dict(main_page.cookies)
        print(f"Main page cookies: {list(cookies.keys())}")
        
        # Use these cookies for API call
        for symbol in symbols:
            url = f'https://www.nseindia.com/api/option-chain-indices?symbol={symbol}'
            resp = requests.get(url, headers=api_headers, cookies=cookies, timeout=10)
            print(f"{symbol} with cookies - Status: {resp.status_code}, Length: {len(resp.text)}")
            
            if len(resp.text) > 2:
                try:
                    data = resp.json()
                    print(f"Success with {symbol} using cookies!")
                    return data
                except:
                    print(f"Non-JSON response: {resp.text[:200]}")
    
    except Exception as e:
        print(f"Error in alternative approach: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return None

def main():
    print("🔍 Trying Alternative NSE Data Access Method")
    print("="*50)
    
    data = get_nse_data_alternative()
    
    if data:
        print("\n✅ SUCCESS: Got live NSE option chain data!")
        # Display some basic info
        if 'records' in data:
            underlying = data['records'].get('underlyingValue', 'Unknown')
            timestamp = data['records'].get('timestamp', 'Unknown')
            print(f"Underlying Value: {underlying}")
            print(f"Timestamp: {timestamp}")
            
            if 'expiryDates' in data['records']:
                expiries = data['records']['expiryDates']
                print(f"Expiry Dates: {expiries[:3]}")  # First 3
            
            if 'data' in data['records']:
                total_options = len(data['records']['data'])
                print(f"Total Options: {total_options}")
    else:
        print("\n❌ Unable to fetch live data from NSE")
        print("This could be due to:")
        print("  - Market closed (outside trading hours)")
        print("  - API restrictions/changes")
        print("  - Anti-bot measures")
        print()
        print("💡 SOLUTIONS:")
        print("  - Check live prices on Zerodha/Kite during market hours")
        print("  - Try again during trading hours (9:15 AM - 3:30 PM IST)")
        print("  - Use browser automation during market hours")
    
    print(f"\n📅 Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")

if __name__ == "__main__":
    main()