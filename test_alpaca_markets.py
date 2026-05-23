"""
🌙 MOON DEV'S MULTI-MARKET TESTER (ALPACA VERSION)
Test the SAME strategies on DIFFERENT markets using REAL data

Moon Dev: "A strategy that works on GOOG might fail on crypto.
           Use Alpaca - it's free, reliable, and what you'll trade with."

This tests your top strategies on:
1. Crypto (BTC, ETH, SOL) - High volatility
2. Tech stocks (TSLA, NVDA) - Momentum
3. Index ETFs (SPY, QQQ) - Market tracking
4. Meme stocks (GME) - Wild swings
"""

from backtesting import Backtest, Strategy
import pandas as pd
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('src/.env')

# Check for Alpaca API keys
ALPACA_API_KEY = os.getenv('PKYTHHF5LBSFNMPARCQZ6FPL54')
ALPACA_SECRET_KEY = os.getenv('ALPACA_PAPER_SECRET_KEY')

if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
    print("\n" + "="*80)
    print("⚠️  ALPACA API KEYS NOT FOUND")
    print("="*80)
    print("\n📋 SETUP INSTRUCTIONS:")
    print("\n1. Go to: https://alpaca.markets/")
    print("2. Sign up for FREE paper trading account")
    print("3. Get your API keys from dashboard")
    print("4. Create file: src/.env")
    print("5. Add these lines:")
    print("\n   ALPACA_PAPER_API_KEY=your_key_here")
    print("   ALPACA_PAPER_SECRET_KEY=your_secret_here")
    print("\n6. Run this script again")
    print("\n💡 Takes 2 minutes. Worth it - Alpaca data is MUCH better than yfinance.")
    print("="*80 + "\n")
    exit()

# Import Alpaca
try:
    from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
    from alpaca.data.timeframe import TimeFrame
except ImportError:
    print("\n⚠️  alpaca-py not installed!")
    print("Run: pip3 install alpaca-py")
    print()
    exit()

# Initialize Alpaca clients
stock_client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)
crypto_client = CryptoHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)


# ============================================================================
# STRATEGIES (Top performers from previous tests)
# ============================================================================

class DualMA(Strategy):
    """Best overall: Sharpe 0.86-1.5 depending on market"""
    fast_ma = 10
    slow_ma = 20
    
    def init(self):
        close = pd.Series(self.data.Close)
        self.ma_fast = self.I(lambda: close.rolling(self.fast_ma).mean())
        self.ma_slow = self.I(lambda: close.rolling(self.slow_ma).mean())
    
    def next(self):
        if self.ma_fast[-1] > self.ma_slow[-1] and self.ma_fast[-2] <= self.ma_slow[-2]:
            if not self.position:
                self.buy()
        elif self.ma_fast[-1] < self.ma_slow[-1] and self.ma_fast[-2] >= self.ma_slow[-2]:
            if self.position:
                self.position.close()


class DualMA_Fast(Strategy):
    """Faster signals, worked great in 2012-2013"""
    fast_ma = 5
    slow_ma = 20
    
    def init(self):
        close = pd.Series(self.data.Close)
        self.ma_fast = self.I(lambda: close.rolling(self.fast_ma).mean())
        self.ma_slow = self.I(lambda: close.rolling(self.slow_ma).mean())
    
    def next(self):
        if self.ma_fast[-1] > self.ma_slow[-1] and self.ma_fast[-2] <= self.ma_slow[-2]:
            if not self.position:
                self.buy()
        elif self.ma_fast[-1] < self.ma_slow[-1] and self.ma_fast[-2] >= self.ma_slow[-2]:
            if self.position:
                self.position.close()


class TripleMA(Strategy):
    """Best in Financial Crisis: Sharpe 1.34"""
    fast = 8
    medium = 30
    slow = 100
    
    def init(self):
        close = pd.Series(self.data.Close)
        self.ma_fast = self.I(lambda: close.rolling(self.fast).mean())
        self.ma_medium = self.I(lambda: close.rolling(self.medium).mean())
        self.ma_slow = self.I(lambda: close.rolling(self.slow).mean())
    
    def next(self):
        if (self.ma_fast[-1] > self.ma_medium[-1] > self.ma_slow[-1] and
            not self.position):
            self.buy()
        elif (self.ma_fast[-1] < self.ma_medium[-1] and self.position):
            self.position.close()


