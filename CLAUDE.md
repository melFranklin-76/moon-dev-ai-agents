# CLAUDE.md — Project Instructions

This file tells Claude Code what this project is and how to work on it.

---

## What This Project Is

A personal options trading dashboard for a **$250 Webull cash account, Level 2** (buy calls/puts only). Built with Streamlit + yfinance. Not a crypto system, not a bot, not connected to Alpaca or any broker API for execution. The trader executes all trades manually on Webull.

**Owner:** Melvin Franklin, Milwaukee WI
**Repo:** github.com/melFranklin-76/moon-dev-ai-agents

---

## Key Files

| File | Purpose |
|------|---------|
| `small_account_dashboard.py` | Main app — all 9 tabs, all UI (~1,600+ lines) |
| `small_account_helpers.py` | All data functions — IV rank, RS vs SPY, squeeze, max pain, best buy strike, earnings, sector flow, signal strength |
| `sheets_backend.py` | Google Sheets persistence (optional) |
| `requirements.txt` | Python dependencies |

**Do not move or rename these files.**

---

## Architecture Rules

### Two-file pattern
- **Data functions** → `small_account_helpers.py` (decorated with `@st.cache_data`)
- **UI + rendering** → `small_account_dashboard.py`
- If a function fetches data from yfinance or does calculations, it goes in helpers
- If it renders HTML or Streamlit widgets, it goes in the dashboard

### Defensive imports
All v3.1+ helper functions are imported in a `try/except ImportError` block in the dashboard. Every new function added to helpers must also get a stub in the except block so version mismatches never crash the app:

```python
try:
    from small_account_helpers import (
        get_new_function,
        ...
    )
except ImportError:
    def get_new_function(symbol: str) -> dict: return {"available": False}
```

### Cache TTL guidelines
- Market prices: `ttl=60`
- Options chains: `ttl=300`
- Earnings dates: `ttl=3600`
- Float / short interest: `ttl=3600`

### Return dict pattern
Every helper function returns a dict with `"available": True/False` as the first key. The dashboard always checks `if result.get("available"):` before rendering.

---

## Session State

Key session state variables:

| Key | Type | Purpose |
|-----|------|---------|
| `watchlist` | list | Ticker symbols for today |
| `trades` | list | All trade records |
| `tendencies` | list | Coach tab entries |
| `account_balance` | float | Current balance |
| `daily_pnl` | float | Today's P&L |
| `daily_reds` | int | Red trades today (3 = locked) |
| `view_mode` | str | 'Simple' or 'Pro' |
| `ntfy_topic` | str | ntfy.sh push channel |
| `price_alerts` | list | Active price alerts |
| `auto_refresh` | bool | 60s auto-refresh toggle |

---

## Data Sources

**Yahoo Finance only** (via yfinance). No paid APIs. Data is ~15-min delayed.
Never add Alpaca, Tradier, Polygon, or Schwab API calls without asking first.
The user is aware of the delay — it is acceptable for a preparation tool.

---

## The 11 Tabs (ordered by daily workflow)

1. **Scan** — Universe scanner, gap scanner, #163/#172/#177 setup signals
2. **Market** — SPY/QQQ/IWM/VIX + sectors + intraday flow
3. **Catalyst** — SMB 5-check pre-market grading
4. **Tickers** — Watchlist cards with Simple/Pro toggle
5. **Entry** — Pre-flight decision gate before trade entry
6. **Options** — Trade plan + Black-Scholes P&L simulator
7. **Journal** — Trade log + Webull CSV import + auto stop alerts
8. **Stats** — 10-day challenge, equity curve, daily goal bar
9. **Plays** — Strategy reference for strategies 159–178
10. **Coach** — Tendencies log + pre-trade checklist
11. **IV Scan** — Multi-expiration IV surface fitting

---

## Simple vs Pro Mode

Toggled in sidebar. Affects Tab 2 (My Tickers) only.

- **Simple Mode:** Composite 0–10 signal score, star rating, one-line advice, compact layer detail, earnings bar. Built for phone screens.
- **Pro Mode:** All 5 individual insider-layer badges + earnings badge + options liquidity.

The `get_signal_strength(symbol)` function in helpers computes the composite score.

---

## Pro Mode Ticker Card Layers (in order)

1. RS vs SPY — `get_rs_vs_spy()`
2. IV Rank — `get_iv_rank()`
3. Squeeze Score — `get_squeeze_score()`
4. Max Pain — `get_max_pain()`
5. Best Buy Strike — `get_best_buy_strike()` (IV surface fitting)
6. Earnings Risk — `get_earnings_date()`
7. Options Liquidity — `get_options_snapshot()`

---

## Deployment

- **Local:** `streamlit run small_account_dashboard.py`
- **Cloud:** Streamlit Community Cloud, auto-deploys on git push
- **Mobile:** "Add to Home Screen" in Safari from the Streamlit Cloud URL

---

## Development Workflow

Use feature branches + pull requests. Never push directly to `main`.

```bash
# Syntax check before committing
python3 -m py_compile small_account_dashboard.py
python3 -m py_compile small_account_helpers.py

# Work on a feature branch
git checkout -b feature/my-change
git add small_account_dashboard.py small_account_helpers.py
git commit -m "description of change"
git push -u origin feature/my-change
# Then create a PR to main for review
```

Streamlit Community Cloud auto-deploys when PRs merge to `main`.

---

## What NOT to Do

- Do not add broker API execution — user trades manually on Webull
- Do not add crypto functionality — stock options dashboard only
- Do not move files without asking
- Do not add paid data source integrations without asking
- Do not use heavy ML libraries for simple calculations — `math` stdlib is sufficient
- Do not exceed ~800 lines per file — split into a new file if needed

---

## Account Context

- $250 starting balance, Webull cash account, Level 2 options
- Trading window: 8:30–9:00 AM CT (9:30–10:00 AM ET) — first 30 min after the open
- Stop loss: -30% premium (hard rule, no exceptions)
- Targets: +15% (half exit), +25% (full exit)
- Max risk per trade: 10–15% of account (1 contract only)
- 3 red trades in one day = journal locks automatically
- Long-term goal: $250 → $2,000, then Level 3 + XSP credit spreads
