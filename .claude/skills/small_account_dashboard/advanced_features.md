# Advanced Dashboard Features

## Overview

The Small Account Dashboard now includes **ALL Moon Dev's AI agent capabilities** integrated directly into a user-friendly interface.

---

## 🔍 TAB 8: STRATEGY FINDER

**Purpose:** Discover new trading strategies from the internet using AI-powered search

### Features:
- **Web Search Integration:** Uses OpenAI's web search to find strategies
- **AI Parsing:** Automatically extracts and summarizes key strategy components
- **Quick Suggestions:** Pre-built search queries for common strategy types
- **Direct Integration:** Send strategies to Backtest Lab or AI Assistant

### How to Use:
1. Enter a search query (e.g., "VWAP scalping strategies")
2. Click "Search Web" or use quick suggestions
3. Review results with extracted key points
4. Send promising strategies to Backtest Lab for testing
5. Ask AI Assistant for clarification on any strategy

### Search Categories:
- **Mean Reversion:** RSI oversold/overbought, Bollinger Band bounces
- **Momentum:** Breakouts, trend following, EMA crossovers
- **VWAP-based:** Reclaims, rejections, double touches
- **Level-based:** Whole dollars, prior close, pre-market high/low
- **Time-based:** Opening range, power hour, first red day
- **Volume:** POC reclaims, LVN slides, volume spikes

### Example Workflow:
```
User Action: Search "opening range breakout 0DTE"
→ AI finds 3 strategies from TradingView, Reddit, YouTube
→ User reviews summaries
→ Send best strategy to Backtest Lab
→ Review backtest results
→ Implement if profitable (>1% return)
```

---

## 🧪 TAB 9: BACKTEST LAB

**Purpose:** Automated backtesting powered by Moon Dev's RBI agents

### Moon Dev's RBI Process:
**R**esearch → **B**acktest → **I**mplement

This tab implements the **Backtest** phase of RBI.

### Features:
- **Strategy Submission:** Submit any strategy idea in plain English
- **Automated Testing:** Runs on historical data automatically
- **Multi-Timeframe:** Tests across 1min, 5min, 15min, 1hour, 1day
- **Queue Management:** Track multiple backtests simultaneously
- **Results Dashboard:** Full statistics for each backtest

### Integration with RBI Agents:
Located in `src/agents/rbi_*.py`:
- `rbi_agent_v3.py` - Latest RBI agent
- `rbi_batch_backtester.py` - Batch processing
- `rbi_agent.py` - Original RBI agent

### How Backtesting Works:
1. **User submits strategy** with description, ticker, timeframe
2. **Strategy added to queue** with "queued" status
3. **User clicks "Run Now"** → Status changes to "running"
4. **RBI agent processes:**
   - Converts strategy description to Python code
   - Fetches historical data
   - Runs backtest using `backtesting.py` library
   - Calculates statistics
   - Saves if return > threshold (default 1%)
5. **Results displayed** with full statistics

### Statistics Tracked:
- **Return %:** Total profit/loss
- **Win Rate %:** Percentage of winning trades
- **Total Trades:** Number of trades taken
- **Sharpe Ratio:** Risk-adjusted return
- **Max Drawdown:** Worst peak-to-trough decline
- **Profit Factor:** Gross profit / Gross loss
- **Average Win/Loss:** Average winner vs average loser

### Example Submission:
```
Strategy Name: VWAP Reclaim Scalp
Description:
- Entry: Price crosses above VWAP on 5min chart
- Confirmation: Volume > 1M shares
- Target: 1.5% gain
- Stop Loss: Break back below VWAP

Ticker: MARA
Timeframe: 5min
Lookback: 90 days
```

### Best Practices:
1. **Be specific** - Include entry, exit, stop loss
2. **Test one variable** - Don't change multiple things at once
3. **Use adequate data** - Minimum 90 days lookback
4. **Compare to buy & hold** - Strategy should beat passive holding
5. **Check hold time** - Short hold time = more capital efficiency

---

## 🤖 TAB 10: AI ASSISTANT

**Purpose:** Personal AI trading coach powered by Claude

