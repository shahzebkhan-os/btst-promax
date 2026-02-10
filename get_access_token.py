#!/usr/bin/env python3
"""
Helper script to get access token after successful authentication
"""

from kiteconnect import KiteConnect
import os

def get_access_token():
    print("Getting Access Token")
    print("=" * 30)
    
    # Since we know the API key from the successful connection
    api_key = "ecn2x11lx0logxol"
    kite = KiteConnect(api_key=api_key)
    
    # We need to set the access token that was obtained in the previous session
    # Since we can't directly access it from the previous session, 
    # we'll need to run the authentication again to get a new access token
    
    print("The access token is session-specific and expires after a certain time.")
    print("To run the analysis, you need to:")
    print("1. Run the demo script again to get a new access token")
    print("2. Or set the access token as an environment variable")
    
    print(f"\nAPI Key being used: {api_key}")
    print("\nTo run the analysis, execute:")
    print("python3 kite_demo.py")
    print("Then after authentication, run:")
    print("python3 analyze_trades_updated.py")

if __name__ == "__main__":
    get_access_token()