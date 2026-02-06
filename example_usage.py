"""
Example usage of NSE Option Chain Analyzer
"""

from option_chain_analyzer import NSEOptionChainAnalyzer

def example_analysis():
    # Initialize the analyzer
    analyzer = NSEOptionChainAnalyzer()
    
    print("NSE Option Chain Analyzer - Example Usage")
    print("="*60)
    
    # Example: Analyze State Bank of India
    print("\n1. Analyzing SBIN.NS with default settings:")
    result_sbin = analyzer.create_summary_report('SBIN.NS')
    
    print("\n" + "="*60)
    
    # Example: Analyze Tata Consultancy Services
    print("\n2. Analyzing TCS.NS with default settings:")
    result_tcs = analyzer.create_summary_report('TCS.NS')
    
    print("\n" + "="*60)
    
    # Example: Analyze with specific expiration date
    print("\n3. Analyzing INFY.NS with specific expiration:")
    # Note: Use an actual expiration date from the available dates
    result_infy = analyzer.create_summary_report('INFY.NS')
    
    print("\n" + "="*60)
    
    # Example: Get just the top strikes without full analysis
    print("\n4. Getting top strikes for HINDUNILVR.NS:")
    option_data = analyzer.get_option_chain('HINDUNILVR.NS')
    if option_data:
        top_strikes = analyzer.get_top_strikes(option_data)
        if top_strikes:
            print("Top 3 strikes by Open Interest:")
            for i, strike in enumerate(top_strikes['top_by_open_interest'][:3]):
                print(f"  {i+1}. Strike: ₹{strike['Strike']:.2f} | Type: {strike['Option_Type']} | OI: {strike['Open_Interest']:,} | Vol: {strike['Volume']:,}")
    
    print("\n" + "="*60)
    
    # Example: Analyze market sentiment using put/call ratios
    print("\n5. Analyzing market sentiment for RELIANCE.NS:")
    option_data = analyzer.get_option_chain('RELIANCE.NS')
    if option_data:
        analysis = analyzer.analyze_strike_levels(option_data)
        if analysis:
            print(f"   Put/Call OI Ratio: {analysis['put_call_ratio']:.2f}")
            print(f"   Put/Call Volume Ratio: {analysis['put_call_volume_ratio']:.2f}")
            
            if analysis['put_call_ratio'] > 1.2:
                print("   Interpretation: Bearish sentiment (high put buying)")
            elif analysis['put_call_ratio'] < 0.8:
                print("   Interpretation: Bullish sentiment (high call buying)")
            else:
                print("   Interpretation: Neutral sentiment")

def batch_analysis_example():
    """Example of analyzing multiple stocks"""
    analyzer = NSEOptionChainAnalyzer()
    
    print("\nBatch Analysis Example:")
    print("="*40)
    
    # Select a few stocks for quick analysis
    sample_stocks = ['SBIN.NS', 'HDFCBANK.NS', 'INFY.NS']
    
    for stock in sample_stocks:
        print(f"\nAnalyzing {stock}...")
        option_data = analyzer.get_option_chain(stock)
        if option_data:
            analysis = analyzer.analyze_strike_levels(option_data)
            if analysis:
                print(f"  Current Price: ₹{analysis['underlying_price']:.2f}")
                print(f"  Put/Call OI Ratio: {analysis['put_call_ratio']:.2f}")
                print(f"  ATM Strike: ₹{analysis['atm_strike']:.2f}")

if __name__ == "__main__":
    example_analysis()
    batch_analysis_example()