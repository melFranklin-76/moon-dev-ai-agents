"""
🌙 Moon Dev's Batch Backtesting System
Test multiple strategies automatically and find the winners

MOON DEV'S RULE: Test 100 ideas, find 5 winners (Sharpe >1.0)
"""

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG
import pandas as pd
import time


class TestStrategy(Strategy):
    """Template strategy - we'll change parameters"""
    fast_ma = 10
    slow_ma = 20
    
    def init(self):
        close = self.data.Close
        self.ma_fast = self.I(lambda x: pd.Series(x).rolling(self.fast_ma).mean(), close)
        self.ma_slow = self.I(lambda x: pd.Series(x).rolling(self.slow_ma).mean(), close)
    
    def next(self):
        if crossover(self.ma_fast, self.ma_slow):
            self.buy()
        elif crossover(self.ma_slow, self.ma_fast):
            self.position.close()


def run_single_test(fast, slow, silent=True):
    """Run a single backtest with given parameters"""
    bt = Backtest(GOOG, TestStrategy, cash=10000, commission=.002)
    stats = bt.optimize(
        fast_ma=[fast],
        slow_ma=[slow],
        maximize='Sharpe Ratio'
    )
    return stats


# ============================================================================
# TEST SUITE - Add your ideas here!
# ============================================================================

test_cases = [
    # Format: (fast_ma, slow_ma, description)
    (10, 20, "Original - Fast momentum"),
    (5, 20, "Very fast entry"),
    (10, 30, "Medium trend"),
    (10, 50, "Long trend"),
    (20, 50, "Slower entry"),
    (5, 10, "Ultra fast scalp"),
    (20, 200, "Long term trend"),
    (50, 200, "Position trading"),
    (10, 100, "Fast + long filter"),
    (15, 45, "3:1 ratio"),
]


# ============================================================================
# RUN ALL TESTS
# ============================================================================

print("\n" + "="*80)
print("🌙 MOON DEV'S BATCH BACKTEST - FINDING WINNERS")
print("="*80 + "\n")
print("Testing {} strategies...\n".format(len(test_cases)))

results = []

for i, (fast, slow, desc) in enumerate(test_cases, 1):
    print(f"[{i}/{len(test_cases)}] Testing: SMA {fast}/{slow} - {desc}...", end=" ")
    
    try:
        stats = run_single_test(fast, slow)
        
        result = {
            'Strategy': desc,
            'Fast MA': fast,
            'Slow MA': slow,
            'Return %': round(stats['Return [%]'], 2),
            'Sharpe': round(stats['Sharpe Ratio'], 2),
            'Win Rate %': round(stats['Win Rate [%]'], 2),
            'Max DD %': round(stats['Max. Drawdown [%]'], 2),
            '# Trades': stats['# Trades']
        }
        
        results.append(result)
        
        # Quick status
        sharpe = result['Sharpe']
        if sharpe >= 1.5:
            print("🔥 WINNER!")
        elif sharpe >= 1.0:
            print("✅ Good")
        elif sharpe >= 0.5:
            print("⚠️  Meh")
        else:
            print("❌ Bad")
            
    except Exception as e:
        print(f"❌ Error: {e}")

# ============================================================================
# RESULTS SUMMARY
# ============================================================================

print("\n" + "="*80)
print("📊 RESULTS RANKED BY SHARPE RATIO")
print("="*80 + "\n")

# Convert to DataFrame and sort
df = pd.DataFrame(results)
df = df.sort_values('Sharpe', ascending=False)

# Print results
for idx, row in df.iterrows():
    sharpe = row['Sharpe']
    
    # Color coding
    if sharpe >= 1.5:
        status = "🔥 EXCELLENT"
    elif sharpe >= 1.0:
        status = "✅ WINNER"
    elif sharpe >= 0.5:
        status = "⚠️  OK"
    else:
        status = "❌ SKIP"
    
    print(f"{status} | Sharpe: {sharpe:>5.2f} | Return: {row['Return %']:>7.1f}% | "
          f"Win: {row['Win Rate %']:>5.1f}% | Trades: {row['# Trades']:>3} | "
          f"SMA {row['Fast MA']}/{row['Slow MA']} - {row['Strategy']}")

# ============================================================================
# WINNERS LIST
# ============================================================================

winners = df[df['Sharpe'] >= 1.0]

print("\n" + "="*80)
print(f"🎯 FOUND {len(winners)} WINNER(S) (Sharpe ≥ 1.0)")
print("="*80 + "\n")

if len(winners) > 0:
    for idx, row in winners.iterrows():
        print(f"✅ {row['Strategy']}")
        print(f"   SMA {row['Fast MA']}/{row['Slow MA']}")
        print(f"   Sharpe: {row['Sharpe']} | Return: {row['Return %']}% | Win Rate: {row['Win Rate %']}%")
        print(f"   Max Drawdown: {row['Max DD %']}% | Trades: {row['# Trades']}")
        print()
    
    print("🎊 Congrats! Forward test these for 2-3 months before going live.\n")
else:
    print("😅 No winners yet. Time to research more strategies!")
    print("   - Try different indicators (RSI, VWAP, etc.)")
    print("   - Test different time periods")
    print("   - Combine multiple signals")
    print("   - Check out Ross Cameron's videos for ideas\n")

# ============================================================================
# SAVE RESULTS
# ============================================================================

df.to_csv('backtest_results.csv', index=False)
print(f"💾 Results saved to: backtest_results.csv\n")

print("="*80)
print("🌙 Moon Dev's Reminder:")
print("   'Test 100 ideas. Find 5 winners. That's your edge.'")
print("="*80 + "\n")

