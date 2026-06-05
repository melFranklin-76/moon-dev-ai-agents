import Foundation
import WebKit

final class CookieStore {
    static let shared = CookieStore()
    private init() {}

    private let storageKey = "PersistentCookiesKey"

    // Save cookies from the provided store to UserDefaults
    func persistCookies(from store: WKHTTPCookieStore, completion: (() -> Void)? = nil) {
        store.getAllCookies { cookies in
            let archived = cookies.compactMap { cookie -> [String: Any]? in
                return cookie.properties as? [String : Any]
            }
            UserDefaults.standard.set(archived, forKey: self.storageKey)
            UserDefaults.standard.synchronize()
            completion?()
        }
    }

    // Restore cookies to the provided store, then call completion
    func restoreCookies(into store: WKHTTPCookieStore, completion: @escaping () -> Void) {
        guard let saved = UserDefaults.standard.array(forKey: storageKey) as? [[HTTPCookiePropertyKey: Any]] else {
            completion()
            return
        }
        let group = DispatchGroup()
        for props in saved {
            if let cookie = HTTPCookie(properties: props) {
                group.enter()
                store.setCookie(cookie) { group.leave() }
            }
        }
        group.notify(queue: .main) {
            completion()
        }
    }
}
