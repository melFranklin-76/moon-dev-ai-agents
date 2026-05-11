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
            "symbol":      sym,
            "name":        q.get("shortName", sym),
            "price":       price,
            "change":      change,
            "volume":      volume,
            "rel_vol":     rel_vol,
            "has_options": _has_options(sym),
        })

    results.sort(key=lambda x: x["change"], reverse=True)
    return results
