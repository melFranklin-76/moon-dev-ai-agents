# 📱 iPhone App Setup — Xcode Guide

Builds a native iOS shell around your Streamlit dashboard.  
Full-screen, custom icon, pull-to-refresh, offline screen.  
Installed directly to your phone via your paid Apple Developer account.

---

## What You Need

- Mac with **Xcode 15+** (free from App Store)
- iPhone plugged in via USB
- Paid Apple Developer account ($99/year) — you already have this

---

## Step 1 — Create the Xcode Project

1. Open **Xcode** → **Create New Project**
2. Choose **iOS** → **App** → Next
3. Fill in:
   - **Product Name:** `ScalperDashboard`
   - **Team:** select your paid Apple Developer team
   - **Bundle Identifier:** `com.yourname.scalper` (anything unique)
   - **Interface:** SwiftUI
   - **Language:** Swift
4. Save it anywhere on your Mac

---

## Step 2 — Replace the Generated Swift Files

Xcode creates `ContentView.swift` and `ScalperDashboardApp.swift` for you.  
Delete their contents and paste in ours. Also add `WebView.swift`.

In the **Project Navigator** (left panel):

1. Click `ContentView.swift` → Select All (⌘A) → Delete → paste contents of `ios_app/ScalperDashboard/ContentView.swift`
2. Click `ScalperDashboardApp.swift` → Select All → Delete → paste contents of `ios_app/ScalperDashboard/ScalperDashboardApp.swift`
3. Right-click the yellow project folder → **Add Files to "ScalperDashboard"** → select `ios_app/ScalperDashboard/WebView.swift`

---

## Step 3 — Set Minimum iOS Version

1. Click your **project name** at the top of the navigator (the blue icon)
2. Select your **Target** → **General** tab
3. Set **Minimum Deployments** to **iOS 16.0**

---

## Step 4 — Add the App Icon

1. In the navigator click `Assets.xcassets` → click `AppIcon`
2. Drag `ios_app/AppIcon-1024.png` into the **1024×1024** slot on the right
3. Xcode fills in all the other sizes automatically

---

## Step 5 — Build and Run

1. Plug in your iPhone via USB
2. In Xcode, click the device picker at the top (where it says "iPhone" or a simulator name)
3. Select your physical iPhone from the list
4. Hit **▶ Play** (or ⌘R)
5. First build takes about 60 seconds — app appears on your home screen as **ScalperDashboard**

---

## What the App Does

| Feature | Detail |
|---------|--------|
| Full-screen dashboard | No browser bar, no Safari UI |
| Dark splash screen | 🌙 logo + spinner while dashboard loads |
| Pull to refresh | Swipe down to reload the page |
| Offline screen | "No Connection" + Retry button if network drops |
| Session persistence | Stays logged in, remembers your watchlist |
| Dark mode | Locked to dark — matches Streamlit theme |

---

## Changing the Dashboard URL

If you ever update your Streamlit URL:

1. Open `ContentView.swift` in Xcode
2. Change line 4: `private let kDashboardURL = "your-new-url"`
3. Hit ⌘R to rebuild and reinstall

---

## Troubleshooting

**Build fails with signing error:**  
Xcode → Settings → Accounts → select your Apple ID → Download Manual Profiles

**Dashboard shows blank white screen:**  
The Streamlit app may be sleeping (free tier hibernates after inactivity).  
Pull down to refresh and wait 30 seconds for it to wake up.

**App crashes on launch:**  
Make sure the URL in `ContentView.swift` line 4 starts with `https://`

**Can't see your iPhone in the device picker:**  
Unplug and replug the USB cable. Trust the computer on your iPhone if prompted.
