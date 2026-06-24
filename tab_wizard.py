"""Tab 11 — Entry Wizard: Pre-flight decision gate before trade entry."""
import streamlit as st
from datetime import datetime, date


def render(tab, *, get_iv_rank, get_earnings_date, get_options_snapshot):
    with tab:
        st.markdown("### 🚦 Should I Enter This Trade?")
        st.caption(
            "Pre-flight check before you hit buy on Webull. Pulls in your daily P&L, "
            "the three-strike rule, time-of-day filter, IV rank, spread quality, "
            "earnings risk, and position sizing — then gives you ONE verdict."
        )

        # ── Inputs ───────────────────────────────────────────────────────────
        wc1, wc2, wc3 = st.columns([2, 1, 1])
        with wc1:
            w_sym = st.text_input(
                "Ticker",
                value=st.session_state.get('selected_ticker', '') or '',
                key='wizard_sym',
            ).upper().strip()
        with wc2:
            w_dir = st.radio("Direction", ["CALL", "PUT"], horizontal=True, key='wizard_dir')
        with wc3:
            w_strat = st.text_input("Strategy #", value="", placeholder="e.g. 163", key='wizard_strat')

        wc4, wc5, wc6 = st.columns(3)
        with wc4:
            w_strike  = st.number_input("Strike ($)", min_value=0.0, value=0.0, step=0.5, key='wizard_strike')
        with wc5:
            w_premium = st.number_input("Est. Premium ($/contract)", min_value=0.0, value=0.0, step=0.05, key='wizard_premium')
        with wc6:
            w_exp     = st.date_input("Expiry", value=date.today(), key='wizard_exp')

        # ── Required-confirmation checkboxes ─────────────────────────────────
        st.markdown("**Required confirmations** — check each before running the gate:")
        rcc1, rcc2 = st.columns(2)
        with rcc1:
            cb_stop   = st.checkbox("Stop-loss defined at −50% premium", key='wizard_cb_stop')
            cb_target = st.checkbox("Target defined (+25% or +50%)",     key='wizard_cb_target')
            cb_time   = st.checkbox("Time-exit defined (e.g. by 3:30 PM ET)", key='wizard_cb_time')
        with rcc2:
            cb_grade  = st.checkbox("Catalyst Grader is A or A+ for this ticker", key='wizard_cb_grade')
            cb_one    = st.checkbox("This is my ONE trade today",        key='wizard_cb_one')
            cb_size   = st.checkbox("Total cost fits in $80 max position", key='wizard_cb_size')

        run_wizard = st.button("🚦 Run Entry Check", type='primary', key='wizard_run')

        if run_wizard and w_sym:
            _run_checks(w_sym, w_dir, w_strike, w_premium, w_exp,
                        cb_stop, cb_target, cb_time, cb_grade, cb_one, cb_size,
                        get_iv_rank, get_earnings_date, get_options_snapshot)


