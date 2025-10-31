# Small Account Dashboard - Complete Setup Guide

## Prerequisites

**Required:**
- Python 3.10+ installed
- Terminal access (Command Line)
- Text editor (VS Code, Cursor, or any editor)

**Optional but Recommended:**
- Alpaca account (paper trading)
- Web browser (Chrome, Safari, Firefox)

---

## Step-by-Step Installation

### 1. Navigate to Project Directory

```bash
cd /Volumes/xcode/MoonDev/moon-dev-ai-agents
```

Or wherever you cloned the repo.

### 2. Install Python Dependencies

**Method 1: Direct Install (Recommended)**
```bash
pip install streamlit plotly pandas python-dotenv alpaca-trade-api --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

**Method 2: Using Requirements File** (if available)
```bash
pip install -r requirements.txt
```

**Method 3: If SSL Errors Persist**
```bash
# Install Python certificates first
/Applications/Python\ 3.13/Install\ Certificates.command

# Then install packages
pip install streamlit plotly pandas python-dotenv alpaca-trade-api
```

### 3. Verify Installation

```bash
python3 -c "import streamlit, plotly, pandas; print('✅ All packages installed successfully!')"
```

If you see the checkmark message, you're good to go!

### 4. Create Environment File (Optional but Recommended)

Create a `.env` file in the project root:

```bash
touch .env
```

Add your Alpaca API credentials:

```env
# Alpaca API Configuration
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Dashboard Settings (Optional)
STARTING_BALANCE=250
MAX_DAILY_LOSS=50
```

**Important:** 
- Never commit `.env` to GitHub
- Start with paper trading (`paper-api.alpaca.markets`)
- Keep your keys secure

---

## Getting Alpaca API Keys

### 1. Create Alpaca Account

1. Go to [alpaca.markets](https://alpaca.markets)
2. Click "Sign Up" (it's free)
3. Complete registration
4. Verify your email

### 2. Access Paper Trading

1. Log into Alpaca dashboard
2. Navigate to "Paper Trading" section
3. This gives you $100,000 virtual money to practice

### 3. Generate API Keys

1. In Paper Trading dashboard, find "API Keys" section
2. Click "Generate New Keys" or "View"
3. You'll see:
   - **API Key ID** (starts with `PK...` for paper)
   - **Secret Key** (long string, shown once)
4. **IMPORTANT:** Copy and save both immediately
5. Paste them into your `.env` file

### 4. Verify Keys Work

```bash
# Test connection (after adding keys to .env)
python3 -c "
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()
api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY'),
    os.getenv('ALPACA_SECRET_KEY'),
    os.getenv('ALPACA_BASE_URL')
)
account = api.get_account()
print(f'✅ Connected! Paper Balance: ${float(account.cash):,.2f}')
"
```

If you see your paper balance, connection successful!

---

## Running the Dashboard

### Basic Run

```bash
streamlit run small_account_dashboard.py
```

### With Virtual Environment (Recommended)

```bash
# Activate environment first
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Then run dashboard
streamlit run small_account_dashboard.py
```

### Expected Output

```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.X.X:8501
```

### Access Dashboard

- **In browser:** Open `http://localhost:8501`
- **Auto-open:** Dashboard usually opens automatically
- **Network access:** Use Network URL to access from phone/tablet

---

## First-Time Configuration

### 1. Check Alpaca Connection

**In Dashboard:**
1. Look at left sidebar
2. Find "🔌 Alpaca Connection" section
3. Should show:
   - "✅ Connected"
   - Paper Balance displayed

**If Connection Failed:**
- Check `.env` file exists in project root
- Verify API keys are correct (no extra spaces)
- Confirm base URL: `https://paper-api.alpaca.markets`
- Restart dashboard (Ctrl+C, then rerun)

### 2. Review Pre-Market Checklist

**In Dashboard:**
1. Go to Tab 1 (🎯 Live Scanner)
2. Find "Pre-Market Checklist" section
3. Familiarize yourself with 8 items
4. This is your daily routine

### 3. Review Your 6 Tickers

**In Dashboard:**
1. Go to Tab 2 (📊 My Tickers)
2. Review: MARA, HOOD, SOFI, BBAI, CAN, COMP
3. Note best strategies for each

