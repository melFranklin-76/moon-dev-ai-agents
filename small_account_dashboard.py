#!/usr/bin/env python3
"""
Small Account Options Scalper Dashboard v3.1
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
 10. IV Scanner        — multi-expiration IV surface fitting
 11. Entry Wizard      — pre-flight decision gate

Run:
  streamlit run small_account_dashboard.py
"""

import streamlit as st
import pandas as pd
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
        get_rs_vs_spy,
        get_squeeze_score,
        get_max_pain,
        get_intraday_sector_flow,
        get_signal_strength,
        get_best_buy_strike,
        get_earnings_date,
        get_volume_spike,
        scan_iv_surface,
        get_rvol,
    )
except ImportError:
    def get_options_snapshot(symbol: str) -> dict:   return {"available": False}
    def get_news(symbol: str) -> list:               return []
    def send_ntfy(*a, **kw):                         pass
    def scan_premarket_gaps(*a, **kw) -> list:       return []
    def get_iv_rank(symbol: str) -> dict:            return {"available": False}
    def get_rs_vs_spy(symbol: str) -> dict:          return {"available": False}
    def get_squeeze_score(symbol: str) -> dict:      return {"available": False}
    def get_max_pain(symbol: str) -> dict:           return {"available": False}
    def get_intraday_sector_flow() -> list:          return []
    def get_signal_strength(symbol: str) -> dict:
        _d = {"rs":  {"pts": 0, "note": "—", "label": "—", "color": "#8b92a8"},
              "iv":  {"pts": 0, "note": "—", "grade": "—", "color": "#8b92a8"},
              "sq":  {"pts": 0, "note": "—", "score": 0,   "color": "#8b92a8"},
              "mp":  {"pts": 0, "note": "—", "strike": 0,  "color": "#8b92a8"},
              "liq": {"pts": 0, "note": "—"}}
        return {"score": 0, "grade": "—", "color": "#8b92a8",
                "emoji": "⬜", "stars": "☆"*10, "advice": "", "detail": _d}
    def get_best_buy_strike(symbol: str) -> dict:    return {"available": False}
    def get_earnings_date(symbol: str) -> dict:      return {"available": False}
    def get_volume_spike(symbol: str) -> dict:       return {"available": False}
    def scan_iv_surface(*a, **kw) -> dict:           return {"available": False}
    def get_rvol(symbol: str) -> dict:               return {"available": False}

try:
    from streamlit_autorefresh import st_autorefresh as _st_autorefresh
    _HAS_AUTOREFRESH = True
except ImportError:
    _HAS_AUTOREFRESH = False
    def _st_autorefresh(*a, **kw): pass

import sheets_backend as _sheets

# Tab modules
import tab_scanner, tab_tickers, tab_trades, tab_performance
import tab_journal, tab_market, tab_catalyst, tab_options
import tab_coach, tab_ivscan, tab_wizard

