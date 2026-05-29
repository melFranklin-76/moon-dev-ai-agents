import SwiftUI
import WebKit

struct WebView: UIViewRepresentable {

    let url: URL
    @Binding var isLoading: Bool
    @Binding var hasError: Bool

    // Optional feature flag: block WebP images via a content rule list.
    // Leave as false by default; set to true if you want to test whether
    // the page provides non-WebP fallbacks.
    var blockWebP: Bool = false

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    func makeUIView(context: Context) -> WKWebView {
        // ── Configuration ─────────────────────────────────────────────────────
        let config = WKWebViewConfiguration()
        config.websiteDataStore           = .default()          // persist cookies/session
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
        refresh.tintColor = UIColor(red: 0.18, green: 0.80, blue: 0.44, alpha: 1) // #2ecc71
        refresh.addTarget(context.coordinator,
                          action: #selector(Coordinator.handleRefresh(_:)),
                          for: .valueChanged)
        webView.scrollView.refreshControl = refresh

        context.coordinator.webView = webView

        // ── Optional: block WebP images using a content rule list ─────────────
        if blockWebP {
            let rules = """
            [
              {
                "trigger": {
                  "url-filter": ".*\\\.webp($|\\?)",
                  "resource-type": ["image"]
                },
                "action": { "type": "block" }
              }
            ]
            """
            WKContentRuleListStore.default().compileContentRuleList(
                forIdentifier: "BlockWebP",
                encodedContentRuleList: rules
            ) { ruleList, error in
                #if DEBUG
                if let error = error { print("[WebView][Rules] compile error:", error) }
                #endif
                if let ruleList = ruleList {
                    webView.configuration.userContentController.add(ruleList)
                }
                webView.load(URLRequest(url: url))
            }
        } else {
            // Standard load
            webView.load(URLRequest(url: url))
        }

        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {}

    // ── Coordinator ───────────────────────────────────────────────────────────
    class Coordinator: NSObject, WKNavigationDelegate {
        var parent: WebView
        weak var webView: WKWebView?

        init(_ parent: WebView) { self.parent = parent }

        // Start loading
        func webView(_ webView: WKWebView,
                     didStartProvisionalNavigation navigation: WKNavigation!) {
            parent.isLoading = true
            parent.hasError  = false
            #if DEBUG
            if let u = webView.url { print("[WebView] didStart:", u.absoluteString) }
            #endif
        }

        // Finished loading
        func webView(_ webView: WKWebView,
                     didFinish navigation: WKNavigation!) {
            parent.isLoading = false
            webView.scrollView.refreshControl?.endRefreshing()
            #if DEBUG
            if let u = webView.url { print("[WebView] didFinish:", u.absoluteString) }
            #endif
        }

        // Handle errors
        func webView(_ webView: WKWebView,
                     didFail navigation: WKNavigation!,
                     withError error: Error) {
            parent.isLoading = false
            parent.hasError  = true
            webView.scrollView.refreshControl?.endRefreshing()
            log(error: error)
        }

        func webView(_ webView: WKWebView,
                     didFailProvisionalNavigation navigation: WKNavigation!,
                     withError error: Error) {
            parent.isLoading = false
            parent.hasError  = true
            webView.scrollView.refreshControl?.endRefreshing()
            log(error: error)
        }

        // Redirects
        func webView(_ webView: WKWebView,
                     didReceive serverRedirectForProvisionalNavigation navigation: WKNavigation!) {
            #if DEBUG
            print("[WebView] redirect")
            #endif
        }

        // Decide policy for actions (external schemes, target=_blank)
        func webView(_ webView: WKWebView,
                     decidePolicyFor navigationAction: WKNavigationAction,
                     decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            #if DEBUG
            if let url = navigationAction.request.url {
                print("[WebView] action:", url.absoluteString)
            }
            #endif

            if let url = navigationAction.request.url,
               let scheme = url.scheme?.lowercased(),
               ["tel", "mailto", "sms", "facetime", "facetime-audio", "maps", "itms-apps"].contains(scheme) {
                UIApplication.shared.open(url, options: [:], completionHandler: nil)
                decisionHandler(.cancel)
                return
            }

            // Open target=_blank links in the same view by allowing; Safari-style behavior can be added if needed.
            decisionHandler(.allow)
        }

        // Response info (status code, MIME type)
        func webView(_ webView: WKWebView,
                     decidePolicyFor navigationResponse: WKNavigationResponse,
                     decisionHandler: @escaping (WKNavigationResponsePolicy) -> Void) {
            #if DEBUG
            let response = navigationResponse.response
            let mime = response.mimeType ?? "nil"
            if let http = response as? HTTPURLResponse {
                print("[WebView] response:", http.statusCode, mime, navigationResponse.isForMainFrame ? "main" : "sub")
            } else {
                print("[WebView] response (non-HTTP):", mime, navigationResponse.isForMainFrame ? "main" : "sub")
            }
            #endif
            decisionHandler(.allow)
        }

        // Recover from WebContent process crashes
        func webViewWebContentProcessDidTerminate(_ webView: WKWebView) {
            #if DEBUG
            print("[WebView] WebContent process terminated — reloading…")
            #endif
            webView.reload()
        }

        @objc func handleRefresh(_ sender: UIRefreshControl) {
            parent.hasError = false
            webView?.reload()
        }

        private func log(error: Error) {
            #if DEBUG
            let ns = error as NSError
            let failing = ns.userInfo[NSURLErrorFailingURLStringErrorKey] as? String
            print("[WebView][Error]", ns.domain, ns.code, error.localizedDescription, "failing:", failing ?? "nil")
            #endif
        }
    }
}