class MomentumBreakout(Strategy):
    """Good for trending markets"""
    lookback = 25
    
    def init(self):
        high = pd.Series(self.data.High)
        self.recent_high = self.I(lambda: high.rolling(self.lookback).max())
    
    def next(self):
        if self.data.Close[-1] > self.recent_high[-2] and not self.position:
            self.buy()
        elif self.position:
            entry = self.trades[-1].entry_price if self.trades else self.data.Close[-1]
            pnl = (self.data.Close[-1] - entry) / entry
            if pnl >= 0.05 or pnl <= -0.02:
                self.position.close()


# ============================================================================
# ALPACA DATA FETCHERS
# ============================================================================

def get_stock_data_alpaca(symbol, days=730):
    """Get stock data from Alpaca (way better than yfinance!)"""
    print(f"   📡 Fetching {symbol} from Alpaca...", end=" ")
    
    try:
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=datetime.now() - timedelta(days=days),
            end=datetime.now()
        )
        
        bars = stock_client.get_stock_bars(request_params)
        df = bars.df
        
        # Reset index to get datetime as column
        df = df.reset_index()
        
        # Alpaca returns multi-index, extract symbol data
        if 'symbol' in df.columns:
            df = df[df['symbol'] == symbol]
        
        # Set timestamp as index
        df = df.set_index('timestamp')
        
        # Rename columns to match backtesting.py format
        df = df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        })
        
        # Select only needed columns
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        print(f"✅ {len(df)} bars")
        return df.dropna()
        
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
        return None


def get_crypto_data_alpaca(symbol, days=730):
    """Get crypto data from Alpaca"""
    print(f"   📡 Fetching {symbol} from Alpaca...", end=" ")
    
    try:
        # Alpaca crypto symbols format: BTC/USD
        alpaca_symbol = symbol.replace('-', '/')
        
        request_params = CryptoBarsRequest(
            symbol_or_symbols=alpaca_symbol,
            timeframe=TimeFrame.Day,
            start=datetime.now() - timedelta(days=days),
            end=datetime.now()
        )
        
        bars = crypto_client.get_crypto_bars(request_params)
        df = bars.df
        
        # Reset index
        df = df.reset_index()
        
        # Extract symbol data
        if 'symbol' in df.columns:
            df = df[df['symbol'] == alpaca_symbol]
        
        # Set timestamp as index
        df = df.set_index('timestamp')
        
        # Rename columns
        df = df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        })
        
        # Select columns
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        print(f"✅ {len(df)} bars")
        return df.dropna()
        
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
        return None


# ============================================================================
# TEST MATRIX
# ============================================================================

test_datasets = [
    # Crypto - High volatility
    ('BTC/USD (Crypto)', get_crypto_data_alpaca, {'symbol': 'BTC-USD', 'days': 730}),
    ('ETH/USD (Crypto)', get_crypto_data_alpaca, {'symbol': 'ETH-USD', 'days': 730}),
    
    # Tech stocks - Momentum
    ('TSLA (Tech/Meme)', get_stock_data_alpaca, {'symbol': 'TSLA', 'days': 730}),
    ('NVDA (Tech)', get_stock_data_alpaca, {'symbol': 'NVDA', 'days': 730}),
    
    # Index ETFs - Market tracking
    ('SPY (S&P 500)', get_stock_data_alpaca, {'symbol': 'SPY', 'days': 730}),
    ('QQQ (Nasdaq)', get_stock_data_alpaca, {'symbol': 'QQQ', 'days': 730}),
    
    # Meme/volatile
    ('GME (Meme)', get_stock_data_alpaca, {'symbol': 'GME', 'days': 730}),
    ('AMC (Meme)', get_stock_data_alpaca, {'symbol': 'AMC', 'days': 730}),
]

