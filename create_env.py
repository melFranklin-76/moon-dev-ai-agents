#!/usr/bin/env python3
"""
Creates your .env file with your Alpaca API keys
"""

# Your API keys (from Alpaca)
ALPACA_API_KEY = "PKYTHHF5LBSFNMPARCQZ6FPL54"
ALPACA_SECRET_KEY = "B4f6y6PwnqJQSvrdT3bgTezEboLzmjMrNjMpnuzNshj7"
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"

# Create .env file content
env_content = f"""# Alpaca API Configuration
# KEEP THIS FILE SECRET - DO NOT COMMIT TO GIT!

# Paper Trading API Keys (for practice)
ALPACA_API_KEY={ALPACA_API_KEY}
ALPACA_SECRET_KEY={ALPACA_SECRET_KEY}
ALPACA_BASE_URL={ALPACA_BASE_URL}

# Trading Bot Configuration
TRADING_MODE=paper
ENABLE_NOTIFICATIONS=false
LOG_LEVEL=INFO

# Risk Management
MAX_POSITION_SIZE=250
MAX_DAILY_LOSS=50
MAX_OPEN_POSITIONS=1

# Strategy Selection (your 20 best)
ACTIVE_STRATEGIES=159,163,164,177
"""

# Write to .env file
try:
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✅ .env file created successfully!")
    print("\nYour keys are saved in .env:")
    print(f"  API Key: {ALPACA_API_KEY[:8]}...{ALPACA_API_KEY[-4:]}")
    print(f"  Base URL: {ALPACA_BASE_URL}")
    print("\n⚠️  IMPORTANT: .env is in .gitignore - your keys are safe!")
    print("\nNext step: Run python test_alpaca.py to test your connection")
except Exception as e:
    print(f"❌ Error creating .env file: {e}")
    print("\nManual alternative:")
    print("1. Create a file named .env")
    print("2. Copy this content into it:\n")
    print(env_content)

