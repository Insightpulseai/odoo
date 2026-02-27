import Foundation
import Security

/// Keychain-backed store for Odoo OAuth access and refresh tokens.
/// All items stored with kSecAttrAccessible = kSecAttrAccessibleAfterFirstUnlock.
final class TokenStore {
    static let shared = TokenStore()
    private init() {}

    struct Tokens: Codable {
        let accessToken: String
        let refreshToken: String
        let expiresAt: Date
    }

    enum TokenStoreError: Error {
        case encodingFailed
        case decodingFailed
        case keychainError(OSStatus)
    }

    private let service = "com.insightpulseai.odoo-mobile"
    private let account = "oauth-tokens"

    func save(_ tokens: SSOAuthSession.OAuthTokens) throws {
        let storableTokens = Tokens(
            accessToken: tokens.accessToken,
            refreshToken: tokens.refreshToken,
            expiresAt: tokens.expiresAt
        )
        guard let data = try? JSONEncoder().encode(storableTokens) else {
            throw TokenStoreError.encodingFailed
        }
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
        ]
        let attributes: [String: Any] = [
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlock,
        ]
        // Attempt update; add if not present
        let status = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)
        if status == errSecItemNotFound {
            let addQuery = query.merging(attributes) { $1 }
            let addStatus = SecItemAdd(addQuery as CFDictionary, nil)
            if addStatus != errSecSuccess {
                throw TokenStoreError.keychainError(addStatus)
            }
        } else if status != errSecSuccess {
            throw TokenStoreError.keychainError(status)
        }
    }

    func load() throws -> Tokens? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne,
        ]
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess, let data = result as? Data else {
            if status == errSecItemNotFound { return nil }
            throw TokenStoreError.keychainError(status)
        }
        guard let tokens = try? JSONDecoder().decode(Tokens.self, from: data) else {
            throw TokenStoreError.decodingFailed
        }
        return tokens
    }

    func clear() throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
        ]
        let status = SecItemDelete(query as CFDictionary)
        if status != errSecSuccess && status != errSecItemNotFound {
            throw TokenStoreError.keychainError(status)
        }
    }
}
