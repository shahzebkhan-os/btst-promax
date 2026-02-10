import requests
import json
import hmac
import hashlib
import time
import logging

class SmallRupeeOrderTester:
    """
    Try placing a small order of ₹200 to test if restrictions allow it
    """
    
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://api.coindcx.com"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def get_headers(self, body_json):
        """
        Generate headers for authenticated API calls
        """
        json_body = json.dumps(body_json, separators=(',', ':'))
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            json_body.encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'Content-Type': 'application/json',
            'X-AUTH-APIKEY': self.api_key,
            'X-AUTH-SIGNATURE': signature
        }
        
        return headers, json_body
    
    def get_account_balance(self):
        """
        Get account balance information
        """
        timestamp = int(round(time.time() * 1000))
        
        body = {
            "timestamp": timestamp
        }
        
        headers, json_body = self.get_headers(body)
        url = f"{self.base_url}/exchange/v1/users/balances"
        
        try:
            response = requests.post(url, data=json_body, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching account balance: {e}")
            return None
    
    def get_market_details(self, symbol):
        """
        Get details for a specific market
        """
        url = f"{self.base_url}/exchange/v1/markets_details"
        try:
            response = requests.get(url)
            response.raise_for_status()
            markets = response.json()
            
            for market in markets:
                if market['symbol'] == symbol:
                    return market
        except Exception as e:
            self.logger.error(f"Error fetching market details: {e}")
            return None
    
    def get_ticker_data(self, symbol):
        """
        Get ticker data for a specific symbol
        """
        url = f"{self.base_url}/exchange/ticker"
        try:
            response = requests.get(url)
            response.raise_for_status()
            ticker_data = response.json()
            
            for item in ticker_data:
                if item['market'] == symbol:
                    return item
        except Exception as e:
            self.logger.error(f"Error fetching ticker for {symbol}: {e}")
            return None
    
    def place_rupee_order(self, market, target_rupees=200):
        """
        Place an order for approximately the target rupee amount
        """
        timestamp = int(round(time.time() * 1000))
        
        # Get market details
        market_details = self.get_market_details(market)
        if not market_details:
            self.logger.error(f"Could not get market details for {market}")
            return None
        
        # Get current price
        ticker_data = self.get_ticker_data(market)
        if not ticker_data:
            self.logger.error(f"Could not get ticker data for {market}")
            return None
        
        current_price = float(ticker_data['last_price'])
        
        # Calculate quantity for target rupee amount
        desired_quantity = target_rupees / current_price
        
        # Apply market minimums
        min_quantity = market_details.get('min_quantity', 0.001)
        min_notional = market_details.get('min_notional', 100)  # Minimum order value in base currency
        
        # Ensure we meet minimum notional requirement
        if desired_quantity * current_price < min_notional:
            desired_quantity = min_notional / current_price
        
        # Apply market precision
        precision = market_details.get('target_currency_precision', 2)
        multiplier = 10 ** precision
        final_quantity = int(desired_quantity * multiplier) / multiplier
        
        # Ensure we meet minimum quantity
        final_quantity = max(final_quantity, min_quantity)
        
        # Prepare the order
        body = {
            "side": "buy",
            "order_type": "market_order",
            "market": market,
            "total_quantity": final_quantity,
            "timestamp": timestamp
        }
        
        headers, json_body = self.get_headers(body)
        url = f"{self.base_url}/exchange/v1/orders/create"
        
        print(f"\n📊 **₹{target_rupees} ORDER FOR {market}**:")
        print(f"   Current Price: ₹{current_price}")
        print(f"   Desired Amount: ₹{target_rupees}")
        print(f"   Calculated Quantity: {desired_quantity}")
        print(f"   Final Quantity: {final_quantity}")
        print(f"   Actual Order Value: ₹{final_quantity * current_price:.2f}")
        print(f"   Min Quantity: {min_quantity}")
        print(f"   Min Notional: ₹{min_notional}")
        print(f"   Precision: {precision}")
        
        try:
            response = requests.post(url, data=json_body, headers=headers)
            result = response.json()
            self.logger.info(f"Order result for {market}: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Order failed for {market}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_response = e.response.json()
                    self.logger.error(f"Error response: {error_response}")
                    return error_response
                except:
                    self.logger.error(f"Raw error response: {e.response.text}")
            return None
    
    def try_rupee_orders(self):
        """
        Try to place orders for ₹200 on different markets
        """
        print("💰 **TRYING ₹200 ORDERS TO TEST RESTRICTIONS**")
        print("=" * 50)
        
        # Get account balance to confirm we have funds
        balance = self.get_account_balance()
        if not balance:
            print("❌ Could not retrieve account balance")
            return None
        
        # Find INR balance
        inr_balance = 0
        for item in balance:
            if item['currency'] == 'INR':
                inr_balance = float(item['balance']) + float(item['locked_balance'])
                break
        
        print(f"Available INR: ₹{inr_balance}")
        
        if inr_balance < 200:
            print("❌ Insufficient balance for ₹200 orders")
            return None
        
        # Test markets that might be less restricted
        test_markets = [
            "XRPINR",    # Mid-cap with good volume
            "ADAUSDT",   # Using USDT pair
            "DOTINR",    # Mid-cap with good volume
            "LINKINR",   # Mid-cap with good volume
        ]
        
        results = {}
        
        for market in test_markets:
            print(f"\n🛒 Testing ₹200 order for {market}...")
            result = self.place_rupee_order(market, target_rupees=200)
            results[market] = result
            
            if result and 'orders' in str(result).lower():
                print(f"   ✅ SUCCESS: ₹200 order placed for {market}")
            else:
                print(f"   ❌ FAILED: {result.get('message', 'Unknown error') if isinstance(result, dict) else 'Error occurred'}")
        
        print(f"\n📋 **₹200 ORDER RESULTS**:")
        print("=" * 35)
        for market, result in results.items():
            status = "✅ SUCCESS" if result and 'orders' in str(result).lower() else "❌ FAILED"
            msg = result.get('message', 'Unknown') if isinstance(result, dict) else 'Error'
            print(f"   {market}: {status} - {msg}")
        
        return results

def main():
    """
    Main function to try ₹200 orders
    """
    print("💸 **ATTEMPTING ₹200 ORDERS TO TEST TRADING RESTRICTIONS**")
    print("=" * 65)
    
    # Load credentials
    import json
    from pathlib import Path
    
    creds_file = Path.home() / '.coindcx_secrets.json'
    if not creds_file.exists():
        print("Error: Credentials file not found.")
        return
    
    with open(creds_file, 'r') as f:
        creds = json.load(f)
    
    tester = SmallRupeeOrderTester(creds['api_key'], creds['secret_key'])
    
    # Try ₹200 orders
    results = tester.try_rupee_orders()
    
    print(f"\n🔍 **ANALYSIS**:")
    print("=" * 15)
    
    success_count = sum(1 for result in results.values() if result and 'orders' in str(result).lower())
    if success_count > 0:
        print(f"🎉 SUCCESS: {success_count} out of {len(results)} attempts worked!")
        print(f"You can place small trades on these markets.")
    else:
        print(f"❌ CONTINUED RESTRICTIONS: No ₹200 orders succeeded")
        print(f"The account still has comprehensive trading restrictions.")
        print(f"You'll need to contact Coindcx support to resolve these issues.")
    
    print(f"\n💡 **RECOMMENDATION**:")
    print("=" * 20)
    print(f"Since API orders are still restricted, use the web interface:")
    print(f"1. Open your Brave browser")
    print(f"2. Go to coindcx.com")
    print(f"3. Login and trade directly through the website")
    print(f"4. This bypasses API restrictions and gives full trading access")

if __name__ == "__main__":
    main()