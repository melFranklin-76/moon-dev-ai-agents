"""
🌙 MOON DEV'S MULTI-MARKET TESTER
Test the SAME strategies on DIFFERENT market conditions

Moon Dev: "A strategy that works on GOOG might fail on crypto.
           Test EVERYTHING on multiple markets."

This tests your top strategies on:
1. Crypto (BTC) - High volatility
2. Tech stocks (TSLA) - Momentum
3. Different time periods
"""

from backtesting import Backtest, Strategy
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time


# ============================================================================
# STRATEGIES (Top performers from Round 1)
# ============================================================================

class DualMA(Strategy):
    """Best from Round 1: Sharpe 0.86"""
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


class TripleMA(Strategy):
    """2nd Best: Sharpe 0.79"""
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
    """7th Best: Sharpe 0.74"""
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
# DATA SOURCES
# ============================================================================

def get_crypto_data(symbol='BTC-USD', period='2y'):
    """Get Bitcoin data (high volatility)"""
    print(f"   Downloading {symbol} crypto data...")
    df = yf.download(symbol, period=period, progress=False)
    df.columns = [col.lower() if isinstance(col, str) else col[0].lower() 
                  for col in df.columns]
    df = df.rename(columns={
        'adj close': 'close',
        'adjclose': 'close'
    })
    df = df[['open', 'high', 'low', 'close', 'volume']].copy()
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    return df.dropna()


def get_stock_data(symbol='TSLA', period='2y'):
    """Get stock data"""
    print(f"   Downloading {symbol} stock data...")
    df = yf.download(symbol, period=period, progress=False)
    df.columns = [col.lower() if isinstance(col, str) else col[0].lower() 
                  for col in df.columns]
    df = df.rename(columns={
        'adj close': 'close',
        'adjclose': 'close'
    })
    df = df[['open', 'high', 'low', 'close', 'volume']].copy()
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    return df.dropna()


# ============================================================================
# TEST MATRIX
# ============================================================================

test_datasets = [
    ('BTC-USD (Crypto)', get_crypto_data, {'symbol': 'BTC-USD', 'period': '2y'}),
    ('ETH-USD (Crypto)', get_crypto_data, {'symbol': 'ETH-USD', 'period': '2y'}),
    ('TSLA (Tech Stock)', get_stock_data, {'symbol': 'TSLA', 'period': '2y'}),
    ('GME (Meme Stock)', get_stock_data, {'symbol': 'GME', 'period': '2y'}),
    ('SPY (S&P 500)', get_stock_data, {'symbol': 'SPY', 'period': '2y'}),
    ('NVDA (Tech)', get_stock_data, {'symbol': 'NVDA', 'period': '2y'}),
]

strategies = [
    ('DualMA 10/20', DualMA),
    ('TripleMA 8/30/100', TripleMA),
    ('Momentum Breakout', MomentumBreakout),
]

print("\n" + "="*80)
print("🌙 MOON DEV'S MULTI-MARKET TESTER")
print("="*80)
print(f"\n📊 Testing {len(strategies)} strategies on {len(test_datasets)} markets")
print(f"⏱️  Estimated time: {len(strategies) * len(test_datasets) * 2 // 60} minutes\n")
print("="*80 + "\n")

# ============================================================================
# RUN ALL TESTS
# ============================================================================

results = []
start_time = time.time()
test_count = 0
total_tests = len(strategies) * len(test_datasets)

for dataset_name, get_data_func, params in test_datasets:
    print(f"\n📈 Testing on {dataset_name}...")
    
    try:
        # Get data
        data = get_data_func(**params)
        
        if len(data) < 200:
            print(f"   ⚠️  Not enough data ({len(data)} bars), skipping...")
            continue
        
        print(f"   ✅ Loaded {len(data)} bars")
        
        # Test each strategy
        for strategy_name, strategy_class in strategies:
            test_count += 1
            print(f"   [{test_count}/{total_tests}] Testing {strategy_name}...", end=" ")
            
            try:
                bt = Backtest(data, strategy_class, cash=10000, commission=.002)
                stats = bt.run()
                
                result = {
                    'Market': dataset_name,
                    'Strategy': strategy_name,
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
                    print(f"🔥 EXCELLENT! Sharpe: {sharpe}")
                elif sharpe >= 1.0:
                    print(f"✅ WINNER! Sharpe: {sharpe}")
                elif sharpe >= 0.5:
                    print(f"⚠️  OK. Sharpe: {sharpe}")
                else:
                    print(f"❌ Bad. Sharpe: {sharpe}")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}")
                
    except Exception as e:
        print(f"   ❌ Failed to load data: {str(e)[:50]}")

elapsed = time.time() - start_time

# ============================================================================
# ANALYZE RESULTS
# ============================================================================

print("\n" + "="*80)
print("📊 MULTI-MARKET RESULTS")
print("="*80 + "\n")

