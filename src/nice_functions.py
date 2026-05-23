"""
NICE FUNCTIONS - Moon Dev's Reusable Trading Functions
=======================================================

This file contains ALL the functions you'll reuse across multiple bots.
Instead of writing 500+ lines per bot, you write 90 lines and call these functions.

Moon Dev's Philosophy:
"Every day you code is easier because you reuse yesterday's work.
 Today's 4 hours of work = 8 hours because you used yesterday's code."

Usage:
    import nice_functions as n
    
    # Then use:
    account = await n.get_account(exchange)
    n.cancel_all_orders(exchange, symbol)
    positions = await n.get_positions(exchange)
"""

import asyncio
import time
from datetime import datetime, timedelta
from termcolor import cprint
import pandas as pd
import pandas_ta as ta

# ============================================================================
# ACCOUNT & POSITION MANAGEMENT
# ============================================================================

async def get_account(broker_manager):
    """
    Get account information (equity, buying power, etc.)
    Works with: Alpaca, CCXT exchanges, HyperLiquid
    """
    try:
        account = await broker_manager.get_account()
        return account
    except Exception as e:
        cprint(f"Error getting account: {e}", "red")
        return None


async def get_positions(broker_manager):
    """
    Get all open positions
    Returns list of positions with symbol, qty, avg_entry, unrealized_pl
    """
    try:
        positions = await broker_manager.get_positions()
        return positions
    except Exception as e:
        cprint(f"Error getting positions: {e}", "red")
        return []


async def get_open_positions(broker_manager, symbol=None):
    """
    Check if we're in a position for a specific symbol
    Returns: (in_position: bool, position_size: float, entry_price: float)
    """
    positions = await get_positions(broker_manager)
    
    if symbol:
        for p in positions:
            if p.symbol == symbol:
                return True, float(p.qty), float(p.avg_entry_price)
        return False, 0.0, 0.0
    else:
        return len(positions) > 0, positions


async def cancel_all_orders(broker_manager, symbol=None):
    """
    Cancel all open orders (or for specific symbol)
    
    Moon Dev: "Floating orders have cost me thousands. 
               I cancel all orders before placing new ones."
    """
    try:
        if symbol:
            cprint(f"Cancelling all orders for {symbol}...", "yellow")
        else:
            cprint("Cancelling ALL open orders...", "yellow")
        
        await broker_manager.cancel_all_orders(symbol)
        cprint("✅ Orders cancelled", "green")
        return True
    except Exception as e:
        cprint(f"Error cancelling orders: {e}", "red")
        return False


# ============================================================================
# ORDER EXECUTION
# ============================================================================

async def place_market_order(broker_manager, symbol, side, quantity, **kwargs):
    """
    Place a market order (buys/sells immediately at current price)
    
    Args:
        symbol: Stock/crypto symbol
        side: 'buy' or 'sell'
        quantity: Number of shares/contracts
        **kwargs: stop_loss, take_profit, etc.
    """
    try:
        cprint(f"Placing MARKET {side.upper()} order: {quantity} {symbol}", "cyan")
        order = await broker_manager.place_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type='market',
            **kwargs
        )
        cprint(f"✅ Order placed: {order.id}", "green")
        return order
    except Exception as e:
        cprint(f"❌ Error placing order: {e}", "red")
        return None


async def place_limit_order(broker_manager, symbol, side, quantity, limit_price, **kwargs):
    """
    Place a limit order (only fills at specified price or better)
    
    Moon Dev: "I use the 11th bid/ask, not the first. 
               Passive orders save on fees and get better fills."
    """
    try:
        cprint(f"Placing LIMIT {side.upper()} order: {quantity} {symbol} @ ${limit_price}", "cyan")
        order = await broker_manager.place_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type='limit',
            limit_price=limit_price,
            **kwargs
        )
        cprint(f"✅ Limit order placed: {order.id}", "green")
        return order
    except Exception as e:
        cprint(f"❌ Error placing limit order: {e}", "red")
        return None


# ============================================================================
# MARKET DATA
# ============================================================================

