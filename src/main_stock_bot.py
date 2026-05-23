"""
🌙 Moon Dev x Ross Cameron Stock Trading Bot
The perfect combination of AI + momentum trading

SYSTEM ARCHITECTURE:
1. Ross Cameron Scanner → Finds momentum setups
2. AI Analyst (Claude/GPT) → Confirms with 70%+ confidence  
3. Risk Agent → Multiple layers of protection
4. Options Executor → Places trades with proper sizing

MOON DEV'S GOLDEN RULES (from bootcamp):
- Risk management is EVERYTHING
- Research → Backtest → Implement (RBI)
- Start with tiny size ($10-20)
- 95% of strategies fail - that's OK!
- Never trade without backtesting first
- Your edge is in YOUR understanding

THIS IS NOT A "COPY AND PROFIT" BOT.
This is a LEARNING SYSTEM. Understand every piece before going live.
"""

import os
import sys
import time
from termcolor import colored, cprint
from dotenv import load_dotenv
from datetime import datetime
import schedule

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import our components
from src.brokers.alpaca_manager import AlpacaManager
from src.agents.stock_risk_agent import StockRiskAgent
from src.agents.stock_ai_analyst import StockAIAnalyst
from src.strategies.ross_cameron_scanner import RossCameronScanner
from src.agents.options_executor import OptionsExecutor

# Load environment
load_dotenv()


