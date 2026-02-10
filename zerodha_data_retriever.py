import json
import pandas as pd
import numpy as np
from kiteconnect import KiteConnect
import time
from datetime import datetime, timedelta

# Load credentials
with open('/Users/aayan/.zerodha_creds.json', 'r') as f:
    creds = json.load(f)

api_key = creds['api_key']
api_secret = creds['api_secret']

# Initialize Kite Connect
kite = KiteConnect(api_key=api_key)

# Print login URL
print("Zerodha API - Data Retrieval Tool")
print("="*50)
print("To proceed, you need to authenticate with Zerodha:")
print(kite.login_url())
print("\nAfter logging in, you'll get a request token.")
print("Please manually complete the authentication process.")
print("Once you have the request token, update the script with it.")

# Note: Normally we would use the request token to get access token
# But for this example, I'll outline what data we can retrieve once authenticated

def get_available_data_types():
    """
    Outline of available data types from Zerodha Kite API
    """
    data_types = {
        "Instruments": {
            "description": "Complete list of tradable instruments",
            "includes": [
                "Nifty 50 stocks",
                "Bank Nifty stocks", 
                "Midcap stocks",
                "Options contracts",
                "Futures contracts"
            ],
            "function": "kite.instruments() or kite.instruments(exchange)"
        },
        "Historical Data": {
            "description": "Historical price data for technical analysis",
            "intervals": [
                "minute",
                "day", 
                "3minute",
                "5minute",
                "15minute",
                "30minute",
                "60minute"
            ],
            "function": "kite.historical_data(instrument_token, from_date, to_date, interval)"
        },
        "Live Market Data": {
            "description": "Real-time market quotes",
            "includes": [
                "Last traded price",
                "Open, High, Low, Close",
                "Volume",
                "OI (for derivatives)",
                "Bid/Ask prices"
            ],
            "function": "kite.quote([list_of_instrument_tokens])"
        },
        "Options Chain": {
            "description": "Complete options chain for Nifty/Bank Nifty",
            "includes": [
                "Strike prices",
                "Call/Put premiums",
                "IV (Implied Volatility)",
                "Delta, Gamma, Theta, Vega"
            ],
            "function": "kite.quote() for options instruments"
        },
        "Portfolio Data": {
            "description": "User's holdings and positions",
            "includes": [
                "Holdings",
                "Positions",
                "Margins",
                "Orders"
            ],
            "function": "kite.holdings(), kite.positions(), kite.margins()"
        },
        "Market Depth": {
            "description": "Detailed market depth",
            "includes": [
                "Top 5 bids/asks",
                "Quantity at each level",
                "Total open interest"
            ],
            "function": "kite.depth(instrument_token)"
        }
    }
    return data_types

def sample_data_structure():
    """
    Sample of the type of data we can collect for ML model
    """
    sample_data = {
        "technical_indicators": [
            "RSI",
            "MACD", 
            "Bollinger Bands",
            "Moving Averages",
            "Stochastic Oscillator",
            "ATR (Average True Range)",
            "Volume indicators"
        ],
        "market_microstructure": [
            "Bid-Ask spread",
            "Order flow",
            "Volume profiles",
            "Open Interest changes"
        ],
        "volatility_metrics": [
            "Historical volatility",
            "Implied volatility (options)",
            "Realized volatility"
        ],
        "sentiment_indicators": [
            "FII/DII data",
            "Put/Call ratios",
            "Options positioning"
        ]
    }
    return sample_data

if __name__ == "__main__":
    print("\nAvailable Data Types from Zerodha API:")
    print("="*50)
    
    data_types = get_available_data_types()
    for category, details in data_types.items():
        print(f"\n{category}:")
        print(f"  Description: {details['description']}")
        if 'includes' in details:
            print("  Includes:")
            for item in details['includes']:
                print(f"    - {item}")
        print(f"  Function: {details['function']}")
    
    print("\nPotential ML Features from Zerodha API:")
    print("="*50)
    
    ml_features = sample_data_structure()
    for category, features in ml_features.items():
        print(f"\n{category}:")
        for feature in features:
            print(f"  - {feature}")
    
    print("\nTo access this data programmatically:")
    print("1. Complete the OAuth flow to get access token")
    print("2. Initialize KiteConnect with access token")
    print("3. Call the appropriate API functions")
    print("4. Process data for ML model training")