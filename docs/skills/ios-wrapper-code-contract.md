# iOS Wrapper Code Contract

## Purpose
This document defines the concrete code contract for the native iOS wrapper shell.

It applies to the following implementation surfaces:
- `WrapperViewController.swift`
- `BiometricAuth.swift`
- `Assets.xcassets`
- supporting `Info.plist` entries required by native auth/biometric behavior

This contract is subordinate to:
- `docs/skills/ios-native-wrapper.md`
- `docs/skills/ios-wrapper-ui-contract.md`

---

## 1. File ownership map

### WrapperViewController.swift
Owns:
- `WKWebView` construction and configuration
- navigation delegation
- route allowlist enforcement
- loading/progress state
- error-state presentation
- external URL handoff
- download/upload handoff coordination
- auth callback restoration target handling
- foreground/background shell reactions delegated from app lifecycle surfaces

Does not own:
- biometric policy persistence
- credential storage
- arbitrary business logic from hosted Odoo pages
- app icon logic
- hardcoded environment selection logic beyond consuming `Environment`

### BiometricAuth.swift
Owns:
- `LocalAuthentication` orchestration
- re-entry gating policy evaluation
- shield/unlock decision result
- biometric-availability probing
- fallback behavior contract
- lock/unlock result typing

Does not own:
- webview navigation
- auth callback handling
- session cookies/tokens
- UI layout of the main wrapper content surface

### Assets.xcassets
Owns:
- app icon delivery assets
- accent color
- native-shell-only branded/supporting assets
- optional state illustrations used by native overlays

Does not own:
- hosted web content assets
- arbitrary duplicate icon variants outside canonical source flow
- non-governed raster assets dropped ad hoc into the catalog

---

## 2. WrapperViewController.swift contract

### Required type role
`WrapperViewController` must remain the primary shell orchestration controller for the hosted app surface.

Preferred declaration shape:
- subclass of `UIViewController`
- conforms to `WKNavigationDelegate`
- conforms to `WKUIDelegate` if web UI delegate handling is required
- delegates file picking / document interaction only through explicit extensions or helper coordinators

### Required collaborators
`WrapperViewController` may depend on:
- `Environment`
- `BiometricAuth`
- `WKWebView`
- a route/host policy value or helper
- optional network/state overlay helpers

It must not directly embed unrelated release/signing/analytics concerns.

### Required state model
The controller must define an explicit shell state model.

Preferred minimum:
```swift
enum WrapperShellState {
    case booting
    case loading(URL?)
    case ready(URL?)
    case error(WrapperErrorState)
    case locked(LockReason)
}
```

Related types should be explicit:

```swift
enum LockReason {
    case coldStartProtection
    case foregroundReentry
    case policyRequired
}

enum WrapperErrorState: Equatable {
    case unreachableHost
    case tlsFailure
    case authRequired
    case blockedHost(URL)
    case unsupportedScheme(URL)
    case fileOperationFailed
    case timedOut
    case unknown
}
```

### Required stored properties

Minimum expected surfaces:

```swift
private let environment: Environment
private let biometricAuth: BiometricAuth
private var webView: WKWebView!
private var shellState: WrapperShellState = .booting
private var pendingPostAuthURL: URL?
private var lastAllowedURL: URL?
```

Optional:

```swift
private var reauthOverlayView: UIView?
private var loadingOverlayView: UIView?
private var errorOverlayView: UIView?
```

### Required lifecycle behavior

`WrapperViewController` must:

* build/configure the `WKWebView` in a deterministic setup path
* install delegates exactly once
* load a deterministic initial route from `Environment`
* transition through explicit shell states
* respond to foreground re-entry without losing contract ownership

### Required method surfaces

The controller should expose or implement equivalent methods for:

```swift
func loadInitialRoute()
func load(url: URL)
func handleAuthCallback(url: URL) -> Bool
func refreshCurrentPage()
func presentRecoverableError(_ errorState: WrapperErrorState)
func clearErrorAndRetry()
func lockForReentryIfNeeded()
func unlockAfterSuccessfulBiometricCheck()
func openExternally(_ url: URL)
```