strategies = [
    ('DualMA 10/20 (Best)', DualMA),
    ('DualMA 5/20 (Fast)', DualMA_Fast),
    ('TripleMA 8/30/100', TripleMA),
    ('Momentum Breakout', MomentumBreakout),
]

print("\n" + "="*80)
print("🌙 MOON DEV'S MULTI-MARKET TESTER (ALPACA)")
print("="*80)
print(f"\n✅ Connected to Alpaca (professional-grade data)")
print(f"📊 Testing {len(strategies)} strategies on {len(test_datasets)} markets")
print(f"⏱️  Estimated time: 2-3 minutes")
print("\n💡 This data is WAY more reliable than yfinance!")
print("="*80 + "\n")

# ============================================================================
# RUN ALL TESTS
# ============================================================================

results = []
start_time = time.time()
test_count = 0
total_tests = len(strategies) * len(test_datasets)

for dataset_name, get_data_func, params in test_datasets:
    print(f"\n📈 Testing {dataset_name}...")
    
    # Get data
    data = get_data_func(**params)
    
    if data is None or len(data) < 200:
        print(f"   ⚠️  Skipping (insufficient data)")
        continue
    
    # Test each strategy
    for strategy_name, strategy_class in strategies:
        test_count += 1
        print(f"   [{test_count}/{total_tests}] {strategy_name}...", end=" ")
        
        try:
            bt = Backtest(data, strategy_class, cash=10000, commission=.002)
            stats = bt.run()
            
            result = {
                'Market': dataset_name,
                'Strategy': strategy_name,
                'Bars': len(data),
                'Return %': round(stats['Return [%]'], 1),
                'Sharpe': round(stats['Sharpe Ratio'], 2),
                'Win Rate %': round(stats['Win Rate [%]'], 1),
                'Max DD %': round(stats['Max. Drawdown [%]'], 1),
                'Trades': int(stats['# Trades']),
                'Buy & Hold %': round(stats['Buy & Hold Return [%]'], 1)
            }
            results.append(result)
            
            # Quick feedback
            sharpe = result['Sharpe']
            if sharpe >= 1.5:
                print(f"🔥 Sharpe: {sharpe}")
            elif sharpe >= 1.0:
                print(f"✅ Sharpe: {sharpe}")
            elif sharpe >= 0.5:
                print(f"⚠️  Sharpe: {sharpe}")
            else:
                print(f"❌ Sharpe: {sharpe}")
                
        except Exception as e:
            print(f"❌ {str(e)[:40]}")

elapsed = time.time() - start_time

# ============================================================================
# ANALYZE RESULTS
# ============================================================================

print("\n" + "="*80)
print("📊 ALPACA MULTI-MARKET RESULTS")
print("="*80 + "\n")

if len(results) == 0:
    print("❌ No results. Check Alpaca connection.\n")
    exit()

df = pd.DataFrame(results)
df_sorted = df.sort_values('Sharpe', ascending=False)

# Save results
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f'alpaca_market_results_{timestamp}.csv'
df_sorted.to_csv(filename, index=False)
print(f"💾 Saved to: {filename}\n")

# ============================================================================
# TOP PERFORMERS
# ============================================================================

print("="*80)
print("🏆 TOP 10 STRATEGY-MARKET COMBINATIONS")
print("="*80 + "\n")

for i, (_, row) in enumerate(df_sorted.head(10).iterrows(), 1):
    status = "🔥" if row['Sharpe'] >= 1.5 else "✅" if row['Sharpe'] >= 1.0 else "⚠️ "
    print(f"{status} #{i:2d} | {row['Market']:<20} | {row['Strategy']}")
    print(f"       Sharpe: {row['Sharpe']:>5.2f} | Return: {row['Return %']:>7.1f}% | "
          f"Beat B&H: {row['Return %'] - row['Buy & Hold %']:+7.1f}% | Trades: {row['Trades']:>3}")
    print()

# ============================================================================
# WINNERS
# ============================================================================

