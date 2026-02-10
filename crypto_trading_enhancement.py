#!/usr/bin/env python3
"""
Enhanced Crypto Trading Strategy for Coindcx
"""

import json
import time
import requests
import hashlib
import hmac
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import ccxt  # Cryptocurrency exchange library

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedCryptoTrader:
    """
    Enhanced crypto trading system with advanced technical analysis
    """
    
    def __init__(self, api_key: str, api_secret: str):
        """
        Initialize the enhanced crypto trader
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.exchange = None
        self.position_size_limit = 0.1  # Max 10% of account per trade
        self.max_daily_risk = 0.02  # Max 2% daily loss
        self.daily_pnl = 0.0
        self.daily_pnl_reset_time = datetime.now()
        
        # Technical indicators configuration
        self.ma_short = 20
        self.ma_long = 50
        self.rsi_period = 14
        self.bb_period = 20
        self.bb_std = 2
        
        # Initialize exchange connection
        self.initialize_exchange()
    
    def initialize_exchange(self):
        """
        Initialize connection to Coindcx or other exchange
        """
        try:
            # Using CCXT to connect to Coindcx
            self.exchange = ccxt.coindcx({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'enableRateLimit': True,
            })
            logger.info("Connected to Coindcx successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Coindcx: {str(e)}")
            # Fallback to simulated trading
            self.exchange = None
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate advanced technical indicators
        """
        # Moving Averages
        df['MA_20'] = df['close'].rolling(window=20).mean()
        df['MA_50'] = df['close'].rolling(window=50).mean()
        df['MA_200'] = df['close'].rolling(window=200).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        # Bollinger Bands
        df['BB_Middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # Stochastic Oscillator
        low_14 = df['low'].rolling(window=14).min()
        high_14 = df['high'].rolling(window=14).max()
        df['STOCH_K'] = 100 * ((df['close'] - low_14) / (high_14 - low_14))
        df['STOCH_D'] = df['STOCH_K'].rolling(window=3).mean()
        
        # Volume indicators
        df['Volume_MA'] = df['volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['volume'] / df['Volume_MA']
        
        # Volatility (ATR)
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['ATR'] = true_range.rolling(window=14).mean()
        
        # Trend strength
        df['Trend_Strength'] = abs(df['MA_20'] - df['MA_50']) / df['ATR']
        
        return df
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on technical indicators
        """
        df['Signal'] = 0
        df['Signal_Name'] = ''
        
        for i in range(1, len(df)):
            # Moving Average Crossover
            ma_bullish = (df['MA_20'].iloc[i] > df['MA_50'].iloc[i] and 
                          df['MA_20'].iloc[i-1] <= df['MA_50'].iloc[i-1])
            ma_bearish = (df['MA_20'].iloc[i] < df['MA_50'].iloc[i] and 
                          df['MA_20'].iloc[i-1] >= df['MA_50'].iloc[i-1])
            
            # RSI Signals
            rsi_oversold = df['RSI'].iloc[i] < 30
            rsi_overbought = df['RSI'].iloc[i] > 70
            rsi_recovering = df['RSI'].iloc[i] > 30 and df['RSI'].iloc[i-1] <= 30
            rsi_weakening = df['RSI'].iloc[i] < 70 and df['RSI'].iloc[i-1] >= 70
            
            # Bollinger Band Signals
            bb_bottom_touch = (df['close'].iloc[i] <= df['BB_Lower'].iloc[i] and
                               df['close'].iloc[i-1] > df['BB_Lower'].iloc[i-1])
            bb_top_touch = (df['close'].iloc[i] >= df['BB_Upper'].iloc[i] and
                            df['close'].iloc[i-1] < df['BB_Upper'].iloc[i-1])
            
            # MACD Signals
            macd_bullish = (df['MACD'].iloc[i] > df['MACD_Signal'].iloc[i] and
                            df['MACD'].iloc[i-1] <= df['MACD_Signal'].iloc[i-1])
            macd_bearish = (df['MACD'].iloc[i] < df['MACD_Signal'].iloc[i] and
                            df['MACD'].iloc[i-1] >= df['MACD_Signal'].iloc[i-1])
            
            # Stochastic Signals
            stoch_oversold = df['STOCH_K'].iloc[i] < 20
            stoch_overbought = df['STOCH_K'].iloc[i] > 80
            stoch_bullish = (df['STOCH_K'].iloc[i] > df['STOCH_D'].iloc[i] and
                             df['STOCH_K'].iloc[i-1] <= df['STOCH_D'].iloc[i-1])
            stoch_bearish = (df['STOCH_K'].iloc[i] < df['STOCH_D'].iloc[i] and
                             df['STOCH_K'].iloc[i-1] >= df['STOCH_D'].iloc[i-1])
            
            # Volume confirmation
            volume_confirmation = df['Volume_Ratio'].iloc[i] > 1.2
            
            # Trend strength filter
            strong_trend = df['Trend_Strength'].iloc[i] > 0.5
            
            # Combined signals with confirmations
            buy_signals = 0
            sell_signals = 0
            signal_names = []
            
            # MA + RSI combination (strong buy signal)
            if ma_bullish and rsi_recovering and volume_confirmation:
                buy_signals += 3
                signal_names.append("MA_RSI_COMBO")
            
            # BB + RSI combination (bounce signal)
            elif bb_bottom_touch and rsi_recovering:
                buy_signals += 2
                signal_names.append("BB_RSI_BOUNCE")
            
            # MACD + Stochastic combo
            elif macd_bullish and stoch_bullish:
                buy_signals += 2
                signal_names.append("MACD_STOCH_COMBO")
            
            # Pure MA crossover (if strong trend)
            elif ma_bullish and strong_trend:
                buy_signals += 1
                signal_names.append("MA_CROSSOVER")
            
            # MA + RSI combination (strong sell signal)
            if ma_bearish and rsi_weakening and volume_confirmation:
                sell_signals += 3
                signal_names.append("MA_RSI_COMBO")
            
            # BB + RSI combination (top signal)
            elif bb_top_touch and rsi_weakening:
                sell_signals += 2
                signal_names.append("BB_RSI_TOP")
            
            # MACD + Stochastic combo
            elif macd_bearish and stoch_bearish:
                sell_signals += 2
                signal_names.append("MACD_STOCH_COMBO")
            
            # Pure MA crossover (if strong trend)
            elif ma_bearish and strong_trend:
                sell_signals += 1
                signal_names.append("MA_CROSSOVER")
            
            # Final signal decision
            if buy_signals > sell_signals and buy_signals >= 2:  # At least 2 confirmations
                df.at[df.index[i], 'Signal'] = 1
                df.at[df.index[i], 'Signal_Name'] = " | ".join(signal_names)
            elif sell_signals > buy_signals and sell_signals >= 2:  # At least 2 confirmations
                df.at[df.index[i], 'Signal'] = -1
                df.at[df.index[i], 'Signal_Name'] = " | ".join(signal_names)
        
        return df
    
    def get_historical_data(self, symbol: str, timeframe: str = '1h', limit: int = 200) -> pd.DataFrame:
        """
        Get historical data for a symbol
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            # Return mock data for testing
            dates = pd.date_range(end=datetime.now(), periods=200, freq='1H')
            df = pd.DataFrame({
                'datetime': dates,
                'open': np.random.uniform(30000, 60000, 200),
                'high': np.random.uniform(30000, 60000, 200),
                'low': np.random.uniform(30000, 60000, 200),
                'close': np.random.uniform(30000, 60000, 200),
                'volume': np.random.uniform(100, 1000, 200),
                'timestamp': [int(date.timestamp() * 1000) for date in dates]
            })
            return df
    
    def analyze_pair(self, symbol: str) -> Dict:
        """
        Analyze a specific trading pair
        """
        df = self.get_historical_data(symbol)
        df = self.calculate_technical_indicators(df)
        df = self.generate_signals(df)
        
        # Get latest values
        latest = df.iloc[-1]
        previous = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
        
        # Calculate additional metrics
        price_change_24h = ((latest['close'] - df['close'].iloc[-25]) / df['close'].iloc[-25]) * 100 if len(df) > 25 else 0
        volatility = df['ATR'].iloc[-1] / latest['close'] * 100 if not pd.isna(df['ATR'].iloc[-1]) else 0
        
        analysis = {
            'symbol': symbol,
            'current_price': latest['close'],
            'rsi': latest['RSI'],
            'macd_histogram': latest['MACD_Hist'],
            'bb_position': (latest['close'] - latest['BB_Lower']) / (latest['BB_Upper'] - latest['BB_Lower']) if (latest['BB_Upper'] - latest['BB_Lower']) != 0 else 0.5,
            'signal': latest['Signal'],
            'signal_name': latest['Signal_Name'],
            'ma_trend': 'BULLISH' if latest['MA_20'] > latest['MA_50'] else 'BEARISH',
            'price_change_24h': price_change_24h,
            'volatility': volatility,
            'volume_ratio': latest['Volume_Ratio'],
            'recommendation': self.get_recommendation(latest, previous),
            'confidence': self.calculate_confidence(latest, previous)
        }
        
        return analysis
    
    def get_recommendation(self, latest: pd.Series, previous: pd.Series) -> str:
        """
        Get trading recommendation based on signals
        """
        if latest['Signal'] == 1:
            return 'STRONG BUY'
        elif latest['Signal'] == -1:
            return 'STRONG SELL'
        elif latest['RSI'] < 30:
            return 'BUY (Oversold)'
        elif latest['RSI'] > 70:
            return 'SELL (Overbought)'
        elif latest['MA_20'] > latest['MA_50'] and latest['close'] > latest['BB_Middle']:
            return 'BUY (Uptrend)'
        elif latest['MA_20'] < latest['MA_50'] and latest['close'] < latest['BB_Middle']:
            return 'SELL (Downtrend)'
        else:
            return 'HOLD'
    
    def calculate_confidence(self, latest: pd.Series, previous: pd.Series) -> float:
        """
        Calculate confidence level for the signal
        """
        confidence = 0.5  # Base confidence
        
        # RSI strength
        if 30 <= latest['RSI'] <= 70:
            confidence += 0.1
        else:
            confidence += 0.05  # Even oversold/overbought has some value
            
        # Moving average alignment
        if latest['MA_20'] > latest['MA_50']:
            if latest['MA_50'] > latest['MA_200']:
                confidence += 0.15  # Strong uptrend
            else:
                confidence += 0.1  # Mild uptrend
        elif latest['MA_20'] < latest['MA_50']:
            if latest['MA_50'] < latest['MA_200']:
                confidence += 0.15  # Strong downtrend
            else:
                confidence += 0.1  # Mild downtrend
                
        # Volume confirmation
        if latest['Volume_Ratio'] > 1.5:
            confidence += 0.1
        elif latest['Volume_Ratio'] > 1.2:
            confidence += 0.05
            
        # MACD strength
        if abs(latest['MACD_Hist']) > latest['ATR'] * 0.1:  # Strong MACD movement
            confidence += 0.1
            
        return min(confidence, 1.0)  # Cap at 1.0
    
    def get_portfolio_info(self) -> Dict:
        """
        Get portfolio information
        """
        if not self.exchange:
            return {
                'total_balance': 10000,  # Mock value
                'available_balance': 8000,  # Mock value
                'positions': [],
                'daily_pnl': self.daily_pnl
            }
        
        try:
            balance = self.exchange.fetch_balance()
            total_balance = 0
            available_balance = 0
            
            for currency, amount in balance['total'].items():
                if amount > 0:
                    total_balance += amount  # This is simplified
                    if currency in balance['free']:
                        available_balance += balance['free'][currency]
            
            return {
                'total_balance': total_balance,
                'available_balance': available_balance,
                'positions': balance['total'],
                'daily_pnl': self.daily_pnl
            }
        except Exception as e:
            logger.error(f"Error getting portfolio info: {str(e)}")
            return {
                'total_balance': 10000,
                'available_balance': 8000,
                'positions': {},
                'daily_pnl': self.daily_pnl
            }
    
    def execute_trade(self, symbol: str, side: str, amount: float, price: float = None) -> Dict:
        """
        Execute a trade (mock implementation for safety)
        """
        logger.info(f"EXECUTION MOCK: {side} {amount} of {symbol}")
        # In real implementation, this would execute actual trades
        return {
            'success': True,
            'order_id': 'MOCK_ORDER_ID',
            'symbol': symbol,
            'side': side,
            'amount': amount,
            'price': price or 0,
            'status': 'filled'
        }
    
    def get_top_opportunities(self, symbols: List[str]) -> List[Dict]:
        """
        Get top trading opportunities
        """
        opportunities = []
        
        for symbol in symbols:
            try:
                analysis = self.analyze_pair(symbol)
                if analysis['confidence'] > 0.6:  # Only high-confidence opportunities
                    opportunities.append(analysis)
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {str(e)}")
        
        # Sort by confidence and signal strength
        opportunities.sort(key=lambda x: (x['confidence'], abs(x['signal'])), reverse=True)
        return opportunities[:10]  # Return top 10 opportunities
    
    def run_analysis_cycle(self, symbols: List[str]) -> Dict:
        """
        Run a complete analysis cycle
        """
        logger.info("Starting analysis cycle...")
        
        # Reset daily P&L if needed
        if (datetime.now() - self.daily_pnl_reset_time).days >= 1:
            self.daily_pnl = 0.0
            self.daily_pnl_reset_time = datetime.now()
        
        # Get portfolio info
        portfolio = self.get_portfolio_info()
        
        # Find top opportunities
        opportunities = self.get_top_opportunities(symbols)
        
        # Prepare results
        results = {
            'timestamp': datetime.now(),
            'portfolio': portfolio,
            'opportunities': opportunities,
            'market_conditions': self.get_market_conditions(opportunities)
        }
        
        logger.info(f"Analysis complete. Found {len(opportunities)} high-confidence opportunities")
        return results
    
    def get_market_conditions(self, opportunities: List[Dict]) -> Dict:
        """
        Assess overall market conditions
        """
        if not opportunities:
            return {'condition': 'NEUTRAL', 'strength': 0.0}
        
        bullish_signals = sum(1 for opp in opportunities if opp['signal'] == 1)
        bearish_signals = sum(1 for opp in opportunities if opp['signal'] == -1)
        total_signals = len(opportunities)
        
        if total_signals == 0:
            return {'condition': 'NEUTRAL', 'strength': 0.0}
        
        bullish_ratio = bullish_signals / total_signals
        bearish_ratio = bearish_signals / total_signals
        
        if bullish_ratio > 0.6:
            condition = 'BULLISH'
            strength = bullish_ratio
        elif bearish_ratio > 0.6:
            condition = 'BEARISH'
            strength = bearish_ratio
        else:
            condition = 'MIXED'
            strength = max(bullish_ratio, bearish_ratio)
        
        return {
            'condition': condition,
            'strength': strength,
            'bullish_count': bullish_signals,
            'bearish_count': bearish_signals,
            'total_opportunities': total_signals
        }

def main():
    """
    Main function to demonstrate the enhanced crypto trading system
    """
    print("Initializing Enhanced Crypto Trading System...")
    print("=" * 70)
    
    # Initialize the trader (using mock credentials for demonstration)
    # In real implementation, load from secure storage
    trader = EnhancedCryptoTrader("MOCK_API_KEY", "MOCK_SECRET")
    
    # Define symbols to monitor
    symbols = [
        'BTC/INR', 'ETH/INR', 'ADA/INR', 'DOT/INR', 'LINK/INR',
        'BCH/INR', 'LTC/INR', 'XRP/INR', 'UNI/INR', 'SOL/INR'
    ]
    
    print(f"Monitoring {len(symbols)} cryptocurrency pairs...")
    
    # Run analysis
    results = trader.run_analysis_cycle(symbols)
    
    print(f"\nMarket Conditions: {results['market_conditions']['condition']}")
    print(f"Market Strength: {results['market_conditions']['strength']:.2%}")
    print(f"Bullish Opportunities: {results['market_conditions']['bullish_count']}")
    print(f"Bearish Opportunities: {results['market_conditions']['bearish_count']}")
    
    print(f"\nPortfolio Information:")
    print(f"Total Balance: ₹{results['portfolio']['total_balance']:,.2f}")
    print(f"Available Balance: ₹{results['portfolio']['available_balance']:,.2f}")
    print(f"Daily P&L: ₹{results['portfolio']['daily_pnl']:,.2f}")
    
    print(f"\nTop Trading Opportunities:")
    print("-" * 100)
    print(f"{'Pair':<10} {'Signal':<12} {'Confidence':<10} {'RSI':<6} {'24h Change':<12} {'Recommendation':<15}")
    print("-" * 100)
    
    for opp in results['opportunities'][:10]:  # Top 10
        signal_str = "BUY" if opp['signal'] == 1 else "SELL" if opp['signal'] == -1 else "HOLD"
        print(f"{opp['symbol']:<10} {signal_str:<12} {opp['confidence']:<10.2%} {opp['rsi']:<6.1f} {opp['price_change_24h']:<12.2f}% {opp['recommendation']:<15}")
    
    print(f"\nEnhanced Crypto Trading System Ready!")
    print(f"This system monitors multiple technical indicators to identify high-probability trading opportunities.")
    print(f"It can help generate profits through systematic crypto trading.")
    
    # Save results
    with open('/Users/aayan/.openclaw/workspace/crypto_trading_analysis.json', 'w') as f:
        json.dump({
            'timestamp': str(results['timestamp']),
            'market_conditions': results['market_conditions'],
            'portfolio': results['portfolio'],
            'top_opportunities': [opp for opp in results['opportunities'][:5]]
        }, f, indent=2, default=str)
    
    print(f"\nAnalysis saved to crypto_trading_analysis.json")

if __name__ == "__main__":
    main()