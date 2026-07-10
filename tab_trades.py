"""Tab 3 — Trade Cards: Strategy reference for strategies 159–178."""
import streamlit as st

CORE_3 = {
    "163. VWAP Reclaim (Long)": (
        "Price dips below VWAP, then reclaims it on a volume burst (1.2x+ avg). "
        "Buy call on the reclaim candle close. Stop: close back below VWAP or -30% premium."
    ),
    "172. Whole-Dollar Break-and-Hold": (
        "Price breaks a whole-dollar level and holds above it for 2 consecutive 1-min closes. "
        "Buy call (or put on breakdown). Stop: back through the level or -30% premium."
    ),
    "162. Premarket High Retest-and-Go": (
        "Stock retests the premarket high after open and pushes through with volume. "
        "Your two logged trades used this one. Stop: rejection at PM high or -30% premium."
    ),
}


def render(tab, *, ALL_STRATEGIES):
    with tab:
        st.markdown("## 🎯 YOUR CORE 3")
        st.markdown(
            "*Master these before touching anything below. With ~1 trade a day, "
            "three strategies is all the sample size you can feed.*"
        )

        for name, desc in CORE_3.items():
            st.markdown(f"""
            <div class="green-box">
            <h3>#{name}</h3>
            <p>{desc}</p>
            <p style="color:#8b92a8; font-size:12px;">
              Targets: +15% (half) · +25% (rest) &nbsp;|&nbsp; Stop: −30% premium, no exceptions
              &nbsp;|&nbsp; Window: 9:30–10:00 AM CT
            </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🗄️ Archive — the other 17")
        st.caption(
            "Unlock these one at a time, only after the Performance tab shows 30+ logged trades "
            "and a clear read on which of the Core 3 actually pays you."
        )

        core_names = set(CORE_3)
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
                    marker = " ⭐ **CORE**" if s in core_names else ""
                    st.markdown(f"- {s}{marker}")
