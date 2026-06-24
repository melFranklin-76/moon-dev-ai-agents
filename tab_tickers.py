"""Tab 2 — My Tickers: Simple/Pro mode watchlist cards."""
import streamlit as st
import pandas as pd


def render(tab, *, snapshots, _watchlist, last_updated,
           get_signal_strength, get_earnings_date, get_options_snapshot,
           get_iv_rank, get_rs_vs_spy, get_squeeze_score, get_max_pain,
           get_best_buy_strike, get_volume_spike, get_rvol):
    with tab:
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
            return

        _vm = st.session_state.get('view_mode', 'Simple')
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
                if _vm == 'Simple':
                    _render_simple_card(sym, snap, color, icon, vwap, price, vwap_label,
                                        get_signal_strength, get_earnings_date, get_rvol)
                else:
                    _render_pro_card(sym, snap, color, icon, vwap, price, vwap_label,
                                     get_options_snapshot, get_iv_rank, get_rs_vs_spy,
                                     get_squeeze_score, get_max_pain, get_best_buy_strike,
                                     get_earnings_date, get_volume_spike, get_rvol)


def _render_simple_card(sym, snap, color, icon, vwap, price, vwap_label,
                         get_signal_strength, get_earnings_date, get_rvol):
    ss   = get_signal_strength(sym)
    earn = get_earnings_date(sym)
    rvol = get_rvol(sym)
    sig_bg = f"{ss['color']}22"
    d = ss.get('detail', {})
    _na = {'color': '#8b92a8', 'note': '—'}
    layers_html = "".join([
        f"<span style='color:{d.get('rs', _na)['color']};'>RS {d.get('rs', _na)['note']}</span> &nbsp;·&nbsp; ",
        f"<span style='color:{d.get('iv', _na)['color']};'>IV {d.get('iv', _na)['note']}</span> &nbsp;·&nbsp; ",
        f"<span style='color:{d.get('mp', _na)['color']};'>{d.get('mp', _na)['note']}</span><br>",
        f"<span style='color:{d.get('sq', _na)['color']};'>Squeeze {d.get('sq', _na)['note']}</span> &nbsp;·&nbsp; ",
        f"<span style='color:#8b92a8;'>Liq {d.get('liq', _na)['note']}</span>",
    ])
    vwap_color = "#2ecc71" if price > vwap and vwap > 0 else "#e74c3c" if vwap > 0 else "#8b92a8"

    if earn.get("available"):
        earn_bar = (
            f"<div style='background:{earn['color']}22; "
            f"border:1px solid {earn['color']}; border-radius:8px; "
            f"padding:7px 10px; margin-top:8px; font-size:12px; line-height:1.4;'>"
            f"<strong style='color:{earn['color']};'>"
            f"{earn['emoji']} EARNINGS {earn['grade']}</strong> "
            f"&nbsp;·&nbsp; {earn['date_str']} &nbsp;·&nbsp; {earn['days']}d away<br>"
            f"<span style='color:#8b92a8;'>{earn['advice']}</span>"
            f"</div>"
        )
    else:
        earn_bar = ""

    st.markdown(f"""
    <div class="simple-card">
      <div class="simple-ticker">{sym}</div>
      <div class="simple-price" style="color:{color};">${price:.2f}</div>
      <div class="simple-change" style="color:{color};">{icon} {snap['change']:+.1f}% &nbsp;·&nbsp;
        <span style="color:{vwap_color};">{vwap_label}</span>
      </div>
      <div class="simple-signal" style="background:{sig_bg}; color:{ss['color']}; border:2px solid {ss['color']};">
        {ss['emoji']} {ss['score']}/10 — {ss['grade']}
      </div>
      <div class="simple-stars" style="color:{ss['color']};">{ss['stars']}</div>
      <div class="simple-advice">{ss['advice']}</div>
      <div class="simple-layers">{layers_html}</div>
      {_badge_rvol(rvol)}
      {earn_bar}
    </div>
    """, unsafe_allow_html=True)


