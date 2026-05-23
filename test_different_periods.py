"""
🌙 MOON DEV'S TIME PERIOD TESTER
Test strategies on DIFFERENT TIME PERIODS of the SAME data

Moon Dev: "A strategy that works 2004-2013 might fail 2014-2024.
           Test across different market regimes."

Using built-in GOOG data split into periods:
- Bull market period
- Bear market period  
- Full period
- Recent years only
"""

from backtesting import Backtest, Strategy
from backtesting.test import GOOG
import pandas as pd
import time


# ============================================================================
# STRATEGIES (Top 3 from Round 1)
# ============================================================================

class DualMA(Strategy):
    """Best: Sharpe 0.86"""
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
    """Variation: Faster signals"""
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


class DualMA_Slow(Strategy):
    """Variation: Slower, more conservative"""
    fast_ma = 10
    slow_ma = 50
    
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


# ============================================================================
# TIME PERIOD SPLITS
# ============================================================================

# Load full GOOG data
full_data = GOOG.copy()
full_data.index = pd.to_datetime(full_data.index)

# Split into periods
periods = {
    'Full Period (2004-2013)': full_data,
    'Early Bull (2004-2007)': full_data['2004':'2007'],
    'Financial Crisis (2008-2009)': full_data['2008':'2009'],
    'Recovery (2010-2011)': full_data['2010':'2011'],
    'Late Period (2012-2013)': full_data['2012':'2013'],
    'First Half (2004-2008)': full_data['2004':'2008'],
    'Second Half (2009-2013)': full_data['2009':'2013'],
}

strategies = [
    ('DualMA 10/20 (Best)', DualMA),
    ('DualMA 5/20 (Fast)', DualMA_Fast),
    ('DualMA 10/50 (Slow)', DualMA_Slow),
    ('TripleMA 8/30/100', TripleMA),
]

print("\n" + "="*80)
print("🌙 MOON DEV'S TIME PERIOD TESTER")
print("="*80)
print(f"\n📊 Testing {len(strategies)} strategies on {len(periods)} time periods")
print(f"⏱️  Estimated time: 2-3 minutes\n")
print("="*80 + "\n")

# ============================================================================
# RUN ALL TESTS
# ============================================================================

results = []
start_time = time.time()
total_tests = len(strategies) * len(periods)
test_count = 0

for period_name, period_data in periods.items():
    if len(period_data) < 100:
        print(f"⚠️  {period_name}: Not enough data ({len(period_data)} bars), skipping")
        continue
    
    print(f"\n📅 Testing period: {period_name} ({len(period_data)} bars)")
    
    for strategy_name, strategy_class in strategies:
        test_count += 1
        print(f"   [{test_count}/{total_tests}] {strategy_name}...", end=" ")
        
        try:
            bt = Backtest(period_data, strategy_class, cash=10000, commission=.002)
            stats = bt.run()
            
            result = {
                'Period': period_name,
                'Strategy': strategy_name,
                'Bars': len(period_data),
                'Return %': round(stats['Return [%]'], 1),
                'Sharpe': round(stats['Sharpe Ratio'], 2),
                'Win Rate %': round(stats['Win Rate [%]'], 1),
                'Max DD %': round(stats['Max. Drawdown [%]'], 1),
                'Trades': int(stats['# Trades']),
                'Buy & Hold %': round(stats['Buy & Hold Return [%]'], 1)
            }
            results.append(result)
            
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
            print(f"❌ Error: {str(e)[:40]}")

# ============================================================================
# ANALYZE RESULTS
# ============================================================================

print("\n" + "="*80)
print("📊 TIME PERIOD ANALYSIS")
print("="*80 + "\n")

df = pd.DataFrame(results)
df_sorted = df.sort_values('Sharpe', ascending=False)

# Save
from datetime import datetime
filename = f'time_period_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
df_sorted.to_csv(filename, index=False)
print(f"💾 Saved to: {filename}\n")

