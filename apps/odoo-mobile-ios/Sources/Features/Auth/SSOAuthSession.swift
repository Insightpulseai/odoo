import AuthenticationServices
import CryptoKit
import Foundation

/// SSO authentication via Odoo OIDC endpoint using ASWebAuthenticationSession.
/// Implements PKCE (RFC 7636) — code_verifier is generated per-session, never stored.
@available(macOS 10.15, iOS 13.0, *)
struct SSOAuthSession {

    /// OAuth token pair returned after successful OIDC flow.
    struct OAuthTokens {
        let accessToken: String
        let refreshToken: String
        let expiresAt: Date
    }

    // MARK: - Configuration (inject from Info.plist or environment)

    private let odooBaseURL: String = {
        Bundle.main.object(forInfoDictionaryKey: "OdooBaseURL") as? String
            ?? "https://erp.insightpulseai.com"
    }()

    private let clientID: String = {
        Bundle.main.object(forInfoDictionaryKey: "OdooOIDCClientID") as? String
            ?? "mobile"
    }()

    private let redirectURI = "odoomobile://oauth/callback"

    // MARK: - Public API

    /// Starts the OIDC Authorization Code + PKCE flow.
    /// Returns nil if the user cancels or any step fails.
    func authenticate() async -> OAuthTokens? {
        let verifier = PKCE.verifier()
        let challenge = PKCE.challenge(for: verifier)

        let authURL = buildAuthURL(challenge: challenge)
        guard let url = URL(string: authURL) else { return nil }

        guard let code = await presentWebSession(url: url) else { return nil }
        return await exchangeCode(code, verifier: verifier)
    }

    // MARK: - PKCE helpers

    enum PKCE {
        /// Generates a cryptographically random code_verifier (43 chars, base64url, RFC 7636 §4.1).
        static func verifier() -> String {
            var bytes = [UInt8](repeating: 0, count: 32)
            _ = SecRandomCopyBytes(kSecRandomDefault, bytes.count, &bytes)
            return Data(bytes).base64URLEncodedString()
        }

        /// Derives code_challenge = BASE64URL(SHA256(ASCII(verifier))) (RFC 7636 §4.2).
        static func challenge(for verifier: String) -> String {
            let data = Data(verifier.utf8)
            let digest = SHA256.hash(data: data)
            return Data(digest).base64URLEncodedString()
        }
    }

    // MARK: - Private helpers

    private func buildAuthURL(challenge: String) -> String {
        var components = URLComponents(string: "\(odooBaseURL)/web/oauth2/authorize")!
        components.queryItems = [
            URLQueryItem(name: "client_id",             value: clientID),
            URLQueryItem(name: "redirect_uri",          value: redirectURI),
            URLQueryItem(name: "response_type",         value: "code"),
            URLQueryItem(name: "scope",                 value: "openid"),
            URLQueryItem(name: "code_challenge",        value: challenge),
            URLQueryItem(name: "code_challenge_method", value: "S256"),
        ]
        return components.url?.absoluteString ?? ""
    }

    /// Presents ASWebAuthenticationSession and returns the authorization code.
    private func presentWebSession(url: URL) async -> String? {
        await withCheckedContinuation { continuation in
            let webSession = ASWebAuthenticationSession(
                url: url,
                callbackURLScheme: "odoomobile"
            ) { callbackURL, error in
                guard
                    error == nil,
                    let callbackURL,
                    let code = URLComponents(url: callbackURL, resolvingAgainstBaseURL: false)?
                        .queryItems?
                        .first(where: { $0.name == "code" })?
                        .value
                else {
                    continuation.resume(returning: nil)
                    return
                }
                continuation.resume(returning: code)
            }
            webSession.prefersEphemeralWebBrowserSession = false
            // presentationContextProvider set via UIWindowSceneDelegate on iOS;
            // on macOS the session self-presents.
            webSession.start()
        }
    }

    /// Exchanges the authorization code + PKCE verifier for tokens.
    private func exchangeCode(_ code: String, verifier: String) async -> OAuthTokens? {
        guard let url = URL(string: "\(odooBaseURL)/web/oauth2/token") else { return nil }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")

        let params: [String: String] = [
            "grant_type":    "authorization_code",
            "code":          code,
            "redirect_uri":  redirectURI,
            "client_id":     clientID,
            "code_verifier": verifier,
        ]
        request.httpBody = params
            .map { "\($0.key)=\($0.value.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? "")" }
            .joined(separator: "&")
            .data(using: .utf8)

        guard
            let (data, response) = try? await URLSession.shared.data(for: request),
            let http = response as? HTTPURLResponse,
            http.statusCode == 200
        else { return nil }

        struct TokenResponse: Decodable {
            let access_token: String
            let refresh_token: String?
            let expires_in: Int?
        }
        guard let tokenResp = try? JSONDecoder().decode(TokenResponse.self, from: data) else { return nil }

        let expiresAt = Date(timeIntervalSinceNow: TimeInterval(tokenResp.expires_in ?? 3600))
        return OAuthTokens(
            accessToken:  tokenResp.access_token,
            refreshToken: tokenResp.refresh_token ?? "",
            expiresAt:    expiresAt
        )
    }
}

// MARK: - Data + base64url

private extension Data {
    /// RFC 4648 §5 base64url without padding.
    func base64URLEncodedString() -> String {
        base64EncodedString()
            .replacingOccurrences(of: "+", with: "-")
            .replacingOccurrences(of: "/", with: "_")
            .replacingOccurrences(of: "=", with: "")
    }
}