df = pd.DataFrame(results)

if len(df) == 0:
    print("❌ No results to analyze. Check data sources.\n")
    exit()

df_sorted = df.sort_values('Sharpe', ascending=False)

# Save results
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f'multi_market_results_{timestamp}.csv'
df_sorted.to_csv(filename, index=False)
print(f"💾 Saved to: {filename}\n")

# ============================================================================
# TOP PERFORMERS
# ============================================================================

print("="*80)
print("🏆 TOP 10 STRATEGY-MARKET COMBINATIONS")
print("="*80 + "\n")

for i, (_, row) in enumerate(df_sorted.head(10).iterrows(), 1):
    status = "🔥" if row['Sharpe'] >= 1.5 else "✅" if row['Sharpe'] >= 1.0 else "⚠️ " if row['Sharpe'] >= 0.5 else "❌"
    print(f"{status} #{i:2d} | {row['Market']:<20} | {row['Strategy']:<20}")
    print(f"       Sharpe: {row['Sharpe']:>5.2f} | Return: {row['Return %']:>7.1f}% | "
          f"Buy&Hold: {row['Buy & Hold %']:>7.1f}% | Trades: {row['Trades']:>3}")
    print()

# ============================================================================
# WINNERS
# ============================================================================

winners = df_sorted[df_sorted['Sharpe'] >= 1.0]

print("="*80)
print(f"🎯 WINNERS: {len(winners)} combinations with Sharpe ≥ 1.0")
print("="*80 + "\n")

if len(winners) > 0:
    print("🎊 CONGRATULATIONS! You found winning strategy-market combinations!\n")
    
    for _, row in winners.iterrows():
        print(f"✅ {row['Strategy']} on {row['Market']}")
        print(f"   Sharpe: {row['Sharpe']} | Return: {row['Return %']}% | "
              f"Win Rate: {row['Win Rate %']}%")
        print(f"   Beat Buy & Hold: {row['Return %'] - row['Buy & Hold %']:+.1f}%\n")
    
    print("📋 NEXT STEPS:")
    print("   1. Forward test these for 2-3 months (paper trading)")
    print("   2. Start with $10-20 per trade")
    print("   3. Track if live results match backtests")
    print("   4. Scale slowly if profitable\n")
else:
    print("⚠️  No Sharpe ≥1.0 found yet.")
    print(f"   But you tested {len(df)} strategy-market combinations!")
    print("   That's more than most traders test in a YEAR.\n")

# ============================================================================
# BEST MARKETS
# ============================================================================

print("="*80)
print("📈 BEST MARKETS (Average Sharpe)")
print("="*80 + "\n")

market_avg = df.groupby('Market')['Sharpe'].mean().sort_values(ascending=False)

for market, avg_sharpe in market_avg.items():
    status = "🔥" if avg_sharpe >= 1.0 else "✅" if avg_sharpe >= 0.5 else "⚠️ "
    print(f"{status} {market:<25} Avg Sharpe: {avg_sharpe:.2f}")

print()

# ============================================================================
# BEST STRATEGIES
# ============================================================================

print("="*80)
print("🎯 BEST STRATEGIES (Average Sharpe)")
print("="*80 + "\n")

strategy_avg = df.groupby('Strategy')['Sharpe'].mean().sort_values(ascending=False)

for strategy, avg_sharpe in strategy_avg.items():
    status = "🔥" if avg_sharpe >= 1.0 else "✅" if avg_sharpe >= 0.5 else "⚠️ "
    print(f"{status} {strategy:<25} Avg Sharpe: {avg_sharpe:.2f}")

print()

# ============================================================================
# SUMMARY
# ============================================================================

print("="*80)
print("📊 OVERALL STATISTICS")
print("="*80 + "\n")

print(f"Total Tests: {len(df)}")
print(f"Winners (Sharpe ≥1.0): {len(winners)} ({len(winners)/len(df)*100:.1f}%)")
print(f"Good (Sharpe ≥0.5): {len(df[df['Sharpe'] >= 0.5])} ({len(df[df['Sharpe'] >= 0.5])/len(df)*100:.1f}%)")
print()
print(f"Average Sharpe: {df['Sharpe'].mean():.2f}")
print(f"Best Sharpe: {df['Sharpe'].max():.2f}")
print(f"Average Return: {df['Return %'].mean():.1f}%")
print(f"Best Return: {df['Return %'].max():.1f}%")
print()
print(f"Total Time: {elapsed/60:.1f} minutes")
print()

print("="*80)
print("🌙 Moon Dev's Wisdom:")
print("   'Different markets = different results.'")
print("   'A strategy that works on crypto might fail on stocks.'")
print("   'Test EVERYTHING on multiple markets.'")
print(f"   'You just tested {len(df)} combinations. That's how you find edge.'")
print("="*80 + "\n")

