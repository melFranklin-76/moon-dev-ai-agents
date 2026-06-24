"""Tab 6 — Market Regime: SPY/QQQ/IWM/VIX + sectors + intraday flow."""
import streamlit as st
import plotly.graph_objects as go
from datetime import date


PDT_CHANGE_DATE = date(2026, 6, 4)


def render(tab, *, get_regime_data, get_sector_data, get_intraday_sector_flow):
    with tab:
        st.markdown("## 🌡️ MARKET REGIME")
        st.markdown("*Check this first — it determines which strategy mode to use*")

        regime  = get_regime_data()
        sectors = get_sector_data()

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

        # ── Intraday Sector Money Flow ───────────────────────────────────────
        st.markdown("---")
        st.markdown("### 💸 Intraday Money Flow — Last 30 Minutes")
        st.caption("Where hot money rotated RIGHT NOW vs daily % change. Updated every 60 seconds.")

        flow = get_intraday_sector_flow()
        if flow:
            fig_flow = go.Figure()
            flow_colors = [r['flow_color'] for r in flow]
            fig_flow.add_trace(go.Bar(
                x=[f"{r['arrow']} {r['symbol']}" for r in flow],
                y=[r['rs_30m'] for r in flow],
                marker_color=flow_colors,
                text=[f"{r['rs_30m']:+.2f}%<br>{r['vol_ratio']:.1f}x vol" for r in flow],
                textposition='outside',
            ))
            fig_flow.add_hline(y=0, line_color='#8b92a8', line_dash='dash')
            fig_flow.update_layout(
                template='plotly_dark', height=280,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title="Sector", yaxis_title="RS vs SPY (30 min) %",
                showlegend=False,
            )
            st.plotly_chart(fig_flow, width="stretch")

            flow_cols = st.columns(5)
            for i, r in enumerate(flow[:5]):
                with flow_cols[i]:
                    st.markdown(
                        f"<div style='background:#1e2130; border-radius:8px; "
                        f"padding:8px; text-align:center;'>"
                        f"<strong style='color:{r['flow_color']};'>{r['symbol']}</strong><br>"
                        f"<small>{r['name']}</small><br>"
                        f"<span style='color:{r['flow_color']}; font-size:18px; font-weight:bold;'>"
                        f"{r['arrow']} {r['rs_30m']:+.2f}%</span><br>"
                        f"<small style='color:#8b92a8;'>30m: {r['chg_30m']:+.2f}% "
                        f"· vol {r['vol_ratio']:.1f}x</small><br>"
                        f"<small style='color:{r['flow_color']};'>{r['flow_label']}</small>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

            st.markdown("---")
            st.markdown(
                "**Reading this:** Bars above 0 = sector outperforming SPY right now. "
                "↑↑ = accelerating. High vol ratio = institutional conviction behind the move. "
                "Trade stocks from the top-ranked sector first."
            )
        else:
            st.info("Market data loading… check back after 9:30 AM ET open.")

        st.markdown("---")
        st.markdown("""**Current Hot Themes (May 2026):**
        🟢 AI Infrastructure · Edge Computing · Healthcare/GLP-1 · Energy/Industrials · Defense/Copper
        🔴 Avoid: Enterprise SaaS (AI disruption risk) · Consumer Discretionary""")

        pdt_days = (PDT_CHANGE_DATE - date.today()).days
        st.markdown("---")
        if pdt_days > 0:
            st.info(f"⏳ **PDT Rule Change in {pdt_days} days** (June 4, 2026) — $25k minimum eliminated, replaced with $2k intraday margin requirement. Cash accounts (like your $250) were never subject to PDT anyway — your limit is T+1 settlement.")
        else:
            st.success("✅ PDT Rule Changed — No more day trade counting on margin accounts.")
