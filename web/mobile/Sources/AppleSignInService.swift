import AuthenticationServices
import UIKit

/// Sign in with Apple — required by App Store Review Guideline 4.8 if the
/// app uses any third-party login (we use Microsoft Entra via MSAL.js inside
/// the PWA). Apple ID becomes a parallel auth path so users who do not have a
/// Microsoft work account can still log in.
///
/// On success, we exchange the Apple identity token for an Odoo session and
/// store the cookie via SessionManager.
final class AppleSignInService: NSObject {

    static let shared = AppleSignInService()

    private var presentationAnchor: ASPresentationAnchor?
    private var completion: ((Result<AppleCredential, Error>) -> Void)?

    private override init() { super.init() }

    struct AppleCredential {
        let userIdentifier: String
        let identityToken: String
        let authorizationCode: String
        let email: String?
        let fullName: String?
    }

    /// Begin the Sign in with Apple flow from the given window.
    func signIn(from window: UIWindow,
                completion: @escaping (Result<AppleCredential, Error>) -> Void) {
        self.presentationAnchor = window
        self.completion = completion

        let provider = ASAuthorizationAppleIDProvider()
        let request = provider.createRequest()
        request.requestedScopes = [.fullName, .email]

        let controller = ASAuthorizationController(authorizationRequests: [request])
        controller.delegate = self
        controller.presentationContextProvider = self
        controller.performRequests()
    }
}

extension AppleSignInService: ASAuthorizationControllerDelegate,
                              ASAuthorizationControllerPresentationContextProviding {

    func presentationAnchor(for controller: ASAuthorizationController) -> ASPresentationAnchor {
        return presentationAnchor ?? UIWindow()
    }

    func authorizationController(controller: ASAuthorizationController,
                                 didCompleteWithAuthorization authorization: ASAuthorization) {
        guard let credential = authorization.credential as? ASAuthorizationAppleIDCredential,
              let identityToken = credential.identityToken,
              let identityTokenString = String(data: identityToken, encoding: .utf8),
              let authorizationCode = credential.authorizationCode,
              let authorizationCodeString = String(data: authorizationCode, encoding: .utf8) else {
            completion?(.failure(NSError(domain: "AppleSignIn", code: -1,
                                         userInfo: [NSLocalizedDescriptionKey: "Invalid Apple credential"])))
            return
        }

        let fullName: String?
        if let nameComponents = credential.fullName,
           let formatted = PersonNameComponentsFormatter().string(for: nameComponents),
           !formatted.isEmpty {
            fullName = formatted
        } else {
            fullName = nil
        }

        let appleCred = AppleCredential(
            userIdentifier: credential.user,
            identityToken: identityTokenString,
            authorizationCode: authorizationCodeString,
            email: credential.email,
            fullName: fullName
        )

        // Persist the user identifier so we can offer "continue as <name>" later.
        _ = KeychainService.shared.set(credential.user, for: "apple_user_id")
        if let email = credential.email {
            _ = KeychainService.shared.set(email, for: "apple_user_email")
        }

        completion?(.success(appleCred))
    }

    func authorizationController(controller: ASAuthorizationController,
                                 didCompleteWithError error: Error) {
        completion?(.failure(error))
    }
}
