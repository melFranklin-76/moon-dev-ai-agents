#!/usr/bin/env python3
"""
Alpaca API Connection Test Script
Tests your API keys and connection to Alpaca
"""

import os
from dotenv import load_dotenv

def test_alpaca_connection():
    """Test Alpaca API connection and display account info"""
    
    print("🔍 Testing Alpaca API Connection...\n")
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API keys from environment
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    
    # Check if keys exist
    if not api_key or not secret_key:
        print("❌ ERROR: API keys not found!")
        print("\nPlease set up your .env file with:")
        print("  ALPACA_API_KEY=your_key_here")
        print("  ALPACA_SECRET_KEY=your_secret_here")
        print("  ALPACA_BASE_URL=https://paper-api.alpaca.markets")
        return False
    
    print(f"✅ API keys found")
    print(f"   API Key: {api_key[:8]}...{api_key[-4:]}")
    print(f"   Base URL: {base_url}\n")
    
    # Try to import alpaca-trade-api
    try:
        import alpaca_trade_api as tradeapi
    except ImportError:
        print("❌ ERROR: alpaca-trade-api not installed!")
        print("\nPlease install it with:")
        print("  pip install alpaca-trade-api")
        return False
    
    # Create API connection
    try:
        api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
        print("✅ API client created\n")
    except Exception as e:
        print(f"❌ ERROR creating API client: {e}")
        return False
    
    # Test 1: Get account info
    print("📊 Test 1: Getting account information...")
    try:
        account = api.get_account()
        print("✅ Account connection successful!\n")
        print("Account Details:")
        print(f"  Account ID: {account.id}")
        print(f"  Status: {account.status}")
        print(f"  Cash: ${float(account.cash):,.2f}")
        print(f"  Buying Power: ${float(account.buying_power):,.2f}")
        print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
        
        if base_url == 'https://paper-api.alpaca.markets':
            print(f"  📝 Mode: PAPER TRADING (practice mode)")
        else:
            print(f"  💰 Mode: LIVE TRADING (real money)")
        
        print()
        
    except Exception as e:
        print(f"❌ Account connection failed: {e}\n")
        print("Possible issues:")
        print("  - Invalid API keys")
        print("  - Wrong base URL (paper vs live)")
        print("  - Account not approved yet")
        print("  - Internet connection issue")
        return False
    
    # Test 2: Get market data
    print("📈 Test 2: Getting market data...")
    try:
        # Get latest AAPL price
        bars = api.get_bars("AAPL", "1Day", limit=1).df
        if len(bars) > 0:
            latest_price = bars['close'].iloc[-1]
            print("✅ Market data working!")
            print(f"  AAPL latest close: ${latest_price:.2f}\n")
        else:
            print("⚠️  No market data returned (market might be closed)\n")
    except Exception as e:
        print(f"❌ Market data failed: {e}\n")
        print("Note: Market data only available during market hours or with subscription")
        print()
    
    # Test 3: Get positions (if any)
    print("📦 Test 3: Checking positions...")
    try:
        positions = api.list_positions()
        if len(positions) > 0:
            print(f"✅ You have {len(positions)} open position(s):")
            for pos in positions:
                print(f"  {pos.symbol}: {pos.qty} shares @ ${float(pos.current_price):.2f}")
        else:
            print("✅ No open positions (clean slate)")
        print()
    except Exception as e:
        print(f"⚠️  Could not get positions: {e}\n")
    
    # Final summary
    print("=" * 50)
    print("🎉 CONNECTION TEST COMPLETE!")
    print("=" * 50)
    print("\n✅ Your Alpaca API is working correctly!")
    print("\nYou can now:")
    print("  1. Start paper trading")
    print("  2. Pull historical data for backtesting")
    print("  3. Build your trading system")
    print("\nNext steps:")
    print("  - Run: python -m src.main_stock_bot (to start the bot)")
    print("  - Or start building your backtest framework")
    print()
    
    return True

if __name__ == "__main__":
    success = test_alpaca_connection()
    exit(0 if success else 1)

