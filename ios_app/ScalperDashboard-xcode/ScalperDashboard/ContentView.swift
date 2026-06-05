import SwiftUI

private let kDashboardURL = "https://2dvgakbpkgannfjzhfcej9.streamlit.app"

struct ContentView: View {
    @State private var isLoading = true
    @State private var hasError  = false

    private let url = URL(string: kDashboardURL)!

    var body: some View {
        ZStack {
            Color(red: 0.055, green: 0.067, blue: 0.090)
                .ignoresSafeArea()

            WebView(url: url, isLoading: $isLoading, hasError: $hasError)
                .ignoresSafeArea()

            if isLoading {
                ProgressView()
                    .tint(.green)
                    .scaleEffect(2)
            }
        }
        .preferredColorScheme(.dark)
    }
}
