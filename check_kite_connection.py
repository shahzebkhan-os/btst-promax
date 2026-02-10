import sys
import os
import json
import pickle
from datetime import datetime

# Add the directory containing the kiteconnect package to the Python path
sys.path.insert(0, '/Users/aayan/.local/lib/python3.9/site-packages')

try:
    from kiteconnect import KiteConnect
    kite_available = True
except ImportError:
    print("❌ KiteConnect library not installed")
    kite_available = False

def check_connection():
    if not kite_available:
        print("❌ KiteConnect library is not available")
        return False
    
    try:
        # Load API credentials
        with open('/Users/aayan/.zerodha_creds.json', 'r') as f:
            creds = json.load(f)
        
        api_key = creds['api_key']
        print(f"✅ API Key found: {api_key}")
        
        # Try to initialize KiteConnect
        kite = KiteConnect(api_key=api_key)
        print("✅ KiteConnect initialized successfully")
        
        # Check if tokens exist
        try:
            with open('/Users/aayan/.zerodha_tokens.pkl', 'rb') as f:
                tokens = pickle.load(f)
            
            access_token = tokens.get('access_token')
            stored_at = tokens.get('stored_at')
            expires_at = tokens.get('expires_at')
            
            print(f"✅ Stored tokens found")
            print(f"   - Stored at: {stored_at}")
            print(f"   - Expires at: {expires_at}")
            
            # Check if token is still valid
            if expires_at:
                if 'T' in expires_at:
                    # Handle ISO format with timezone
                    if '+' in expires_at or expires_at.endswith('Z'):
                        expiry_time = datetime.fromisoformat(expires_at)
                    else:
                        # Parse without timezone - handle both formats
                        try:
                            expiry_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                        except ValueError:
                            # Try alternate format
                            expiry_time = datetime.strptime(expires_at, '%Y-%m-%dT%H:%M:%S.%f')
                else:
                    # Handle different format
                    expiry_time = datetime.strptime(expires_at, '%Y-%m-%dT%H:%M:%S.%f')
                
                current_time = datetime.now()
                if current_time > expiry_time:
                    print("❌ Access token has EXPIRED")
                    print(f"   - Current time: {current_time}")
                    print(f"   - Expiry time: {expiry_time}")
                    return False
                else:
                    print("✅ Access token is VALID")
                    kite.set_access_token(access_token)
                    
                    # Test the connection with a simple API call
                    try:
                        profile = kite.profile()
                        print(f"✅ Connected as user: {profile.get('user_name', 'Unknown')} (ID: {profile.get('user_id', 'Unknown')})")
                        print("✅ Connection TEST PASSED")
                        return True
                    except Exception as e:
                        print(f"❌ Connection test failed: {str(e)}")
                        return False
            else:
                print("❌ No expiry time found in tokens")
                return False
                
        except FileNotFoundError:
            print("❌ No stored tokens found - need to authenticate first")
            return False
        except Exception as e:
            print(f"❌ Error loading tokens: {str(e)}")
            return False
            
    except FileNotFoundError:
        print("❌ Credentials file not found")
        return False
    except Exception as e:
        print(f"❌ Error checking connection: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Checking Kite API Connection Status...")
    print()
    
    success = check_connection()
    
    if success:
        print()
        print("🎉 CONNECTION STATUS: CONNECTED ✅")
    else:
        print()
        print("🔌 CONNECTION STATUS: DISCONNECTED ❌")
        print()
        print("To connect, you need to:")
        print("1. Authenticate via the login URL")
        print("2. Obtain a request token")
        print("3. Generate a new access token")