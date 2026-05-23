#!/usr/bin/env python3
"""
Generate Video Voiceover using OpenAI TTS API

This script reads the video script and generates high-quality voiceover
audio files for each section using OpenAI's Text-to-Speech API.

Requirements:
    pip install openai python-dotenv

Usage:
    python generate_video_voiceover.py
"""

import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Output directory for audio files
OUTPUT_DIR = Path("video_voiceover_audio")
OUTPUT_DIR.mkdir(exist_ok=True)

# Video script sections with timestamps
# Each section has: (name, start_time, narration_text)
SCRIPT_SECTIONS = [
    {
        "name": "00_intro_hook",
        "timestamp": "0:00-0:30",
        "text": """Hey everyone! In this video, I'm going to show you the Small Account 
Options Scalper Dashboard - a powerful tool I built for traders with 
$250-$500 accounts who want to trade options systematically.

This dashboard includes:
- 26 battle-tested trading strategies
- Live setup scanner
- Real-time charts with indicators
- AI-powered strategy finder
- Automated backtesting
- And even a trading AI assistant

Whether you're starting with $250 or $2,500, this dashboard will help 
you trade with discipline and track every trade.

Let's dive in!"""
    },
    {
        "name": "01_why_dashboard",
        "timestamp": "0:30-1:30",
        "text": """Most traders fail because they lack three things:
1. A proven strategy
2. Discipline to follow it
3. A way to track progress

This dashboard solves all three problems.

I've refined 178 strategies down to the 20 absolute best for small 
accounts - strategies #159 through #178. These work on stocks like 
MARA, HOOD, SOFI, BBAI, CAN, and COMP.

PLUS, I've included 6 bonus algorithmic strategies you can study 
and adapt for your trading.

The dashboard also has a built-in 10-day challenge. If you can follow 
ONE strategy for 10 consecutive green days, you prove you can trade 
with discipline. That's the goal.

Now let me show you how to set this up..."""
    },
    {
        "name": "02_installation_setup",
        "timestamp": "1:30-3:00",
        "text": """First, let's get this installed. You'll need Python 3 installed on 
your computer.

Step 1: Open Terminal or Command Prompt on Windows.

Step 2: Navigate to the project folder.

Step 3: Install dependencies with pip install streamlit plotly pandas 
python-dotenv alpaca-trade-api numpy.

If you get SSL errors, add these flags: --trusted-host pypi.org 
--trusted-host files.pythonhosted.org

Step 4: Launch the dashboard with streamlit run small_account_dashboard.py

The dashboard will automatically open in your browser at localhost:8501.

And we're live! Now let me give you the full tour..."""
    },
    {
        "name": "03_tab_live_scanner",
        "timestamp": "3:00-4:00",
        "text": """The LIVE SCANNER is your command center.

Here you'll see cards for each ticker in your watchlist - MARA, HOOD, 
SOFI, BBAI, CAN, and COMP.

Each card shows:
- Current price and change
- Active strategy setups
- Entry conditions
- Which option to buy (strike, expiry, delta)
- Stop loss and target exits

You can also add or remove tickers dynamically. Let me show you...

Type in the ticker... click Add... and boom, it's in your watchlist.

Don't like a ticker? Click Remove.

Reset to defaults? One click.

At the bottom, there's a Pre-Market Checklist - 8 things you should 
check before you start trading. This keeps you disciplined.

Let's move to the next tab..."""
    },
    {
        "name": "04_tab_trade_cards",
        "timestamp": "4:00-5:00",
        "text": """The TRADE CARDS tab gives you a clean overview of your current 
trading status.

At the top, you see:
- Your account balance
- Today's P/L
- This week's P/L
- Days until your next challenge goal

Below that, you'll see cards for each ticker showing:
- Last price
- Whether it's above or below VWAP
- The current setup status

This is great for a quick glance at the market without getting 
overwhelmed by details.

Notice the account balance updates as you log trades in the journal.

Speaking of which... let's look at performance tracking..."""
    },
    {
        "name": "05_tab_performance",
        "timestamp": "5:00-6:00",
        "text": """The PERFORMANCE tab is where you track your progress.

The big chart at the top shows your account balance over time. 
Green is good, red means you took a loss.

Below that, you see your key metrics:
- Total trades
- Win rate percentage
- Average win amount
- Average loss amount
- Biggest win and biggest loss

And here's the 10-Day Challenge tracker. 

The goal is simple: 10 consecutive green days following ONE strategy.

Each green box is a winning day. Each red X is a loss. If you hit a 
red day, you start over.

Why 10 days? Because it proves you can follow a plan with discipline.

After 10 green days, you're allowed to scale up your position size.

Let's check out the journal..."""
    },
    {
        "name": "06_tab_journal",
        "timestamp": "6:00-7:00",
        "text": """This is the JOURNAL - the most important tab in the entire dashboard.

Why? Because every professional trader journals their trades.

Here's how to log a trade:

1. Date and time
2. Ticker (it auto-suggests from your watchlist)
3. Strategy number (159-178 or bonus algos)
4. Option details (strike, expiry, type)
5. Entry and exit prices
6. Result (Green or Red)
7. P/L amount
8. Notes about what you saw

The trade appears in the table below. You can search, filter, and 
sort all your trades.

And here's the killer feature... You can export everything to CSV 
and analyze it in Excel or Google Sheets.

At the end of each month, export your trades and review:
- Which strategies worked best
- Which tickers gave you the most wins
- What time of day you trade best
- Your emotional patterns

This is how you improve.

Now let's look at strategy performance..."""
    },
    {
        "name": "07_tab_strategy_stats",
        "timestamp": "7:00-8:00",
        "text": """The STRATEGY STATS tab shows you which strategies are actually 
making you money.

Once you've logged trades, this dashboard automatically calculates:
- Total trades per strategy
- Win rate for each strategy
- Average P/L per strategy
- Profit factor

The top 5 performers show you what's working RIGHT NOW.

The full table shows every strategy sorted by performance.

Click any column header to sort - by win rate, by total P/L, 
by number of trades.

The Insights section gives you AI-powered recommendations based on 
your data:
- Which strategy to focus on
- Which one to avoid
- What patterns it noticed

This is gold. Most traders never analyze their performance like this.

Let's check out the live charts..."""
    },
    {
        "name": "08_tab_live_charts",
        "timestamp": "8:00-9:30",
        "text": """Now we're getting into the fun stuff - LIVE CHARTS.

At the top, you select:
- Your ticker (MARA, HOOD, SOFI, etc.)
- Timeframe (1min, 5min, 15min, 1hour, 1day)
- Number of bars to display

The chart loads with real-time data from Alpaca.

Now check out all these indicators you can toggle:
- VWAP (blue line - crucial for strategies #163, #164)
- EMAs (9 and 20 - for trend confirmation)
- SMA (50 and 200 - for longer term trend)
- Bollinger Bands (for volatility)
- RSI (oversold/overbought indicator)
- Volume bars (confirm your entries)
- Whole Dollar Levels (critical for strategy #172)

See how the whole dollar levels show up? Those are $15, $16, $17, etc. 
Options scalpers love these levels because they act as magnets.

Below the chart, you get:
- Current price vs VWAP status
- RSI level (overbought, neutral, oversold)
- Automated strategy suggestions based on what the chart shows

The dashboard actually reads the indicators and tells you: "Hey, this 
looks like a VWAP reclaim setup" or "Price is at a whole dollar level."

This is like having a trading assistant watching the charts for you.

Let's move to the Strategy Finder..."""
    },
    {
        "name": "09_tab_strategy_finder",
        "timestamp": "9:30-10:30",
        "text": """The STRATEGY FINDER is your research assistant.

Say you want to find new strategies or learn more about specific 
patterns. Just type in a search query like "VWAP scalping strategies"
and click Search.

The AI searches the web and returns relevant strategy ideas with:
- A summary of the strategy
- Key points and rules
- Where it works best

You can then:
- Send it to the Backtest Lab to test it
- Add it to your journal as notes
- Ask the AI assistant to analyze it

Or use these quick search buttons for common strategies:
- Intraday VWAP
- Opening Range Breakout
- Options Scalping

And here's the new section - the 6 Bonus Algorithmic Strategies:

- Turtle Breakout (55-bar breakout system)
- Correlation Trading (ETH → Altcoin lag plays)
- Consolidation Pop (range breakout scalping)
- Nadarya-Watson (advanced indicators)
- Market Making (bid/ask spread capture)
- Mean Reversion (multi-timeframe pullbacks)

These are fully-coded strategies in the '6 Bonus Algos' folder that 
you can study and adapt.

Click any button to learn more about that strategy.

Now let's look at the Backtest Lab..."""
    },
    {
        "name": "10_tab_backtest_lab",
        "timestamp": "10:30-11:30",
        "text": """The BACKTEST LAB lets you test strategies before risking real money.

Here's how it works:

1. Name your strategy
2. Describe the rules in plain English
3. Select ticker to test on
4. Choose timeframe
5. Set lookback period (how many days of data)

For example, Strategy: "VWAP Reclaim"
Rules: "Buy when price crosses above VWAP with volume confirmation. 
Exit at +2% or if price closes back below VWAP."
Ticker: MARA
Timeframe: 5min
Lookback: 30 days

The strategy enters the queue.

You can see pending backtests here. Click "Run Now" to process them, 
or "Cancel" if you change your mind.

Once complete, results appear showing:
- Total return percentage
- Win rate
- Number of trades
- Sharpe ratio (risk-adjusted return)

This helps you validate strategies before putting real money at risk.

Now let's check out the AI Assistant..."""
    },
    {
        "name": "11_tab_ai_assistant",
        "timestamp": "11:30-12:30",
        "text": """The AI ASSISTANT is like having a trading coach available 24/7.

You can ask it anything about:
- Strategy selection
- Chart analysis
- Trade journal review
- Risk management
- The bonus algos

For example, ask: "Which strategy should I use on MARA right now?"

The AI considers current market conditions, your watchlist, and the 
26 strategies to give you specific recommendations.

Ask: "Tell me about the Turtle Trading bonus algo"

It explains the strategy, how it works, and how you can adapt it 
for options trading.

The AI has context about:
- Your current account balance
- Open trades
- Win rate
- Recent performance

This means it can give you personalized advice, not generic responses.

Ask: "Analyze my last 10 trades"

It looks at your patterns and gives you feedback on what's working 
and what needs improvement.

This is incredibly powerful for continuous learning.

Now let me give you an overview of all 26 strategies..."""
    },
    {
        "name": "12_strategies_overview",
        "timestamp": "12:30-14:00",
        "text": """Let's talk about the 26 strategies included in this dashboard.

THE 20 MAIN STRATEGIES (159-178)

These are refined from 178 total strategies through extensive 
backtesting. They're the absolute best for small account options trading.

Top 5 you need to know:

Strategy #159: 1-min ORB + VWAP Hold
- First 5 minutes after open
- Breakout of opening range above VWAP
- Target: +15-25%
- Best on MARA, HOOD, SOFI

Strategy #163: VWAP Reclaim
- Price below VWAP, then crosses back above
- Volume confirmation required
- Easiest setup to spot
- My personal favorite for consistency

Strategy #172: Whole Dollar Break
- Price breaks and holds above whole dollar
- Options contracts get active here
- Clear levels, easy risk management
- Perfect for 0DTE scalping

Strategy #177: BTC-Lead Sync
- Bitcoin breaks a level
- MARA or CAN confirms the move
- Correlation play
- Great for crypto-related stocks

Strategy #178: Power Hour Momentum
- Last hour of trading (3-4pm)
- Big moves happen here
- Closing orders create momentum
- Higher risk, higher reward

THE 6 BONUS ALGORITHMIC STRATEGIES

These are fully-coded automated strategies you can study:

Turtle Trading:
- 55-bar breakout system
- 2x ATR stop loss
- 0.2% profit target
- Works on 1min to 4hour charts

Correlation Strategy:
- Trades altcoins that lag ETH
- Finds catch-up opportunities
- Adapt for COIN, MARA when BTC moves

Consolidation Pop:
- Tight range breakouts
- Entries in lower 1/3 of range
- Perfect for whole dollar levels

Nadarya-Watson + Stoch RSI:
- Advanced indicators combo
- Best on 1-hour timeframe
- 300%+ backtest results

Market Maker:
- Bid/ask spread capture
- Complex order management
- Study this to understand liquidity

Mean Reversion (74 Tickers):
- Multi-market scanner
- Trades back to 15min SMA
- With 4hour trend filter

All the code for these bonus strategies is in the '6 Bonus Algos' 
folder. You can read the Python code, understand the logic, and 
adapt concepts for your own trading.

Now let me give you some pro tips..."""
    },
    {
        "name": "13_pro_tips",
        "timestamp": "14:00-15:30",
        "text": """Here are my top tips for using this dashboard effectively:

TIP #1: Master ONE strategy first

Don't try to trade all 26 strategies. Pick ONE. I recommend #163 
(VWAP Reclaim) because it's easiest to spot.

Trade it for 30 days. Log every trade. Learn its nuances. THEN add 
a second strategy.

TIP #2: Journal IMMEDIATELY after every trade

Not at the end of the day. Not tomorrow. Immediately.

While the emotions are fresh, write down what you saw, what you felt, 
what you did right, what you did wrong.

This habit separates profitable traders from everyone else.

TIP #3: Use the Live Scanner as your command center

Don't stare at 6 different charts. Let the scanner do the work.

Set price alerts at key levels. When an alert triggers, check the 
scanner for confirmation. If it shows a setup, execute.

TIP #4: The 10-day challenge is SACRED

If you can't get 10 consecutive green days following ONE strategy, 
you're not ready to scale up.

This isn't about being profitable - it's about proving you can follow 
a plan with discipline.

Red day? Start over. No exceptions.

TIP #5: Use the Backtest Lab before live trading

Found a new strategy? Backtest it first.

Submit it to the Backtest Lab, see the results, THEN decide if it's 
worth trading live.

TIP #6: Review Strategy Stats weekly

Every Sunday, look at your Strategy Stats tab.

Which strategies are working? Double down on those.
Which strategies are losing? Stop trading them.

Let the data guide you, not your emotions.

TIP #7: Start with paper trading

Use Alpaca's paper trading API first. Get comfortable with the 
dashboard, log 50 trades, prove consistency.

Then switch to live with real money.

TIP #8: The bonus algos are for learning

Don't try to run the automated bots without understanding them first.

Read the code. Understand the logic. Adapt the concepts for manual 
trading. THEN consider automation.

TIP #9: Risk management is non-negotiable

- Max $50 loss per day
- One contract until 10 green days
- No overnight holds (exit by 3:50pm)
- Stop loss on every trade

Break these rules and you'll blow up your account.

TIP #10: Use the AI Assistant daily

Before trading: "What setups should I watch today?"
After trading: "Analyze my last trade"
End of week: "Review my week's performance"

The AI learns from your patterns. Use it.

Now let's wrap this up..."""
    },
    {
        "name": "14_conclusion",
        "timestamp": "17:00-18:00",
        "text": """Alright, that's the complete tour of the Small Account Options 
Scalper Dashboard.

Quick Recap:

10 Tabs:
1. Live Scanner - Your command center
2. Trade Cards - Quick market overview
3. Performance - Track your progress
4. Journal - Log every trade
5. Strategy Stats - See what works
6. Live Charts - Real-time data with indicators
7. Strategy Finder - Research new ideas
8. Backtest Lab - Test before trading
9. AI Assistant - Your 24/7 coach

26 Strategies:
- 20 main strategies (159-178)
- 6 bonus algorithmic strategies

Your Next Steps:

1. Install the dashboard (follow the commands I showed)
2. Add your tickers to the watchlist
3. Pick ONE strategy to master (I recommend #163)
4. Paper trade for 30 days
5. Journal every single trade
6. Complete the 10-day challenge
7. Review Strategy Stats weekly
8. Use the AI Assistant for guidance

In the sidebar, you'll find links to:
- Complete dashboard guide
- All 26 strategies detailed
- Setup instructions
- Common workflows
- Advanced features guide

Everything is documented.

Final Thoughts:

This dashboard is a tool. It won't make you profitable by itself.

But if you:
- Pick ONE strategy
- Trade it consistently
- Journal every trade
- Follow the rules
- Complete the 10-day challenge

You WILL see improvement.

Small account trading is about consistency, discipline, and continuous 
learning. This dashboard gives you the framework.

Now go execute.

Questions? Drop them in the comments. I'll answer every one.

Want the code? Link in the description.

Found this helpful? Like and subscribe for more trading tools.

Thanks for watching, and happy trading!"""
    }
]

