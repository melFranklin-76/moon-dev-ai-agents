"""
small_account_helpers.py
Helper functions for Small Account Dashboard v3.0
— market regime, sector data, XSP spread data, tendencies persistence,
  momentum universe scanner
"""

import csv
import math
import numpy as np
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
    min_rel_vol: float = 1.0,
) -> list:
    """
    Scan Yahoo Finance day_gainers + most_actives.
    Filter by momentum criteria, return list of result dicts sorted by % change.

    The very last entry in the returned list (if non-empty) carries no symbol
    and instead holds diagnostic counts so the UI can explain a zero result.
    Callers should filter out any row where `symbol` is falsy.
    """
    raw: dict = {}
    for screen in ("day_gainers", "most_actives"):
        for q in _fetch_screen(screen):
            sym = q.get("symbol", "")
            if sym and sym not in raw:
                raw[sym] = q

    # Per-filter rejection counts
    rejected = {"price": 0, "change": 0, "volume": 0, "rel_vol": 0}
    results = []
    for sym, q in raw.items():
        price   = float(q.get("regularMarketPrice", 0) or 0)
        change  = float(q.get("regularMarketChangePercent", 0) or 0)
        volume  = int(q.get("regularMarketVolume", 0) or 0)
        avg_vol = int(q.get("averageDailyVolume3Month", 1) or 1)
        rel_vol = round(volume / avg_vol, 2) if avg_vol > 0 else 0.0

        if not (min_price <= price <= max_price):
            rejected["price"] += 1
            continue
        if change < min_change:
            rejected["change"] += 1
            continue
        if volume < min_volume:
            rejected["volume"] += 1
            continue
        if rel_vol < min_rel_vol:
            rejected["rel_vol"] += 1
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

    # Append diagnostic sentinel row so the UI can show why zero passed
    results.append({
        "symbol": "",
        "_diag":  {"raw_count": len(raw), "rejected": rejected},
    })
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


# ── IV Rank ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_iv_rank(symbol: str) -> dict:
    """
    IV Rank for options buyers.

    Uses ATM implied volatility from the nearest weekly expiry and compares it
    to rolling historical realized volatility (HV20 / HV63) as a proxy for the
    52-week IV range.  Returns a grade — CHEAP / FAIR / RICH — with the key
    numbers so the trader knows exactly what they're paying for.

    CHEAP  →  IV below recent realised vol  →  buy options, small move = big profit
    FAIR   →  IV roughly in line            →  normal premium, trade on signal merit
    RICH   →  IV elevated vs recent moves   →  overpaying, need a BIG move to profit
    """
    try:
        t = yf.Ticker(symbol)

        # ── 1. current price ──────────────────────────────────────────────────
        hist5 = t.history(period='5d', interval='1d')
        if hist5.empty:
            return {"available": False}
        price = float(hist5['Close'].iloc[-1])

        # ── 2. ATM implied volatility from nearest expiry ─────────────────────
        exps = t.options
        if not exps:
            return {"available": False}
        chain  = t.option_chain(exps[0])
        calls  = chain.calls
        calls  = calls[calls['impliedVolatility'] > 0].copy()
        if calls.empty:
            return {"available": False}
        atm_idx  = (calls['strike'] - price).abs().argsort().iloc[0]
        atm_call = calls.iloc[atm_idx]
        current_iv = float(atm_call['impliedVolatility'])   # already annualised (0–1+)

        # ── 3. Historical realised volatility (annualised) ────────────────────
        hist1y = t.history(period='1y', interval='1d')
        if len(hist1y) < 30:
            return {"available": False}
        log_ret = np.log(hist1y['Close'] / hist1y['Close'].shift(1)).dropna()
        hv20    = float(log_ret.tail(20).std() * np.sqrt(252))
        hv63    = float(log_ret.tail(63).std() * np.sqrt(252))

        # ── 4. IV Rank: approximate 52-wk IV range via rolling HV windows ─────
        hv_roll = [
            float(log_ret.iloc[i:i+20].std() * np.sqrt(252))
            for i in range(0, max(len(log_ret) - 20, 1), 5)
        ]
        hv_min  = min(hv_roll)
        hv_max  = max(hv_roll)
        iv_rank = (
            (current_iv - hv_min) / (hv_max - hv_min) * 100
            if hv_max > hv_min else 50.0
        )
        iv_rank = round(min(max(iv_rank, 0), 100), 1)

        # ── 5. IV / HV ratio ──────────────────────────────────────────────────
        ratio = round(current_iv / hv20, 2) if hv20 > 0 else 1.0

        # ── 6. Grade ──────────────────────────────────────────────────────────
        if ratio < 0.85:
            grade = "CHEAP"
            color = "#2ecc71"
            emoji = "🟢"
            advice = (
                f"IV ({current_iv*100:.0f}%) is BELOW recent realised vol "
                f"({hv20*100:.0f}%). Options are a bargain — "
                f"a normal move pays well."
            )
        elif ratio > 1.40:
            grade = "RICH"
            color = "#e74c3c"
            emoji = "🔴"
            advice = (
                f"IV ({current_iv*100:.0f}%) is {ratio:.1f}x recent realised vol "
                f"({hv20*100:.0f}%). You are overpaying for premium — "
                f"the stock needs a BIG move just to break even. "
                f"Wait for IV to drop OR reduce size."
            )
        else:
            grade = "FAIR"
            color = "#f39c12"
            emoji = "🟡"
            advice = (
                f"IV ({current_iv*100:.0f}%) is roughly in line with recent "
                f"realised vol ({hv20*100:.0f}%). Normal premium — "
                f"trade on signal merit alone."
            )

        return {
            "available":  True,
            "symbol":     symbol,
            "current_iv": round(current_iv * 100, 1),   # % e.g. 45.2
            "hv20":       round(hv20 * 100, 1),
            "hv63":       round(hv63 * 100, 1),
            "ratio":      ratio,
            "iv_rank":    iv_rank,
            "grade":      grade,
            "color":      color,
            "emoji":      emoji,
            "advice":     advice,
            "expiry":     exps[0],
            "strike":     float(atm_call['strike']),
        }

    except Exception:
        return {"available": False}


