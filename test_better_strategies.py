"""
🌙 Better Strategies Using Just Pandas (No pandas_ta needed!)
Ross Cameron momentum + technical indicators
"""

from backtesting import Backtest, Strategy
from backtesting.test import GOOG
import pandas as pd
import numpy as np


class RSI_Strategy(Strategy):
    """RSI oscillator strategy - buy oversold, sell overbought"""
    rsi_period = 14
    rsi_lower = 30
    rsi_upper = 70
    
    def init(self):
        # Calculate RSI manually
        def calculate_rsi(prices, period=14):
            prices = pd.Series(prices)
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        
        self.rsi = self.I(calculate_rsi, self.data.Close, self.rsi_period)
    
    def next(self):
        if self.rsi[-1] < self.rsi_lower:
            if not self.position:
                self.buy()
        elif self.rsi[-1] > self.rsi_upper:
            if self.position:
                self.position.close()


class BollingerBands_Strategy(Strategy):
    """Buy at lower band, sell at upper band"""
    bb_period = 20
    bb_std = 2
    
    def init(self):
        def calculate_bb(prices, period=20, std_dev=2):
            prices = pd.Series(prices)
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            upper = sma + (std * std_dev)
            lower = sma - (std * std_dev)
            return lower, sma, upper
        
        lower, middle, upper = calculate_bb(self.data.Close, self.bb_period, self.bb_std)
        self.lower_band = self.I(lambda: lower)
        self.middle_band = self.I(lambda: middle)
        self.upper_band = self.I(lambda: upper)
    
    def next(self):
        price = self.data.Close[-1]
        # Buy when price touches lower band
        if price <= self.lower_band[-1]:
            if not self.position:
                self.buy()
        # Sell when price touches upper band
        elif price >= self.upper_band[-1]:
            if self.position:
                self.position.close()


class MomentumBreakout_Strategy(Strategy):
    """Ross Cameron style - buy breakouts above recent high"""
    lookback = 20
    
    def init(self):
        def rolling_high(prices, period=20):
            return pd.Series(prices).rolling(window=period).max()
        
        self.recent_high = self.I(rolling_high, self.data.High, self.lookback)
    
    def next(self):
        # Breakout: price breaks above recent high
        if self.data.Close[-1] > self.recent_high[-2]:  # Previous recent high
            if not self.position:
                self.buy()
        # Exit on 5% profit or 2% loss
        elif self.position:
            entry_price = self.position.entry_price
            current_price = self.data.Close[-1]
            profit_pct = (current_price - entry_price) / entry_price
            
            if profit_pct >= 0.05 or profit_pct <= -0.02:
                self.position.close()


class DualMA_Filter(Strategy):
    """Dual MA with volume filter"""
    fast_ma = 10
    slow_ma = 50
    
    def init(self):
        close = self.data.Close
        volume = self.data.Volume
        
        self.ma_fast = self.I(lambda x: pd.Series(x).rolling(self.fast_ma).mean(), close)
        self.ma_slow = self.I(lambda x: pd.Series(x).rolling(self.slow_ma).mean(), close)
        self.vol_avg = self.I(lambda x: pd.Series(x).rolling(20).mean(), volume)
    
    def next(self):
        # Only trade when volume is above average (momentum filter)
        if self.data.Volume[-1] < self.vol_avg[-1]:
            return
        
        # Buy when fast MA crosses above slow MA
        if self.ma_fast[-1] > self.ma_slow[-1] and self.ma_fast[-2] <= self.ma_slow[-2]:
            if not self.position:
                self.buy()
        # Sell when fast MA crosses below slow MA
        elif self.ma_fast[-1] < self.ma_slow[-1] and self.ma_fast[-2] >= self.ma_slow[-2]:
            if self.position:
                self.position.close()


# ============================================================================
# TEST ALL STRATEGIES
# ============================================================================

strategies_to_test = [
    ("RSI Oscillator", RSI_Strategy),
    ("Bollinger Bands Mean Reversion", BollingerBands_Strategy),
    ("Momentum Breakout (Ross Cameron)", MomentumBreakout_Strategy),
    ("Dual MA + Volume Filter", DualMA_Filter),
]

print("\n" + "="*70)
print("🔍 TESTING BETTER STRATEGIES (All using just pandas!)")
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
        
        if result['Sharpe'] >= 1.5:
            print(f"   🔥 EXCELLENT! Sharpe: {result['Sharpe']}, Return: {result['Return %']}%\n")
        elif result['Sharpe'] >= 1.0:
            print(f"   ✅ WINNER! Sharpe: {result['Sharpe']}, Return: {result['Return %']}%\n")
        else:
            print(f"   ⚠️  Sharpe: {result['Sharpe']} (need ≥1.0)\n")
    
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

# ============================================================================
# RESULTS
# ============================================================================

print("="*70)
print("📊 FINAL RESULTS (Sorted by Sharpe Ratio)")
print("="*70 + "\n")

df = pd.DataFrame(results).sort_values('Sharpe', ascending=False)

for _, row in df.iterrows():
    status = "🔥" if row['Sharpe'] >= 1.5 else "✅" if row['Sharpe'] >= 1.0 else "⚠️ " if row['Sharpe'] >= 0.5 else "❌"
    print(f"{status} {row['Strategy']:<35} | Sharpe: {row['Sharpe']:>5.2f} | "
          f"Return: {row['Return %']:>6.1f}% | Trades: {row['Trades']:>3}")

winners = df[df['Sharpe'] >= 1.0]

print("\n" + "="*70)
print(f"🎯 WINNERS: {len(winners)} strategies with Sharpe ≥ 1.0")
print("="*70 + "\n")

if len(winners) > 0:
    for _, row in winners.iterrows():
        print(f"✅ {row['Strategy']}")
        print(f"   Sharpe: {row['Sharpe']} | Return: {row['Return %']}% | Win Rate: {row['Win Rate %']}%\n")
    print("🎊 CONGRATS! Forward test these for 2-3 months!\n")
else:
    print("Keep testing! Moon Dev found his first winner at idea #37.")
    print(f"You're at ~{len(results) + 7}/100 ideas tested.\n")

# Save results
df.to_csv('better_strategies_results.csv', index=False)
print("💾 Saved to better_strategies_results.csv\n")

print("="*70)
print("🌙 Moon Dev: 'pandas is all you need. Keep testing!'")
print("="*70 + "\n")

