"""
🌙 Moon Dev's Alpaca Broker Manager
Unified interface for stock & options trading with Alpaca
Built for Ross Cameron's Warrior Trading strategies
"""

import os
import sys
from termcolor import colored, cprint
from dotenv import load_dotenv
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

# Load environment variables
load_dotenv()

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, GetAssetsRequest
    from alpaca.trading.enums import OrderSide, TimeInForce, AssetClass, AssetStatus
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest, StockQuotesRequest, StockLatestQuoteRequest
    from alpaca.data.timeframe import TimeFrame
except ImportError:
    cprint("❌ Alpaca SDK not installed. Run: pip install alpaca-py", "red")
    sys.exit(1)


class AlpacaManager:
    """
    Alpaca broker manager for stock and options trading
    Simple interface following Ross Cameron's day trading strategies
    """

    def __init__(self, paper_trading=True):
        """
        Initialize Alpaca connection
        
        Args:
            paper_trading (bool): Use paper trading (True) or live trading (False)
        """
        try:
            # Get API keys from environment
            if paper_trading:
                api_key = os.getenv('ALPACA_PAPER_API_KEY')
                api_secret = os.getenv('ALPACA_PAPER_SECRET_KEY')
                cprint("📄 Using PAPER TRADING mode (fake money)", "yellow")
            else:
                api_key = os.getenv('ALPACA_LIVE_API_KEY')
                api_secret = os.getenv('ALPACA_LIVE_SECRET_KEY')
                cprint("💰 Using LIVE TRADING mode (REAL MONEY)", "red")
            
            if not api_key or not api_secret:
                raise ValueError(
                    f"Alpaca API keys not found in .env file!\n"
                    f"Need: ALPACA_{'PAPER' if paper_trading else 'LIVE'}_API_KEY and "
                    f"ALPACA_{'PAPER' if paper_trading else 'LIVE'}_SECRET_KEY"
                )
            
            # Initialize trading client
            self.trading_client = TradingClient(api_key, api_secret, paper=paper_trading)
            
            # Initialize data client (for market data)
            self.data_client = StockHistoricalDataClient(api_key, api_secret)
            
            self.paper_trading = paper_trading
            
            # Test connection
            account = self.trading_client.get_account()
            
            cprint(f"✅ Connected to Alpaca successfully!", "green")
            cprint(f"   Account: ${float(account.equity):,.2f}", "cyan")
            cprint(f"   Buying Power: ${float(account.buying_power):,.2f}", "cyan")
            cprint(f"   Day Trade Count: {account.daytrade_count}/3", "cyan")
            
        except Exception as e:
            cprint(f"❌ Failed to connect to Alpaca: {str(e)}", "red")
            raise

    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information
        
        Returns:
            Dict with account details
        """
        try:
            account = self.trading_client.get_account()
            
            return {
                'equity': float(account.equity),
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'portfolio_value': float(account.portfolio_value),
                'daytrade_count': int(account.daytrade_count),
                'pattern_day_trader': account.pattern_day_trader,
                'trading_blocked': account.trading_blocked,
                'account_blocked': account.account_blocked,
            }
        except Exception as e:
            cprint(f"❌ Error getting account info: {str(e)}", "red")
            return {}

    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get all open positions
        
        Returns:
            List of positions with details
        """
        try:
            positions = self.trading_client.get_all_positions()
            
            position_list = []
            for pos in positions:
                position_list.append({
                    'symbol': pos.symbol,
                    'qty': float(pos.qty),
                    'side': 'long' if float(pos.qty) > 0 else 'short',
                    'market_value': float(pos.market_value),
                    'avg_entry_price': float(pos.avg_entry_price),
                    'current_price': float(pos.current_price),
                    'unrealized_pl': float(pos.unrealized_pl),
                    'unrealized_plpc': float(pos.unrealized_plpc),
                    'cost_basis': float(pos.cost_basis),
                })
            
            return position_list
            
        except Exception as e:
            cprint(f"❌ Error getting positions: {str(e)}", "red")
            return []

    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get specific position
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Position details or None
        """
        try:
            pos = self.trading_client.get_open_position(symbol)
            
            return {
                'symbol': pos.symbol,
                'qty': float(pos.qty),
                'side': 'long' if float(pos.qty) > 0 else 'short',
                'market_value': float(pos.market_value),
                'avg_entry_price': float(pos.avg_entry_price),
                'current_price': float(pos.current_price),
                'unrealized_pl': float(pos.unrealized_pl),
                'unrealized_plpc': float(pos.unrealized_plpc),
            }
            
        except Exception as e:
            # Position doesn't exist
            return None

    def place_market_order(self, symbol: str, qty: int, side: str = 'buy') -> Optional[Dict[str, Any]]:
        """
        Place a market order (executes immediately at current price)
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            qty: Number of shares or contracts
            side: 'buy' or 'sell'
            
        Returns:
            Order details or None if failed
        """
        try:
            order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
            
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=order_side,
                time_in_force=TimeInForce.DAY
            )
            
            order = self.trading_client.submit_order(order_data)
            
            cprint(f"✅ {side.upper()} order placed: {qty} {symbol}", "green")
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'qty': float(order.qty),
                'side': order.side.value,
                'type': order.type.value,
                'status': order.status.value,
                'filled_qty': float(order.filled_qty) if order.filled_qty else 0,
            }
            
        except Exception as e:
            cprint(f"❌ Error placing order: {str(e)}", "red")
            return None

    def place_limit_order(self, symbol: str, qty: int, limit_price: float, side: str = 'buy') -> Optional[Dict[str, Any]]:
        """
        Place a limit order (only executes at specified price or better)
        
        Args:
            symbol: Stock symbol
            qty: Number of shares
            limit_price: Maximum price for buy, minimum for sell
            side: 'buy' or 'sell'
            
        Returns:
            Order details or None if failed
        """
        try:
            order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
            
            order_data = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=order_side,
                time_in_force=TimeInForce.DAY,
                limit_price=limit_price
            )
            
            order = self.trading_client.submit_order(order_data)
            
            cprint(f"✅ {side.upper()} limit order placed: {qty} {symbol} @ ${limit_price}", "green")
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'qty': float(order.qty),
                'side': order.side.value,
                'type': order.type.value,
                'limit_price': float(order.limit_price),
                'status': order.status.value,
            }
            
        except Exception as e:
            cprint(f"❌ Error placing limit order: {str(e)}", "red")
            return None

    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an open order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.trading_client.cancel_order_by_id(order_id)
            cprint(f"✅ Order {order_id} cancelled", "green")
            return True
        except Exception as e:
            cprint(f"❌ Error cancelling order: {str(e)}", "red")
            return False

    def close_position(self, symbol: str, qty: Optional[int] = None) -> bool:
        """
        Close a position (sell all or partial)
        
        Args:
            symbol: Stock symbol
            qty: Number of shares to close (None = close all)
            
        Returns:
            True if successful
        """
        try:
            if qty:
                self.trading_client.close_position(symbol, close_options={'qty': qty})
            else:
                self.trading_client.close_position(symbol)
            
            cprint(f"✅ Closed position: {symbol}", "green")
            return True
            
        except Exception as e:
            cprint(f"❌ Error closing position: {str(e)}", "red")
            return False

    def get_stock_bars(self, symbol: str, timeframe: str = '1Min', limit: int = 100) -> pd.DataFrame:
        """
        Get historical price bars for technical analysis
        
        Args:
            symbol: Stock symbol
            timeframe: '1Min', '5Min', '15Min', '1Hour', '1Day'
            limit: Number of bars to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Map timeframe string to TimeFrame enum
            tf_map = {
                '1Min': TimeFrame.Minute,
                '5Min': TimeFrame(5, TimeFrame.Unit.Minute),
                '15Min': TimeFrame(15, TimeFrame.Unit.Minute),
                '1Hour': TimeFrame.Hour,
                '1Day': TimeFrame.Day,
            }
            
            tf = tf_map.get(timeframe, TimeFrame.Minute)
            
            # Calculate start time
            now = datetime.now()
            start = now - timedelta(days=5)  # Get last 5 days of data
            
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=tf,
                start=start,
                limit=limit
            )
            
            bars = self.data_client.get_stock_bars(request)
            
            # Convert to DataFrame
            if symbol in bars:
                df = bars[symbol].df
                return df
            else:
                return pd.DataFrame()
            
        except Exception as e:
            cprint(f"❌ Error getting bars for {symbol}: {str(e)}", "red")
            return pd.DataFrame()

    def get_latest_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get latest bid/ask quote
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict with quote data
        """
        try:
            request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            quotes = self.data_client.get_stock_latest_quote(request)
            
            if symbol in quotes:
                quote = quotes[symbol]
                return {
                    'symbol': symbol,
                    'bid': float(quote.bid_price),
                    'ask': float(quote.ask_price),
                    'bid_size': int(quote.bid_size),
                    'ask_size': int(quote.ask_size),
                    'spread': float(quote.ask_price) - float(quote.bid_price),
                }
            return None
            
        except Exception as e:
            cprint(f"❌ Error getting quote for {symbol}: {str(e)}", "red")
            return None

    def is_market_open(self) -> bool:
        """
        Check if market is currently open
        
        Returns:
            True if market is open
        """
        try:
            clock = self.trading_client.get_clock()
            return clock.is_open
        except Exception as e:
            cprint(f"❌ Error checking market status: {str(e)}", "red")
            return False

    def get_market_hours(self) -> Dict[str, Any]:
        """
        Get market open/close times for today
        
        Returns:
            Dict with market hours info
        """
        try:
            clock = self.trading_client.get_clock()
            return {
                'is_open': clock.is_open,
                'next_open': clock.next_open,
                'next_close': clock.next_close,
                'timestamp': clock.timestamp,
            }
        except Exception as e:
            cprint(f"❌ Error getting market hours: {str(e)}", "red")
            return {}


def test_connection():
    """
    Test Alpaca connection - run this first!
    """
    cprint("\n" + "="*60, "cyan")
    cprint("🌙 Moon Dev's Alpaca Connection Test", "white", "on_blue")
    cprint("="*60 + "\n", "cyan")
    
    try:
        # Initialize in paper trading mode
        alpaca = AlpacaManager(paper_trading=True)
        
        # Test 1: Account info
        cprint("\n📊 Testing Account Info...", "cyan")
        account = alpaca.get_account_info()
        if account:
            cprint(f"   ✅ Equity: ${account['equity']:,.2f}", "green")
            cprint(f"   ✅ Buying Power: ${account['buying_power']:,.2f}", "green")
            cprint(f"   ✅ Day Trades Used: {account['daytrade_count']}/3", "green")
        
        # Test 2: Market status
        cprint("\n🏢 Testing Market Status...", "cyan")
        is_open = alpaca.is_market_open()
        cprint(f"   ✅ Market is {'OPEN' if is_open else 'CLOSED'}", "green" if is_open else "yellow")
        
        # Test 3: Get positions
        cprint("\n📈 Testing Positions...", "cyan")
        positions = alpaca.get_positions()
        cprint(f"   ✅ Found {len(positions)} open positions", "green")
        
        # Test 4: Get quote (SPY as test)
        cprint("\n💰 Testing Market Data (SPY)...", "cyan")
        quote = alpaca.get_latest_quote('SPY')
        if quote:
            cprint(f"   ✅ SPY Bid: ${quote['bid']:.2f}", "green")
            cprint(f"   ✅ SPY Ask: ${quote['ask']:.2f}", "green")
        
        cprint("\n" + "="*60, "cyan")
        cprint("🎉 All tests passed! You're ready to trade!", "white", "on_green")
        cprint("="*60 + "\n", "cyan")
        
        return True
        
    except Exception as e:
        cprint(f"\n❌ Connection test failed: {str(e)}", "red")
        cprint("\n💡 Make sure you have:", "yellow")
        cprint("   1. Created an Alpaca account at alpaca.markets", "yellow")
        cprint("   2. Added your API keys to the .env file", "yellow")
        cprint("   3. Installed alpaca-py: pip install alpaca-py", "yellow")
        return False


if __name__ == "__main__":
    # Run connection test
    test_connection()

