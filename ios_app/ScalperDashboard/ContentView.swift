import SwiftUI

struct ContentView: View {
    @AppStorage("serverHost") private var serverHost = "192.168.10.14"
    @AppStorage("serverPort") private var serverPort = "8501"
    @State private var showSettings = false
    @State private var reloadID = UUID()

    private var serverURL: URL {
        URL(string: "http://\(serverHost):\(serverPort)") ?? URL(string: "about:blank")!
    }

    var body: some View {
        NavigationStack {
            WebView(url: serverURL, reloadID: reloadID)
                .ignoresSafeArea(edges: .bottom)
                .navigationTitle("🌙 Scalper Dashboard")
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .navigationBarLeading) {
                        Button {
                            reloadID = UUID()
                        } label: {
                            Image(systemName: "arrow.clockwise")
                        }
                    }
                    ToolbarItem(placement: .navigationBarTrailing) {
                        Button {
                            showSettings = true
                        } label: {
                            Image(systemName: "gearshape")
                        }
                    }
                }
        }
        .sheet(isPresented: $showSettings, onDismiss: {
            reloadID = UUID()
        }) {
            SettingsView()
        }
    }
}
