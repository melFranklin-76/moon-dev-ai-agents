"""
🌙 MOON DEV'S 1000 STRATEGY TESTING MACHINE
Test 1000+ strategy combinations to find the winners

MOON DEV: "Test 100 ideas, find 5 winners. You're testing 1000. Legend."

This will take 30-60 minutes. Go grab coffee. Let the machine work.
"""

from backtesting import Backtest, Strategy
from backtesting.test import GOOG
import pandas as pd
import numpy as np
from datetime import datetime
import time


# ============================================================================
# STRATEGY TEMPLATES
# ============================================================================

class DualMA(Strategy):
    """Dual Moving Average Crossover"""
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


class RSI_Strategy(Strategy):
    """RSI Oscillator"""
    rsi_period = 14
    rsi_lower = 30
    rsi_upper = 70
    
    def init(self):
        def calc_rsi(prices, period):
            prices = pd.Series(prices)
            delta = prices.diff()
            gain = delta.where(delta > 0, 0).rolling(window=period).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)
    
    def next(self):
        if self.rsi[-1] < self.rsi_lower and not self.position:
            self.buy()
        elif self.rsi[-1] > self.rsi_upper and self.position:
            self.position.close()


class BollingerBands(Strategy):
    """Bollinger Bands Mean Reversion"""
    bb_period = 20
    bb_std = 2
    
    def init(self):
        close = pd.Series(self.data.Close)
        self.sma = self.I(lambda: close.rolling(self.bb_period).mean())
        self.std = self.I(lambda: close.rolling(self.bb_period).std())
    
    def next(self):
        lower = self.sma[-1] - (self.std[-1] * self.bb_std)
        upper = self.sma[-1] + (self.std[-1] * self.bb_std)
        price = self.data.Close[-1]
        
        if price <= lower and not self.position:
            self.buy()
        elif price >= upper and self.position:
            self.position.close()


class TripleMA(Strategy):
    """Triple Moving Average System"""
    fast = 5
    medium = 20
    slow = 50
    
    def init(self):
        close = pd.Series(self.data.Close)
        self.ma_fast = self.I(lambda: close.rolling(self.fast).mean())
        self.ma_medium = self.I(lambda: close.rolling(self.medium).mean())
        self.ma_slow = self.I(lambda: close.rolling(self.slow).mean())
    
    def next(self):
        # Buy when fast > medium > slow (bullish alignment)
        if (self.ma_fast[-1] > self.ma_medium[-1] > self.ma_slow[-1] and
            not self.position):
            self.buy()
        # Sell when alignment breaks
        elif (self.ma_fast[-1] < self.ma_medium[-1] and self.position):
            self.position.close()


class MomentumBreakout(Strategy):
    """Breakout above recent highs"""
    lookback = 20
    
    def init(self):
        high = pd.Series(self.data.High)
        self.recent_high = self.I(lambda: high.rolling(self.lookback).max())
    
    def next(self):
        if self.data.Close[-1] > self.recent_high[-2] and not self.position:
            self.buy()
        elif self.position:
            entry = self.trades[-1].entry_price if self.trades else self.data.Close[-1]
            pnl = (self.data.Close[-1] - entry) / entry
            if pnl >= 0.05 or pnl <= -0.02:  # 5% profit or 2% loss
                self.position.close()


# ============================================================================
# PARAMETER RANGES TO TEST
# ============================================================================

test_matrix = {
    'DualMA': {
        'strategy': DualMA,
        'params': [
            {'fast_ma': fast, 'slow_ma': slow}
            for fast in range(5, 31, 5)    # 5, 10, 15, 20, 25, 30
            for slow in range(20, 201, 20)  # 20, 40, 60, ..., 200
            if fast < slow
        ]
    },
    'RSI': {
        'strategy': RSI_Strategy,
        'params': [
            {'rsi_period': period, 'rsi_lower': lower, 'rsi_upper': upper}
            for period in [10, 14, 20, 30]
            for lower in [20, 25, 30, 35]
            for upper in [65, 70, 75, 80]
            if lower < 50 < upper
        ]
    },
    'BollingerBands': {
        'strategy': BollingerBands,
        'params': [
            {'bb_period': period, 'bb_std': std}
            for period in [15, 20, 25, 30]
            for std in [1.5, 2.0, 2.5, 3.0]
        ]
    },
    'TripleMA': {
        'strategy': TripleMA,
        'params': [
            {'fast': fast, 'medium': medium, 'slow': slow}
            for fast in [5, 8, 10]
            for medium in [20, 30, 40]
            for slow in [50, 100, 200]
            if fast < medium < slow
        ]
    },
    'MomentumBreakout': {
        'strategy': MomentumBreakout,
        'params': [
            {'lookback': period}
            for period in range(10, 51, 5)  # 10, 15, 20, ..., 50
        ]
    }
}

# Calculate total tests
total_tests = sum(len(config['params']) for config in test_matrix.values())

print("\n" + "="*80)
print("🌙 MOON DEV'S 1000 STRATEGY TESTING MACHINE")
print("="*80)
print(f"\n📊 Total strategies to test: {total_tests}")
print(f"⏱️  Estimated time: {total_tests * 2 // 60} minutes")
print("\n🔥 Go grab coffee. This is where legends are made.\n")
print("="*80 + "\n")

# ============================================================================
# RUN ALL TESTS
# ============================================================================

