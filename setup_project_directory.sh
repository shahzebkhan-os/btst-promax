#!/bin/bash

# Script to finalize the NSE Option Chain Analyzer project setup

echo "NSE Option Chain Analyzer - Project Setup"
echo "========================================"

# Check if we're in the right directory
if [ ! -d "nse-option-chain-analyzer" ]; then
    echo "Error: nse-option-chain-analyzer directory not found!"
    exit 1
fi

echo "Project directory found."

# Navigate to the project directory
cd nse-option-chain-analyzer

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: NSE Option Chain Analyzer with share selection feature"
    echo "Git repository initialized and files committed."
else
    echo "Git repository already exists."
fi

echo ""
echo "Setup complete!"
echo "To push to GitHub, follow the instructions in GITHUB_PUSH_INSTRUCTIONS.md"
echo ""
echo "Quick summary of what's in this project:"
echo "- option_chain_analyzer.py: Main analyzer with share selection"
echo "- web_interface.py: Flask web interface"
echo "- example_usage.py: Usage examples"
echo "- README.md: Complete documentation"
echo "- Plus configuration files, workflows, and documentation"
echo ""