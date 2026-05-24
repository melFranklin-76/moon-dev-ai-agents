import SwiftUI

// ── Replace this with your Streamlit Cloud URL ────────────────────────────────
private let kDashboardURL = "https://2dvgakbpkgannfjzhfcej9.streamlit.app"

struct ContentView: View {

    @State private var isLoading = true
    @State private var hasError  = false

    private let url = URL(string: kDashboardURL)!

    var body: some View {
        ZStack {
            // ── Background colour matches Streamlit dark theme ─────────────
            Color(red: 0.055, green: 0.067, blue: 0.090)
                .ignoresSafeArea()

            // ── Dashboard ──────────────────────────────────────────────────
            if !hasError {
                WebView(url: url, isLoading: $isLoading, hasError: $hasError)
                    .ignoresSafeArea()
            }

            // ── Offline / error screen ─────────────────────────────────────
            if hasError {
                OfflineView {
                    hasError  = false
                    isLoading = true
                }
            }

            // ── Splash / loading screen ────────────────────────────────────
            if isLoading && !hasError {
                SplashView()
                    .transition(.opacity)
            }
        }
        .animation(.easeInOut(duration: 0.3), value: isLoading)
        .animation(.easeInOut(duration: 0.3), value: hasError)
        .preferredColorScheme(.dark)
    }
}

// ── Splash screen ──────────────────────────────────────────────────────────────
struct SplashView: View {
    @State private var pulse = false

    var body: some View {
        ZStack {
            Color(red: 0.055, green: 0.067, blue: 0.090)
                .ignoresSafeArea()

            VStack(spacing: 20) {
                Text("🌙")
                    .font(.system(size: 72))
                    .scaleEffect(pulse ? 1.08 : 1.0)
                    .animation(.easeInOut(duration: 1.1).repeatForever(autoreverses: true),
                               value: pulse)

                Text("$250 Scalper")
                    .font(.system(size: 28, weight: .bold, design: .rounded))
                    .foregroundColor(.white)

                Text("Options Dashboard")
                    .font(.system(size: 15, weight: .medium))
                    .foregroundColor(Color(white: 0.55))

                Spacer().frame(height: 12)

                ProgressView()
                    .tint(Color(red: 0.18, green: 0.80, blue: 0.44))
                    .scaleEffect(1.2)
            }
        }
        .onAppear { pulse = true }
    }
}

// ── Offline screen ─────────────────────────────────────────────────────────────
struct OfflineView: View {
    let onRetry: () -> Void

    var body: some View {
        ZStack {
            Color(red: 0.055, green: 0.067, blue: 0.090)
                .ignoresSafeArea()

            VStack(spacing: 24) {
                Text("📡")
                    .font(.system(size: 60))

                Text("No Connection")
                    .font(.system(size: 22, weight: .bold))
                    .foregroundColor(.white)

                Text("Check your Wi-Fi or cellular signal,\nthen try again.")
                    .font(.system(size: 15))
                    .foregroundColor(Color(white: 0.55))
                    .multilineTextAlignment(.center)

                Button(action: onRetry) {
                    Label("Retry", systemImage: "arrow.clockwise")
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(.black)
                        .frame(width: 160, height: 48)
                        .background(Color(red: 0.18, green: 0.80, blue: 0.44))
                        .cornerRadius(12)
                }
            }
            .padding(32)
        }
    }
}

#Preview {
    ContentView()
}
