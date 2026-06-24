"""Tab 4 — Performance: 10-day challenge tracker, equity curve, analytics."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date


def render(tab):
    with tab:
        st.markdown("## 📈 10-DAY CHALLENGE TRACKER")

        c_left, c_right = st.columns([2, 1])

        with c_left:
            icons   = {1: "✅", -1: "❌", 0: "⬜"}
            day_row = " ".join(icons[d] for d in st.session_state.challenge_days)
            streak  = st.session_state.current_streak
            st.markdown(f"""
            <div class="green-box">
            <h2>🏆 10-Day Prove-It Challenge</h2>
            <p style="font-size:32px; text-align:center;">{day_row}</p>
            <p><strong>Streak:</strong> {streak} days 🔥 &nbsp;&nbsp;
               <strong>Status:</strong> {'ON TRACK! 🎯' if streak >= 3 else 'KEEP GOING!'}</p>
            <p style="color:#f39c12;">⚠️ One red day resets counter to 0!</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### Equity Curve")
            trades = st.session_state.trades
            if trades:
                df_eq = pd.DataFrame(trades)
                df_eq['pnl']  = pd.to_numeric(df_eq['pnl'], errors='coerce').fillna(0)
                df_eq['date'] = pd.to_datetime(df_eq['date'], errors='coerce')
                df_eq = df_eq.sort_values('date')
                df_eq['equity'] = 250 + df_eq['pnl'].cumsum()
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_eq['date'], y=df_eq['equity'],
                    mode='lines+markers', name='Account Value',
                    line=dict(color='#2ecc71', width=3)
                ))
                fig.update_layout(template='plotly_dark', height=300,
                                  margin=dict(l=20, r=20, t=20, b=20),
                                  xaxis_title="Date", yaxis_title="Account Value ($)")
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("Log trades to see your equity curve.")

        with c_right:
            today_str = date.today().isoformat()
            today_tr  = [t for t in st.session_state.trades if str(t.get('date',''))[:10] == today_str]
            wins_t    = len([t for t in today_tr if t.get('result') == 'Green'])

            st.markdown("### Today's Stats")
            st.metric("Trades",   str(len(today_tr)))
            st.metric("Win Rate", f"{wins_t/len(today_tr)*100:.0f}%" if today_tr else "N/A")
            if today_tr:
                pnls = [float(t.get('pnl', 0)) for t in today_tr]
                st.metric("Best",  f"+${max(pnls):.2f}")
                st.metric("Worst", f"${min(pnls):.2f}")

            st.markdown("### All-Time")
            all_tr   = st.session_state.trades
            all_wins = len([t for t in all_tr if t.get('result') == 'Green'])
            st.metric("Total Trades", str(len(all_tr)))
            st.metric("Win Rate", f"{all_wins/len(all_tr)*100:.0f}%" if all_tr else "N/A")
            if all_tr:
                all_pnl = sum(float(t.get('pnl', 0)) for t in all_tr)
                st.metric("Total P/L", f"${all_pnl:.2f}")

        # ── Performance Analytics ─────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 📊 Strategy & Time Analytics")
        all_tr = st.session_state.trades
        if len(all_tr) >= 3:
            df_a = pd.DataFrame(all_tr)
            df_a['pnl']    = pd.to_numeric(df_a['pnl'], errors='coerce').fillna(0)
            df_a['date']   = pd.to_datetime(df_a['date'], errors='coerce')
            df_a['win']    = df_a['result'] == 'Green'
            df_a['dow']    = df_a['date'].dt.strftime('%a')
            df_a['hour']   = df_a['date'].dt.hour

            ana_col1, ana_col2, ana_col3 = st.columns(3)

            with ana_col1:
                st.markdown("**Win Rate by Strategy**")
                strat_g = (df_a.groupby('strategy')
                           .agg(trades=('win','count'), wins=('win','sum'), pnl=('pnl','sum'))
                           .reset_index())
                strat_g['win_rate'] = strat_g['wins'] / strat_g['trades'] * 100
                strat_g = strat_g.sort_values('win_rate', ascending=False).head(8)
                strat_g['label'] = strat_g['strategy'].str[:20]
                fig_s = go.Figure(go.Bar(
                    x=strat_g['win_rate'], y=strat_g['label'],
                    orientation='h',
                    marker_color=['#2ecc71' if w >= 50 else '#e74c3c' for w in strat_g['win_rate']],
                    text=[f"{w:.0f}% ({t})" for w, t in zip(strat_g['win_rate'], strat_g['trades'])],
                    textposition='outside',
                ))
                fig_s.update_layout(template='plotly_dark', height=280,
                                    margin=dict(l=10,r=30,t=10,b=10),
                                    xaxis=dict(range=[0, 110], title="Win %"))
                st.plotly_chart(fig_s, width="stretch")

            with ana_col2:
                st.markdown("**Win Rate by Day**")
                dow_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
                dow_g = (df_a.groupby('dow')
                         .agg(trades=('win','count'), wins=('win','sum'))
                         .reindex(dow_order).reset_index())
                dow_g['win_rate'] = dow_g['wins'] / dow_g['trades'] * 100
                fig_d = go.Figure(go.Bar(
                    x=dow_g['dow'], y=dow_g['win_rate'],
                    marker_color=['#2ecc71' if (w >= 50 if not pd.isna(w) else False) else '#e74c3c'
                                  for w in dow_g['win_rate']],
                    text=[f"{w:.0f}%" if not pd.isna(w) else "" for w in dow_g['win_rate']],
                    textposition='outside',
                ))
                fig_d.update_layout(template='plotly_dark', height=280,
                                    margin=dict(l=10,r=10,t=10,b=10),
                                    yaxis=dict(range=[0, 110], title="Win %"))
                st.plotly_chart(fig_d, width="stretch")

            with ana_col3:
                st.markdown("**P&L Distribution**")
                fig_p = go.Figure(go.Histogram(
                    x=df_a['pnl'],
                    marker_color='#3498db',
                    nbinsx=15,
                ))
                fig_p.add_vline(x=0, line_color='#e74c3c', line_dash='dash')
                fig_p.update_layout(template='plotly_dark', height=280,
                                    margin=dict(l=10,r=10,t=10,b=10),
                                    xaxis_title="P&L ($)", yaxis_title="# trades")
                st.plotly_chart(fig_p, width="stretch")
        else:
            st.info("Log at least 3 trades to unlock analytics — strategy win rates, best days, P&L distribution.")
