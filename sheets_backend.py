"""
sheets_backend.py
Google Sheets persistence for Small Account Dashboard.
Falls back silently to CSV/local when Sheets credentials are not configured.
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

TRADE_FIELDS     = ['date', 'ticker', 'strategy', 'side', 'entry', 'exit', 'pnl', 'result', 'notes']
TENDENCY_FIELDS  = ['date', 'tendency']


@st.cache_resource
def _sheets_client():
    """Return authenticated gspread client, or None if secrets not present."""
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=SCOPES,
        )
        return gspread.authorize(creds)
    except Exception:
        return None


def _spreadsheet():
    client = _sheets_client()
    if not client:
        return None
    try:
        sheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
        return client.open_by_key(sheet_id)
    except Exception:
        return None


def _worksheet(name: str, headers: list):
    """Get or create a worksheet tab with the given headers."""
    ss = _spreadsheet()
    if not ss:
        return None
    try:
        ws = ss.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(title=name, rows=1000, cols=len(headers))
        ws.append_row(headers)
    return ws


def sheets_available() -> bool:
    return _sheets_client() is not None


# ── Trades ────────────────────────────────────────────────────────────────────

def load_trades() -> list:
    ws = _worksheet("Trades", TRADE_FIELDS)
    if not ws:
        return []
    try:
        return ws.get_all_records()
    except Exception:
        return []


def save_trade(trade: dict):
    ws = _worksheet("Trades", TRADE_FIELDS)
    if not ws:
        return
    try:
        ws.append_row([str(trade.get(f, '')) for f in TRADE_FIELDS])
    except Exception:
        pass


# ── Tendencies ────────────────────────────────────────────────────────────────

def load_tendencies() -> list:
    ws = _worksheet("Tendencies", TENDENCY_FIELDS)
    if not ws:
        return []
    try:
        return ws.get_all_records()
    except Exception:
        return []


def save_tendency(text: str):
    ws = _worksheet("Tendencies", TENDENCY_FIELDS)
    if not ws:
        return
    try:
        ws.append_row([datetime.now().strftime('%Y-%m-%d'), text])
    except Exception:
        pass