### Route and host policy

Host policy must be explicit and centralized.

Required behavior:

* allow only configured primary hosts
* reject unknown hosts explicitly
* separate external-system schemes from internal allowed routes
* treat callback URLs as first-class supported routes
* never silently widen the allowlist in code review

Preferred helper shape:

```swift
struct HostPolicy {
    let allowedHosts: Set<String>
    let authCallbackSchemes: Set<String>

    func decision(for url: URL) -> NavigationDecision
}
```

### Navigation delegate rules

`WKNavigationDelegate` implementation must:

* allow known internal routes
* block unknown/unapproved hosts
* hand off external URLs explicitly
* map failures into `WrapperErrorState`
* preserve `lastAllowedURL` where useful for recovery

### UI delegate rules

If `WKUIDelegate` is used, it must be for legitimate shell concerns only:

* file chooser bridge
* JS alert/confirm/prompt handling if explicitly approved
* new-window handling mapped to policy

Do not use it to backdoor unsupported navigation behavior.

### Overlay rules

Overlays must be:

* state-driven
* temporary
* non-decorative
* removable after recovery

The controller must never leave stale overlays over interactive content after state recovery.

### Forbidden patterns

Reject changes that:

* inject CSS/JS for primary shell styling of hosted content
* hardcode production URLs outside `Environment`
* store secrets/tokens in the controller
* use implicit booleans instead of an explicit shell state model
* silently permit arbitrary hosts
* merge biometric policy into controller logic beyond orchestration calls

### Acceptance criteria

A compliant `WrapperViewController.swift` change must preserve:

* deterministic initial route loading
* explicit shell state transitions
* allowlist-based navigation
* recoverable error states
* explicit auth callback handling
* lock/re-entry orchestration without biometric-policy sprawl

---

## 3. BiometricAuth.swift contract

### Required type role
`BiometricAuth` must remain the single native policy/orchestration surface for biometric re-entry.

Preferred shape:
- value-free service object or lightweight final class
- wraps `LAContext` usage
- returns typed results rather than leaking framework-specific behavior across the app

Preferred declaration shape:
```swift
final class BiometricAuth
```

### Required result types

Use explicit result typing.

Preferred minimum:

```swift
enum BiometricAvailability {
    case available(BiometryKind)
    case unavailable
    case notEnrolled
    case lockedOut
}

enum BiometryKind {
    case faceID
    case touchID
    case none
}

enum BiometricAuthResult: Equatable {
    case success
    case cancelled
    case fallbackRequested
    case failed
    case unavailable
    case lockedOut
}
```

### Required policy model

Policy must be explicit and testable.

Preferred minimum:

```swift
struct BiometricPolicy: Equatable {
    let enabled: Bool
    let relockAfterSeconds: TimeInterval
    let requireImmediateLockOnBackground: Bool
    let invalidateOnBiometricSetChange: Bool
}
```

### Required method surfaces

`BiometricAuth.swift` should expose or implement equivalent methods for:

```swift
func availability() -> BiometricAvailability
func shouldRequireReentry(lastUnlockAt: Date?, now: Date) -> Bool
func authenticateForReentry(reason: String) async -> BiometricAuthResult
func invalidateProtectedStateIfNeeded() -> Bool
```

If async/await is not yet used in the codebase, a callback-based equivalent is acceptable, but the result type must still be explicit.

### LAContext handling rules

* create/use `LAContext` in a controlled boundary
* do not leak raw `NSError` handling across the controller layer
* map system outcomes into typed domain results
* support passcode fallback only when policy and UX require it
* do not loop-prompt after cancellation/failure

### Persistence boundaries

`BiometricAuth` may evaluate:

* last unlock timestamp
* local policy flags
* biometric-set invalidation markers

It must not persist:

* credentials
* raw session cookies
* unrelated app settings

### Required UX semantics

`BiometricAuth` must support:

* first availability check without prompting
* explicit re-entry prompt invocation
* cancellation as a recoverable outcome
* lockout/unavailable states separated from generic failure

