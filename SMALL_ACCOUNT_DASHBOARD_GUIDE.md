# 🌙 SMALL ACCOUNT DASHBOARD - COMPLETE GUIDE

## 📋 Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Setup](#setup)
4. [Dashboard Features](#dashboard-features)
5. [The 20 Best Strategies](#the-20-best-strategies)
6. [Trading Rules](#trading-rules)
7. [10-Day Challenge](#10-day-challenge)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**Small Account Options Scalper Dashboard** is designed specifically for traders with small accounts ($250-$500) who want to:
- Trade **options only** with Level 2 approval
- Follow **proven strategies** (the 20 best out of 178 tested)
- Practice **discipline** with the 10-day challenge
- Track performance and journal every trade
- Use **real-time scanning** for entry signals

### Key Features
✅ Live setup scanner for 6 tickers (MARA, HOOD, SOFI, BBAI, CAN, COMP)  
✅ 20 battle-tested strategies (159-178)  
✅ Risk management built-in (max $50 loss per day)  
✅ 10-day "Prove-It" challenge tracker  
✅ Trade journal with CSV export  
✅ Alpaca API integration (paper and live)  

---

## 🚀 Installation

### Step 1: Install Python Dependencies

```bash
cd /Volumes/xcode/MoonDev/moon-dev-ai-agents
pip install streamlit plotly pandas python-dotenv alpaca-trade-api --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

**Note:** If you get SSL errors, use the `--trusted-host` flags shown above.

### Step 2: Verify Installation

```bash
python3 -c "import streamlit, plotly, pandas; print('✅ All packages installed!')"
```

---

## ⚙️ Setup

### 1. Configure Alpaca API (Optional but Recommended)

Create or edit your `.env` file in the project root:

```bash
# Alpaca API Configuration
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # Use paper for testing
```

**How to get Alpaca API keys:**
1. Sign up at [alpaca.markets](https://alpaca.markets)
2. Go to "Paper Trading" section
3. Generate API keys
4. Copy them to your `.env` file

**Important:** Start with paper trading! Only switch to live after 10 consecutive green days.

### 2. Launch the Dashboard

```bash
streamlit run small_account_dashboard.py
```

The dashboard will open automatically at: `http://localhost:8501`

---

## 📊 Dashboard Features

### Tab 1: 🎯 LIVE SCANNER

**Purpose:** Real-time monitoring of your 6 tickers for strategy signals.

**Features:**
- **Active Setups:** Shows current trade opportunities with:
  - Ticker symbol and strategy number
  - Entry trigger conditions
  - Option strike/expiry/delta
  - Bid/ask spread (only trade if tight!)
  - Entry price (premium cost)
  - Stop loss ($ amount and %)
  - Target exits (15% and 25% gains)
  
- **Pre-Market Checklist:** 8 essential items to check before trading:
  1. Mark PM High/Low
  2. Mark Prior Day High/Low/Close
  3. Check BTC price (for MARA/CAN correlation)
  4. Check earnings calendar
  5. Define Opening Range (wait 5 min after open)
  6. Plot VWAP
  7. Check Level 2 liquidity
  8. **ONE setup only today** ⚠️

- **Risk Management Box:** 
  - Max loss today: $50 (20% of $250 account)
  - Current loss tracker
  - Max position size: $80 (1 contract)
  - **STOP TRADING at -$50!** ⛔

**How to Use:**
1. Check pre-market checklist every morning
2. Watch for green "Active Setups" boxes
3. Verify bid/ask spread is tight (< $0.05 difference)
4. Click "🚀 EXECUTE TRADE" when ready
5. Immediately log the trade in the Journal tab

---

### Tab 2: 📊 MY TICKERS

**Purpose:** Quick view of your 6 core tickers and their best setups.

**Your 6 Tickers:**
- **MARA** (Marathon Digital) - Bitcoin-correlated
- **HOOD** (Robinhood) - High volume, tech stock
- **SOFI** (SoFi Technologies) - Fintech
- **BBAI** (BigBear.ai) - Small cap tech
- **CAN** (Canaan Inc) - Bitcoin mining, BTC-correlated
- **COMP** (Compass Inc) - Tech sector

**For Each Ticker You See:**
- Current price and % change
- Volume (need good volume for options liquidity)
- VWAP level (key for most strategies)
- Best 3 strategies for that ticker

**How to Use:**
1. Watch for tickers above/below VWAP
2. Check if volume is above average
3. Match current price action to listed strategies
4. Cross-reference with Live Scanner tab

---

### Tab 3: 🎴 TRADE CARDS

**Purpose:** Reference for your 20 best-of-the-best strategies.

**Strategy Categories:**

#### 🚀 Momentum + Confirmation (159-162)
- **159. 1-min ORB + VWAP Hold** - Opening Range Breakout that holds VWAP
- **160. 1-min ORB Fail → VWAP Reject** - Fade the failed breakout
- **161. 5-min OR Break + 1-min Flag** - Break of 5-min range with pullback
- **162. Premarket High Retest-and-Go** - PM high break and retest

#### 💧 VWAP Edge (163-165)
- **163. VWAP Reclaim (Long)** - Price reclaims VWAP with volume
- **164. VWAP Rejection (Short)** - Price rejects VWAP, go short
- **165. VWAP Micro Double Bottom/Top** - VWAP touch twice, reversal

#### 📈 Pullback Continuations (166-168)
- **166. 9/20 EMA Pullback (Long)** - Pullback to 9 or 20 EMA in uptrend
- **167. 9/20 EMA Pullback (Short)** - Pullback to 9 or 20 EMA in downtrend
- **168. Higher-Low / Lower-High Continuation** - Trend continuation pattern

#### 🔄 Reversal / Mean-Reversion (169-171)
- **169. Stop-Run Reclaim** - Price runs stops, then reverses
- **170. Exhaustion Wick Reversal** - Large wick = exhaustion, fade it
- **171. Bollinger Squeeze Release** - Bollinger bands squeeze, then expand

#### 💰 Price Levels & Auction (172-175)
- **172. Whole-Dollar Break-and-Hold** - Break of $10, $15, $20, etc.
- **173. Half-Dollar Rejection Fade** - Rejection at $10.50, $15.50, etc.
- **174. POC Reclaim/Loss** - Point of Control (volume profile)
- **175. LVN Slide** - Low Volume Node = fast moves through

#### 🔗 Correlation (176-177)
- **176. Index-Lead Sync (SPY/QQQ)** - Your ticker follows SPY/QQQ
- **177. BTC-Lead Sync (MARA/CAN)** - MARA/CAN follow Bitcoin price

#### ⏰ Time-of-Day (178)
- **178. Golden-Hour Range Break** - 2-3pm range break (10:30-11:30am also works)

**How to Use:**
1. Click each category to expand and review strategies
2. Memorize your top 5 favorite setups
3. Print this tab for reference during trading hours
4. Only trade setups you FULLY understand

---

### Tab 4: 📈 PERFORMANCE

**Purpose:** Track your 10-Day Challenge and overall stats.

**10-Day Challenge Tracker:**
- Visual display: ✅ = green day, ❌ = red day, ⬜ = pending
- Current streak counter
- Status indicator (ON TRACK! or KEEP GOING!)
- ⚠️ **One red day resets counter to 0!**

**Equity Curve:**
- Line chart showing account growth over time
- Goal: Steady upward slope (consistency > big wins)

**Stats Displayed:**
- **Today's Stats:** Trades, win rate, best/worst trade
- **All-Time:** Total trades, total win rate, profit factor, max drawdown

**How to Use:**
1. Check your streak every day
2. Celebrate green days, learn from red days
3. If you break the streak, START OVER
4. Don't increase position size until 10 green days complete

---

### Tab 5: 📝 JOURNAL

**Purpose:** Log every single trade (required for the challenge).

**Trade Entry Form:**
- **Ticker:** Select from your 6 tickers
- **Strategy:** Choose which strategy (159-178)
- **Side:** Call or Put
- **Entry Price:** Premium paid (per contract)
- **Exit Price:** Premium received (per contract)
- **Result:** Green, Flat, or Red
- **Notes:** What you saw, why you entered, how it felt

**Trade History Table:**
- Shows all logged trades
- Sortable by date, ticker, P/L
- Export to CSV for analysis

**How to Use:**
1. **Log IMMEDIATELY after each trade** (don't wait until end of day)
2. Be honest in your notes (mistakes are learning opportunities)
3. Export CSV weekly to review patterns
4. Required fields: ALL of them (no shortcuts!)

**Example Trade Log:**
```
Ticker: MARA
Strategy: 177. BTC-Lead Sync
Side: Call
Entry: $0.66
Exit: $0.82
Result: Green
Notes: "BTC broke $72,500, MARA followed within 2 min. 
Entered at VWAP reclaim. Clean setup. Exited at +25% target. 
Felt calm, stuck to plan."
```

---

## 🎴 The 20 Best Strategies (Detailed)

### Top 5 Must-Know Strategies

#### #163: VWAP Reclaim (Long) 💧
**Setup:**
- Price is below VWAP
- Price pushes back up and closes above VWAP on 1-min chart
- Volume increases on the reclaim candle

**Entry:**
- Buy call option when next 1-min candle opens above VWAP

**Stop:**
- If price closes back below VWAP = EXIT
- Or -20% on premium

**Target:**
- +15% (first target, take half)
- +25% (second target, close rest)

**Example:**
```
SOFI trading at $8.85, VWAP at $8.88
- 9:47am: SOFI pushes to $8.89, closes above VWAP with volume
- Entry: Buy $9 Call (Nov 8) for $0.65
- Stop: -$13 OR close below $8.88
- Target 1: $0.75 (+15%)
- Target 2: $0.81 (+25%)
```

---

#### #177: BTC-Lead Sync (MARA/CAN) 🔗
**Setup:**
- Bitcoin (BTCUSD) breaks a key level ($70k, $72.5k, $75k, etc.)
- MARA or CAN confirms by also breaking its level or VWAP

**Entry:**
- Buy call if BTC breaks UP and MARA/CAN confirms
- Buy put if BTC breaks DOWN and MARA/CAN confirms

**Stop:**
- If MARA/CAN breaks back through entry level
- Or -20% on premium

**Target:**
- +15% and +25% (scale out)

**Example:**
```
BTC at $72,450, approaching $72,500 resistance
MARA at $15.28, VWAP at $15.32
- 10:15am: BTC breaks $72,500 with volume
- 10:16am: MARA pushes to $15.35, above VWAP
- Entry: Buy MARA $15.50 Call for $0.66
- Stop: -$13 OR MARA loses $15.32
- Exit: +25% at $0.82
```

---

#### #172: Whole-Dollar Break-and-Hold 💰
**Setup:**
- Price approaches a whole dollar level ($15, $20, $25, etc.)
- Price breaks through with volume
- Price holds above level for 1-2 candles (1-min chart)

**Entry:**
- Buy call after 2 closes above whole dollar
- (Or put if breaking down)

**Stop:**
- Back below whole dollar = EXIT
- Or -20% on premium

**Target:**
- +15% and +25%

**Example:**
```
HOOD at $14.95, approaching $15.00
- 1:23pm: HOOD breaks to $15.02 with volume
- 1:24pm: HOOD holds at $15.04
- 1:25pm: HOOD at $15.06 ✅ 2 closes above $15
- Entry: Buy HOOD $15 Call for $0.72
- Stop: -$14 OR back below $15.00
- Target: $0.83 (+15%), $0.90 (+25%)
```

---

#### #159: 1-min ORB + VWAP Hold 🚀
**Setup:**
- First 5 minutes after market open (9:30-9:35am)
- Price breaks above Opening Range high
- Price stays above VWAP

**Entry:**
- Buy call after 1-min close above OR high AND above VWAP

**Stop:**
- Below VWAP = EXIT
- Or -20%

**Target:**
- +15% and +25%

**Example:**
```
BBAI Opening Range: $3.60 - $3.65 (9:30-9:35am)
VWAP: $3.62
- 9:36am: BBAI breaks to $3.68, above OR and VWAP
- Entry: Buy $3.50 Call for $0.55
- Stop: -$11 OR below VWAP ($3.62)
- Targets: $0.63, $0.69
```

---

#### #164: VWAP Rejection (Short) 💧
**Setup:**
- Price is above VWAP
- Price pushes down to VWAP and REJECTS (bounces down)
- Volume increases on rejection candle

**Entry:**
- Buy put when next candle opens below VWAP rejection wick

**Stop:**
- If price closes back above VWAP = EXIT
- Or -20%

**Target:**
- +15% and +25%

**Example:**
```
COMP at $5.52, VWAP at $5.45
- 11:45am: COMP drops to $5.46, wicks to VWAP, closes at $5.48
- Price rejected VWAP and bounced down
- Entry: Buy $5.50 Put for $0.58
- Stop: -$12 OR close above $5.45
- Targets: $0.67, $0.73
```

---

## ⚠️ Trading Rules (MUST FOLLOW)

### Position Sizing Rules
1. **ONE contract maximum** until 10 green days complete
2. **Max $80 per trade** (includes premium + fees)
3. **Max 2 open positions** at once (prefer 1)
4. **No averaging down** (if wrong, exit and reassess)

### Risk Management Rules
1. **Max loss per day: $50** (20% of $250 account)
2. **Max loss per trade: -20%** on premium paid
3. **Stop trading if down $50 in one day** ⛔
4. **Take profit at +15% or +25%** (don't get greedy)

### Entry Rules
1. **Wait for setup confirmation** (no FOMO)
2. **Check bid/ask spread** (must be tight, <$0.05 difference)
3. **Only trade 9:35am - 3:30pm** (no pre-market or after-hours)
4. **One strategy per day** (focus beats chaos)

### Exit Rules
1. **Stop loss is MANDATORY** (no hoping it comes back)
2. **Take profit at +15%** (at least 50% of position)
3. **Trail stop after +20%** (protect profits)
4. **Exit before 3:50pm** (don't hold overnight)

### Journal Rules
1. **Log EVERY trade** (wins and losses)
2. **Write notes IMMEDIATELY** (not hours later)
3. **Be honest about mistakes** (ego is the enemy)
4. **Review journal weekly** (find patterns)

---

## 🏆 10-Day Challenge

### Goal
Complete **10 consecutive green or flat days** to prove you have discipline and consistency.

### Rules
- ✅ **Green day** = any profit (even $1)
- ✅ **Flat day** = $0 P/L (no trades or breakeven)
- ❌ **Red day** = any loss (even -$1) → **RESET TO DAY 0**

### Why This Matters
- Small accounts NEED consistency
- One big loss can wipe out weeks of gains
- 10 green days proves you can follow a plan
- After 10 days, increase to 2 contracts (still max $80 each)

### What Happens If You Fail?
- **Reset counter to 0** (no exceptions)
- **Review what went wrong** (journal review)
- **Start fresh tomorrow** (don't revenge trade)
- **Remember:** Most small account traders fail here

### After 10 Green Days
1. Celebrate! 🎉 (You're in the top 10% now)
2. Increase to **2 contracts max** per trade
3. Keep **same risk rules** ($50 max loss per day)
4. Start a new 10-day challenge with 2 contracts
5. After second 10-day run, increase account size

---

## 🛠️ Troubleshooting

### Dashboard Won't Start

**Problem:** `ModuleNotFoundError: No module named 'plotly'`

**Solution:**
```bash
pip install plotly --trusted-host pypi.org --trusted-host files.pythonhosted.org
# Then restart Streamlit (Ctrl+C, then rerun)
```

---

### SSL Certificate Errors

**Problem:** `SSLError: OSStatus -26276`

**Solution:**
```bash
# Method 1: Install Python certificates
/Applications/Python\ 3.13/Install\ Certificates.command

# Method 2: Use trusted-host flags
pip install [package] --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

---

### Alpaca API Not Connecting

**Problem:** "❌ Connection Failed" in sidebar

**Solution:**
1. Check `.env` file exists in project root
2. Verify API keys are correct (no extra spaces)
3. Confirm base URL: `https://paper-api.alpaca.markets` for paper trading
4. Restart the dashboard

---

### Dashboard Shows Wrong Data

**Problem:** Old data or stale information

**Solution:**
1. Click "🔄 Refresh Data" button in sidebar
2. Or press `R` key in the browser
3. Or click "Always rerun" in Streamlit menu (top right)

---

### Can't Export Trades to CSV

**Problem:** Export button not working

**Solution:**
1. Make sure you have at least 1 trade logged
2. Click "📥 Export to CSV" button
3. File will download to your Downloads folder
4. Filename format: `trades_YYYYMMDD.csv`

---

### Resource Files Not Showing

**Problem:** "file not found" in Resources section

**Solution:**
The dashboard looks for these files in:
```
/Volumes/xcode/MoonDev/moon-dev-ai-agents/
```

Check if these files exist:
- `trading_ideas.md`
- `ALPACA_SETUP.md`
- `QUICK_START.md`

If missing, create them or check the file path.

---

## 📚 Additional Resources

### Recommended Reading
- **Trading Ideas** (`trading_ideas.md`) - All 178 strategies explained
- **Alpaca Setup** (`ALPACA_SETUP.md`) - Complete API setup guide
- **Quick Start** (`QUICK_START.md`) - General trading bot guide

### Community & Support
- Discord: [Add your server link]
- Twitter: [Add your handle]
- GitHub: [Add repo link]

### Paper Trading Platforms
- **Alpaca** (API-based, recommended)
- **ThinkOrSwim** (TD Ameritrade paper account)
- **TastyWorks** (also has paper trading)

---

## 🎯 Quick Start Checklist

### First Time Setup
- [ ] Install Python dependencies (`pip install ...`)
- [ ] Create `.env` file with Alpaca keys
- [ ] Run dashboard (`streamlit run small_account_dashboard.py`)
- [ ] Verify dashboard loads at `http://localhost:8501`
- [ ] Check Alpaca connection in sidebar (green checkmark)

### Before Each Trading Day
- [ ] Complete pre-market checklist (Tab 1)
- [ ] Review your 20 strategies (Tab 3)
- [ ] Check 10-day challenge streak (Tab 4)
- [ ] Set daily P/L to $0 in your mind
- [ ] Remember: ONE setup only today!

### During Trading Hours
- [ ] Monitor Live Scanner (Tab 1) for signals
- [ ] Wait for confirmation (don't FOMO)
- [ ] Check bid/ask spread before entry
- [ ] Execute trade (paper or live)
- [ ] **Log trade IMMEDIATELY** (Tab 5)
- [ ] Set stop loss alert on your broker

### After Trading Day
- [ ] Review all trades in Journal (Tab 5)
- [ ] Update 10-day challenge tracker
- [ ] Export trades to CSV
- [ ] Write notes: What worked? What didn't?
- [ ] Plan for tomorrow: Which strategy will you focus on?

---

## 💡 Pro Tips

### For Small Accounts
1. **Consistency > Home Runs** - Base hits win the game
2. **-20% is better than -50%** - Take your stop losses
3. **Journal is your secret weapon** - Review it weekly
4. **One setup mastery** - Don't be a jack of all trades
5. **Time > Money** - Master the skill, money follows

### Strategy Selection
1. Start with **#163 (VWAP Reclaim)** - Easiest to spot
2. Then add **#177 (BTC-Lead Sync)** - Great for MARA/CAN
3. Then add **#172 (Whole-Dollar)** - Clear levels
4. Master these 3 before adding more

### Execution Tips
1. **Set alerts at key levels** - Don't stare at charts all day
2. **Scale out at targets** - Take profits in stages
3. **Use limit orders** - Don't pay the spread
4. **Avoid low volume options** - Bid/ask spread kills you

### Psychology Tips
1. **Red days will happen** - It's part of the game
2. **Don't revenge trade** - Step away after max loss
3. **Celebrate small wins** - +$10 is progress
4. **Trust the process** - 10 days proves it works

---

## 🚨 Final Reminders

### The Non-Negotiables
1. ⛔ **Stop at -$50 daily loss** (no exceptions)
2. ⛔ **One contract maximum** (until 10 green days)
3. ⛔ **Journal EVERY trade** (no shortcuts)
4. ⛔ **No revenge trading** (take breaks)
5. ⛔ **No overnight holds** (exit by 3:50pm)

### Your Mission
Complete the 10-day challenge. That's it. Nothing else matters right now.

Every green day is proof you can follow a plan.  
Every logged trade is practice for consistency.  
Every stop loss honored is protection of your future.

**You've got this.** 🌙

---

*Dashboard v1.0 | Built for $250 accounts | Made with ❤️ for small account traders*

