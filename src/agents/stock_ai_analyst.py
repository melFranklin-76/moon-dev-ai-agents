"""
🌙 Moon Dev's AI Stock Analysis Agent
Uses Claude/GPT to analyze charts and confirm trading setups

MOON DEV'S AI PHILOSOPHY:
"AI is your co-pilot, not your pilot. Use it to confirm your edge."

This agent:
1. Analyzes technical indicators
2. Confirms Ross Cameron setups
3. Provides confidence scores
4. Gives reasoning for decisions
"""

import os
from termcolor import colored, cprint
from typing import Dict, Optional
from datetime import datetime


try:
    from anthropic import Anthropic
except ImportError:
    cprint("⚠️  Anthropic not installed. Run: pip install anthropic", "yellow")
    Anthropic = None

try:
    import openai
except ImportError:
    cprint("⚠️  OpenAI not installed. Run: pip install openai", "yellow")
    openai = None


class StockAIAnalyst:
    """
    AI-powered stock analysis using Claude or GPT
    
    Moon Dev uses this as a CONFIRMATION layer, not the primary signal.
    """
    
    def __init__(self, ai_provider: str = 'claude'):
        """
        Initialize AI analyst
        
        Args:
            ai_provider: 'claude' or 'gpt' (default: claude)
        """
        self.provider = ai_provider.lower()
        
        if self.provider == 'claude':
            anthropic_key = os.getenv('ANTHROPIC_KEY')
            if not anthropic_key:
                raise ValueError("ANTHROPIC_KEY not found in .env file!")
            self.client = Anthropic(api_key=anthropic_key)
            self.model = "claude-3-5-sonnet-20241022"  # Latest Sonnet
        
        elif self.provider == 'gpt':
            openai_key = os.getenv('OPENAI_KEY')
            if not openai_key:
                raise ValueError("OPENAI_KEY not found in .env file!")
            openai.api_key = openai_key
            self.model = "gpt-4"
        
        else:
            raise ValueError(f"Unknown provider: {ai_provider}. Use 'claude' or 'gpt'")
        
        cprint(f"🤖 AI Analyst initialized ({self.provider.upper()})", "cyan")
    
    def analyze_stock_setup(self, symbol: str, setup_data: Dict) -> Dict:
        """
        Analyze a Ross Cameron trading setup with AI
        
        Args:
            symbol: Stock symbol
            setup_data: Dict with price, volume, gap%, indicators, etc.
            
        Returns:
            Dict with AI analysis and confidence score
        """
        try:
            # Build the analysis prompt
            prompt = self._build_analysis_prompt(symbol, setup_data)
            
            cprint(f"\n🤖 Analyzing {symbol} with {self.provider.upper()}...", "cyan")
            
            # Get AI response
            if self.provider == 'claude':
                response = self._query_claude(prompt)
            else:
                response = self._query_gpt(prompt)
            
            # Parse response
            analysis = self._parse_ai_response(response)
            
            # Print summary
            self._print_analysis_summary(symbol, analysis)
            
            return analysis
            
        except Exception as e:
            cprint(f"❌ Error in AI analysis: {str(e)}", "red")
            return {
                'decision': 'PASS',
                'confidence': 0,
                'reasoning': f'AI analysis failed: {str(e)}',
                'risk_level': 'HIGH'
            }
    
    def _build_analysis_prompt(self, symbol: str, data: Dict) -> str:
        """
        Build the AI analysis prompt
        
        This is CRITICAL - the prompt determines the quality of analysis
        """
        prompt = f"""You are Moon Dev's AI trading analyst, specializing in Ross Cameron's Warrior Trading momentum strategies.

Analyze this stock setup and provide a clear trading recommendation.

**STOCK:** {symbol}
**TIME:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

**SETUP DATA:**
- Current Price: ${data.get('price', 'N/A')}
- Gap %: {data.get('gap_percent', 'N/A')}%
- Volume: {data.get('volume', 'N/A'):,}
- Relative Volume: {data.get('rvol', 'N/A')}x
- Float: {data.get('float', 'N/A'):,} shares
- News Catalyst: {data.get('news', 'None')}

**TECHNICAL INDICATORS:**
- Near VWAP: {data.get('near_vwap', 'Unknown')}
- RSI: {data.get('rsi', 'N/A')}
- Bull Flag Pattern: {data.get('bull_flag', 'No')}
- Support Level: ${data.get('support', 'N/A')}
- Resistance Level: ${data.get('resistance', 'N/A')}

**ROSS CAMERON'S CRITERIA:**
1. Gap 3%+ ✓/✗: {' ✓' if data.get('gap_percent', 0) >= 3 else '✗'}
2. Price $2-20 ✓/✗: {'✓' if 2 <= data.get('price', 0) <= 20 else '✗'}
3. Volume 500k+ ✓/✗: {'✓' if data.get('volume', 0) >= 500000 else '✗'}
4. Float <100M ✓/✗: {'✓' if data.get('float', 999999999) <= 100000000 else '✗'}

**YOUR TASK:**
Provide analysis in this EXACT format:

DECISION: [BUY/PASS]
CONFIDENCE: [0-100]
RISK_LEVEL: [LOW/MEDIUM/HIGH]

REASONING:
[2-3 sentences explaining your decision. Focus on:
- Does this meet Ross Cameron's momentum criteria?
- Is risk/reward favorable?
- Any red flags?]

ENTRY_STRATEGY:
[If BUY: Where to enter? Wait for pullback or buy now?]

STOP_LOSS:
[Suggested stop loss level and why]

TAKE_PROFIT:
[Profit target and reasoning]

Remember Moon Dev's rule: "If you're not 70%+ confident, it's a PASS."
"""
        return prompt
    
    def _query_claude(self, prompt: str) -> str:
        """
        Query Claude for analysis
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.3,  # Lower temp for more consistent analysis
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            cprint(f"❌ Claude API error: {str(e)}", "red")
            return ""
    
    def _query_gpt(self, prompt: str) -> str:
        """
        Query GPT for analysis
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are Moon Dev's AI trading analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            cprint(f"❌ GPT API error: {str(e)}", "red")
            return ""
    
    def _parse_ai_response(self, response: str) -> Dict:
        """
        Parse AI response into structured format
        """
        # Initialize defaults
        analysis = {
            'decision': 'PASS',
            'confidence': 0,
            'risk_level': 'HIGH',
            'reasoning': '',
            'entry_strategy': '',
            'stop_loss': '',
            'take_profit': '',
            'raw_response': response
        }
        
        try:
            lines = response.split('\n')
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('DECISION:'):
                    decision = line.split(':', 1)[1].strip().upper()
                    analysis['decision'] = 'BUY' if 'BUY' in decision else 'PASS'
                
                elif line.startswith('CONFIDENCE:'):
                    conf_str = line.split(':', 1)[1].strip()
                    # Extract number from string like "75" or "75%"
                    conf_num = ''.join(filter(str.isdigit, conf_str))
                    analysis['confidence'] = int(conf_num) if conf_num else 0
                
                elif line.startswith('RISK_LEVEL:'):
                    risk = line.split(':', 1)[1].strip().upper()
                    analysis['risk_level'] = risk
                
                elif line.startswith('REASONING:'):
                    # Capture multi-line reasoning
                    idx = lines.index(line)
                    reasoning_lines = []
                    for i in range(idx + 1, len(lines)):
                        if lines[i].strip() and not lines[i].strip().startswith(('ENTRY', 'STOP', 'TAKE')):
                            reasoning_lines.append(lines[i].strip())
                        elif lines[i].strip().startswith(('ENTRY', 'STOP', 'TAKE')):
                            break
                    analysis['reasoning'] = ' '.join(reasoning_lines)
                
                elif line.startswith('ENTRY_STRATEGY:'):
                    analysis['entry_strategy'] = line.split(':', 1)[1].strip()
                
                elif line.startswith('STOP_LOSS:'):
                    analysis['stop_loss'] = line.split(':', 1)[1].strip()
                
                elif line.startswith('TAKE_PROFIT:'):
                    analysis['take_profit'] = line.split(':', 1)[1].strip()
        
        except Exception as e:
            cprint(f"⚠️  Error parsing AI response: {str(e)}", "yellow")
            analysis['reasoning'] = response[:200]  # Use first 200 chars as fallback
        
        return analysis
    
    def _print_analysis_summary(self, symbol: str, analysis: Dict) -> None:
        """
        Print a nice summary of AI analysis
        """
        decision_color = "green" if analysis['decision'] == 'BUY' else "yellow"
        confidence = analysis['confidence']
        
        cprint(f"\n{'='*60}", "cyan")
        cprint(f"🤖 AI ANALYSIS: {symbol}", "white", "on_blue")
        cprint(f"{'='*60}", "cyan")
        
        cprint(f"\n📊 Decision: {analysis['decision']}", decision_color)
        cprint(f"🎯 Confidence: {confidence}%", "green" if confidence >= 70 else "yellow")
        cprint(f"⚠️  Risk Level: {analysis['risk_level']}", "cyan")
        
        cprint(f"\n💭 Reasoning:", "cyan")
        cprint(f"   {analysis['reasoning']}", "white")
        
        if analysis['decision'] == 'BUY':
            cprint(f"\n📈 Entry Strategy:", "cyan")
            cprint(f"   {analysis['entry_strategy']}", "white")
            
            cprint(f"\n🛑 Stop Loss:", "cyan")
            cprint(f"   {analysis['stop_loss']}", "white")
            
            cprint(f"\n🎯 Take Profit:", "cyan")
            cprint(f"   {analysis['take_profit']}", "white")
        
        cprint(f"\n{'='*60}\n", "cyan")
        
        # Moon Dev's threshold
        if confidence < 70:
            cprint("⚠️  Moon Dev says: Under 70% confidence = PASS", "yellow")
    
    def batch_analyze_watchlist(self, watchlist: list) -> Dict:
        """
        Analyze multiple stocks and rank by AI confidence
        
        Args:
            watchlist: List of dicts with stock data
            
        Returns:
            Dict with ranked results
        """
        cprint(f"\n🔍 Batch analyzing {len(watchlist)} stocks...", "cyan")
        
        results = []
        
        for stock_data in watchlist:
            symbol = stock_data.get('symbol', 'UNKNOWN')
            analysis = self.analyze_stock_setup(symbol, stock_data)
            
            results.append({
                'symbol': symbol,
                'decision': analysis['decision'],
                'confidence': analysis['confidence'],
                'risk_level': analysis['risk_level'],
                'reasoning': analysis['reasoning']
            })
        
        # Sort by confidence (highest first)
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Print ranked list
        cprint(f"\n📊 RANKED RESULTS:", "white", "on_blue")
        for i, result in enumerate(results, 1):
            color = "green" if result['decision'] == 'BUY' and result['confidence'] >= 70 else "yellow"
            cprint(f"{i}. {result['symbol']}: {result['decision']} ({result['confidence']}%)", color)
        
        return {'results': results, 'top_pick': results[0] if results else None}


def test_ai_analyst():
    """
    Test the AI analyst with example data
    """
    cprint("\n🧪 Testing AI Stock Analyst", "cyan")
    
    # Initialize analyst
    analyst = StockAIAnalyst(ai_provider='claude')
    
    # Example stock data (Ross Cameron setup)
    test_stock = {
        'symbol': 'TSLA',
        'price': 8.75,
        'gap_percent': 5.2,
        'volume': 1_250_000,
        'rvol': 3.5,
        'float': 45_000_000,
        'news': 'Earnings beat expectations',
        'near_vwap': True,
        'rsi': 65,
        'bull_flag': True,
        'support': 8.50,
        'resistance': 9.20
    }
    
    # Analyze
    analysis = analyst.analyze_stock_setup('TSLA', test_stock)
    
    cprint("\n✅ AI analyst test complete!", "green")
    
    return analysis


if __name__ == "__main__":
    test_ai_analyst()

