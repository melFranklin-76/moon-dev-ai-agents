"""Tab 1 — Live Scanner: Universe scanner, gap scanner, setup signals."""
import streamlit as st
import pandas as pd


def render(tab, *, snapshots, btc_price, _watchlist, last_updated,
           scan_momentum_universe, get_squeeze_score, get_news,
           get_intraday_sector_flow, get_rs_vs_spy, send_ntfy,
           scan_premarket_gaps, run_scanner):
    with tab:
        st.markdown("## 🟢 LIVE SETUP SCANNER")

        # ── Universe Scanner ─────────────────────────────────────────────────
        st.markdown("### 🔭 Find Today's Optionable Movers")
        st.caption("Scans Yahoo Finance day gainers + most actives. Filters by your criteria. Flags which ones have options.")

        with st.expander("⚙️ Scanner Filters", expanded=False):
            fc1, fc2, fc3, fc4 = st.columns(4)
            f_min_price  = fc1.number_input("Min Price ($)",   value=2.0,   step=0.5,  min_value=0.5)
            f_max_price  = fc2.number_input("Max Price ($)",   value=100.0, step=5.0,  min_value=1.0)
            f_min_change = fc3.number_input("Min Change (%)",  value=3.0,   step=0.5,  min_value=0.5)
            f_min_relvol = fc4.number_input(
                "Min Rel Vol (x)", value=1.0, step=0.1, min_value=0.1,
                help="Volume vs 3-month average. Stays under 1.0x most of the morning — "
                     "set to 0.5x in pre-market, 1.0x mid-day, 2.0x+ for explosive movers only.",
            )

        scan_col, info_col = st.columns([1, 3])
        run_scan = scan_col.button("🚀 Scan Universe Now", type="primary", width="stretch")
        info_col.caption("Takes ~20–30 seconds. Results cached 5 min. Checks ALL Yahoo Finance movers — nothing slips through.")

        if run_scan:
            with st.spinner("Scanning universe... checking options availability..."):
                universe = scan_momentum_universe(
                    min_price=f_min_price, max_price=f_max_price,
                    min_change=f_min_change, min_rel_vol=f_min_relvol,
                )
            st.session_state['_last_universe'] = universe

        raw_universe = st.session_state.get('_last_universe', [])
        _diag    = next((r['_diag'] for r in raw_universe if not r.get('symbol')), None)
        universe = [r for r in raw_universe if r.get('symbol')]

        if universe:
            st.markdown(f"**{len(universe)} stocks meet criteria** — click ➕ to add to watchlist · always verify options chain on Webull before trading")
            st.caption("⚠️ Confirm open interest > 200 and bid/ask spread < 10% on Webull before entering any trade.")

            for r in universe:
                rc1, rc2, rc3, rc4, rc5, rc6, rc7 = st.columns([1, 2, 1, 1, 1, 1, 1])
                rc1.markdown(f"**{r['symbol']}**")
                rc2.markdown(f"<small>{r['name'][:28]}</small>", unsafe_allow_html=True)
                rc3.markdown(f"**${r['price']:.2f}**")
                rc4.markdown(f"<span style='color:#2ecc71'>+{r['change']:.1f}%</span>", unsafe_allow_html=True)
                rc5.markdown(f"{r['rel_vol']:.1f}x vol")
                sq_r = get_squeeze_score(r['symbol'])
                if sq_r.get("available"):
                    rc6.markdown(
                        f"<span style='color:{sq_r['color']}; font-weight:bold;'>"
                        f"{sq_r['emoji']}{sq_r['score']}</span>",
                        unsafe_allow_html=True
                    )
                else:
                    rc6.markdown("—")
                if rc7.button("➕", key=f"add_uni_{r['symbol']}"):
                    if r['symbol'] not in st.session_state.watchlist:
                        st.session_state.watchlist.append(r['symbol'])
                    st.session_state.selected_ticker = r['symbol']
                    st.session_state.news_cache[r['symbol']] = get_news(r['symbol'])
                    st.cache_data.clear()
                    st.rerun()
        elif _diag:
            rej = _diag['rejected']
            bottleneck = max(rej, key=rej.get)
            labels = {
                "price":   f"price outside ${f_min_price:g}–${f_max_price:g}",
                "change":  f"% change below {f_min_change:g}%",
                "volume":  "volume below 500K",
                "rel_vol": f"rel-volume below {f_min_relvol:g}x",
            }
            st.warning(
                f"**0 of {_diag['raw_count']} movers passed.** "
                f"Biggest filter: **{labels[bottleneck]}** ({rej[bottleneck]} rejected). "
                f"Full breakdown: price {rej['price']}, change {rej['change']}, "
                f"volume {rej['volume']}, rel-vol {rej['rel_vol']}."
            )
            if bottleneck == "rel_vol":
                st.caption(
                    "💡 Rel-volume stays under 1.0x most of the morning until volume builds. "
                    "Try lowering **Min Rel Vol** to 0.5x pre-market, or 0.7x in the first hour."
                )
            elif bottleneck == "change":
                st.caption("💡 The whole tape may be flat today — try lowering **Min Change** to 2.0%.")
        elif not run_scan:
            st.info("Hit **Scan Universe Now** to find today's optionable movers. Do this each morning after 8:30 AM CT.")

        # ── News for selected ticker ─────────────────────────────────────────
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

        # ── Pre-Market Gap Scanner ───────────────────────────────────────────
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
                    rs_sig = get_rs_vs_spy(sig['ticker'])
                    if rs_sig.get("available"):
                        rs_ratio_txt = (
                            f"{rs_sig['rs']:.1f}x" if abs(rs_sig['rs']) < 90
                            else ("∞" if rs_sig['rs'] > 0 else "−∞")
                        )
                        rs_line = (
                            f"<p><strong>RS vs SPY:</strong> "
                            f"<span style='color:{rs_sig['color']};'>"
                            f"{rs_sig['label']} {rs_sig['stars']} ({rs_ratio_txt})</span> "
                            f"— {rs_sig['desc']}</p>"
                        )
                    else:
                        rs_line = ""
                    st.markdown(f"""
                    <div class="{box}">
                    <h3>{sig['ticker']} — {sig['strategy']} {sig['strength']}</h3>
                    <p><strong>Signal:</strong> {sig['signal']}</p>
                    <p><strong>Trigger:</strong> {sig['trigger']}</p>
                    <p><strong>Entry:</strong> {sig['entry_note']}</p>
                    {rs_line}
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
            _flow = get_intraday_sector_flow()
            if _flow:
                _hot  = _flow[0]
                _cold = _flow[-1]
                st.markdown(
                    f"<div style='background:#1e2130; border-radius:8px; "
                    f"padding:8px 12px; margin-bottom:8px;'>"
                    f"<span style='color:{_hot['flow_color']}; font-weight:bold;'>"
                    f"🔥 HOT MONEY → {_hot['name']} ({_hot['symbol']}) "
                    f"{_hot['arrow']} RS {_hot['rs_30m']:+.2f}% · "
                    f"vol {_hot['vol_ratio']:.1f}x</span><br>"
                    f"<span style='color:{_cold['flow_color']}; font-size:12px;'>"
                    f"🧊 COLD: {_cold['name']} ({_cold['symbol']}) "
                    f"RS {_cold['rs_30m']:+.2f}%</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

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
