import AuthenticationServices
import Foundation

/// SSO authentication via Odoo OIDC endpoint using ASWebAuthenticationSession.
/// Tokens are returned as OAuthTokens; caller is responsible for storing them.
struct SSOAuthSession: NSObject {
    /// OAuth token pair returned after successful OIDC flow.
    struct OAuthTokens {
        let accessToken: String
        let refreshToken: String
        let expiresAt: Date
    }

    // TODO: inject from app configuration / Info.plist key
    private let odooBaseURL: String = {
        Bundle.main.object(forInfoDictionaryKey: "OdooBaseURL") as? String
            ?? "https://erp.insightpulseai.com"
    }()

    private let clientID: String = {
        Bundle.main.object(forInfoDictionaryKey: "OdooOIDCClientID") as? String
            ?? "mobile"
    }()

    private let redirectURI = "odoomobile://oauth/callback"

    /// Starts the OIDC Authorization Code flow.
    /// Returns nil if the user cancels or an error occurs.
    func authenticate() async -> OAuthTokens? {
        // TODO: implement PKCE challenge generation
        let authURL = buildAuthURL()
        guard let url = URL(string: authURL) else { return nil }

        return await withCheckedContinuation { continuation in
            let session = ASWebAuthenticationSession(
                url: url,
                callbackURLScheme: "odoomobile"
            ) { callbackURL, error in
                guard
                    error == nil,
                    let callbackURL = callbackURL,
                    let code = URLComponents(url: callbackURL, resolvingAgainstBaseURL: false)?
                        .queryItems?
                        .first(where: { $0.name == "code" })?
                        .value
                else {
                    continuation.resume(returning: nil)
                    return
                }

                Task {
                    let tokens = await self.exchangeCode(code)
                    continuation.resume(returning: tokens)
                }
            }
            session.prefersEphemeralWebBrowserSession = false
            // TODO: set presentationContextProvider via UIWindowSceneDelegate
            session.start()
        }
    }

    // MARK: - Private helpers

    private func buildAuthURL() -> String {
        // TODO: add PKCE code_challenge
        "\(odooBaseURL)/web/oauth2/authorize"
            + "?client_id=\(clientID)"
            + "&redirect_uri=\(redirectURI.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? "")"
            + "&response_type=code"
            + "&scope=openid"
    }

    private func exchangeCode(_ code: String) async -> OAuthTokens? {
        // TODO: implement token endpoint POST with PKCE verifier
        nil
    }
}
