# iOS Native Wrapper Skill Pack

## Purpose
This skill pack governs native iOS wrapper applications that embed a hosted product surface (for example, Odoo via `WKWebView`) while preserving native-quality authentication, biometrics, release automation, testing, and runtime diagnostics.

## Scope
Use this skill pack when the repository contains or adds:
- an Xcode iOS target
- `WKWebView` or related embedded web runtime
- biometric access gating
- App Store / TestFlight distribution
- CI/CD for build, test, archive, or release

Do not use this skill pack for:
- Flutter / React Native / Capacitor-first apps
- fully native line-of-business apps with no embedded web surface
- macOS-only applications

---

## Canonical stack

### Required Apple frameworks
- `WebKit`
- `LocalAuthentication`
- `AuthenticationServices`
- `XCTest`
- `MetricKit`

### Required toolchain surfaces
- Xcode
- `xcodebuild`
- `xcrun simctl`
- `fastlane` (preferred for release automation)
- App Store Connect API authentication
- CI on macOS runners or Xcode Cloud

---

## Design authority

Use Apple's current design-system guidance as the authority for visual and interaction decisions in the iOS wrapper.

### Canonical references
- Apple Technology Overview: App design and UI
- Apple Technology Overview: Liquid Glass
- Apple Technology Overview: Adopting Liquid Glass
- Apple HIG: Materials
- Apple HIG: App icons
- Apple Design Resources
- Icon Composer
- SF Symbols 7
- Sample code: Landmarks — Building an app with Liquid Glass
- SwiftUI guidance: Applying Liquid Glass to custom views

### Interpretation for wrapper apps
For hosted-product wrappers (for example, Odoo in `WKWebView`):
- keep primary business content dominant; chrome should recede
- prefer native bars, sheets, popovers, and entry points over heavy custom web-shell chrome
- use Liquid Glass for app chrome and transient controls, not as decorative overlay noise
- move branding emphasis into content and app icon treatment rather than persistent heavy headers
- prefer clearer bottom/reachable navigation and compact top chrome where appropriate
- preserve comfortable tap targets, spacing, and clear interactive affordances
- use official icon pipeline (`Icon Composer`) and system iconography (`SF Symbols`) rather than custom inconsistent assets

### Wrapper-specific rules
- Do not attempt to visually "glassify" the hosted web content itself through arbitrary CSS overlays
- Apply native design language to the shell: navigation, sheets, menus, auth gates, alerts, upload/share actions
- Keep host web content readable and operational first; native styling should frame it, not compete with it
- Any Liquid Glass usage must improve hierarchy, focus, or ergonomics

---

## Skill modules

### 1. ios-build-release
#### Responsibilities
- Own scheme selection, build configuration, archive/export flow, and versioning policy
- Standardize simulator vs device build behavior
- Enforce deterministic archive settings
- Guard bundle identifier, signing style, and export options drift

#### Inputs
- Xcode project or workspace
- scheme name
- configuration (`Debug`, `Release`)
- export method (`app-store`, `ad-hoc`, `development`, `enterprise`)
- bundle identifier(s)

#### Outputs
- successful build
- archive artifact
- exportable `.ipa` where applicable
- reproducible CI logs

#### Acceptance criteria
- app builds successfully for simulator
- app archives successfully for iPhone device target
- version and build numbers are deterministic or policy-driven
- signing errors fail fast with actionable diagnostics

---

### 2. ios-test-runner
#### Responsibilities
- Run unit, integration, and UI automation suites
- Use Xcode test plans when present
- Collect test results, screenshots, and failure diagnostics
- Maintain a stable smoke path for wrapper login and shell load

#### Required baseline tests
- app launch
- wrapper root view render
- webview initial navigation
- auth handoff success path
- biometric unlock success path
- offline / unreachable-host error handling

#### Acceptance criteria
- all unit tests pass
- smoke UI test passes on current simulator target
- failures emit `xcresult` artifacts and screenshots
- no test relies on manual simulator interaction

---

### 3. ios-webview-wrapper
#### Responsibilities
- Configure `WKWebView` safely and predictably
- Own navigation policy, allowed hosts, external URL handling, and download/upload behavior
- Preserve cookies/session state only through approved pathways
- Intercept deep links and route them correctly
- Expose explicit error states for network, TLS, or auth issues

#### Guardrails
- do not allow unrestricted navigation to arbitrary hosts
- do not bypass ATS or TLS policy without documented exception
- do not store credentials in plaintext
- do not build custom auth flows inside injected JavaScript when system auth surfaces are available

#### Acceptance criteria
- allowlist-based host navigation is enforced
- external URLs open outside the wrapper when policy requires
- file upload/download flows function on device and simulator where supported
- webview state restoration behavior is defined and tested

---

### 4. ios-auth-biometrics
#### Responsibilities
- Gate sensitive sessions or app re-entry with Face ID / Touch ID / passcode fallback
- Define lock timing and re-auth policy
- Store only minimal session-unlock metadata locally
- Handle biometric unavailable / changed-enrollment / lockout cases

