# odoo-mobile-ios — Mobile App Test Evidence

**Stamp**: 2026-03-01T09:41+0800
**Branch**: feat/ipai-module-audit-odoo19
**Scope**: `apps/odoo-mobile-ios/`
**Swift**: 6.2.3 (arm64-apple-macosx26.0)

---

## STATUS=COMPLETE

**19 / 19 tests passed** — 2 suites, 0 failures.

---

## [CONTEXT]

- **repo**: /Users/tbwa/Documents/GitHub/Insightpulseai/odoo
- **branch**: feat/ipai-module-audit-odoo19
- **cwd**: apps/odoo-mobile-ios
- **goal**: Build Swift package, run unit tests, verify network readiness
- **stamp**: 2026-03-01T09:41+0800

---

## [EVIDENCE]

### Network Readiness

| Endpoint | Status |
|----------|--------|
| Odoo ERP — `https://erp.insightpulseai.com` | HTTP 200 ✅ |
| Supabase — `https://spdtwktxdalcfigzeqrz.supabase.co` | HTTP 200 ✅ |

### Build

```
command: swift build (macOS arm64)
result:  PASS — Build complete
```

### Test Run

```
command: swift test -Xswiftc -F<CLT/Frameworks> -Xlinker -rpath <CLT/Frameworks>
result:  PASS — Test run with 19 tests in 2 suites passed after 0.101 seconds.
saved_to: logs/swift_test.log
```

| Suite | Tests | Result | Duration |
|-------|-------|--------|----------|
| DeepLinkRouter | 14 | ✅ All passed | 0.002s |
| TokenStore | 5 | ✅ All passed | 0.101s |

#### DeepLinkRouter — 14 tests

| Test | Result |
|------|--------|
| record — sale.order/42 | ✅ passed |
| record — purchase.order/1 | ✅ passed |
| record — account.move/999 | ✅ passed |
| record — missing id → unknown | ✅ passed |
| record — non-numeric id → unknown | ✅ passed |
| task — id 7 | ✅ passed |
| task — large id 100000 | ✅ passed |
| task — non-numeric id → unknown | ✅ passed |
| expense — id 3 | ✅ passed |
| expense — non-numeric id → unknown | ✅ passed |
| universal link insightpulseai.com → unknown (stub) | ✅ passed |
| random https URL → unknown | ✅ passed |
| wrong scheme 'odoo://' → unknown | ✅ passed |
| empty path → unknown | ✅ passed |

#### TokenStore — 5 tests

| Test | Result |
|------|--------|
| save + load round-trip | ✅ passed |
| load returns nil when empty | ✅ passed |
| clear removes tokens | ✅ passed |
| overwrite updates value | ✅ passed |
| clear is idempotent on empty keychain | ✅ passed |

---

## [CHANGES]

| File | Change |
|------|--------|
| `Package.swift` | Added `.macOS(.v14)` platform to enable `swift test` on macOS |
| `Sources/App/OdooMobileApp.swift` | Wrapped in `#if os(iOS) \|\| os(visionOS)` — removes `@main` `_main` conflict with test runner |
| `Sources/Features/Push/PushRegistration.swift` | Wrapped in `#if canImport(UIKit)` — UIApplication.shared requires UIKit |
| `Sources/Features/DocumentScan/DocumentScanView.swift` | Wrapped in `#if canImport(UIKit)` — VisionKit + UIViewControllerRepresentable require UIKit |
| `Sources/Features/Auth/SSOAuthSession.swift` | Removed `: NSObject` (struct can't inherit from class in Swift 6); added `@available(macOS 10.15, iOS 13.0, *)` |
| `Sources/Features/Push/DeepLinkRouter.swift` | Swift 6 pattern fix: bound optional `let idStr?` is non-optional — removed `?? ""` and `!` force-unwraps |
| `Tests/TestFoundationBridge.swift` | New — provides `url(_:)` and `futureDate(_:)` helpers so test files avoid importing both `Foundation` and `Testing` in the same file (avoids missing `_Testing_Foundation` cross-import overlay in CLT) |
| `Tests/DeepLinkRouterTests.swift` | New — 14 Swift Testing tests for `DeepLinkRouter.resolve()` |
| `Tests/TokenStoreTests.swift` | New — 5 Swift Testing tests for `TokenStore` Keychain CRUD; `.serialized` prevents concurrent Keychain collision |

---

## [NOTES]

### Why `-Xswiftc -F` and `-Xlinker -rpath`

Command Line Tools ships `Testing.framework` at a non-standard path:

```
/Library/Developer/CommandLineTools/Library/Developer/Frameworks/Testing.framework
```

The framework binary and `_Testing_Foundation` cross-import overlay are present but lack swiftmodule files. To use `import Testing` with `import Foundation` in the same file requires the `_Testing_Foundation` swiftmodule (only in full Xcode SDK).

**Workaround**: `TestFoundationBridge.swift` imports only `Foundation` and provides typed helpers; test files import only `Testing` + `@testable import OdooMobile`. This avoids the cross-import overlay requirement.

The `-Xswiftc -F` flag exposes `Testing.framework` to the compiler; the `-Xlinker -rpath` flag ensures the test binary can find it at runtime.

### TokenStore — Keychain on macOS

`errSecDuplicateItem` (-25299) appeared when two tests with shared Keychain state ran concurrently. Fixed by adding `.serialized` to the test suite so tests run sequentially.

### Source Files Not Tested

The following files are guarded from macOS compilation and have no macOS-runnable unit tests (require iOS Simulator or device + Xcode):

- `PushRegistration.swift` — APNs device registration (UIApplication.shared)
- `DocumentScanView.swift` — VNDocumentCameraViewController (VisionKit / UIKit camera)
- `SSOAuthSession.swift` — ASWebAuthenticationSession (requires iOS 13+)
- `OdooMobileApp.swift` — SwiftUI App entry point
- `BiometricGate.swift` — LAContext Face ID / Touch ID
- `OfflineQueue.swift` — CoreData (TODO stubs)
- `OdooClient.swift` — URLSession async RPC

---

## [NEXT - DETERMINISTIC]

1. Install Xcode 16+ (`xcodes install "16.4"`) to run full suite including Simulator tests
2. Wire `OdooClient.call` → actual test against `odoo_dev` JSON-RPC endpoint
3. Implement PKCE in `SSOAuthSession.authenticate()` (marked TODO)
4. Complete `OdooClient.uploadDocument()` multipart upload (marked TODO)
5. Add CoreData store to `OfflineQueue` (marked TODO)
6. Run `xcodebuild test -destination "platform=iOS Simulator,name=iPhone 16"` in CI
