# NSE Option Chain Analyzer - Project Structure

## Overview
This project provides a comprehensive tool for analyzing NSE (National Stock Exchange of India) option chain data with an intuitive share selection feature.

## Directory Structure
```
NSE-Option-Chain-Analyzer/
├── option_chain_analyzer.py     # Main analyzer class and CLI
├── web_interface.py             # Flask web interface
├── example_usage.py             # Example usage demonstrations
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── setup.py                   # Package setup file
├── config.json               # Configuration settings
├── .github/
│   └── workflows/
│       └── python-app.yml    # GitHub Actions workflow
└── PROJECT_STRUCTURE.md      # This file
```

## Key Files Description

### `option_chain_analyzer.py`
- Main class `NSEOptionChainAnalyzer` with comprehensive option chain analysis features
- Share selection functionality for Nifty 50 stocks
- Option chain data retrieval and processing
- Key level analysis (ATM, max pain, support/resistance)
- Trading recommendations based on option metrics
- Interactive CLI interface

### `web_interface.py`
- Flask-based web interface for the analyzer
- HTML/CSS/JavaScript frontend for stock selection
- AJAX-powered analysis without page refresh
- Responsive design for desktop and mobile
- Real-time results display

### `example_usage.py`
- Demonstrates various ways to use the analyzer
- Shows different analysis scenarios
- Batch analysis examples
- Sample outputs and interpretations

### `requirements.txt`
- Lists all required Python packages
- Compatible with latest versions
- Minimal dependencies for lightweight installation

### `setup.py`
- Package configuration for distribution
- Entry point for command-line usage
- Metadata for PyPI publication

### `README.md`
- Comprehensive documentation
- Installation instructions
- Usage examples
- Feature descriptions
- Contribution guidelines

## Features Implemented

### 1. Share Selection
- Browse all Nifty 50 stocks
- Search functionality
- Detailed stock information

### 2. Option Chain Data
- Complete call and put options data
- Strike prices, premiums, volume, OI
- Implied volatility metrics
- In-the-money/out-of-the-money status

### 3. Analysis Features
- ATM (At-The-Money) strike identification
- Max pain level calculation
- Support/resistance level detection
- Put/call ratio analysis
- Volume and open interest analysis

### 4. Trading Insights
- Market sentiment interpretation
- High probability trade setups
- Key level recommendations
- Risk management suggestions

### 5. Output Formats
- Console display with formatting
- JSON export capability
- Structured data access
- Web interface visualization

## Usage Scenarios

### Command Line Interface
```bash
python option_chain_analyzer.py
```

### Programmatic Access
```python
from option_chain_analyzer import NSEOptionChainAnalyzer
analyzer = NSEOptionChainAnalyzer()
result = analyzer.create_summary_report('SBIN.NS')
```

### Web Interface
```bash
python web_interface.py
# Then visit http://localhost:5000
```

### Example Usage
```bash
python example_usage.py
```

## Technical Requirements

### Dependencies
- yfinance: For stock and option data retrieval
- pandas: For data manipulation
- numpy: For numerical computations
- Flask: For web interface (optional)

### Compatibility
- Python 3.7+
- Works on Windows, Mac, Linux
- Internet connection required for market data
- No special hardware requirements

## Future Enhancements

### Planned Features
- Real-time data streaming
- Advanced technical indicators
- Portfolio tracking
- Alert systems
- Mobile app interface
- Historical analysis
- Backtesting capabilities

### Potential Integrations
- Trading platform APIs
- Charting libraries
- News feeds
- Economic calendar
- Social sentiment analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please create an issue in the repository.