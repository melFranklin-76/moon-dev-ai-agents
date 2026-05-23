"""
🌙 Ross Cameron's Warrior Trading Scanner
Combined with Moon Dev's Risk Management Philosophy

MOON DEV'S GOLDEN RULES (from transcripts):
1. Risk management is EVERYTHING
2. Research → Backtest → Implement (RBI System)
3. 95% of strategies fail - test 100, find 5 winners
4. Start with $10-20 even if you have more
5. Never copy strategies blindly - understand EVERYTHING
6. Back test before you implement
7. Multiple layers of risk protection
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from termcolor import colored, cprint
import os


class RossCameronScanner:
    """
    Ross Cameron's Warrior Trading momentum scanner
    
    CRITERIA (from Ross Cameron):
    1. Gap up 3%+ from previous close
    2. Price: $2-20 (sweet spot for momentum)
    3. Float: Under 100M shares (moves faster)
    4. Relative Volume (RVOL): 2x+ average
    5. News catalyst (earnings, FDA, etc.)
    6. Volume: 500k+ shares
    
    MOON DEV'S ADDITIONS:
    - Multiple risk layers
    - Position size limits
    - Daily loss limits
    - Kill switch functionality
    """
    
    def __init__(self, alpaca_manager):
        """
        Initialize scanner with Alpaca connection
        
        Args:
            alpaca_manager: AlpacaManager instance
        """
        self.alpaca = alpaca_manager
        self.MAX_DAILY_LOSS = 50  # Moon Dev: Never risk more than you can afford
        self.MAX_TRADE_RISK = 20  # Per trade max loss
        self.daily_pnl = 0
        self.trades_today = 0
        
        cprint("🔍 Ross Cameron Scanner initialized", "cyan")
        cprint("⚠️  Moon Dev Risk Rules Active:", "yellow")
        cprint(f"   • Max Daily Loss: ${self.MAX_DAILY_LOSS}", "yellow")
        cprint(f"   • Max Trade Risk: ${self.MAX_TRADE_RISK}", "yellow")
    
    def scan_morning_gappers(self, min_gap_percent: float = 3.0) -> List[Dict]:
        """
        Scan for Ross Cameron's morning gap-up setups
        
        This is THE bread and butter strategy from Warrior Trading.
        Best time: 9:30-10:30 AM EST (first hour of trading)
        
        Args:
            min_gap_percent: Minimum gap % (default 3%)
            
        Returns:
            List of stocks meeting criteria
        """
        try:
            cprint(f"\n🌅 Scanning morning gappers (>{min_gap_percent}% gap)...", "cyan")
            
            # Get market scanner results
            # TODO: Implement with Alpaca's scanner API or Polygon
            # For now, return example structure
            
            gappers = []
            
            # Example structure - you'll populate this from real data
            example_gapper = {
                'symbol': 'EXAMPLE',
                'gap_percent': 5.2,
                'price': 8.50,
                'volume': 1_200_000,
                'rvol': 3.5,  # 3.5x normal volume
                'float': 45_000_000,  # 45M shares
                'news': 'Earnings beat',
                'meets_criteria': True
            }
            
            cprint(f"✅ Found {len(gappers)} gappers meeting criteria", "green")
            return gappers
            
        except Exception as e:
            cprint(f"❌ Error scanning gappers: {str(e)}", "red")
            return []
    
    def check_ross_criteria(self, symbol: str, price: float, volume: int, 
                           gap_percent: float, float_shares: int) -> Dict:
        """
        Check if stock meets Ross Cameron's criteria
        
        Returns dict with pass/fail for each criterion
        """
        criteria = {
            'gap_check': gap_percent >= 3.0,
            'price_check': 2.0 <= price <= 20.0,
            'volume_check': volume >= 500_000,
            'float_check': float_shares <= 100_000_000,
            'overall_pass': False
        }
        
        # All criteria must pass
        criteria['overall_pass'] = all([
            criteria['gap_check'],
            criteria['price_check'],
            criteria['volume_check'],
            criteria['float_check']
        ])
        
        return criteria
    
    def calculate_position_size(self, account_value: float, stock_price: float, 
                                risk_percent: float = 0.02) -> int:
        """
        Calculate position size using Moon Dev's risk management
        
        MOON DEV PHILOSOPHY:
        - Never risk more than 1-2% per trade
        - With $200 account, probably 1 contract at a time
        - Scale up ONLY after proving profitability
        
        Args:
            account_value: Total account value
            stock_price: Current stock price
            risk_percent: Risk per trade (default 2%)
            
        Returns:
            Number of shares to buy
        """
        # Moon Dev: With small account, be EXTRA careful
        if account_value < 1000:
            max_position_value = min(account_value * 0.1, 50)  # Max $50 position
            cprint(f"⚠️  Small account detected - limiting position to ${max_position_value:.2f}", "yellow")
        else:
            max_position_value = account_value * risk_percent
        
        shares = int(max_position_value / stock_price)
        
        # Must buy at least 1 share
        shares = max(1, shares)
        
        cprint(f"📊 Position size: {shares} shares @ ${stock_price:.2f} = ${shares * stock_price:.2f}", "cyan")
        return shares
    
    def check_daily_risk_limits(self) -> bool:
        """
        MOON DEV'S KILL SWITCH #1: Daily loss limit
        
        This is the FIRST layer of protection.
        If we hit max daily loss, STOP TRADING.
        
        Returns:
            True if safe to trade, False if limits hit
        """
        if abs(self.daily_pnl) >= self.MAX_DAILY_LOSS:
            cprint(f"\n🛑 DAILY LOSS LIMIT HIT: ${self.daily_pnl:.2f}", "red", "on_white")
            cprint("   Moon Dev says: STOP. Come back tomorrow.", "red")
            return False
        
        # Pattern Day Trader rule check
        if self.trades_today >= 3:
            cprint(f"\n⚠️  PDT Warning: {self.trades_today}/3 day trades used", "yellow")
            if self.alpaca.get_account_info()['equity'] < 25000:
                cprint("   🚫 Cannot make more day trades (PDT rule)", "red")
                return False
        
        return True
    
    def get_vwap_signal(self, symbol: str) -> Optional[str]:
        """
        Ross Cameron VWAP Strategy
        
        SETUP:
        - Stock gaps up, pulls back to VWAP
        - Bounces off VWAP with volume
        - Enter long on bounce
        
        Returns:
            'BUY' if setup present, None otherwise
        """
        try:
            # Get 1-minute bars
            bars = self.alpaca.get_stock_bars(symbol, '1Min', limit=100)
            
            if bars.empty:
                return None
            
            # Calculate VWAP
            bars['vwap'] = (bars['close'] * bars['volume']).cumsum() / bars['volume'].cumsum()
            
            current_price = bars['close'].iloc[-1]
            current_vwap = bars['vwap'].iloc[-1]
            
            # Check if price is near VWAP (within 0.5%)
            distance_from_vwap = abs(current_price - current_vwap) / current_vwap
            
            if distance_from_vwap < 0.005:  # Within 0.5%
                cprint(f"✅ {symbol} touching VWAP: ${current_price:.2f} (VWAP: ${current_vwap:.2f})", "green")
                return 'BUY'
            
            return None
            
        except Exception as e:
            cprint(f"❌ Error checking VWAP for {symbol}: {str(e)}", "red")
            return None
    
    def find_bull_flags(self, symbol: str) -> bool:
        """
        Ross Cameron Bull Flag Pattern
        
        PATTERN:
        1. Strong move up (pole)
        2. Consolidation (flag)
        3. Breakout above flag high
        
        Returns:
            True if bull flag detected
        """
        try:
            bars = self.alpaca.get_stock_bars(symbol, '5Min', limit=50)
            
            if bars.empty or len(bars) < 20:
                return False
            
            # Look for recent strong move (pole)
            recent_high = bars['high'].tail(20).max()
            recent_low = bars['low'].tail(20).min()
            
            pole_size = (recent_high - recent_low) / recent_low
            
            # Must have at least 5% move to form pole
            if pole_size < 0.05:
                return False
            
            # Check if consolidating near highs (flag)
            current_price = bars['close'].iloc[-1]
            consolidation_range = (recent_high - current_price) / recent_high
            
            # Flag should be within 3% of highs
            if consolidation_range < 0.03:
                cprint(f"🚩 {symbol} forming bull flag - watch for breakout!", "green")
                return True
            
            return False
            
        except Exception as e:
            cprint(f"❌ Error checking bull flag for {symbol}: {str(e)}", "red")
            return False


def test_scanner():
    """
    Test the scanner - Moon Dev style
    
    ALWAYS TEST BEFORE GOING LIVE!
    """
    from src.brokers.alpaca_manager import AlpacaManager
    
    cprint("\n" + "="*60, "cyan")
    cprint("🧪 Testing Ross Cameron Scanner", "white", "on_blue")
    cprint("="*60 + "\n", "cyan")
    
    # Initialize (paper trading)
    alpaca = AlpacaManager(paper_trading=True)
    scanner = RossCameronScanner(alpaca)
    
    # Test 1: Morning gappers
    cprint("\n📋 Test 1: Scanning morning gappers...", "cyan")
    gappers = scanner.scan_morning_gappers()
    
    # Test 2: Check criteria
    cprint("\n📋 Test 2: Testing criteria checker...", "cyan")
    test_stock = {
        'symbol': 'TEST',
        'price': 8.50,
        'volume': 750000,
        'gap_percent': 5.2,
        'float': 45000000
    }
    
    result = scanner.check_ross_criteria(
        test_stock['symbol'],
        test_stock['price'],
        test_stock['volume'],
        test_stock['gap_percent'],
        test_stock['float']
    )
    
    cprint(f"   Results: {result}", "green" if result['overall_pass'] else "yellow")
    
    # Test 3: Position sizing
    cprint("\n📋 Test 3: Testing position sizing (Moon Dev style)...", "cyan")
    account_info = alpaca.get_account_info()
    shares = scanner.calculate_position_size(
        account_value=account_info['equity'],
        stock_price=8.50
    )
    
    cprint(f"\n{'='*60}", "cyan")
    cprint("✅ All scanner tests complete!", "white", "on_green")
    cprint(f"{'='*60}\n", "cyan")


if __name__ == "__main__":
    test_scanner()

