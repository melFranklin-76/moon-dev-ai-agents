---
name: Small Account Dashboard
description: Expert knowledge for the $250 Options Scalper Dashboard - 20 battle-tested strategies, live scanner, 10-day challenge tracker, and risk management for small account traders
---

# Small Account Options Scalper Dashboard - Expert Skill

## What This Skill Covers

This skill provides instant expertise on the **Small Account Options Scalper Dashboard** - a Streamlit-based trading dashboard designed for traders with $250-$500 accounts trading options only.

**When to use this skill:**
- Setting up and running the dashboard
- Understanding the 20 best strategies (159-178)
- Using the live scanner and trade journal
- Following the 10-day challenge rules
- Configuring Alpaca API integration
- Troubleshooting dashboard issues

## Repository Location

**Main File:** `small_account_dashboard.py`  
**Documentation:** `SMALL_ACCOUNT_DASHBOARD_GUIDE.md`  
**Project Root:** Current working directory

## Quick Start Commands

### Run the Dashboard
```bash
# Basic run
streamlit run small_account_dashboard.py

# With virtual environment
source venv/bin/activate
streamlit run small_account_dashboard.py
```

### Install Dependencies
```bash
pip install streamlit plotly pandas python-dotenv alpaca-trade-api --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

### Access Dashboard
- Local: `http://localhost:8501`
- Network: `http://192.168.X.X:8501`

### Stop Dashboard
- Press `Ctrl + C` in terminal

## Core Architecture Overview

### Dashboard Structure
```
small_account_dashboard.py (main file, ~456 lines)
├── Tab 1: 🎯 Live Scanner
│   ├── Active Setups (real-time signals)
│   ├── Pre-Market Checklist (8 items)
│   └── Risk Management Box ($50 max loss)
├── Tab 2: 📊 My Tickers
│   └── 6 core tickers (MARA, HOOD, SOFI, BBAI, CAN, COMP)
├── Tab 3: 🎴 Trade Cards
│   └── 20 strategies organized by category
├── Tab 4: 📈 Performance
│   ├── 10-Day Challenge Tracker
│   └── Equity Curve + Stats
└── Tab 5: 📝 Journal
    ├── Trade Entry Form
    └── Trade History with CSV export

Sidebar:
├── Alpaca Connection Status
├── Quick Actions (Refresh, View Strategies)
└── Resources (expandable guides)
```

### Key Components

**State Management (Session State):**
- `trades` - List of all logged trades
- `challenge_days` - 10-day challenge progress (0=pending, 1=green, -1=red)
- `current_streak` - Current consecutive green days
- `account_balance` - Starting at $250.00
- `daily_pnl` - Today's profit/loss

**Alpaca Integration:**
- Function: `get_alpaca_connection()`
- Reads from `.env` file: `ALPACA_API_KEY`, `ALPACA_SECRET_KEY`, `ALPACA_BASE_URL`
- Paper trading by default: `https://paper-api.alpaca.markets`

**Resources System:**
- Files are loaded dynamically from workspace path
- Displayed as expandable sections in sidebar
- Files: `SMALL_ACCOUNT_DASHBOARD_GUIDE.md`, `trading_ideas.md`, `ALPACA_SETUP.md`, `QUICK_START.md`

## The 6 Core Tickers

1. **MARA** (Marathon Digital) - Bitcoin-correlated mining stock
2. **HOOD** (Robinhood) - High volume fintech
3. **SOFI** (SoFi Technologies) - Fintech, good volatility
4. **BBAI** (BigBear.ai) - Small cap tech, news-driven
5. **CAN** (Canaan Inc) - Bitcoin mining, BTC-synced
6. **COMP** (Compass Inc) - Tech sector, index-correlated

**Why these 6?**
- High options liquidity (tight bid/ask spreads)
- Suitable for small premiums ($50-$80 per contract)
- Clear technical patterns (VWAP, whole dollars, EMAs)
- Correlation opportunities (BTC for MARA/CAN, SPY/QQQ for others)

## The 20 Best Strategies (Categories)

**🚀 Momentum + Confirmation (159-162)**
- Opening Range Breakouts with confirmation
- Premarket high retests

**💧 VWAP Edge (163-165)**
- VWAP reclaims, rejections, double touches
- Highest win rate strategies

**📈 Pullback Continuations (166-168)**
- EMA pullbacks in trending markets
- Higher-low / lower-high patterns

**🔄 Reversal / Mean-Reversion (169-171)**
- Stop runs, exhaustion wicks, Bollinger squeezes

**💰 Price Levels & Auction (172-175)**
- Whole/half dollar breaks and rejections
- POC and LVN plays

