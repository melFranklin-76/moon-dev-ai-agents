"""
🌙 Simple Batch Backtest - Test Multiple Strategies
Find winners with Sharpe Ratio > 1.0
"""

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG
import pandas as pd


class SMAStrategy(Strategy):
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


# Test combinations
strategies = [
    (10, 20, "Fast momentum (your first test)"),
    (5, 20, "Very fast entry"),
    (10, 30, "Medium trend"),
    (10, 50, "Long trend following"),
    (20, 50, "Slower entry"),
    (15, 45, "3:1 ratio"),
    (20, 100, "Position trading"),
]

print("\n" + "="*70)
print("🌙 TESTING {} STRATEGIES".format(len(strategies)))
print("="*70 + "\n")

results = []

for i, (fast, slow, desc) in enumerate(strategies, 1):
    print(f"[{i}/{len(strategies)}] SMA {fast}/{slow} - {desc}...")
    
    # Temporarily set class variables
    SMAStrategy.fast_ma = fast
    SMAStrategy.slow_ma = slow
    
    bt = Backtest(GOOG, SMAStrategy, cash=10000, commission=.002)
    stats = bt.run()
    
    result = {
        'Fast': fast,
        'Slow': slow,
        'Description': desc,
        'Return %': round(stats['Return [%]'], 1),
        'Sharpe': round(stats['Sharpe Ratio'], 2),
        'Win Rate %': round(stats['Win Rate [%]'], 1),
        'Max DD %': round(stats['Max. Drawdown [%]'], 1),
        'Trades': int(stats['# Trades'])
    }
    results.append(result)
    
    # Quick feedback
    if result['Sharpe'] >= 1.5:
        print(f"   🔥 EXCELLENT! Sharpe: {result['Sharpe']}, Return: {result['Return %']}%\n")
    elif result['Sharpe'] >= 1.0:
        print(f"   ✅ WINNER! Sharpe: {result['Sharpe']}, Return: {result['Return %']}%\n")
    elif result['Sharpe'] >= 0.5:
        print(f"   ⚠️  OK. Sharpe: {result['Sharpe']}, Return: {result['Return %']}%\n")
    else:
        print(f"   ❌ Bad. Sharpe: {result['Sharpe']}, Return: {result['Return %']}%\n")

# Show results
print("="*70)
print("📊 FINAL RESULTS (Sorted by Sharpe Ratio)")
print("="*70 + "\n")

df = pd.DataFrame(results).sort_values('Sharpe', ascending=False)

for _, row in df.iterrows():
    status = "🔥" if row['Sharpe'] >= 1.5 else "✅" if row['Sharpe'] >= 1.0 else "⚠️ " if row['Sharpe'] >= 0.5 else "❌"
    print(f"{status} SMA {row['Fast']:>2}/{row['Slow']:<3} | Sharpe: {row['Sharpe']:>5.2f} | "
          f"Return: {row['Return %']:>6.1f}% | Win: {row['Win Rate %']:>4.1f}% | "
          f"DD: {row['Max DD %']:>5.1f}% | Trades: {row['Trades']:>3}")

# Winners
winners = df[df['Sharpe'] >= 1.0]

print("\n" + "="*70)
print(f"🎯 WINNERS: {len(winners)} strategies with Sharpe ≥ 1.0")
print("="*70 + "\n")

if len(winners) > 0:
    for _, row in winners.iterrows():
        print(f"✅ SMA {row['Fast']}/{row['Slow']} - {row['Description']}")
        print(f"   Sharpe: {row['Sharpe']} | Return: {row['Return %']}% | Win Rate: {row['Win Rate %']}%\n")
    print("🎊 Next step: Forward test these for 2-3 months!\n")
else:
    print("No winners yet. Moon Dev says this is NORMAL.")
    print("He tests 100 ideas to find 5 winners. Keep going!\n")

df.to_csv('results.csv', index=False)
print("💾 Saved to results.csv\n")

print("="*70)
print("🌙 'Test 100 ideas. Find 5 winners.' - Moon Dev")
print("="*70 + "\n")