def generate_voiceover(section_name, text, voice="alloy", speed=1.0):
    """
    Generate voiceover audio using OpenAI TTS API
    
    Args:
        section_name: Name of the section (for filename)
        text: Text to convert to speech
        voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
        speed: Speed of speech (0.25 to 4.0, default 1.0)
    
    Returns:
        Path to saved audio file
    """
    print(f"🎤 Generating audio for: {section_name}")
    
    try:
        response = client.audio.speech.create(
            model="tts-1-hd",  # Use HD model for best quality
            voice=voice,
            input=text,
            speed=speed
        )
        
        # Save audio file
        output_path = OUTPUT_DIR / f"{section_name}.mp3"
        response.stream_to_file(output_path)
        
        print(f"✅ Saved: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error generating {section_name}: {e}")
        return None

def generate_all_sections():
    """Generate voiceover for all script sections"""
    
    print("\n" + "="*60)
    print("🎬 GENERATING VIDEO VOICEOVER AUDIO")
    print("="*60 + "\n")
    
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"📝 Total sections: {len(SCRIPT_SECTIONS)}")
    print(f"🎙️ Voice: alloy (you can change this)")
    print("\n" + "-"*60 + "\n")
    
    generated_files = []
    
    for i, section in enumerate(SCRIPT_SECTIONS, 1):
        print(f"\n[{i}/{len(SCRIPT_SECTIONS)}] {section['name']} ({section['timestamp']})")
        
        output_path = generate_voiceover(
            section_name=section['name'],
            text=section['text'],
            voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
            speed=1.0  # Adjust speed if needed
        )
        
        if output_path:
            generated_files.append(output_path)
        
        # Small delay to respect API rate limits
        time.sleep(0.5)
    
    print("\n" + "="*60)
    print("✅ VOICEOVER GENERATION COMPLETE!")
    print("="*60 + "\n")
    
    print(f"📊 Generated {len(generated_files)}/{len(SCRIPT_SECTIONS)} audio files")
    print(f"📁 Location: {OUTPUT_DIR}/")
    print("\n📋 Next Steps:")
    print("1. Record screen showing the dashboard for each section")
    print("2. Import screen recordings and audio files into video editor")
    print("3. Sync audio to video using the timestamps")
    print("4. Export final video")
    print("\n💡 Recommended video editors:")
    print("   - DaVinci Resolve (free)")
    print("   - iMovie (Mac, free)")
    print("   - Clipchamp (Windows, free)")
    
    return generated_files

