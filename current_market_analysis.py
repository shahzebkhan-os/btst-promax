import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def calculate_technical_indicators(df):
    """Calculate technical indicators for analysis"""
    df = df.copy()
    
    # Moving averages
    df['SMA_10'] = df['Close'].rolling(window=10).mean()
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['BB_middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
    df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
    
    # Volatility
    df['volatility'] = df['Close'].rolling(window=10).std()
    
    # Daily change percentage
    df['daily_change_pct'] = ((df['Close'] - df['Open']) / df['Open']) * 100
    
    return df

def analyze_current_nifty50():
    """Analyze current Nifty 50 stocks for fresh recommendations"""
    
    print("="*80)
    print("🎯 CURRENT NIFTY 50 MARKET ANALYSIS")
    print("="*80)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Nifty 50 stocks
    nifty50_stocks = [
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
        'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'BAJFINANCE.NS',
        'LT.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'AXISBANK.NS', 'SUNPHARMA.NS',
        'TITAN.NS', 'ULTRACEMCO.NS', 'WIPRO.NS', 'NESTLEIND.NS', 'M&M.NS',
        'IOC.NS', 'ONGC.NS', 'POWERGRID.NS', 'COALINDIA.NS', 'GRASIM.NS',
        'BRITANNIA.NS', 'HINDZINC.NS', 'ZEEL.NS', 'SHREECEM.NS', 'BPCL.NS',
        'JSWSTEEL.NS', 'NTPC.NS', 'HEROMOTOCO.NS', 'TECHM.NS', 'DRREDDY.NS',
        'HDFC.NS', 'UPL.NS', 'INDUSINDBK.NS', 'ADANIPORTS.NS', 'CIPLA.NS',
        'SBILIFE.NS', 'VEDL.NS', 'APOLLOHOSP.NS', 'DIVISLAB.NS', 'EICHERMOT.NS',
        'HCLTECH.NS', 'TATACONSUM.NS', 'BAJAJFINSV.NS', 'KOTAKBANK.NS', 'ADANIENT.NS'
    ]
    
    analysis_results = []
    
    print(f"Analyzing {len(nifty50_stocks)} Nifty 50 stocks for current market situation...")
    print()
    
    for i, symbol in enumerate(nifty50_stocks, 1):
        try:
            print(f"[{i}/{len(nifty50_stocks)}] Analyzing {symbol}...", end='\r')
            
            # Get current data (last 30 days for indicators)
            stock = yf.Ticker(symbol)
            df = stock.history(period="30d")
            
            if len(df) < 20:  # Need minimum data
                continue
            
            # Calculate technical indicators
            df = calculate_technical_indicators(df)
            
            # Get current values
            current_data = df.iloc[-1]
            prev_data = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
            
            current_price = current_data['Close']
            prev_close = prev_data['Close']
            daily_change = ((current_price - prev_close) / prev_close) * 100
            rsi = current_data['RSI']
            sma_20 = current_data['SMA_20']
            sma_50 = current_data['SMA_50']
            volatility = current_data['volatility']
            
            # Determine trend and direction
            if pd.isna(sma_20) or pd.isna(sma_50) or pd.isna(rsi):
                continue
            
            # Technical analysis for direction
            trend_strength = 0
            if current_price > sma_20 > sma_50 and rsi < 70:  # Bullish pattern
                direction = 'UP'
                trend_strength = min(0.9, 0.5 + (current_price - sma_20) / current_price)
            elif current_price < sma_20 < sma_50 and rsi > 30:  # Bearish pattern
                direction = 'DOWN'
                trend_strength = min(0.9, 0.5 + (sma_20 - current_price) / current_price)
            elif rsi > 70:  # Overbought
                direction = 'DOWN'
                trend_strength = 0.6
            elif rsi < 30:  # Oversold
                direction = 'UP'
                trend_strength = 0.6
            else:
                # Neutral trend based on moving averages alignment
                if current_price > sma_20 and sma_20 > sma_50:
                    direction = 'UP'
                    trend_strength = 0.55
                elif current_price < sma_20 and sma_20 < sma_50:
                    direction = 'DOWN'
                    trend_strength = 0.55
                else:
                    continue  # Too neutral to recommend
            
            # Confidence based on multiple factors
            confidence = trend_strength
            if volatility and not pd.isna(volatility):
                # Adjust confidence based on volatility (higher volatility = less certainty)
                volatility_factor = max(0.8, 1.0 - (volatility / current_price))
                confidence *= volatility_factor
            
            confidence = min(confidence, 0.95)  # Cap at 95%
            
            result = {
                'symbol': symbol,
                'current_price': current_price,
                'daily_change': daily_change,
                'rsi': rsi,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'direction': direction,
                'confidence': confidence,
                'volatility': volatility
            }
            
            analysis_results.append(result)
        
        except Exception as e:
            continue  # Skip if error
    
    print(f"\n✅ Analysis completed! Analyzed {len(analysis_results)} stocks")
    print()
    
    # Sort by confidence
    sorted_results = sorted(analysis_results, key=lambda x: x['confidence'], reverse=True)
    
    print("="*100)
    print("🏆 CURRENT TOP RECOMMENDATIONS (Based on Live Market Data)")
    print("="*100)
    print()
    
    # Separate calls and puts by confidence
    calls = [(r, 'CALL') for r in sorted_results if r['direction'] == 'UP']
    puts = [(r, 'PUT') for r in sorted_results if r['direction'] == 'DOWN']
    
    print("🥇 TOP 10 HIGH-CONFIDENCE CALL OPTIONS (Bullish - Expecting UP movement):")
    print("-" * 90)
    print(f"{'Symbol':<10} {'Current':<8} {'Change':<8} {'RSI':<6} {'Confidence':<10} {'Recommendation'}")
    print("-" * 90)
    
    for result, opt_type in calls[:10]:
        print(f"{result['symbol']:<10} ₹{result['current_price']:<7.2f} {result['daily_change']:<7.2f}% "
              f"{result['rsi']:<6.1f} {result['confidence']*100:<9.2f}% {opt_type}")
    
    print()
    print("🥈 TOP 10 HIGH-CONFIDENCE PUT OPTIONS (Bearish - Expecting DOWN movement):")
    print("-" * 90)
    print(f"{'Symbol':<10} {'Current':<8} {'Change':<8} {'RSI':<6} {'Confidence':<10} {'Recommendation'}")
    print("-" * 90)
    
    for result, opt_type in puts[:10]:
        print(f"{result['symbol']:<10} ₹{result['current_price']:<7.2f} {result['daily_change']:<7.2f}% "
              f"{result['rsi']:<6.1f} {result['confidence']*100:<9.2f}% {opt_type}")
    
    print()
    print("="*100)
    print("📊 CURRENT MARKET INSIGHTS:")
    print("="*100)
    
    # Count trends
    up_count = len([r for r in analysis_results if r['direction'] == 'UP'])
    down_count = len([r for r in analysis_results if r['direction'] == 'DOWN'])
    
    print(f"• Total analyzed stocks: {len(analysis_results)}")
    print(f"• Stocks trending UP: {up_count} ({up_count/len(analysis_results)*100:.1f}%)")
    print(f"• Stocks trending DOWN: {down_count} ({down_count/len(analysis_results)*100:.1f}%)")
    print(f"• Average confidence: {np.mean([r['confidence'] for r in analysis_results])*100:.2f}%")
    print(f"• Highest confidence: {max([r['confidence'] for r in analysis_results])*100:.2f}%")
    print()
    
    # Sector insights
    sector_map = {
        'RELIANCE.NS': 'Energy', 'TCS.NS': 'Technology', 'HDFCBANK.NS': 'Banking',
        'INFY.NS': 'Technology', 'ICICIBANK.NS': 'Banking', 'HINDUNILVR.NS': 'FMCG',
        'ITC.NS': 'FMCG', 'SBIN.NS': 'Banking', 'BHARTIARTL.NS': 'Telecom',
        'BAJFINANCE.NS': 'Finance', 'LT.NS': 'Construction', 'ASIANPAINT.NS': 'Paints',
        'MARUTI.NS': 'Auto', 'AXISBANK.NS': 'Banking', 'SUNPHARMA.NS': 'Pharma',
        'TITAN.NS': 'Luxury', 'ULTRACEMCO.NS': 'Cement', 'WIPRO.NS': 'Technology',
        'NESTLEIND.NS': 'FMCG', 'M&M.NS': 'Auto', 'IOC.NS': 'Oil&Gas',
        'ONGC.NS': 'Oil&Gas', 'POWERGRID.NS': 'Power', 'COALINDIA.NS': 'Mining',
        'GRASIM.NS': 'Diversified', 'BRITANNIA.NS': 'FMCG', 'HINDZINC.NS': 'Metals',
        'ZEEL.NS': 'Media', 'SHREECEM.NS': 'Cement', 'BPCL.NS': 'Oil&Gas',
        'JSWSTEEL.NS': 'Steel', 'NTPC.NS': 'Power', 'HEROMOTOCO.NS': 'Auto',
        'TECHM.NS': 'Technology', 'DRREDDY.NS': 'Pharma', 'HDFC.NS': 'Banking',
        'UPL.NS': 'Chemicals', 'INDUSINDBK.NS': 'Banking', 'ADANIPORTS.NS': 'Infrastructure',
        'CIPLA.NS': 'Pharma', 'SBILIFE.NS': 'Insurance', 'VEDL.NS': 'Metals',
        'APOLLOHOSP.NS': 'Healthcare', 'DIVISLAB.NS': 'Pharma', 'EICHERMOT.NS': 'Auto',
        'HCLTECH.NS': 'Technology', 'TATACONSUM.NS': 'FMCG', 'BAJAJFINSV.NS': 'Finance',
        'KOTAKBANK.NS': 'Banking', 'ADANIENT.NS': 'Infrastructure'
    }
    
    # Categorize by sector
    sector_trends = {}
    for result in analysis_results:
        sector = sector_map.get(result['symbol'], 'Other')
        if sector not in sector_trends:
            sector_trends[sector] = {'up': 0, 'down': 0, 'total': 0}
        sector_trends[sector]['total'] += 1
        if result['direction'] == 'UP':
            sector_trends[sector]['up'] += 1
        else:
            sector_trends[sector]['down'] += 1
    
    print("🏢 SECTOR WISE BREAKDOWN:")
    print("-" * 60)
    print(f"{'Sector':<15} {'Total':<6} {'Bullish':<8} {'Bearish':<8} {'Trend'}")
    print("-" * 60)
    
    for sector, data in sorted(sector_trends.items(), key=lambda x: x[1]['total'], reverse=True)[:10]:
        if data['total'] >= 2:  # Only show sectors with 2+ stocks
            trend = "📈 Bullish" if data['up'] > data['down'] else "📉 Bearish"
            print(f"{sector:<15} {data['total']:<6} {data['up']:<8} {data['down']:<8} {trend}")
    
    print()
    print("💡 RECOMMENDATION NOTES:")
    print("• CALL options: For stocks expected to rise (bullish positions)")
    print("• PUT options: For stocks expected to fall (bearish positions)")
    print("• Focus on high-confidence recommendations for better success rate")
    print("• Consider position sizing based on confidence levels")
    print()
    print("🎯 CURRENT ANALYSIS COMPLETE!")

if __name__ == "__main__":
    analyze_current_nifty50()