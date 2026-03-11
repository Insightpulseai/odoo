#if canImport(UIKit)
import UIKit
import UserNotifications

/// Registers device APNs token with the Odoo server.
struct PushRegistration {
    private let odooClient: OdooClient

    init(client: OdooClient = OdooClient()) {
        self.odooClient = client
    }

    func requestAndRegister() async {
        let center = UNUserNotificationCenter.current()
        guard (try? await center.requestAuthorization(options: [.alert, .badge, .sound])) == true else {
            return
        }
        await MainActor.run {
            UIApplication.shared.registerForRemoteNotifications()
        }
    }

    func register(deviceTokenData: Data) async {
        let tokenString = deviceTokenData.map { String(format: "%02x", $0) }.joined()
        print("[PushRegistration] APNs token: \(tokenString) — TODO: register with Odoo")
    }
}
#endif