load_dotenv()

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="$250 Scalper Dashboard",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""<style>
    /* ── Base ── */
    .main {background-color: #0e1117;}
    .stMetric {background-color: #1e2130; padding: 15px; border-radius: 10px;}
    .stMetric label {color: #8b92a8 !important; font-size: 14px !important;}
    .stMetric [data-testid="stMetricValue"] {color: #ffffff !important; font-size: 32px !important;}
    .green-box  {background-color: #1a3d1a; padding: 15px; border-radius: 10px; border: 2px solid #2ecc71; margin-bottom: 12px;}
    .red-box    {background-color: #3d1a1a; padding: 15px; border-radius: 10px; border: 2px solid #e74c3c; margin-bottom: 12px;}
    .yellow-box {background-color: #3d361a; padding: 15px; border-radius: 10px; border: 2px solid #f39c12; margin-bottom: 12px;}
    .trade-card {background-color: #1e2130; padding: 20px; border-radius: 10px; margin: 10px 0;}
    h1 {color: #2ecc71 !important;}
    h2 {color: #3498db !important;}
    h3 {color: #f39c12 !important;}
    .big-text {font-size: 40px; font-weight: bold; text-align: center;}

    /* ── Simple Mode cards (mobile-first) ── */
    .simple-card {
        background: #1e2130;
        border-radius: 14px;
        padding: 18px 16px;
        margin: 8px 0;
        border: 1px solid #2a2d3e;
    }
    .simple-ticker  {font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: 1px;}
    .simple-price   {font-size: 36px; font-weight: 700; text-align: center; margin: 6px 0;}
    .simple-change  {font-size: 16px; text-align: center; margin-bottom: 8px;}
    .simple-signal  {font-size: 28px; font-weight: 900; text-align: center;
                     padding: 10px; border-radius: 10px; margin: 8px 0;}
    .simple-stars   {font-size: 20px; text-align: center; letter-spacing: 2px;}
    .simple-advice  {font-size: 13px; color: #8b92a8; text-align: center; margin-top: 6px;}
    .simple-layers  {font-size: 12px; color: #8b92a8; margin-top: 8px; line-height: 1.8;}

    /* ── Mobile responsive ── */
    @media (max-width: 768px) {
        .simple-price  {font-size: 44px;}
        .simple-signal {font-size: 32px;}
        .stButton button {height: 52px !important; font-size: 18px !important;}
        .stTabs [data-baseweb="tab"] {font-size: 13px !important; padding: 8px 6px !important;}
    }
</style>""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────────
BTC_TICKER = "BTC-USD"
BTC_KEY_LEVELS = [60000, 65000, 70000, 72500, 75000, 80000, 85000, 90000, 95000, 100000]

TRADES_FILE = Path(__file__).parent / "src" / "data" / "small_account" / "trades.csv"
TRADES_FILE.parent.mkdir(parents=True, exist_ok=True)
TRADE_FIELDS = ['date', 'ticker', 'strategy', 'side', 'entry', 'exit', 'pnl', 'result', 'notes']

ALERTS_FILE  = Path(__file__).parent / "src" / "data" / "small_account" / "alerts.csv"
ALERT_FIELDS = ['ticker', 'target', 'direction', 'created', 'triggered']

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

# ── Persistence ──────────────────────────────────────────────────────────────
def load_alerts() -> list:
    if not ALERTS_FILE.exists():
        return []
    try:
        df = pd.read_csv(ALERTS_FILE)
        df['triggered'] = df['triggered'].astype(str).str.lower().isin(['true', '1', 'yes'])
        return df.to_dict('records')
    except Exception:
        return []

def save_alerts(alerts: list):
    try:
        with open(ALERTS_FILE, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=ALERT_FIELDS)
            w.writeheader()
            for a in alerts:
                w.writerow({k: a.get(k, '') for k in ALERT_FIELDS})
    except Exception:
        pass

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

# ── Session State ────────────────────────────────────────────────────────────
_trades_from_file = load_trades()
_total_pnl = sum(float(t.get('pnl', 0)) for t in _trades_from_file)
_starting_balance = 250.00
_computed_balance = round(_starting_balance + _total_pnl, 2)

_today_str = date.today().isoformat()
_daily_pnl = sum(
    float(t.get('pnl', 0)) for t in _trades_from_file
    if str(t.get('date', '')).startswith(_today_str)
)

_daily_goal    = 25.0
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
    'selected_ticker':  '',
    'ntfy_topic':       '',
    'news_cache':       {},
    'view_mode':        'Simple',
    'price_alerts':     load_alerts(),
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.session_state.account_balance = _computed_balance
st.session_state.daily_pnl       = round(_daily_pnl, 2)
st.session_state.daily_reds      = _today_reds

# ── Data Layer ───────────────────────────────────────────────────────────────
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

# ── Scanner Engine ───────────────────────────────────────────────────────────
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

# ── Load Market Data ─────────────────────────────────────────────────────────
_watchlist = st.session_state.get('watchlist', [])
with st.spinner("Loading market data..."):
    btc_price    = get_btc_price()
    snapshots    = {sym: get_snapshot(sym) for sym in _watchlist}
    last_updated = datetime.now().strftime('%H:%M:%S')

# ── Price Alert Check ────────────────────────────────────────────────────────
_alerts       = st.session_state.get('price_alerts', [])
_ntfy_topic   = st.session_state.get('ntfy_topic', '')
_alert_fired  = False
for _al in _alerts:
    if _al.get('triggered'):
        continue
    _sym    = str(_al.get('ticker', '')).upper()
    _target = float(_al.get('target', 0))
    _dirn   = str(_al.get('direction', 'above'))
    if not _sym or _target <= 0:
        continue
    if _sym in snapshots:
        _curr = snapshots[_sym]['price']
    else:
        try:
            _df_a = yf.Ticker(_sym).history(period='1d', interval='5m')
            _curr = float(_df_a['Close'].iloc[-1]) if not _df_a.empty else 0.0
        except Exception:
            _curr = 0.0
    if _curr <= 0:
        continue
    _hit = (_dirn == 'above' and _curr >= _target) or \
           (_dirn == 'below' and _curr <= _target)
    if _hit:
        _al['triggered'] = True
        _alert_fired     = True
        _arrow = "▲" if _dirn == 'above' else "▼"
        _msg   = f"{_sym} is at ${_curr:.2f} — your {_arrow} ${_target:.2f} alert triggered!"
        st.toast(f"🔔 {_sym} {_arrow} ${_target:.2f} — ALERT!", icon="🔔")
        if _ntfy_topic:
            send_ntfy(_ntfy_topic, f"🔔 Price Alert: {_sym} {_arrow} ${_target:.2f}", _msg, priority="urgent")
if _alert_fired:
    save_alerts(_alerts)
    st.session_state['price_alerts'] = _alerts

# ── Auto-refresh ─────────────────────────────────────────────────────────────
if _HAS_AUTOREFRESH and st.session_state.get('auto_refresh', True):
    _st_autorefresh(interval=60_000, key="main_autorefresh")

# ── Header ───────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.markdown("# 🌙 SMALL ACCOUNT SCALPER")
    st.markdown("### $250 Challenge | Options Only | Webull")

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

# ── Top Stats Bar ────────────────────────────────────────────────────────────
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

# ── Daily P&L Goal Bar ──────────────────────────────────────────────────────
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

st.markdown(f"""
<div style="background:#1e2130; border-radius:8px; padding:8px 14px; margin:4px 0 10px 0;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
    <span style="color:{_goal_color}; font-weight:bold;">{_goal_msg}</span>
    <span style="color:#8b92a8; font-size:12px;">${_dpnl:+.2f} / +${_daily_goal:.0f}</span>
  </div>
  <div style="background:#0e1117; border-radius:4px; height:8px; overflow:hidden;">
    <div style="background:{_goal_color}; width:{_goal_pct*100:.0f}%; height:8px; border-radius:4px;"></div>
  </div>
</div>""", unsafe_allow_html=True)

# ── Trading Window Countdown ─────────────────────────────────────────────────
from zoneinfo import ZoneInfo
_now_ct = datetime.now(ZoneInfo("America/Chicago"))
_open_h, _open_m = 8, 30   # 8:30 AM CT = pre-market prep
_trade_h, _trade_m = 9, 30  # 9:30 AM CT = entries
_close_h, _close_m = 10, 0  # 10:00 AM CT = window closes

_now_mins = _now_ct.hour * 60 + _now_ct.minute
_open_mins  = _open_h * 60 + _open_m
_trade_mins = _trade_h * 60 + _trade_m
_close_mins = _close_h * 60 + _close_m

if _now_mins < _open_mins:
    _mins_left = _trade_mins - _now_mins
    _tw_color = "#3498db"
    _tw_msg = f"⏳ Trading window opens in {_mins_left} min — prep your watchlist"
    _tw_pct = 0.0
elif _now_mins < _trade_mins:
    _mins_left = _trade_mins - _now_mins
    _tw_color = "#f39c12"
    _tw_msg = f"🔍 Pre-market scan — entries open in {_mins_left} min"
    _tw_pct = (_now_mins - _open_mins) / (_trade_mins - _open_mins)
elif _now_mins < _close_mins:
    _mins_left = _close_mins - _now_mins
    _tw_color = "#2ecc71"
    _tw_msg = f"🟢 WINDOW OPEN — {_mins_left} min left to enter trades"
    _tw_pct = (_now_mins - _trade_mins) / (_close_mins - _trade_mins)
else:
    _mins_left = 0
    _tw_color = "#e74c3c"
    _tw_msg = "🔴 Window closed — no new entries. Manage open positions only."
    _tw_pct = 1.0

st.markdown(f"""
<div style="background:#1e2130; border-radius:8px; padding:8px 14px; margin:4px 0 10px 0;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
    <span style="color:{_tw_color}; font-weight:bold; font-size:14px;">{_tw_msg}</span>
    <span style="color:#8b92a8; font-size:12px;">{_now_ct.strftime('%I:%M %p CT')}</span>
  </div>
  <div style="background:#0e1117; border-radius:4px; height:6px; overflow:hidden;">
    <div style="background:{_tw_color}; width:{_tw_pct*100:.0f}%; height:6px; border-radius:4px;"></div>
  </div>
</div>""", unsafe_allow_html=True)
st.markdown("---")

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
    "🎯 Live Scanner",
    "📊 My Tickers",
    "🎴 Trade Cards",
    "📈 Performance",
    "📝 Journal",
    "🌡️ Market Regime",
    "🔍 Catalyst Grader",
    "💰 Options Planner",
    "🧠 Coach",
    "📊 IV Scanner",
    "🚦 Entry Wizard",
])

# ── Render each tab via its module ───────────────────────────────────────────
tab_scanner.render(tab1,
    snapshots=snapshots, btc_price=btc_price, _watchlist=_watchlist,
    last_updated=last_updated, scan_momentum_universe=scan_momentum_universe,
    get_squeeze_score=get_squeeze_score, get_news=get_news,
    get_intraday_sector_flow=get_intraday_sector_flow,
    get_rs_vs_spy=get_rs_vs_spy, send_ntfy=send_ntfy,
    scan_premarket_gaps=scan_premarket_gaps, run_scanner=run_scanner,
)

tab_tickers.render(tab2,
    snapshots=snapshots, _watchlist=_watchlist, last_updated=last_updated,
    get_signal_strength=get_signal_strength, get_earnings_date=get_earnings_date,
    get_options_snapshot=get_options_snapshot, get_iv_rank=get_iv_rank,
    get_rs_vs_spy=get_rs_vs_spy, get_squeeze_score=get_squeeze_score,
    get_max_pain=get_max_pain, get_best_buy_strike=get_best_buy_strike,
    get_volume_spike=get_volume_spike, get_rvol=get_rvol,
)

tab_trades.render(tab3, ALL_STRATEGIES=ALL_STRATEGIES)

tab_performance.render(tab4)

tab_journal.render(tab5,
    ALL_STRATEGIES=ALL_STRATEGIES, TRADE_FIELDS=TRADE_FIELDS,
    save_trade=save_trade, load_trades=load_trades,
)

tab_market.render(tab6,
    get_regime_data=get_regime_data, get_sector_data=get_sector_data,
    get_intraday_sector_flow=get_intraday_sector_flow,
)

tab_catalyst.render(tab7,
    get_snapshot=get_snapshot, get_max_pain=get_max_pain,
    get_rs_vs_spy=get_rs_vs_spy, get_iv_rank=get_iv_rank,
)

tab_options.render(tab8,
    get_max_pain=get_max_pain, get_iv_rank=get_iv_rank,
    get_xsp_data=get_xsp_data,
)

tab_coach.render(tab9,
    save_tendency=save_tendency, load_tendencies=load_tendencies,
)

tab_ivscan.render(tab10, scan_iv_surface=scan_iv_surface)

tab_wizard.render(tab11,
    get_iv_rank=get_iv_rank, get_earnings_date=get_earnings_date,
    get_options_snapshot=get_options_snapshot,
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    st.markdown("### 👁️ View Mode")
    _mode_choice = st.radio(
        "Choose your view:",
        ["🟢 Simple", "🔬 Pro"],
        index=0 if st.session_state.get('view_mode', 'Simple') == 'Simple' else 1,
        horizontal=True, key="mode_radio",
        help="Simple = clean signal card. Pro = all 5 insider layers.",
    )
    st.session_state['view_mode'] = 'Simple' if _mode_choice == '🟢 Simple' else 'Pro'
    if st.session_state['view_mode'] == 'Simple':
        st.caption("📱 Simple Mode — clean cards, perfect for mobile. One score tells the story.")
    else:
        st.caption("🔬 Pro Mode — all 5 insider layers visible. For when you want the full picture.")

    st.markdown("---")
    st.markdown("### 🔄 Auto-Refresh")
    _ar_on = st.toggle("Refresh every 60 seconds",
                        value=st.session_state.get('auto_refresh', True),
                        key="auto_refresh_toggle",
                        help="Keeps prices, alerts, and signals current while the tab is open.")
    st.session_state['auto_refresh'] = _ar_on
    st.caption("🟢 Live — updating every 60s" if _ar_on else "⏸ Paused — hit ⌘R / F5 to refresh manually")

    st.markdown("---")
    st.markdown("### 💰 Starting Balance")
    st.caption("Set your actual Webull starting balance. The dashboard adds/subtracts trade P/L automatically.")
    new_start = st.number_input("Starting balance ($)", value=250.0, min_value=1.0, step=1.0, key="start_bal_input")
    if st.button("✅ Set Balance", key="set_bal_btn"):
        st.session_state['_starting_balance_override'] = new_start
        st.rerun()

    override = st.session_state.get('_starting_balance_override', 250.0)
    live_bal = round(override + _total_pnl, 2)
    st.session_state.account_balance = live_bal
    st.metric("Current Balance", f"${live_bal:.2f}", delta=f"${_total_pnl:+.2f} all-time P/L")

    st.markdown("---")
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
    _ntfy_input = st.text_input("ntfy.sh topic",
        value=st.session_state.get('ntfy_topic', ''),
        placeholder="e.g. scalper_mel_2025", key="ntfy_input",
        help="Pick any unique name. Install ntfy app on iPhone → subscribe to same topic.")
    if st.button("💾 Save Topic", key="save_ntfy"):
        st.session_state['ntfy_topic'] = _ntfy_input.strip()
        st.success(f"Topic saved: {_ntfy_input.strip()}")
    if st.session_state.get('ntfy_topic'):
        if st.button("🔔 Test Notification", key="test_ntfy"):
            send_ntfy(st.session_state['ntfy_topic'],
                      "🌙 Scalper Dashboard Test",
                      "Push notifications are working! You'll get alerts when signals fire.",
                      priority="default")
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
    st.markdown("### 🔔 Price Alerts")
    st.caption("Triggers on each page refresh. Sends push + on-screen toast.")
    _al_c1, _al_c2 = st.columns([1, 1])
    with _al_c1:
        _new_tick  = st.text_input("Ticker", placeholder="ONDS", key="al_tick_input").upper().strip()
    with _al_c2:
        _new_price = st.number_input("Target $", min_value=0.01, step=0.25, format="%.2f", key="al_price_input")
    _new_dir = st.radio("Trigger when price is:", ["▲ Above target", "▼ Below target"],
                        horizontal=True, key="al_dir_radio")
    if st.button("➕ Add Alert", key="add_alert_btn"):
        if _new_tick and _new_price > 0:
            _new_al = {
                "ticker": _new_tick, "target": round(_new_price, 2),
                "direction": "above" if "Above" in _new_dir else "below",
                "created": date.today().isoformat(), "triggered": False,
            }
            _cur_alerts = st.session_state.get('price_alerts', [])
            _cur_alerts.append(_new_al)
            save_alerts(_cur_alerts)
            st.session_state['price_alerts'] = _cur_alerts
            st.success(f"Alert set: {_new_tick} {'▲' if 'Above' in _new_dir else '▼'} ${_new_price:.2f}")
            st.rerun()
        else:
            st.warning("Enter a ticker and target price.")

    _all_alerts  = st.session_state.get('price_alerts', [])
    _active_als  = [a for a in _all_alerts if not a.get('triggered')]
    _done_als    = [a for a in _all_alerts if a.get('triggered')]

    if _active_als:
        st.caption(f"**{len(_active_als)} active alert{'s' if len(_active_als) != 1 else ''}:**")
        for _ai, _a in enumerate(_active_als):
            _arrow = "▲" if _a['direction'] == 'above' else "▼"
            _rc1, _rc2 = st.columns([4, 1])
            with _rc1:
                st.markdown(f"<small>🔔 <strong>{_a['ticker']}</strong> {_arrow} <strong>${float(_a['target']):.2f}</strong></small>", unsafe_allow_html=True)
            with _rc2:
                if st.button("✕", key=f"del_al_{_ai}", help="Remove alert"):
                    _all_alerts = [x for x in _all_alerts if x is not _a]
                    save_alerts(_all_alerts)
                    st.session_state['price_alerts'] = _all_alerts
                    st.rerun()
    else:
        st.caption("No active alerts.")

    if _done_als:
        st.caption(f"✅ {len(_done_als)} triggered")
        if st.button("🗑 Clear triggered", key="clear_triggered_btn"):
            _all_alerts = [a for a in _all_alerts if not a.get('triggered')]
            save_alerts(_all_alerts)
            st.session_state['price_alerts'] = _all_alerts
            st.rerun()

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
    st.markdown("*Dashboard v3.1 | $250 | Options Only*")

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#8b92a8;">
<p>🌙 <strong>Rules:</strong> 1 contract · Breakout or bailout · 9:30 AM CT cutoff · 3 strikes and done · Journal everything</p>
<p>Made for small account traders building real discipline</p>
</div>
""", unsafe_allow_html=True)