### 4. Review Your 20 Strategies

**In Dashboard:**
1. Go to Tab 3 (🎴 Trade Cards)
2. Expand each category
3. Read through strategies
4. Pick 1-3 favorites to start

### 5. Set Up Journal

**In Dashboard:**
1. Go to Tab 5 (📝 Journal)
2. Practice logging a fake trade:
   - Ticker: MARA
   - Strategy: "163. VWAP Reclaim"
   - Side: Call
   - Entry: $0.66
   - Exit: $0.82
   - Result: Green
   - Notes: "Practice trade"
3. Click "💾 Save Trade"
4. Verify it appears in Trade History
5. Test "📥 Export to CSV"

---

## Customization Options

### Change Starting Balance

**In `small_account_dashboard.py`:**

Find this line (around line 52):
```python
if 'account_balance' not in st.session_state:
    st.session_state.account_balance = 250.00
```

Change `250.00` to your desired amount:
```python
st.session_state.account_balance = 500.00  # For $500 account
```

### Change Max Daily Loss

**In `small_account_dashboard.py`:**

Find the risk management box (around line 174):
```python
<p><strong>Max Loss Today:</strong> $50 (20% of account)</p>
```

Update both the displayed amount and percentage:
```python
<p><strong>Max Loss Today:</strong> $100 (20% of account)</p>
```

### Change Tickers

**In `small_account_dashboard.py`:**

Find the tickers list (around line 189):
```python
tickers = [
    {"symbol": "MARA", ...},
    {"symbol": "HOOD", ...},
    # Add/remove tickers here
]
```

Add your preferred tickers with same structure.

### Change Workspace Path (For Resources)

**In `small_account_dashboard.py`:**

Find this line (around line 423):
```python
workspace_path = "/Volumes/xcode/MoonDev/moon-dev-ai-agents"
```

Change to your actual workspace path:
```python
workspace_path = "/path/to/your/workspace"
```

Or use dynamic path:
```python
import os
workspace_path = os.getcwd()  # Uses current directory
```

---

## Troubleshooting Installation

### Issue: "command not found: pip"

**Solution:**
```bash
# Try pip3 instead
pip3 install streamlit plotly pandas

# Or use python3 -m pip
python3 -m pip install streamlit plotly pandas
```

### Issue: "command not found: streamlit"

**Solution:**
```bash
# Make sure it's installed
pip install streamlit

# Run with python3 -m
python3 -m streamlit run small_account_dashboard.py

# Or find where it's installed
which streamlit
# Then use full path
/usr/local/bin/streamlit run small_account_dashboard.py
```

### Issue: "ModuleNotFoundError: No module named 'plotly'"

**Solution:**
```bash
# Install plotly specifically
pip install plotly --trusted-host pypi.org --trusted-host files.pythonhosted.org

# Restart dashboard (Ctrl+C, then rerun)
streamlit run small_account_dashboard.py
```

### Issue: SSL Certificate Errors

**Problem:**
```
SSLError: OSStatus -26276
```

**Solution 1 - Install Certificates:**
```bash
/Applications/Python\ 3.13/Install\ Certificates.command
```

**Solution 2 - Use Trusted Host:**
```bash
pip install [package] --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

**Solution 3 - Upgrade pip:**
```bash
pip install --upgrade pip
```

### Issue: Port 8501 Already in Use

**Problem:**
```
Address already in use
```

**Solution 1 - Kill Existing Process:**
```bash
# Find process using port 8501
lsof -i :8501

# Kill it (replace PID with actual process ID)
kill -9 [PID]

# Or kill all streamlit processes
pkill -f streamlit
```

**Solution 2 - Use Different Port:**
```bash
streamlit run small_account_dashboard.py --server.port 8502
```

### Issue: Dashboard Shows Blank Page

**Solution:**
1. Check terminal for errors
2. Try hard refresh in browser (Cmd+Shift+R or Ctrl+Shift+R)
3. Clear browser cache
4. Try different browser
5. Check firewall settings

### Issue: Permission Denied Errors

**Problem:**
```
PermissionError: [Errno 1] Operation not permitted
```

**Solution:**
```bash
# Use --user flag
pip install --user streamlit plotly pandas

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install streamlit plotly pandas
```

---

## Virtual Environment Setup (Recommended)

### Create Virtual Environment

```bash
# Navigate to project
cd /Volumes/xcode/MoonDev/moon-dev-ai-agents