### Capabilities:
- **Strategy Selection:** Recommends strategies based on market conditions
- **Chart Analysis:** Confirms setups and identifies entry/exit points
- **Trade Journal Analysis:** Finds patterns in your trading history
- **Risk Management:** Position sizing and stop loss guidance
- **Real-time Advice:** Answers specific questions about current setups

### Context Awareness:
The AI Assistant has access to:
- Your account balance
- Current open trades
- Trade history from Journal tab
- All 20 strategies (#159-178)
- Current market time (best trading hours)
- Your watchlist tickers

### Example Conversations:

#### Strategy Selection:
**You:** "Which strategy should I use on MARA right now?"

**AI:** "Based on current market conditions (10:15am, high volume):
- Strategy #163: VWAP Reclaim if MARA is near VWAP
- Strategy #172: Whole Dollar Break if MARA near $15 or $16
- Strategy #159: Already missed ORB window (9:30-9:45am)

Tell me MARA's current price and I'll give you specific entry/exit!"

#### Chart Analysis:
**You:** "MARA at $15.20, just broke above VWAP with volume spike. Good for Strategy #163?"

**AI:** "YES! ✅ This is a textbook Strategy #163 setup:
- Price: $15.20 (ABOVE VWAP ✅)
- Volume: Spike confirmed ✅
- Time: 10:15am (prime time ✅)

**Entry Plan:**
- Buy $15.50 Call (0DTE) at current premium
- Stop: If MARA drops below VWAP OR -20% on premium
- Target 1: +15% (close 50% of position)
- Target 2: +25% (close rest)

**Risk:** 1 contract only, max loss $15-20"

#### Trade Analysis:
**You:** "Analyze my last 10 trades"

**AI:** "📊 Pattern Recognition:

**Strengths:**
- 80% win rate on Strategy #172 (Whole Dollar)
- Best performance 9:45-10:30am
- Good at cutting losers quickly

**Weaknesses:**
- Cutting winners too early (avg 12% vs target 25%)
- Trading too late in the day (after 2pm)
- Overtrading Strategy #163 (only 45% win rate for you)

**Recommendations:**
1. FOCUS: Strategy #172 during 9:45-10:30am
2. STOP: Trading after 2pm
3. IMPROVE: Let winners run to 25% minimum"

### Integration with Other Tabs:
- **References Live Charts:** Can discuss specific tickers from Charts tab
- **Uses Journal Data:** Analyzes your actual trading history
- **Suggests Backtests:** Recommends strategies to test in Backtest Lab
- **Strategy Finder Link:** Can explain strategies found in Strategy Finder

---

## 📊 INTEGRATION EXAMPLE: COMPLETE WORKFLOW

### Scenario: Finding and Implementing a New Strategy

#### Step 1: STRATEGY FINDER
**Action:** Search "RSI oversold mean reversion"
**Result:** Find 3 strategies, one looks promising

#### Step 2: AI ASSISTANT
**Ask:** "What do you think about this RSI strategy?"
**Response:** AI evaluates the strategy, suggests improvements

#### Step 3: BACKTEST LAB
**Action:** Submit improved strategy for backtesting
**Result:** 2.5% return, 65% win rate ✅

#### Step 4: LIVE CHARTS
**Action:** Monitor tickers for RSI oversold signals
**Result:** SOFI shows RSI at 28 (oversold)

#### Step 5: AI ASSISTANT
**Ask:** "SOFI RSI at 28, good entry?"
**Response:** AI confirms setup, provides entry/exit plan

#### Step 6: EXECUTE
**Action:** Trade the setup (in paper trading first!)

#### Step 7: JOURNAL
**Action:** Log the trade with all details

#### Step 8: STRATEGY STATS
**Action:** Review performance after 10+ trades
**Result:** Determine if strategy works for YOU

---

## 🔗 CONNECTION TO MOON DEV'S AGENTS

### RBI Agents (Research-Backtest-Implement)
- **Location:** `src/agents/rbi_*.py`
- **Purpose:** Automate the strategy development process
- **Integration:** Backtest Lab tab connects directly to these agents

### Web Search Agent
- **Location:** Will be created based on Moon Dev's architecture
- **Purpose:** Search web for trading strategies
- **Integration:** Strategy Finder tab (currently using mock data)

### Chart Analysis Agent
- **Location:** `src/agents/chartanalysis_agent.py`
- **Purpose:** Generate and analyze trading charts
- **Integration:** Can be added to Live Charts tab for AI-powered analysis

### Chat Agents
- **Location:** `src/agents/chat_agent*.py`
- **Purpose:** Conversational AI for trading advice
- **Integration:** AI Assistant tab (currently using pattern matching)

---

## 🚀 NEXT-LEVEL FEATURES (Future Enhancements)

### Real AI Integration (vs. Current Mock Responses)

#### Currently:
- Strategy Finder: Mock search results
- Backtest Lab: Queue system (not executing actual backtests yet)
- AI Assistant: Pattern-matching responses

#### Future Integration:
1. **Connect to OpenAI Search API** for real web searches
2. **Execute RBI agents** from Backtest Lab UI
3. **Integrate Claude API** for true conversational AI
4. **Real-time data** from Alpaca for live analysis
5. **Automated trading** execution (with user approval)

### Implementation Roadmap:

#### Phase 1: Core Integrations ✅ (DONE)
- ✅ UI for Strategy Finder
- ✅ UI for Backtest Lab
- ✅ UI for AI Assistant
- ✅ Session state management
- ✅ Tab navigation

#### Phase 2: Agent Connections (IN PROGRESS)
- ⏳ Connect to RBI agents in `src/agents/`
- ⏳ Integrate OpenAI Search API
- ⏳ Add Claude API for AI Assistant
- ⏳ Real Alpaca data integration

#### Phase 3: Automation (FUTURE)
- 📋 Automated strategy discovery (always-on web search)
- 📋 Scheduled backtesting
- 📋 Real-time alerts for setups
- 📋 Automated trade execution

---

## 💡 PRO TIPS FOR MAXIMUM EFFECTIVENESS

### 1. Use the Complete RBI Workflow
Don't skip steps! Research → Backtest → Implement

### 2. Focus on Your Edge
Not all strategies work for everyone. Find YOUR winning strategies through testing.

### 3. Keep Position Sizes Small
$250 account = 1 contract only until 10 green days

### 4. Journal EVERYTHING
The Strategy Stats tab is only as good as your Journal data

### 5. Ask the AI Assistant BEFORE Trading
Get a second opinion on every setup

### 6. Backtest Before Live Trading
Even with paper money, test it first!

### 7. Review Stats Weekly
Strategy Stats tab every Sunday to plan the week

---

## 🎯 QUICK REFERENCE: WHEN TO USE EACH TAB

| Situation | Use This Tab |
|-----------|-------------|
| Looking for new strategy ideas | 🔍 Strategy Finder |
| Want to test if a strategy works | 🧪 Backtest Lab |
| Need advice on a current setup | 🤖 AI Assistant |
| Analyzing a specific ticker | 📈 Live Charts |
| Checking your performance | 📊 Strategy Stats |
| Recording a trade | 📝 Journal |
| Monitoring your watchlist | 📊 My Tickers |
| Finding active setups RIGHT NOW | 🎯 Live Scanner |

---

## 📚 RELATED FILES

- **Main Dashboard:** `small_account_dashboard.py`
- **User Guide:** `SMALL_ACCOUNT_DASHBOARD_GUIDE.md`
- **20 Strategies:** `.claude/skills/small_account_dashboard/strategies.md`
- **Setup Instructions:** `.claude/skills/small_account_dashboard/setup.md`
- **Daily Workflows:** `.claude/skills/small_account_dashboard/workflows.md`
- **RBI Agents:** `src/agents/rbi_*.py`
- **Chart Agent:** `src/agents/chartanalysis_agent.py`
- **Nice Functions:** `src/nice_funcs_hl.py` (indicators)

---

*Built with ❤️ for small account traders | Moon Dev's AI Agents Ecosystem*

