# iOS Native Wrapper Skill

## Purpose
Reusable agent skill for native iOS wrapper applications that embed a hosted product surface (e.g., Odoo via `WKWebView`) while preserving native-quality authentication, biometrics, release automation, testing, and runtime diagnostics.

## Scope
Use this skill when a repository contains or adds:
- an Xcode iOS target
- `WKWebView` or related embedded web runtime
- biometric access gating
- App Store / TestFlight distribution
- CI/CD for build, test, archive, or release

Do not use for Flutter / React Native / Capacitor-first apps, fully native LOB apps, or macOS-only applications.

## Skill modules

| # | Module | Owns |
|---|--------|------|
| 1 | ios-build-release | scheme, config, archive, versioning |
| 2 | ios-test-runner | unit, UI, smoke tests, xcresult |
| 3 | ios-webview-wrapper | WKWebView config, navigation policy, host allowlist |
| 4 | ios-auth-biometrics | Face ID / Touch ID, re-entry gating, lock policy |
| 5 | ios-web-auth-session | ASWebAuthenticationSession, callback handling |
| 6 | ios-ci-distribution | fastlane, TestFlight, API key auth |
| 7 | ios-crash-triage | MetricKit, crash/hang classification |
| 8 | ios-signing-and-profiles | team ID, entitlements, provisioning |
| 9 | ios-app-review-readiness | App Review risk areas, native value-add |

## Design authority
- Apple's current App design and UI / Liquid Glass guidance
- `Icon Composer` for multilayer app icon authoring
- `SF Symbols 7` for native shell iconography

## Contract chain
This skill is the reusable org-wide definition. Repo-local applied contracts live in the target project repo:

```text
<project-repo>/docs/skills/
  ios-native-wrapper.md          # applied skill pack
  ios-wrapper-ui-contract.md     # UI/shell rules
  ios-wrapper-code-contract.md   # file-level code boundaries
```

## Canonical stack
- WebKit, LocalAuthentication, AuthenticationServices, XCTest, MetricKit
- Xcode, xcodebuild, xcrun simctl, fastlane
- App Store Connect API, CI on macOS runners or Xcode Cloud

## Mandatory boundaries
- Auth policy in native code, not ad hoc JavaScript injection
- Biometric policy in native code
- Webview navigation restricted by explicit policy
- Secrets out of source control
- Simulator smoke tests before beta/release promotion
