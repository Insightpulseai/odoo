# Testing — odoo-mobile-ios

## Test suites

| Suite | Tests | Requires |
|-------|-------|----------|
| `BiometricGate` | 4 | macOS CLT only (injected mocks, no hardware) |
| `DeepLinkRouter` | 14 | macOS CLT only |
| `OdooClient` | 7 | macOS CLT only (MockURLProtocol) |
| `OdooClientTransport` | 2 | macOS CLT only (CaptureTransport) |
| `OfflineQueue` | 4 | macOS CLT only (in-memory CoreData) |
| `TokenStore` | 5 | macOS CLT only (Keychain) |
| **Total** | **36** | |

---

## Running tests locally (macOS Command Line Tools)

No Xcode installation required. All unit tests run under Swift CLT.

```bash
cd apps/odoo-mobile-ios

swift test \
  -Xswiftc -F"/Library/Developer/CommandLineTools/Library/Developer/Frameworks" \
  -Xlinker -rpath \
  -Xlinker "/Library/Developer/CommandLineTools/Library/Developer/Frameworks"
```

The `-F` and `-rpath` flags are **required** on macOS CLT installations (no Xcode).
They locate `Testing.framework` which ships with the Swift CLT but is not on the
default framework search path. Do not remove these flags.

Expected output (last line):
```
Test run with 36 tests in 6 suites passed after 0.NNN seconds.
```

---

## Running tests locally (Xcode / iOS Simulator)

Requires Xcode 16.x. The canonical pinned version is **16.4**.

```bash
# Install (one-time, Apple ID required)
xcodes install "16.4"

# Select Xcode (or use the shared script)
scripts/mobile/verify_xcode.sh

# Run on Simulator
cd apps/odoo-mobile-ios
xcodebuild test \
  -scheme OdooMobile \
  -destination "platform=iOS Simulator,name=iPhone 16,OS=latest" \
  CODE_SIGN_IDENTITY="" \
  CODE_SIGNING_REQUIRED=NO
```

---

## Evidence logs

Test logs from CI and local verification runs are saved to:

```
web/docs/evidence/<YYYYMMDD-HHMM+0800>/odoo-mobile-ios-*/logs/swift-test.log
```

Example (Phase 4 BiometricGate run):
```
web/docs/evidence/20260301-1047+0800/odoo-mobile-ios-biometric/logs/swift-test.log
```

---

## Design constraints

### Foundation + Testing cross-import overlay

The macOS CLT ships without `_Testing_Foundation.framework`. This means a single
`.swift` file **cannot** contain both `import Foundation` and `import Testing`.

**File-split pattern** (enforced across all test files):

| File | Allowed imports | Purpose |
|------|----------------|---------|
| `*Mocks.swift` | `Foundation`, `LocalAuthentication`, `@testable import OdooMobile` | Mock structs + helpers |
| `*Tests.swift` | `Testing`, `@testable import OdooMobile` | `@Suite` + `@Test` functions |

Foundation types needed in test files must be accessed via type inference from the
mock helpers. Never add `import Foundation` to a `*Tests.swift` file.

### Inter-suite parallelism

Swift Testing runs `@Suite` instances **in parallel** by default. Static shared state
in `URLProtocol` subclasses causes race conditions across suites. Each suite uses its
own dedicated `URLProtocol` subclass:

| Suite | Protocol class | Session factory |
|-------|---------------|-----------------|
| `OdooClientTests` | `MockURLProtocol` | `mockSession()` |
| `OfflineQueueTests` | `OfflineQueueMockProtocol` | `queueSyncSession()` |
| `OdooClientTransportTests` | `CaptureTransport` (injected) | `makeClientWithCapture()` |

### BiometricGate

`LAContext` requires biometric hardware or a Simulator. On macOS CLT, it is
unavailable. The `BiometricAuthenticating` protocol (in `BiometricGate.swift`)
makes the gate injectable so tests run without hardware.

### OfflineQueue CoreData

`NSPersistentContainer` normally looks for a `.momd` bundle resource. SPM has no
Xcode-managed resources. The in-memory stack uses a programmatic
`NSManagedObjectModel` and `URL(fileURLWithPath: "/dev/null")` as the store URL.
Use `OfflineQueue.makeInMemory()` in tests; never `OfflineQueue.shared`.
