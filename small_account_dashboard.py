#!/usr/bin/env python3
"""
Small Account Options Scalper Dashboard
$250 Webull Account | Level 2 | 20 Best Strategies

To run this dashboard:
1. Install dependencies: pip install streamlit plotly pandas
2. Run: streamlit run small_account_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="$250 Scalper Dashboard",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for small account trader aesthetic
st.markdown("""
<style>
    .main {background-color: #0e1117;}
    .stMetric {background-color: #1e2130; padding: 15px; border-radius: 10px;}
    .stMetric label {color: #8b92a8 !important; font-size: 14px !important;}
    .stMetric [data-testid="stMetricValue"] {color: #ffffff !important; font-size: 32px !important;}
    .green-box {background-color: #1a3d1a; padding: 15px; border-radius: 10px; border: 2px solid #2ecc71;}
    .red-box {background-color: #3d1a1a; padding: 15px; border-radius: 10px; border: 2px solid #e74c3c;}
    .yellow-box {background-color: #3d361a; padding: 15px; border-radius: 10px; border: 2px solid #f39c12;}
    .trade-card {background-color: #1e2130; padding: 20px; border-radius: 10px; margin: 10px 0;}
    h1 {color: #2ecc71 !important;}
    h2 {color: #3498db !important;}
    h3 {color: #f39c12 !important;}
    .big-text {font-size: 48px; font-weight: bold; text-align: center;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'trades' not in st.session_state:
    st.session_state.trades = []
if 'challenge_days' not in st.session_state:
    st.session_state.challenge_days = [0] * 10  # 0=pending, 1=green, -1=red
if 'current_streak' not in st.session_state:
    st.session_state.current_streak = 0
if 'account_balance' not in st.session_state:
    st.session_state.account_balance = 250.00
if 'daily_pnl' not in st.session_state:
    st.session_state.daily_pnl = 0.00

# Helper function to connect to Alpaca
def get_alpaca_connection():
    """Connect to Alpaca API"""
    try:
        import alpaca_trade_api as tradeapi
        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY')
        base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        if not api_key or not secret_key:
            return None
            
        api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
        return api
    except Exception as e:
        st.error(f"Alpaca connection error: {e}")
        return None

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("# 🌙 SMALL ACCOUNT SCALPER")
    st.markdown("### $250 Challenge | Level 2 | Options Only")

st.markdown("---")

# Top Stats Row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("💰 Account", f"${st.session_state.account_balance:.2f}")
    
with col2:
    pnl_color = "🟢" if st.session_state.daily_pnl >= 0 else "🔴"
    pnl_pct = (st.session_state.daily_pnl / st.session_state.account_balance) * 100 if st.session_state.account_balance > 0 else 0
    st.metric("📈 Today's P/L", f"{pnl_color} ${st.session_state.daily_pnl:.2f}", f"{pnl_pct:.1f}%")
    
with col3:
    st.metric("🎯 Challenge", f"Day {st.session_state.current_streak}/10")
    
with col4:
    open_positions = len([t for t in st.session_state.trades if t.get('status') == 'open'])
    st.metric("📦 Open", str(open_positions))
    
with col5:
    buying_power = st.session_state.account_balance - (open_positions * 80)
    st.metric("💵 Buying Power", f"${buying_power:.2f}")

st.markdown("---")

# Main Content Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Live Scanner", 
    "📊 My Tickers", 
    "🎴 Trade Cards",
    "📈 Performance",
    "📝 Journal"
])

# TAB 1: LIVE SCANNER
with tab1:
    st.markdown("## 🟢 LIVE SETUP SCANNER")
    st.markdown("*Scanning your 20 BEST strategies for entry signals...*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Active Setups")
        
        # Example setup (in real version, this would scan real data)
        st.markdown("""
        <div class="green-box">
        <h3>$MARA - BTC-Lead Sync (#177) 🔥</h3>
        <p><strong>Trigger:</strong> BTCUSD broke $72,500 ↑<br>
        MARA reclaimed VWAP at $15.32</p>
        <p><strong>Entry:</strong> $15.50 Call (Nov 8, Δ 0.42)<br>
        <strong>Spread:</strong> $0.65 x $0.67 ✅ TIGHT<br>
        <strong>Premium:</strong> $66 (1 contract)</p>
        <p><strong>Stop:</strong> -$13 (-20%) OR lose VWAP<br>
        <strong>Target:</strong> $76 (+15%), $82 (+25%)</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 EXECUTE MARA TRADE", key="trade_mara", type="primary"):
            st.success("Trade executed! (Paper trading)")
            st.balloons()
        
        st.markdown("""
        <div class="yellow-box">
        <h3>$HOOD - VWAP Reclaim (#163) ⏳</h3>
        <p><strong>Status:</strong> Setting up...<br>
        Price approaching VWAP at $23.15</p>
        <p><strong>Wait for:</strong> 1-min close above VWAP + volume burst</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Pre-Market Checklist")
        
        checklist_items = [
            "Mark PM High/Low",
            "Mark Prior Day High/Low/Close",
            "Check BTC price (for MARA/CAN)",
            "Check earnings calendar",
            "Define Opening Range (wait 5 min)",
            "Plot VWAP",
            "Check Level 2 liquidity",
            "ONE setup only today"
        ]
        
        for i, item in enumerate(checklist_items):
            checked = st.checkbox(item, key=f"check_{i}")
        
        st.markdown("---")
        
        st.markdown("### ⚠️ Risk Management")
        st.markdown("""
        <div class="red-box">
        <p><strong>Max Loss Today:</strong> $50 (20% of account)</p>
        <p><strong>Current Loss:</strong> $0</p>
        <p><strong>Remaining Risk:</strong> $50 🟢</p>
        <hr>
        <p><strong>Max Position Size:</strong> $80 (1 contract)</p>
        <p><strong>Current Position:</strong> $0</p>
        <p><strong>STOP TRADING at -$50!</strong> ⛔</p>
        </div>
        """, unsafe_allow_html=True)

# TAB 2: MY TICKERS
with tab2:
    st.markdown("## 📊 YOUR 6 TICKERS")
    
    # Mock data (in real version, pull from Alpaca/API)
    tickers = [
        {"symbol": "MARA", "price": 15.32, "change": 2.1, "volume": "4.2M", "vwap": 15.15, "best_setups": ["BTC-Lead (#177)", "ORB Hold (#159)", "VWAP Reclaim (#163)"]},
        {"symbol": "HOOD", "price": 23.45, "change": -0.8, "volume": "8.1M", "vwap": 23.52, "best_setups": ["VWAP Reclaim (#163)", "Whole-Dollar (#172)", "PMH Retest (#162)"]},
        {"symbol": "SOFI", "price": 8.92, "change": 1.3, "volume": "3.5M", "vwap": 8.88, "best_setups": ["POC Reclaim (#174)", "Prior Close (#148)", "VWAP Reject (#164)"]},
        {"symbol": "BBAI", "price": 3.67, "change": 0.5, "volume": "890K", "vwap": 3.65, "best_setups": ["News Spike (#150)", "ORB Break (#161)", "LVN Slide (#175)"]},
        {"symbol": "CAN", "price": 2.18, "change": 3.2, "volume": "1.2M", "vwap": 2.12, "best_setups": ["BTC Sync (#177)", "Whole-Dollar (#172)", "VWAP Double (#165)"]},
        {"symbol": "COMP", "price": 5.43, "change": -0.2, "volume": "456K", "vwap": 5.45, "best_setups": ["Index Lead (#176)", "POC Reclaim (#174)", "Inside Day (#156)"]},
    ]
    
    col1, col2, col3 = st.columns(3)
    
    for i, ticker in enumerate(tickers):
        with [col1, col2, col3][i % 3]:
            color = "🟢" if ticker['change'] > 0 else "🔴"
            
            st.markdown(f"""
            <div class="trade-card">
            <h2>${ticker['symbol']}</h2>
            <p class="big-text" style="color: {'#2ecc71' if ticker['change'] > 0 else '#e74c3c'};">${ticker['price']:.2f}</p>
            <p>{color} {ticker['change']:+.1f}% | Vol: {ticker['volume']}</p>
            <p><strong>VWAP:</strong> ${ticker['vwap']:.2f}</p>
            <hr>
            <p><strong>Best Setups:</strong></p>
            <ul>
            {"".join([f"<li>{setup}</li>" for setup in ticker['best_setups']])}
            </ul>
            </div>
            """, unsafe_allow_html=True)

# TAB 3: TRADE CARDS
with tab3:
    st.markdown("## 🎴 YOUR 20 BEST-OF-THE-BEST")
    st.markdown("*Strategies 159-178 | Refined from 178 total*")
    
    # Strategy categories
    categories = {
        "🚀 Momentum + Confirmation (159-162)": [
            "159. 1-min ORB + VWAP Hold",
            "160. 1-min ORB Fail → VWAP Reject",
            "161. 5-min OR Break + 1-min Flag",
            "162. Premarket High Retest-and-Go"
        ],
        "💧 VWAP Edge (163-165)": [
            "163. VWAP Reclaim (Long)",
            "164. VWAP Rejection (Short)",
            "165. VWAP Micro Double Bottom/Top"
        ],
        "📈 Pullback Continuations (166-168)": [
            "166. 9/20 EMA Pullback (Long)",
            "167. 9/20 EMA Pullback (Short)",
            "168. Higher-Low / Lower-High Continuation"
        ],
        "🔄 Reversal / Mean-Reversion (169-171)": [
            "169. Stop-Run Reclaim",
            "170. Exhaustion Wick Reversal",
            "171. Bollinger Squeeze Release"
        ],
        "💰 Price Levels & Auction (172-175)": [
            "172. Whole-Dollar Break-and-Hold",
            "173. Half-Dollar Rejection Fade",
            "174. POC Reclaim/Loss",
            "175. LVN Slide"
        ],
        "🔗 Correlation (176-177)": [
            "176. Index-Lead Sync (SPY/QQQ)",
            "177. BTC-Lead Sync (MARA/CAN)"
        ],
        "⏰ Time-of-Day (178)": [
            "178. Golden-Hour Range Break"
        ]
    }
    
    for category, strategies in categories.items():
        with st.expander(category, expanded=False):
            for strategy in strategies:
                st.markdown(f"- {strategy}")

# TAB 4: PERFORMANCE
with tab4:
    st.markdown("## 📈 10-DAY CHALLENGE TRACKER")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Challenge visualization
        days_display = []
        for i, day in enumerate(st.session_state.challenge_days):
            if day == 1:
                days_display.append("✅")
            elif day == -1:
                days_display.append("❌")
            else:
                days_display.append("⬜")
        
        st.markdown(f"""
        <div class="green-box">
        <h2>🏆 10-Day Prove-It Challenge</h2>
        <p style="font-size: 18px;">Goal: 10 consecutive green/flat days to prove discipline</p>
        <p style="font-size: 36px; text-align: center;">
        {' '.join(days_display)}
        </p>
        <p><strong>Current Streak:</strong> {st.session_state.current_streak} days 🔥</p>
        <p><strong>Status:</strong> {'ON TRACK!' if st.session_state.current_streak >= 3 else 'KEEP GOING!'}</p>
        <hr>
        <p style="color: #f39c12;">⚠️ One red day resets counter to 0!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Equity curve placeholder
        st.markdown("### Equity Curve")
        dates = pd.date_range(end=datetime.now(), periods=10, freq='D')
        equity = [250, 266, 274, 274, 289, 295, 310, 318, 325, 250]  # Mock data
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=equity, mode='lines+markers', 
                                name='Account Value', line=dict(color='#2ecc71', width=3)))
        fig.update_layout(
            template='plotly_dark',
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Date",
            yaxis_title="Account Value ($)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Today's Stats")
        st.metric("Trades", "1")
        st.metric("Win Rate", "100%")
        st.metric("Best Trade", "+25%")
        st.metric("Worst Trade", "N/A")
        
        st.markdown("### All-Time")
        st.metric("Total Trades", "3")
        st.metric("Total Win Rate", "100%")
        st.metric("Profit Factor", "2.4")
        st.metric("Max Drawdown", "-5%")

# TAB 5: JOURNAL
with tab5:
    st.markdown("## 📝 TRADE JOURNAL")
    st.markdown("*Log every trade for the 10-day challenge*")
    
    # Trade entry form
    with st.expander("➕ Log New Trade", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            ticker = st.selectbox("Ticker", ["MARA", "HOOD", "SOFI", "BBAI", "CAN", "COMP"])
            strategy = st.selectbox("Strategy", [
                "159. 1-min ORB + VWAP Hold",
                "163. VWAP Reclaim",
                "164. VWAP Rejection",
                "177. BTC-Lead Sync",
                "172. Whole-Dollar Break"
            ])
            side = st.radio("Side", ["Call", "Put"])
            entry_price = st.number_input("Entry Price ($)", value=0.66, step=0.01)
        
        with col2:
            exit_price = st.number_input("Exit Price ($)", value=0.82, step=0.01)
            pnl = (exit_price - entry_price) * 100  # 1 contract = 100 shares
            result = st.radio("Result", ["Green", "Flat", "Red"])
            notes = st.text_area("Notes", "BTC broke $72,500, MARA followed. Clean entry at VWAP reclaim.")
        
        if st.button("💾 Save Trade"):
            st.session_state.trades.append({
                'date': datetime.now(),
                'ticker': ticker,
                'strategy': strategy,
                'side': side,
                'entry': entry_price,
                'exit': exit_price,
                'pnl': pnl,
                'result': result,
                'notes': notes
            })
            st.success("Trade logged!")
            st.rerun()
    
    # Trade history table
    st.markdown("### Trade History")
    if st.session_state.trades:
        df = pd.DataFrame(st.session_state.trades)
        st.dataframe(df, use_container_width=True)
        
        # Export button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name=f"trades_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No trades logged yet. Start trading and log your first trade!")

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
    # Alpaca connection status
    st.markdown("### 🔌 Alpaca Connection")
    api = get_alpaca_connection()
    if api:
        try:
            account = api.get_account()
            st.success("✅ Connected")
            st.metric("Paper Balance", f"${float(account.cash):,.2f}")
        except:
            st.error("❌ Connection Failed")
    else:
        st.warning("⚠️ API keys not configured")
        st.info("Add keys to .env file")
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    if st.button("📊 View All Strategies"):
        st.info("See trading_ideas.md for all 178 strategies")
    
    st.markdown("---")
    
    # Resources
    st.markdown("### 📚 Resources")
    
    # Check which files exist
    workspace_path = "/Volumes/xcode/MoonDev/moon-dev-ai-agents"
    resources = [
        ("📖 Dashboard Guide (START HERE!)", "SMALL_ACCOUNT_DASHBOARD_GUIDE.md"),
        ("📝 Trading Ideas", "trading_ideas.md"),
        ("🔧 Alpaca Setup", "ALPACA_SETUP.md"),
        ("🚀 Quick Start", "QUICK_START.md")
    ]
    
    for title, filename in resources:
        filepath = os.path.join(workspace_path, filename)
        if os.path.exists(filepath):
            with st.expander(title):
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                        st.markdown(content)
                except Exception as e:
                    st.error(f"Error reading {filename}: {e}")
        else:
            st.text(f"{title} (file not found)")
    
    st.markdown("---")
    st.markdown("*Dashboard v1.0*")
    st.markdown("*Built for $250 accounts*")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #8b92a8;">
<p>🌙 <strong>Remember:</strong> One contract only until 10 green days | Respect your stops | Journal every trade</p>
<p>Made with ❤️ for small account traders</p>
</div>
""", unsafe_allow_html=True)

