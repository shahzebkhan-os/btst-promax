#!/usr/bin/env python3
"""
Comprehensive Top Stocks Analysis for Indian Market
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_top_nifty_stocks():
    """
    Get top Nifty 50 stocks for analysis
    """
    # Top Nifty 50 stocks by market cap
    nifty_stocks = [
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
        'ICICIBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS',
        'LT.NS', 'ASIANPAINT.NS', 'AXISBANK.NS', 'MARUTI.NS', 'SUNPHARMA.NS',
        'TITAN.NS', 'ULTRACEMCO.NS', 'NESTLEIND.NS', 'WIPRO.NS', 'BAJFINANCE.NS',
        'HCLTECH.NS', 'TATAMOTORS.NS', 'POWERGRID.NS', 'BAJAJFINSERV.NS', 'BRITANNIA.NS',
        'ONGC.NS', 'JSWSTEEL.NS', 'GRASIM.NS', 'TATASTEEL.NS', 'EICHERMOT.NS',
        'IOC.NS', 'COALINDIA.NS', 'UPL.NS', 'INDUSINDBK.NS', 'VEDL.NS',
        'DRREDDY.NS', 'HEROMOTOCO.NS', 'SHREECEM.NS', 'BPCL.NS', 'M&M.NS',
        'ADANIPORTS.NS', 'NTPC.NS', 'DIVISLAB.NS', 'HDFC.NS', 'CIPLA.NS',
        'APOLLOHOSP.NS', 'MINDTREE.NS', 'BAJAJ-AUTO.NS', 'TATACONSUM.NS', 'GODREJCP.NS'
    ]
    return nifty_stocks

def calculate_technical_indicators(df):
    """
    Calculate technical indicators for stock analysis
    """
    # Simple Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    
    # Exponential Moving Averages
    df['EMA_20'] = df['Close'].ewm(span=20).mean()
    df['EMA_50'] = df['Close'].ewm(span=50).mean()
    
    # Relative Strength Index
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['Close'].ewm(span=12).mean()
    exp2 = df['Close'].ewm(span=26).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
    
    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
    
    # Average True Range (Volatility)
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['ATR'] = true_range.rolling(window=14).mean()
    
    # Price change indicators
    df['PCT_CHANGE_5D'] = df['Close'].pct_change(periods=5) * 100
    df['PCT_CHANGE_20D'] = df['Close'].pct_change(periods=20) * 100
    df['PCT_CHANGE_50D'] = df['Close'].pct_change(periods=50) * 100
    
    return df

def analyze_stock(symbol):
    """
    Analyze a single stock and return key metrics
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="6mo")
        
        if df.empty or len(df) < 50:
            return None
            
        df = calculate_technical_indicators(df)
        
        # Get the latest data
        current_price = df['Close'].iloc[-1]
        sma_20 = df['SMA_20'].iloc[-1]
        sma_50 = df['SMA_50'].iloc[-1]
        sma_200 = df['SMA_200'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        macd = df['MACD'].iloc[-1]
        macd_signal = df['MACD_Signal'].iloc[-1]
        atr = df['ATR'].iloc[-1]
        pct_change_50d = df['PCT_CHANGE_50D'].iloc[-1]
        
        # Calculate technical scores
        trend_score = 0
        if current_price > sma_20 > sma_50 > sma_200:
            trend_score = 3  # Strong uptrend
        elif current_price > sma_20 > sma_50:
            trend_score = 2  # Uptrend
        elif current_price > sma_20:
            trend_score = 1  # Mild uptrend
        elif current_price < sma_20 < sma_50 < sma_200:
            trend_score = -3  # Strong downtrend
        elif current_price < sma_20 < sma_50:
            trend_score = -2  # Downtrend
        else:
            trend_score = 0  # Sideways
        
        rsi_score = 0
        if 30 <= rsi <= 70:
            rsi_score = 1  # Neutral RSI
        elif rsi < 30:
            rsi_score = 2  # Oversold
        else:
            rsi_score = -1  # Overbought
        
        momentum_score = 0
        if pct_change_50d > 10:
            momentum_score = 2  # Strong positive momentum
        elif pct_change_50d > 0:
            momentum_score = 1  # Positive momentum
        elif pct_change_50d < -10:
            momentum_score = -2  # Strong negative momentum
        else:
            momentum_score = 0  # Neutral momentum
        
        # Overall score
        overall_score = trend_score + rsi_score + momentum_score
        
        # Determine recommendation
        recommendation = ""
        if trend_score >= 2 and rsi_score >= 0 and momentum_score >= 1:
            recommendation = "STRONG BUY"
        elif trend_score >= 1 and rsi_score >= 0:
            recommendation = "BUY"
        elif trend_score <= -2 and rsi_score <= -1:
            recommendation = "STRONG SELL"
        elif trend_score <= -1 and rsi_score <= -1:
            recommendation = "SELL"
        else:
            recommendation = "HOLD"
        
        return {
            'symbol': symbol.replace('.NS', ''),
            'current_price': current_price,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'sma_200': sma_200,
            'rsi': rsi,
            'macd': macd,
            'macd_signal': macd_signal,
            'atr': atr,
            'pct_change_50d': pct_change_50d,
            'trend_score': trend_score,
            'rsi_score': rsi_score,
            'momentum_score': momentum_score,
            'overall_score': overall_score,
            'recommendation': recommendation
        }
    except Exception as e:
        logger.warning(f"Could not analyze {symbol}: {str(e)}")
        return None

def analyze_top_stocks():
    """
    Analyze top stocks and rank them
    """
    print("Analyzing top Nifty stocks...")
    nifty_stocks = get_top_nifty_stocks()
    
    results = []
    for i, stock in enumerate(nifty_stocks[:20]):  # Analyze top 20 to start with
        print(f"Analyzing {stock} ({i+1}/20)...")
        result = analyze_stock(stock)
        if result:
            results.append(result)
    
    # Create DataFrame and sort by overall score
    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values(by='overall_score', ascending=False)
    
    return df_results

def main():
    """
    Main function to analyze and rank top stocks
    """
    print("Starting comprehensive stock analysis...")
    print("="*50)
    
    try:
        # Analyze top stocks
        results_df = analyze_top_stocks()
        
        if results_df.empty:
            print("No stocks could be analyzed. Please check your internet connection.")
            return
        
        print("\nTOP 10 STOCKS BY TECHNICAL SCORE:")
        print("="*80)
        print(f"{'Rank':<4} {'Symbol':<10} {'Price':<8} {'RSI':<6} {'Trend':<6} {'Momentum':<8} {'Score':<6} {'Recommendation':<15}")
        print("-"*80)
        
        for idx, row in results_df.head(10).iterrows():
            print(f"{idx+1:<4} {row['symbol']:<10} {row['current_price']:<8.2f} {row['rsi']:<6.2f} "
                  f"{row['trend_score']:<6} {row['momentum_score']:<8} {row['overall_score']:<6} {row['recommendation']:<15}")
        
        print(f"\nBOTTOM 5 STOCKS BY TECHNICAL SCORE:")
        print("="*80)
        print(f"{'Rank':<4} {'Symbol':<10} {'Price':<8} {'RSI':<6} {'Trend':<6} {'Momentum':<8} {'Score':<6} {'Recommendation':<15}")
        print("-"*80)
        
        for idx, row in results_df.tail(5).iterrows():
            rank = len(results_df) - list(results_df.index).index(idx)
            print(f"{rank:<4} {row['symbol']:<10} {row['current_price']:<8.2f} {row['rsi']:<6.2f} "
                  f"{row['trend_score']:<6} {row['momentum_score']:<8} {row['overall_score']:<6} {row['recommendation']:<15}")
        
        # Identify top picks with explanation
        print(f"\nTOP 3 PICKS WITH REASONING:")
        print("="*80)
        
        for i, (_, row) in enumerate(results_df.head(3).iterrows()):
            print(f"\n{i+1}. {row['symbol']} (Score: {row['overall_score']})")
            print(f"   Current Price: ₹{row['current_price']:.2f}")
            print(f"   RSI: {row['rsi']:.2f} ({'Oversold' if row['rsi'] < 30 else 'Overbought' if row['rsi'] > 70 else 'Neutral'})")
            print(f"   50-day Change: {row['pct_change_50d']:.2f}%")
            print(f"   Trend: {row['trend_score']} (Positive if >0, Negative if <0)")
            print(f"   Recommendation: {row['recommendation']}")
            
            # Provide specific reasoning
            reasons = []
            if row['trend_score'] >= 2:
                reasons.append("Strong uptrend with all SMAs aligned positively")
            if 30 <= row['rsi'] <= 70:
                reasons.append("RSI in healthy range (not overbought/oversold)")
            elif row['rsi'] < 30:
                reasons.append("RSI showing oversold condition (potential bounce)")
            if row['pct_change_50d'] > 10:
                reasons.append("Strong positive momentum over last 50 days")
            
            if reasons:
                print(f"   Reasoning: {', '.join(reasons)}")
        
        # Save results
        results_df.to_csv('/Users/aayan/.openclaw/workspace/top_stocks_analysis.csv', index=False)
        print(f"\nFull analysis saved to: /Users/aayan/.openclaw/workspace/top_stocks_analysis.csv")
        
        print(f"\nANALYSIS COMPLETE!")
        print(f"Total stocks analyzed: {len(results_df)}")
        print(f"Top recommendation: {results_df.iloc[0]['symbol']} with score {results_df.iloc[0]['overall_score']}")
        
    except Exception as e:
        print(f"Error in analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()