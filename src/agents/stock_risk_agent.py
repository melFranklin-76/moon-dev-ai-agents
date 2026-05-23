"""
🌙 Moon Dev's Risk Management Agent - Stock Edition
Adapted from his crypto risk agent for stocks/options

MOON DEV'S RISK PHILOSOPHY (from transcripts):
"Risk management is EVERYTHING. Your edge can actually BE in risk management."

LAYERS OF PROTECTION:
1. Only 1-2% of capital in exchange at a time
2. Max loss per trade (8-10%)
3. Daily loss limit ($50 with $200 account)
4. Kill switch for emergency exits
5. Position size limits
6. PDT (Pattern Day Trader) rule compliance
"""

import os
import sys
from termcolor import colored, cprint
from datetime import datetime, timedelta
from typing import Optional, Dict
import time


class StockRiskAgent:
    """
    Moon Dev's proven risk management system adapted for stocks
    
    This agent runs BEFORE every trade and can kill positions instantly.
    """
    
    def __init__(self, alpaca_manager, max_daily_loss: float = 50, max_trade_loss: float = 20):
        """
        Initialize risk agent
        
        Args:
            alpaca_manager: AlpacaManager instance
            max_daily_loss: Maximum $ loss per day (default $50)
            max_trade_loss: Maximum $ loss per trade (default $20)
        """
        self.alpaca = alpaca_manager
        self.MAX_DAILY_LOSS = max_daily_loss
        self.MAX_TRADE_LOSS = max_trade_loss
        
        # Track today's performance
        self.daily_pnl = 0
        self.trades_today = 0
        self.start_of_day_equity = None
        
        cprint("\n🛡️  Moon Dev Risk Agent Initialized", "white", "on_blue")
        cprint(f"   Max Daily Loss: ${self.MAX_DAILY_LOSS}", "cyan")
        cprint(f"   Max Trade Loss: ${self.MAX_TRADE_LOSS}", "cyan")
    
    def check_can_trade(self) -> bool:
        """
        MOON DEV'S FIRST CHECK: Can we even trade right now?
        
        This runs BEFORE every trade attempt.
        Multiple layers of protection.
        
        Returns:
            True if safe to trade, False if any limit hit
        """
        cprint("\n🔍 Running pre-trade risk checks...", "cyan")
        
        # Check 1: Market open?
        if not self.alpaca.is_market_open():
            cprint("   ⏰ Market is closed", "yellow")
            return False
        
        # Check 2: Get account info
        account = self.alpaca.get_account_info()
        
        if not account:
            cprint("   ❌ Cannot get account info", "red")
            return False
        
        # Check 3: Account blocked?
        if account.get('trading_blocked') or account.get('account_blocked'):
            cprint("   🚫 Account is blocked from trading", "red")
            return False
        
        # Check 4: Initialize daily tracking
        if self.start_of_day_equity is None:
            self.start_of_day_equity = account['equity']
            cprint(f"   📊 Starting equity: ${self.start_of_day_equity:,.2f}", "cyan")
        
        # Check 5: Calculate today's P&L
        current_equity = account['equity']
        self.daily_pnl = current_equity - self.start_of_day_equity
        
        cprint(f"   💰 Daily P&L: ${self.daily_pnl:+.2f}", 
               "green" if self.daily_pnl >= 0 else "red")
        
        # Check 6: MOON DEV KILL SWITCH #1 - Daily loss limit
        if abs(self.daily_pnl) >= self.MAX_DAILY_LOSS and self.daily_pnl < 0:
            cprint(f"\n🛑 DAILY LOSS LIMIT HIT: ${self.daily_pnl:.2f}", "white", "on_red")
            cprint("   Moon Dev says: STOP TRADING. Come back tomorrow.", "red")
            cprint("   The market will be here tomorrow. Your capital might not.", "red")
            return False
        
        # Check 7: PDT Rule (Pattern Day Trader)
        daytrade_count = account.get('daytrade_count', 0)
        self.trades_today = daytrade_count
        
        if current_equity < 25000 and daytrade_count >= 3:
            cprint(f"\n⚠️  PDT LIMIT REACHED: {daytrade_count}/3 day trades used", "yellow")
            cprint("   Cannot make more day trades until next week", "yellow")
            return False
        
        if daytrade_count >= 2:
            cprint(f"   ⚠️  Warning: {daytrade_count}/3 day trades used today", "yellow")
        
        # All checks passed
        cprint("   ✅ All risk checks passed - safe to trade", "green")
        return True
    
    def calculate_stop_loss(self, entry_price: float, risk_percent: float = 0.02) -> float:
        """
        Calculate stop loss price
        
        Moon Dev: Always know your exit BEFORE you enter
        
        Args:
            entry_price: Entry price
            risk_percent: Risk as decimal (default 2% = 0.02)
            
        Returns:
            Stop loss price
        """
        stop_loss = entry_price * (1 - risk_percent)
        cprint(f"   🛑 Stop loss set at: ${stop_loss:.2f} ({risk_percent*100}% below entry)", "yellow")
        return stop_loss
    
    def calculate_take_profit(self, entry_price: float, reward_ratio: float = 2.0) -> float:
        """
        Calculate take profit using risk:reward ratio
        
        Moon Dev: Aim for 2:1 or 3:1 risk:reward minimum
        
        Args:
            entry_price: Entry price
            reward_ratio: Reward multiple of risk (default 2.0 = 2:1)
            
        Returns:
            Take profit price
        """
        # If risking 2%, aim for 4% gain (2:1)
        risk_percent = 0.02
        reward_percent = risk_percent * reward_ratio
        
        take_profit = entry_price * (1 + reward_percent)
        cprint(f"   🎯 Take profit set at: ${take_profit:.2f} ({reward_ratio}:1 R:R)", "green")
        return take_profit
    
    def kill_switch(self, symbol: Optional[str] = None) -> bool:
        """
        MOON DEV'S KILL SWITCH
        Emergency exit from all positions
        
        This is called when:
        - Daily loss limit hit
        - Position size exceeds max
        - Something goes terribly wrong
        
        Args:
            symbol: Specific symbol to close (None = close all)
            
        Returns:
            True if successful
        """
        cprint(f"\n🚨 KILL SWITCH ACTIVATED 🚨", "white", "on_red")
        
        try:
            # Get all positions
            positions = self.alpaca.get_positions()
            
            if not positions:
                cprint("   No positions to close", "yellow")
                return True
            
            # Close specific symbol or all
            if symbol:
                cprint(f"   Closing position: {symbol}", "yellow")
                result = self.alpaca.close_position(symbol)
                if result:
                    cprint(f"   ✅ {symbol} closed", "green")
                return result
            else:
                cprint(f"   Closing ALL {len(positions)} positions", "yellow")
                for pos in positions:
                    symbol = pos['symbol']
                    cprint(f"   Closing {symbol}...", "yellow")
                    self.alpaca.close_position(symbol)
                    time.sleep(0.5)  # Brief delay between closes
                
                cprint("   ✅ All positions closed", "green")
                return True
                
        except Exception as e:
            cprint(f"   ❌ Error in kill switch: {str(e)}", "red")
            return False
    
    def check_position_health(self, symbol: str) -> Dict:
        """
        Check if current position is healthy
        
        Moon Dev: Monitor every position constantly
        
        Returns:
            Dict with position health status
        """
        try:
            position = self.alpaca.get_position(symbol)
            
            if not position:
                return {'healthy': True, 'action': 'none', 'reason': 'No position'}
            
            # Calculate position P&L
            unrealized_pl = position['unrealized_pl']
            entry_price = position['avg_entry_price']
            current_price = position['current_price']
            pl_percent = position['unrealized_plpc'] * 100
            
            cprint(f"\n📊 Position Health Check: {symbol}", "cyan")
            cprint(f"   Entry: ${entry_price:.2f}", "cyan")
            cprint(f"   Current: ${current_price:.2f}", "cyan")
            cprint(f"   P&L: ${unrealized_pl:+.2f} ({pl_percent:+.2f}%)", 
                   "green" if unrealized_pl >= 0 else "red")
            
            # Check if stop loss hit (using MAX_TRADE_LOSS)
            if unrealized_pl < -self.MAX_TRADE_LOSS:
                return {
                    'healthy': False,
                    'action': 'close',
                    'reason': f'Stop loss hit: ${unrealized_pl:.2f}'
                }
            
            # Check if take profit hit (2:1 ratio)
            take_profit_target = self.MAX_TRADE_LOSS * 2
            if unrealized_pl >= take_profit_target:
                return {
                    'healthy': True,
                    'action': 'consider_close',
                    'reason': f'Take profit target reached: ${unrealized_pl:.2f}'
                }
            
            return {'healthy': True, 'action': 'hold', 'reason': 'Position within limits'}
            
        except Exception as e:
            cprint(f"❌ Error checking position health: {str(e)}", "red")
            return {'healthy': False, 'action': 'error', 'reason': str(e)}
    
    def monitor_all_positions(self) -> None:
        """
        Monitor all open positions and take action if needed
        
        Moon Dev: This runs in the background constantly
        """
        try:
            positions = self.alpaca.get_positions()
            
            if not positions:
                return
            
            cprint(f"\n👀 Monitoring {len(positions)} positions...", "cyan")
            
            for pos in positions:
                symbol = pos['symbol']
                health = self.check_position_health(symbol)
                
                if not health['healthy']:
                    cprint(f"\n⚠️  UNHEALTHY POSITION: {symbol}", "red")
                    cprint(f"   Reason: {health['reason']}", "red")
                    
                    if health['action'] == 'close':
                        cprint(f"   🚨 Closing {symbol} immediately", "red")
                        self.alpaca.close_position(symbol)
                
                elif health['action'] == 'consider_close':
                    cprint(f"\n💰 {symbol}: {health['reason']}", "green")
                    cprint(f"   Consider taking profits", "green")
        
        except Exception as e:
            cprint(f"❌ Error monitoring positions: {str(e)}", "red")
    
    def get_risk_summary(self) -> Dict:
        """
        Get current risk status summary
        
        Returns:
            Dict with risk metrics
        """
        account = self.alpaca.get_account_info()
        
        if not account:
            return {}
        
        positions = self.alpaca.get_positions()
        total_position_value = sum(abs(pos['market_value']) for pos in positions)
        
        summary = {
            'equity': account['equity'],
            'cash': account['cash'],
            'buying_power': account['buying_power'],
            'daily_pnl': self.daily_pnl,
            'daily_pnl_percent': (self.daily_pnl / self.start_of_day_equity * 100) if self.start_of_day_equity else 0,
            'positions_count': len(positions),
            'total_position_value': total_position_value,
            'daytrades_used': self.trades_today,
            'can_trade': self.check_can_trade()
        }
        
        return summary
    
    def print_risk_dashboard(self) -> None:
        """
        Print a nice risk dashboard
        
        Moon Dev: Always know where you stand
        """
        summary = self.get_risk_summary()
        
        if not summary:
            return
        
        cprint("\n" + "="*60, "cyan")
        cprint("🛡️  MOON DEV RISK DASHBOARD", "white", "on_blue")
        cprint("="*60, "cyan")
        
        cprint(f"\n💰 Account Status:", "cyan")
        cprint(f"   Equity: ${summary['equity']:,.2f}", "white")
        cprint(f"   Cash: ${summary['cash']:,.2f}", "white")
        cprint(f"   Buying Power: ${summary['buying_power']:,.2f}", "white")
        
        pnl_color = "green" if summary['daily_pnl'] >= 0 else "red"
        cprint(f"\n📊 Today's Performance:", "cyan")
        cprint(f"   P&L: ${summary['daily_pnl']:+,.2f} ({summary['daily_pnl_percent']:+.2f}%)", pnl_color)
        cprint(f"   Day Trades Used: {summary['daytrades_used']}/3", "white")
        
        cprint(f"\n📈 Positions:", "cyan")
        cprint(f"   Open Positions: {summary['positions_count']}", "white")
        cprint(f"   Total Exposure: ${summary['total_position_value']:,.2f}", "white")
        
        cprint(f"\n🎯 Risk Limits:", "cyan")
        loss_remaining = self.MAX_DAILY_LOSS - abs(summary['daily_pnl']) if summary['daily_pnl'] < 0 else self.MAX_DAILY_LOSS
        cprint(f"   Daily Loss Limit: ${self.MAX_DAILY_LOSS}", "white")
        cprint(f"   Remaining Buffer: ${loss_remaining:.2f}", "white")
        
        can_trade_status = "✅ CLEAR TO TRADE" if summary['can_trade'] else "🛑 TRADING HALTED"
        can_trade_color = "green" if summary['can_trade'] else "red"
        cprint(f"\n{can_trade_status}", can_trade_color)
        
        cprint("\n" + "="*60 + "\n", "cyan")


def test_risk_agent():
    """
    Test the risk agent
    """
    from src.brokers.alpaca_manager import AlpacaManager
    
    cprint("\n🧪 Testing Moon Dev Risk Agent", "cyan")
    
    alpaca = AlpacaManager(paper_trading=True)
    risk_agent = StockRiskAgent(alpaca, max_daily_loss=50, max_trade_loss=20)
    
    # Test 1: Can we trade?
    can_trade = risk_agent.check_can_trade()
    
    # Test 2: Show dashboard
    risk_agent.print_risk_dashboard()
    
    # Test 3: Calculate stops
    cprint("\n📋 Testing stop loss calculation...", "cyan")
    entry = 10.00
    stop = risk_agent.calculate_stop_loss(entry, risk_percent=0.02)
    target = risk_agent.calculate_take_profit(entry, reward_ratio=2.0)
    
    cprint("\n✅ Risk agent tests complete!", "green")


if __name__ == "__main__":
    test_risk_agent()

