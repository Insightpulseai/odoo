import UIKit
import WebKit

class WrapperViewController: UIViewController, WKNavigationDelegate, WKUIDelegate {
    var webView: WKWebView!
    private var bridge: JSBridge?

    let baseURL = AppEnvironment.current.baseURL

    override func loadView() {
        let webConfiguration = WKWebViewConfiguration()
        let contentController = WKUserContentController()

        // Inject the JS-side shim before any page JS runs.
        JSBridge.installShim(on: contentController)

        webConfiguration.userContentController = contentController
        webConfiguration.allowsInlineMediaPlayback = true
        webConfiguration.mediaTypesRequiringUserActionForPlayback = []

        webView = WKWebView(frame: .zero, configuration: webConfiguration)
        webView.navigationDelegate = self
        webView.uiDelegate = self
        webView.allowsBackForwardNavigationGestures = true

        // Wire native handlers AFTER the webView exists.
        let bridge = JSBridge(webView: webView, hostController: self)
        for name in JSBridge.handlerNames {
            contentController.add(bridge, name: name)
        }
        self.bridge = bridge

        #if DEBUG
        if #available(iOS 16.4, *) {
            webView.isInspectable = true
        }
        #endif

        view = webView
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        loadApp()
    }

    private func loadApp() {
        var request = URLRequest(url: baseURL)
        request.cachePolicy = .reloadRevalidatingCacheData
        webView.load(request)
    }

    public func navigateTo(url: URL) {
        var request = URLRequest(url: url)
        request.cachePolicy = .reloadRevalidatingCacheData
        webView.load(request)
    }

    // MARK: - WKNavigationDelegate

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        handleLoadError(error)
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        handleLoadError(error)
    }

    private func handleLoadError(_ error: Error) {
        let nsError = error as NSError
        if nsError.code == NSURLErrorCancelled { return }
        showOfflineState()
    }

    private func showOfflineState() {
        let alert = UIAlertController(
            title: "Connection Error",
            message: "Failed to connect to InsightPulse. Please check your network and try again.",
            preferredStyle: .alert
        )
        alert.addAction(UIAlertAction(title: "Retry", style: .default) { [weak self] _ in
            self?.loadApp()
        })
        present(alert, animated: true)
    }
}