# Create venv
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install packages
pip install streamlit plotly pandas python-dotenv alpaca-trade-api

# Run dashboard
streamlit run small_account_dashboard.py
```

### Deactivate Virtual Environment

```bash
deactivate
```

### Benefits of Virtual Environment

- Isolated dependencies (no conflicts)
- Clean project structure
- Easy to replicate setup
- Recommended for production use

---

## Updating the Dashboard

### Pull Latest Changes

```bash
# If you cloned from GitHub
git pull origin main

# Check for new dependencies
pip install -r requirements.txt

# Restart dashboard
streamlit run small_account_dashboard.py
```

### Backup Your Data

**Before updating:**

1. Export trades from Journal (Tab 5)
2. Save CSV file
3. Note your current settings
4. Backup `.env` file

**After updating:**

1. Re-import trades if needed
2. Verify settings still correct
3. Test all features

---

## Uninstalling

### Remove Dashboard Files

```bash
# Delete main file
rm small_account_dashboard.py

# Delete guide
rm SMALL_ACCOUNT_DASHBOARD_GUIDE.md

# Delete skills (if installed)
rm -rf .claude/skills/small_account_dashboard
```

### Remove Python Packages

```bash
pip uninstall streamlit plotly pandas python-dotenv alpaca-trade-api
```

### Remove Environment File

```bash
rm .env
```

---

## Production Deployment (Optional)

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub account
4. Select repository
5. Add secrets (API keys) in Streamlit dashboard
6. Deploy!

**Note:** Free tier available, perfect for personal use.

### Deploy to Heroku

1. Create `Procfile`:
```
web: streamlit run small_account_dashboard.py --server.port $PORT
```

2. Create `requirements.txt`:
```
streamlit
plotly
pandas
python-dotenv
alpaca-trade-api
```

3. Deploy to Heroku:
```bash
heroku create your-app-name
git push heroku main
heroku config:set ALPACA_API_KEY=your_key
heroku config:set ALPACA_SECRET_KEY=your_secret
```

---

## Next Steps After Installation

1. ✅ **Run the dashboard** - Make sure it loads
2. ✅ **Check Alpaca connection** - Verify API keys work
3. ✅ **Review the 20 strategies** - Pick your favorites (Tab 3)
4. ✅ **Practice logging trades** - Use Journal tab (Tab 5)
5. ✅ **Read the full guide** - `SMALL_ACCOUNT_DASHBOARD_GUIDE.md`
6. ✅ **Paper trade for 10 days** - Complete the challenge
7. ✅ **Go live only after success** - Prove discipline first

---

## Support & Resources

### Documentation
- **Full Guide:** `SMALL_ACCOUNT_DASHBOARD_GUIDE.md`
- **Strategies:** Available in dashboard Tab 3
- **Alpaca Docs:** [alpaca.markets/docs](https://alpaca.markets/docs)
- **Streamlit Docs:** [docs.streamlit.io](https://docs.streamlit.io)

### Community
- GitHub Issues (if available)
- Discord (if available)
- Twitter (if available)

### Getting Help

**If you encounter issues:**

1. Check this setup guide first
2. Review troubleshooting section
3. Check terminal output for error messages
4. Search Streamlit docs for specific errors
5. Ask for help (provide error messages)

---

## Security Best Practices

### API Keys
- ✅ Always use `.env` file (never hardcode keys)
- ✅ Add `.env` to `.gitignore`
- ✅ Never commit keys to GitHub
- ✅ Use paper trading keys first
- ✅ Rotate keys regularly

### Data
- ✅ Export journal data regularly
- ✅ Backup `.env` file securely
- ✅ Don't share API keys with anyone
- ✅ Monitor account activity on Alpaca

### Updates
- ✅ Keep packages updated
- ✅ Review code changes before pulling
- ✅ Test on paper account first
- ✅ Backup before major updates

---

**Installation complete! You're ready to start trading with discipline.** 🚀

Remember: The dashboard is a tool. Your discipline makes it work. Complete the 10-day challenge!

