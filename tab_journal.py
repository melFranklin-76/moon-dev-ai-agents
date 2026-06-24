"""Tab 5 — Journal: Trade log, Webull CSV import, Google Sheets export."""
import streamlit as st
import pandas as pd
from datetime import datetime, date
from pathlib import Path


def render(tab, *, ALL_STRATEGIES, TRADE_FIELDS, save_trade, load_trades):
    with tab:
        st.markdown("## 📝 TRADE JOURNAL")
        st.markdown("*Log every trade — wins and losses*")

        # ── Three-Strike Auto-Block ──────────────────────────────────────────
        _reds_today = st.session_state.daily_reds
        _blocked    = _reds_today >= 3
        if _blocked:
            st.markdown("""
            <div class="red-box">
            <h2>🛑 THREE STRIKES — JOURNAL LOCKED FOR TODAY</h2>
            <p>You've had <strong>3 red trades</strong> today. The rules are clear: <strong>STOP TRADING.</strong></p>
            <p>No more setups today. Close your charts. Review your tendencies. Come back tomorrow fresh.</p>
            <p style="color:#f39c12;"><em>"The best trade is sometimes no trade." — every pro trader ever</em></p>
            </div>
            """, unsafe_allow_html=True)
        elif _reds_today > 0:
            st.markdown(
                f'<div class="yellow-box"><p>⚠️ <strong>{_reds_today}/3 red trades today.</strong> '
                f'One more red trade locks the journal. Trade only A+ setups now.</p></div>',
                unsafe_allow_html=True
            )

        # ── Webull CSV Import ────────────────────────────────────────────────
        with st.expander("📥 Import from Webull CSV", expanded=False):
            st.markdown("""
            **How to export from Webull:**
            1. Webull app → **Account** → **Orders** (top right)
            2. Filter to **Options** → tap ↗ export icon (top right)
            3. Choose date range → **Export**
            4. Upload the CSV file here
            """)
            st.caption("All pairing is automatic — buys matched to sells, P&L calculated.")

            _wb_file = st.file_uploader("Upload Webull Order History CSV",
                                        type=["csv"], key="wb_csv_uploader")
            if _wb_file:
                _import_webull_csv(_wb_file, TRADE_FIELDS, save_trade, load_trades)

        # ── Google Sheets Export ─────────────────────────────────────────────
        with st.expander("📊 Export to Google Sheets", expanded=False):
            _google_sheets_export(TRADE_FIELDS)

        with st.expander("➕ Log New Trade", expanded=False and not _blocked):
            c1, c2 = st.columns(2)
            with c1:
                ticker_sel   = st.text_input("Ticker", value=st.session_state.get('selected_ticker', ''), placeholder="e.g. NVDA", key="journal_ticker").upper().strip()
                strategy_sel = st.selectbox("Strategy", ALL_STRATEGIES)
                side_sel     = st.radio("Side", ["Call", "Put"])
                entry_p      = st.number_input("Entry Price ($)", value=0.66, step=0.01, min_value=0.01)
            with c2:
                exit_p  = st.number_input("Exit Price ($)", value=0.82, step=0.01, min_value=0.01)
                pnl_val = round((exit_p - entry_p) * 100, 2)
                st.metric("P/L This Trade", f"${pnl_val:+.2f}")
                result_sel = st.radio("Result", ["Green", "Flat", "Red"])
                notes_val  = st.text_area("Notes", placeholder="What did you see? Why enter? How did it feel?")

            if st.button("💾 Save Trade", type="primary", disabled=_blocked):
                trade = {
                    'date': datetime.now().isoformat(), 'ticker': ticker_sel,
                    'strategy': strategy_sel, 'side': side_sel,
                    'entry': entry_p, 'exit': exit_p, 'pnl': pnl_val,
                    'result': result_sel, 'notes': notes_val,
                }
                st.session_state.trades.append(trade)
                save_trade(trade)
                st.success(f"Trade logged! P/L: ${pnl_val:+.2f}")
                st.rerun()

        st.markdown("### Trade History")
        if st.session_state.trades:
            df_j = pd.DataFrame(st.session_state.trades)
            show = [c for c in TRADE_FIELDS if c in df_j.columns]
            st.dataframe(df_j[show], width="stretch")
            st.download_button(
                "📥 Export to CSV",
                df_j.to_csv(index=False),
                f"trades_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
        else:
            st.info("No trades logged yet. Start trading and log your first trade!")


def _import_webull_csv(_wb_file, TRADE_FIELDS, save_trade, load_trades):
    try:
        _wb_df = pd.read_csv(_wb_file)
        _wb_df.columns = [c.strip() for c in _wb_df.columns]
        st.markdown(f"**{len(_wb_df)} rows · Columns:** `{list(_wb_df.columns)}`")

        def _find_col(df, *keywords):
            for kw in keywords:
                for c in df.columns:
                    if kw.lower() in c.lower():
                        return c
            return None

        _sym_c  = _find_col(_wb_df, 'symbol', 'ticker', 'option')
        _side_c = _find_col(_wb_df, 'side', 'action', 'buy/sell', 'type')
        _px_c   = _find_col(_wb_df, 'avg. price', 'avg price', 'price', 'fill')
        _qty_c  = _find_col(_wb_df, 'filled qty', 'qty', 'quantity', 'shares')
        _dt_c   = _find_col(_wb_df, 'filled at', 'placed', 'date', 'time')
        _st_c   = _find_col(_wb_df, 'status')

        if not _sym_c or not _side_c or not _px_c:
            st.error(
                f"Couldn't auto-detect columns. Found: {list(_wb_df.columns)}\n\n"
                "Expected columns containing: symbol, side (buy/sell), price."
            )
            return

        _wdf = _wb_df.copy()
        if _st_c:
            _wdf = _wdf[_wdf[_st_c].astype(str).str.lower()
                        .isin(['filled', 'complete', 'executed', 'all filled'])]

        _buys  = _wdf[_wdf[_side_c].astype(str).str.upper()
                      .isin(['BUY', 'BOUGHT', 'B', 'BUY TO OPEN'])].copy()
        _sells = _wdf[_wdf[_side_c].astype(str).str.upper()
                      .isin(['SELL', 'SOLD', 'S', 'SELL TO CLOSE'])].copy()

        _matched = set()
        _parsed  = []
        for _, _br in _buys.iterrows():
            _bsym = str(_br[_sym_c]).strip()
            try:
                _bpx = float(str(_br[_px_c]).replace('$','').replace(',',''))
            except Exception:
                continue
            _bqty = 1
            if _qty_c:
                try:
                    _bqty = max(1, int(float(str(_br[_qty_c]).replace(',',''))))
                except Exception:
                    pass
            _bdt = str(_br[_dt_c]).split()[0] if _dt_c else date.today().isoformat()

            for _si, _sr in _sells.iterrows():
                if _si in _matched:
                    continue
                if str(_sr[_sym_c]).strip() != _bsym:
                    continue
                try:
                    _spx = float(str(_sr[_px_c]).replace('$','').replace(',',''))
                except Exception:
                    continue
                _sqty = 1
                if _qty_c:
                    try:
                        _sqty = max(1, int(float(str(_sr[_qty_c]).replace(',',''))))
                    except Exception:
                        pass
                _matched.add(_si)
                _pnl   = round((_spx - _bpx) * min(_bqty, _sqty) * 100, 2)
                _under = _bsym.split()[0] if ' ' in _bsym else _bsym
                _side  = ('Put' if 'put' in _bsym.lower() else 'Call')
                _parsed.append({
                    'date':     _bdt,
                    'ticker':   _under,
                    'strategy': 'Imported — Webull',
                    'side':     _side,
                    'entry':    _bpx,
                    'exit':     _spx,
                    'pnl':      _pnl,
                    'result':   'Green' if _pnl >= 0 else 'Red',
                    'notes':    _bsym,
                })
                break

        if not _parsed:
            st.warning(
                "No matched buy→sell pairs found. "
                "Make sure you exported **Options** order history "
                "and that both legs of each trade are in the file."
            )
            st.dataframe(_wb_df.head(5))
        else:
            st.success(f"✅ {len(_parsed)} completed trades detected")
            st.dataframe(pd.DataFrame(_parsed), width="stretch")
            if st.button(f"✅ Import {len(_parsed)} trades", key="wb_import_btn",
                         type="primary"):
                for _t in _parsed:
                    save_trade(_t)
                st.session_state.trades = load_trades()
                st.cache_data.clear()
                st.success(f"Imported {len(_parsed)} trades! Journal updated.")
                st.rerun()
    except Exception as _e:
        st.error(f"Error reading CSV: {_e}")
        st.caption("Try exporting again from Webull with the default settings.")


def _google_sheets_export(TRADE_FIELDS):
    st.markdown("""
    **Sync your trades to Google Sheets for advanced analysis and sharing.**

    [How to get your Sheet ID](https://developers.google.com/sheets/api/guides/concepts#spreadsheet_id)
    — it's the long string in the URL between `/d/` and `/edit`.
    """)
    _gs_sheet_id  = st.text_input("Google Sheet ID", placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms", key="gs_sheet_id")
    _gs_tab_name  = st.text_input("Sheet Tab Name", value="Trades", key="gs_tab_name")

    if st.button("Sync Now", type="primary", key="gs_sync_btn"):
        try:
            import gspread
            from google.oauth2.service_account import Credentials as _GCreds

            _CREDS_PATH = Path(__file__).parent / "src" / "data" / "small_account" / "google_creds.json"
            if not _CREDS_PATH.exists():
                st.error(f"""
**google_creds.json not found** at `{_CREDS_PATH}`

**How to set it up:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable **Google Sheets API** + **Google Drive API**
3. IAM & Admin → Service Accounts → Create service account
4. Download the JSON key file
5. Save it as: `{_CREDS_PATH}`
6. Share your Google Sheet with the service account email (found in the JSON)
                """)
            elif not _gs_sheet_id.strip():
                st.warning("Enter a Google Sheet ID above.")
            else:
                _scopes  = [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ]
                _creds   = _GCreds.from_service_account_file(str(_CREDS_PATH), scopes=_scopes)
                _gc      = gspread.authorize(_creds)
                _sh      = _gc.open_by_key(_gs_sheet_id.strip())
                _tab_nm  = _gs_tab_name.strip() or "Trades"
                try:
                    _ws  = _sh.worksheet(_tab_nm)
                except gspread.WorksheetNotFound:
                    _ws  = _sh.add_worksheet(title=_tab_nm, rows=1000, cols=20)
                    _ws.append_row(TRADE_FIELDS)

                _existing = _ws.get_all_records()
                _exist_keys = set()
                for _row in _existing:
                    _k = (
                        str(_row.get('date', ''))[:10],
                        str(_row.get('ticker', '')).upper(),
                        str(_row.get('side', '')).lower(),
                    )
                    _exist_keys.add(_k)

                _new_trades = []
                for _t in st.session_state.get('trades', []):
                    _k = (
                        str(_t.get('date', ''))[:10],
                        str(_t.get('ticker', '')).upper(),
                        str(_t.get('side', '')).lower(),
                    )
                    if _k not in _exist_keys:
                        _new_trades.append(_t)

                for _nt in _new_trades:
                    _ws.append_row([str(_nt.get(f, '')) for f in TRADE_FIELDS])

                st.success(f"Synced {len(_new_trades)} new trades to Google Sheets ({_tab_nm}).")

        except ImportError:
            st.info(
                "gspread / google-auth not installed. Run: "
                "`pip install gspread>=6.0.0 google-auth>=2.0.0`"
            )
        except Exception as _gs_err:
            st.error(f"Google Sheets sync failed: {_gs_err}")
