"""Tab 8 — Options Planner: Directional calls/puts + XSP spreads + backtest."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date
import math as _math


def render(tab, *, get_max_pain, get_iv_rank, get_xsp_data):
    with tab:
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

        if "Directional" in mode:
            _render_directional(get_max_pain, get_iv_rank)
        else:
            _render_xsp(get_xsp_data)

        # ── Quick Strategy Backtest ──────────────────────────────────────────
        st.markdown("---")
        _render_backtest()


def _bs_price(S, K, T, iv, is_call=True, r=0.0):
    if T <= 0: return max((S-K if is_call else K-S), 0.0)
    if iv <= 0 or S <= 0 or K <= 0: return 0.0
    try:
        _d1 = (_math.log(S/K) + (r + 0.5*iv**2)*T) / (iv*_math.sqrt(T))
        _d2 = _d1 - iv*_math.sqrt(T)
        _N  = lambda x: 0.5*(1 + _math.erf(x/_math.sqrt(2)))
        if is_call:
            return max(S*_N(_d1) - K*_math.exp(-r*T)*_N(_d2), 0.0)
        else:
            return max(K*_math.exp(-r*T)*_N(-_d2) - S*_N(-_d1), 0.0)
    except Exception:
        return 0.0


def _render_directional(get_max_pain, get_iv_rank):
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
        if d_tick:
            mp_p = get_max_pain(d_tick)
            if mp_p.get("available") and mp_p['pain_strikes']:
                st.markdown(f"""
                <div style="background:#1e2130; border-radius:8px;
                            padding:10px 14px; margin-bottom:8px;">
                <strong style="color:{mp_p['pull_color']};">
                  📌 Max Pain: ${mp_p['max_pain_strike']:.0f} &nbsp;
                  {mp_p['pull_label']}
                </strong><br>
                <span style="color:{mp_p['pin_color']}; font-size:13px;">
                  {mp_p['pin_status']}
                </span><br>
                <span style="color:#8b92a8; font-size:12px;">
                  {mp_p['pull_note']}
                </span>
                </div>""", unsafe_allow_html=True)

                fig_mp = go.Figure()
                fig_mp.add_trace(go.Bar(
                    x=mp_p['pain_strikes'], y=mp_p['pain_values'],
                    marker_color=[
                        "#e74c3c" if s == mp_p['max_pain_strike'] else "#3498db"
                        for s in mp_p['pain_strikes']
                    ],
                    name="Total Pain ($)",
                ))
                fig_mp.add_vline(x=mp_p['current_price'], line_color="#2ecc71", line_dash="dash",
                                 annotation_text=f"Price ${mp_p['current_price']:.2f}",
                                 annotation_font_color="#2ecc71")
                fig_mp.add_vline(x=mp_p['max_pain_strike'], line_color="#e74c3c", line_dash="dot",
                                 annotation_text=f"Max Pain ${mp_p['max_pain_strike']:.0f}",
                                 annotation_font_color="#e74c3c")
                fig_mp.update_layout(template='plotly_dark', height=220,
                                     margin=dict(l=10, r=10, t=10, b=30),
                                     xaxis_title="Strike", yaxis_title="Total Pain ($)",
                                     showlegend=False)
                st.plotly_chart(fig_mp, use_container_width=True)
                st.caption(f"Red bar = max pain strike. Green dashed = current price. "
                           f"Price is pulled toward the red bar as {mp_p['expiry']} approaches.")

        if d_tick:
            iv_p = get_iv_rank(d_tick)
            if iv_p.get("available"):
                iv_p_box = (
                    "green-box" if iv_p['grade'] == "CHEAP" else
                    "red-box"   if iv_p['grade'] == "RICH"  else
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

            _render_simulator(d_price, d_prem, d_side, strike)
        else:
            st.info("Enter stock price and option premium to generate trade plan.")


def _render_simulator(d_price, d_prem, d_side, strike):
    st.markdown("---")
    st.markdown("### 📊 Scenario Simulator")
    st.caption("Black-Scholes estimate of option value at different stock prices. Not a guarantee — use as a guide.")

    _sim_dte = st.slider("Days to expiry", min_value=1, max_value=45, value=7, key="sim_dte")
    _sim_iv  = st.slider("Implied Volatility (%)", min_value=10, max_value=300, value=80, key="sim_iv",
                          help="Check IV Rank badge on your ticker card for the current IV.")
    _sim_contracts = st.number_input("Contracts", min_value=1, max_value=10, value=1, step=1, key="sim_contracts")

    _is_call = "Call" in d_side
    _K       = float(strike)
    _S0      = float(d_price)
    _iv_dec  = _sim_iv / 100.0
    _T0      = _sim_dte / 365.0
    _prem    = float(d_prem)
    _contracts = int(_sim_contracts)
    _total_cost = round(_prem * 100 * _contracts, 2)

    _moves = [-0.20, -0.15, -0.10, -0.05, 0.0,
               0.05,  0.10,  0.15,  0.20,
               0.25,  0.30,  0.40,  0.50]
    _rows = []
    for _m in _moves:
        _S    = round(_S0 * (1 + _m), 2)
        _opt    = round(_bs_price(_S, _K, _T0, _iv_dec, _is_call), 2)
        _pnl_d  = round((_opt - _prem) * 100 * _contracts, 2)
        _pnl_pc = round((_opt - _prem) / _prem * 100, 1) if _prem > 0 else 0
        _rows.append({
            "Stock Move":  f"{_m:+.0%}",
            "Stock $":     f"${_S:.2f}",
            "Option $":    f"${_opt:.2f}",
            f"P&L ({_contracts}c)": f"${_pnl_d:+.2f}",
            "P&L %":       f"{_pnl_pc:+.1f}%",
            "_pnl":        _pnl_d,
        })

    _df_sim = pd.DataFrame(_rows)

    def _color_row(row):
        v = row["_pnl"]
        bg = "#1a3d1a" if v > 0 else ("#3d1a1a" if v < 0 else "#2a2d3e")
        return [f"background-color:{bg}"]*len(row)

    st.dataframe(
        _df_sim.drop(columns=["_pnl"]).style.apply(_color_row, axis=1),
        use_container_width=True, hide_index=True,
    )

    _be_move = (_K + _prem - _S0) / _S0 * 100 if _is_call else (_S0 - _K - _prem) / _S0 * -100
    _target_stock_25 = _K + (_prem * 1.25) if _is_call else _K - (_prem * 1.25)

    st.markdown(f"""
    <div style="background:#1e2130; border-radius:8px; padding:10px 14px; font-size:13px;">
      <strong>Key levels:</strong><br>
      💀 Break-even at expiry: <strong>${_K + _prem:.2f}</strong> stock
      &nbsp;(+{_be_move:.1f}% from current)<br>
      🎯 +25% option exit → stock needs ≈ <strong>${_target_stock_25:.2f}</strong><br>
      💸 Max loss: <strong>${_total_cost:.2f}</strong> (full premium if expires worthless)<br>
      📅 Time decay: option loses ~${round(_prem*0.10*100*_contracts,2):.2f}
      /day at current theta estimate
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Time decay at current stock price:**")
    _decay_rows = []
    for _days_left in [_sim_dte, max(_sim_dte-3,1), max(_sim_dte-7,1),
                       max(_sim_dte-14,1), 1]:
        _T_d    = _days_left / 365.0
        _opt_td = round(_bs_price(_S0, _K, _T_d, _iv_dec, _is_call), 2)
        _pnl_td = round((_opt_td - _prem)*100*_contracts, 2)
        _decay_rows.append({
            "Days Remaining": _days_left,
            "Option Value":   f"${_opt_td:.2f}",
            "P&L":            f"${_pnl_td:+.2f}",
        })
    st.dataframe(pd.DataFrame(_decay_rows), use_container_width=True, hide_index=True)


