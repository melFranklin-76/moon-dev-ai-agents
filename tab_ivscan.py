"""Tab 10 — IV Scanner: Multi-expiration IV surface fitting, chart, chain table."""
import streamlit as st
import plotly.graph_objects as go


def render(tab, *, scan_iv_surface):
    with tab:
        st.markdown("### 📊 IV Surface Scanner")
        st.caption("Finds options pricing rich or cheap vs the fitted volatility smile, across every expiration in your window.")

        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            iv_sym = st.text_input(
                "Symbol",
                value=st.session_state.get('selected_ticker', '') or 'SPY',
                key='iv_scanner_sym',
            ).upper().strip()
        with c2:
            opt_type = st.radio("Type", ["calls", "puts"], horizontal=True, key='iv_scanner_type')
        with c3:
            direction = st.radio("Mode", ["Buy (cheap)", "Sell (rich)"], horizontal=True, key='iv_scanner_dir')

        c4, c5, c6, c7 = st.columns(4)
        with c4:
            dte_range = st.slider("Days to Expiry", 1, 120, (7, 60), key='iv_scanner_dte')
        with c5:
            min_oi = st.number_input("Min Open Interest", min_value=0, value=10, step=10, key='iv_scanner_oi')
        with c6:
            min_vol = st.number_input("Min Volume", min_value=0, value=0, step=10, key='iv_scanner_vol')
        with c7:
            delta_range = st.slider("|Delta| Range", 0.05, 0.95, (0.10, 0.75), step=0.05, key='iv_scanner_delta')

        scan_btn = st.button("🔍 Scan", type='primary', use_container_width=False, key='iv_scanner_btn')

        if scan_btn and iv_sym:
            with st.spinner(f"Scanning {iv_sym} {opt_type} across expirations…"):
                scan = scan_iv_surface(
                    iv_sym,
                    dte_min=dte_range[0], dte_max=dte_range[1],
                    opt_type=opt_type,
                    min_oi=int(min_oi), min_vol=int(min_vol),
                    delta_min=delta_range[0], delta_max=delta_range[1],
                )
            st.session_state['iv_scan_result'] = scan
            st.session_state['iv_scan_meta'] = {'direction': direction, 'symbol': iv_sym}

        scan = st.session_state.get('iv_scan_result')
        meta = st.session_state.get('iv_scan_meta', {})

        if scan and scan.get("available"):
            _render_results(scan, meta, opt_type)
        elif scan is not None:
            st.warning(
                f"No usable surface for **{meta.get('symbol','')}**. "
                "Try widening the DTE range, lowering Min OI, or pick a more-liquid symbol."
            )
        else:
            st.info("Pick a symbol and hit **Scan** to fit the IV surface across expirations.")


