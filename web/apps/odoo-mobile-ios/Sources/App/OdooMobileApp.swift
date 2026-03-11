#if os(iOS) || os(visionOS)
import SwiftUI

@main
struct OdooMobileApp: App {
    @StateObject private var authState = AuthState()
    var body: some Scene {
        WindowGroup {
            ContentView().environmentObject(authState)
        }
    }
}
struct ContentView: View {
    @EnvironmentObject var authState: AuthState
    var body: some View {
        if authState.isAuthenticated { MainTabView() } else { LoginView() }
    }
}
struct LoginView: View {
    @EnvironmentObject var authState: AuthState
    var body: some View {
        VStack(spacing: 24) {
            Image(systemName: "building.2.crop.circle").font(.system(size: 64)).foregroundColor(.accentColor)
            Text("Odoo Mobile").font(.largeTitle.bold())
            Button("Sign In with Odoo SSO") { Task { await authState.signIn() } }
                .buttonStyle(.borderedProminent).controlSize(.large)
        }.padding()
    }
}
struct MainTabView: View {
    var body: some View {
        TabView {
            Text("Dashboard").tabItem { Label("Home", systemImage: "house") }
            Text("Documents").tabItem { Label("Docs", systemImage: "doc.viewfinder") }
            Text("Tasks").tabItem { Label("Tasks", systemImage: "checklist") }
            Text("Profile").tabItem { Label("Profile", systemImage: "person.circle") }
        }
    }
}
@MainActor
class AuthState: ObservableObject {
    @Published var isAuthenticated = false
    func signIn() async {
        if #available(iOS 13.0, *) {
            let session = SSOAuthSession()
            if let tokens = await session.authenticate() {
                try? TokenStore.shared.save(tokens)
                isAuthenticated = true
            }
        }
    }
    func signOut() { try? TokenStore.shared.clear(); isAuthenticated = false }
}
#endif
