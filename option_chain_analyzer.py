"""
NSE Option Chain Analyzer with Share Selection Feature
GitHub Project: NSE-Option-Chain-Analyzer
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
import requests
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class NSEOptionChainAnalyzer:
    def __init__(self):
        self.nifty_50_stocks = [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
            'ICICIBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS',
            'LT.NS', 'AXISBANK.NS', 'ASIANPAINT.NS', 'SUNPHARMA.NS', 'TITAN.NS',
            'ULTRACEMCO.NS', 'NESTLEIND.NS', 'WIPRO.NS', 'MARUTI.NS', 'HCLTECH.NS',
            'POWERGRID.NS', 'BAJFINANCE.NS', 'BRITANNIA.NS', 'M&M.NS', 'ONGC.NS',
            'NTPC.NS', 'GRASIM.NS', 'ADANIPORTS.NS', 'DRREDDY.NS', 'COALINDIA.NS',
            'SHREECEM.NS', 'BPCL.NS', 'UPL.NS', 'IOC.NS', 'HEROMOTOCO.NS',
            'JSWSTEEL.NS', 'INDUSINDBK.NS', 'VEDL.NS', 'HDFC.NS', 'BAJAJFINSV.NS',
            'BAJAJ-AUTO.NS', 'TATAMOTORS.NS', 'CIPLA.NS', 'EICHERMOT.NS', 'GAIL.NS',
            'APOLLOHOSP.NS', 'HDFCLIFE.NS', 'TATASTEEL.NS', 'TECHM.NS', 'DIVISLAB.NS'
        ]
        
    def get_stock_data(self, symbol):
        """Get current stock data"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1d")
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            
            # Get additional info
            info = stock.info
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'sector': sector,
                'industry': industry,
                'currency': info.get('currency', 'INR'),
                'market_cap': info.get('marketCap', 'N/A')
            }
        except Exception as e:
            print(f"Error getting data for {symbol}: {str(e)}")
            return None
    
    def get_option_chain(self, symbol, expiration_date=None):
        """Get option chain data for a symbol"""
        try:
            stock = yf.Ticker(symbol)
            
            # Get available expiration dates
            exp_dates = stock.options
            
            if not exp_dates:
                return None
            
            # Use specified expiration date or get the nearest one
            if expiration_date is None:
                expiration_date = exp_dates[0]
            elif expiration_date not in exp_dates:
                print(f"Expiration date {expiration_date} not available. Using nearest: {exp_dates[0]}")
                expiration_date = exp_dates[0]
            
            # Get option chain for the expiration date
            opt = stock.option_chain(expiration_date)
            
            # Process calls
            calls = opt.calls.copy()
            calls = calls[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility', 'inTheMoney']]
            calls.columns = ['Strike', 'Last_Price', 'Bid', 'Ask', 'Volume', 'Open_Interest', 'IV', 'ITM']
            calls['Option_Type'] = 'CALL'
            
            # Process puts
            puts = opt.puts.copy()
            puts = puts[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility', 'inTheMoney']]
            puts.columns = ['Strike', 'Last_Price', 'Bid', 'Ask', 'Volume', 'Open_Interest', 'IV', 'ITM']
            puts['Option_Type'] = 'PUT'
            
            # Combine calls and puts
            option_chain = pd.concat([calls, puts], ignore_index=True)
            
            # Add underlying price
            stock_data = self.get_stock_data(symbol)
            underlying_price = stock_data['current_price'] if stock_data else None
            
            return {
                'symbol': symbol,
                'underlying_price': underlying_price,
                'expiration_date': expiration_date,
                'option_chain': option_chain,
                'available_expirations': exp_dates
            }
        except Exception as e:
            print(f"Error getting option chain for {symbol}: {str(e)}")
            return None
    
    def analyze_strike_levels(self, option_data):
        """Analyze key strike levels and option metrics"""
        if option_data is None:
            return None
        
        df = option_data['option_chain']
        underlying_price = option_data['underlying_price']
        
        if underlying_price is None:
            return None
        
        # Calculate metrics
        atm_strike = min(option_data['option_chain']['Strike'], key=lambda x: abs(x - underlying_price))
        
        # Calculate total open interest by strike
        oi_by_strike = df.groupby('Strike')[['Open_Interest']].sum().reset_index()
        max_pain = oi_by_strike.loc[oi_by_strike['Open_Interest'].idxmax(), 'Strike']
        
        # Calculate total volume by strike
        vol_by_strike = df.groupby('Strike')[['Volume']].sum().reset_index()
        highest_volume_strike = vol_by_strike.loc[vol_by_strike['Volume'].idxmax(), 'Strike']
        
        analysis = {
            'atm_strike': atm_strike,
            'max_pain': max_pain,
            'highest_volume_strike': highest_volume_strike,
            'underlying_price': underlying_price,
            'total_call_oi': df[df['Option_Type'] == 'CALL']['Open_Interest'].sum(),
            'total_put_oi': df[df['Option_Type'] == 'PUT']['Open_Interest'].sum(),
            'put_call_ratio': df[df['Option_Type'] == 'PUT']['Open_Interest'].sum() / max(1, df[df['Option_Type'] == 'CALL']['Open_Interest'].sum()),
            'total_call_volume': df[df['Option_Type'] == 'CALL']['Volume'].sum(),
            'total_put_volume': df[df['Option_Type'] == 'PUT']['Volume'].sum(),
            'put_call_volume_ratio': df[df['Option_Type'] == 'PUT']['Volume'].sum() / max(1, df[df['Option_Type'] == 'CALL']['Volume'].sum())
        }
        
        return analysis
    
    def get_top_strikes(self, option_data, top_n=5):
        """Get top strikes by open interest and volume"""
        if option_data is None:
            return None
        
        df = option_data['option_chain']
        
        # Top strikes by open interest
        top_oi = df.nlargest(top_n, 'Open_Interest')[['Strike', 'Option_Type', 'Last_Price', 'Open_Interest', 'Volume', 'IV']]
        
        # Top strikes by volume
        top_vol = df.nlargest(top_n, 'Volume')[['Strike', 'Option_Type', 'Last_Price', 'Open_Interest', 'Volume', 'IV']]
        
        return {
            'top_by_open_interest': top_oi.to_dict('records'),
            'top_by_volume': top_vol.to_dict('records')
        }
    
    def generate_recommendations(self, option_data):
        """Generate trading recommendations based on option chain data"""
        if option_data is None:
            return None
        
        analysis = self.analyze_strike_levels(option_data)
        if analysis is None:
            return None
        
        recommendations = []
        
        # High open interest strikes (potential support/resistance)
        df = option_data['option_chain']
        high_oi_strikes = df.nlargest(5, 'Open_Interest')[['Strike', 'Option_Type', 'Open_Interest']]
        
        for _, row in high_oi_strikes.iterrows():
            if row['Option_Type'] == 'CALL':
                # High call open interest acts as resistance
                if row['Strike'] > analysis['underlying_price']:
                    rec = {
                        'type': 'RESISTANCE_LEVEL',
                        'strike': row['Strike'],
                        'action': 'Consider selling calls or buying puts if price approaches',
                        'confidence': 'HIGH' if row['Open_Interest'] > analysis['total_call_oi'] * 0.05 else 'MEDIUM'
                    }
                    recommendations.append(rec)
            else:
                # High put open interest acts as support
                if row['Strike'] < analysis['underlying_price']:
                    rec = {
                        'type': 'SUPPORT_LEVEL',
                        'strike': row['Strike'],
                        'action': 'Consider buying calls or selling puts if price approaches',
                        'confidence': 'HIGH' if row['Open_Interest'] > analysis['total_put_oi'] * 0.05 else 'MEDIUM'
                    }
                    recommendations.append(rec)
        
        # Put-call ratio analysis
        pcr = analysis['put_call_ratio']
        if pcr > 1.2:
            rec = {
                'type': 'MARKET_SENTIMENT',
                'action': 'High put-call ratio suggests bearish sentiment',
                'confidence': 'MEDIUM'
            }
            recommendations.append(rec)
        elif pcr < 0.8:
            rec = {
                'type': 'MARKET_SENTIMENT',
                'action': 'Low put-call ratio suggests bullish sentiment',
                'confidence': 'MEDIUM'
            }
            recommendations.append(rec)
        
        return recommendations
    
    def create_summary_report(self, symbol, expiration_date=None):
        """Create a comprehensive summary report for a symbol"""
        print(f"🔍 Analyzing Option Chain for: {symbol}")
        print("="*60)
        
        # Get option chain data
        option_data = self.get_option_chain(symbol, expiration_date)
        if option_data is None:
            print(f"❌ Could not retrieve option chain data for {symbol}")
            return None
        
        # Get stock data
        stock_data = self.get_stock_data(symbol)
        
        # Analyze strike levels
        analysis = self.analyze_strike_levels(option_data)
        top_strikes = self.get_top_strikes(option_data)
        recommendations = self.generate_recommendations(option_data)
        
        # Print report
        print(f"\n📈 STOCK INFO: {symbol}")
        print("-"*40)
        if stock_data:
            print(f"Current Price: ₹{stock_data['current_price']:.2f}")
            print(f"Sector: {stock_data['sector']}")
            print(f"Industry: {stock_data['industry']}")
        
        print(f"\n📅 EXPIRATION DATE: {option_data['expiration_date']}")
        print("-"*40)
        
        print(f"\n📊 OPTION CHAIN ANALYSIS:")
        print("-"*40)
        if analysis:
            print(f"At-the-Money Strike: ₹{analysis['atm_strike']:.2f}")
            print(f"Max Pain Level: ₹{analysis['max_pain']:.2f}")
            print(f"Highest Volume Strike: ₹{analysis['highest_volume_strike']:.2f}")
            print(f"Total Call OI: {analysis['total_call_oi']:,}")
            print(f"Total Put OI: {analysis['total_put_oi']:,}")
            print(f"Put/Call OI Ratio: {analysis['put_call_ratio']:.2f}")
            print(f"Total Call Volume: {analysis['total_call_volume']:,}")
            print(f"Total Put Volume: {analysis['total_put_volume']:,}")
            print(f"Put/Call Volume Ratio: {analysis['put_call_volume_ratio']:.2f}")
        
        print(f"\n🎯 TOP STRIKES BY OPEN INTEREST:")
        print("-"*40)
        if top_strikes:
            for i, strike in enumerate(top_strikes['top_by_open_interest'][:3]):
                print(f"{i+1}. Strike: ₹{strike['Strike']:.2f} | Type: {strike['Option_Type']} | OI: {strike['Open_Interest']:,} | Vol: {strike['Volume']:,} | IV: {strike['IV']*100:.1f}%")
        
        print(f"\n🔥 TOP STRIKES BY VOLUME:")
        print("-"*40)
        if top_strikes:
            for i, strike in enumerate(top_strikes['top_by_volume'][:3]):
                print(f"{i+1}. Strike: ₹{strike['Strike']:.2f} | Type: {strike['Option_Type']} | OI: {strike['Open_Interest']:,} | Vol: {strike['Volume']:,} | IV: {strike['IV']*100:.1f}%")
        
        print(f"\n💡 RECOMMENDATIONS:")
        print("-"*40)
        if recommendations:
            for i, rec in enumerate(recommendations[:5]):  # Show top 5
                if rec['type'] == 'SUPPORT_LEVEL':
                    print(f"{i+1}. Support Level: ₹{rec['strike']:.2f}")
                    print(f"   Action: {rec['action']}")
                    print(f"   Confidence: {rec['confidence']}")
                elif rec['type'] == 'RESISTANCE_LEVEL':
                    print(f"{i+1}. Resistance Level: ₹{rec['strike']:.2f}")
                    print(f"   Action: {rec['action']}")
                    print(f"   Confidence: {rec['confidence']}")
                elif rec['type'] == 'MARKET_SENTIMENT':
                    print(f"{i+1}. Market Sentiment: {rec['action']}")
                    print(f"   Confidence: {rec['confidence']}")
        else:
            print("No specific recommendations available")
        
        print(f"\n📋 AVAILABLE EXPIRATION DATES:")
        print("-"*40)
        for i, exp in enumerate(option_data['available_expirations'][:5]):  # Show first 5
            print(f"{i+1}. {exp}")
        
        return {
            'symbol': symbol,
            'stock_data': stock_data,
            'option_data': option_data,
            'analysis': analysis,
            'top_strikes': top_strikes,
            'recommendations': recommendations
        }
    
    def list_available_stocks(self):
        """List all available stocks for analysis"""
        print("🏛️  NIFTY 50 STOCKS AVAILABLE FOR ANALYSIS:")
        print("="*60)
        for i, stock in enumerate(self.nifty_50_stocks, 1):
            print(f"{i:2d}. {stock}")

def main():
    analyzer = NSEOptionChainAnalyzer()
    
    print("NSE Option Chain Analyzer")
    print("="*60)
    print("This tool analyzes option chain data for Indian stocks")
    print("Features:")
    print("- Select any Nifty 50 stock for analysis")
    print("- View option chain data (calls & puts)")
    print("- Analyze key levels (ATM, Max Pain, Support/Resistance)")
    print("- Get trading recommendations based on OI and volume")
    print("- View put/call ratios and market sentiment")
    print()
    
    while True:
        print("\nOPTIONS:")
        print("1. List available stocks")
        print("2. Analyze specific stock")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            analyzer.list_available_stocks()
        elif choice == '2':
            symbol = input("\nEnter stock symbol (e.g., SBIN.NS, TCS.NS): ").strip().upper()
            if not symbol.endswith('.NS'):
                symbol += '.NS'
            
            # Check if it's in our list
            if symbol not in analyzer.nifty_50_stocks:
                print(f"⚠️  Warning: {symbol} is not in Nifty 50, but we'll try to analyze it anyway...")
            
            expiration = input("Enter expiration date (YYYY-MM-DD) or press Enter for nearest: ").strip()
            if expiration == "":
                expiration = None
            else:
                try:
                    datetime.strptime(expiration, '%Y-%m-%d')
                except ValueError:
                    print("Invalid date format. Using nearest expiration.")
                    expiration = None
            
            result = analyzer.create_summary_report(symbol, expiration)
            
            if result:
                save = input("\nSave analysis to file? (y/n): ").strip().lower()
                if save == 'y':
                    filename = f"option_analysis_{symbol.replace('.NS', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w') as f:
                        json.dump(result, f, indent=2, default=str)
                    print(f"✅ Analysis saved to {filename}")
        
        elif choice == '3':
            print("Thank you for using NSE Option Chain Analyzer!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()