def _render_pro_card(sym, snap, color, icon, vwap, price, vwap_label,
                      get_options_snapshot, get_iv_rank, get_rs_vs_spy,
                      get_squeeze_score, get_max_pain, get_best_buy_strike,
                      get_earnings_date, get_volume_spike, get_rvol):
    opt = get_options_snapshot(sym)
    rvol = get_rvol(sym)
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

    iv = get_iv_rank(sym)
    iv_html = _badge_iv(iv)

    rs = get_rs_vs_spy(sym)
    rs_html = _badge_rs(rs, sym)

    sq = get_squeeze_score(sym)
    sq_html = _badge_squeeze(sq)

    mp = get_max_pain(sym)
    mp_html = _badge_max_pain(mp)

    bbs = get_best_buy_strike(sym)
    bbs_html = _badge_best_buy(bbs)

    earn = get_earnings_date(sym)
    earn_html = _badge_earnings(earn)

    vs = get_volume_spike(sym)
    vs_html = _badge_volume_spike(vs)

    st.markdown(f"""
    <div class="trade-card">
    <h2>${sym}</h2>
    <p class="big-text" style="color:{color};">${price:.2f}</p>
    <p>{icon} {snap['change']:+.1f}% | Vol: {snap['volume']}</p>
    <p><strong>VWAP:</strong> ${vwap:.2f} &nbsp;<em>{vwap_label}</em></p>
    <hr>
    {rs_html}
    {iv_html}
    {sq_html}
    {mp_html}
    {bbs_html}
    {earn_html}
    {vs_html}
    {_badge_rvol(rvol)}
    <hr>
    {liq_html}
    <p><strong>Strategies:</strong> #163 VWAP · #172 Whole-$ · #177 BTC-sync</p>
    </div>
    """, unsafe_allow_html=True)


