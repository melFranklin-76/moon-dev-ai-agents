import SwiftUI
import WebKit
import UIKit

struct WebView: UIViewRepresentable {
    let url: URL
    @Binding var isLoading: Bool
    @Binding var hasError: Bool
    @Binding var errorMessage: String?

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.websiteDataStore = .default()
        config.defaultWebpagePreferences.allowsContentJavaScript = true

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        webView.uiDelegate = context.coordinator
        webView.isOpaque = false
        webView.backgroundColor = .clear
        webView.scrollView.backgroundColor = .clear
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.allowsBackForwardNavigationGestures = false

        #if DEBUG
        if #available(iOS 16.4, *) {
            webView.isInspectable = true
        }
        #endif

        // Pull-to-refresh setup
        webView.scrollView.alwaysBounceVertical = true
        let refresh = UIRefreshControl()
        refresh.addTarget(context.coordinator, action: #selector(Coordinator.handleRefresh(_:)), for: .valueChanged)
        webView.scrollView.refreshControl = refresh

        context.coordinator.startObserving(webView)

        // Restore cookies before the initial load to preserve sessions across launches
        CookieStore.shared.restoreCookies(into: webView.configuration.websiteDataStore.httpCookieStore) {
            if self.url.isFileURL {
                webView.loadFileURL(self.url, allowingReadAccessTo: self.url.deletingLastPathComponent())
            } else {
                let request = URLRequest(url: self.url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 30)
                webView.load(request)
            }
        }

        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {
        // Reload if the bound URL changes (e.g., cache-busting token)
        if webView.url != url {
            if url.isFileURL {
                webView.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
            } else {
                let request = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 30)
                webView.load(request)
            }
        }
    }

    static func dismantleUIView(_ webView: WKWebView, coordinator: Coordinator) {
        coordinator.stopObserving()
        webView.navigationDelegate = nil
        webView.uiDelegate = nil
        webView.stopLoading()
        webView.scrollView.refreshControl?.removeTarget(coordinator, action: #selector(Coordinator.handleRefresh(_:)), for: .valueChanged)
        webView.scrollView.refreshControl = nil
    }

    class Coordinator: NSObject, WKNavigationDelegate, WKUIDelegate {
        var parent: WebView
        private var progressObservation: NSKeyValueObservation?
        weak var webView: WKWebView?

        init(_ parent: WebView) { self.parent = parent }

        func startObserving(_ webView: WKWebView) {
            self.webView = webView
            progressObservation = webView.observe(\.estimatedProgress, options: [.new]) { [weak self] _, change in
                guard let self else { return }
                DispatchQueue.main.async {
                    let progress = change.newValue ?? 1.0
                    self.parent.isLoading = progress < 1.0
                }
            }
        }

        func stopObserving() {
            progressObservation?.invalidate()
            progressObservation = nil
            webView = nil
        }

        deinit {
            stopObserving()
        }

        @objc func handleRefresh(_ sender: UIRefreshControl) {
            if let webView = webView {
                if webView.url != nil {
                    webView.reload()
                } else {
                    if parent.url.isFileURL {
                        webView.loadFileURL(parent.url, allowingReadAccessTo: parent.url.deletingLastPathComponent())
                    } else {
                        let request = URLRequest(url: parent.url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 30)
                        webView.load(request)
                    }
                }
            }
        }

        // MARK: - WKNavigationDelegate

        func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!) {
            parent.isLoading = true
            parent.hasError = false
            parent.errorMessage = nil
        }

        func webView(_ webView: WKWebView, didCommit navigation: WKNavigation!) {
            parent.isLoading = true
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            parent.isLoading = false
            parent.hasError = false
            parent.errorMessage = nil
            webView.scrollView.refreshControl?.endRefreshing()
        }

        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            parent.isLoading = false
            parent.hasError = true
            parent.errorMessage = self.friendlyMessage(for: error, url: webView.url)
            webView.scrollView.refreshControl?.endRefreshing()
            print("[WebView] didFail:", error.localizedDescription)
        }

        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            parent.isLoading = false
            parent.hasError = true
            parent.errorMessage = self.friendlyMessage(for: error, url: webView.url)
            webView.scrollView.refreshControl?.endRefreshing()
            print("[WebView] didFailProvisional:", error.localizedDescription)
        }

        func webViewWebContentProcessDidTerminate(_ webView: WKWebView) {
            // Attempt to recover from process termination
            print("[WebView] Web content process terminated; reloading.")
            webView.reload()
        }

        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            if let url = navigationAction.request.url,
               let scheme = url.scheme?.lowercased(),
               scheme != "http", scheme != "https", scheme != "file" {
                UIApplication.shared.open(url, options: [:], completionHandler: nil)
                decisionHandler(.cancel)
                return
            }
            decisionHandler(.allow)
        }

        // MARK: - WKUIDelegate

        // Handle target="_blank" by opening in the same webView
        func webView(_ webView: WKWebView, createWebViewWith configuration: WKWebViewConfiguration, for navigationAction: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? {
            if navigationAction.targetFrame == nil, let url = navigationAction.request.url {
                webView.load(URLRequest(url: url))
            }
            return nil
        }

        // MARK: - Error messaging
        private func friendlyMessage(for error: Error, url: URL?) -> String {
            let nsError = error as NSError
            if nsError.domain == NSURLErrorDomain, let urlError = URLError.Code(rawValue: nsError.code) {
                switch urlError {
                case .notConnectedToInternet:
                    return "No internet connection. Please check your network and try again."
                case .timedOut:
                    return "The request timed out. Please try again."
                case .cannotFindHost, .cannotConnectToHost:
                    return "Cannot reach the server. Please try again later."
                case .networkConnectionLost:
                    return "Network connection was lost. Please retry."
                case .secureConnectionFailed:
                    return "Secure connection failed. Please try again."
                case .appTransportSecurityRequiresSecureConnection:
                    return "This content requires HTTPS."
                default:
                    break
                }
            }
            if nsError.domain == WKError.errorDomain, let wkCode = WKError.Code(rawValue: nsError.code) {
                switch wkCode {
                case .webContentProcessTerminated:
                    return "The page was reloaded due to a crash."
                case .webViewInvalidated:
                    return "The web view was invalidated. Please try again."
                case .frameLoadInterruptedByPolicyChange:
                    return "Navigation was interrupted by a policy change."
                default:
                    break
                }
            }
            if let failingURL = url { return "Failed to load: \(failingURL.absoluteString)\n\(error.localizedDescription)" }
            return error.localizedDescription
        }
    }
}