# ── Relative Strength vs SPY ──────────────────────────────────────────────────
@st.cache_data(ttl=60)
def _get_spy_change() -> float:
    """SPY today % change — cached once, shared by every RS call."""
    try:
        df = yf.Ticker('SPY').history(period='2d', interval='1d')
        if len(df) < 2:
            return 0.0
        return float(
            (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
        )
    except Exception:
        return 0.0


@st.cache_data(ttl=60)
def get_rs_vs_spy(symbol: str) -> dict:
    """
    Real-time Relative Strength score vs SPY.

    RS = stock % change today / SPY % change today.

    Score 1-10:
      10  Stock UP while SPY DOWN   — strongest possible signal
       9  RS >= 3x                  — blazing momentum
       7  RS >= 2x                  — strong, momentum confirmed
       6  RS >= 1.2x                — slightly outperforming
       5  RS ~= 1x                  — moving with market
       3  RS < 0.8x                 — underperforming
       1  Stock DOWN while SPY UP   — avoid

    For call buying: target score >= 7 (STRONG or better).
    """
    try:
        df = yf.Ticker(symbol).history(period='2d', interval='1d')
        if len(df) < 2:
            return {"available": False}

        stock_chg = float(
            (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
        )
        spy_chg = _get_spy_change()

        # ── Determine label, color, score ─────────────────────────────────────
        if stock_chg > 0 and spy_chg <= 0:
            label, color, score = "LEADING ↑", "#2ecc71", 10
            rs   = 99.0
            desc = (f"{symbol} GREEN while SPY is flat/red — "
                    f"institutions are buying into weakness. Strongest RS signal.")

        elif stock_chg <= 0 and spy_chg > 0:
            label, color, score = "LAGGING ↓", "#e74c3c", 1
            rs   = -99.0
            desc = (f"{symbol} RED while SPY is green — "
                    f"distribution happening. Avoid calls here.")

        elif abs(spy_chg) < 0.05:
            label, color, score = "SPY FLAT", "#8b92a8", 5
            rs   = 1.0
            desc = f"SPY essentially flat — judge {symbol} ({stock_chg:+.1f}%) on its own merit."

        else:
            rs = stock_chg / spy_chg

            if rs >= 3.0:
                label, color, score = "BLAZING 🔥", "#2ecc71", 9
                desc = (f"{symbol} moving {rs:.1f}x faster than SPY — "
                        f"extremely strong relative momentum.")
            elif rs >= 2.0:
                label, color, score = "STRONG", "#2ecc71", 7
                desc = (f"Outpacing SPY by {rs:.1f}x — "
                        f"momentum confirmed. Good call candidate.")
            elif rs >= 1.2:
                label, color, score = "ABOVE MKT", "#f39c12", 6
                desc = (f"Slight outperformance ({rs:.1f}x). "
                        f"OK signal — look for stronger RS on A+ setups.")
            elif rs >= 0.8:
                label, color, score = "IN LINE", "#8b92a8", 5
                desc = (f"Moving with the market ({rs:.1f}x). "
                        f"No RS edge — rely entirely on price setup quality.")
            elif rs >= 0.0:
                label, color, score = "WEAK", "#e74c3c", 3
                desc = (f"Underperforming SPY ({rs:.1f}x). "
                        f"Market is dragging it up — reduce size or skip.")
            else:
                label, color, score = "VERY WEAK", "#e74c3c", 1
                desc = (f"Moving opposite to SPY ({rs:.1f}x). "
                        f"Active distribution — avoid.")

        stars = "★" * min(round(score / 2), 5) + "☆" * (5 - min(round(score / 2), 5))

        return {
            "available": True,
            "symbol":    symbol,
            "stock_chg": round(stock_chg, 2),
            "spy_chg":   round(spy_chg, 2),
            "rs":        round(rs, 2) if abs(rs) < 90 else rs,
            "label":     label,
            "color":     color,
            "score":     score,
            "stars":     stars,
            "desc":      desc,
        }

    except Exception:
        return {"available": False}


# ── Float + Short Interest / Squeeze Score ────────────────────────────────────
@st.cache_data(ttl=3600)   # float/SI data updates daily — cache 1 hour
def get_squeeze_score(symbol: str) -> dict:
    """
    Squeeze Score: Float + Short Interest = potential energy for a short squeeze.

    Low float (few shares) + high short interest (many shorts trapped) +
    a catalyst = the recipe for a 20-100%+ intraday move.

    Scoring (0-100):
      Float component  (40 pts max):
        < 5M shares  → 40 pts   🔥 micro-float
        < 10M        → 30 pts
        < 50M        → 15 pts
        < 100M       →  5 pts
        >= 100M      →  0 pts

      Short Interest % of float  (40 pts max):
        > 30%  → 40 pts   heavy short load
        > 20%  → 30 pts
        > 10%  → 20 pts
        >  5%  → 10 pts
        <=  5% →  0 pts

      Days to Cover / Short Ratio  (20 pts max):
        > 5 days → 20 pts   shorts can't exit fast
        > 3 days → 10 pts
        > 1 day  →  5 pts

    Grade:
      75-100 → 🔥 SQUEEZE CANDIDATE
      50-74  → ⚡ ELEVATED PRESSURE
      25-49  → 📊 MODERATE
       0-24  → ➖ LOW
    """
    try:
        info = yf.Ticker(symbol).info

        float_shares = int(info.get('floatShares', 0) or 0)
        shares_short = int(info.get('sharesShort', 0) or 0)
        short_ratio  = float(info.get('shortRatio', 0) or 0)       # days to cover
        short_pct    = float(info.get('shortPercentOfFloat', 0) or 0) * 100

        if float_shares == 0:
            return {"available": False}

        # ── Float score ───────────────────────────────────────────────────────
        if float_shares < 5_000_000:
            float_pts, float_label = 40, f"{float_shares/1e6:.1f}M 🔥 MICRO"
        elif float_shares < 10_000_000:
            float_pts, float_label = 30, f"{float_shares/1e6:.1f}M 🔥 LOW"
        elif float_shares < 50_000_000:
            float_pts, float_label = 15, f"{float_shares/1e6:.0f}M moderate"
        elif float_shares < 100_000_000:
            float_pts, float_label = 5,  f"{float_shares/1e6:.0f}M large"
        else:
            float_pts, float_label = 0,  f"{float_shares/1e6:.0f}M heavy"

        # ── Short Interest score ──────────────────────────────────────────────
        if short_pct > 30:
            si_pts, si_label = 40, f"{short_pct:.1f}% 🔥 HEAVILY SHORTED"
        elif short_pct > 20:
            si_pts, si_label = 30, f"{short_pct:.1f}% HIGH"
        elif short_pct > 10:
            si_pts, si_label = 20, f"{short_pct:.1f}% elevated"
        elif short_pct > 5:
            si_pts, si_label = 10, f"{short_pct:.1f}% moderate"
        else:
            si_pts, si_label = 0,  f"{short_pct:.1f}% low"

        # ── Days-to-cover score ───────────────────────────────────────────────
        if short_ratio > 5:
            dtc_pts, dtc_label = 20, f"{short_ratio:.1f} days 🔥 trapped"
        elif short_ratio > 3:
            dtc_pts, dtc_label = 10, f"{short_ratio:.1f} days elevated"
        elif short_ratio > 1:
            dtc_pts, dtc_label =  5, f"{short_ratio:.1f} days moderate"
        else:
            dtc_pts, dtc_label =  0, f"{short_ratio:.1f} days easy cover"

        total = float_pts + si_pts + dtc_pts

        # ── Grade ─────────────────────────────────────────────────────────────
        if total >= 75:
            grade, color, emoji = "SQUEEZE CANDIDATE", "#2ecc71", "🔥"
            advice = (
                "Low float + heavy short load = one catalyst away from a "
                "violent squeeze. Watch for volume spike as the trigger."
            )
        elif total >= 50:
            grade, color, emoji = "ELEVATED PRESSURE", "#f39c12", "⚡"
            advice = (
                "Significant short interest. A strong catalyst could force "
                "covering and amplify the move beyond the normal range."
            )
        elif total >= 25:
            grade, color, emoji = "MODERATE", "#8b92a8", "📊"
            advice = "Some short pressure but not squeeze territory."
        else:
            grade, color, emoji = "LOW", "#8b92a8", "➖"
            advice = "High float or low short interest — moves driven by buyers, not shorts covering."

        return {
            "available":    True,
            "symbol":       symbol,
            "float_shares": float_shares,
            "float_label":  float_label,
            "float_pts":    float_pts,
            "short_pct":    round(short_pct, 1),
            "si_label":     si_label,
            "si_pts":       si_pts,
            "short_ratio":  round(short_ratio, 1),
            "dtc_label":    dtc_label,
            "dtc_pts":      dtc_pts,
            "score":        total,
            "grade":        grade,
            "color":        color,
            "emoji":        emoji,
            "advice":       advice,
        }

    except Exception:
        return {"available": False}


# ── Max Pain ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_max_pain(symbol: str) -> dict:
    """
    Max Pain: the strike price where option sellers (market makers) collect
    the most premium — i.e. where the most open interest expires worthless.

    Price gravitates toward max pain as expiration approaches. The pull is
    strongest in the final 3–5 days before expiry (pinning effect).

    Algorithm: for each possible expiry strike, calculate the total intrinsic
    value that would be paid out to ALL option holders. The strike with the
    LOWEST total payout = max pain for option buyers = max profit for sellers.

    Magnetic pull strength:
      ≤ 2 days  → very strong pin  (MMs actively defend)
      ≤ 5 days  → strong pull
      ≤ 14 days → moderate         (worth watching)
      > 14 days → weak             (too early to matter much)
    """
    try:
        t    = yf.Ticker(symbol)
        exps = t.options
        if not exps:
            return {"available": False}

        # Current price
        hist = t.history(period='1d', interval='1m')
        if hist.empty:
            return {"available": False}
        price  = float(hist['Close'].iloc[-1])
        expiry = exps[0]

        chain = t.option_chain(expiry)
        calls = chain.calls[['strike', 'openInterest']].copy()
        puts  = chain.puts[['strike',  'openInterest']].copy()
        calls['openInterest'] = calls['openInterest'].fillna(0).astype(int)
        puts['openInterest']  = puts['openInterest'].fillna(0).astype(int)

        strikes = sorted(set(calls['strike'].tolist() + puts['strike'].tolist()))
        if len(strikes) < 3:
            return {"available": False}

        # ── Calculate total pain at each strike ───────────────────────────────
        pain = {}
        for s in strikes:
            call_pain = sum(
                (s - r['strike']) * r['openInterest'] * 100
                for _, r in calls.iterrows() if r['strike'] < s
            )
            put_pain = sum(
                (r['strike'] - s) * r['openInterest'] * 100
                for _, r in puts.iterrows() if r['strike'] > s
            )
            pain[s] = call_pain + put_pain

        max_pain_strike = min(pain, key=pain.get)

        # ── Direction & distance ──────────────────────────────────────────────
        diff     = max_pain_strike - price
        diff_pct = diff / price * 100

        # ── Days to expiry ────────────────────────────────────────────────────
        exp_date    = datetime.strptime(expiry, '%Y-%m-%d').date()
        days_to_exp = (exp_date - datetime.now().date()).days

        if days_to_exp <= 2:
            pull_label = "🧲 VERY STRONG PIN"
            pull_color = "#e74c3c"
            pull_note  = "Final days — MMs actively defending max pain. High probability of pin."
        elif days_to_exp <= 5:
            pull_label = "🧲 STRONG PULL"
            pull_color = "#f39c12"
            pull_note  = "Inside 5 days — price likely drifting toward max pain this week."
        elif days_to_exp <= 14:
            pull_label = "📍 MODERATE"
            pull_color = "#8b92a8"
            pull_note  = "Worth noting but too early for strong pin action."
        else:
            pull_label = "📍 WEAK"
            pull_color = "#8b92a8"
            pull_note  = f"Expiry {days_to_exp} days out — max pain matters more in final week."

        if abs(diff) < 0.50:
            pin_status = "📌 PRICE AT MAX PAIN — watch for chop / consolidation"
            pin_color  = "#f39c12"
        elif diff > 0:
            pin_status = f"↑ Max pain ${max_pain_strike:.0f} is ABOVE price — gravitational pull UP"
            pin_color  = "#2ecc71"
        else:
            pin_status = f"↓ Max pain ${max_pain_strike:.0f} is BELOW price — gravitational pull DOWN"
            pin_color  = "#e74c3c"

        # Top 5 strikes by open interest for the pain curve chart
        pain_items = sorted(pain.items(), key=lambda x: x[0])

        return {
            "available":        True,
            "symbol":           symbol,
            "expiry":           expiry,
            "days_to_exp":      days_to_exp,
            "current_price":    round(price, 2),
            "max_pain_strike":  max_pain_strike,
            "diff":             round(diff, 2),
            "diff_pct":         round(diff_pct, 1),
            "pin_status":       pin_status,
            "pin_color":        pin_color,
            "pull_label":       pull_label,
            "pull_color":       pull_color,
            "pull_note":        pull_note,
            "pain_strikes":     [x[0] for x in pain_items],
            "pain_values":      [x[1] for x in pain_items],
        }

    except Exception:
        return {"available": False}


# ── Intraday Sector Money Flow ─────────────────────────────────────────────────
_SECTORS = {
    'XLK':  'Technology',
    'XLV':  'Healthcare',
    'XLF':  'Financials',
    'XLE':  'Energy',
    'XLI':  'Industrials',
    'XLY':  'Consumer Disc',
    'XLP':  'Consumer Staples',
    'XLB':  'Materials',
    'XLC':  'Communications',
    'XLU':  'Utilities',
}


@st.cache_data(ttl=60)
def get_intraday_sector_flow() -> list:
    """
    Where is hot money rotating RIGHT NOW — last 30 minutes of sector action.

    For each sector ETF:
      - 30-min % change  (where it's been)
      - RS vs SPY 30-min (outperforming or lagging the broad market)
      - Acceleration     (is the move speeding up or fading?)
      - Volume ratio     (last 30 min vs prior 30 min — confirms conviction)
      - Arrow            (↑↑ surging · ↑ rising · → flat · ↓ fading · ↓↓ dumping)

    Sorted by RS vs SPY so the hottest sector is always at the top.

    Trading rule: if top-ranked sector has RS > +0.2% and vol_ratio > 1.2,
    look for momentum setups in stocks from that sector first.
    """
    try:
        # ── SPY baseline (30-min and 15-min segments) ─────────────────────────
        spy_df = yf.Ticker('SPY').history(period='1d', interval='5m')
        if len(spy_df) < 7:
            return []
        spy_30m  = float(
            (spy_df['Close'].iloc[-1] - spy_df['Close'].iloc[-7]) /
             spy_df['Close'].iloc[-7] * 100
        )
        spy_15m_r = float(
            (spy_df['Close'].iloc[-1] - spy_df['Close'].iloc[-4]) /
             spy_df['Close'].iloc[-4] * 100
        )
        spy_15m_p = float(
            (spy_df['Close'].iloc[-4] - spy_df['Close'].iloc[-7]) /
             spy_df['Close'].iloc[-7] * 100
        )
    except Exception:
        return []

    results = []
    for sym, name in _SECTORS.items():
        try:
            df = yf.Ticker(sym).history(period='1d', interval='5m')
            if len(df) < 7:
                continue

            close = df['Close']

            # 30-min change
            chg_30m = float(
                (close.iloc[-1] - close.iloc[-7]) / close.iloc[-7] * 100
            )

            # Two 15-min halves for acceleration
            chg_15m_r = float(
                (close.iloc[-1] - close.iloc[-4]) / close.iloc[-4] * 100
            )
            chg_15m_p = float(
                (close.iloc[-4] - close.iloc[-7]) / close.iloc[-7] * 100
            )
            accel = chg_15m_r - chg_15m_p   # positive = speeding up

            # RS vs SPY for the last 30 min
            rs_30m = chg_30m - spy_30m

            # Volume conviction (last 30 min vs prior 30 min)
            vol_now  = df['Volume'].iloc[-7:].sum()
            vol_prev = df['Volume'].iloc[-14:-7].sum() if len(df) >= 14 else vol_now
            vol_ratio = round(vol_now / vol_prev, 2) if vol_prev > 0 else 1.0

            # Trend arrow
            if accel > 0.15:   arrow = "↑↑"
            elif accel > 0.03: arrow = "↑"
            elif accel > -0.03: arrow = "→"
            elif accel > -0.15: arrow = "↓"
            else:               arrow = "↓↓"

            # Flow label
            if rs_30m > 0.3 and vol_ratio > 1.3:
                flow_label, flow_color = "🔥 HOT INFLOW",  "#2ecc71"
            elif rs_30m > 0.1:
                flow_label, flow_color = "↗ INFLOW",       "#2ecc71"
            elif rs_30m > -0.1:
                flow_label, flow_color = "→ NEUTRAL",      "#8b92a8"
            elif rs_30m > -0.3:
                flow_label, flow_color = "↘ OUTFLOW",      "#e74c3c"
            else:
                flow_label, flow_color = "🧊 COLD DUMP",   "#e74c3c"

            results.append({
                "symbol":     sym,
                "name":       name,
                "price":      round(float(close.iloc[-1]), 2),
                "chg_30m":   round(chg_30m, 3),
                "rs_30m":    round(rs_30m, 3),
                "accel":     round(accel, 3),
                "arrow":     arrow,
                "vol_ratio": vol_ratio,
                "flow_label": flow_label,
                "flow_color": flow_color,
            })

        except Exception:
            continue

    results.sort(key=lambda x: x['rs_30m'], reverse=True)
    return results


# ── Composite Signal Strength (Simple Mode) ────────────────────────────────────
def get_signal_strength(symbol: str) -> dict:
    """
    Aggregate all 5 insider layers into one 0–10 score for Simple Mode.

    Layer weights:
      RS vs SPY     0–2 pts  (confirms market tailwind)
      IV Rank       0–2 pts  (options are cheap = good, rich = bad)
      Squeeze Score 0–2 pts  (short squeeze potential)
      Max Pain      0–2 pts  (price moving toward max pain = tailwind)
      Liquidity     0–2 pts  (can actually trade the option)

    Grade:
      8–10 → 🟢 STRONG SETUP   — all systems green, high confidence
      5–7  → 🟡 MODERATE        — tradeable but check the weak layers
      0–4  → 🔴 WEAK / SKIP     — one or more critical layers failing

    Designed for Simple Mode cards and the future iPhone app.
    Each sub-score is explained so the user knows exactly WHY.
    """
    score  = 0
    detail = {}

    # ── 1. RS vs SPY (0–2) ───────────────────────────────────────────────────
    rs = get_rs_vs_spy(symbol)
    if rs.get("available"):
        if rs['score'] >= 7:
            rs_pts, rs_note = 2, "Market confirming ✅"
        elif rs['score'] >= 5:
            rs_pts, rs_note = 1, "Neutral vs market"
        else:
            rs_pts, rs_note = 0, "Lagging market ❌"
    else:
        rs_pts, rs_note = 1, "RS data unavailable"
    score += rs_pts
    detail['rs'] = {'pts': rs_pts, 'note': rs_note,
                    'label': rs.get('label', '—'), 'color': rs.get('color', '#8b92a8')}

    # ── 2. IV Rank (0–2) ─────────────────────────────────────────────────────
    iv = get_iv_rank(symbol)
    if iv.get("available"):
        if iv['grade'] == 'CHEAP':
            iv_pts, iv_note = 2, "Options cheap ✅"
        elif iv['grade'] == 'FAIR':
            iv_pts, iv_note = 1, "Options fairly priced"
        else:
            iv_pts, iv_note = 0, "Options overpriced ❌"
    else:
        iv_pts, iv_note = 1, "IV data unavailable"
    score += iv_pts
    detail['iv'] = {'pts': iv_pts, 'note': iv_note,
                    'grade': iv.get('grade', '—'), 'color': iv.get('color', '#8b92a8')}

    # ── 3. Squeeze Score (0–2) ───────────────────────────────────────────────
    sq = get_squeeze_score(symbol)
    if sq.get("available"):
        if sq['score'] >= 60:
            sq_pts, sq_note = 2, "Squeeze fuel ✅"
        elif sq['score'] >= 30:
            sq_pts, sq_note = 1, "Some short pressure"
        else:
            sq_pts, sq_note = 0, "Low squeeze potential"
    else:
        sq_pts, sq_note = 0, "Squeeze data unavailable"
    score += sq_pts
    detail['sq'] = {'pts': sq_pts, 'note': sq_note,
                    'score': sq.get('score', 0), 'color': sq.get('color', '#8b92a8')}

    # ── 4. Max Pain direction (0–2) ──────────────────────────────────────────
    mp = get_max_pain(symbol)
    if mp.get("available"):
        if mp['diff'] > 0.5:          # max pain above price = pull up
            mp_pts, mp_note = 2, "Max pain pulling UP ✅"
        elif abs(mp['diff']) <= 0.5:  # at max pain = pin risk
            mp_pts, mp_note = 1, "At max pain — chop risk"
        else:                          # max pain below = pull down
            mp_pts, mp_note = 0, "Max pain pulling DOWN ❌"
    else:
        mp_pts, mp_note = 1, "Max pain data unavailable"
    score += mp_pts
    detail['mp'] = {'pts': mp_pts, 'note': mp_note,
                    'strike': mp.get('max_pain_strike', 0),
                    'color': mp.get('pull_color', '#8b92a8')}

    # ── 5. Options Liquidity (0–2) ───────────────────────────────────────────
    opt = get_options_snapshot(symbol)
    if opt.get("available") and opt.get("calls"):
        any_liquid = any(r['liquid'] for r in opt['calls'])
        if any_liquid:
            liq_pts, liq_note = 2, "Options liquid ✅"
        else:
            liq_pts, liq_note = 0, "Wide spreads / low OI ❌"
    else:
        liq_pts, liq_note = 1, "Liquidity data unavailable"
    score += liq_pts
    detail['liq'] = {'pts': liq_pts, 'note': liq_note}

    # ── Grade ─────────────────────────────────────────────────────────────────
    if score >= 8:
        grade, color, emoji, advice = (
            "STRONG SETUP", "#2ecc71", "🟢",
            "All systems green. High confidence — trade your plan."
        )
    elif score >= 5:
        grade, color, emoji, advice = (
            "MODERATE", "#f39c12", "🟡",
            "Tradeable but check the weak layers below before entering."
        )
    else:
        grade, color, emoji, advice = (
            "WEAK / SKIP", "#e74c3c", "🔴",
            "Too many red flags. Better setups will come — wait."
        )

    stars = "★" * score + "☆" * (10 - score)

    return {
        "symbol": symbol,
        "score":  score,
        "grade":  grade,
        "color":  color,
        "emoji":  emoji,
        "stars":  stars,
        "advice": advice,
        "detail": detail,
    }


# ── IV Surface Scanner (multi-expiration) ────────────────────────────────────
def scan_iv_surface(
    symbol: str,
    dte_min: int = 7,
    dte_max: int = 60,
    opt_type: str = "calls",   # "calls" or "puts"
    min_oi: int = 10,
    min_vol: int = 0,
    delta_min: float = 0.10,
    delta_max: float = 0.75,
) -> dict:
    """
    Multi-expiration IV surface scan.

    For each expiration in [dte_min, dte_max], fit a quadratic smile to the
    selected option type, compute residuals (actual_IV − fitted_IV), and
    rank every option by how cheap (residual < 0) or rich (residual > 0)
    it sits vs its smile.

    Returns:
      {
        "available": True,
        "symbol": symbol,
        "spot": float,
        "expirations": [...list of "YYYY-MM-DD" strings...],
        "per_expiry": {
            "YYYY-MM-DD": {
                "dte": int,
                "strikes": np.array,
                "ivs":     np.array,
                "fitted":  np.array,
                "residuals_pp": np.array,
                "df": pd.DataFrame with columns:
                    strike, bid, ask, mid, iv_pct, fitted_iv_pct, residual_pp,
                    delta, oi, volume, spread_pp, spread_warn (bool), oi_warn (bool)
            },
            ...
        },
        "top_candidates": pd.DataFrame with top 10 cheapest options across
            ALL expirations.
      }

    On failure (no data, <5 strikes in any expiry, etc): {"available": False}
    """
    try:
        t = yf.Ticker(symbol)
        exps = t.options
        if not exps:
            return {"available": False}

        # ── Spot ──────────────────────────────────────────────────────────────
        hist = t.history(period='2d', interval='1d')
        if hist.empty:
            return {"available": False}
        spot = float(hist['Close'].iloc[-1])

        now_ts = pd.Timestamp.now()
        per_expiry: dict = {}
        good_expiries: list = []
        all_rows: list = []

        for exp in exps:
            try:
                exp_ts = pd.Timestamp(exp)
                dte = (exp_ts - now_ts).days
                if dte < dte_min or dte > dte_max:
                    continue

                chain = t.option_chain(exp)
                df = (chain.calls if opt_type == "calls" else chain.puts).copy()
                if df is None or df.empty:
                    continue

                # ── Basic filters ────────────────────────────────────────────
                df = df[
                    (df['impliedVolatility'] > 0.01) &
                    (df['strike'] >= spot * 0.70) &
                    (df['strike'] <= spot * 1.50)
                ].reset_index(drop=True)

                # Open interest / volume gates
                df['openInterest'] = df.get('openInterest', 0).fillna(0).astype(int)
                df['volume']       = df.get('volume', 0).fillna(0).astype(int)
                df = df[(df['openInterest'] >= min_oi) & (df['volume'] >= min_vol)].reset_index(drop=True)

                if len(df) < 5:
                    continue

                strikes = df['strike'].values.astype(float)
                ivs     = df['impliedVolatility'].values.astype(float)

                # ── Quadratic smile fit ──────────────────────────────────────
                coeffs = np.polyfit(strikes, ivs, 2)
                fitted = np.polyval(coeffs, strikes)
                residuals_pp = (ivs - fitted) * 100.0

                # ── Black-Scholes delta per row (no risk-free rate) ──────────
                T = max(dte, 1) / 365.0
                deltas = np.zeros(len(df))
                for i, (k, iv) in enumerate(zip(strikes, ivs)):
                    try:
                        if iv <= 0 or T <= 0 or k <= 0:
                            deltas[i] = 0.0
                            continue
                        d1 = (math.log(spot / k) + 0.5 * iv * iv * T) / (iv * math.sqrt(T))
                        n_d1 = 0.5 * (1.0 + math.erf(d1 / math.sqrt(2)))
                        if opt_type == "calls":
                            deltas[i] = n_d1
                        else:
                            deltas[i] = n_d1 - 1.0
                    except Exception:
                        deltas[i] = 0.0

                # ── Bid/ask/mid/spread ───────────────────────────────────────
                bids = df.get('bid', 0).fillna(0).astype(float).values
                asks = df.get('ask', 0).fillna(0).astype(float).values
                mids = (bids + asks) / 2.0
                spread_pp = np.where(mids > 0, (asks - bids) / mids * 100.0, 0.0)

                spread_warn = spread_pp > 10.0
                oi_warn = df['openInterest'].values < 50

                # ── Delta filter (absolute value for puts) ───────────────────
                abs_deltas = np.abs(deltas)
                keep_mask = (abs_deltas >= delta_min) & (abs_deltas <= delta_max)

                if keep_mask.sum() < 1:
                    # Not enough rows after delta filter — still keep the smile data
                    # but skip if everything filtered out
                    continue

                # Build the filtered DataFrame for display / candidates
                out_df = pd.DataFrame({
                    'strike':        strikes,
                    'bid':           bids,
                    'ask':           asks,
                    'mid':           mids,
                    'iv_pct':        ivs * 100.0,
                    'fitted_iv_pct': fitted * 100.0,
                    'residual_pp':   residuals_pp,
                    'delta':         deltas,
                    'oi':            df['openInterest'].values,
                    'volume':        df['volume'].values,
                    'spread_pp':     spread_pp,
                    'spread_warn':   spread_warn,
                    'oi_warn':       oi_warn,
                })
                out_df = out_df[keep_mask].reset_index(drop=True)
                if len(out_df) < 1:
                    continue

                per_expiry[exp] = {
                    'dte':          int(dte),
                    'strikes':      strikes,
                    'ivs':          ivs,
                    'fitted':       fitted,
                    'residuals_pp': residuals_pp,
                    'df':           out_df,
                }
                good_expiries.append(exp)

                # Collect rows for top-candidates table
                tc_rows = out_df.copy()
                tc_rows['expiry'] = exp
                tc_rows['dte']    = int(dte)
                all_rows.append(tc_rows)

            except Exception:
                continue

        if not good_expiries:
            return {"available": False}

        # ── Build top_candidates across all expirations ──────────────────────
        if all_rows:
            all_df = pd.concat(all_rows, ignore_index=True)
            top_candidates = all_df.sort_values('residual_pp', ascending=True).head(10).reset_index(drop=True)
            top_candidates = top_candidates[[
                'expiry', 'dte', 'strike', 'mid', 'iv_pct', 'residual_pp',
                'delta', 'oi', 'volume', 'spread_pp', 'spread_warn', 'oi_warn',
            ]]
        else:
            top_candidates = pd.DataFrame()

        return {
            "available":      True,
            "symbol":         symbol,
            "spot":           spot,
            "expirations":    good_expiries,
            "per_expiry":     per_expiry,
            "top_candidates": top_candidates,
        }

    except Exception:
        return {"available": False}


# ── Best Buy Strike (IV Surface Fitting) ──────────────────────────────────────
@st.cache_data(ttl=300)
def get_best_buy_strike(symbol: str) -> dict:
    """
    Find the best-value CALL to BUY on the nearest expiry.

    Method:
      1. Pull the calls chain for the nearest expiry.
      2. Filter to strikes within 70%–150% of spot with valid IV.
      3. Fit a quadratic (smile) curve to the (strike, IV) data.
      4. Compute residuals: actual_IV − fitted_IV for every strike.
      5. The most-negative residual = strike priced cheapest vs its neighbors.

    A negative residual means that option is on sale relative to what the
    volatility smile implies it should cost.  The larger the discount (in
    percentage-point terms, PP), the better the value for a call BUYER.

    Grades:
      VERY CHEAP  < −5 PP  → genuine mispricing, check OI / bid-ask first
      CHEAP       < −3 PP  → solid discount, worth prioritising
      SLIGHT DISC < −1 PP  → minor edge, trade on signal merit
      FAIR              else → uniformly priced chain, no relative edge
    """
    try:
        t    = yf.Ticker(symbol)
        exps = t.options
        if not exps:
            return {"available": False}

        # ── 1. Current price ──────────────────────────────────────────────────
        hist = t.history(period='2d', interval='1d')
        if hist.empty:
            return {"available": False}
        price = float(hist['Close'].iloc[-1])

        # ── 2. Nearest expiry calls, cleaned ──────────────────────────────────
        chain = t.option_chain(exps[0])
        calls = chain.calls.copy()
        calls = calls[
            (calls['impliedVolatility'] > 0.01) &
            (calls['strike'] >= price * 0.70) &
            (calls['strike'] <= price * 1.50)
        ].reset_index(drop=True)

        if len(calls) < 5:
            return {"available": False}

        strikes = calls['strike'].values.astype(float)
        ivs     = calls['impliedVolatility'].values.astype(float)

        # ── 3. Fit quadratic smile ────────────────────────────────────────────
        coeffs     = np.polyfit(strikes, ivs, 2)
        fitted_ivs = np.polyval(coeffs, strikes)

        # ── 4. Residuals (negative = cheaper than the smile suggests) ─────────
        residuals = ivs - fitted_ivs

        # ── 5. Best buy = most negative residual ──────────────────────────────
        best_idx       = int(np.argmin(residuals))
        best_strike    = float(strikes[best_idx])
        best_iv        = float(ivs[best_idx])
        best_fitted_iv = float(fitted_ivs[best_idx])
        residual_pp    = float(residuals[best_idx]) * 100   # to percentage points

        # ── 6. Option details for that strike ─────────────────────────────────
        row = calls.iloc[best_idx]
        oi  = int(row.get('openInterest', 0) or 0)
        bid = float(row.get('bid', 0) or 0)
        ask = float(row.get('ask', 0) or 0)

        # ── 7. Approximate Black-Scholes delta (no risk-free rate) ────────────
        try:
            exp_ts      = pd.Timestamp(exps[0])
            days_to_exp = max((exp_ts - pd.Timestamp.now()).days, 1)
            T           = days_to_exp / 365.0
            d1          = (math.log(price / best_strike) + 0.5 * best_iv ** 2 * T) / (
                            best_iv * math.sqrt(T)
                          )
            delta       = round(0.5 * (1.0 + math.erf(d1 / math.sqrt(2))), 2)
        except Exception:
            days_to_exp = 0
            delta       = 0.50

        # ── 8. Grade ──────────────────────────────────────────────────────────
        if residual_pp < -5:
            grade, color, emoji = "VERY CHEAP", "#2ecc71", "🟢"
            advice = (
                f"${best_strike:.2f} call is {abs(residual_pp):.1f} PP below the "
                f"smile — market is pricing it well below its neighbours. "
                f"Verify OI ({oi:,}) and spread before entering."
            )
        elif residual_pp < -3:
            grade, color, emoji = "CHEAP", "#2ecc71", "🟢"
            advice = (
                f"${best_strike:.2f} call sits {abs(residual_pp):.1f} PP cheap vs "
                f"the fitted smile. Solid relative value for a call buyer."
            )
        elif residual_pp < -1:
            grade, color, emoji = "SLIGHT DISCOUNT", "#f39c12", "🟡"
            advice = (
                f"${best_strike:.2f} call is marginally cheap ({residual_pp:+.1f} PP). "
                f"Minor edge — rely on your price setup, not the discount alone."
            )
        else:
            grade, color, emoji = "FAIRLY PRICED", "#8b92a8", "⬜"
            advice = (
                f"Chain is uniformly priced — no relative edge on any strike. "
                f"${best_strike:.2f} is the closest to fair value."
            )

        return {
            "available":      True,
            "symbol":         symbol,
            "expiry":         exps[0],
            "best_strike":    best_strike,
            "iv_pct":         round(best_iv * 100, 1),
            "fitted_iv_pct":  round(best_fitted_iv * 100, 1),
            "residual_pp":    round(residual_pp, 1),
            "oi":             oi,
            "bid":            bid,
            "ask":            ask,
            "delta":          delta,
            "days_to_exp":    days_to_exp,
            "strikes_scanned": len(calls),
            "grade":          grade,
            "color":          color,
            "emoji":          emoji,
            "advice":         advice,
        }

    except Exception:
        return {"available": False}


# ── Volume Spike / Capitulation Signal ───────────────────────────────────────
@st.cache_data(ttl=60)
def get_volume_spike(symbol: str) -> dict:
    """
    Detects unusual volume vs 20-bar average on 5-min bars.
    Returns spike ratio, direction, grade, color, emoji, advice.
    """
    try:
        df = yf.Ticker(symbol).history(period='2d', interval='5m')
        if df.empty or len(df) < 22:
            return {"available": False}

        df = df.copy()
        df['avg_vol'] = df['Volume'].rolling(20).mean()
        df = df.dropna(subset=['avg_vol'])
        if df.empty:
            return {"available": False}

        cur_vol  = int(df['Volume'].iloc[-1])
        avg_vol  = float(df['avg_vol'].iloc[-1])
        if avg_vol <= 0:
            return {"available": False}

        spike_ratio = cur_vol / avg_vol
        last_close  = float(df['Close'].iloc[-1])
        prev_close  = float(df['Close'].iloc[-2])
        direction   = "UP" if last_close >= prev_close else "DOWN"

        if spike_ratio >= 3.0:
            grade, color, emoji = "CAPITULATION", "#ff4444", "🔥"
        elif spike_ratio >= 2.0:
            grade, color, emoji = "HIGH VOLUME", "#ff8c00", "⚡"
        elif spike_ratio >= 1.5:
            grade, color, emoji = "ELEVATED", "#ffd700", "📈"
        else:
            grade, color, emoji = "NORMAL", "#888888", "💤"

        if grade == "CAPITULATION" and direction == "DOWN":
            advice = "Possible reversal — watch for bounce entry"
        elif grade == "CAPITULATION" and direction == "UP":
            advice = "Momentum surge — breakout or blow-off top"
        elif grade == "HIGH VOLUME":
            advice = "Watch for follow-through"
        else:
            advice = "No unusual volume"

        return {
            "available":   True,
            "spike_ratio": round(spike_ratio, 2),
            "direction":   direction,
            "grade":       grade,
            "color":       color,
            "emoji":       emoji,
            "advice":      advice,
            "avg_vol":     int(avg_vol),
            "cur_vol":     cur_vol,
        }
    except Exception:
        return {"available": False}


# ── Earnings Date & Risk ───────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_earnings_date(symbol: str) -> dict:
    """
    Next earnings date and risk grade for a call BUYER.

    Earnings = IV spike before, IV crush immediately after.
    Buying calls into earnings at a $250 account is an account killer.

    Risk grades:
      DANGER    ≤ 3 days  — do not buy calls, IV crush is imminent
      HIGH RISK ≤ 7 days  — IV already inflated, exit before announcement
      CAUTION   ≤ 14 days — on radar, plan your exit date
      WATCH     ≤ 30 days — not immediate, keep it in mind
      CLEAR     > 30 days — no near-term crush risk
    """
    try:
        t       = yf.Ticker(symbol)
        now_utc = pd.Timestamp.now(tz='UTC')
        next_dt = None

        # ── Method 1: earnings_dates DataFrame (most reliable) ────────────────
        try:
            ed = t.earnings_dates
            if ed is not None and not ed.empty:
                future = ed[ed.index > now_utc]
                if not future.empty:
                    next_dt = future.index.min()   # soonest upcoming
        except Exception:
            pass

        # ── Method 2: calendar dict / DataFrame (fallback) ───────────────────
        if next_dt is None:
            try:
                cal = t.calendar
                if isinstance(cal, dict):
                    for raw in cal.get('Earnings Date', []):
                        ts = pd.Timestamp(raw)
                        if ts.tzinfo is None:
                            ts = ts.tz_localize('UTC')
                        if ts > now_utc:
                            if next_dt is None or ts < next_dt:
                                next_dt = ts
                elif isinstance(cal, pd.DataFrame) and not cal.empty:
                    for col in ['Earnings Date', 'Earnings date']:
                        if col in cal.columns:
                            for raw in cal[col].dropna():
                                ts = pd.Timestamp(raw)
                                if ts.tzinfo is None:
                                    ts = ts.tz_localize('UTC')
                                if ts > now_utc:
                                    if next_dt is None or ts < next_dt:
                                        next_dt = ts
            except Exception:
                pass

        if next_dt is None:
            return {"available": False}

        if next_dt.tzinfo is None:
            next_dt = next_dt.tz_localize('UTC')

        days     = max((next_dt - now_utc).days, 0)
        date_str = next_dt.strftime('%b %d')

        # ── Risk grade ────────────────────────────────────────────────────────
        if days <= 3:
            grade, color, emoji = "DANGER",    "#e74c3c", "🚨"
            advice = (
                f"Earnings {date_str} ({days}d). DO NOT buy calls — "
                f"IV crushes the moment results drop. Any premium gain vanishes overnight."
            )
        elif days <= 7:
            grade, color, emoji = "HIGH RISK", "#e74c3c", "⚠️"
            advice = (
                f"Earnings {date_str} ({days}d). IV already inflated — "
                f"you're paying extra for a coin flip. Exit before or skip."
            )
        elif days <= 14:
            grade, color, emoji = "CAUTION",   "#f39c12", "⚠️"
            advice = (
                f"Earnings {date_str} ({days}d). "
                f"Plan your exit before the date — don't hold through it."
            )
        elif days <= 30:
            grade, color, emoji = "WATCH",     "#f39c12", "👀"
            advice = f"Earnings {date_str} ({days}d). On radar — not immediate."
        else:
            grade, color, emoji = "CLEAR",     "#2ecc71", "✅"
            advice = f"Next earnings {date_str} ({days}d). No near-term crush risk."

        return {
            "available": True,
            "symbol":    symbol,
            "date_str":  date_str,
            "days":      days,
            "grade":     grade,
            "color":     color,
            "emoji":     emoji,
            "advice":    advice,
        }

    except Exception:
        return {"available": False}
