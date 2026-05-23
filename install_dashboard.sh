#!/bin/bash
# Quick Dashboard Installation Script

echo "🌙 Installing Small Account Dashboard..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install packages
echo "📥 Installing required packages..."
pip install --upgrade pip
pip install streamlit plotly pandas alpaca-trade-api python-dotenv

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Run: python3 create_env.py"
    echo ""
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 To run your dashboard:"
echo "   source venv/bin/activate"
echo "   streamlit run small_account_dashboard.py"
echo ""
echo "📚 Read DASHBOARD_SETUP.md for full guide"
echo ""

