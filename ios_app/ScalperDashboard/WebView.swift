import SwiftUI
import WebKit

struct WebView: UIViewRepresentable {
    let url: URL
    let reloadID: UUID

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    func makeUIView(context: Context) -> WKWebView {
        let webView = WKWebView()
        webView.navigationDelegate = context.coordinator
        webView.allowsBackForwardNavigationGestures = true

        let refresh = UIRefreshControl()
        refresh.addTarget(context.coordinator,
                          action: #selector(Coordinator.handleRefresh(_:)),
                          for: .valueChanged)
        webView.scrollView.refreshControl = refresh

        context.coordinator.webView = webView
        webView.load(URLRequest(url: url))
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {
        if context.coordinator.lastReloadID != reloadID {
            context.coordinator.lastReloadID = reloadID
            webView.load(URLRequest(url: url))
        }
    }

    // MARK: - Coordinator

    class Coordinator: NSObject, WKNavigationDelegate {
        weak var webView: WKWebView?
        var lastReloadID = UUID()

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            webView.scrollView.refreshControl?.endRefreshing()
        }

        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            webView.scrollView.refreshControl?.endRefreshing()
            loadErrorPage(in: webView, error: error)
        }

        func webView(_ webView: WKWebView,
                     didFailProvisionalNavigation navigation: WKNavigation!,
                     withError error: Error) {
            webView.scrollView.refreshControl?.endRefreshing()
            loadErrorPage(in: webView, error: error)
        }

        @objc func handleRefresh(_ sender: UIRefreshControl) {
            webView?.reload()
        }

        private func loadErrorPage(in webView: WKWebView, error: Error) {
            let html = """
            <html><body style="background:#0e1117;color:#e74c3c;font-family:sans-serif;
                               padding:40px;text-align:center;">
              <h2>Cannot reach dashboard</h2>
              <p style="color:#8b92a8;">\(error.localizedDescription)</p>
              <p style="color:#f39c12;margin-top:32px;">
                Make sure Streamlit is running on your Mac:<br><br>
                <code style="color:#2ecc71;">
                  streamlit run small_account_dashboard.py --server.address=0.0.0.0
                </code>
              </p>
              <p style="color:#8b92a8;font-size:13px;margin-top:24px;">
                Then tap ↺ to retry
              </p>
            </body></html>
            """
            webView.loadHTMLString(html, baseURL: nil)
        }
    }
}
