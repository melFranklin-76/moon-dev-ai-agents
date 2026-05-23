# ⚡ Quick Start — 5 Steps to Your First Trading Day

## Step 1 — Install

```bash
git clone https://github.com/melFranklin-76/moon-dev-ai-agents.git
cd moon-dev-ai-agents
pip install -r requirements.txt
```

## Step 2 — Run

```bash
streamlit run small_account_dashboard.py
```

Opens at `http://localhost:8501`

## Step 3 — Set Your Balance

Sidebar → 💰 Starting Balance → enter your actual Webull balance → Set Balance

## Step 4 — Pre-Market Routine (before 9:00 AM CT)

1. **Market Regime tab** — Check SPY/QQQ/IWM. Are they above their 20-day MA? Green = trade, red = reduce size or sit out.
2. **Live Scanner tab** — Run the screener. Add any tickers that fire signals to your watchlist.
3. **My Tickers tab** — Check each ticker card. You need:
   - Signal score ≥ 7/10 (Simple Mode) or green RS + IV CHEAP/FAIR (Pro Mode)
   - Earnings → CLEAR or WATCH (never trade into DANGER or HIGH RISK)
   - VWAP position noted
4. **Catalyst Grader tab** — Grade your top 1-2 candidates. A or A+ only.
5. **Options Planner tab** — Paste in your ticker, stock price, and option premium. Get your exact entry, stop, and targets before the open.

## Step 5 — During the Trade

- Entry window: **9:30 AM CT only** (first 30 minutes of market open in Central Time = 10:30 ET)
- Stop loss fires at **-30% premium** — no exceptions
- First exit at **+15%** (sell half)
- Full exit at **+25%** or close by 9:30 AM CT

## After the Trade — Log It

Journal tab → Log New Trade (manual) or import your Webull CSV at the end of the week.

---

## On Your Phone

Safari → your Streamlit Cloud URL → Share → Add to Home Screen → Done.
Tap the icon — full-screen app, no browser bar.

---

## Push Notifications

Sidebar → 📲 Push Notifications → enter a topic name (e.g. `scalper_mel`) → Save
Download **ntfy** app on iPhone → subscribe to same topic.
You'll get a push every time a scanner signal fires or a price alert triggers.
