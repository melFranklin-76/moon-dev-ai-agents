import SwiftUI
import WebKit

struct WebView: UIViewRepresentable {

    let url: URL
    @Binding var isLoading: Bool
    @Binding var hasError: Bool

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    func makeUIView(context: Context) -> WKWebView {
        // ── Configuration ─────────────────────────────────────────────────────
        let config = WKWebViewConfiguration()
        config.websiteDataStore           = .default()
        config.allowsInlineMediaPlayback  = true

        let prefs = WKWebpagePreferences()
        prefs.allowsContentJavaScript     = true
        config.defaultWebpagePreferences  = prefs

        // ── WebView ───────────────────────────────────────────────────────────
        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate        = context.coordinator
        webView.allowsBackForwardNavigationGestures = false
        webView.scrollView.showsVerticalScrollIndicator   = false
        webView.scrollView.showsHorizontalScrollIndicator = false
        webView.scrollView.bounces        = true
        webView.backgroundColor           = UIColor(red: 0.055, green: 0.067,
                                                     blue: 0.090, alpha: 1)
        webView.isOpaque                  = false

        // ── Pull-to-refresh ───────────────────────────────────────────────────
        let refresh = UIRefreshControl()
        refresh.tintColor = UIColor(red: 0.18, green: 0.80, blue: 0.44, alpha: 1)
        refresh.addTarget(context.coordinator,
                          action: #selector(Coordinator.handleRefresh(_:)),
                          for: .valueChanged)
        webView.scrollView.refreshControl = refresh

        context.coordinator.webView = webView
        webView.load(URLRequest(url: url))
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {}

    // ── Coordinator ───────────────────────────────────────────────────────────
    class Coordinator: NSObject, WKNavigationDelegate {
        var parent: WebView
        weak var webView: WKWebView?

        init(_ parent: WebView) { self.parent = parent }

        func webView(_ webView: WKWebView,
                     didStartProvisionalNavigation _: WKNavigation!) {
            parent.isLoading = true
            parent.hasError  = false
        }

        func webView(_ webView: WKWebView,
                     didFinish _: WKNavigation!) {
            parent.isLoading = false
            webView.scrollView.refreshControl?.endRefreshing()
        }

        func webView(_ webView: WKWebView,
                     didFail _: WKNavigation!,
                     withError error: Error) {
            parent.isLoading = false
            parent.hasError  = true
            webView.scrollView.refreshControl?.endRefreshing()
        }

        func webView(_ webView: WKWebView,
                     didFailProvisionalNavigation _: WKNavigation!,
                     withError error: Error) {
            parent.isLoading = false
            parent.hasError  = true
            webView.scrollView.refreshControl?.endRefreshing()
        }

        @objc func handleRefresh(_ sender: UIRefreshControl) {
            parent.hasError = false
            webView?.reload()
        }
    }
}
