"""
🌙 Ross Cameron Style Strategies
Test momentum + VWAP + RSI combinations
"""

from backtesting import Backtest, Strategy
from backtesting.test import GOOG
import pandas as pd
import pandas_ta as ta


class RSI_Strategy(Strategy):
    """Buy oversold, sell overbought"""
    rsi_period = 14
    rsi_lower = 30
    rsi_upper = 70
    
    def init(self):
        self.rsi = self.I(ta.rsi, pd.Series(self.data.Close), length=self.rsi_period)
    
    def next(self):
        if self.rsi < self.rsi_lower:
            if not self.position:
                self.buy()
        elif self.rsi > self.rsi_upper:
            if self.position:
                self.position.close()


class VWAP_Strategy(Strategy):
    """Buy below VWAP, sell above"""
    
    def init(self):
        # Calculate VWAP
        df = pd.DataFrame({
            'high': self.data.High,
            'low': self.data.Low,
            'close': self.data.Close,
            'volume': self.data.Volume
        })
        self.vwap = self.I(ta.vwap, df['high'], df['low'], df['close'], df['volume'])
    
    def next(self):
        price = self.data.Close[-1]
        if price < self.vwap[-1] * 0.98:  # 2% below VWAP
            if not self.position:
                self.buy()
        elif price > self.vwap[-1]:  # Back above VWAP
            if self.position:
                self.position.close()


class RSI_MA_Combo(Strategy):
    """RSI + Moving Average combo"""
    
    def init(self):
        self.rsi = self.I(ta.rsi, pd.Series(self.data.Close), length=14)
        self.ma = self.I(ta.sma, pd.Series(self.data.Close), length=20)
    
    def next(self):
        # Buy when RSI oversold AND price above MA
        if self.rsi < 30 and self.data.Close[-1] > self.ma[-1]:
            if not self.position:
                self.buy()
        # Sell when RSI overbought OR price below MA
        elif self.rsi > 70 or self.data.Close[-1] < self.ma[-1]:
            if self.position:
                self.position.close()


# Test all strategies
strategies_to_test = [
    ("RSI Only", RSI_Strategy),
    ("VWAP Mean Reversion", VWAP_Strategy),
    ("RSI + MA Combo", RSI_MA_Combo),
]

print("\n" + "="*70)
print("🔍 TESTING ROSS CAMERON STYLE STRATEGIES")
print("="*70 + "\n")

results = []

for name, strategy_class in strategies_to_test:
    print(f"Testing: {name}...")
    
    try:
        bt = Backtest(GOOG, strategy_class, cash=10000, commission=.002)
        stats = bt.run()
        
        result = {
            'Strategy': name,
            'Return %': round(stats['Return [%]'], 1),
            'Sharpe': round(stats['Sharpe Ratio'], 2),
            'Win Rate %': round(stats['Win Rate [%]'], 1),
            'Max DD %': round(stats['Max. Drawdown [%]'], 1),
            'Trades': int(stats['# Trades'])
        }
        results.append(result)
        
        if result['Sharpe'] >= 1.0:
            print(f"   ✅ WINNER! Sharpe: {result['Sharpe']}\n")
        else:
            print(f"   ⚠️  Sharpe: {result['Sharpe']} (need ≥1.0)\n")
    
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

# Results
print("="*70)
print("📊 RESULTS")
print("="*70 + "\n")

df = pd.DataFrame(results).sort_values('Sharpe', ascending=False)

for _, row in df.iterrows():
    status = "✅" if row['Sharpe'] >= 1.0 else "⚠️ " if row['Sharpe'] >= 0.5 else "❌"
    print(f"{status} {row['Strategy']:<25} | Sharpe: {row['Sharpe']:>5.2f} | "
          f"Return: {row['Return %']:>6.1f}% | Trades: {row['Trades']:>3}")

winners = df[df['Sharpe'] >= 1.0]

print(f"\n🎯 Found {len(winners)} winner(s)!\n")

if len(winners) > 0:
    print("✅ CONGRATS! You found a strategy with Sharpe >1.0!")
    print("   Next: Forward test for 2-3 months before going live.\n")
else:
    print("Keep testing! You're at ~10/100 ideas tested.")
    print("Moon Dev found his first winner at idea #37.\n")

print("="*70)