def _render_xsp(get_xsp_data):
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
            sell_s   = int(xsp_px)
            buy_s    = sell_s - 1
            cap_req  = round((1.00 - credit) * 100, 2)
            max_pft  = round(credit * 100, 2)
            max_loss = round((1.00 - credit) * 100, 2)
            early_bv = round(credit * 0.24, 2)
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


def _render_backtest():
    with st.expander("▶ Quick Strategy Backtest", expanded=False):
        st.caption("Run a simple backtest directly in the dashboard using real OHLCV data.")

        _bt_sym   = st.text_input("Symbol", value=st.session_state.get('selected_ticker', 'SPY'), key="bt_sym").upper().strip() or "SPY"
        _bt_strat = st.selectbox("Strategy", ["MACD Crossover", "SMA Breakout", "Volume Spike Reversal"], key="bt_strat")
        _bt_days  = st.slider("Lookback (days)", min_value=60, max_value=180, value=90, key="bt_days")

        if st.button("Run Backtest", type="primary", key="bt_run"):
            try:
                import yfinance as _yf_bt
                _bt_df = _yf_bt.Ticker(_bt_sym).history(period=f"{_bt_days}d", interval='1d')
                if _bt_df is None or _bt_df.empty or len(_bt_df) < 20:
                    st.warning(f"Not enough data for {_bt_sym}. Try a different symbol or shorter lookback.")
                else:
                    try:
                        from backtesting import Backtest, Strategy
                        import pandas_ta as ta

                        _bt_df = _bt_df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
                        _bt_df.index = pd.to_datetime(_bt_df.index).tz_localize(None)
                        _bt_df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

                        if _bt_strat == "MACD Crossover":
                            class _S(Strategy):
                                def init(self):
                                    _c = pd.Series(self.data.Close)
                                    _macd = ta.macd(_c)
                                    if _macd is None or _macd.empty:
                                        self._macd_line   = self.I(lambda: _c * 0)
                                        self._signal_line = self.I(lambda: _c * 0)
                                    else:
                                        _ml = _macd.iloc[:, 0].values
                                        _sl = _macd.iloc[:, 1].values
                                        self._macd_line   = self.I(lambda: _ml)
                                        self._signal_line = self.I(lambda: _sl)
                                def next(self):
                                    if self._macd_line[-1] > self._signal_line[-1] and self._macd_line[-2] <= self._signal_line[-2]:
                                        if not self.position: self.buy()
                                    elif self._macd_line[-1] < self._signal_line[-1] and self._macd_line[-2] >= self._signal_line[-2]:
                                        if self.position: self.position.close()

                        elif _bt_strat == "SMA Breakout":
                            class _S(Strategy):
                                def init(self):
                                    _c = pd.Series(self.data.Close)
                                    _sma_vals = _c.rolling(20).mean().values
                                    self._sma = self.I(lambda: _sma_vals)
                                def next(self):
                                    if self.data.Close[-1] > self._sma[-1] and self.data.Close[-2] <= self._sma[-2]:
                                        if not self.position: self.buy()
                                    elif self.data.Close[-1] < self._sma[-1] and self.data.Close[-2] >= self._sma[-2]:
                                        if self.position: self.position.close()

                        else:
                            class _S(Strategy):
                                _bar_count = 0
                                def init(self):
                                    _v = pd.Series(self.data.Volume)
                                    _avg_vals = _v.rolling(20).mean().values
                                    self._avg_vol = self.I(lambda: _avg_vals)
                                    self._entry_bar = 0
                                def next(self):
                                    _bar = len(self.data.Close)
                                    _c   = self.data.Close
                                    _v   = self.data.Volume
                                    if self.position:
                                        if _bar - self._entry_bar >= 5:
                                            self.position.close()
                                    else:
                                        _avg = self._avg_vol[-1]
                                        if _avg > 0 and _v[-1] > 2 * _avg:
                                            _bar_chg = (_c[-1] - _c[-2]) / _c[-2] if _c[-2] > 0 else 0
                                            if _bar_chg < -0.01:
                                                self.buy()
                                                self._entry_bar = _bar

                        _bt_obj = Backtest(_bt_df, _S, cash=10_000, commission=0.002)
                        _stats  = _bt_obj.run()

                        _ret     = round(float(_stats.get('Return [%]', 0)), 2)
                        _dd      = round(float(_stats.get('Max. Drawdown [%]', 0)), 2)
                        _trades  = int(_stats.get('# Trades', 0))
                        _winrate = round(float(_stats.get('Win Rate [%]', 0)), 1)
                        _sharpe  = round(float(_stats.get('Sharpe Ratio', 0) or 0), 2)

                        _m1, _m2, _m3, _m4, _m5 = st.columns(5)
                        _m1.metric("Return %",     f"{_ret:+.2f}%",  delta_color="normal" if _ret >= 0 else "inverse")
                        _m2.metric("Max Drawdown", f"{_dd:.2f}%",    delta_color="inverse")
                        _m3.metric("Sharpe Ratio", f"{_sharpe:.2f}")
                        _m4.metric("# Trades",     str(_trades))
                        _m5.metric("Win Rate",     f"{_winrate:.1f}%")

                        st.caption("3 months of data is thin — use as directional filter only")

                    except ImportError:
                        st.warning("backtesting or pandas_ta not installed. Run: `pip install backtesting>=0.3.3 pandas_ta`")
                    except Exception as _bt_err:
                        st.warning(f"Backtest error: {_bt_err}")

            except Exception as _outer_err:
                st.warning(f"Data fetch error: {_outer_err}")
