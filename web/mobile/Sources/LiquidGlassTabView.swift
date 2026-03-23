import SwiftUI

/// Root SwiftUI view adopting iOS 26 Liquid Glass tab bar.
/// Wraps the existing WKWebView-based WrapperViewController in a modern
/// tab interface with glass effects, scroll-minimization, and search integration.
///
/// Requires: iOS 26+ SDK (Xcode 26). Falls back to standard tabs on iOS 16-25.
@available(iOS 18.0, *)
struct LiquidGlassTabView: View {
    @State private var selectedTab: AppTab = .home
    @SceneStorage("selectedTab") private var persistedTab: String = AppTab.home.rawValue

    var body: some View {
        TabView(selection: $selectedTab) {
            Tab("Home", systemImage: "house", value: .home) {
                OdooWebView(route: "/web#action=home")
            }

            Tab("Expenses", systemImage: "plus.circle", value: .addExpense) {
                OdooWebView(route: "/web#action=expense")
            }

            Tab("Analytics", systemImage: "chart.bar", value: .analytics) {
                OdooWebView(route: "/web#action=analytics")
            }

            Tab("Search", systemImage: "magnifyingglass", value: .search) {
                OdooWebView(route: "/web#action=search")
            }

            Tab("Settings", systemImage: "gearshape", value: .settings) {
                OdooWebView(route: "/web#action=settings")
            }
        }
        .liquidGlassIfAvailable()
        .onChange(of: selectedTab) { _, newValue in
            persistedTab = newValue.rawValue
        }
        .onAppear {
            if let restored = AppTab(rawValue: persistedTab) {
                selectedTab = restored
            }
        }
    }
}

// MARK: - Tab Enum

enum AppTab: String, Hashable {
    case home
    case addExpense
    case analytics
    case search
    case settings
}

// MARK: - Liquid Glass Conditional Modifier

extension View {
    /// Applies Liquid Glass tab bar behavior on iOS 26+, no-op on earlier versions.
    @ViewBuilder
    func liquidGlassIfAvailable() -> some View {
        if #available(iOS 26.0, *) {
            self
                .tabBarMinimizeBehavior(.onScrollDown)
        } else {
            self
        }
    }
}

// MARK: - OdooWebView (SwiftUI wrapper for WKWebView)

import WebKit

struct OdooWebView: UIViewRepresentable {
    let route: String

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator

        #if DEBUG
        if #available(iOS 16.4, *) {
            webView.isInspectable = true
        }
        #endif

        let url = AppEnvironment.current.baseURL
            .appendingPathComponent(route)
        webView.load(URLRequest(url: url))
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {
        // Route changes trigger navigation
        let url = AppEnvironment.current.baseURL
            .appendingPathComponent(route)
        let currentURL = webView.url?.absoluteString ?? ""
        if !currentURL.contains(route) {
            webView.load(URLRequest(url: url))
        }
    }

    func makeCoordinator() -> Coordinator { Coordinator() }

    class Coordinator: NSObject, WKNavigationDelegate {
        func webView(_ webView: WKWebView,
                     didFailProvisionalNavigation navigation: WKNavigation!,
                     withError error: Error) {
            print("OdooWebView load failed: \(error.localizedDescription)")
        }
    }
}