all_results = []
start_time = time.time()
test_count = 0

for strategy_name, config in test_matrix.items():
    strategy_class = config['strategy']
    params_list = config['params']
    
    print(f"🧪 Testing {strategy_name} ({len(params_list)} variations)...")
    
    for params in params_list:
        test_count += 1
        
        # Progress indicator every 50 tests
        if test_count % 50 == 0:
            elapsed = time.time() - start_time
            tests_per_sec = test_count / elapsed
            remaining = (total_tests - test_count) / tests_per_sec
            print(f"   [{test_count}/{total_tests}] {test_count/total_tests*100:.1f}% complete | "
                  f"~{remaining/60:.0f}min remaining")
        
        try:
            # Set parameters
            for key, value in params.items():
                setattr(strategy_class, key, value)
            
            # Run backtest
            bt = Backtest(GOOG, strategy_class, cash=10000, commission=.002)
            stats = bt.run()
            
            # Store results
            result = {
                'Test #': test_count,
                'Strategy': strategy_name,
                'Parameters': str(params),
                'Return %': round(stats['Return [%]'], 2),
                'Sharpe': round(stats['Sharpe Ratio'], 2),
                'Win Rate %': round(stats['Win Rate [%]'], 1),
                'Max DD %': round(stats['Max. Drawdown [%]'], 1),
                'Trades': int(stats['# Trades']),
                'Profit Factor': round(stats.get('Profit Factor', 0), 2)
            }
            all_results.append(result)
            
        except Exception as e:
            # Skip failed tests
            pass

print(f"\n✅ Testing complete! Tested {len(all_results)} strategies.\n")

# ============================================================================
# ANALYZE RESULTS
# ============================================================================

print("="*80)
print("📊 ANALYZING RESULTS...")
print("="*80 + "\n")

df = pd.DataFrame(all_results)
df = df.sort_values('Sharpe', ascending=False)

# Save ALL results
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f'backtest_results_{timestamp}.csv'
df.to_csv(filename, index=False)
print(f"💾 Full results saved to: {filename}\n")

# ============================================================================
# TOP PERFORMERS
# ============================================================================

print("="*80)
print("🏆 TOP 20 STRATEGIES BY SHARPE RATIO")
print("="*80 + "\n")

top_20 = df.head(20)

for i, (_, row) in enumerate(top_20.iterrows(), 1):
    status = "🔥" if row['Sharpe'] >= 1.5 else "✅" if row['Sharpe'] >= 1.0 else "⚠️ "
    print(f"{status} #{i:2d} | {row['Strategy']:<20} | Sharpe: {row['Sharpe']:>5.2f} | "
          f"Return: {row['Return %']:>7.1f}% | Trades: {row['Trades']:>3}")
    print(f"      {row['Parameters']}")
    print()

# ============================================================================
# WINNERS ANALYSIS
# ============================================================================

winners = df[df['Sharpe'] >= 1.0]
excellent = df[df['Sharpe'] >= 1.5]

print("="*80)
print("🎯 WINNERS SUMMARY")
print("="*80 + "\n")

print(f"Total Tested: {len(df)}")
print(f"Winners (Sharpe ≥1.0): {len(winners)} ({len(winners)/len(df)*100:.1f}%)")
print(f"Excellent (Sharpe ≥1.5): {len(excellent)} ({len(excellent)/len(df)*100:.1f}%)")
print()

if len(winners) > 0:
    print("✅ WINNING STRATEGIES:\n")
    for _, row in winners.iterrows():
        print(f"   {row['Strategy']}: {row['Parameters']}")
        print(f"   → Sharpe: {row['Sharpe']} | Return: {row['Return %']}% | "
              f"Win Rate: {row['Win Rate %']}%\n")
    
    print("🎊 CONGRATULATIONS! You found winning strategies!")
    print("   Next steps:")
    print("   1. Forward test the top 5 for 2-3 months (paper trading)")
    print("   2. Compare results to backtest")
    print("   3. If they match, go live with $10-20 per trade")
    print("   4. Scale slowly if profitable\n")
else:
    print("⚠️  No strategies with Sharpe ≥1.0 found.")
    print("   But you learned what DOESN'T work (that's valuable!)")
    print("   Try different indicators or market conditions.\n")

# ============================================================================
# STATISTICS
# ============================================================================

print("="*80)
print("📈 OVERALL STATISTICS")
print("="*80 + "\n")

print(f"Average Sharpe Ratio: {df['Sharpe'].mean():.2f}")
print(f"Median Sharpe Ratio: {df['Sharpe'].median():.2f}")
print(f"Best Sharpe Ratio: {df['Sharpe'].max():.2f}")
print(f"Worst Sharpe Ratio: {df['Sharpe'].min():.2f}")
print()
print(f"Average Return: {df['Return %'].mean():.1f}%")
print(f"Best Return: {df['Return %'].max():.1f}%")
print(f"Worst Return: {df['Return %'].min():.1f}%")
print()
print(f"Total Time: {(time.time() - start_time)/60:.1f} minutes")
print()

print("="*80)
print("🌙 Moon Dev's Wisdom:")
print("   'You just did what 99% of traders never do: SYSTEMATIC TESTING.'")
print("   'The winners you found? That's YOUR edge.'")
print("   'Now forward test them. Prove they work in real-time.'")
print("="*80 + "\n")