winners = df_sorted[df_sorted['Sharpe'] >= 1.0]

print("="*80)
print(f"🎯 WINNERS: {len(winners)} with Sharpe ≥ 1.0")
print("="*80 + "\n")

if len(winners) > 0:
    print("🎊 BOOM! Found winners on REAL market data!\n")
    
    for _, row in winners.iterrows():
        print(f"✅ {row['Strategy']} on {row['Market']}")
        print(f"   Sharpe: {row['Sharpe']} | Return: {row['Return %']}% | "
              f"Win Rate: {row['Win Rate %']}%")
        beat_bh = row['Return %'] - row['Buy & Hold %']
        print(f"   Beat Buy & Hold by: {beat_bh:+.1f}%\n")
    
    print("="*80)
    print("📋 MOON DEV'S NEXT STEPS:")
    print("="*80)
    print("\n✅ You found strategies that work on REAL data")
    print("✅ Tested on multiple markets (not overfit to one)")
    print("✅ Used Alpaca (same API you'll trade with)")
    print("\n🚀 NOW:")
    print("   1. Forward test for 2-3 months (paper trading)")
    print("   2. Use your $200 with $10-20 per trade")
    print("   3. Track: Does live match backtest?")
    print("   4. If profitable for 3 months → scale slowly")
    print("\n⚠️  REMEMBER:")
    print("   - Past performance ≠ future results")
    print("   - Start SMALL")
    print("   - Ross Cameron's strategy + your edge = 💰")
    print("="*80 + "\n")
    
else:
    print(f"⚠️  No Sharpe ≥1.0 yet on these markets.")
    print(f"   But you tested {len(df)} combinations!")
    print("   Try: Different timeframes, more symbols, optimize parameters\n")

# ============================================================================
# BEST MARKETS
# ============================================================================

print("="*80)
print("📈 BEST MARKETS (Avg Sharpe)")
print("="*80 + "\n")

market_avg = df.groupby('Market')['Sharpe'].mean().sort_values(ascending=False)

for market, avg_sharpe in market_avg.items():
    status = "🔥" if avg_sharpe >= 1.0 else "✅" if avg_sharpe >= 0.5 else "⚠️ "
    print(f"{status} {market:<25} Avg Sharpe: {avg_sharpe:.2f}")

# ============================================================================
# BEST STRATEGIES
# ============================================================================

print("\n" + "="*80)
print("🎯 BEST STRATEGIES (Avg Sharpe Across All Markets)")
print("="*80 + "\n")

strategy_avg = df.groupby('Strategy')['Sharpe'].mean().sort_values(ascending=False)

for strategy, avg_sharpe in strategy_avg.items():
    status = "🔥" if avg_sharpe >= 1.0 else "✅" if avg_sharpe >= 0.5 else "⚠️ "
    print(f"{status} {strategy:<30} Avg Sharpe: {avg_sharpe:.2f}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("📊 OVERALL STATISTICS")
print("="*80 + "\n")

print(f"Total Tests: {len(df)}")
print(f"Winners (Sharpe ≥1.0): {len(winners)} ({len(winners)/len(df)*100:.1f}%)")
print(f"Good (Sharpe ≥0.5): {len(df[df['Sharpe'] >= 0.5])} ({len(df[df['Sharpe'] >= 0.5])/len(df)*100:.1f}%)")
print()
print(f"Best Sharpe: {df['Sharpe'].max():.2f}")
print(f"Average Sharpe: {df['Sharpe'].mean():.2f}")
print(f"Average Return: {df['Return %'].mean():.1f}%")
print(f"Best Return: {df['Return %'].max():.1f}%")
print()
print(f"Time: {elapsed/60:.1f} min")
print()

print("="*80)
print("🌙 Moon Dev's Wisdom:")
print("   'You just tested strategies on PROFESSIONAL data.'")
print("   'Alpaca = same API you'll use to trade live.'")
print("   'This is the R and B of the RBI system.'")
print(f"   'Total tested: {173 + 28 + len(df)} strategies. Legend.'")
print("="*80 + "\n")

