"""
🌙 Quick Test - 100 Strategies (5 min warmup)
Test the system works before running 1000
"""

from backtesting import Backtest, Strategy
from backtesting.test import GOOG
import pandas as pd
import time

class DualMA(Strategy):
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

# Test 100 MA combinations
params = [
    (fast, slow)
    for fast in range(5, 26, 5)  # 5, 10, 15, 20, 25
    for slow in range(20, 101, 10)  # 20, 30, 40, ..., 100
    if fast < slow
]

print(f"\n🌙 Quick Test: {len(params)} strategies (~5 min)\n")

results = []
start = time.time()

for i, (fast, slow) in enumerate(params, 1):
    DualMA.fast_ma = fast
    DualMA.slow_ma = slow
    
    if i % 10 == 0:
        print(f"[{i}/{len(params)}] {i/len(params)*100:.0f}%...")
    
    try:
        bt = Backtest(GOOG, DualMA, cash=10000, commission=.002)
        stats = bt.run()
        
        results.append({
            'Fast': fast,
            'Slow': slow,
            'Sharpe': round(stats['Sharpe Ratio'], 2),
            'Return %': round(stats['Return [%]'], 1),
            'Trades': int(stats['# Trades'])
        })
    except:
        pass

df = pd.DataFrame(results).sort_values('Sharpe', ascending=False)

print(f"\n✅ Done in {(time.time()-start)/60:.1f} min!\n")
print("🏆 TOP 10:\n")

for i, (_, row) in enumerate(df.head(10).iterrows(), 1):
    status = "🔥" if row['Sharpe'] >= 1.5 else "✅" if row['Sharpe'] >= 1.0 else "⚠️ "
    print(f"{status} #{i}: SMA {row['Fast']}/{row['Slow']} | "
          f"Sharpe: {row['Sharpe']} | Return: {row['Return %']}%")

winners = df[df['Sharpe'] >= 1.0]
print(f"\n🎯 Winners (Sharpe ≥1.0): {len(winners)}/{len(df)}\n")

if len(winners) > 0:
    print("✅ FOUND WINNERS! Ready for the full 1000 test.\n")
else:
    print("⚠️  No winners in MA strategies. Will test other indicators in full run.\n")