# ============================================================================
# TOP PERFORMERS
# ============================================================================

print("="*80)
print("🏆 TOP 10 STRATEGY-PERIOD COMBINATIONS")
print("="*80 + "\n")

for i, (_, row) in enumerate(df_sorted.head(10).iterrows(), 1):
    status = "🔥" if row['Sharpe'] >= 1.5 else "✅" if row['Sharpe'] >= 1.0 else "⚠️ "
    print(f"{status} #{i}: {row['Strategy']:<25} | {row['Period']}")
    print(f"     Sharpe: {row['Sharpe']:>5.2f} | Return: {row['Return %']:>7.1f}% | "
          f"Trades: {row['Trades']:>3} | Win: {row['Win Rate %']:>5.1f}%")
    print()

# ============================================================================
# WINNERS
# ============================================================================

winners = df_sorted[df_sorted['Sharpe'] >= 1.0]

print("="*80)
print(f"🎯 WINNERS: {len(winners)} with Sharpe ≥ 1.0")
print("="*80 + "\n")

if len(winners) > 0:
    print("🎊 FOUND WINNERS! These work in specific market conditions:\n")
    
    for _, row in winners.iterrows():
        print(f"✅ {row['Strategy']} in {row['Period']}")
        print(f"   Sharpe: {row['Sharpe']} | Return: {row['Return %']}% | "
              f"Beat B&H by: {row['Return %'] - row['Buy & Hold %']:+.1f}%\n")
else:
    tested = len(df)
    print(f"⚠️  Tested {tested} combinations, no Sharpe ≥1.0 yet.\n")

# ============================================================================
# BEST PERIODS
# ============================================================================

print("="*80)
print("📈 BEST TIME PERIODS (Avg Sharpe)")
print("="*80 + "\n")

period_avg = df.groupby('Period')['Sharpe'].mean().sort_values(ascending=False)

for period, avg_sharpe in period_avg.items():
    status = "✅" if avg_sharpe >= 0.5 else "⚠️ "
    bars = df[df['Period'] == period]['Bars'].iloc[0]
    print(f"{status} {period:<30} Sharpe: {avg_sharpe:>5.2f} ({bars} bars)")

# ============================================================================
# BEST STRATEGIES  
# ============================================================================

print("\n" + "="*80)
print("🎯 BEST STRATEGIES (Avg Sharpe Across All Periods)")
print("="*80 + "\n")

strategy_avg = df.groupby('Strategy')['Sharpe'].mean().sort_values(ascending=False)

for strategy, avg_sharpe in strategy_avg.items():
    status = "✅" if avg_sharpe >= 0.5 else "⚠️ "
    print(f"{status} {strategy:<30} Avg Sharpe: {avg_sharpe:.2f}")

# ============================================================================
# INSIGHTS
# ============================================================================

print("\n" + "="*80)
print("💡 KEY INSIGHTS")
print("="*80 + "\n")

print(f"Total Combinations Tested: {len(df)}")
print(f"Winners (Sharpe ≥1.0): {len(winners)} ({len(winners)/len(df)*100:.1f}%)")
print(f"Good (Sharpe ≥0.5): {len(df[df['Sharpe'] >= 0.5])} ({len(df[df['Sharpe'] >= 0.5])/len(df)*100:.1f}%)")
print()
print(f"Best Sharpe: {df['Sharpe'].max():.2f}")
print(f"Average Sharpe: {df['Sharpe'].mean():.2f}")
print(f"Worst Sharpe: {df['Sharpe'].min():.2f}")
print()
print(f"Time: {(time.time() - start_time)/60:.1f} min")
print()

print("="*80)
print("🌙 Moon Dev's Lesson:")
print("   'Same strategy, different periods = different results.'")
print("   'A strategy that works in bull markets fails in bear markets.'")
print("   'THIS is why you need multiple strategies for different conditions.'")
print(f"   'Total tested today: {173 + len(df)} strategies. Legend status.'")
print("="*80 + "\n")

