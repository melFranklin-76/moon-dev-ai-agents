"""Tab 7 — Catalyst Grader: SMB 5-check pre-market grading system."""
import streamlit as st


def render(tab, *, get_snapshot, get_max_pain, get_rs_vs_spy, get_iv_rank):
    with tab:
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

                # Max Pain check
                mp_g = get_max_pain(ticker_g)
                if mp_g.get("available"):
                    st.markdown(f"""
                    <div style="background:#1e2130; border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                    <strong style="color:{mp_g['pull_color']};">
                      📌 Max Pain: ${mp_g['max_pain_strike']:.0f} &nbsp;
                      ({mp_g['diff_pct']:+.1f}% from ${mp_g['current_price']:.2f}) &nbsp;
                      {mp_g['pull_label']}
                    </strong><br>
                    <span style="color:{mp_g['pin_color']}; font-size:13px;">
                      {mp_g['pin_status']}
                    </span><br>
                    <span style="color:#8b92a8; font-size:12px;">
                      {mp_g['pull_note']} &nbsp;·&nbsp; Expiry: {mp_g['expiry']} ({mp_g['days_to_exp']} days)
                    </span>
                    </div>""", unsafe_allow_html=True)

                # Relative Strength check
                rs_g = get_rs_vs_spy(ticker_g)
                if rs_g.get("available"):
                    rs_g_ratio = (
                        f"{rs_g['rs']:.1f}x" if abs(rs_g['rs']) < 90
                        else ("∞ (leading)" if rs_g['rs'] > 0 else "lagging badly")
                    )
                    rs_g_box = (
                        "green-box"  if rs_g['score'] >= 7 else
                        "red-box"    if rs_g['score'] <= 3 else
                        "yellow-box"
                    )
                    st.markdown(f"""
                    <div class="{rs_g_box}">
                    <h3>📊 RS vs SPY: {rs_g['label']} &nbsp; {rs_g['stars']}</h3>
                    <p>{rs_g['desc']}</p>
                    <p style="font-size:12px; color:#8b92a8;">
                      {ticker_g}: {rs_g['stock_chg']:+.1f}% &nbsp;·&nbsp;
                      SPY: {rs_g['spy_chg']:+.1f}% &nbsp;·&nbsp;
                      Ratio: {rs_g_ratio}
                    </p>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.info(f"RS data loading for {ticker_g}…")

                # IV Rank check
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

                # Options liquidity check
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
