# Odoo Mobile iOS — Constitution

## Non-Negotiable Constraints

1. **iOS 17+ only.** No fallback for older OS versions.
2. **SwiftUI throughout.** No UIKit wrappers unless a framework forces it (e.g., `VNDocumentCameraViewController`).
3. **No private APIs.** Only public frameworks: Foundation, SwiftUI, UIKit (when required), LocalAuthentication, Vision, VisionKit, CoreData, UserNotifications, AuthenticationServices, Network.
4. **App Store compliant.** Privacy Nutrition Labels must reflect all data categories. No background location. No hidden network calls.
5. **No hardcoded credentials.** All endpoints, client IDs, and tokens via environment configuration or Keychain.
6. **Keychain for secrets.** Access/refresh tokens stored in Keychain with `kSecAttrAccessible = afterFirstUnlock`.
7. **Offline-first for writes.** All mutations queue to CoreData offline queue; sync on reachability restore.
8. **Fastlane match for certificates.** No local certificate files in the repo. `fastlane match appstore` only.
9. **Package.swift only.** No `.xcodeproj`, no CocoaPods, no Carthage.
10. **OIDC/OAuth2 for auth.** `ASWebAuthenticationSession` → Odoo OIDC endpoint. No direct password exchange.
