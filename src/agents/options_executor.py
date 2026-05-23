"""
🌙 Moon Dev's Options Trading Executor
Executes options trades following Ross Cameron's momentum strategies

⚠️  CRITICAL DISCLAIMER:
Options trading is EXTREMELY risky. You can lose 100% of your investment.
This is for educational purposes. Trade at your own risk.

MOON DEV'S OPTIONS RULES:
1. Start with 1 contract ONLY
2. ATM or 1 strike OTM calls
3. 0-2 DTE (days to expiration) for maximum leverage
4. Quick scalps: 20-50% gains, cut at -30%
5. NEVER hold through major resistance
"""

import os
from termcolor import colored, cprint
from typing import Optional, Dict
from datetime import datetime, timedelta


class OptionsExecutor:
    """
    Executes options trades with Moon Dev's risk management
    
    This is the FINAL step after:
    1. Scanner finds setup (Ross Cameron criteria)
    2. AI confirms with 70%+ confidence
    3. Risk agent approves trade
    """
    
    def __init__(self, alpaca_manager, risk_agent):
        """
        Initialize options executor
        
        Args:
            alpaca_manager: AlpacaManager instance
            risk_agent: StockRiskAgent instance
        """
        self.alpaca = alpaca_manager
        self.risk_agent = risk_agent
        
        # Moon Dev's options settings
        self.MAX_CONTRACTS = 1  # Start with 1 contract ONLY
        self.PROFIT_TARGET = 0.30  # 30% gain target
        self.STOP_LOSS = 0.30  # -30% max loss
        
        cprint("\n📊 Options Executor initialized", "cyan")
        cprint("⚠️  Starting with 1 contract (Moon Dev's rule)", "yellow")
    
    def execute_options_trade(self, symbol: str, ai_analysis: Dict, setup_data: Dict) -> Optional[Dict]:
        """
        Execute an options trade
        
        MOON DEV'S PROCESS:
        1. Final risk check
        2. Select best option strike
        3. Place limit order (not market!)
        4. Set mental stops
        5. Monitor position
        
        Args:
            symbol: Stock symbol
            ai_analysis: AI analysis dict with confidence
            setup_data: Scanner data
            
        Returns:
            Trade details or None if trade rejected
        """
        try:
            cprint(f"\n{'='*60}", "cyan")
            cprint(f"💰 EXECUTING OPTIONS TRADE: {symbol}", "white", "on_blue")
            cprint(f"{'='*60}", "cyan")
            
            # Step 1: FINAL RISK CHECK (Moon Dev's kill switch layer)
            if not self.risk_agent.check_can_trade():
                cprint("🛑 Risk agent blocked trade", "red")
                return None
            
            # Step 2: Confidence check
            if ai_analysis['confidence'] < 70:
                cprint(f"⚠️  AI confidence too low: {ai_analysis['confidence']}%", "yellow")
                cprint("   Moon Dev's rule: Need 70%+ confidence", "yellow")
                return None
            
            # Step 3: Get account info for position sizing
            account = self.alpaca.get_account_info()
            equity = account['equity']
            
            # With $200 account, we're limited
            if equity < 500:
                cprint(f"⚠️  Small account detected: ${equity:.2f}", "yellow")
                cprint("   Recommending stock instead of options", "yellow")
                # Fall back to stock trading
                return self._execute_stock_trade(symbol, ai_analysis, setup_data)
            
            # Step 4: Find best option contract
            option_chain = self._get_option_chain(symbol)
            
            if not option_chain:
                cprint("⚠️  No options available, using stock instead", "yellow")
                return self._execute_stock_trade(symbol, ai_analysis, setup_data)
            
            # Step 5: Select strike (ATM or 1 OTM)
            best_option = self._select_best_option(symbol, option_chain, setup_data['price'])
            
            if not best_option:
                cprint("❌ Could not find suitable option", "red")
                return None
            
            # Step 6: Place the order
            cprint(f"\n📈 Placing options order:", "cyan")
            cprint(f"   Symbol: {best_option['symbol']}", "white")
            cprint(f"   Strike: ${best_option['strike']}", "white")
            cprint(f"   Expiry: {best_option['expiry']}", "white")
            cprint(f"   Premium: ${best_option['premium']:.2f}", "white")
            cprint(f"   Quantity: {self.MAX_CONTRACTS} contract", "white")
            
            # Calculate total cost
            total_cost = best_option['premium'] * 100 * self.MAX_CONTRACTS
            cprint(f"   Total Cost: ${total_cost:.2f}", "green")
            
            # Place limit order
            order = self.alpaca.place_limit_order(
                symbol=best_option['symbol'],
                qty=self.MAX_CONTRACTS,
                limit_price=best_option['premium'],
                side='buy'
            )
            
            if not order:
                cprint("❌ Order failed", "red")
                return None
            
            # Calculate stops
            stop_loss_price = best_option['premium'] * (1 - self.STOP_LOSS)
            take_profit_price = best_option['premium'] * (1 + self.PROFIT_TARGET)
            
            trade_details = {
                'symbol': best_option['symbol'],
                'underlying': symbol,
                'strike': best_option['strike'],
                'expiry': best_option['expiry'],
                'entry_price': best_option['premium'],
                'quantity': self.MAX_CONTRACTS,
                'total_cost': total_cost,
                'stop_loss': stop_loss_price,
                'take_profit': take_profit_price,
                'order_id': order['id'],
                'timestamp': datetime.now(),
                'ai_confidence': ai_analysis['confidence'],
                'strategy': 'Ross Cameron Momentum'
            }
            
            # Print trade summary
            self._print_trade_summary(trade_details)
            
            # Log trade
            self._log_trade(trade_details)
            
            cprint("\n✅ Options trade executed successfully!", "green")
            
            return trade_details
            
        except Exception as e:
            cprint(f"❌ Error executing options trade: {str(e)}", "red")
            return None
    
    def _execute_stock_trade(self, symbol: str, ai_analysis: Dict, setup_data: Dict) -> Optional[Dict]:
        """
        Fall back to stock trading if options not suitable
        
        This happens when:
        - Account too small for options
        - No suitable options available
        - Volatility too high
        """
        try:
            cprint(f"\n💼 Executing STOCK trade instead: {symbol}", "cyan")
            
            # Calculate position size
            account = self.alpaca.get_account_info()
            stock_price = setup_data['price']
            
            shares = self.risk_agent.calculate_position_size(
                account_value=account['equity'],
                stock_price=stock_price,
                risk_percent=0.02  # 2% risk
            )
            
            # With $200 account and $10 stock = 2 shares max
            if shares < 1:
                cprint("❌ Cannot afford even 1 share", "red")
                return None
            
            cprint(f"   Buying {shares} shares @ ${stock_price:.2f}", "cyan")
            
            # Place order
            order = self.alpaca.place_limit_order(
                symbol=symbol,
                qty=shares,
                limit_price=stock_price,
                side='buy'
            )
            
            if not order:
                return None
            
            # Calculate stops
            stop_loss = self.risk_agent.calculate_stop_loss(stock_price, risk_percent=0.02)
            take_profit = self.risk_agent.calculate_take_profit(stock_price, reward_ratio=2.0)
            
            trade_details = {
                'symbol': symbol,
                'type': 'stock',
                'entry_price': stock_price,
                'quantity': shares,
                'total_cost': stock_price * shares,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'order_id': order['id'],
                'timestamp': datetime.now(),
                'ai_confidence': ai_analysis['confidence']
            }
            
            self._print_trade_summary(trade_details)
            
            return trade_details
            
        except Exception as e:
            cprint(f"❌ Error executing stock trade: {str(e)}", "red")
            return None
    
    def _get_option_chain(self, symbol: str) -> Optional[Dict]:
        """
        Get option chain for symbol
        
        NOTE: Alpaca options support is limited. This is a placeholder.
        You may need to use:
        - TD Ameritrade API
        - Interactive Brokers
        - Options data provider
        """
        try:
            # TODO: Implement real options chain fetching
            # For now, return None (will fall back to stocks)
            cprint("⚠️  Options chain fetching not yet implemented", "yellow")
            return None
            
        except Exception as e:
            cprint(f"❌ Error getting option chain: {str(e)}", "red")
            return None
    
    def _select_best_option(self, symbol: str, option_chain: Dict, current_price: float) -> Optional[Dict]:
        """
        Select best option contract
        
        MOON DEV'S RULES:
        - ATM (at-the-money) or 1 strike OTM
        - 0-2 DTE for day trading
        - Reasonable premium ($0.50-$3.00 range)
        - Good liquidity (volume & open interest)
        """
        # TODO: Implement option selection logic
        return None
    
    def _print_trade_summary(self, trade: Dict) -> None:
        """
        Print trade summary
        """
        cprint(f"\n{'='*60}", "cyan")
        cprint("📊 TRADE SUMMARY", "white", "on_blue")
        cprint(f"{'='*60}", "cyan")
        
        cprint(f"\n🎯 Symbol: {trade.get('symbol', trade.get('underlying', 'N/A'))}", "white")
        cprint(f"💰 Entry: ${trade['entry_price']:.2f}", "white")
        cprint(f"📦 Quantity: {trade['quantity']}", "white")
        cprint(f"💵 Total Cost: ${trade['total_cost']:.2f}", "green")
        
        cprint(f"\n🛑 Stop Loss: ${trade['stop_loss']:.2f}", "red")
        cprint(f"🎯 Take Profit: ${trade['take_profit']:.2f}", "green")
        
        risk_amount = trade['total_cost'] * self.STOP_LOSS
        reward_amount = trade['total_cost'] * self.PROFIT_TARGET
        cprint(f"\n📊 Risk: ${risk_amount:.2f}", "yellow")
        cprint(f"📈 Reward: ${reward_amount:.2f}", "green")
        cprint(f"⚖️  R:R Ratio: 1:{reward_amount/risk_amount:.1f}", "cyan")
        
        cprint(f"\n🤖 AI Confidence: {trade.get('ai_confidence', 0)}%", "cyan")
        cprint(f"⏰ Time: {trade['timestamp'].strftime('%H:%M:%S')}", "cyan")
        
        cprint(f"\n{'='*60}\n", "cyan")
    
    def _log_trade(self, trade: Dict) -> None:
        """
        Log trade to file for tracking
        
        Moon Dev: "Track EVERYTHING. You can't improve what you don't measure."
        """
        try:
            log_file = "trades_log.txt"
            
            with open(log_file, 'a') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"Trade executed: {trade['timestamp']}\n")
                f.write(f"Symbol: {trade.get('symbol', trade.get('underlying'))}\n")
                f.write(f"Entry: ${trade['entry_price']:.2f}\n")
                f.write(f"Quantity: {trade['quantity']}\n")
                f.write(f"Total: ${trade['total_cost']:.2f}\n")
                f.write(f"Stop: ${trade['stop_loss']:.2f}\n")
                f.write(f"Target: ${trade['take_profit']:.2f}\n")
                f.write(f"AI Confidence: {trade.get('ai_confidence', 0)}%\n")
                f.write(f"{'='*60}\n")
            
            cprint(f"📝 Trade logged to {log_file}", "cyan")
            
        except Exception as e:
            cprint(f"⚠️  Could not log trade: {str(e)}", "yellow")
    
    def monitor_position(self, trade: Dict) -> None:
        """
        Monitor open position and manage exits
        
        This runs in a loop checking:
        - Has stop loss been hit?
        - Has take profit been hit?
        - Time decay concerns?
        """
        try:
            symbol = trade.get('symbol', trade.get('underlying'))
            
            cprint(f"\n👀 Monitoring position: {symbol}", "cyan")
            
            # Get current position
            position = self.alpaca.get_position(symbol)
            
            if not position:
                cprint("   No position found", "yellow")
                return
            
            # Check health
            health = self.risk_agent.check_position_health(symbol)
            
            if not health['healthy'] and health['action'] == 'close':
                cprint(f"🚨 {health['reason']}", "red")
                cprint("   Closing position...", "red")
                self.alpaca.close_position(symbol)
            
        except Exception as e:
            cprint(f"❌ Error monitoring position: {str(e)}", "red")


def test_options_executor():
    """
    Test the options executor
    """
    from src.brokers.alpaca_manager import AlpacaManager
    from src.agents.stock_risk_agent import StockRiskAgent
    
    cprint("\n🧪 Testing Options Executor", "cyan")
    
    alpaca = AlpacaManager(paper_trading=True)
    risk_agent = StockRiskAgent(alpaca)
    executor = OptionsExecutor(alpaca, risk_agent)
    
    # Example AI analysis
    ai_analysis = {
        'decision': 'BUY',
        'confidence': 85,
        'reasoning': 'Strong momentum setup with catalyst'
    }
    
    # Example setup data
    setup_data = {
        'symbol': 'AAPL',
        'price': 175.50,
        'gap_percent': 4.2,
        'volume': 2_000_000,
        'rvol': 3.5
    }
    
    cprint("\n📋 Test data prepared", "cyan")
    cprint("   (Not executing real trade in test mode)", "yellow")
    
    cprint("\n✅ Executor test complete!", "green")


if __name__ == "__main__":
    test_options_executor()