def test_single_section():
    """Test generation with just the intro section"""
    print("\n🧪 Testing with intro section only...")
    
    test_section = SCRIPT_SECTIONS[0]
    output_path = generate_voiceover(
        section_name="test_intro",
        text=test_section['text'],
        voice="alloy",
        speed=1.0
    )
    
    if output_path:
        print(f"\n✅ Test successful! Listen to: {output_path}")
        print("   If you like the voice, run the full generation.")
        print("   To change voice, edit the 'voice' parameter.")
    
    return output_path

def list_available_voices():
    """List available OpenAI TTS voices"""
    print("\n🎙️ AVAILABLE VOICES:")
    print("-" * 40)
    voices = [
        ("alloy", "Neutral, balanced voice (default)"),
        ("echo", "Clear, professional voice"),
        ("fable", "Warm, engaging voice"),
        ("onyx", "Deep, authoritative voice"),
        ("nova", "Energetic, friendly voice"),
        ("shimmer", "Soft, pleasant voice")
    ]
    
    for voice, description in voices:
        print(f"  {voice:10} - {description}")
    
    print("\nTo change voice, edit the 'voice' parameter in generate_voiceover()")

if __name__ == "__main__":
    import sys
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY not found in environment")
        print("\n📝 Add to your .env file:")
        print("   OPENAI_API_KEY=your_openai_api_key_here")
        sys.exit(1)
    
    # Show available voices
    list_available_voices()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # Test with just intro
            test_single_section()
        elif sys.argv[1] == "full":
            # Generate all sections
            generate_all_sections()
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("\nUsage:")
            print("  python generate_video_voiceover.py test  # Test with intro only")
            print("  python generate_video_voiceover.py full  # Generate all sections")
    else:
        print("\n" + "="*60)
        print("🎬 VIDEO VOICEOVER GENERATOR")
        print("="*60)
        print("\nUsage:")
        print("  python generate_video_voiceover.py test  # Test with intro only")
        print("  python generate_video_voiceover.py full  # Generate all sections")
        print("\n💡 Run 'test' first to hear the voice quality!")





