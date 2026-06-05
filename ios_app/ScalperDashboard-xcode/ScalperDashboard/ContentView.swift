import SwiftUI

private let kDashboardURL = "https://2dvgakbpkgannfjzhfcej9.streamlit.app"

struct ContentView: View {
    @Binding var reloadTickExternal: Int

    @State private var isLoading = true
    @State private var hasError  = false
    @State private var errorMessage: String?
    @State private var reloadTickInternal = 0

    private var combinedReloadTick: Int { reloadTickExternal ^ reloadTickInternal }

    private var currentURL: URL {
        var components = URLComponents(string: kDashboardURL)!
        var items = components.queryItems ?? []
        items.append(URLQueryItem(name: "_r", value: String(combinedReloadTick)))
        components.queryItems = items
        return components.url!
    }

    init(reloadTickExternal: Binding<Int>) {
        self._reloadTickExternal = reloadTickExternal
    }

    var body: some View {
        ZStack {
            Color(red: 0.055, green: 0.067, blue: 0.090)
                .ignoresSafeArea()

            WebView(url: currentURL, isLoading: $isLoading, hasError: $hasError, errorMessage: $errorMessage)
                .ignoresSafeArea()

            if isLoading {
                ProgressView()
                    .tint(.green)
                    .scaleEffect(2)
                    .transition(.opacity)
            }

            if hasError {
                VStack(spacing: 12) {
                    Text("Something went wrong")
                        .font(.headline)
                        .foregroundStyle(.white)
                    Text(errorMessage ?? "Please check your connection and try again.")
                        .font(.subheadline)
                        .foregroundStyle(.white.opacity(0.7))
                    HStack(spacing: 12) {
                        Button {
                            // Force a reload by bumping the internal token
                            reloadTickInternal &+= 1
                            isLoading = true
                            hasError = false
                        } label: {
                            Text("Retry")
                                .bold()
                                .padding(.horizontal, 16)
                                .padding(.vertical, 10)
                                .background(.green)
                                .foregroundStyle(.black)
                                .clipShape(Capsule())
                        }

                        Button {
                            if let url = URL(string: kDashboardURL) {
                                UIApplication.shared.open(url)
                            }
                        } label: {
                            Text("Open in Safari")
                                .bold()
                                .padding(.horizontal, 16)
                                .padding(.vertical, 10)
                                .background(.white.opacity(0.15))
                                .foregroundStyle(.white)
                                .clipShape(Capsule())
                        }
                    }
                }
                .padding(20)
                .background(.black.opacity(0.5))
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                .overlay(
                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                        .stroke(.white.opacity(0.15), lineWidth: 1)
                )
                .padding()
                .transition(.opacity)
            }
        }
        .preferredColorScheme(.dark)
    }
}

// Convenience for previews
#Preview {
    ContentView(reloadTickExternal: .constant(0))
}
