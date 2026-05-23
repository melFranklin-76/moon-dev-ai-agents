# 🌙 $250 Small Account Options Scalper Dashboard

A personal trading dashboard built for a **$250 Webull cash account, Level 2 options** (buy calls/puts only). Tracks live prices, scores setups, logs trades, and protects against common small account mistakes.

---

## What It Is

A Streamlit web app that runs in your browser (or on your phone via Add to Home Screen). It pulls live market data from Yahoo Finance and gives you a single place to:

- Scan for momentum setups before the open
- Score every ticker on 5 insider layers before you touch it
- Know if earnings are coming before you buy a call
- Find which exact strike is the best value on the chain
- Log every trade and track your 10-day challenge
- Simulate what happens to your option at different stock price moves

**This is a preparation tool, not an execution tool.** You still trade manually on Webull.

---

## The 9 Tabs

| Tab | What it does |
|-----|-------------|
| 📡 **Live Scanner** | Scans for #163 VWAP Reclaim, #172 Whole-Dollar Break, #177 BTC Sync signals |
| 📊 **My Tickers** | Live cards for your watchlist — Simple Mode (0-10 score) or Pro Mode (all 5 layers) |
| 🎴 **Trade Cards** | Your 20 best-of-the-best strategy reference (strategies 159–178) |
| 📈 **Performance** | 10-day challenge tracker, equity curve, daily P&L goal bar |
| 📝 **Journal** | Log trades manually or import from Webull CSV. 3-strike auto-lock. |
| 🌡️ **Market Regime** | SPY/QQQ/IWM/VIX + sector flow + PDT countdown |
| 🎯 **Catalyst Grader** | SMB 5-check pre-market grading system (A/B/C/F) |
| 💰 **Options Planner** | Trade plan generator + Black-Scholes P&L scenario simulator |
| 🧠 **Coach** | Tendencies log + pre-trade checklist |

---

## The 5 Layers (Pro Mode Ticker Cards)

Every ticker card in Pro Mode shows:

1. **RS vs SPY** — Is this stock leading or lagging the market right now?
2. **IV Rank** — Are options cheap, fair, or expensive vs recent history?
3. **Squeeze Score** — Float + short interest pressure (0–100)
4. **Max Pain** — Where market makers profit most at expiry
5. **Best Buy Strike** — Which specific call is cheapest vs the IV smile curve

In **Simple Mode**, all 5 layers collapse into a single 0–10 score with a star rating and one-line advice. Built for phone screens.

---

## Earnings Protection

Every ticker card shows the next earnings date and a risk grade:

| Grade | Days | Meaning |
|-------|------|---------|
| 🚨 DANGER | ≤ 3d | Do not buy calls — IV crush incoming |
| ⚠️ HIGH RISK | ≤ 7d | IV already inflated, exit or skip |
| ⚠️ CAUTION | ≤ 14d | Plan your exit before the date |
| 👀 WATCH | ≤ 30d | On radar |
| ✅ CLEAR | > 30d | No near-term risk |

---

## How to Run It

### Requirements
- Python 3.11+
- A Webull account (Level 2 options)

### Install
```bash
git clone https://github.com/melFranklin-76/moon-dev-ai-agents.git
cd moon-dev-ai-agents
pip install -r requirements.txt
```

### Run
```bash
streamlit run small_account_dashboard.py
```

Opens at `http://localhost:8501`

### On Your Phone
Open your Streamlit Cloud URL in Safari → Share → Add to Home Screen. Full-screen, no browser bar, works like an app.

---

## Key Files

| File | What it is |
|------|-----------|
| `small_account_dashboard.py` | The entire dashboard — 9 tabs, all UI |
| `small_account_helpers.py` | All data functions (IV rank, RS, squeeze, max pain, earnings, etc.) |
| `sheets_backend.py` | Google Sheets persistence (optional) |
| `requirements.txt` | Python dependencies |
| `src/data/small_account/trades.csv` | Your trade journal (auto-created) |
| `src/data/small_account/alerts.csv` | Your price alerts (auto-created) |

---

## GitHub Workflow

```bash
# Get latest
git pull origin main

# Save and push changes
git add -A
git commit -m "what you changed"
git push origin main
```

Your repo: `github.com/melFranklin-76/moon-dev-ai-agents`

Streamlit Cloud auto-deploys on every push — no extra steps.

---

## Trade Logging

**Option 1 — Webull CSV Import** (easiest):
1. Webull app → Account → Orders → Options → ↗ Export
2. Journal tab → "Import from Webull CSV" → upload file
3. App pairs all buy/sell legs and imports P&L automatically

**Option 2 — Manual log**:
Journal tab → "Log New Trade" → fill in ticker, entry, exit → P&L auto-calculates

---

## Price Alerts

Sidebar → 🔔 Price Alerts → enter ticker + target price + direction.

Triggers on every page refresh (auto-refresh every 60s). Fires:
- On-screen toast notification
- Push to your phone via [ntfy.sh](https://ntfy.sh) (free, no account)

---

## Push Notifications (iPhone)

1. Download **ntfy** app (free)
2. Sidebar → Push Notifications → enter any unique topic name (e.g. `scalper_mel`)
3. In the ntfy app, subscribe to the same topic
4. Done — signals and price alerts push to your phone

---

## Account Rules (Hard-Coded)

- Starting balance: $250
- Daily P&L goal: +$25 (+10%)
- Three red trades in one day → journal locks automatically
- Options window: 9:30 AM CT only (momentum fades after)
- Stop loss: -30% premium
- Take profit: +15% (half) / +25% (rest)

---

## What This Is NOT

- Not a bot — you execute all trades manually on Webull
- Not real-time — Yahoo Finance data is ~15 min delayed
- Not financial advice — this is a personal tool for tracking and preparation
- Not connected to Alpaca, crypto, or any of Moon Dev's original agents

---

## Strategy Reference

Strategies 159–178 are documented in the Trade Cards tab. The three active scanner strategies:

- **#163 VWAP Reclaim** — price crosses above VWAP with volume burst
- **#172 Whole-Dollar Break** — two consecutive closes above a whole number
- **#177 BTC Sync** — stock correlated to BTC shows same directional move

---

*Built with Streamlit + yfinance + plotly. Data from Yahoo Finance.*
