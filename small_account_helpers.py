"""
small_account_helpers.py
Helper functions for Small Account Dashboard v3.0
— market regime, sector data, XSP spread data, tendencies persistence,
  momentum universe scanner
"""

import csv
import requests
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
_DATA_DIR = Path(__file__).parent / "src" / "data" / "small_account"
try:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
except (PermissionError, OSError):
    # Streamlit Cloud read-only fs — fall back to /tmp
    _DATA_DIR = Path("/tmp") / "small_account"
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
TEND_FILE = _DATA_DIR / "tendencies.csv"

# ── Regime Data ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_regime_data() -> dict:
    """SPY, QQQ, IWM, VIX — price, 20-day MA, daily % change."""
    result = {}
    for sym in ['SPY', 'QQQ', 'IWM', '^VIX']:
        try:
            df = yf.Ticker(sym).history(period='30d', interval='1d')
            if df.empty or len(df) < 2:
                continue
            price = float(df['Close'].iloc[-1])
            ma20  = float(df['Close'].rolling(20).mean().iloc[-1])
            prev  = float(df['Close'].iloc[-2])
            chg   = (price - prev) / prev * 100 if prev else 0
            result[sym] = {
                'price':    price,
                'ma20':     ma20,
                'change':   chg,
                'above_ma': price > ma20,
            }
        except Exception:
            pass
    return result


@st.cache_data(ttl=300)
def get_sector_data() -> dict:
    """Daily % change for key sector ETFs."""
    sectors = {
        'XLK': 'Technology',
        'XLV': 'Healthcare',
        'XLI': 'Industrials',
        'XLE': 'Energy',
        'XLF': 'Financials',
        'XLU': 'Utilities',
    }
    result = {}
    for sym, name in sectors.items():
        try:
            df = yf.Ticker(sym).history(period='2d', interval='1d')
            if len(df) >= 2:
                p0 = float(df['Close'].iloc[-2])
                p1 = float(df['Close'].iloc[-1])
                result[sym] = {
                    'name':   name,
                    'price':  p1,
                    'change': (p1 - p0) / p0 * 100 if p0 else 0,
                }
        except Exception:
            pass
    return result


@st.cache_data(ttl=300)
def get_xsp_data() -> dict:
    """
    XSP ≈ SPY (both track ~1/10 of SPX).
    Returns price, 20-day MA, signal for the put credit spread strategy.
    """
    try:
        df = yf.Ticker('SPY').history(period='30d', interval='1d')
        if df.empty or len(df) < 20:
            return {}
        price = float(df['Close'].iloc[-1])
        ma20  = float(df['Close'].rolling(20).mean().iloc[-1])
        above = price > ma20
        return {
            'price':    price,
            'ma20':     ma20,
            'above_ma': above,
            'signal':   'ENTER' if above else 'WAIT',
        }
    except Exception:
        return {}


# ── Tendencies Persistence ────────────────────────────────────────────────────
def load_tendencies() -> list:
    if not TEND_FILE.exists():
        return []
    try:
        return pd.read_csv(TEND_FILE).to_dict('records')
    except Exception:
        return []


def save_tendency(text: str):
    exists = TEND_FILE.exists()
    with open(TEND_FILE, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['date', 'tendency'])
        if not exists:
            w.writeheader()
        w.writerow({'date': datetime.now().strftime('%Y-%m-%d'), 'tendency': text})


# ── Momentum Universe Scanner ─────────────────────────────────────────────────
_YF_HEADERS = {"User-Agent": "Mozilla/5.0"}
_YF_SCREEN_URL = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"


def _fetch_screen(screen_id: str, count: int = 100) -> list:
    """Pull quotes from a Yahoo Finance predefined screener."""
    try:
        r = requests.get(
            _YF_SCREEN_URL,
            params={"scrIds": screen_id, "count": count, "formatted": "false"},
            headers=_YF_HEADERS,
            timeout=15,
        )
        return r.json().get("finance", {}).get("result", [{}])[0].get("quotes", [])
    except Exception:
        return []


def _has_options(symbol: str) -> bool:
    try:
        return len(yf.Ticker(symbol).options) > 0
    except Exception:
        return False


@st.cache_data(ttl=300)
def scan_momentum_universe(
    min_price: float = 2.0,
    max_price: float = 100.0,
    min_change: float = 3.0,
    min_volume: int = 500_000,
    min_rel_vol: float = 2.0,
) -> list:
    """
    Scan Yahoo Finance day_gainers + most_actives.
    Filter by momentum criteria, flag options availability.
    Returns list of result dicts sorted by % change descending.
    """
    raw: dict = {}
    for screen in ("day_gainers", "most_actives"):
        for q in _fetch_screen(screen):
            sym = q.get("symbol", "")
            if sym and sym not in raw:
                raw[sym] = q

    results = []
    for sym, q in raw.items():
        price   = float(q.get("regularMarketPrice", 0) or 0)
        change  = float(q.get("regularMarketChangePercent", 0) or 0)
        volume  = int(q.get("regularMarketVolume", 0) or 0)
        avg_vol = int(q.get("averageDailyVolume3Month", 1) or 1)
        rel_vol = round(volume / avg_vol, 2) if avg_vol > 0 else 0.0

        if not (min_price <= price <= max_price):
            continue
        if change < min_change:
            continue
        if volume < min_volume:
            continue
        if rel_vol < min_rel_vol:
            continue

        results.append({
            "symbol":  sym,
            "name":    q.get("shortName", sym),
            "price":   price,
            "change":  change,
            "volume":  volume,
            "rel_vol": rel_vol,
        })

    results.sort(key=lambda x: x["change"], reverse=True)
    return results


