import SwiftUI

@main
struct ScalperDashboardApp: App {
    @Environment(\.scenePhase) private var scenePhase
    @State private var reloadTick = 0

    var body: some Scene {
        WindowGroup {
            ContentView(reloadTickExternal: $reloadTick)
                .preferredColorScheme(.dark)
        }
        .onChange(of: scenePhase) { _, newPhase in
            if newPhase == .active {
                // Bump the tick to force a refresh of the dashboard when app becomes active
                reloadTick += 1
            }
        }
    }
}
