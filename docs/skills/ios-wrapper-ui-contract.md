# iOS Wrapper UI Contract

## Purpose
This document defines the implementation contract for native iOS wrapper shells that host product content in `WKWebView` while applying Apple-native shell behavior for navigation, materials, auth, biometrics, and icon assets.

This contract is subordinate to:
- `docs/skills/ios-native-wrapper.md`

---

## 1. Shell design contract

### Core rule
The hosted web product is the primary content layer.

The native wrapper owns:
- app entry
- shell navigation
- auth handoff
- biometric re-entry
- file/document integration
- external routing
- transient progress and error states
- native share / upload / system actions

### Disallowed patterns
- persistent branded native header that duplicates the hosted app header
- decorative glass overlays directly on hosted HTML content
- unrestricted browsing behavior
- DOM-scripted auth as the primary authentication strategy
- native chrome that obscures key hosted content

### Required shell behavior
- content-first layout
- restrained native chrome
- explicit host allowlist
- native handling for external URLs when policy requires
- visible loading/progress state
- recoverable network/auth error state
- consistent foreground re-entry behavior

---

## 2. WrapperViewController contract

### Responsibilities
`WrapperViewController` is the single orchestration surface for:
- `WKWebView` lifecycle
- route policy
- loading state
- error state
- external navigation handoff
- file picker / upload / share actions
- auth callback re-entry target restoration

### Required view hierarchy
Preferred hierarchy:

```text
WrapperViewController.view
  ShellContainerView
    WKWebView
    LoadingOverlayView
    ErrorOverlayView
    ReauthShieldView
```

### Layout rules
- `WKWebView` fills the available safe-area content region
- no permanent decorative overlay on top of the web content
- overlays are temporary, dismissible, and state-driven
- shell bars or controls must not materially reduce task space

### Loading state
Must support:
- initial app boot/loading state
- page transition state
- manual refresh/retry state
- timeout escalation to recoverable error state

### Error state
Required recoverable states:
- unreachable host
- TLS / connectivity failure
- auth required / expired session
- blocked route / unsupported host
- file operation failure

Every error state must expose:
- concise user-facing explanation
- retry action
- safe exit/back action where relevant

### Navigation policy
Must implement:
- allowlist-based primary hosts
- explicit external-host policy
- callback URL handling
- mailto/tel/maps/document handoff policy
- download interception policy
- upload picker integration policy

### Route ownership model
The wrapper may own only:
- launch route
- auth callback routes
- explicit native-only routes (settings, biometric unlock, diagnostics, about, etc.)

The hosted app owns:
- business navigation
- in-app record/detail routing
- application-specific workflow routes

### Acceptance criteria
- webview always starts with deterministic initial route
- blocked hosts never silently load
- external URLs open through explicit native/system handoff
- loading, timeout, and retry are testable without manual interaction
- error overlays are state-driven and removable after recovery

---

## 3. Native chrome contract

### Principle
Use native chrome only where it improves clarity, reachability, or safety.

### Required behavior
- keep chrome compact
- avoid stacked top bars unless functionally required
- prefer native sheets/popovers/menus for native-only actions
- prefer bottom/reachable action placement when actions are frequent
- preserve edge-to-edge content emphasis

### Typical native-only actions
- refresh
- share
- open in browser
- upload attachment
- scan/import document
- environment switcher
- diagnostics/support
- sign out / re-lock

### Acceptance criteria
- no redundant navigation layer competes with hosted app navigation
- shell actions are clearly native-only and scoped
- hosted content remains visually dominant

---

## 4. BiometricAuth contract

### Responsibilities
`BiometricAuth` owns:
- re-entry gating policy
- LocalAuthentication prompt orchestration
- passcode fallback behavior
- protected-state invalidation on biometric state change when enabled by policy
- lock timing rules

### Required policy surface
At minimum, support:
- biometric enabled/disabled flag
- foreground re-lock timeout
- immediate lock on backgrounding for sensitive mode
- changed-biometric-enrollment invalidation policy
- fallback behavior when biometrics unavailable or locked out

### UX rules
- do not prompt repeatedly in loops
- do not show biometric prompt before the app has enough state to know whether a protected session exists
- when locked, present a native shield over hosted content
- keep protected content obscured until unlock succeeds
- failure/cancel state must remain recoverable

### ReauthShieldView requirements
Must:
- fully obscure protected content
- show app identity + short unlock prompt
- offer retry
- offer fallback/cancel path where policy allows
- never leak prior page contents in screenshots during locked state where feasible

### Acceptance criteria
- foreground re-entry after timeout triggers reauth shield
- successful unlock restores prior state without forced full restart when possible
- failed or cancelled unlock leaves content protected
- changed biometric enrollment invalidates protected session when policy requires

---

## 5. Authentication handoff contract

### Required behavior
- use system-supported auth entry (`ASWebAuthenticationSession` or approved equivalent) for external identity flows
- restore user to intended post-login destination
- clear local protected state on sign-out
- treat auth-expired state distinctly from generic network failure

### Acceptance criteria
- auth callback round-trip works on simulator and device
- cancelled login is handled explicitly
- expired session yields recoverable auth-required state, not blank content

---

## 6. App icon asset contract

### Canonical tooling
- `Icon Composer` for multilayer app icon authoring
- `SF Symbols` for native shell action iconography
- Xcode asset catalog as delivery surface

### Required icon rules
- maintain one canonical source icon definition
- preserve light/dark/tinted appearance behavior where applicable
- avoid raster-only ad hoc icon variants as the design source of truth
- align shell action symbols to SF Symbols unless a product-specific symbol is justified

### Preferred asset structure
```text
web/mobile/
  Sources/
    Assets.xcassets/
      AppIcon.appiconset/
      AccentColor.colorset/
      Symbols/
docs/
  skills/
    ios-native-wrapper.md
    ios-wrapper-ui-contract.md
design/
  ios/
    app-icon/
      OdooWrapper.iconcomposer
      README.md
```

### Acceptance criteria
- app icon has one canonical editable source
- exported icon assets are derived from that source
- shell actions use SF Symbols by default
- icon behavior is reviewable for appearance-mode variants

---

## 7. Accessibility and ergonomics contract

### Required
- dynamic type does not break shell controls
- controls remain discoverable over variable backgrounds
- tap targets remain comfortable
- loading/error/reauth states are screen-reader reachable
- symbols have accessible labels where needed

### Acceptance criteria
- shell remains operable with larger text sizes
- core native actions are accessible via VoiceOver labels
- overlay states can be navigated without trapped focus

---

## Concrete code contract

For file-level implementation rules, apply:
- `docs/skills/ios-wrapper-code-contract.md`

This governs:
- `WrapperViewController.swift`
- `BiometricAuth.swift`
- `Assets.xcassets`
- supporting `Info.plist` and environment boundaries

---

## 8. Code review gates

A wrapper UI change should be rejected if it:
- adds persistent ornamental shell chrome
- treats Liquid Glass as decoration instead of functional shell material
- pushes auth back into brittle web scripting
- widens route permissions without explicit host-policy update
- introduces icon drift outside the canonical icon pipeline

---

## 9. Definition of done

A wrapper UI change is done only when:
- `WrapperViewController` state model remains explicit
- loading/error/lock states are test-covered
- biometric re-entry policy is documented and implemented
- host allowlist behavior is enforced
- icon/source asset changes preserve canonical source ownership
- the shell still makes hosted content primary