def _render_results(scan, meta, opt_type):
    st.success(f"Found {len(scan['expirations'])} expirations. Spot: ${scan['spot']:.2f}")

    sel_exp = st.selectbox("Expiration to chart", scan['expirations'], key='iv_scanner_exp')
    ex_data = scan['per_expiry'][sel_exp]

    is_buy = (meta.get('direction', '').startswith('Buy'))
    if is_buy:
        colors = ['#2ecc71' if r < -1 else '#e74c3c' if r > 3 else '#888888' for r in ex_data['residuals_pp']]
    else:
        colors = ['#2ecc71' if r > 3 else '#e74c3c' if r < -3 else '#888888' for r in ex_data['residuals_pp']]
    sizes = [14 if abs(r) >= 3 else 8 for r in ex_data['residuals_pp']]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ex_data['strikes'], y=ex_data['fitted'] * 100,
        mode='lines', line=dict(color='#8b92a8', dash='dash', width=2),
        name='Fitted smile',
    ))
    hover = [
        f"Strike ${s:.2f}<br>IV {iv*100:.1f}%<br>Residual {r:+.1f} PP<br>Delta {d:.2f}<br>OI {oi:,}"
        for s, iv, r, d, oi in zip(
            ex_data['strikes'], ex_data['ivs'], ex_data['residuals_pp'],
            ex_data['df']['delta'].values, ex_data['df']['oi'].values,
        )
    ]
    fig.add_trace(go.Scatter(
        x=ex_data['strikes'], y=ex_data['ivs'] * 100,
        mode='markers',
        marker=dict(color=colors, size=sizes, line=dict(color='#0e1117', width=1)),
        text=hover, hoverinfo='text',
        name=opt_type.capitalize(),
    ))
    fig.add_vline(x=scan['spot'], line=dict(color='#f39c12', width=1, dash='dot'),
                  annotation_text=f"Spot ${scan['spot']:.2f}", annotation_position="top")
    fig.update_layout(
        title=f"{scan['symbol']} {opt_type} · {sel_exp} ({ex_data['dte']} DTE)",
        xaxis_title="Strike", yaxis_title="Implied Volatility (%)",
        template='plotly_dark', height=460,
        paper_bgcolor='#0e1117', plot_bgcolor='#161b22',
        font=dict(color='#c9d1d9'),
        margin=dict(l=40, r=20, t=50, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Chain table
    st.markdown(f"#### Chain — {sel_exp}")
    chain_df = ex_data['df'].copy()
    chain_df = chain_df[[
        'strike', 'bid', 'ask', 'mid', 'iv_pct', 'fitted_iv_pct',
        'residual_pp', 'delta', 'oi', 'volume', 'spread_pp',
        'spread_warn', 'oi_warn',
    ]].rename(columns={
        'iv_pct': 'IV %', 'fitted_iv_pct': 'Fitted %',
        'residual_pp': 'IV+PP', 'delta': 'Δ',
        'oi': 'OI', 'volume': 'Vol', 'spread_pp': 'Spread %',
    })

    def _style_chain(row):
        styles = [''] * len(row)
        r = row['IV+PP']
        if is_buy:
            if r < -3:   bg = 'background-color: rgba(46,204,113,0.15)'
            elif r > 3:  bg = 'background-color: rgba(231,76,60,0.10)'
            else:        bg = ''
        else:
            if r > 3:    bg = 'background-color: rgba(46,204,113,0.15)'
            elif r < -3: bg = 'background-color: rgba(231,76,60,0.10)'
            else:        bg = ''
        for i in range(len(row)):
            styles[i] = bg
        if row['spread_warn']:
            bi = list(row.index).index('bid')
            ai = list(row.index).index('ask')
            styles[bi] += '; background-color: rgba(241,196,15,0.30)'
            styles[ai] += '; background-color: rgba(241,196,15,0.30)'
        if row['oi_warn']:
            oi_i = list(row.index).index('OI')
            styles[oi_i] += '; background-color: rgba(241,196,15,0.30)'
        return styles

    styled = chain_df.style.apply(_style_chain, axis=1).format({
        'strike': '${:.2f}', 'bid': '${:.2f}', 'ask': '${:.2f}', 'mid': '${:.2f}',
        'IV %': '{:.1f}%', 'Fitted %': '{:.1f}%', 'IV+PP': '{:+.1f}',
        'Δ': '{:.2f}', 'OI': '{:,}', 'Vol': '{:,}', 'Spread %': '{:.1f}%',
    })
    st.dataframe(
        styled.hide(axis="columns", subset=['spread_warn', 'oi_warn']),
        use_container_width=True, height=320,
    )

    # Top candidates
    st.markdown(f"#### Top {'Cheapest' if is_buy else 'Richest'} Across All Expirations")
    tc = scan['top_candidates'].copy()
    if not is_buy:
        tc = tc.sort_values('residual_pp', ascending=False).head(10)
    tc_disp = tc.rename(columns={
        'expiry': 'Expiry', 'dte': 'DTE', 'strike': 'Strike', 'mid': 'Mid',
        'iv_pct': 'IV %', 'residual_pp': 'IV+PP', 'delta': 'Δ',
        'oi': 'OI', 'volume': 'Vol', 'spread_pp': 'Spread %',
    })
    st.dataframe(
        tc_disp[['Expiry','DTE','Strike','Mid','IV %','IV+PP','Δ','OI','Vol','Spread %']]
            .style.format({
                'Strike': '${:.2f}', 'Mid': '${:.2f}',
                'IV %': '{:.1f}%', 'IV+PP': '{:+.1f}',
                'Δ': '{:.2f}', 'OI': '{:,}', 'Vol': '{:,}', 'Spread %': '{:.1f}%',
            }),
        use_container_width=True, height=380,
    )

    st.caption(
        "**IV+PP** = actual IV minus fitted-smile IV, in percentage points. "
        "Negative = cheap relative to its neighbors (buy candidate). "
        "Positive = rich relative to its neighbors (sell candidate). "
        "Yellow cells flag wide bid/ask spreads or thin open interest. "
        "Yahoo Finance IV is sometimes stale — verify on your broker before trading."
    )