async def get_current_price(broker_manager, symbol):
    """Get current bid/ask/last price for a symbol"""
    try:
        quote = await broker_manager.get_quote(symbol)
        return {
            'bid': quote.bid_price,
            'ask': quote.ask_price,
            'last': quote.last_price
        }
    except Exception as e:
        cprint(f"Error getting price for {symbol}: {e}", "red")
        return None


async def get_historical_data(broker_manager, symbol, timeframe, lookback_days=30):
    """
    Get historical OHLCV data
    
    Returns: pandas DataFrame with columns: open, high, low, close, volume
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        df = await broker_manager.get_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date
        )
        
        if df.empty:
            cprint(f"No historical data for {symbol}", "yellow")
            return pd.DataFrame()
        
        return df
    except Exception as e:
        cprint(f"Error getting historical data: {e}", "red")
        return pd.DataFrame()


def get_ask_bid_from_orderbook(orderbook_data, level=1):
    """
    Get bid/ask from order book at specified level
    
    Args:
        orderbook_data: Order book dict with 'bids' and 'asks'
        level: 1 = best bid/ask, 11 = 11th best (Moon Dev's favorite)
    
    Returns: (bid_price, ask_price)
    """
    try:
        bid = float(orderbook_data['bids'][level-1][0])
        ask = float(orderbook_data['asks'][level-1][0])
        return bid, ask
    except IndexError:
        cprint(f"Order book doesn't have {level} levels", "yellow")
        return None, None


# ============================================================================
# TECHNICAL INDICATORS (using pandas-ta)
# ============================================================================

def calculate_sma(data, period=20):
    """Simple Moving Average"""
    return ta.sma(data, length=period)


def calculate_ema(data, period=20):
    """Exponential Moving Average"""
    return ta.ema(data, length=period)


def calculate_rsi(data, period=14):
    """Relative Strength Index"""
    return ta.rsi(data, length=period)


def calculate_vwap(df):
    """
    Volume Weighted Average Price
    
    Moon Dev: "VWAP is the best-kept secret of hedge funds"
    """
    if 'high' not in df.columns or 'low' not in df.columns:
        cprint("Need 'high', 'low', 'close', 'volume' columns for VWAP", "red")
        return None
    
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    return (typical_price * df['volume']).cumsum() / df['volume'].cumsum()


def calculate_vwma(data, volume, period=20):
    """
    Volume Weighted Moving Average
    
    Moon Dev: "Took me 200 hours to code this perfectly"
    """
    return (data * volume).rolling(window=period).sum() / volume.rolling(window=period).sum()


def calculate_bollinger_bands(data, period=20, std=2):
    """Bollinger Bands (upper, middle, lower)"""
    bbands = ta.bbands(data, length=period, std=std)
    return bbands


def calculate_macd(data, fast=12, slow=26, signal=9):
    """MACD (Moving Average Convergence Divergence)"""
    macd = ta.macd(data, fast=fast, slow=slow, signal=signal)
    return macd


def calculate_atr(df, period=14):
    """Average True Range (volatility indicator)"""
    return ta.atr(df['high'], df['low'], df['close'], length=period)


def calculate_adx(df, period=14):
    """Average Directional Index (trend strength)"""
    return ta.adx(df['high'], df['low'], df['close'], length=period)


# ============================================================================
# RISK MANAGEMENT
# ============================================================================

async def check_position_pnl(broker_manager, symbol, target_profit_pct, max_loss_pct):
    """
    Check if position has hit profit target or stop loss
    
    Returns: ('CLOSE', reason) if should close, else (None, None)
    """
    positions = await get_positions(broker_manager)
    
    for p in positions:
        if p.symbol == symbol:
            pnl_pct = (float(p.unrealized_pl) / float(p.cost_basis)) * 100
            
            if pnl_pct >= target_profit_pct:
                return 'CLOSE', f'Hit profit target: {pnl_pct:.2f}%'
            elif pnl_pct <= -abs(max_loss_pct):
                return 'CLOSE', f'Hit stop loss: {pnl_pct:.2f}%'
    
    return None, None


async def check_daily_loss_limit(broker_manager, initial_equity, max_daily_loss_pct):
    """
    Check if we've hit daily loss limit (Moon Dev's kill switch)
    
    Returns: True if should stop trading
    """
    account = await get_account(broker_manager)
    if not account:
        return False
    
    current_equity = float(account.equity)
    loss_pct = ((initial_equity - current_equity) / initial_equity) * 100
    
    if loss_pct >= max_daily_loss_pct:
        cprint(f"🚨 DAILY LOSS LIMIT HIT: {loss_pct:.2f}% 🚨", "red", attrs=['bold'])
        return True
    
    return False


def calculate_position_size(account_equity, risk_per_trade_pct, entry_price, stop_loss_price):
    """
    Calculate position size based on risk management
    
    Moon Dev's Rule: Never risk more than 1-2% per trade
    
    Args:
        account_equity: Total account value
        risk_per_trade_pct: % of account to risk (e.g., 0.02 for 2%)
        entry_price: Your entry price
        stop_loss_price: Your stop loss price
    
    Returns: Number of shares/contracts to buy
    """
    risk_amount = account_equity * risk_per_trade_pct
    risk_per_share = abs(entry_price - stop_loss_price)
    
    if risk_per_share == 0:
        cprint("⚠️ Stop loss = entry price. Cannot calculate position size.", "yellow")
        return 0
    
    position_size = int(risk_amount / risk_per_share)
    
    cprint(f"Position Sizing:", "cyan")
    cprint(f"  Risk Amount: ${risk_amount:.2f}", "cyan")
    cprint(f"  Risk Per Share: ${risk_per_share:.2f}", "cyan")
    cprint(f"  Position Size: {position_size} shares", "cyan")
    
    return position_size


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def sleep_between_orders(seconds=60):
    """
    Sleep to avoid over-trading
    
    Moon Dev: "Sometimes I only want to trade every 20 minutes"
    """
    cprint(f"💤 Sleeping for {seconds} seconds to avoid over-trading...", "yellow")
    time.sleep(seconds)


async def check_order_book_sentiment(orderbook_data, loops=12, sleep_seconds=5):
    """
    Moon Dev's order book analysis
    
    Collects order book data over time and determines if more buyers or sellers
    
    Args:
        orderbook_data: Function that returns fresh order book
        loops: Number of times to check (12 loops × 5 sec = 60 seconds)
        sleep_seconds: Seconds between checks
    
    Returns: 'BULLISH', 'BEARISH', or 'NEUTRAL'
    """
    bid_volume_total = 0
    ask_volume_total = 0
    
    for i in range(loops):
        try:
            ob = await orderbook_data()
            
            # Sum top 10 bids and asks
            bid_vol = sum([float(bid[1]) for bid in ob['bids'][:10]])
            ask_vol = sum([float(ask[1]) for ask in ob['asks'][:10]])
            
            bid_volume_total += bid_vol
            ask_volume_total += ask_vol
            
            await asyncio.sleep(sleep_seconds)
        except Exception as e:
            cprint(f"Error in order book analysis: {e}", "red")
    
    # Determine sentiment
    if bid_volume_total > ask_volume_total * 1.2:
        return 'BULLISH'
    elif ask_volume_total > bid_volume_total * 1.2:
        return 'BEARISH'
    else:
        return 'NEUTRAL'


def format_currency(amount):
    """Format numbers as currency"""
    return f"${amount:,.2f}"


def format_percentage(value):
    """Format as percentage"""
    return f"{value:.2f}%"


def print_trade_summary(symbol, side, quantity, entry_price, exit_price=None, pnl=None):
    """Pretty print trade information"""
    cprint("=" * 50, "cyan")
    cprint(f"  TRADE: {side.upper()} {quantity} {symbol}", "white", attrs=['bold'])
    cprint(f"  Entry: {format_currency(entry_price)}", "cyan")
    if exit_price:
        cprint(f"  Exit: {format_currency(exit_price)}", "cyan")
    if pnl:
        color = "green" if pnl > 0 else "red"
        cprint(f"  P&L: {format_currency(pnl)}", color, attrs=['bold'])
    cprint("=" * 50, "cyan")


# ============================================================================
# ROSS CAMERON SPECIFIC FUNCTIONS
# ============================================================================

def calculate_rvol(current_volume, avg_volume_list):
    """
    Relative Volume - Ross Cameron's key metric
    
    Args:
        current_volume: Today's volume so far
        avg_volume_list: List of past volumes for same time
    
    Returns: RVOL ratio (>2.0 is high, per Ross)
    """
    if not avg_volume_list or len(avg_volume_list) == 0:
        return 0
    
    avg_vol = sum(avg_volume_list) / len(avg_volume_list)
    
    if avg_vol == 0:
        return 0
    
    rvol = current_volume / avg_vol
    return rvol


def check_gap_up(today_open, yesterday_close):
    """
    Check for gap-up (Ross Cameron's favorite setup)
    
    Returns: (gap_percent, is_gap)
    """
    gap_percent = ((today_open - yesterday_close) / yesterday_close) * 100
    is_gap = gap_percent >= 5.0  # Ross looks for 5%+ gaps
    
    return gap_percent, is_gap


def check_bull_flag(df, window=20):
    """
    Detect bull flag pattern (Ross Cameron's bread and butter)
    
    A bull flag is:
    - Strong uptrend (flagpole)
    - Followed by consolidation/pullback (flag)
    - Then breakout to new highs
    """
    if len(df) < window:
        return False
    
    recent_data = df.tail(window)
    
    # Check for prior strong move (flagpole)
    early_close = recent_data['close'].iloc[0]
    mid_high = recent_data['high'].iloc[window//2]
    flagpole_gain = ((mid_high - early_close) / early_close) * 100
    
    # Check for consolidation (flag)
    recent_close = recent_data['close'].iloc[-1]
    consolidation = abs(((recent_close - mid_high) / mid_high) * 100)
    
    # Bull flag criteria
    is_bull_flag = flagpole_gain > 10 and consolidation < 5
    
    return is_bull_flag


# ============================================================================
# MOON DEV'S PERSONAL FAVORITES
# ============================================================================

def moon_dev_print_banner():
    """Print Moon Dev's signature banner"""
    cprint("\n" + "="*60, "cyan")
    cprint("🌙 MOON DEV TRADING BOT", "white", attrs=['bold'])
    cprint("="*60 + "\n", "cyan")


def moon_dev_daily_reminder():
    """Moon Dev's daily reminder"""
    cprint("\n💡 Remember:", "yellow", attrs=['bold'])
    cprint("   - The alpha is in research & backtest, not the bot", "yellow")
    cprint("   - Never risk more than 1-2% per trade", "yellow")
    cprint("   - Emotion is the enemy. Let the algo trade.", "yellow")
    cprint("   - 95% of strategies fail. That's why you test 100.\n", "yellow")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example of how to use nice_functions.py in your bot:
    
    # In your bot file:
    import nice_functions as n
    
    # Get account
    account = await n.get_account(alpaca_manager)
    
    # Check positions
    in_position, size, entry = await n.get_open_positions(alpaca_manager, "AAPL")
    
    # Place order
    await n.place_market_order(alpaca_manager, "AAPL", "buy", 10)
    
    # Get historical data
    df = await n.get_historical_data(alpaca_manager, "AAPL", "1Day", 30)
    
    # Calculate indicators
    df['sma20'] = n.calculate_sma(df['close'], 20)
    df['vwap'] = n.calculate_vwap(df)
    
    # Risk management
    should_close, reason = await n.check_position_pnl(alpaca_manager, "AAPL", 5.0, 2.0)
    
    # Position sizing
    shares = n.calculate_position_size(10000, 0.02, 150, 145)
    """
    
    moon_dev_print_banner()
    cprint("✅ Nice Functions loaded successfully!", "green")
    cprint("\nThis file contains all the reusable functions you need.", "white")
    cprint("Import it with: import nice_functions as n\n", "cyan")
    moon_dev_daily_reminder()

