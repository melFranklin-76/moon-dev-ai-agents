"""Tab 3 — Trade Cards: Strategy reference for strategies 159–178."""
import streamlit as st


def render(tab, *, ALL_STRATEGIES):
    with tab:
        st.markdown("## 🎴 YOUR 20 BEST-OF-THE-BEST")
        st.markdown("*Strategies 159–178 | Refined from 178 total*")

        strategy_groups = {
            "🚀 Momentum + Confirmation (159-162)":   ALL_STRATEGIES[0:4],
            "💧 VWAP Edge (163-165)":                 ALL_STRATEGIES[4:7],
            "📈 Pullback Continuations (166-168)":    ALL_STRATEGIES[7:10],
            "🔄 Reversal / Mean-Reversion (169-171)": ALL_STRATEGIES[10:13],
            "💰 Price Levels & Auction (172-175)":    ALL_STRATEGIES[13:17],
            "🔗 Correlation (176-177)":               ALL_STRATEGIES[17:19],
            "⏰ Time-of-Day (178)":                   ALL_STRATEGIES[19:],
        }
        for cat, strats in strategy_groups.items():
            with st.expander(cat, expanded=False):
                for s in strats:
                    st.markdown(f"- {s}")
