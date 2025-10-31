# Small Account Dashboard - Common Workflows

## Daily Trading Workflow

### Morning Routine (8:00-9:30am EST)

**1. Start Dashboard**
```bash
cd /path/to/project
source venv/bin/activate  # if using venv
streamlit run small_account_dashboard.py
```

**2. Pre-Market Checklist (Tab 1)**

Check each item:
- [ ] Mark PM High/Low on your charts
- [ ] Mark Prior Day High/Low/Close
- [ ] Check BTC price (for MARA/CAN correlation trades)
- [ ] Check earnings calendar (avoid earnings if possible)
- [ ] Define Opening Range (wait 5 min after open)
- [ ] Plot VWAP on your charts
- [ ] Check Level 2 liquidity on broker
- [ ] **ONE setup only today** (pick your strategy)

**3. Review Challenge Status (Tab 4)**
- Check current streak
- Note how many green days completed
- Remember: ONE red day resets to 0

**4. Check Account Status (Top Stats)**
- Verify account balance correct
- Confirm daily P/L at $0 (fresh start)
- Check buying power available

**5. Select Today's Strategy (Tab 3)**
- Pick ONE strategy from the 20
- Re-read the rules for that strategy
- Set alerts on broker for key levels

---

### Market Open (9:30-9:35am)

**Wait for Opening Range to Form**

```
9:30:00 - Market opens
9:30:00-9:35:00 - DO NOT TRADE (let range form)
9:35:00 - Opening range complete, begin watching
```

**What to Watch:**
- High and low of first 5 minutes
- VWAP starts calculating
- Volume profile building
- BTC price action (if trading MARA/CAN)

**Set Alerts:**
- Opening range high break
- Opening range low break
- VWAP touches
- Whole dollar levels
- BTC key levels (if applicable)

---

### Trading Hours (9:35am-3:30pm)

**Active Trading Workflow:**

**Step 1: Monitor Scanner (Tab 1)**
- Watch for green "Active Setups" boxes
- Check if setup matches your chosen strategy
- Verify all conditions met

**Step 2: Confirm Setup**
```
Checklist before entering:
- [ ] Matches my chosen strategy for today
- [ ] All conditions confirmed (not just some)
- [ ] Bid/ask spread tight (< $0.05)
- [ ] Premium cost ≤ $80
- [ ] Daily loss still under $50 (have room)
- [ ] Clear stop loss level identified
- [ ] Clear take profit targets identified
```

**Step 3: Execute Trade**

*Paper Trading:*
1. Click "🚀 EXECUTE TRADE" button in scanner
2. Dashboard logs it automatically (if implemented)