def _badge_iv(iv):
    if not iv.get("available"):
        return "<p style='color:#8b92a8;'><small>IV data loading…</small></p>"
    return (
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


def _badge_rs(rs, sym):
    if not rs.get("available"):
        return "<p style='color:#8b92a8;'><small>RS data loading…</small></p>"
    rs_ratio_txt = (
        f"{rs['rs']:.1f}x" if abs(rs['rs']) < 90
        else ("∞" if rs['rs'] > 0 else "−∞")
    )
    return (
        f"<p style='margin:4px 0;'>"
        f"<span style='background:{rs['color']}22; color:{rs['color']}; "
        f"border:1px solid {rs['color']}; border-radius:5px; "
        f"padding:2px 8px; font-weight:bold; font-size:13px;'>"
        f"RS {rs['label']} &nbsp;|&nbsp; {rs['stars']} &nbsp;|&nbsp; "
        f"{rs_ratio_txt} vs SPY</span></p>"
        f"<p style='color:#8b92a8; font-size:11px; margin:2px 0;'>"
        f"{sym} {rs['stock_chg']:+.1f}% &nbsp;·&nbsp; "
        f"SPY {rs['spy_chg']:+.1f}% &nbsp;·&nbsp; "
        f"{rs['desc']}</p>"
    )


def _badge_squeeze(sq):
    if not sq.get("available"):
        return "<p style='color:#8b92a8;'><small>Squeeze data loading…</small></p>"
    return (
        f"<p style='margin:4px 0;'>"
        f"<span style='background:{sq['color']}22; color:{sq['color']}; "
        f"border:1px solid {sq['color']}; border-radius:5px; "
        f"padding:2px 8px; font-weight:bold; font-size:13px;'>"
        f"{sq['emoji']} SQUEEZE {sq['score']}/100 — {sq['grade']}</span></p>"
        f"<p style='color:#8b92a8; font-size:11px; margin:2px 0;'>"
        f"Float: {sq['float_label']} &nbsp;·&nbsp; "
        f"Short: {sq['si_label']} &nbsp;·&nbsp; "
        f"DTC: {sq['dtc_label']}</p>"
        f"<p style='color:#8b92a8; font-size:11px; margin:2px 0;'>{sq['advice']}</p>"
    )


def _badge_max_pain(mp):
    if not mp.get("available"):
        return ""
    return (
        f"<p style='margin:4px 0; font-size:12px;'>"
        f"<span style='color:{mp['pull_color']}; font-weight:bold;'>"
        f"📌 Max Pain ${mp['max_pain_strike']:.0f}</span> &nbsp;"
        f"<span style='color:{mp['pin_color']};'>"
        f"({mp['diff_pct']:+.1f}% from price)</span> &nbsp;"
        f"<span style='color:{mp['pull_color']}; font-size:11px;'>"
        f"{mp['pull_label']} · {mp['days_to_exp']}d to expiry"
        f"</span></p>"
    )


def _badge_best_buy(bbs):
    if not bbs.get("available"):
        return ""
    spread     = round(bbs['ask'] - bbs['bid'], 2)
    spread_pct = round(spread / ((bbs['bid'] + bbs['ask']) / 2) * 100, 0) if (bbs['bid'] + bbs['ask']) > 0 else 0
    return (
        f"<p style='margin:6px 0 2px 0;'>"
        f"<span style='background:{bbs['color']}22; color:{bbs['color']}; "
        f"border:1px solid {bbs['color']}; border-radius:5px; "
        f"padding:2px 8px; font-weight:bold; font-size:13px;'>"
        f"🎯 BEST BUY CALL: ${bbs['best_strike']:.2f} &nbsp;·&nbsp; "
        f"{bbs['emoji']} {bbs['grade']}</span></p>"
        f"<p style='color:#8b92a8; font-size:11px; margin:2px 0;'>"
        f"IV: <strong style='color:#fff;'>{bbs['iv_pct']}%</strong> &nbsp;·&nbsp; "
        f"Surface: {bbs['fitted_iv_pct']}% &nbsp;·&nbsp; "
        f"Discount: <strong style='color:{bbs['color']};'>{bbs['residual_pp']:+.1f} PP</strong> &nbsp;·&nbsp; "
        f"Δ{bbs['delta']:.2f} &nbsp;·&nbsp; "
        f"OI: {bbs['oi']:,} &nbsp;·&nbsp; "
        f"${bbs['bid']:.2f}×${bbs['ask']:.2f} "
        f"<span style='color:#f39c12;'>(spread {spread_pct:.0f}%)</span>"
        f"</p>"
        f"<p style='color:#8b92a8; font-size:11px; margin:2px 0;'>"
        f"{bbs['advice']}</p>"
    )


def _badge_earnings(earn):
    if not earn.get("available"):
        return ""
    return (
        f"<p style='margin:6px 0 2px 0;'>"
        f"<span style='background:{earn['color']}22; color:{earn['color']}; "
        f"border:1px solid {earn['color']}; border-radius:5px; "
        f"padding:2px 8px; font-weight:bold; font-size:13px;'>"
        f"{earn['emoji']} EARNINGS {earn['grade']} &nbsp;·&nbsp; "
        f"{earn['date_str']} &nbsp;·&nbsp; {earn['days']}d away"
        f"</span></p>"
        f"<p style='color:#8b92a8; font-size:11px; margin:2px 0;'>"
        f"{earn['advice']}</p>"
    )


def _badge_volume_spike(vs):
    if not vs.get("available"):
        return ""
    return (
        f"<p style='margin:6px 0 2px 0;'>"
        f"<span style='background:{vs['color']}22; color:{vs['color']}; "
        f"border:1px solid {vs['color']}; border-radius:5px; "
        f"padding:2px 8px; font-weight:bold; font-size:13px;'>"
        f"{vs['emoji']} {vs['grade']} &nbsp; {vs['spike_ratio']:.1f}× vol &nbsp;·&nbsp; "
        f"{vs['direction']}"
        f"</span></p>"
        f"<p style='color:#8b92a8; font-size:11px; margin:2px 0;'>"
        f"{vs['advice']} &nbsp;·&nbsp; "
        f"cur: {vs['cur_vol']:,} &nbsp; avg: {vs['avg_vol']:,}"
        f"</p>"
    )


def _badge_rvol(rv):
    if not rv.get("available"):
        return ""
    return (
        f"<p style='margin:6px 0 2px 0;'>"
        f"<span style='background:{rv['color']}22; color:{rv['color']}; "
        f"border:1px solid {rv['color']}; border-radius:5px; "
        f"padding:2px 8px; font-weight:bold; font-size:13px;'>"
        f"{rv['emoji']} RVOL {rv['rvol']:.1f}× &nbsp;·&nbsp; {rv['grade']}"
        f"</span></p>"
        f"<p style='color:#8b92a8; font-size:11px; margin:2px 0;'>"
        f"{rv['advice']}"
        f"</p>"
    )
