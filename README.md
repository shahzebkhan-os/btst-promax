# NSE Option Chain Analyzer

A comprehensive Python tool for analyzing NSE (National Stock Exchange of India) option chain data with an intuitive share selection feature.

## 🎯 Features

- **Share Selection**: Choose any stock from the Nifty 50 for detailed option chain analysis
- **Option Chain Data**: View complete call and put option data including strike prices, premiums, volume, open interest, and implied volatility
- **Key Level Analysis**: Identify ATM (At-The-Money) strikes, max pain levels, and support/resistance zones
- **Volume & Open Interest Analysis**: Analyze top strikes by volume and open interest
- **Market Sentiment**: Calculate and interpret put/call ratios
- **Trading Recommendations**: Get actionable insights based on option chain data
- **Multiple Expirations**: Access and analyze different expiration dates
- **Export Capability**: Save analysis results to JSON files

## 🛠️ Requirements

- Python 3.7+
- yfinance
- pandas
- numpy

## 📦 Installation

```bash
pip install yfinance pandas numpy
```

## 🚀 Usage

### Command Line Interface

```bash
python option_chain_analyzer.py
```

Follow the interactive prompts to:
1. List available stocks (Nifty 50)
2. Select a specific stock for analysis
3. Choose expiration date (or use nearest)
4. View comprehensive option chain analysis

### Programmatic Usage

```python
from option_chain_analyzer import NSEOptionChainAnalyzer

analyzer = NSEOptionChainAnalyzer()

# Analyze a specific stock
result = analyzer.create_summary_report('SBIN.NS')

# Or specify an expiration date
result = analyzer.create_summary_report('TCS.NS', '2026-02-26')
```

## 📊 Analysis Components

### Stock Information
- Current price
- Sector and industry classification
- Market capitalization

### Option Chain Metrics
- Strike prices with corresponding premiums
- Bid/Ask spreads
- Volume and open interest
- Implied volatility
- In-the-money/Out-of-the-money status

### Key Levels
- At-the-Money (ATM) strike
- Max Pain level
- Highest volume strike
- Support and resistance levels based on open interest

### Ratios & Indicators
- Put/Call Open Interest Ratio
- Put/Call Volume Ratio
- Implied volatility analysis

### Trading Insights
- Support and resistance levels
- Market sentiment interpretation
- High probability trade setups
- Key strike recommendations

## 🏛️ Supported Stocks

The tool includes all Nifty 50 stocks:
- RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS, HINDUNILVR.NS
- ICICIBANK.NS, SBIN.NS, BHARTIARTL.NS, ITC.NS, KOTAKBANK.NS
- And 40+ more major Indian stocks

## 📈 Example Output

```
🔍 Analyzing Option Chain for: SBIN.NS
============================================================

📈 STOCK INFO: SBIN.NS
----------------------------------------
Current Price: ₹785.10
Sector: Financial Services
Industry: Banks

📅 EXPIRATION DATE: 2026-02-26
----------------------------------------

📊 OPTION CHAIN ANALYSIS:
----------------------------------------
At-the-Money Strike: ₹785.00
Max Pain Level: ₹790.00
Highest Volume Strike: ₹780.00
Total Call OI: 1,234,567
Total Put OI: 987,654
Put/Call OI Ratio: 0.80
Total Call Volume: 234,567
Total Put Volume: 187,654
Put/Call Volume Ratio: 0.80

🎯 TOP STRIKES BY OPEN INTEREST:
----------------------------------------
1. Strike: ₹780.00 | Type: CALL | OI: 123,456 | Vol: 12,345 | IV: 25.4%
2. Strike: ₹790.00 | Type: PUT | OI: 112,345 | Vol: 11,234 | IV: 24.8%
3. Strike: ₹785.00 | Type: CALL | OI: 101,234 | Vol: 10,123 | IV: 25.1%
```

## 🤝 Contributing

Contributions are welcome! Feel free to submit a Pull Request for:

- Bug fixes
- New analysis features
- UI improvements
- Additional stock coverage
- Performance optimizations

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and informational purposes only. It does not constitute investment advice. Always do your own research and consult with qualified financial advisors before making investment decisions. Trading options involves substantial risk and may not be suitable for all investors.

## 🆘 Support

If you encounter any issues or have suggestions for improvements, please create an issue in this repository.