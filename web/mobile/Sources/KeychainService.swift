import Foundation
import Security

/// Keychain wrapper for secure token/session storage.
/// Concur parity: Secure session persistence across app launches.
final class KeychainService {

    static let shared = KeychainService()

    private let service = "com.insightpulseai.odoo"

    private init() {}

    /// Store a value securely in the Keychain.
    func set(_ value: String, for key: String) -> Bool {
        guard let data = value.data(using: .utf8) else { return false }

        // Delete existing entry first
        delete(key)

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
        ]

        let status = SecItemAdd(query as CFDictionary, nil)
        return status == errSecSuccess
    }

    /// Retrieve a value from the Keychain.
    func get(_ key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess,
              let data = result as? Data,
              let value = String(data: data, encoding: .utf8) else {
            return nil
        }
        return value
    }

    /// Delete a value from the Keychain.
    @discardableResult
    func delete(_ key: String) -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key
        ]

        let status = SecItemDelete(query as CFDictionary)
        return status == errSecSuccess || status == errSecItemNotFound
    }
}

// MARK: - Session Manager

/// Manages Odoo session tokens using Keychain storage.
/// Injects session cookies into WKWebView on app resume.
final class SessionManager {

    static let shared = SessionManager()

    private let sessionKey = "odoo_session_id"
    private let csrfKey = "odoo_csrf_token"

    private init() {}

    var sessionID: String? {
        get { KeychainService.shared.get(sessionKey) }
        set {
            if let value = newValue {
                _ = KeychainService.shared.set(value, for: sessionKey)
            } else {
                KeychainService.shared.delete(sessionKey)
            }
        }
    }

    var csrfToken: String? {
        get { KeychainService.shared.get(csrfKey) }
        set {
            if let value = newValue {
                _ = KeychainService.shared.set(value, for: csrfKey)
            } else {
                KeychainService.shared.delete(csrfKey)
            }
        }
    }

    /// Check if we have a persisted session.
    var hasSession: Bool { sessionID != nil }

    /// Clear all session data (logout).
    func clearSession() {
        sessionID = nil
        csrfToken = nil
        print("Session cleared from Keychain")
    }
}
