# 📱 iPhone App Setup — Xcode Guide

Builds a native iOS shell around your Streamlit dashboard.
Full-screen, custom icon, pull-to-refresh, offline screen. 
Sideloaded directly to your phone — no App Store needed.

---

## What You Need

- Mac with **Xcode 15+** (free from App Store)
- iPhone plugged in via USB
- Free Apple ID (no paid developer account needed for personal use)

---

## Step 1 — Create the Xcode Project

1. Open **Xcode** → **Create New Project**
2. Choose **iOS** → **App** → Next
3. Fill in:
   - **Product Name:** `ScalperDashboard`
   - **Team:** your Apple ID (add it in Xcode → Settings → Accounts if needed)
   - **Bundle Identifier:** `com.yourname.scalper` (anything unique)
   - **Interface:** SwiftUI
   - **Language:** Swift
4. Save it anywhere on your Mac (Desktop is fine)

---

## Step 2 — Replace the Generated Files

Xcode creates `ContentView.swift` and `ScalperDashboardApp.swift` for you.
Replace them with the files from this folder, and add `WebView.swift`.

In the **Project Navigator** (left panel):

1. Click `ContentView.swift` → select all → delete → paste in our `ContentView.swift`
2. Click `ScalperDashboardApp.swift` → select all → delete → paste in our `ScalperDashboardApp.swift`
3. Right-click the folder → **Add Files** → select `WebView.swift`

---

## Step 3 — Set Minimum iOS Version

1. Click your project name at the top of the navigator
2. Select your **Target** → **General**
3. Set **Minimum Deployments** to **iOS 16.0**

---

## Step 4 — Add App Icon

1. In the navigator, click `Assets.xcassets` → `AppIcon`
2. Drag a **1024×1024 PNG** image into the slot
3. Use any image — a green moon emoji screenshot works perfectly

   Quick way: screenshot the 🌙 emoji on your Mac at large size,
   or use any free icon generator (appicon.co → upload → download)

---

## Step 5 — Trust Your Developer Certificate on iPhone

First time only:

1. On iPhone: **Settings → General → VPN & Device Management**
2. Find your Apple ID → tap **Trust**

---

## Step 6 — Build and Run

1. Plug in your iPhone via USB
2. In Xcode, select your iPhone from the device picker (top bar)
3. Hit the **▶ Play** button (or ⌘R)
4. Xcode builds and installs — takes about 60 seconds first time
5. App appears on your home screen as **ScalperDashboard**

---

## What the App Does

| Feature | Detail |
|---------|--------|
| Full-screen dashboard | No browser bar, no Safari UI |
| Dark splash screen | 🌙 logo + loading spinner while dashboard loads |
| Pull to refresh | Swipe down to reload the page |
| Offline screen | "No Connection" + Retry button if network drops |
| Session persistence | Stays logged in, remembers your watchlist |
| Dark mode | Locked to dark — matches Streamlit theme |

---

## Updating the App

If you change the Streamlit URL in the future:

1. Open `ContentView.swift`
2. Change line 4: `private let kDashboardURL = "your-new-url"`
3. ⌘R to rebuild and reinstall

---

## Re-installing After 7 Days

Free Apple IDs expire sideloaded apps every 7 days.
Just plug in and hit ▶ again — takes 30 seconds to reinstall.

If you want apps that don't expire, get a paid Apple Developer account ($99/year).
For personal use, the 7-day cycle is fine — just keep Xcode handy.

---

## Troubleshooting

**"Untrusted Developer" on iPhone:**
Settings → General → VPN & Device Management → Trust your Apple ID

**Build fails with signing error:**
Xcode → Preferences → Accounts → add your Apple ID → click "Download Manual Profiles"

**Dashboard shows blank white screen:**
The Streamlit app might be sleeping (Streamlit Cloud free tier hibernates).
Pull down to refresh and wait 30 seconds for it to wake up.

**App crashes on launch:**
Make sure the URL in `ContentView.swift` line 4 starts with `https://`
