import sys
import os
import json
import pickle
import logging
from datetime import datetime, timedelta

# Add the directory containing the kiteconnect package to the Python path
sys.path.insert(0, '/Users/aayan/.local/lib/python3.9/site-packages')

try:
    from kiteconnect import KiteConnect
except ImportError:
    print("KiteConnect library not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "kiteconnect"])
    from kiteconnect import KiteConnect

def get_kite_connection():
    """Initialize KiteConnect with stored credentials"""
    try:
        # Load API credentials
        with open('/Users/aayan/.zerodha_creds.json', 'r') as f:
            creds = json.load(f)
        
        api_key = creds['api_key']
        api_secret = creds['api_secret']
        
        kite = KiteConnect(api_key=api_key)
        
        # Try to load stored access token
        try:
            with open('/Users/aayan/.zerodha_tokens.pkl', 'rb') as f:
                tokens = pickle.load(f)
            
            access_token = tokens.get('access_token')
            expires_at = tokens.get('expires_at')
            
            if access_token and expires_at:
                # Check if token is still valid (expires after 1 day)
                if 'T' in expires_at:
                    # Handle ISO format with timezone
                    if '+' in expires_at or expires_at.endswith('Z'):
                        expiry_time = datetime.fromisoformat(expires_at)
                    else:
                        # Parse without timezone
                        expiry_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                else:
                    # Handle different format
                    expiry_time = datetime.strptime(expires_at, '%Y-%m-%dT%H:%M:%S.%f')
                
                current_time = datetime.now()
                if current_time > expiry_time:
                    print("Access token has expired. Need to re-authenticate.")
                    return None, kite
                else:
                    kite.set_access_token(access_token)
                    print("Using existing access token")
                    return kite, kite
            else:
                print("No stored tokens found. Need to authenticate.")
                return None, kite
        except FileNotFoundError:
            print("No stored tokens found. Need to authenticate.")
            return None, kite
        except Exception as e:
            print(f"Error loading tokens: {str(e)}")
            print("Need to authenticate again.")
            return None, kite
            
    except Exception as e:
        print(f"Error initializing KiteConnect: {str(e)}")
        return None, None

def get_available_indices(kite):
    """Get available index symbols"""
    try:
        # Get all instruments
        instruments = kite.instruments()
        
        # Filter for indices and options
        indices = []
        for inst in instruments:
            if inst['segment'] in ['NSE', 'BSE'] and inst['instrument_type'] == 'EQ':
                if 'NIFTY' in inst['name'] or 'BANK' in inst['name']:
                    indices.append(inst)
        
        return indices
    except Exception as e:
        print(f"Error getting instruments: {str(e)}")
        return []

def search_instruments(kite, query):
    """Search for instruments by name"""
    try:
        instruments = kite.search_instruments('NSE', query)
        return instruments
    except Exception as e:
        print(f"Error searching instruments: {str(e)}")
        return []

def get_options_chain(kite, underlying_symbol):
    """Get options chain for a specific underlying"""
    try:
        # Get instruments for the underlying
        instruments = kite.instruments('NFO')
        
        # Filter for options of the specific underlying
        options = []
        for inst in instruments:
            if (inst['segment'] == 'NFO-OPT' and 
                underlying_symbol in inst['name']):
                
                # Only include if it's for the current or next expiry
                expiry_date = inst['expiry']
                today = datetime.today().date()
                max_expiry = today + timedelta(days=30)  # Next month
                
                if today <= expiry_date <= max_expiry:
                    options.append(inst)
        
        # Sort by expiry and strike
        options.sort(key=lambda x: (x['expiry'], x['strike']))
        
        return options
        
    except Exception as e:
        print(f"Error getting options chain for {underlying_symbol}: {str(e)}")
        return []

def display_options_chain_simple(options_data, kite, underlying):
    """Display options chain with real-time prices"""
    if not options_data:
        print("No options data available")
        return
    
    print(f"\n{'='*140}")
    print(f"OPTIONS CHAIN FOR {underlying} - REAL-TIME DATA")
    print(f"{'='*140}")
    
    # Group options by expiry
    from collections import defaultdict
    expiries = defaultdict(list)
    for opt in options_data:
        exp = opt['expiry']
        expiries[exp].append(opt)
    
    for expiry, opts in expiries.items():
        print(f"\nExpiry: {expiry.strftime('%Y-%m-%d')} ({len(opts)} contracts)")
        print(f"{'-'*140}")
        print(f"{'Symbol':<18} {'Type':<5} {'Strike':<8} {'LTP':<8} {'Chg':<8} {'Bid':<8} {'Ask':<8} {'IV':<8} {'OI':<12}")
        print(f"{'-'*140}")
        
        # Get quotes for these options
        try:
            # Create list of tokens to fetch quotes for
            tokens = [f"NFO:{opt['tradingsymbol']}" for opt in opts]
            
            # Fetch quotes in batches of 50 to avoid hitting limits
            for i in range(0, len(tokens), 50):
                batch = tokens[i:i+50]
                quotes = kite.quote(batch)
                
                # Sort options by strike price
                opts.sort(key=lambda x: x['strike'])
                
                for opt in opts:
                    token_key = f"NFO:{opt['tradingsymbol']}"
                    if token_key in quotes:
                        quote_data = quotes[token_key]
                        ltp = quote_data.get('last_price', 0)
                        bid = quote_data.get('depth', {}).get('buy', [{}])[0].get('price', 0)
                        ask = quote_data.get('depth', {}).get('sell', [{}])[0].get('price', 0)
                        oi = quote_data.get('oi', 0)
                        prev_close = quote_data.get('ohlc', {}).get('close', 0)
                        
                        # Calculate change
                        if prev_close != 0:
                            chg = ((ltp - prev_close) / prev_close) * 100
                        else:
                            chg = 0
                        
                        # IV is not directly available in quote, using a placeholder
                        iv = 0  # Placeholder - actual IV requires historical data or separate calculation
                        
                        print(f"{opt['tradingsymbol']:<18} {opt['option_type']:<5} {opt['strike']:<8.2f} "
                              f"{ltp:<8.2f} {chg:<8.2f} {bid:<8.2f} {ask:<8.2f} {iv:<8.2f} {oi:<12.0f}")
        except Exception as e:
            print(f"Error fetching quotes: {str(e)}")
            # Display without live prices
            for opt in opts:
                print(f"{opt['tradingsymbol']:<18} {opt['option_type']:<5} {opt['strike']:<8.2f}")

def scan_all_optionable_best(kite):
    """Scan all optionable underlyings and pick best chain by OI at ATM."""
    print("Fetching NFO instruments...")
    instruments = kite.instruments('NFO')

    # group options by underlying name
    by_underlying = {}
    today = datetime.today().date()
    for inst in instruments:
        if inst.get('segment') != 'NFO-OPT':
            continue
        name = inst.get('name')
        if not name:
            continue
        by_underlying.setdefault(name, []).append(inst)

    best = None

    for underlying, opts in by_underlying.items():
        # nearest expiry >= today
        opts = [o for o in opts if o.get('expiry') and o['expiry'] >= today]
        if not opts:
            continue
        nearest_expiry = min(set(o['expiry'] for o in opts))
        opts = [o for o in opts if o['expiry'] == nearest_expiry]

        # get underlying LTP
        try:
            ltp_data = kite.ltp([f"NSE:{underlying}"])
            underlying_ltp = ltp_data.get(f"NSE:{underlying}", {}).get('last_price')
        except Exception:
            continue
        if not underlying_ltp:
            continue

        # choose ATM strike
        atm = min(opts, key=lambda o: abs((o.get('strike') or 0) - underlying_ltp))
        strike = atm.get('strike')
        if strike is None:
            continue
        # find CE/PE for same strike
        ce = next((o for o in opts if o.get('strike') == strike and o.get('option_type') == 'CE'), None)
        pe = next((o for o in opts if o.get('strike') == strike and o.get('option_type') == 'PE'), None)
        if not ce and not pe:
            continue

        tokens = []
        if ce:
            tokens.append(f"NFO:{ce['tradingsymbol']}")
        if pe:
            tokens.append(f"NFO:{pe['tradingsymbol']}")
        try:
            quotes = kite.quote(tokens) if tokens else {}
        except Exception:
            continue

        ce_q = quotes.get(f"NFO:{ce['tradingsymbol']}", {}) if ce else {}
        pe_q = quotes.get(f"NFO:{pe['tradingsymbol']}", {}) if pe else {}
        ce_oi = ce_q.get('oi', 0) or 0
        pe_oi = pe_q.get('oi', 0) or 0
        ce_ltp = ce_q.get('last_price', 0) or 0
        pe_ltp = pe_q.get('last_price', 0) or 0

        score = ce_oi + pe_oi
        row = {
            "underlying": underlying,
            "expiry": nearest_expiry,
            "strike": strike,
            "underlying_ltp": underlying_ltp,
            "CE_ltp": ce_ltp,
            "CE_oi": ce_oi,
            "PE_ltp": pe_ltp,
            "PE_oi": pe_oi,
            "score": score,
        }
        if (best is None) or (row["score"] > best["score"]):
            best = row

    return best


def main():
    print("Connecting to Zerodha Kite API for real-time options data...")
    
    kite, kite_instance = get_kite_connection()
    
    if kite is None:
        print("\nCannot connect to Kite API directly due to expired token.")
        print("\nTo get real-time options prices, you need to:")
        print("1. Visit:", kite_instance.login_url())
        print("2. Login to your Zerodha account")
        print("3. Authorize the application")
        print("4. Copy the request_token from the callback URL")
        print("5. Use the request_token to generate access_token")
        
        # Show the login URL
        print(f"\nLogin URL: {kite_instance.login_url()}")
        return
    
    try:
        print("Scanning all optionable underlyings for best chain (ATM OI)...")
        best = scan_all_optionable_best(kite)
        if best:
            print("\nBEST OPTION CHAIN (ATM OI SCORE)")
            for k, v in best.items():
                print(f"{k}: {v}")
        else:
            print("No optionable data returned.")

    except Exception as e:
        print(f"Error accessing Kite API: {str(e)}")
        print("\nThe API may be returning an error due to token expiration or other access issues.")
        print("Please refresh your tokens by re-authenticating with Zerodha.")

if __name__ == "__main__":
    main()