#!/usr/bin/env python3
"""
Small Account Options Scalper Dashboard v3.0
$250 Account | Options Only | Webull | Cash Account

Tabs:
  1. Live Scanner      — #163 VWAP Reclaim · #172 Whole-Dollar · #177 BTC Sync
  2. My Tickers        — 6 live ticker cards with VWAP
  3. Trade Cards       — 20 best-of-the-best strategy reference
  4. Performance       — 10-day challenge tracker + equity curve
  5. Journal           — log every trade to CSV
  6. Market Regime     — SPY/QQQ/IWM/VIX + sectors + PDT countdown
  7. Catalyst Grader   — SMB 5-check pre-market grading system
  8. Options Planner   — directional calls + XSP put credit spreads
  9. Coach             — tendencies log + pre-trade checklist

Run:
  streamlit run small_account_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date
import os, csv
from pathlib import Path
from dotenv import load_dotenv
import yfinance as yf

from small_account_helpers import (
    get_regime_data, get_sector_data, get_xsp_data,
    load_tendencies as _load_tend_csv,
    save_tendency   as _save_tend_csv,
    scan_momentum_universe,
)
# v3.1+ helpers — defensive import so a version mismatch never crashes the app
try:
    from small_account_helpers import (
        get_options_snapshot,
        get_news,
        send_ntfy,
        scan_premarket_gaps,
        get_iv_rank,
    )
except ImportError:
    def get_options_snapshot(symbol: str) -> dict: return {"available": False}
    def get_news(symbol: str) -> list:             return []
    def send_ntfy(*a, **kw):                       pass
    def scan_premarket_gaps(*a, **kw) -> list:     return []
    def get_iv_rank(symbol: str) -> dict:          return {"available": False}
import sheets_backend as _sheets

load_dotenv()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="$250 Scalper Dashboard",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""<style>
    .main {background-color: #0e1117;}
    .stMetric {background-color: #1e2130; padding: 15px; border-radius: 10px;}
    .stMetric label {color: #8b92a8 !important; font-size: 14px !important;}
    .stMetric [data-testid="stMetricValue"] {color: #ffffff !important; font-size: 32px !important;}
    .green-box {background-color: #1a3d1a; padding: 15px; border-radius: 10px; border: 2px solid #2ecc71; margin-bottom: 12px;}
    .red-box {background-color: #3d1a1a; padding: 15px; border-radius: 10px; border: 2px solid #e74c3c; margin-bottom: 12px;}
    .yellow-box {background-color: #3d361a; padding: 15px; border-radius: 10px; border: 2px solid #f39c12; margin-bottom: 12px;}
    .trade-card {background-color: #1e2130; padding: 20px; border-radius: 10px; margin: 10px 0;}
    h1 {color: #2ecc71 !important;}
    h2 {color: #3498db !important;}
    h3 {color: #f39c12 !important;}
    .big-text {font-size: 40px; font-weight: bold; text-align: center;}
</style>""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
BTC_TICKER = "BTC-USD"
BTC_KEY_LEVELS = [60000, 65000, 70000, 72500, 75000, 80000, 85000, 90000, 95000, 100000]
PDT_CHANGE_DATE = date(2026, 6, 4)

# No hardcoded tickers — watchlist is managed dynamically in the sidebar

TRADES_FILE = Path(__file__).parent / "src" / "data" / "small_account" / "trades.csv"
TRADES_FILE.parent.mkdir(parents=True, exist_ok=True)
TRADE_FIELDS = ['date', 'ticker', 'strategy', 'side', 'entry', 'exit', 'pnl', 'result', 'notes']

ALL_STRATEGIES = [
    "159. 1-min ORB + VWAP Hold",         "160. 1-min ORB Fail → VWAP Reject",
    "161. 5-min OR Break + 1-min Flag",   "162. Premarket High Retest-and-Go",
    "163. VWAP Reclaim (Long)",            "164. VWAP Rejection (Short)",
    "165. VWAP Micro Double Bottom/Top",  "166. 9/20 EMA Pullback Long",
    "167. 9/20 EMA Pullback Short",       "168. Higher-Low / Lower-High",
    "169. Stop-Run Reclaim",              "170. Exhaustion Wick Reversal",
    "171. Bollinger Squeeze Release",     "172. Whole-Dollar Break-and-Hold",
    "173. Half-Dollar Rejection Fade",    "174. POC Reclaim/Loss",
    "175. LVN Slide",                     "176. Index-Lead Sync (SPY/QQQ)",
    "177. BTC-Lead Sync (MARA/CAN)",      "178. Golden-Hour Range Break",
]

# ── Persistence ───────────────────────────────────────────────────────────────
def load_trades() -> list:
    if _sheets.sheets_available():
        return _sheets.load_trades()
    if not TRADES_FILE.exists():
        return []
    try:
        return pd.read_csv(TRADES_FILE).to_dict('records')
    except Exception:
        return []

def save_trade(trade: dict):
    if _sheets.sheets_available():
        _sheets.save_trade(trade)
        return
    exists = TRADES_FILE.exists()
    with open(TRADES_FILE, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=TRADE_FIELDS)
        if not exists:
            w.writeheader()
        w.writerow({k: trade.get(k, '') for k in TRADE_FIELDS})

def load_tendencies() -> list:
    if _sheets.sheets_available():
        return _sheets.load_tendencies()
    return _load_tend_csv()

def save_tendency(text: str):
    if _sheets.sheets_available():
        _sheets.save_tendency(text)
    else:
        _save_tend_csv(text)

# ── Session State ─────────────────────────────────────────────────────────────
_trades_from_file = load_trades()
_total_pnl = sum(float(t.get('pnl', 0)) for t in _trades_from_file)
_starting_balance = 250.00
_computed_balance = round(_starting_balance + _total_pnl, 2)

# Today's trades only for daily_pnl
_today_str = date.today().isoformat()
_daily_pnl = sum(
    float(t.get('pnl', 0)) for t in _trades_from_file
    if str(t.get('date', '')).startswith(_today_str)
)

_daily_goal    = 25.0          # target daily P&L (+10% of $250)
_today_reds    = len([t for t in _trades_from_file
                      if str(t.get('date', '')).startswith(_today_str)
                      and t.get('result') == 'Red'])

defaults = {
    'trades':           _trades_from_file,
    'tendencies':       load_tendencies(),
    'challenge_days':   [0] * 10,
    'current_streak':   0,
    'account_balance':  _computed_balance,
    'starting_balance': _starting_balance,
    'daily_pnl':        round(_daily_pnl, 2),
    'daily_reds':       _today_reds,
    'watchlist':        [],
    'selected_ticker':  '',   # set when ➕ is clicked — auto-fills other tabs
    'ntfy_topic':       '',   # ntfy.sh push notification channel
    'news_cache':       {},   # {symbol: [headlines]} populated on ➕ click
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Always recalculate from file so stale session state can't corrupt it
st.session_state.account_balance = _computed_balance
st.session_state.daily_pnl       = round(_daily_pnl, 2)
st.session_state.daily_reds      = _today_reds

# ── Data Layer ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def get_bars(symbol: str) -> pd.DataFrame:
    try:
        df = yf.Ticker(symbol).history(period="1d", interval="1m")
        if df.empty:
            df = yf.Ticker(symbol).history(period="5d", interval="5m")
        df.index = pd.to_datetime(df.index)
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_btc_price() -> float:
    try:
        df = yf.Ticker(BTC_TICKER).history(period="1d", interval="1m")
        return float(df['Close'].iloc[-1]) if not df.empty else 0.0
    except Exception:
        return 0.0

@st.cache_data(ttl=60)
def get_btc_bars() -> pd.DataFrame:
    try:
        df = yf.Ticker(BTC_TICKER).history(period="1d", interval="1m")
        return df if not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def calc_vwap(df: pd.DataFrame) -> float:
    if df.empty or 'Volume' not in df.columns:
        return 0.0
    try:
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        return float((tp * df['Volume']).cumsum().iloc[-1] / df['Volume'].cumsum().iloc[-1])
    except Exception:
        return 0.0

def get_snapshot(symbol: str) -> dict:
    df = get_bars(symbol)
    if df.empty:
        return {"symbol": symbol, "price": 0, "change": 0, "volume": "N/A", "vwap": 0, "bars": df}
    price  = float(df['Close'].iloc[-1])
    open_p = float(df['Open'].iloc[0])
    change = ((price - open_p) / open_p) * 100 if open_p > 0 else 0
    vol    = df['Volume'].sum()
    vol_s  = f"{vol/1e6:.1f}M" if vol > 1e6 else f"{vol/1e3:.0f}K"
    return {"symbol": symbol, "price": price, "change": change,
            "volume": vol_s, "vwap": calc_vwap(df), "bars": df}

# ── Scanner Engine ────────────────────────────────────────────────────────────
def scan_163(snap: dict) -> dict | None:
    df, vwap = snap['bars'], snap['vwap']
    if df.empty or vwap == 0 or len(df) < 3:
        return None
    prev     = float(df['Close'].iloc[-2])
    curr     = float(df['Close'].iloc[-1])
    avg_vol  = float(df['Volume'].iloc[-10:].mean()) if len(df) >= 10 else float(df['Volume'].mean())
    curr_vol = float(df['Volume'].iloc[-1])
    if prev < vwap and curr > vwap and curr_vol > avg_vol * 1.2:
        return {
            "ticker": snap['symbol'], "strategy": "#163 VWAP Reclaim", "signal": "CALL",
            "strength": "🔥 ACTIVE",
            "trigger": f"Reclaimed VWAP ${vwap:.2f} with volume burst ({curr_vol/avg_vol:.1f}x avg)",
            "entry_note": f"Price ${curr:.2f} just crossed above VWAP ${vwap:.2f}",
            "stop": "Close back below VWAP OR -20% premium",
            "targets": "+15% (half), +25% (rest)",
        }
    return None

def scan_172(snap: dict) -> dict | None:
    df = snap['bars']
    if df.empty or len(df) < 4:
        return None
    price = snap['price']
    whole = int(price)
    c_2 = float(df['Close'].iloc[-3])
    c_1 = float(df['Close'].iloc[-2])
    c_0 = float(df['Close'].iloc[-1])
    if c_2 < whole and c_1 > whole and c_0 > whole:
        return {
            "ticker": snap['symbol'], "strategy": "#172 Whole-Dollar Break", "signal": "CALL",
            "strength": "🔥 ACTIVE",
            "trigger": f"Broke and held ${whole}.00 for 2 candles (${c_1:.2f}, ${c_0:.2f})",
            "entry_note": f"Buy call — 2 closes above ${whole}.00 confirmed",
            "stop": f"Back below ${whole}.00 OR -20% premium",
            "targets": "+15% (half), +25% (rest)",
        }
    if c_2 > whole and c_1 < whole and c_0 < whole:
        return {
            "ticker": snap['symbol'], "strategy": "#172 Whole-Dollar Break", "signal": "PUT",
            "strength": "🔥 ACTIVE",
            "trigger": f"Broke and held below ${whole}.00 for 2 candles (${c_1:.2f}, ${c_0:.2f})",
            "entry_note": f"Buy put — 2 closes below ${whole}.00 confirmed",
            "stop": f"Back above ${whole}.00 OR -20% premium",
            "targets": "+15% (half), +25% (rest)",
        }
    return None

def scan_177(snap: dict, btc_price: float) -> dict | None:
    if btc_price == 0:
        return None
    btc_df = get_btc_bars()
    if btc_df.empty or len(btc_df) < 2:
        return None
    btc_prev = float(btc_df['Close'].iloc[-2])
    btc_curr = float(btc_df['Close'].iloc[-1])
    broken, direction = None, None
    for lvl in BTC_KEY_LEVELS:
        if btc_prev < lvl < btc_curr:
            broken, direction = lvl, "UP"; break
        if btc_prev > lvl > btc_curr:
            broken, direction = lvl, "DOWN"; break
    if not broken:
        return None
    vwap, price = snap['vwap'], snap['price']
    confirmed = (direction == "UP" and price > vwap) or (direction == "DOWN" and price < vwap)
    if confirmed:
        signal = "CALL" if direction == "UP" else "PUT"
        arrow  = "↑" if direction == "UP" else "↓"
        side   = "above" if direction == "UP" else "below"
        return {
            "ticker": snap['symbol'], "strategy": "#177 BTC-Lead Sync", "signal": signal,
            "strength": "🔥 ACTIVE",
            "trigger": f"BTC broke ${broken:,} {arrow} — {snap['symbol']} confirmed {side} VWAP",
            "entry_note": f"{snap['symbol']} ${price:.2f} {side} VWAP ${vwap:.2f}",
            "stop": f"{snap['symbol']} {'loses' if direction=='UP' else 'reclaims'} VWAP OR -20% premium",
            "targets": "+15% (half), +25% (rest)",
        }
    return None

def run_scanner(snapshots: dict, btc_price: float) -> list:
    signals = []
    for snap in snapshots.values():
        for fn in (scan_163, scan_172):
            r = fn(snap)
            if r:
                signals.append(r)
        r = scan_177(snap, btc_price)
        if r:
            signals.append(r)
    return signals

# ── Alpaca ────────────────────────────────────────────────────────────────────
def get_alpaca():
    try:
        import alpaca_trade_api as tradeapi
        key    = os.getenv('ALPACA_API_KEY')
        secret = os.getenv('ALPACA_SECRET_KEY')
        url    = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        if not key or not secret:
            return None
        return tradeapi.REST(key, secret, url, api_version='v2')
    except Exception:
        return None

# ── Load Market Data ──────────────────────────────────────────────────────────
_watchlist = st.session_state.get('watchlist', [])
with st.spinner("Loading market data..."):
    btc_price    = get_btc_price()
    snapshots    = {sym: get_snapshot(sym) for sym in _watchlist}
    last_updated = datetime.now().strftime('%H:%M:%S')

# ── Header ────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.markdown("# 🌙 SMALL ACCOUNT SCALPER")
    st.markdown("### $250 Challenge | Options Only | Webull")

# Account level + progress bar
lc1, lc2, lc3 = st.columns([1, 2, 1])
with lc2:
    balance = st.session_state.account_balance
    goal    = 2000.0
    pct_to_goal = min(balance / goal, 1.0)
    st.markdown(f"""
    <div style="background:#1e2130; border-radius:10px; padding:14px; text-align:center; margin-bottom:8px;">
      <span style="color:#f39c12; font-size:18px; font-weight:bold;">
        ✅ Webull Level 2 &nbsp;|&nbsp; Cash Account &nbsp;|&nbsp; Buy Calls &amp; Puts Only
      </span><br>
      <span style="color:#8b92a8; font-size:13px;">
        Level 3 (credit spreads) unlocks at <strong style="color:#2ecc71;">$2,000 margin account</strong>
      </span>
    </div>
    """, unsafe_allow_html=True)
    st.progress(pct_to_goal, text=f"Path to Level 3: ${balance:.0f} / $2,000  ({pct_to_goal*100:.0f}%)")

st.markdown("---")

# ── Top Stats Bar ─────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
open_pos = len([t for t in st.session_state.trades if t.get('status') == 'open'])

with c1: st.metric("💰 Account",    f"${st.session_state.account_balance:.2f}")
with c2:
    pnl = st.session_state.daily_pnl
    pct = (pnl / st.session_state.account_balance * 100) if st.session_state.account_balance else 0
    st.metric("📈 Today P/L", f"{'🟢' if pnl >= 0 else '🔴'} ${pnl:.2f}", f"{pct:.1f}%")
with c3: st.metric("🎯 Challenge",  f"Day {st.session_state.current_streak}/10")
with c4: st.metric("📦 Open",       str(open_pos))
with c5: st.metric("💵 Buying Pwr", f"${st.session_state.account_balance - open_pos * 80:.2f}")
with c6: st.metric("₿ BTC",         f"${btc_price:,.0f}" if btc_price else "N/A")

st.caption(f"Data via yfinance (15-min delayed during market hours) — refreshed {last_updated}")

# ── Daily P&L Goal Bar ────────────────────────────────────────────────────────
_dpnl      = st.session_state.daily_pnl
_goal_pct  = min(max(_dpnl / _daily_goal, 0), 1.0)
_reds_now  = st.session_state.daily_reds
if _reds_now >= 3:
    _goal_color = "#e74c3c"
    _goal_msg   = f"🛑 THREE STRIKES — Stop trading for today! ({_reds_now} red trades)"
elif _dpnl < 0:
    _goal_color = "#e74c3c"
    _goal_msg   = f"📉 Today: ${_dpnl:+.2f}  |  Goal: +${_daily_goal:.0f}  |  {_reds_now}/3 red trades"
elif _dpnl >= _daily_goal:
    _goal_color = "#2ecc71"
    _goal_msg   = f"🎯 GOAL HIT! +${_dpnl:.2f}  |  Consider locking in and stepping away."
else:
    _goal_color = "#f39c12"
    _goal_msg   = f"📈 Today: ${_dpnl:+.2f} / +${_daily_goal:.0f} goal  |  {_reds_now}/3 red trades"

_goal_bar_html = f"""
<div style="background:#1e2130; border-radius:8px; padding:8px 14px; margin:4px 0 10px 0;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
    <span style="color:{_goal_color}; font-weight:bold;">{_goal_msg}</span>
    <span style="color:#8b92a8; font-size:12px;">${_dpnl:+.2f} / +${_daily_goal:.0f}</span>
  </div>
  <div style="background:#0e1117; border-radius:4px; height:8px; overflow:hidden;">
    <div style="background:{_goal_color}; width:{_goal_pct*100:.0f}%; height:8px; border-radius:4px;"></div>
  </div>