**🔗 Correlation (176-177)**
- Index-lead sync (SPY/QQQ)
- BTC-lead sync (MARA/CAN) - **MOST PROFITABLE**

**⏰ Time-of-Day (178)**
- Golden hour range breaks (2-3pm, 10:30-11:30am)

*Full strategy details available in: `strategies.md` resource file*

## Common Workflows

### Daily Trading Routine

**Pre-Market (8:00-9:30am EST):**
1. Complete pre-market checklist (Tab 1)
2. Mark PM high/low on charts
3. Check BTC price if trading MARA/CAN
4. Check earnings calendar
5. Select ONE strategy to focus on today

**Market Open (9:30am):**
1. Wait 5 minutes for opening range to form
2. Monitor Live Scanner (Tab 1) for signals
3. Verify bid/ask spread is tight (<$0.05)
4. Only enter if ALL conditions met

**During Market (9:35am-3:30pm):**
1. Watch for green setup boxes in scanner
2. Check VWAP and key levels on My Tickers (Tab 2)
3. Execute trade only when confirmed
4. **Log trade IMMEDIATELY** in Journal (Tab 5)
5. Set stop loss alert on broker

**End of Day (3:30-4:00pm):**
1. Exit all positions by 3:50pm (no overnight holds)
2. Review trades in Journal (Tab 5)
3. Update 10-day challenge tracker (Tab 4)
4. Export trades to CSV for weekly review

### Execute a Trade

**Setup Checklist:**
- [ ] Pre-market checklist complete (8 items)
- [ ] Setup confirmed on Live Scanner
- [ ] Bid/ask spread < $0.05 difference
- [ ] Premium cost ≤ $80 (1 contract)
- [ ] Daily loss < $50 (still have room)

**Execution:**
1. Click "🚀 EXECUTE TRADE" in scanner (paper trading)
2. Or manually execute on your broker (live trading)
3. **Immediately go to Tab 5 (Journal)**
4. Fill out trade entry form:
   - Ticker, Strategy, Side (Call/Put)
   - Entry price, Exit price
   - Result (Green/Flat/Red)
   - Notes (what you saw, why entered)
5. Click "💾 Save Trade"

**Management:**
1. Set stop loss: -20% on premium OR technical level break
2. Take profit 1: +15% (close 50% of position)
3. Take profit 2: +25% (close remaining)
4. Trail stop after +20% to protect profits

### Configure Alpaca API

**1. Create `.env` file in project root:**
```bash
# Alpaca API Configuration
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

**2. Get API Keys:**
- Sign up at alpaca.markets
- Go to "Paper Trading" section
- Generate API keys
- Copy to `.env` file

**3. Verify Connection:**
- Open dashboard
- Check sidebar: Should show "✅ Connected"
- Shows paper balance

**4. Switch to Live Trading:**
- Change `ALPACA_BASE_URL=https://api.alpaca.markets`
- **ONLY after 10 consecutive green days!**

### Review 10-Day Challenge Progress

**Access:** Tab 4 (Performance)

**Challenge Rules:**
- ✅ Green day = any profit (even $1)
- ✅ Flat day = $0 P/L (no trades or breakeven)
- ❌ Red day = any loss (even -$1) → RESET TO DAY 0

**Progress Display:**
- ✅ = Green day completed
- ❌ = Red day (streak reset)
- ⬜ = Pending day

**Current Streak:**
- Shows number of consecutive green/flat days
- Goal: 10 days to prove discipline

**After 10 Days:**
- Increase to 2 contracts maximum (still $80 each max)
- Start new 10-day challenge with 2 contracts
- Keep same risk rules ($50 max loss per day)

### Export Trade History

**Access:** Tab 5 (Journal)

**Steps:**
1. Scroll to "Trade History" section
2. Review logged trades in table
3. Click "📥 Export to CSV" button
4. File downloads to your Downloads folder
5. Filename: `trades_YYYYMMDD.csv`

**Weekly Review:**
1. Export CSV every Friday
2. Open in Excel/Google Sheets
3. Analyze patterns:
   - Which strategies have highest win rate?
   - Which tickers most profitable?
   - What times of day work best?
   - What mistakes repeated?

## Trading Rules (CRITICAL)

### Position Sizing
1. **ONE contract maximum** until 10 green days complete
2. **Max $80 per trade** (premium + fees)
3. **Max 2 open positions** at once (prefer 1)
4. **No averaging down** (if wrong, exit)

### Risk Management
1. **Max loss per day: $50** (20% of $250 account)
2. **Max loss per trade: -20%** on premium
3. **STOP TRADING at -$50 daily loss** ⛔
4. **Take profit at +15% and +25%** (scale out)