class MoonDevStockBot:
    """
    The main trading bot orchestrator
    
    This coordinates all components following Moon Dev's philosophy
    """
    
    def __init__(self, paper_trading=True, ai_provider='claude'):
        """
        Initialize the trading bot
        
        Args:
            paper_trading: Use paper trading (HIGHLY recommended to start)
            ai_provider: 'claude' or 'gpt'
        """
        cprint("\n" + "="*70, "cyan")
        cprint("🌙 MOON DEV x ROSS CAMERON STOCK BOT", "white", "on_blue")
        cprint("="*70 + "\n", "cyan")
        
        # Initialize components
        cprint("📡 Connecting to Alpaca...", "cyan")
        self.alpaca = AlpacaManager(paper_trading=paper_trading)
        
        cprint("🛡️  Initializing risk management...", "cyan")
        self.risk_agent = StockRiskAgent(self.alpaca, max_daily_loss=50, max_trade_loss=20)
        
        cprint("🤖 Loading AI analyst...", "cyan")
        self.ai_analyst = StockAIAnalyst(ai_provider=ai_provider)
        
        cprint("🔍 Setting up Ross Cameron scanner...", "cyan")
        self.scanner = RossCameronScanner(self.alpaca)
        
        cprint("💰 Initializing trade executor...", "cyan")
        self.executor = OptionsExecutor(self.alpaca, self.risk_agent)
        
        # Bot state
        self.running = False
        self.trades_today = []
        
        cprint("\n✅ All systems initialized!", "green")
        cprint("\n⚠️  REMEMBER: This is for LEARNING. Test everything before going live.\n", "yellow")
    
    def run_morning_scan(self):
        """
        Run the morning gap scanner (9:30-10:30 AM)
        
        This is Ross Cameron's bread and butter time
        """
        try:
            cprint("\n🌅 Running morning gap scan...", "cyan")
            
            # Step 1: Check if we can trade
            if not self.risk_agent.check_can_trade():
                cprint("🛑 Risk agent blocked trading", "red")
                return
            
            # Step 2: Scan for gappers
            gappers = self.scanner.scan_morning_gappers(min_gap_percent=3.0)
            
            if not gappers:
                cprint("   No gappers found meeting criteria", "yellow")
                return
            
            cprint(f"✅ Found {len(gappers)} potential setups", "green")
            
            # Step 3: Analyze each with AI
            for setup in gappers:
                symbol = setup['symbol']
                
                cprint(f"\n🔍 Analyzing {symbol}...", "cyan")
                
                # Get AI analysis
                ai_analysis = self.ai_analyst.analyze_stock_setup(symbol, setup)
                
                # Check if AI says BUY with high confidence
                if ai_analysis['decision'] == 'BUY' and ai_analysis['confidence'] >= 70:
                    cprint(f"🎯 {symbol} passed AI screening!", "green")
                    
                    # Execute trade
                    trade = self.executor.execute_options_trade(symbol, ai_analysis, setup)
                    
                    if trade:
                        self.trades_today.append(trade)
                        cprint(f"✅ Trade executed: {symbol}", "green")
                        
                        # Monitor position
                        self.monitor_active_trades()
                    
                    # Moon Dev rule: Only 1-2 trades per session max
                    if len(self.trades_today) >= 2:
                        cprint("\n⚠️  Max trades reached for today (Moon Dev's rule)", "yellow")
                        break
                else:
                    cprint(f"⏭️  {symbol} - PASS (AI: {ai_analysis['confidence']}%)", "yellow")
        
        except Exception as e:
            cprint(f"❌ Error in morning scan: {str(e)}", "red")
    
    def monitor_active_trades(self):
        """
        Monitor all active positions
        
        Moon Dev: "Set it and forget it? NO. Monitor constantly."
        """
        try:
            positions = self.alpaca.get_positions()
            
            if not positions:
                return
            
            cprint(f"\n👀 Monitoring {len(positions)} positions...", "cyan")
            
            for pos in positions:
                symbol = pos['symbol']
                
                # Check position health
                health = self.risk_agent.check_position_health(symbol)
                
                # Take action if needed
                if not health['healthy'] and health['action'] == 'close':
                    cprint(f"\n🚨 Closing {symbol}: {health['reason']}", "red")
                    self.alpaca.close_position(symbol)
                
                elif health['action'] == 'consider_close':
                    cprint(f"\n💰 {symbol}: {health['reason']}", "green")
        
        except Exception as e:
            cprint(f"❌ Error monitoring trades: {str(e)}", "red")
    
    def run_bot_cycle(self):
        """
        One complete bot cycle
        
        This runs every X minutes during market hours
        """
        try:
            # Show risk dashboard
            self.risk_agent.print_risk_dashboard()
            
            # Check market hours
            if not self.alpaca.is_market_open():
                cprint("⏰ Market is closed", "yellow")
                return
            
            # Check time - only trade 9:30-11:00 AM (Ross Cameron style)
            now = datetime.now()
            if now.hour == 9 and now.minute >= 30:
                # Morning session
                self.run_morning_scan()
            elif now.hour == 10:
                # Still morning session
                self.monitor_active_trades()
            elif now.hour >= 11:
                cprint("⏰ Past 11 AM - closing out day trading positions", "yellow")
                # Close all day trading positions
                self.close_all_positions()
            else:
                cprint("⏰ Waiting for market open (9:30 AM)", "yellow")
        
        except Exception as e:
            cprint(f"❌ Error in bot cycle: {str(e)}", "red")
    
    def close_all_positions(self):
        """
        Close all positions
        
        Moon Dev: Have an exit plan for everything
        """
        try:
            positions = self.alpaca.get_positions()
            
            if not positions:
                cprint("   No positions to close", "yellow")
                return
            
            cprint(f"\n🔒 Closing {len(positions)} positions...", "cyan")
            
            for pos in positions:
                symbol = pos['symbol']
                cprint(f"   Closing {symbol}...", "yellow")
                self.alpaca.close_position(symbol)
                time.sleep(0.5)
            
            cprint("✅ All positions closed", "green")
        
        except Exception as e:
            cprint(f"❌ Error closing positions: {str(e)}", "red")
    
    def start(self, mode='test'):
        """
        Start the bot
        
        Args:
            mode: 'test' (one cycle) or 'live' (continuous)
        """
        cprint("\n🚀 Starting bot...", "cyan")
        
        if mode == 'test':
            cprint("🧪 TEST MODE: Running one cycle", "yellow")
            self.run_bot_cycle()
            cprint("\n✅ Test cycle complete!", "green")
        
        elif mode == 'live':
            cprint("🔴 LIVE MODE: Bot will run continuously", "red")
            cprint("   Press Ctrl+C to stop\n", "yellow")
            
            self.running = True
            
            # Schedule checks every 5 minutes during market hours
            schedule.every(5).minutes.do(self.run_bot_cycle)
            
            while self.running:
                try:
                    schedule.run_pending()
                    time.sleep(30)  # Check every 30 seconds
                
                except KeyboardInterrupt:
                    cprint("\n\n🛑 Stopping bot...", "yellow")
                    self.running = False
                    break
                
                except Exception as e:
                    cprint(f"\n❌ Error: {str(e)}", "red")
                    cprint("⏸️  Sleeping 60 seconds before retry...", "yellow")
                    time.sleep(60)
            
            cprint("\n👋 Bot stopped. Stay profitable! 🌙\n", "cyan")


def main():
    """
    Main entry point
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Moon Dev x Ross Cameron Stock Bot')
    parser.add_argument('--mode', choices=['test', 'live'], default='test',
                       help='Run mode: test (one cycle) or live (continuous)')
    parser.add_argument('--paper', action='store_true', default=True,
                       help='Use paper trading (default: True)')
    parser.add_argument('--ai', choices=['claude', 'gpt'], default='claude',
                       help='AI provider (default: claude)')
    
    args = parser.parse_args()
    
    # Initialize bot
    bot = MoonDevStockBot(
        paper_trading=args.paper,
        ai_provider=args.ai
    )
    
    # Start bot
    bot.start(mode=args.mode)


if __name__ == "__main__":
    main()