</div>"""
st.markdown(_goal_bar_html, unsafe_allow_html=True)
st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "🎯 Live Scanner",
    "📊 My Tickers",
    "🎴 Trade Cards",
    "📈 Performance",
    "📝 Journal",
    "🌡️ Market Regime",
    "🔍 Catalyst Grader",
    "💰 Options Planner",
    "🧠 Coach",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1  LIVE SCANNER
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("## 🟢 LIVE SETUP SCANNER")

    # ── Universe Scanner ──────────────────────────────────────────────────────
    st.markdown("### 🔭 Find Today's Optionable Movers")
    st.caption("Scans Yahoo Finance day gainers + most actives. Filters by your criteria. Flags which ones have options.")

    with st.expander("⚙️ Scanner Filters", expanded=False):
        fc1, fc2, fc3, fc4 = st.columns(4)
        f_min_price  = fc1.number_input("Min Price ($)",   value=2.0,   step=0.5,  min_value=0.5)
        f_max_price  = fc2.number_input("Max Price ($)",   value=100.0, step=5.0,  min_value=1.0)
        f_min_change = fc3.number_input("Min Change (%)",  value=3.0,   step=0.5,  min_value=0.5)
        f_min_relvol = fc4.number_input("Min Rel Vol (x)", value=2.0,   step=0.5,  min_value=0.5)

    scan_col, info_col = st.columns([1, 3])
    run_scan = scan_col.button("🚀 Scan Universe Now", type="primary", use_container_width=True)
    info_col.caption("Takes ~20–30 seconds. Results cached 5 min. Checks ALL Yahoo Finance movers — nothing slips through.")

    if run_scan:
        with st.spinner("Scanning universe... checking options availability..."):
            universe = scan_momentum_universe(
                min_price=f_min_price,
                max_price=f_max_price,
                min_change=f_min_change,
                min_rel_vol=f_min_relvol,
            )
        st.session_state['_last_universe'] = universe

    universe = st.session_state.get('_last_universe', [])

    if universe:
        st.markdown(f"**{len(universe)} stocks meet criteria** — click ➕ to add to watchlist · always verify options chain on Webull before trading")
        st.caption("⚠️ Confirm open interest > 200 and bid/ask spread < 10% on Webull before entering any trade.")

        for r in universe:
            rc1, rc2, rc3, rc4, rc5, rc6 = st.columns([1, 2, 1, 1, 1, 1])
            rc1.markdown(f"**{r['symbol']}**")
            rc2.markdown(f"<small>{r['name'][:28]}</small>", unsafe_allow_html=True)
            rc3.markdown(f"**${r['price']:.2f}**")
            rc4.markdown(f"<span style='color:#2ecc71'>+{r['change']:.1f}%</span>", unsafe_allow_html=True)
            rc5.markdown(f"{r['rel_vol']:.1f}x vol")
            if rc6.button("➕", key=f"add_uni_{r['symbol']}"):
                if r['symbol'] not in st.session_state.watchlist:
                    st.session_state.watchlist.append(r['symbol'])
                st.session_state.selected_ticker = r['symbol']
                # Auto-fetch news for the selected ticker
                st.session_state.news_cache[r['symbol']] = get_news(r['symbol'])
                st.cache_data.clear()
                st.rerun()
    elif not run_scan:
        st.info("Hit **Scan Universe Now** to find today's optionable movers. Do this each morning after 8:30 AM CT.")

    # ── News for selected ticker ──────────────────────────────────────────────
    _sel        = st.session_state.get('selected_ticker', '')
    _news_cache = st.session_state.get('news_cache', {})
    if _sel:
        _headlines = _news_cache.get(_sel, [])
        if _headlines:
            st.markdown(f"#### 📰 Latest News: **{_sel}**")
            for n in _headlines:
                st.markdown(f"- [{n['title']}]({n['link']}) — *{n['publisher']}* `{n['time']}`")
        else:
            if st.button(f"📰 Load News for {_sel}", key="fetch_news_btn"):
                st.session_state.news_cache[_sel] = get_news(_sel)
                st.rerun()

    # ── Pre-Market Gap Scanner ────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("🌅 Pre-Market Gap Scanner (open before 8:30 AM CT)", expanded=False):
        st.caption("Finds stocks with significant overnight gaps — prime candidates for ORB setups at open.")
        gc1, gc2, gc3 = st.columns(3)
        g_min_gap   = gc1.number_input("Min Gap (%)",   value=3.0,  step=0.5, min_value=1.0, key="gap_pct")
        g_min_price = gc2.number_input("Min Price ($)", value=2.0,  step=0.5, min_value=0.5, key="gap_minp")
        g_max_price = gc3.number_input("Max Price ($)", value=100.0, step=5.0, min_value=1.0, key="gap_maxp")
        if st.button("🔍 Scan Pre-Market Gaps", key="gap_scan_btn"):
            with st.spinner("Scanning for gap stocks..."):
                gaps = scan_premarket_gaps(g_min_gap, g_min_price, g_max_price)
            st.session_state['_last_gaps'] = gaps

        gaps = st.session_state.get('_last_gaps', [])
        if gaps:
            st.markdown(f"**{len(gaps)} gap stocks found** — click ➕ to add to watchlist")
            for g in gaps:
                gdir   = "🟢 Gap UP" if g['gap_pct'] > 0 else "🔴 Gap DOWN"
                color  = "#2ecc71" if g['gap_pct'] > 0 else "#e74c3c"
                ga1, ga2, ga3, ga4, ga5, ga6 = st.columns([1, 2, 1, 1, 1, 1])
                ga1.markdown(f"**{g['symbol']}**")
                ga2.markdown(f"<small>{g['name'][:28]}</small>", unsafe_allow_html=True)
                ga3.markdown(f"${g['gap_price']:.2f}")
                ga4.markdown(f"prev ${g['prev_close']:.2f}")
                ga5.markdown(f"<span style='color:{color}'>{g['gap_pct']:+.1f}%</span>", unsafe_allow_html=True)
                if ga6.button("➕", key=f"add_gap_{g['symbol']}"):
                    if g['symbol'] not in st.session_state.watchlist:
                        st.session_state.watchlist.append(g['symbol'])
                    st.session_state.selected_ticker = g['symbol']
                    st.session_state.news_cache[g['symbol']] = get_news(g['symbol'])
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.info("Click **Scan Pre-Market Gaps** to find overnight gap stocks.")

    st.markdown("### 🎯 Setup Signals (Your Watchlist)")
    st.caption("Signals fire on #163 VWAP Reclaim · #172 Whole-Dollar · #177 BTC Sync across tickers you've added above.")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Active Setups")
        signals = run_scanner(snapshots, btc_price)
        # Fire push notifications for new signals
        _ntfy_topic = st.session_state.get('ntfy_topic', '')
        if signals and _ntfy_topic:
            for sig in signals:
                send_ntfy(
                    _ntfy_topic,
                    f"🔥 {sig['ticker']} — {sig['strategy']}",
                    f"{sig['signal']} | {sig['trigger']} | Entry: {sig['entry_note']}",
                )
        if signals:
            for sig in signals:
                box = "green-box" if sig['signal'] == "CALL" else "red-box"
                st.markdown(f"""
                <div class="{box}">
                <h3>${sig['ticker']} — {sig['strategy']} {sig['strength']}</h3>
                <p><strong>Signal:</strong> {sig['signal']}</p>
                <p><strong>Trigger:</strong> {sig['trigger']}</p>
                <p><strong>Entry:</strong> {sig['entry_note']}</p>
                <p><strong>Stop:</strong> {sig['stop']}</p>
                <p><strong>Targets:</strong> {sig['targets']}</p>
                </div>
                """, unsafe_allow_html=True)
        elif not _watchlist:
            st.markdown("""
            <div class="yellow-box">
            <h3>📋 Watchlist Empty</h3>
            <p>Scan the universe above → click ➕ on any optionable stock → signals will appear here.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="yellow-box">
            <h3>⏳ No Active Setups Right Now</h3>
            <p>Watching your tickers — no confirmed signals yet.<br>
            <strong>Patience is a position.</strong></p>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("#### Pre-Market Checklist")
        checklist = [
            "Mark PM High/Low",
            "Mark Prior Day High/Low/Close",
            "Check BTC price (if watching BTC-correlated stocks)",
            "Check earnings calendar",
            "Define Opening Range (wait 5 min after open)",
            "Plot VWAP",
            "Check Level 2 liquidity",
            "ONE setup only today ⚠️",
        ]
        for i, item in enumerate(checklist):
            st.checkbox(item, key=f"chk_{i}")

        st.markdown("---")
        st.markdown("### ⚠️ Risk Management")
        remaining = 50 + st.session_state.daily_pnl
        rm_box = "green-box" if remaining > 25 else "red-box"
        st.markdown(f"""
        <div class="{rm_box}">
        <p><strong>Max Loss Today:</strong> $50 (20% of account)</p>
        <p><strong>Today's P/L:</strong> ${st.session_state.daily_pnl:.2f}</p>
        <p><strong>Remaining Risk:</strong> ${remaining:.2f} {'🟢' if remaining > 25 else '🔴 NEAR LIMIT'}</p>
        <hr>
        <p><strong>Max Position Size:</strong> $80 (1 contract)</p>
        <p><strong>STOP TRADING at -$50!</strong> ⛔</p>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2  MY TICKERS
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("## 📊 TODAY'S WATCHLIST")
    st.caption(f"Live prices | Updated {last_updated} | Add tickers via sidebar")

    if not _watchlist:
        st.markdown("""
        <div class="yellow-box">
        <h3>📋 Your watchlist is empty</h3>
        <p><strong>How to use this tab:</strong></p>
        <ol>
          <li>Run your Finviz / TradingView screener (3%+ gain, 2x vol, catalyst)</li>
          <li>Add qualifying tickers in the <strong>sidebar → Today's Watchlist</strong></li>
          <li>Live prices, VWAP position, and setup signals will appear here</li>
        </ol>
        <p>Clear the watchlist each morning and start fresh with that day's movers.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        cols = st.columns(min(len(_watchlist), 3))
        for i, sym in enumerate(_watchlist):
            snap  = snapshots.get(sym, {"symbol": sym, "price": 0, "change": 0, "volume": "N/A", "vwap": 0, "bars": pd.DataFrame()})
            color = "#2ecc71" if snap['change'] > 0 else "#e74c3c"
            icon  = "🟢" if snap['change'] > 0 else "🔴"
            vwap  = snap['vwap']
            price = snap['price']
            if vwap > 0:
                vwap_label = f"↑ ABOVE VWAP (+${price-vwap:.2f})" if price > vwap else f"↓ BELOW VWAP (-${vwap-price:.2f})"
            else:
                vwap_label = "VWAP N/A"

            with cols[i % 3]:
                # Options liquidity check
                opt = get_options_snapshot(sym)
                if opt.get("available"):
                    liq_rows = opt["calls"][:2]
                    liq_lines = ""
                    for row in liq_rows:
                        badge = "✅" if row["liquid"] else "❌"
                        liq_lines += (
                            f"<p style='margin:2px 0;'>{badge} ${row['strike']:.0f} call "
                            f"OI:{row['oi']} spread:{row['spread_pct']:.0f}%</p>"
                        )
                    liq_html = f"<p><strong>Options ({opt['expiry']}):</strong></p>{liq_lines}"
                else:
                    liq_html = "<p style='color:#8b92a8;'><small>Options data N/A</small></p>"

                # IV Rank badge
                iv = get_iv_rank(sym)
                if iv.get("available"):
                    iv_html = (
                        f"<p style='margin:4px 0;'>"
                        f"<span style='background:{iv['color']}22; color:{iv['color']}; "
                        f"border:1px solid {iv['color']}; border-radius:5px; "
                        f"padding:2px 8px; font-weight:bold; font-size:13px;'>"
                        f"{iv['emoji']} IV {iv['grade']} &nbsp;|&nbsp; "
                        f"IV:{iv['current_iv']}% &nbsp; HV20:{iv['hv20']}% &nbsp; "
                        f"Rank:{iv['iv_rank']:.0f}</span></p>"
                        f"<p style='color:#8b92a8; font-size:11px; margin:2px 0;'>"
                        f"{iv['advice']}</p>"
                    )
                else:
                    iv_html = "<p style='color:#8b92a8;'><small>IV data loading…</small></p>"

                st.markdown(f"""
                <div class="trade-card">
                <h2>${sym}</h2>
                <p class="big-text" style="color:{color};">${price:.2f}</p>
                <p>{icon} {snap['change']:+.1f}% | Vol: {snap['volume']}</p>
                <p><strong>VWAP:</strong> ${vwap:.2f} &nbsp;<em>{vwap_label}</em></p>
                <hr>
                {iv_html}
                <hr>
                {liq_html}
                <p><strong>Strategies:</strong> #163 VWAP · #172 Whole-$ · #177 BTC-sync</p>
                </div>
                """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3  TRADE CARDS
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("## 🎴 YOUR 20 BEST-OF-THE-BEST")
    st.markdown("*Strategies 159–178 | Refined from 178 total*")

    strategy_groups = {
        "🚀 Momentum + Confirmation (159-162)":   ALL_STRATEGIES[0:4],
        "💧 VWAP Edge (163-165)":                 ALL_STRATEGIES[4:7],
        "📈 Pullback Continuations (166-168)":    ALL_STRATEGIES[7:10],
        "🔄 Reversal / Mean-Reversion (169-171)": ALL_STRATEGIES[10:13],
        "💰 Price Levels & Auction (172-175)":    ALL_STRATEGIES[13:17],
        "🔗 Correlation (176-177)":               ALL_STRATEGIES[17:19],
        "⏰ Time-of-Day (178)":                   ALL_STRATEGIES[19:],
    }
    for cat, strats in strategy_groups.items():
        with st.expander(cat, expanded=False):
            for s in strats:
                st.markdown(f"- {s}")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4  PERFORMANCE
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("## 📈 10-DAY CHALLENGE TRACKER")

    c_left, c_right = st.columns([2, 1])

    with c_left:
        icons   = {1: "✅", -1: "❌", 0: "⬜"}
        day_row = " ".join(icons[d] for d in st.session_state.challenge_days)
        streak  = st.session_state.current_streak
        st.markdown(f"""
        <div class="green-box">
        <h2>🏆 10-Day Prove-It Challenge</h2>
        <p style="font-size:32px; text-align:center;">{day_row}</p>
        <p><strong>Streak:</strong> {streak} days 🔥 &nbsp;&nbsp;
           <strong>Status:</strong> {'ON TRACK! 🎯' if streak >= 3 else 'KEEP GOING!'}</p>
        <p style="color:#f39c12;">⚠️ One red day resets counter to 0!</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Equity Curve")
        trades = st.session_state.trades
        if trades:
            df_eq = pd.DataFrame(trades)
            df_eq['pnl']  = pd.to_numeric(df_eq['pnl'], errors='coerce').fillna(0)
            df_eq['date'] = pd.to_datetime(df_eq['date'], errors='coerce')
            df_eq = df_eq.sort_values('date')
            df_eq['equity'] = 250 + df_eq['pnl'].cumsum()
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_eq['date'], y=df_eq['equity'],
                mode='lines+markers', name='Account Value',
                line=dict(color='#2ecc71', width=3)
            ))
            fig.update_layout(template='plotly_dark', height=300,
                              margin=dict(l=20, r=20, t=20, b=20),
                              xaxis_title="Date", yaxis_title="Account Value ($)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Log trades to see your equity curve.")

    with c_right:
        today_str = date.today().isoformat()
        today_tr  = [t for t in st.session_state.trades if str(t.get('date',''))[:10] == today_str]
        wins_t    = len([t for t in today_tr if t.get('result') == 'Green'])

        st.markdown("### Today's Stats")
        st.metric("Trades",   str(len(today_tr)))
        st.metric("Win Rate", f"{wins_t/len(today_tr)*100:.0f}%" if today_tr else "N/A")
        if today_tr:
            pnls = [float(t.get('pnl', 0)) for t in today_tr]
            st.metric("Best",  f"+${max(pnls):.2f}")
            st.metric("Worst", f"${min(pnls):.2f}")

        st.markdown("### All-Time")
        all_tr   = st.session_state.trades
        all_wins = len([t for t in all_tr if t.get('result') == 'Green'])
        st.metric("Total Trades", str(len(all_tr)))
        st.metric("Win Rate", f"{all_wins/len(all_tr)*100:.0f}%" if all_tr else "N/A")
        if all_tr:
            all_pnl = sum(float(t.get('pnl', 0)) for t in all_tr)
            st.metric("Total P/L", f"${all_pnl:.2f}")

    # ── Performance Analytics ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 Strategy & Time Analytics")
    all_tr = st.session_state.trades
    if len(all_tr) >= 3:
        df_a = pd.DataFrame(all_tr)
        df_a['pnl']    = pd.to_numeric(df_a['pnl'], errors='coerce').fillna(0)
        df_a['date']   = pd.to_datetime(df_a['date'], errors='coerce')
        df_a['win']    = df_a['result'] == 'Green'
        df_a['dow']    = df_a['date'].dt.strftime('%a')   # Mon Tue etc
        df_a['hour']   = df_a['date'].dt.hour

        ana_col1, ana_col2, ana_col3 = st.columns(3)

        # Win rate by strategy (top 8)
        with ana_col1:
            st.markdown("**Win Rate by Strategy**")
            strat_g = (df_a.groupby('strategy')
                       .agg(trades=('win','count'), wins=('win','sum'), pnl=('pnl','sum'))
                       .reset_index())
            strat_g['win_rate'] = strat_g['wins'] / strat_g['trades'] * 100
            strat_g = strat_g.sort_values('win_rate', ascending=False).head(8)
            strat_g['label'] = strat_g['strategy'].str[:20]
            fig_s = go.Figure(go.Bar(
                x=strat_g['win_rate'], y=strat_g['label'],
                orientation='h',
                marker_color=['#2ecc71' if w >= 50 else '#e74c3c' for w in strat_g['win_rate']],
                text=[f"{w:.0f}% ({t})" for w, t in zip(strat_g['win_rate'], strat_g['trades'])],
                textposition='outside',
            ))
            fig_s.update_layout(template='plotly_dark', height=280,
                                margin=dict(l=10,r=30,t=10,b=10),
                                xaxis=dict(range=[0, 110], title="Win %"))
            st.plotly_chart(fig_s, use_container_width=True)

        # Win rate by day of week
        with ana_col2:
            st.markdown("**Win Rate by Day**")
            dow_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
            dow_g = (df_a.groupby('dow')
                     .agg(trades=('win','count'), wins=('win','sum'))
                     .reindex(dow_order).reset_index())
            dow_g['win_rate'] = dow_g['wins'] / dow_g['trades'] * 100
            fig_d = go.Figure(go.Bar(
                x=dow_g['dow'], y=dow_g['win_rate'],
                marker_color=['#2ecc71' if (w >= 50 if not pd.isna(w) else False) else '#e74c3c'
                              for w in dow_g['win_rate']],
                text=[f"{w:.0f}%" if not pd.isna(w) else "" for w in dow_g['win_rate']],
                textposition='outside',
            ))
            fig_d.update_layout(template='plotly_dark', height=280,
                                margin=dict(l=10,r=10,t=10,b=10),
                                yaxis=dict(range=[0, 110], title="Win %"))
            st.plotly_chart(fig_d, use_container_width=True)

        # P&L distribution
        with ana_col3:
            st.markdown("**P&L Distribution**")
            fig_p = go.Figure(go.Histogram(
                x=df_a['pnl'],
                marker_color='#3498db',
                nbinsx=15,
            ))
            fig_p.add_vline(x=0, line_color='#e74c3c', line_dash='dash')
            fig_p.update_layout(template='plotly_dark', height=280,
                                margin=dict(l=10,r=10,t=10,b=10),
                                xaxis_title="P&L ($)", yaxis_title="# trades")
            st.plotly_chart(fig_p, use_container_width=True)
    else:
        st.info("Log at least 3 trades to unlock analytics — strategy win rates, best days, P&L distribution.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5  JOURNAL
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.markdown("## 📝 TRADE JOURNAL")
    st.markdown("*Log every trade — wins and losses*")

    # ── Three-Strike Auto-Block ───────────────────────────────────────────────
    _reds_today = st.session_state.daily_reds
    _blocked    = _reds_today >= 3
    if _blocked:
        st.markdown("""
        <div class="red-box">
        <h2>🛑 THREE STRIKES — JOURNAL LOCKED FOR TODAY</h2>
        <p>You've had <strong>3 red trades</strong> today. The rules are clear: <strong>STOP TRADING.</strong></p>
        <p>No more setups today. Close your charts. Review your tendencies. Come back tomorrow fresh.</p>
        <p style="color:#f39c12;"><em>"The best trade is sometimes no trade." — every pro trader ever</em></p>
        </div>
        """, unsafe_allow_html=True)
    elif _reds_today > 0:
        st.markdown(
            f'<div class="yellow-box"><p>⚠️ <strong>{_reds_today}/3 red trades today.</strong> '
            f'One more red trade locks the journal. Trade only A+ setups now.</p></div>',
            unsafe_allow_html=True
        )

    with st.expander("➕ Log New Trade", expanded=False and not _blocked):
        c1, c2 = st.columns(2)
        with c1:
            ticker_sel   = st.text_input("Ticker", value=st.session_state.get('selected_ticker', ''), placeholder="e.g. NVDA", key="journal_ticker").upper().strip()
            strategy_sel = st.selectbox("Strategy", ALL_STRATEGIES)
            side_sel     = st.radio("Side", ["Call", "Put"])
            entry_p      = st.number_input("Entry Price ($)", value=0.66, step=0.01, min_value=0.01)
        with c2:
            exit_p  = st.number_input("Exit Price ($)", value=0.82, step=0.01, min_value=0.01)
            pnl_val = round((exit_p - entry_p) * 100, 2)
            st.metric("P/L This Trade", f"${pnl_val:+.2f}")
            result_sel = st.radio("Result", ["Green", "Flat", "Red"])
            notes_val  = st.text_area("Notes", placeholder="What did you see? Why enter? How did it feel?")

        if st.button("💾 Save Trade", type="primary", disabled=_blocked):
            trade = {
                'date': datetime.now().isoformat(), 'ticker': ticker_sel,
                'strategy': strategy_sel, 'side': side_sel,
                'entry': entry_p, 'exit': exit_p, 'pnl': pnl_val,
                'result': result_sel, 'notes': notes_val,
            }
            st.session_state.trades.append(trade)
            save_trade(trade)
            st.success(f"Trade logged! P/L: ${pnl_val:+.2f}")
            st.rerun()  # recalculates balance from CSV on next load

    st.markdown("### Trade History")
    if st.session_state.trades:
        df_j = pd.DataFrame(st.session_state.trades)
        show = [c for c in TRADE_FIELDS if c in df_j.columns]
        st.dataframe(df_j[show], use_container_width=True)
        st.download_button(
            "📥 Export to CSV",
            df_j.to_csv(index=False),
            f"trades_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )
    else:
        st.info("No trades logged yet. Start trading and log your first trade!")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6  MARKET REGIME
# ─────────────────────────────────────────────────────────────────────────────
with tab6:
    st.markdown("## 🌡️ MARKET REGIME")
    st.markdown("*Check this first — it determines which strategy mode to use*")

    regime  = get_regime_data()
    sectors = get_sector_data()

    # Index cards
    col_spy, col_qqq, col_iwm, col_vix = st.columns(4)
    index_map = [
        (col_spy, 'SPY',  'S&P 500'),
        (col_qqq, 'QQQ',  'Nasdaq'),
        (col_iwm, 'IWM',  'Russell 2K'),
        (col_vix, '^VIX', 'VIX'),
    ]
    for col, sym, label in index_map:
        d = regime.get(sym, {})
        with col:
            if d:
                color    = "#2ecc71" if d['change'] > 0 else "#e74c3c"
                ma_icon  = "✅ above 20MA" if d.get('above_ma') else "❌ below 20MA"
                # VIX: invert color logic (high VIX = bad)
                if sym == '^VIX':
                    color   = "#e74c3c" if d['price'] > 25 else "#2ecc71"
                    ma_icon = f"VIX {'🔴 ELEVATED' if d['price'] > 25 else '🟢 CALM'}"
                st.markdown(f"""
                <div class="trade-card">
                <h3>{label}</h3>
                <p style="font-size:26px; color:{color}; font-weight:bold;">${d['price']:.2f}</p>
                <p style="color:{color};">{d['change']:+.2f}%</p>
                <p><small>{ma_icon}</small></p>
                </div>""", unsafe_allow_html=True)
            else:
                with col:
                    st.markdown(f'<div class="trade-card"><h3>{label}</h3><p>Loading…</p></div>', unsafe_allow_html=True)

    # Regime determination
    spy_d  = regime.get('SPY', {})
    qqq_d  = regime.get('QQQ', {})
    vix_d  = regime.get('^VIX', {})
    vix_px = vix_d.get('price', 25)
    above  = sum(1 for x in [spy_d, qqq_d] if x.get('above_ma'))

    if above == 2 and vix_px < 25:
        rlabel, rbox = "🟢 MOMENTUM FAVORABLE — Full strategy active. A+ and A setups.", "green-box"
    elif above >= 1 or vix_px < 30:
        rlabel, rbox = "🟡 MIXED CONDITIONS — A+ setups only. Reduce size. Skip B-grades.", "yellow-box"
    else:
        rlabel, rbox = "🔴 DEFENSIVE MODE — A+ setups only or sit on hands. Wait for better conditions.", "red-box"

    st.markdown(f'<div class="{rbox}" style="margin-top:16px;"><h3>{rlabel}</h3></div>', unsafe_allow_html=True)

    # Sectors
    st.markdown("### Sector Performance Today")
    if sectors:
        scols = st.columns(len(sectors))
        for col, (sym, d) in zip(scols, sectors.items()):
            color = "#2ecc71" if d['change'] > 0 else "#e74c3c"
            with col:
                st.markdown(f"""
                <div class="trade-card" style="text-align:center; padding:10px;">
                <strong>{sym}</strong><br>
                <small>{d['name']}</small><br>
                <span style="color:{color}; font-size:20px; font-weight:bold;">{d['change']:+.1f}%</span>
                </div>""", unsafe_allow_html=True)
    else:
        st.info("Sector data loading…")

    # Hot sectors note
    st.markdown("---")
    st.markdown("""**Current Hot Themes (May 2026):**
    🟢 AI Infrastructure · Edge Computing · Healthcare/GLP-1 · Energy/Industrials · Defense/Copper
    🔴 Avoid: Enterprise SaaS (AI disruption risk) · Consumer Discretionary""")

    # PDT countdown
    pdt_days = (PDT_CHANGE_DATE - date.today()).days
    st.markdown("---")
    if pdt_days > 0:
        st.info(f"⏳ **PDT Rule Change in {pdt_days} days** (June 4, 2026) — $25k minimum eliminated, replaced with $2k intraday margin requirement. Cash accounts (like your $250) were never subject to PDT anyway — your limit is T+1 settlement.")
    else:
        st.success("✅ PDT Rule Changed — No more day trade counting on margin accounts.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 7  CATALYST GRADER
# ─────────────────────────────────────────────────────────────────────────────
with tab7:
    st.markdown("## 🔍 PRE-MARKET CATALYST GRADER")
    st.markdown("*SMB 5-check system — run this before every catalyst play*")

    c_left, c_right = st.columns([1, 1])

    with c_left:
        ticker_g = st.text_input("Ticker Symbol", value=st.session_state.get('selected_ticker', ''), placeholder="e.g. FSLY", key="grader_ticker").upper().strip()

        st.markdown("#### 5 Checks in Favor")
        ch1 = st.checkbox("1. Pre-market % AVOL > 20%  *(extended hours vol ÷ 30-day avg daily vol)*")
        ch2 = st.checkbox("2. Inflection quarter  *(first clean profitable beat + accelerating revenue YoY)*")
        ch3 = st.checkbox("3. Higher timeframe chart  *(base breakout, room to run, not extended)*")

        theme_sel = st.selectbox("4. Theme alignment", [
            "✅ AI Infrastructure / Edge Computing",
            "✅ Healthcare / GLP-1 / Biotech",
            "✅ Energy / Industrials / Defense",
            "✅ Copper / Data Centers / Power",
            "⚠️ Neutral / Other",
            "❌ Enterprise SaaS / Software (AI disruption risk)",
            "❌ Consumer Discretionary",
        ])
        ch4 = not theme_sel.startswith("❌")

        ch5 = st.checkbox("5. Market environment supports breakouts  *(check Regime tab — green or yellow?)*")

        checks = [ch1, ch2, ch3, ch4, ch5]
        score  = sum(checks)

        st.markdown(f"**Checks confirmed: {score} / 5**")

    with c_right:
        if ticker_g:
            snap  = get_snapshot(ticker_g)
            price = snap.get('price', 0)

            # Grade
            if score == 5:
                grade, gbox = "A+", "green-box"
                note = "All 5 checks confirmed. This is your best-case scenario. Trade it — 1 contract, icebreaker rule."
            elif score == 4:
                grade, gbox = "A", "green-box"
                note = "Strong setup. Trade it with full discipline. Stay strict on exits."
            elif score == 3:
                grade, gbox = "B", "yellow-box"
                note = "Borderline. If you trade it, reduce size and be quicker to exit."
            else:
                grade, gbox = "SKIP", "red-box"
                note = "Too many unknowns. There will be a better setup tomorrow."

            st.markdown(f"""
            <div class="{gbox}">
            <h2>Grade: {grade} &nbsp;&nbsp; ({score}/5)</h2>
            <p>{note}</p>
            </div>""", unsafe_allow_html=True)

            # ── IV Rank check ─────────────────────────────────────────────
            iv_g = get_iv_rank(ticker_g)
            if iv_g.get("available"):
                iv_box = (
                    "green-box"  if iv_g['grade'] == "CHEAP" else
                    "red-box"    if iv_g['grade'] == "RICH"  else
                    "yellow-box"
                )
                iv_warn = ""
                if iv_g['grade'] == "RICH":
                    iv_warn = " ⚠️ Consider waiting for IV to drop before entering."
                elif iv_g['grade'] == "CHEAP":
                    iv_warn = " ✅ Good time to buy options — premium is cheap."
                st.markdown(f"""
                <div class="{iv_box}">
                <h3>{iv_g['emoji']} IV Rank: {iv_g['iv_rank']:.0f} — Options are {iv_g['grade']}{iv_warn}</h3>
                <p>{iv_g['advice']}</p>
                <p style="font-size:12px; color:#8b92a8;">
                  Current IV: {iv_g['current_iv']}% &nbsp;|&nbsp;
                  HV20: {iv_g['hv20']}% &nbsp;|&nbsp;
                  HV63: {iv_g['hv63']}% &nbsp;|&nbsp;
                  IV/HV ratio: {iv_g['ratio']}x &nbsp;|&nbsp;
                  Expiry used: {iv_g['expiry']}
                </p>
                </div>""", unsafe_allow_html=True)
            else:
                st.info(f"IV data loading for {ticker_g}…")

            # ── Options liquidity check ───────────────────────────────────────
            if price > 0:
                if price < 5:
                    st.error(f"⚠️ Options Liquidity: {ticker_g} at ${price:.2f} — stocks under $5 almost never have liquid options. Wide spreads will eat your edge. Consider skipping or trading a correlated liquid name.")
                elif price < 10:
                    st.warning(f"⚠️ Options Liquidity: {ticker_g} at ${price:.2f} — verify open interest > 200 contracts and bid/ask spread < 10% before entering.")
                else:
                    st.success(f"✅ {ticker_g} at ${price:.2f} — price range supports options liquidity. Still confirm open interest > 200 and tight spread.")

                if grade in ("A+", "A"):
                    strike = round(price)
                    st.markdown("### Entry Plan")
                    st.markdown(f"""
| Field | Value |
|---|---|
| Strike | ${strike} ATM |
| Delta target | 0.40 – 0.60 |
| Expiry | Next weekly (1–2 weeks out) |
| Contracts | **1** (icebreaker rule) |
| Exit +15% | Premium × 1.15 |
| Exit +25% | Premium × 1.25 |
| Stop loss | −30% premium OR back below VWAP |
| Window | **9:30 – 9:30 AM CT only** |
                    """)
        else:
            st.info("Enter a ticker symbol on the left to grade the setup.")
            st.markdown("""
**How to use this tab:**
1. Run pre-market scanner (Finviz, TradingView) at 7:00 AM CT (pre-market opens)
2. Find stocks with > 20% pre-market volume vs daily average
3. Enter each candidate here and work through the 5 checks
4. Only trade A or A+ grades
5. Cross-reference with Regime tab before entering
""")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 8  OPTIONS PLANNER
# ─────────────────────────────────────────────────────────────────────────────
with tab8:
    st.markdown("## 💰 OPTIONS TRADE PLANNER")

    st.markdown("""
    <div style="background:#1e2130; border-radius:10px; padding:12px 16px; margin-bottom:12px;">
      <span style="color:#2ecc71; font-size:16px; font-weight:bold;">✅ AVAILABLE NOW (Level 2)</span>
      &nbsp;&nbsp;|&nbsp;&nbsp;
      <span style="color:#e74c3c; font-size:16px; font-weight:bold;">🔒 LOCKED (Level 3 + $2,000 margin)</span><br>
      <span style="color:#8b92a8; font-size:13px;">Use the <strong style="color:#2ecc71;">Directional Call / Put</strong> mode today.
      The XSP spread calculator is shown for learning — you can't execute it yet.</span>
    </div>
    """, unsafe_allow_html=True)

    mode = st.radio(
        "Select mode:",
        ["📈 Directional Call Play (momentum) — ✅ AVAILABLE NOW", "📊 XSP Put Credit Spread (income) — 🔒 LOCKED"],
        horizontal=True
    )

    st.markdown("---")

    # ── Mode A: Directional Call ──────────────────────────────────────────────
    if "Directional" in mode:
        st.markdown("### Directional Call / Put — Momentum Setup")
        st.caption("Use after Catalyst Grader confirms A or A+ grade. Entry window 9:30–9:30 AM CT only.")

        c1, c2 = st.columns(2)
        with c1:
            d_tick   = st.text_input("Ticker", value=st.session_state.get('selected_ticker', ''), placeholder="e.g. FSLY", key="planner_ticker").upper()
            d_price  = st.number_input("Current Stock Price ($)", value=0.0, step=0.01, min_value=0.0)
            d_prem   = st.number_input("Option Ask — Premium ($)", value=0.0, step=0.01, min_value=0.0,
                                        help="The price you pay per share. Multiply × 100 for total cost.")
            d_side   = st.radio("Direction", ["Call (bullish)", "Put (bearish)"], horizontal=True)
            d_time   = st.time_input("Entry Time (CT)", value=datetime.strptime("08:35", "%H:%M").time())

        with c2:
            # IV Rank — show before the plan so you know what you're paying
            if d_tick:
                iv_p = get_iv_rank(d_tick)
                if iv_p.get("available"):
                    iv_p_box = (
                        "green-box"  if iv_p['grade'] == "CHEAP" else
                        "red-box"    if iv_p['grade'] == "RICH"  else
                        "yellow-box"
                    )
                    st.markdown(f"""
                    <div class="{iv_p_box}" style="padding:10px 14px; margin-bottom:8px;">
                    <strong>{iv_p['emoji']} {d_tick} — Options are {iv_p['grade']} &nbsp;
                    (IV Rank {iv_p['iv_rank']:.0f})</strong><br>
                    <span style="font-size:13px;">{iv_p['advice']}</span><br>
                    <span style="font-size:11px; color:#8b92a8;">
                      IV {iv_p['current_iv']}% &nbsp;·&nbsp;
                      HV20 {iv_p['hv20']}% &nbsp;·&nbsp;
                      ratio {iv_p['ratio']}x
                    </span>
                    </div>""", unsafe_allow_html=True)

            if d_price > 0 and d_prem > 0:
                strike = round(d_price)
                cost   = round(d_prem * 100, 2)
                tgt15  = round(d_prem * 1.15, 2)
                tgt25  = round(d_prem * 1.25, 2)
                stop   = round(d_prem * 0.70, 2)
                rr     = round((tgt25 - d_prem) / (d_prem - stop), 2) if d_prem > stop else 0

                box_color = "green-box" if "Call" in d_side else "red-box"
                st.markdown(f"""
                <div class="{box_color}">
                <h3>Trade Plan: {d_tick if d_tick else 'ticker'} {d_side}</h3>
                <p><strong>Strike:</strong> ${strike} ATM &nbsp;|&nbsp; <strong>Delta target:</strong> 0.40–0.60</p>
                <p><strong>Expiry:</strong> Next weekly (1–2 weeks out)</p>
                <p><strong>Total cost:</strong> ${cost:.2f} (1 contract)</p>
                <hr>
                <p>🎯 <strong>Exit target 1 (+15%):</strong> sell at ${tgt15}</p>
                <p>🎯 <strong>Exit target 2 (+25%):</strong> sell at ${tgt25}</p>
                <p>🛑 <strong>Stop loss (−30%):</strong> exit at ${stop}</p>
                <p><strong>Risk/Reward:</strong> {rr:.1f}:1</p>
                </div>""", unsafe_allow_html=True)

                cutoff = datetime.strptime("09:30", "%H:%M").time()
                if d_time > cutoff:
                    st.warning(f"⚠️ THETA WARNING: {d_time.strftime('%H:%M')} CT is past the 9:30 AM CT momentum window. Time decay accelerates sharply. Wait for tomorrow's open unless this is an exceptional A+ setup.")
                else:
                    mins_left = (datetime.combine(date.today(), cutoff) - datetime.combine(date.today(), d_time)).seconds // 60
                    st.success(f"✅ In momentum window — {mins_left} min remaining before 9:30 AM CT cutoff (10:30 ET).")
            else:
                st.info("Enter stock price and option premium to generate trade plan.")

    # ── Mode B: XSP Put Credit Spread ────────────────────────────────────────
    else:
        st.markdown("""
        <div class="red-box">
          <h2 style="color:#e74c3c;">🔒 NOT AVAILABLE YET — Requires Level 3 + Margin Account</h2>
          <p><strong>What you need:</strong></p>
          <ul>
            <li>Webull options approval: <strong>Level 3</strong> (allows credit spreads)</li>
            <li>Margin account with <strong>$2,000 minimum equity</strong></li>
          </ul>
          <p><strong>Your path:</strong> Grow to $2,000 via Level 2 call/put buying →
          open margin account → apply for Level 3 → unlock this strategy.</p>
          <p style="color:#f39c12;">⬇️ Calculator shown below for learning purposes only.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### XSP Put Credit Spread — Income Strategy (Preview)")
        st.markdown("*Will enter when XSP (≈ SPY) closes above 20-day MA. Exit if it closes below.*")

        xsp = get_xsp_data()
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("#### Signal Check (SPY as XSP proxy)")
            if xsp:
                sig_box  = "green-box" if xsp['above_ma'] else "red-box"
                sig_text = "✅ SPY ABOVE 20-MA → ENTER SPREAD" if xsp['above_ma'] else "❌ SPY BELOW 20-MA → WAIT / EXIT EXISTING"
                st.markdown(f'<div class="{sig_box}"><h3>{sig_text}</h3></div>', unsafe_allow_html=True)
                st.metric("SPY Price",  f"${xsp['price']:.2f}")
                st.metric("20-Day MA",  f"${xsp['ma20']:.2f}")
                default_px = xsp['price']
            else:
                st.warning("SPY data unavailable — enter price manually")
                default_px = 0.0

            xsp_px = st.number_input("XSP/SPY Price (use actual XSP from Webull)", value=default_px, step=0.01, min_value=0.0)
            credit = st.number_input("Credit to Collect ($ per share)", value=0.35, step=0.01, min_value=0.01,
                                     help="Typical ATM 1-point put credit spread on XSP collects ~$0.33–$0.38")

        with c2:
            if xsp_px > 0 and credit > 0:
                sell_s   = int(xsp_px)        # just below current price
                buy_s    = sell_s - 1
                cap_req  = round((1.00 - credit) * 100, 2)
                max_pft  = round(credit * 100, 2)
                max_loss = round((1.00 - credit) * 100, 2)
                early_bv = round(credit * 0.24, 2)   # value remaining at 76% profit captured
                early_pft = round(max_pft * 0.76, 2)

                st.markdown(f"""
                <div class="green-box">
                <h3>Spread Setup</h3>
                <p><strong>Sell:</strong> {sell_s} Put &nbsp;|&nbsp; <strong>Buy:</strong> {buy_s} Put</p>
                <p><strong>Expiry:</strong> 14 days out (two weeks)</p>
                <p><strong>Credit received:</strong> ${credit:.2f} → <strong>${max_pft:.0f} total</strong></p>
                <p><strong>Capital required:</strong> <strong>${cap_req:.2f}</strong></p>
                <p><strong>Max profit:</strong> ${max_pft:.0f} &nbsp;|&nbsp; <strong>Max loss:</strong> ${max_loss:.0f}</p>
                <hr>
                <h4>Velocity of Capital</h4>
                <p>Close early when spread costs <strong>${early_bv:.2f}</strong> to buy back</p>
                <p>That locks in <strong>${early_pft:.0f} profit (76%)</strong> — then re-establish at current price</p>
                </div>""", unsafe_allow_html=True)

                st.markdown("**Rules:**")
                st.markdown(f"- Enter only when SPY/XSP closes **above** 20-day MA")
                st.markdown(f"- Exit immediately if SPY/XSP closes **below** 20-day MA")
                st.markdown(f"- Expiry: 14 days out")
                st.markdown(f"- $250 account → **1 spread max** (${cap_req:.0f} at risk)")
                st.markdown(f"- On Webull: need **Level 3 options approval** for credit spreads")
            else:
                st.info("Enter XSP price and credit amount to calculate the spread.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 9  COACH
# ─────────────────────────────────────────────────────────────────────────────
with tab9:
    st.markdown("## 🧠 TENDENCIES COACH")
    st.markdown("*Log your mistakes. Review before every trading session. Break the patterns.*")
    st.caption("74% of small account failures come from repeating the same behavioral mistakes — not from bad strategy.")

    c_left, c_right = st.columns([1, 1])

    with c_left:
        st.markdown("### Log a Tendency / Mistake")
        tend_text = st.text_area(
            "Describe the pattern:",
            height=120,
            placeholder="e.g. Held past 9:30 AM CT because I was convinced it would keep running. Lost 30% of premium to theta. Rule: breakout or bailout."
        )
        if st.button("💾 Save Tendency", type="primary"):
            if tend_text.strip():
                save_tendency(tend_text.strip())
                st.session_state.tendencies = load_tendencies()
                st.success("Logged.")
                st.rerun()

        st.markdown("---")
        st.markdown("### Pre-Trade Checklist")
        st.markdown("*Check all boxes before placing any trade*")
        pre_checks = [
            "Reviewed my tendencies list →",
            "Setup is A or A+ (Catalyst Grader tab)",
            "Regime is green or yellow (Regime tab)",
            "Entry time is before 9:30 AM CT (momentum window)",
            "Options liquidity verified (OI > 200, spread < 10%)",
            "1 contract only — icebreaker rule",
            "Stop loss level pre-defined before entry",
            "This is not revenge trading",
            "I have not already had 3 losing trades today",
        ]
        for i, item in enumerate(pre_checks):
            st.checkbox(item, key=f"pre_{i}")

    with c_right:
        st.markdown("### Your Tendencies")
        tends = st.session_state.tendencies
        if tends:
            for t in reversed(tends[-15:]):
                st.markdown(f"""
                <div class="yellow-box">
                <p><small>📅 {t.get('date', '')}</small></p>
                <p>{t.get('tendency', '')}</p>
                </div>""", unsafe_allow_html=True)

            df_t = pd.DataFrame(tends)
            st.download_button(
                "📥 Export Tendencies",
                df_t.to_csv(index=False),
                f"tendencies_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
        else:
            st.info("No tendencies logged yet. After every losing trade, come here and describe what went wrong. This is where your edge gets built.")
            st.markdown("""
**Common tendencies to watch for:**
- Holding past 9:30 AM CT (theta enemy)
- Chasing after missing the first entry
- Revenge trading after a loss
- Entering B-grade setups on slow days
- Ignoring the regime tab (trading into bad environment)
- Skipping stop loss discipline
""")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    # ── Account Balance ───────────────────────────────────────────────────────
    st.markdown("### 💰 Starting Balance")
    st.caption("Set your actual Webull starting balance. The dashboard adds/subtracts trade P/L automatically.")
    new_start = st.number_input("Starting balance ($)", value=250.0, min_value=1.0, step=1.0, key="start_bal_input")
    if st.button("✅ Set Balance", key="set_bal_btn"):
        # Patch the module-level constant so recalc picks it up on next rerun
        st.session_state['_starting_balance_override'] = new_start
        st.rerun()

    override = st.session_state.get('_starting_balance_override', 250.0)
    live_bal = round(override + _total_pnl, 2)
    st.session_state.account_balance = live_bal
    st.metric("Current Balance", f"${live_bal:.2f}", delta=f"${_total_pnl:+.2f} all-time P/L")

    st.markdown("---")
    # ── Watchlist ─────────────────────────────────────────────────────────────
    st.markdown("### 📋 Today's Watchlist")
    st.caption("Add tickers from your screener. Only stocks that meet your criteria.")

    new_tick = st.text_input("Add ticker", placeholder="e.g. NVDA", key="new_tick_input").upper().strip()
    if st.button("➕ Add", key="add_tick_btn") and new_tick:
        if new_tick not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_tick)
            st.cache_data.clear()
            st.rerun()

    if st.session_state.watchlist:
        for tick in list(st.session_state.watchlist):
            col_t, col_x = st.columns([3, 1])
            col_t.markdown(f"**{tick}**")
            if col_x.button("✕", key=f"rm_{tick}"):
                st.session_state.watchlist.remove(tick)
                st.cache_data.clear()
                st.rerun()
        if st.button("🗑 Clear All", key="clear_watchlist"):
            st.session_state.watchlist = []
            st.cache_data.clear()
            st.rerun()
    else:
        st.info("No tickers yet. Find momentum names on Finviz, then add them here.")

    st.markdown("---")
    st.markdown("### 📲 Push Notifications (ntfy.sh)")
    st.caption("Get iPhone alerts when signals fire. Free — no account needed.")
    _ntfy_input = st.text_input(
        "ntfy.sh topic",
        value=st.session_state.get('ntfy_topic', ''),
        placeholder="e.g. scalper_mel_2025",
        key="ntfy_input",
        help="Pick any unique name. Install ntfy app on iPhone → subscribe to same topic."
    )
    if st.button("💾 Save Topic", key="save_ntfy"):
        st.session_state['ntfy_topic'] = _ntfy_input.strip()
        st.success(f"Topic saved: {_ntfy_input.strip()}")
    if st.session_state.get('ntfy_topic'):
        if st.button("🔔 Test Notification", key="test_ntfy"):
            send_ntfy(
                st.session_state['ntfy_topic'],
                "🌙 Scalper Dashboard Test",
                "Push notifications are working! You'll get alerts when signals fire.",
                priority="default"
            )
            st.success("Test sent — check your phone!")
        st.caption(f"Active: ntfy.sh/**{st.session_state['ntfy_topic']}**")
    else:
        st.markdown("""
        <small>
        1. Download <strong>ntfy</strong> app on iPhone (free)<br>
        2. Enter any unique topic name above<br>
        3. In the app, subscribe to that same topic<br>
        4. Signals will push to your phone automatically
        </small>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔌 Alpaca Connection")
    api = get_alpaca()
    if api:
        try:
            acct = api.get_account()
            st.success("✅ Connected")
            st.metric("Paper Balance", f"${float(acct.cash):,.2f}")
        except Exception:
            st.error("❌ Connection Failed")
    else:
        st.warning("⚠️ No API keys")
        st.caption("Add ALPACA_API_KEY + ALPACA_SECRET_KEY to .env")

    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("### 📡 Scanner Status")
    wl = st.session_state.watchlist
    st.markdown(f"**Watching:** {', '.join(wl) if wl else 'None — add tickers above'}")
    st.markdown("**Active:** #163 · #172 · #177")
    st.markdown("**Source:** yfinance (15-min delay)")
    st.markdown(f"**Last run:** {last_updated}")

    st.markdown("---")
    st.markdown("### 🔗 Free Tools")
    st.markdown("[📊 Finviz Screener](https://finviz.com/screener.ashx)")
    st.markdown("[📰 Catalyst / Earnings](https://www.getcatalyst.org/)")
    st.markdown("[📅 Yahoo Earnings Calendar](https://finance.yahoo.com/calendar/earnings/)")
    st.markdown("[📓 TradesViz Journal](https://www.tradesviz.com/)")
    st.markdown("[📈 TradingView Charts](https://www.tradingview.com/)")
    st.markdown("[🐋 Unusual Whales Flow](https://unusualwhales.com/)")

    st.markdown("---")
    st.markdown("### 📚 Resources")
    guide_path = Path(__file__).parent / "SMALL_ACCOUNT_DASHBOARD_GUIDE.md"
    if guide_path.exists():
        with st.expander("📖 Dashboard Guide"):
            st.markdown(guide_path.read_text())

    st.markdown("---")
    st.markdown("*Dashboard v3.0 | $250 | Options Only*")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#8b92a8;">
<p>🌙 <strong>Rules:</strong> 1 contract · Breakout or bailout · 9:30 AM CT cutoff · 3 strikes and done · Journal everything</p>
<p>Made for small account traders building real discipline</p>
</div>
""", unsafe_allow_html=True)
