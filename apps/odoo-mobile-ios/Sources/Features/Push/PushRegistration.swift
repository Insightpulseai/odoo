import UIKit
import UserNotifications

/// Registers device APNs token with the Odoo server.
struct PushRegistration {
    private let odooClient: OdooClient

    init(client: OdooClient = OdooClient()) {
        self.odooClient = client
    }

    /// Request notification authorization and register device token with Odoo.
    func requestAndRegister() async {
        let center = UNUserNotificationCenter.current()
        guard (try? await center.requestAuthorization(options: [.alert, .badge, .sound])) == true else {
            return
        }
        await MainActor.run {
            UIApplication.shared.registerForRemoteNotifications()
        }
    }

    /// Called from AppDelegate/scene delegate with the APNs device token data.
    func register(deviceTokenData: Data) async {
        let tokenString = deviceTokenData.map { String(format: "%02x", $0) }.joined()
        // TODO: call OdooClient to POST token to /web/push/register or custom endpoint
        print("[PushRegistration] APNs token: \(tokenString) — TODO: register with Odoo")
    }
}
