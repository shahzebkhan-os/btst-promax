"""
Web Interface for NSE Option Chain Analyzer
"""

from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
import json
from datetime import datetime
import os

# Import our analyzer class
from option_chain_analyzer import NSEOptionChainAnalyzer

app = Flask(__name__)

# Initialize the analyzer
analyzer = NSEOptionChainAnalyzer()

@app.route('/')
def index():
    """Main page with stock selection"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NSE Option Chain Analyzer</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #34495e;
            }
            input[type="text"], select {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
            }
            button {
                background-color: #3498db;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background-color: #2980b9;
            }
            .results {
                margin-top: 30px;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 5px;
                display: none;
            }
            .loading {
                text-align: center;
                padding: 20px;
                display: none;
            }
            .error {
                color: #e74c3c;
                padding: 10px;
                background-color: #fadbd8;
                border-radius: 5px;
                margin: 10px 0;
                display: none;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }
            th {
                background-color: #3498db;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            .section {
                margin: 20px 0;
                padding: 15px;
                border-left: 4px solid #3498db;
                background-color: #ecf0f1;
            }
            .recommendation {
                background-color: #d5f4e6;
                border-left: 4px solid #27ae60;
            }
            .sentiment {
                background-color: #fdeaa7;
                border-left: 4px solid #f39c12;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>NSE Option Chain Analyzer</h1>
            
            <div class="form-group">
                <label for="stock">Select Stock:</label>
                <select id="stock" onchange="loadExpirations()">
                    <option value="">Choose a stock...</option>
                    ''' + ''.join([f'<option value="{stock}">{stock}</option>' for stock in analyzer.nifty_50_stocks[:20]]) + '''
                </select>
            </div>
            
            <div class="form-group">
                <label for="custom_stock">Or enter custom stock:</label>
                <input type="text" id="custom_stock" placeholder="e.g., SBIN.NS">
            </div>
            
            <div class="form-group">
                <label for="expiration">Expiration Date:</label>
                <select id="expiration">
                    <option value="">Loading...</option>
                </select>
            </div>
            
            <button onclick="analyze()">Analyze Option Chain</button>
            
            <div class="loading" id="loading">
                <p>Analyzing option chain data...</p>
            </div>
            
            <div class="error" id="error"></div>
            
            <div class="results" id="results"></div>
        </div>

        <script>
            function loadExpirations() {
                const stock = document.getElementById('stock').value || document.getElementById('custom_stock').value;
                if (!stock) return;
                
                fetch('/get_expirations', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({stock: stock})
                })
                .then(response => response.json())
                .then(data => {
                    const select = document.getElementById('expiration');
                    select.innerHTML = '';
                    
                    if (data.success) {
                        data.expirations.forEach(exp => {
                            const option = document.createElement('option');
                            option.value = exp;
                            option.textContent = exp;
                            select.appendChild(option);
                        });
                    } else {
                        select.innerHTML = '<option value="">Error loading expirations</option>';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('error').textContent = 'Error loading expirations';
                    document.getElementById('error').style.display = 'block';
                });
            }
            
            function analyze() {
                const stock = document.getElementById('stock').value || document.getElementById('custom_stock').value;
                const expiration = document.getElementById('expiration').value;
                
                if (!stock) {
                    document.getElementById('error').textContent = 'Please select a stock';
                    document.getElementById('error').style.display = 'block';
                    return;
                }
                
                document.getElementById('loading').style.display = 'block';
                document.getElementById('error').style.display = 'none';
                document.getElementById('results').style.display = 'none';
                
                fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        stock: stock,
                        expiration: expiration
                    })
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.success) {
                        displayResults(data.result);
                    } else {
                        document.getElementById('error').textContent = data.error;
                        document.getElementById('error').style.display = 'block';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('error').textContent = 'Error analyzing option chain';
                    document.getElementById('error').style.display = 'block';
                });
            }
            
            function displayResults(result) {
                let html = `
                    <div class="section">
                        <h2>Stock Information: ${result.symbol}</h2>
                        <p><strong>Current Price:</strong> ₹${result.stock_data.current_price.toFixed(2)}</p>
                        <p><strong>Sector:</strong> ${result.stock_data.sector}</p>
                        <p><strong>Industry:</strong> ${result.stock_data.industry}</p>
                    </div>
                    
                    <div class="section">
                        <h2>Option Chain Analysis - ${result.option_data.expiration_date}</h2>
                        <p><strong>ATM Strike:</strong> ₹${result.analysis.atm_strike.toFixed(2)}</p>
                        <p><strong>Max Pain:</strong> ₹${result.analysis.max_pain.toFixed(2)}</p>
                        <p><strong>Put/Call Ratio:</strong> ${result.analysis.put_call_ratio.toFixed(2)}</p>
                    </div>
                    
                    <div class="section">
                        <h3>Top Strikes by Open Interest</h3>
                        <table>
                            <tr>
                                <th>Strike</th>
                                <th>Type</th>
                                <th>Last Price</th>
                                <th>OI</th>
                                <th>Volume</th>
                                <th>IV</th>
                            </tr>
                `;
                
                result.top_strikes.top_by_open_interest.slice(0, 5).forEach(strike => {
                    html += `
                        <tr>
                            <td>${strike.Strike}</td>
                            <td>${strike.Option_Type}</td>
                            <td>₹${strike.Last_Price.toFixed(2)}</td>
                            <td>${strike.Open_Interest.toLocaleString()}</td>
                            <td>${strike.Volume.toLocaleString()}</td>
                            <td>${(strike.IV * 100).toFixed(1)}%</td>
                        </tr>
                    `;
                });
                
                html += `
                    </table>
                </div>
                
                <div class="section recommendation">
                    <h3>Recommendations</h3>
                `;
                
                result.recommendations.forEach(rec => {
                    html += `
                        <p><strong>${rec.type}:</strong> ${rec.action} (${rec.confidence} confidence)</p>
                    `;
                });
                
                html += `
                    </div>
                `;
                
                document.getElementById('results').innerHTML = html;
                document.getElementById('results').style.display = 'block';
                document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
            }
        </script>
    </body>
    </html>
    '''

@app.route('/analyze', methods=['POST'])
def analyze_route():
    """Route to analyze option chain"""
    try:
        data = request.json
        stock = data.get('stock')
        expiration = data.get('expiration')
        
        # Validate stock symbol
        if not stock:
            return jsonify({'success': False, 'error': 'Stock symbol is required'})
        
        # Analyze the option chain
        option_data = analyzer.get_option_chain(stock, expiration)
        if not option_data:
            return jsonify({'success': False, 'error': 'Could not retrieve option chain data'})
        
        # Get stock data
        stock_data = analyzer.get_stock_data(stock)
        if not stock_data:
            return jsonify({'success': False, 'error': 'Could not retrieve stock data'})
        
        # Analyze strike levels
        analysis = analyzer.analyze_strike_levels(option_data)
        if not analysis:
            return jsonify({'success': False, 'error': 'Could not analyze strike levels'})
        
        # Get top strikes
        top_strikes = analyzer.get_top_strikes(option_data)
        if not top_strikes:
            return jsonify({'success': False, 'error': 'Could not get top strikes'})
        
        # Generate recommendations
        recommendations = analyzer.generate_recommendations(option_data)
        if not recommendations:
            recommendations = []
        
        result = {
            'symbol': stock,
            'stock_data': stock_data,
            'option_data': {
                'expiration_date': option_data['expiration_date']
            },
            'analysis': analysis,
            'top_strikes': top_strikes,
            'recommendations': recommendations
        }
        
        return jsonify({'success': True, 'result': result})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_expirations', methods=['POST'])
def get_expirations():
    """Route to get available expiration dates"""
    try:
        data = request.json
        stock = data.get('stock')
        
        if not stock:
            return jsonify({'success': False, 'error': 'Stock symbol is required'})
        
        # Get available expirations
        ticker = yf.Ticker(stock)
        expirations = ticker.options
        
        return jsonify({'success': True, 'expirations': expirations})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("Starting NSE Option Chain Analyzer Web Interface...")
    print("Visit http://localhost:5000 to access the web interface")
    app.run(debug=True, host='0.0.0.0', port=5000)