### Forbidden patterns

Reject changes that:

* mix `LAContext` calls into `WrapperViewController`
* use untyped booleans for auth outcomes
* trigger prompt loops on foreground events
* treat unavailable biometrics the same as failed biometrics
* store credentials/tokens in biometric helpers

### Acceptance criteria

A compliant `BiometricAuth.swift` change must preserve:

* typed availability/results
* policy-driven re-entry decisioning
* controlled `LAContext` boundary
* no prompt-loop regressions
* clean separation from webview logic

---

## 4. Assets.xcassets contract

### Purpose
`Assets.xcassets` is the delivery surface for native shell assets. It must remain structured, minimal, and governed.

### Canonical source-of-truth
App icon source must live outside the catalog and render into it.

Preferred source:
```text
design/ios/app-icon/OdooWrapper.iconcomposer
```

Derived delivery surface:

```text
Sources/Assets.xcassets/AppIcon.appiconset
```

If the repo uses a different iOS root path, preserve the existing root and keep the same ownership model.

### Required asset catalog layout

Preferred structure:

```text
Assets.xcassets/
  AppIcon.appiconset
  AccentColor.colorset
  Shell/
    UnlockShieldBackground.colorset
    LoadingAccent.colorset
  Status/
    NetworkError.imageset
    AuthRequired.imageset
  Brand/
    Wordmark.imageset
```

### Naming rules

Use stable semantic names.

Allowed patterns:

* `AppIcon`
* `AccentColor`
* `Shell/*`
* `Status/*`
* `Brand/*`

Do not use:

* random export names
* timestamped names
* duplicated "final/final2/new" style names
* arbitrary vendor/source filenames as permanent catalog names

### SF Symbols rule

Prefer SF Symbols for native shell actions:

* refresh
* share
* browser handoff
* diagnostics
* lock/unlock
* settings
* retry

Do not create custom raster icons for standard shell actions unless a product-specific exception is documented.

### App icon rules

* one canonical editable source
* asset-catalog app icon is derived output
* appearance behavior must remain reviewable
* no separate unmanaged icon source in random folders

### Native-only illustration rules

Only allow custom illustrations/imagesets when they support native overlays such as:

* network error
* auth required
* locked shield
* empty diagnostic state

Do not mirror hosted Odoo module artwork inside native assets without a clear shell-level need.

### Color asset rules

Use asset colors for shell-level semantics only:

* accent
* shield background
* overlay backgrounds where needed

Do not use the catalog as an uncontrolled theme dump for hosted web content.

### Acceptance criteria

A compliant `Assets.xcassets` change must preserve:

* one canonical app icon source
* stable semantic asset names
* SF Symbols as default shell iconography
* minimal native-only asset scope

---

## 5. Required companion config

### Info.plist contract
If biometrics are enabled, `Info.plist` must include a clear Face ID usage string.

Required key when applicable:
- `NSFaceIDUsageDescription`

The string should describe real user value, for example re-entry protection for the app.

### Environment contract
`WrapperViewController` must consume environment configuration from `Environment.swift` or an equivalent dedicated environment surface.

It must not hardcode:
- base URLs
- auth callback schemes
- host allowlists by environment
- feature flags that belong to environment config

---

## 6. Code review reject conditions

Reject a change if it:
- adds hardcoded production routing into `WrapperViewController`
- spreads biometric prompt logic outside `BiometricAuth`
- introduces untyped shell state or auth outcomes
- drops ad hoc assets into `Assets.xcassets` without naming discipline
- bypasses explicit host allowlist logic
- makes the app icon source ambiguous
- uses custom raster symbols where SF Symbols should be used
- couples webview business routing to native shell logic

---

## 7. Definition of done

A code-level wrapper change is done only when:
- `WrapperViewController.swift` still owns shell orchestration cleanly
- `BiometricAuth.swift` still owns biometric policy/orchestration cleanly
- `Assets.xcassets` still follows governed naming and source ownership
- `Info.plist` and `Environment.swift` remain aligned with the shell contract
- the change is reviewable against explicit type/state/policy boundaries
