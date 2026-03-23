import UIKit
import SwiftUI

class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?
    private var blurEffectView: UIVisualEffectView?

    func scene(_ scene: UIScene,
               willConnectTo session: UISceneSession,
               options connectionOptions: UIScene.ConnectionOptions) {

        guard let windowScene = (scene as? UIWindowScene) else { return }
        let window = UIWindow(windowScene: windowScene)

        // iOS 18+: Use SwiftUI Tab API (Liquid Glass on iOS 26+)
        // Earlier: Use UIKit WrapperViewController directly
        if #available(iOS 18.0, *) {
            let hostingController = UIHostingController(rootView: LiquidGlassTabView())
            window.rootViewController = hostingController
        } else {
            let webVC = WrapperViewController()
            window.rootViewController = webVC
        }

        self.window = window
        window.makeKeyAndVisible()
        
        // Handle deep link on cold start
        if let userActivity = connectionOptions.userActivities.first {
            self.scene(scene, continue: userActivity)
        }
    }
    
    func sceneWillResignActive(_ scene: UIScene) {
        // Blur screen for security to prevent sensitive data in multitask view
        guard blurEffectView == nil, let window = window else { return }
        let blurEffect = UIBlurEffect(style: .systemMaterial)
        let blurView = UIVisualEffectView(effect: blurEffect)
        blurView.frame = window.bounds
        window.addSubview(blurView)
        self.blurEffectView = blurView
    }

    func sceneDidBecomeActive(_ scene: UIScene) {
        // Biometric unlock on resume
        if blurEffectView != nil {
            BiometricAuth.shared.authenticateUser { [weak self] success, _ in
                if success {
                    self?.removeBlur()
                } else {
                    print("Biometric failed. Please authenticate.")
                }
            }
        }
    }
    
    private func removeBlur() {
        UIView.animate(withDuration: 0.3, animations: {
            self.blurEffectView?.alpha = 0
        }) { _ in
            self.blurEffectView?.removeFromSuperview()
            self.blurEffectView = nil
        }
    }
    
    // MARK: - Deep Links / Universal Links
    func scene(_ scene: UIScene, continue userActivity: NSUserActivity) {
        guard userActivity.activityType == NSUserActivityTypeBrowsingWeb,
              let incomingURL = userActivity.webpageURL,
              let webVC = window?.rootViewController as? WrapperViewController else {
            return
        }
        
        // Forward universal link directly to WKWebView
        webVC.navigateTo(url: incomingURL)
    }
}