def _run_checks(w_sym, w_dir, w_strike, w_premium, w_exp,
                cb_stop, cb_target, cb_time, cb_grade, cb_one, cb_size,
                get_iv_rank, get_earnings_date, get_options_snapshot):
    with st.spinner(f"Running pre-flight checks for {w_sym}..."):
        iv     = get_iv_rank(w_sym)
        earn   = get_earnings_date(w_sym)
        opts   = get_options_snapshot(w_sym)

        contract_cost = w_premium * 100 if w_premium > 0 else 0
        stop_loss     = contract_cost * 0.50
        target_25     = contract_cost * 0.25
        target_50     = contract_cost * 0.50

        dte = max((w_exp - date.today()).days, 0)

        now_et = datetime.now()
        hr, mn = now_et.hour, now_et.minute
        mins_since_open = (hr - 9) * 60 + (mn - 30)
        in_first_5    = 0 <= mins_since_open < 5
        in_midday     = 150 <= mins_since_open < 240
        in_death_zone = in_first_5 or in_midday
        after_330     = mins_since_open >= 360

        spread_pct = None
        oi_at_strike = None
        if opts.get("available"):
            rows = opts['calls'] if w_dir == 'CALL' else opts['puts']
            if rows and w_strike > 0:
                closest = min(rows, key=lambda r: abs(r['strike'] - w_strike))
                spread_pct  = closest['spread_pct']
                oi_at_strike = closest['oi']

        # ── HARD BLOCKERS ────────────────────────────────────────────────
        blockers = []
        if st.session_state.daily_pnl <= -50:
            blockers.append(("Daily loss limit hit", f"P&L is ${st.session_state.daily_pnl:.0f} — already at −$50 cap"))
        if st.session_state.daily_reds >= 3:
            blockers.append(("Three-strike rule", f"{st.session_state.daily_reds} red trades today — stop"))
        if contract_cost > 80:
            blockers.append(("Position too large", f"${contract_cost:.0f} exceeds $80 max per trade"))
        if in_death_zone:
            z = "first 5 min (no opening range)" if in_first_5 else "midday chop (12:00–1:30 PM ET)"
            blockers.append(("Death zone", f"It's the {z} — wait it out"))
        if not all([cb_stop, cb_target, cb_time, cb_grade, cb_one, cb_size]):
            missing = sum(1 for c in [cb_stop, cb_target, cb_time, cb_grade, cb_one, cb_size] if not c)
            blockers.append(("Missing confirmations", f"{missing} required checkbox(es) unchecked"))

        # ── WARNINGS ─────────────────────────────────────────────────────
        warnings = []
        if earn.get("available") and earn.get("days") is not None and earn['days'] <= 5 and w_dir == 'CALL':
            warnings.append(("Earnings within 5 days", f"IV crush risk — earnings in {earn['days']}d"))
        if iv.get("available") and iv.get("rank", 0) > 80:
            warnings.append(("IV Rank > 80", f"Paying peak vol (rank {iv['rank']:.0f})"))
        if spread_pct is not None and spread_pct > 15:
            warnings.append(("Wide spread", f"Bid/ask spread is {spread_pct:.0f}% of mid — execution risk"))
        if dte <= 1:
            warnings.append(("0–1 DTE", "Same-day expiry — gamma risk is extreme"))
        if after_330:
            warnings.append(("After 3:30 PM ET", "Time decay accelerates into close"))

        # ── SOFT WARNINGS ────────────────────────────────────────────────
        soft = []
        if spread_pct is not None and 10 < spread_pct <= 15:
            soft.append(f"Spread is {spread_pct:.0f}% of mid (10–15% range)")
        if iv.get("available") and 60 <= iv.get("rank", 0) <= 80:
            soft.append(f"IV rank {iv['rank']:.0f} (60–80 range)")
        if oi_at_strike is not None and oi_at_strike < 200:
            soft.append(f"Open interest only {oi_at_strike} at ${w_strike:.0f} strike (target: >200)")

        # ── Verdict ──────────────────────────────────────────────────────
        if blockers:
            verdict_color = "#e74c3c"
            verdict_text  = "🔴 SKIP"
            verdict_sub   = f"{len(blockers)} hard blocker(s) — DO NOT enter this trade"
        elif len(warnings) >= 2:
            verdict_color = "#f39c12"
            verdict_text  = "🟡 WAIT"
            verdict_sub   = f"{len(warnings)} strong warnings — improve setup before entering"
        elif warnings:
            verdict_color = "#f39c12"
            verdict_text  = "🟡 WAIT"
            verdict_sub   = "1 warning — consider waiting for cleaner setup"
        else:
            verdict_color = "#2ecc71"
            verdict_text  = "🟢 ENTER"
            verdict_sub   = "All critical checks passed — execute your plan"

        st.markdown(
            f"""
            <div style='background:{verdict_color}; padding:24px; border-radius:12px;
                        margin:16px 0; text-align:center; box-shadow:0 4px 18px rgba(0,0,0,0.4);'>
                <h1 style='color:white; margin:0; font-size:48px;'>{verdict_text}</h1>
                <p style='color:white; margin:8px 0 0 0; font-size:16px; opacity:0.95;'>
                    {verdict_sub}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if w_premium > 0:
            pcc1, pcc2, pcc3, pcc4 = st.columns(4)
            pcc1.metric("Cost (1 ct)",  f"${contract_cost:.0f}")
            pcc2.metric("Risk at −50%", f"${stop_loss:.0f}")
            pcc3.metric("Target +25%",  f"+${target_25:.0f}")
            pcc4.metric("Target +50%",  f"+${target_50:.0f}")

        with st.expander(f"🛑 Hard Blockers ({len(blockers)})", expanded=bool(blockers)):
            if blockers:
                for name, why in blockers:
                    st.markdown(f"- ❌ **{name}** — {why}")
            else:
                st.markdown("- ✅ Daily P&L OK  \n- ✅ Three-strike rule OK  \n- ✅ Position size OK  \n- ✅ Not in death zone  \n- ✅ All confirmations checked")

        with st.expander(f"⚠️ Strong Warnings ({len(warnings)})", expanded=bool(warnings)):
            if warnings:
                for name, why in warnings:
                    st.markdown(f"- ⚠️ **{name}** — {why}")
            else:
                st.markdown("No strong warnings — setup looks clean on the macro filters.")

        if soft:
            with st.expander(f"💡 Soft Warnings ({len(soft)})"):
                for s in soft:
                    st.markdown(f"- 💡 {s}")

        with st.expander("🔎 What the wizard saw"):
            cdc1, cdc2 = st.columns(2)
            with cdc1:
                st.markdown("**Account state**")
                st.markdown(f"- Daily P&L: **${st.session_state.daily_pnl:.2f}** (of −$50 cap)")
                st.markdown(f"- Red trades today: **{st.session_state.daily_reds}** (of 3 max)")
                st.markdown(f"- Time: **{now_et.strftime('%I:%M %p')}** server-local")
                st.markdown(f"- Minutes since open: **{mins_since_open}**")
            with cdc2:
                st.markdown("**Trade signals**")
                st.markdown(f"- IV Rank: **{iv.get('rank','—')}**" + (f" ({iv.get('label','')})" if iv.get('available') else " (not available)"))
                st.markdown(f"- Earnings in: **{earn.get('days','—')}d**" + (f" ({earn.get('date_str','')})" if earn.get('available') else " (not available)"))
                st.markdown(f"- Spread @ ${w_strike:.0f}: **{spread_pct if spread_pct is not None else '—'}%**")
                st.markdown(f"- OI @ ${w_strike:.0f}: **{oi_at_strike if oi_at_strike is not None else '—'}**")
                st.markdown(f"- Days to expiry: **{dte}**")
