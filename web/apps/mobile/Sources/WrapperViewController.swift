import UIKit
import WebKit

class WrapperViewController: UIViewController, WKNavigationDelegate, WKUIDelegate {
    var webView: WKWebView!
    
    // Config
    let odooBaseURL = AppEnvironment.current.baseURL

    override func loadView() {
        let webConfiguration = WKWebViewConfiguration()
        // Setup configuration for JS Bridge
        let contentController = WKUserContentController()
        webConfiguration.userContentController = contentController
        
        webView = WKWebView(frame: .zero, configuration: webConfiguration)
        webView.navigationDelegate = self
        webView.uiDelegate = self
        
        // Allows the WKWebView to inspect if needed via Safari
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
        
        loadOdoo()
    }
    
    private func loadOdoo() {
        var request = URLRequest(url: odooBaseURL)
        request.cachePolicy = .reloadRevalidatingCacheData
        webView.load(request)
    }
    
    // MARK: - Direct Routing (Deep Links & Push)
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
        print("Failed to load Odoo: \(error.localizedDescription)")
        showOfflineState()
    }
    
    private func showOfflineState() {
        // Fallback UI for offline / no-connectivity loading
        let alert = UIAlertController(title: "Connection Error", 
                                      message: "Failed to connect to InsightPulseAI. Please check your network and try again.", 
                                      preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "Retry", style: .default, handler: { [weak self] _ in
            self?.loadOdoo()
        }))
        present(alert, animated: true)
    }
    
    // MARK: - WKUIDelegate (Camera/File Upload Bridge)
    
    // WKWebView natively handles <input type="file"> via the UIDelegate 
    // by presenting the UIDocumentPickerViewController / UIImagePickerController
    // internally, satisfying Phase 3 native capabilities passively.
}