#### Acceptance criteria
- biometric prompt appears only for protected actions or re-entry conditions
- passcode fallback behaves correctly
- changed biometric enrollment invalidates protected state when policy requires
- failure modes are visible and recoverable

---

### 5. ios-web-auth-session
#### Responsibilities
- Prefer `ASWebAuthenticationSession` or equivalent system-supported auth surfaces for external identity flows
- Handle callback URLs, custom schemes, and universal links
- Transfer authenticated state back into the wrapper safely
- Avoid brittle login automation inside the webview

#### Acceptance criteria
- callback handling succeeds on simulator and device
- app returns to the intended post-login destination
- auth session cancellation is handled explicitly
- sign-out clears local protected state and invalid session surfaces

---

### 6. ios-ci-distribution
#### Responsibilities
- Define `fastlane` lanes or equivalent automation for build, test, beta, and release
- Use App Store Connect API keys instead of manual session-only release flows when possible
- Manage changelog/release note injection
- Publish to TestFlight with deterministic metadata

#### Acceptance criteria
- CI can run build + test without manual IDE interaction
- release lane can archive and upload to TestFlight
- signing secrets are injected from secure CI storage, not repo plaintext
- failed uploads produce actionable logs

---

### 7. ios-crash-triage
#### Responsibilities
- Parse and classify crash, hang, and performance diagnostics from `MetricKit`
- Group failures by app version / device / OS
- Identify wrapper-specific regressions such as webview hangs, auth loops, or startup deadlocks

#### Acceptance criteria
- crash diagnostics are retained per release
- top crash / hang classes can be summarized after a beta run
- release readiness includes a regression review of diagnostics

---

### 8. ios-signing-and-profiles
#### Responsibilities
- Validate team ID, bundle IDs, entitlements, provisioning profiles, and capabilities
- Detect signing drift early in CI
- Keep Debug/Release signing strategy explicit

#### Acceptance criteria
- signing configuration is documented and machine-checkable
- entitlements match enabled capabilities
- CI fails fast on missing or mismatched provisioning assets

---

### 9. ios-app-review-readiness
#### Responsibilities
- Review wrapper behavior against App Review risk areas
- Ensure permission prompts, privacy disclosures, account flows, and external links are defensible
- Flag "just a website in a shell" risks and require native value-add justification

#### Native value-add checklist
At least several of the following should be real and user-visible:
- biometric re-entry protection
- push notifications
- deep links / universal links
- file capture / upload integration
- secure auth handoff
- offline or degraded-state handling
- device-native sharing / document flows
- app-specific shell navigation and safeguards

#### Acceptance criteria
- privacy usage strings are present and accurate
- sign-in/out flows are reviewable and stable
- wrapper includes defensible native capabilities beyond simple website mirroring
- release notes include any reviewer-facing context needed

---

## Implementation contract

For concrete UI/shell rules, apply:
- `docs/skills/ios-wrapper-ui-contract.md`
- `docs/skills/ios-wrapper-code-contract.md`

This contract governs:
- `WrapperViewController`
- native shell chrome
- `BiometricAuth`
- auth callback/re-entry behavior
- app icon and shell symbol asset policy
- file-level code boundaries for `WrapperViewController.swift`, `BiometricAuth.swift`, and `Assets.xcassets`

---

## Repo operating rules

### Source-of-truth order
1. Xcode project/workspace and entitlements
2. this skill pack
3. CI workflow definitions
4. `Fastfile` / release automation
5. app-level README or runbook

### Mandatory implementation boundaries
- Keep auth policy in native code, not ad hoc JavaScript injection
- Keep biometric policy in native code
- Restrict webview navigation by explicit policy
- Keep secrets out of source control
- Make simulator smoke tests mandatory before beta/release promotion

### Preferred project structure
```text
web/mobile/
  OdooWrapper.xcodeproj
  Sources/
    AppDelegate.swift
    SceneDelegate.swift
    Environment.swift
    WrapperViewController.swift
    BiometricAuth.swift
    KeychainService.swift
    CameraCaptureBridge.swift
    OCRService.swift
    LiquidGlassTabView.swift
    GlassEffectComponents.swift
    Theme.swift
    Info.plist
  Tests/
  docs/
fastlane/
  Fastfile
.github/workflows/
  ios-ci.yml
```

---

## Definition of done

A wrapper app is not considered production-ready until all of the following are true:

* simulator build is green
* device archive is green
* smoke UI path is automated
* auth callback path is tested
* biometric policy is implemented
* signing is reproducible in CI
* TestFlight distribution is automated
* crash / hang diagnostics are reviewed after beta validation

---

## Non-goals

* building a cross-platform abstraction layer
* replacing native auth with brittle DOM scripting
* allowing unrestricted browsing through the wrapper shell
* maintaining parallel manual-only release processes