*Live Trading:*
1. Open your broker (Webull, TD Ameritrade, etc.)
2. Find the option contract
3. Verify bid/ask spread again
4. Use limit order (don't market buy)
5. Entry price: Near midpoint of bid/ask
6. Set stop loss immediately after fill

**Step 4: Log Trade IMMEDIATELY (Tab 5)**
```
Do NOT wait until end of day!
Log it RIGHT NOW while details fresh.
```

Fill out form:
- **Ticker:** (e.g., MARA)
- **Strategy:** (e.g., "177. BTC-Lead Sync")
- **Side:** Call or Put
- **Entry Price:** Premium paid per contract
- **Exit Price:** (leave blank until exit)
- **Result:** (leave blank until exit)
- **Notes:** What you saw, why you entered, how you feel

Click "💾 Save Trade"

**Step 5: Manage Position**

Set alerts on broker:
- Stop loss: -20% on premium (or technical level)
- Target 1: +15% (alert to close 50%)
- Target 2: +25% (alert to close rest)

Monitor:
- Price action vs your stop level
- Time (don't forget 3:50pm exit)
- BTC correlation (if applicable)
- Volume (decreasing volume = warning)

**Step 6: Exit Trade**

*Hit Target:*
1. Close position at target (or scale out)
2. **Update Journal immediately** (Tab 5)
3. Fill in Exit Price and Result
4. Add final notes

*Hit Stop:*
1. Close position at stop loss
2. **Update Journal immediately**
3. No revenge trading - wait for next setup
4. If hit -$50 daily loss → DONE FOR THE DAY

*Approaching 3:50pm:*
1. Close ALL positions (no matter what)
2. Update Journal for each trade
3. No overnight holds (non-negotiable)

---

### End of Day (3:30-4:00pm)

**1. Close All Positions**
- Exit everything by 3:50pm
- Update Journal with final results
- Calculate day's P/L

**2. Review Performance (Tab 4)**
- Update 10-day challenge tracker
- Mark today: ✅ (green) or ❌ (red) or ⬜ (flat)
- Update streak counter
- Review equity curve

**3. Journal Review (Tab 5)**
- Read your notes for today
- What worked? What didn't?
- Did you follow your plan?
- Any emotional decisions?

**4. Export Data (Weekly)**

If Friday or end of week:
1. Click "📥 Export to CSV" (Tab 5)
2. Save file: `trades_[date].csv`
3. Open in Excel/Sheets
4. Analyze patterns

**5. Plan Tomorrow**
- Which strategy will you focus on?
- What did you learn today?
- Any alerts to set for tomorrow?
- Check economic calendar

---

## Specific Strategy Workflows

### Workflow: Trading Strategy #163 (VWAP Reclaim)

**Pre-Setup:**
1. Chart open with VWAP indicator
2. 1-minute candles
3. Volume indicator visible

**Watching Phase:**
```
Price below VWAP
↓
Waiting for push back up
↓
Volume increasing?
↓
1-min candle closes above VWAP?
```

**Entry Conditions:**
- [ ] Price was below VWAP
- [ ] Price pushed back up
- [ ] 1-min candle closes ABOVE VWAP
- [ ] Volume increased on that candle
- [ ] Next candle opens above VWAP

**Entry:**
```
Next candle opens → BUY CALL immediately
Entry price: Near mid of bid/ask
Stop loss: Price close below VWAP OR -20%
```

**Management:**
```
Watching:
- Does price stay above VWAP? ✅
- Is volume supporting? ✅
- Approaching +15%? → Prepare to sell 50%

Exit Points:
1. Closes below VWAP → EXIT ALL (stop hit)
2. Premium -20% → EXIT ALL (stop hit)
3. Premium +15% → SELL 50%
4. Premium +25% → SELL REST
```

**Post-Trade:**
- Log in Journal (Tab 5)
- Note: Was volume good? Did it respect VWAP?

---

### Workflow: Trading Strategy #177 (BTC-Lead Sync)

**Pre-Setup:**
1. BTC chart open (TradingView or Coinbase)
2. MARA or CAN chart open
3. Note key BTC levels: $70k, $72.5k, $75k, etc.

**Watching Phase:**
```
BTC approaching key level
↓
MARA/CAN watching simultaneously
↓
BTC breaks level with volume?
↓
MARA/CAN confirms within 1-2 min?
```

**Entry Conditions:**
- [ ] BTC breaks key level (e.g., $72,500)
- [ ] BTC break has volume (not slow grind)
- [ ] MARA/CAN confirms (breaks VWAP, whole dollar, or PM high)
- [ ] Confirmation within 1-2 minutes (not 10 min later)
- [ ] Correlation obvious (if weak, skip trade)

**Entry:**
```
MARA/CAN confirms → BUY CALL (if BTC broke up)
Entry price: Near mid of bid/ask
Stop loss: MARA/CAN breaks back through confirmation level
```

**Example:**
```
10:15am: BTC breaks $72,500 ↑
10:16am: MARA breaks $15.32 (VWAP) ↑
10:16:30am: BUY MARA $15.50 Call @ $0.66
Stop: MARA closes below $15.32
Target 1: $0.76 (+15%)
Target 2: $0.82 (+25%)
```

**Management:**
```
Watching:
- BTC still trending same direction? ✅
- MARA/CAN still correlated? ✅
- If correlation breaks → EXIT (even if not at stop)

Exit Points:
1. Correlation breaks → EXIT
2. MARA/CAN through stop level → EXIT
3. Premium -20% → EXIT
4. Premium +15% → SELL 50%
5. Premium +25% → SELL REST
```

**Post-Trade:**
- Log in Journal
- Note: Did correlation hold? How long? BTC level?

---

### Workflow: Trading Strategy #172 (Whole-Dollar Break)

**Pre-Setup:**
1. Chart with whole dollar levels marked
2. Watching ticker approach level (e.g., $15.00)
3. Volume indicator ready

**Watching Phase:**
```
Price approaching whole dollar
↓
Price breaks through with volume
↓
Does it hold? (1 candle)
↓
Does it hold again? (2 candles)
```

**Entry Conditions:**
- [ ] Price approached whole dollar level
- [ ] Price broke through with volume
- [ ] First 1-min candle closes above level
- [ ] Second 1-min candle closes above level
- [ ] ✅ 2 consecutive closes = confirmed

**Entry:**
```
After 2nd close above → BUY CALL
Entry price: Near mid of bid/ask
Stop loss: Back below whole dollar OR -20%
```

**Example:**
```
HOOD at $14.95
1:23pm: Breaks to $15.02 (volume) ✅ 1st close above
1:24pm: Holds at $15.04 ✅ 2nd close above
1:25pm: BUY HOOD $15 Call @ $0.72
Stop: Below $15.00
Targets: $0.83 (+15%), $0.90 (+25%)
```

**Management:**
```
Watching:
- Does price respect whole dollar as support? ✅
- Volume still good? ✅

Exit Points:
1. Closes back below whole dollar → EXIT
2. Premium -20% → EXIT
3. Premium +15% → SELL 50%
4. Premium +25% → SELL REST
```

---

## Risk Management Workflows

### Workflow: Hit Stop Loss (Single Trade)

**When Stop Triggered:**

1. **Exit immediately** (no hoping, no waiting)
2. **Log trade in Journal**
   - Mark as "Red"
   - Write notes: "Hit stop at [level]. Was I wrong about [X]?"
3. **Calculate daily loss so far**
   - Add to running total for day
   - Check if approaching -$50 limit
4. **Take a break**
   - 15-minute break minimum
   - Walk away from computer
   - Clear your head
5. **Review what went wrong**
   - Was setup invalid?
   - Did I enter too early?
   - Was volume weak?
   - Did I ignore warning signs?
6. **Decide: Continue or Stop?**
   - If under -$50 total → Can continue carefully
   - If at -$50 total → DONE FOR THE DAY ⛔
   - If emotional → DONE FOR THE DAY ⛔

**Do NOT:**
- ❌ Revenge trade (trying to "get it back")
- ❌ Double position size (desperation)
- ❌ Trade different strategy (loss of focus)
- ❌ Ignore the -$50 daily limit

---

### Workflow: Hit -$50 Daily Loss Limit

**When Limit Reached:**

**IMMEDIATE ACTIONS:**

1. **STOP TRADING** ⛔
   ```
   Close dashboard trading functions
   Log out of broker
   Step away from computer
   ```

2. **Log Final Trades**
   - Update Journal for any open trades
   - Mark day as RED ❌ in challenge tracker (Tab 4)

3. **Reset Streak (Tab 4)**
   - Current streak → 0
   - This is painful but necessary
   - This teaches discipline

4. **End of Day Review (MANDATORY)**
   - What went wrong?
   - Was it one big loss or multiple small ones?
   - Did I follow my strategy or deviate?
   - Was I emotional or disciplined?
   - What will I do differently tomorrow?

5. **Export Journal Data**
   - Save today's trades to CSV
   - Review in detail tonight

**REST OF DAY:**
- ❌ No more trading (even if you "see a setup")
- ❌ No revenge planning
- ✅ Physical activity (walk, gym, etc.)
- ✅ Review educational material
- ✅ Plan tomorrow's strategy

**NEXT DAY:**
- Fresh start (mental reset)
- Review yesterday's lessons
- Choose ONE strategy again
- Follow risk rules strictly

---

### Workflow: Hit Target (+15% or +25%)

**When Target Reached:**

**+15% Target (First Target):**

1. **Sell 50% of position immediately**
   ```
   Don't wait for more
   Take profit now
   Lock in gains
   ```

2. **Update Journal**
   - Note partial exit
   - Current P/L on closed portion

3. **Adjust Stop for Remaining 50%**
   ```
   Move stop to breakeven OR
   Move stop to +5%
   (Protect profits, can't lose now)
   ```

4. **Let runner go to +25%**
   - Now risk-free (stop at breakeven)
   - If hits, great (+25%)
   - If stops out, still win (+15% on half)

**+25% Target (Second Target):**

1. **Close remaining position**
   - Take full profit
   - Don't get greedy

2. **Update Journal fully**
   - Final exit price
   - Final P/L
   - Notes: "What went right? Can I repeat?"

3. **Celebrate!** 🎉
   - You followed your plan
   - You took profits (discipline)
   - This is the process working

4. **Update Challenge Tracker** (if end of day)
   - Mark as GREEN ✅
   - Advance streak counter

5. **Rest or Wait for Next Setup**
   - If early in day, wait for next signal
   - If late, consider stopping for day (end on high note)
   - Don't overtrade after big win

---

## Special Workflows

### Workflow: First Day Using Dashboard

**Complete Setup:**

1. **Installation** (see setup.md)
   - Install packages
   - Create .env file
   - Add Alpaca keys

2. **Run Dashboard**
   ```bash
   streamlit run small_account_dashboard.py
   ```

3. **Verify Connection** (Sidebar)
   - Should see "✅ Connected"
   - Paper balance shown

4. **Tour All Tabs**
   - Tab 1: Live Scanner (study pre-market checklist)
   - Tab 2: My Tickers (note the 6 tickers)
   - Tab 3: Trade Cards (pick 3 favorite strategies)
   - Tab 4: Performance (understand challenge)
   - Tab 5: Journal (practice logging a trade)

5. **Practice Trade Logging**
   ```
   Log fake trade to test system:
   Ticker: MARA
   Strategy: #163 (VWAP Reclaim)
   Side: Call
   Entry: $0.66
   Exit: $0.82
   Result: Green
   Notes: "Practice trade to test dashboard"
   ```

6. **Export Test**
   - Export to CSV
   - Open file
   - Verify format correct

7. **Read Full Guide**
   - `SMALL_ACCOUNT_DASHBOARD_GUIDE.md`
   - Tab 3 for strategy details
   - Plan tomorrow's focus strategy

**Tomorrow:** Start 10-day challenge!

---

### Workflow: Weekly Review (Every Friday)

**End of Week Analysis:**

**1. Export All Trades**
```
Tab 5 (Journal) → "📥 Export to CSV"
Save as: trades_week_[date].csv
```

**2. Open in Spreadsheet**
- Excel, Google Sheets, or Numbers
- Review all trades from the week

**3. Calculate Metrics**
```
Win Rate: (# Green trades / Total trades) * 100
Average Gain: Sum of gains / # winning trades
Average Loss: Sum of losses / # losing trades
Profit Factor: Total gains / Total losses
Best Strategy: Which strategy # won most?
Best Ticker: Which ticker most profitable?
Best Time: What time of day worked best?
```

**4. Pattern Analysis**
- Which strategy had highest win rate?
- Which ticker most consistent?
- What time of day best results?
- What mistakes repeated?
- What setups avoided (good discipline)?

**5. Equity Curve Review (Tab 4)**
- Is curve trending up? ✅
- Consistent slope or choppy?
- Any big drawdowns?
- Recovery time from red days?

**6. Challenge Progress Review (Tab 4)**
- Current streak: X days
- How many times reset this week?
- What caused resets?
- Getting better each week?

**7. Plan Next Week**
```
Focus Strategy: [Pick one based on data]
Focus Ticker: [Pick 2-3 based on performance]
Goal: [Specific, e.g., "Complete 5 green days"]
Improvement: [One thing to work on]
```

**8. Archive Data**
```
Create folder: trading_data/week_[date]/
Save:
- trades_week_[date].csv
- notes_week_[date].txt
- screenshots of equity curve
```

---

### Workflow: Monthly Deep Dive

**End of Month Analysis:**

**1. Compile All Weekly Exports**
```
Combine all CSVs from the month
Total trades count
Total P/L
```

**2. Advanced Metrics**
```
Monthly Win Rate
Monthly Profit Factor
Average Daily P/L
Best Week vs Worst Week
Longest Winning Streak
Longest Losing Streak
Max Drawdown
Recovery Time
Sharpe Ratio (if using advanced tracking)
```

**3. Strategy Performance Ranking**
```
Rank all 20 strategies by:
1. Win Rate
2. Profit Factor
3. Frequency Used
4. Average Gain

Identify:
- Top 3 strategies to focus on
- Bottom 3 to avoid or improve
```

**4. Psychological Review**
```
Questions to ask:
- When did I deviate from plan?
- What triggered emotional decisions?
- Which losses hurt most (why)?
- Which wins felt best (why)?
- Am I improving discipline?
- Is the 10-day challenge helping?
```

**5. Adjust for Next Month**
```
Changes to make:
- Strategy focus (top performers)
- Ticker selection (if needed)
- Risk parameters (if appropriate)
- Schedule (best times to trade)
- Position sizing (if completed 10-day challenge)
```

**6. Goal Setting**
```
Next month's goals:
- Complete 10-day challenge (if not yet)
- Achieve X% return
- Maintain Y% win rate
- Log every trade without exception
- Improve one specific skill
```

---

## Emergency Workflows

### Workflow: Dashboard Crashes

**If dashboard freezes or crashes:**

1. **Save any data visible**
   - Screenshot if possible
   - Note last action taken

2. **Force quit**
   ```bash
   Ctrl + C in terminal
   # Or if frozen:
   pkill -f streamlit
   ```

3. **Restart dashboard**
   ```bash
   streamlit run small_account_dashboard.py
   ```

4. **Verify data**
   - Check if trades still in Journal
   - Check challenge tracker status
   - Verify account balance

5. **If data lost**
   - Check for autosave (if implemented)
   - Manually re-enter critical data
   - Export to CSV immediately

6. **Report issue**
   - Note what caused crash
   - Document steps to reproduce
   - Report to developer (if applicable)

---

### Workflow: Can't Access Dashboard

**If dashboard won't start:**

1. **Check terminal for errors**
   ```
   Read error message carefully
   Note specific module or line number
   ```

2. **Common fixes:**
   ```bash
   # Module not found?
   pip install [missing_module]
   
   # Port in use?
   pkill -f streamlit
   streamlit run small_account_dashboard.py
   
   # Permission denied?
   chmod +x small_account_dashboard.py
   
   # Python version?
   python3 --version  # Should be 3.10+
   ```

3. **Reinstall dependencies**
   ```bash
   pip install --upgrade streamlit plotly pandas
   ```

4. **Check file permissions**
   ```bash
   ls -la small_account_dashboard.py
   # Should be readable
   ```

5. **Try different port**
   ```bash
   streamlit run small_account_dashboard.py --server.port 8502
   ```

6. **Last resort: Fresh install**
   ```bash
   # Backup .env and any data first!
   rm -rf venv/
   python3 -m venv venv
   source venv/bin/activate
   pip install streamlit plotly pandas python-dotenv alpaca-trade-api
   streamlit run small_account_dashboard.py
   ```

---

## Automation Tips

### Set Up Daily Startup Script

Create `start_dashboard.sh`:

```bash
#!/bin/bash
cd /Volumes/xcode/MoonDev/moon-dev-ai-agents
source venv/bin/activate
streamlit run small_account_dashboard.py
```

Make executable:
```bash
chmod +x start_dashboard.sh
```

Run anytime:
```bash
./start_dashboard.sh
```

---

### Set Up Auto-Export

**Weekly auto-export reminder:**

Use system calendar or task scheduler:
- Friday 4pm: "Export dashboard trades to CSV"
- Reminder includes: "Tab 5 → Export to CSV"

---

## Workflow Summary

**Daily:**
- ✅ Pre-market checklist (8am)
- ✅ Select strategy (before 9:30am)
- ✅ Trade execution (9:35am-3:30pm)
- ✅ Log trades immediately
- ✅ Close all by 3:50pm
- ✅ End of day review (4pm)

**Weekly:**
- ✅ Export trades (Friday)
- ✅ Analyze performance
- ✅ Plan next week

**Monthly:**
- ✅ Deep performance review
- ✅ Adjust strategies
- ✅ Set new goals

**Always:**
- ✅ Follow risk rules ($50 max loss)
- ✅ One contract maximum (until 10 days)
- ✅ Journal every trade
- ✅ Respect the 10-day challenge

---

**Remember: The workflow is the system. The system creates discipline. Discipline creates consistency. Consistency creates results.** 🎯

