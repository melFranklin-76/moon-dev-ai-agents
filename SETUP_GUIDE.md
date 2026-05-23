# 🔧 Setup Guide — Full Configuration

Everything beyond `pip install` and `streamlit run`.

---

## 1. Environment Variables

Create a `.env` file in the project root (copy from the template below).
This file is gitignored — it never gets pushed to GitHub.

```bash
# .env — create this file, don't commit it

# Google Sheets (optional — for trade journal backup)
GOOGLE_SHEETS_CREDS_JSON=your_service_account_json_here
GOOGLE_SHEET_ID=your_sheet_id_here
```

If you skip Google Sheets, the journal saves to a local CSV instead (`src/data/small_account/trades.csv`). Either works fine.

---

## 2. Google Sheets Backup (Optional)

Lets your trade journal sync to a Google Sheet so it's accessible anywhere and backed up forever.

**Step 1 — Create a service account:**
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. New project → Enable Google Sheets API + Google Drive API
3. IAM & Admin → Service Accounts → Create
4. Download the JSON key file

**Step 2 — Create your Sheet:**
1. Create a new Google Sheet
2. Share it with your service account email (Editor access)
3. Copy the Sheet ID from the URL: `docs.google.com/spreadsheets/d/THIS_PART/edit`

**Step 3 — Add to .env:**
```
GOOGLE_SHEETS_CREDS_JSON={"type":"service_account","project_id":"..."}
GOOGLE_SHEET_ID=1abc123...
```

The sheet will auto-create two tabs: `Trades` and `Tendencies`.

---

## 3. Streamlit Cloud Deployment (Free)

Run your dashboard 24/7 in the cloud so you can access it from any device.

**Step 1:** Push your code to GitHub (already set up).

**Step 2:** Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.

**Step 3:** New app → select your repo → branch: `main` → main file: `small_account_dashboard.py` → Deploy.

**Step 4:** Add your environment variables:
- Settings → Secrets → paste your `.env` contents in TOML format:
```toml
GOOGLE_SHEETS_CREDS_JSON = "..."
GOOGLE_SHEET_ID = "..."
```

**That's it.** Every `git push origin main` auto-redeploys the app. Your Streamlit Cloud URL is your dashboard URL — bookmark it, add to iPhone home screen.

---

## 4. iPhone Setup

1. Open your Streamlit Cloud URL in **Safari**
2. Tap the **Share** button (box with arrow)
3. Tap **Add to Home Screen**
4. Name it: `$250 Scalper`
5. Tap **Add**

Opens full-screen with no browser bar. Works in Simple Mode (designed for phone screens).

---

## 5. Push Notifications (ntfy.sh)

Get alerts on your iPhone when scanner signals fire or price targets hit.

**On your iPhone:**
1. Download the **ntfy** app (free, App Store)
2. Tap + to add a subscription
3. Enter your topic name (you choose this — make it unique, e.g. `scalper_mel_2025`)

**In the dashboard:**
1. Sidebar → 📲 Push Notifications
2. Enter the same topic name → Save
3. Tap "Test Notification" to confirm it works

You'll now get a push notification for:
- Scanner signals (VWAP reclaim, whole-dollar break, BTC sync)
- Price alerts (when a ticker hits your target)
- Hot sector alerts (when a sector is running hard)

ntfy is completely free. No account needed. No subscription. The topic name acts as your "channel."

---

## 6. Price Alerts

Set up while you're away from the screen.

1. Sidebar → 🔔 Price Alerts
2. Enter: Ticker, Target price, Direction (above/below)
3. Add Alert

Checks on every page refresh (auto-refresh every 60s). Fires on-screen toast + ntfy push to your phone.

Example:
- ONDS ▲ $11.50 → buy alert if it breaks out
- ONDS ▼ $9.00 → stop alert if it breaks down

---

## 7. GitHub Workflow

```bash
# Pull latest before starting work
git pull origin main

# After making changes
git add -A
git commit -m "describe your change"
git push origin main
```

Your repo: `github.com/melFranklin-76/moon-dev-ai-agents`

---

## 8. Data Files (Auto-Created)

| File | Contents |
|------|---------|
| `src/data/small_account/trades.csv` | Trade journal (local backup) |
| `src/data/small_account/alerts.csv` | Active price alerts |
| `src/data/small_account/tendencies.csv` | Coach tab entries |

These are created automatically the first time you use each feature. Back them up occasionally by downloading from the Journal tab's "Export to CSV" button.

---

## 9. Auto-Refresh

Dashboard refreshes every 60 seconds by default — keeps prices and alerts current.

Toggle in sidebar → 🔄 Auto-Refresh → on/off.

Turn it off if you're on a slow connection or want to save bandwidth.

---

## 10. Watchlist

The watchlist resets every browser session (by design — fresh tickers each day).

**Pre-market routine:**
1. Run your Finviz/TradingView scanner (3%+ gain, 2x+ volume, catalyst)
2. Add qualifying tickers in Sidebar → 📋 Today's Watchlist
3. Dashboard loads live data for each ticker automatically

No more than 6 tickers at once — keeps the cards readable and your focus tight.
