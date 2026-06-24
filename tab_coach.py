"""Tab 9 — Coach: Tendencies log + pre-trade checklist."""
import streamlit as st
import pandas as pd
from datetime import datetime


def render(tab, *, save_tendency, load_tendencies):
    with tab:
        st.markdown("## 🧠 TENDENCIES COACH")
        st.markdown("*Log your mistakes. Review before every trading session. Break the patterns.*")
        st.caption("74% of small account failures come from repeating the same behavioral mistakes — not from bad strategy.")

        c_left, c_right = st.columns([1, 1])

        with c_left:
            st.markdown("### Log a Tendency / Mistake")
            tend_text = st.text_area(
                "Describe the pattern:",
                height=120,
                placeholder="e.g. Held past 9:30 AM CT because I was convinced it would keep running. Lost 30% of premium to theta. Rule: breakout or bailout."
            )
            if st.button("💾 Save Tendency", type="primary"):
                if tend_text.strip():
                    save_tendency(tend_text.strip())
                    st.session_state.tendencies = load_tendencies()
                    st.success("Logged.")
                    st.rerun()

            st.markdown("---")
            st.markdown("### Pre-Trade Checklist")
            st.markdown("*Check all boxes before placing any trade*")
            pre_checks = [
                "Reviewed my tendencies list →",
                "Setup is A or A+ (Catalyst Grader tab)",
                "Regime is green or yellow (Regime tab)",
                "Entry time is before 9:30 AM CT (momentum window)",
                "Options liquidity verified (OI > 200, spread < 10%)",
                "1 contract only — icebreaker rule",
                "Stop loss level pre-defined before entry",
                "This is not revenge trading",
                "I have not already had 3 losing trades today",
            ]
            for i, item in enumerate(pre_checks):
                st.checkbox(item, key=f"pre_{i}")

        with c_right:
            st.markdown("### Your Tendencies")
            tends = st.session_state.tendencies
            if tends:
                for t in reversed(tends[-15:]):
                    st.markdown(f"""
                    <div class="yellow-box">
                    <p><small>📅 {t.get('date', '')}</small></p>
                    <p>{t.get('tendency', '')}</p>
                    </div>""", unsafe_allow_html=True)

                df_t = pd.DataFrame(tends)
                st.download_button(
                    "📥 Export Tendencies",
                    df_t.to_csv(index=False),
                    f"tendencies_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
            else:
                st.info("No tendencies logged yet. After every losing trade, come here and describe what went wrong. This is where your edge gets built.")
                st.markdown("""
**Common tendencies to watch for:**
- Holding past 9:30 AM CT (theta enemy)
- Chasing after missing the first entry
- Revenge trading after a loss
- Entering B-grade setups on slow days
- Ignoring the regime tab (trading into bad environment)
- Skipping stop loss discipline
""")