# ── Options Chain Liquidity ───────────────────────────────────────────────────
@st.cache_data(ttl=120)
def get_options_snapshot(symbol: str) -> dict:
    """ATM options liquidity: OI and bid/ask spread for nearest expiry."""
    try:
        t    = yf.Ticker(symbol)
        exps = t.options
        if not exps:
            return {"available": False}
        df_px = t.history(period='1d', interval='1m')
        if df_px.empty:
            return {"available": False}
        price = float(df_px['Close'].iloc[-1])
        chain = t.option_chain(exps[0])

        def liquidity_row(row):
            oi  = int(row.get('openInterest', 0) or 0)
            bid = float(row.get('bid', 0) or 0)
            ask = float(row.get('ask', 0) or 0)
            mid = (bid + ask) / 2 if (bid + ask) > 0 else 1
            spread_pct = (ask - bid) / mid * 100 if mid > 0 else 999
            return {
                "strike":     float(row['strike']),
                "oi":         oi,
                "bid":        bid,
                "ask":        ask,
                "spread_pct": round(spread_pct, 1),
                "liquid":     oi > 200 and spread_pct < 10,
            }

        calls = chain.calls
        puts  = chain.puts
        atm_c = calls.iloc[(calls['strike'] - price).abs().argsort()[:3]]
        atm_p = puts.iloc[(puts['strike']  - price).abs().argsort()[:3]]

        return {
            "available": True,
            "expiry":    exps[0],
            "price":     price,
            "calls":     [liquidity_row(r) for _, r in atm_c.iterrows()],
            "puts":      [liquidity_row(r) for _, r in atm_p.iterrows()],
        }
    except Exception:
        return {"available": False}


# ── News Fetch ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_news(symbol: str) -> list:
    """Fetch up to 5 recent news headlines for a ticker via yfinance."""
    try:
        raw = yf.Ticker(symbol).news or []
        result = []
        for item in raw[:5]:
            ts = item.get("providerPublishTime", 0)
            dt = datetime.utcfromtimestamp(ts).strftime('%m/%d %H:%M') if ts else ""
            result.append({
                "title":     item.get("title", ""),
                "link":      item.get("link", ""),
                "publisher": item.get("publisher", ""),
                "time":      dt,
            })
        return result
    except Exception:
        return []


# ── Push Notifications (ntfy.sh) ─────────────────────────────────────────────
def send_ntfy(topic: str, title: str, message: str, priority: str = "high"):
    """Send a push notification to an ntfy.sh topic (free, no account needed)."""
    if not topic:
        return
    try:
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode("utf-8"),
            headers={
                "Title":    title,
                "Priority": priority,
                "Tags":     "chart_with_upwards_trend",
            },
            timeout=5,
        )
    except Exception:
        pass


# ── Pre-Market Gap Scanner ────────────────────────────────────────────────────
@st.cache_data(ttl=120)
def scan_premarket_gaps(
    min_gap_pct: float = 3.0,
    min_price:   float = 2.0,
    max_price:   float = 100.0,
) -> list:
    """
    Scan day_gainers + most_actives for pre-market gap stocks.
    Uses preMarketPrice vs regularMarketPreviousClose.
    """
    raw: dict = {}
    for screen in ("day_gainers", "most_actives"):
        for q in _fetch_screen(screen):
            sym = q.get("symbol", "")
            if sym and sym not in raw:
                raw[sym] = q

    results = []
    for sym, q in raw.items():
        price      = float(q.get("regularMarketPrice", 0) or 0)
        prev_close = float(q.get("regularMarketPreviousClose", 0) or 0)
        pre_price  = float(q.get("preMarketPrice", 0) or 0)

        if not (min_price <= price <= max_price):
            continue
        if prev_close <= 0:
            continue

        gap_price = pre_price if pre_price > 0 else price
        gap_pct   = (gap_price - prev_close) / prev_close * 100

        if abs(gap_pct) < min_gap_pct:
            continue

        results.append({
            "symbol":     sym,
            "name":       q.get("shortName", sym),
            "prev_close": round(prev_close, 2),
            "gap_price":  round(gap_price, 2),
            "gap_pct":    round(gap_pct, 2),
            "volume":     int(q.get("regularMarketVolume", 0) or 0),
        })

    results.sort(key=lambda x: abs(x["gap_pct"]), reverse=True)
    return results[:20]