### Entry Requirements
1. Wait for setup confirmation (no FOMO)
2. Check bid/ask spread (< $0.05)
3. Only trade 9:35am - 3:30pm EST
4. ONE strategy per day (focus beats chaos)

### Exit Requirements
1. Stop loss is MANDATORY (no hoping)
2. Take 50% at +15%, rest at +25%
3. Trail stop after +20%
4. Exit all positions by 3:50pm

### Journal Requirements
1. Log EVERY trade (wins and losses)
2. Write notes IMMEDIATELY (not later)
3. Be honest about mistakes
4. Review journal weekly

## Development Rules

### Code Style
- Keep `small_account_dashboard.py` clean and readable
- Use session state for persistence
- Mock data is okay for development (marked as "Mock data")
- Real Alpaca integration optional but recommended

### File Management
- Main file: `small_account_dashboard.py` (~456 lines)
- Guide: `SMALL_ACCOUNT_DASHBOARD_GUIDE.md` (comprehensive)
- Never expose API keys (use `.env` file only)
- Resources loaded from workspace path dynamically

### Customization Points
1. **Account Balance:** Change `st.session_state.account_balance = 250.00`
2. **Max Loss:** Adjust `$50` in risk management box
3. **Tickers:** Edit `tickers` list in Tab 2
4. **Strategies:** Modify `categories` dict in Tab 3
5. **Workspace Path:** Update `workspace_path` variable for resources

## Troubleshooting

### Common Issues

**1. ModuleNotFoundError: No module named 'plotly'**
```bash
pip install plotly --trusted-host pypi.org --trusted-host files.pythonhosted.org
# Then restart: Ctrl+C and rerun streamlit
```

**2. SSL Certificate Errors**
```bash
# Method 1: Install certificates
/Applications/Python\ 3.13/Install\ Certificates.command

# Method 2: Use trusted-host flags (shown above)
```

**3. Alpaca API "Connection Failed"**
- Check `.env` file exists in project root
- Verify API keys correct (no extra spaces)
- Confirm base URL for paper: `https://paper-api.alpaca.markets`
- Restart dashboard

**4. Dashboard Shows Stale Data**
- Click "🔄 Refresh Data" in sidebar
- Or press `R` in browser
- Or enable "Always rerun" (top right menu)

**5. Resources Not Showing**
- Files must exist in workspace root
- Check paths: `SMALL_ACCOUNT_DASHBOARD_GUIDE.md`, `trading_ideas.md`
- Update `workspace_path` variable if needed

**6. Can't Stop Dashboard**
- Press `Ctrl + C` in terminal where Streamlit is running
- If frozen, close terminal and kill process:
  ```bash
  pkill -f streamlit
  ```

## Best Practices

### Strategy Selection (For Beginners)
1. **Start with #163 (VWAP Reclaim)** - Easiest to spot, clear entry/exit
2. **Add #177 (BTC-Lead Sync)** - Great for MARA/CAN, correlation obvious
3. **Add #172 (Whole-Dollar Break)** - Psychological levels, clear hold/break
4. **Master these 3** before adding more

### Execution Tips
1. Set alerts at key levels (don't stare at charts all day)
2. Use limit orders (don't pay the spread)
3. Avoid low volume options (bid/ask spread kills you)
4. Scale out at targets (take profits in stages)

### Psychology Tips
1. Red days happen - it's part of the game
2. Don't revenge trade after max loss
3. Celebrate small wins (+$10 is progress)
4. Trust the process (10 days proves it works)

### Dashboard Usage
1. Keep it open during trading hours
2. Check pre-market checklist every morning
3. Log trades immediately (not end of day)
4. Review performance tab weekly
5. Export journal monthly for deep analysis

## File References

For deeper information, refer to these resource files:

- **strategies.md** - Detailed breakdown of all 20 strategies with examples
- **setup.md** - Complete installation and configuration guide
- **workflows.md** - Step-by-step common tasks and trading workflows
- **architecture.md** - Technical details of dashboard implementation

*These files are loaded progressively as needed to avoid context bloat*

## Philosophy

This dashboard is built for **small account traders** who:
- Can't afford to lose (every dollar counts)
- Need discipline and consistency over home runs
- Want proven strategies (tested, not theoretical)
- Trade options because of limited capital
- Need risk management built-in (not optional)

**Core Belief:** Consistency beats variance for small accounts. Ten consecutive green days proves you can follow a plan. That's worth more than one lucky 100% gain.

**The Mission:** Complete the 10-day challenge. Nothing else matters right now.

---

**Questions?** Ask anything about:
- Setting up the dashboard
- Understanding the strategies
- Using the live scanner
- Following the 10-day challenge
- Configuring Alpaca
- Troubleshooting issues

This skill has instant answers for all dashboard-related questions.

