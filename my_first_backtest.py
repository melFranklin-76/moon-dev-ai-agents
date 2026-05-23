"""
YOUR FIRST BACKTEST - Simple Moving Average Strategy
====================================================

This tests: Buy when fast MA crosses above slow MA, sell when it crosses below.

Run this with: python my_first_backtest.py
"""

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG  # Example data
import pandas as pd


class SimpleSMA(Strategy):
    # Parameters you can optimize
    fast_period = 10
    slow_period = 20
    
    def init(self):
        # Calculate moving averages
        close = self.data.Close
        self.fast_ma = self.I(lambda x: pd.Series(x).rolling(self.fast_period).mean(), close)
        self.slow_ma = self.I(lambda x: pd.Series(x).rolling(self.slow_period).mean(), close)
    
    def next(self):
        # Trading logic
        if crossover(self.fast_ma, self.slow_ma):
            self.buy()
        elif crossover(self.slow_ma, self.fast_ma):
            self.position.close()


# Run the backtest
bt = Backtest(
    GOOG,                    # Using Google stock data (example)
    SimpleSMA,               # Our strategy
    cash=10000,              # Starting with $10,000
    commission=0.002         # 0.2% commission (conservative)
)

# Run and print results
print("\n" + "="*60)
print("YOUR FIRST BACKTEST RESULTS")
print("="*60 + "\n")

stats = bt.run()
print(stats)

print("\n" + "="*60)
print("KEY METRICS TO WATCH:")
print("="*60)
print(f"Return: {stats['Return [%]']:.2f}%")
print(f"Sharpe Ratio: {stats['Sharpe Ratio']:.2f} (target: >1.0)")
print(f"Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
print(f"# Trades: {stats['# Trades']}")
print("\n")

# Show the chart
bt.plot()

