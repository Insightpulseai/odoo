# iOS Wrapper Code Contract (Canonical)

## Purpose
Reusable code contract for native iOS wrapper shell implementation files. Defines file ownership, type contracts, state models, and code review boundaries.

## File ownership

### WrapperViewController.swift
Owns: WKWebView construction/config, navigation delegation, route allowlist enforcement, loading/progress/error states, external URL handoff, download/upload coordination, auth callback restoration, foreground/background lifecycle reactions.

Does not own: biometric policy persistence, credential storage, hosted app business logic, app icon logic, hardcoded environment selection.

### BiometricAuth.swift
Owns: LocalAuthentication orchestration, re-entry gating policy, shield/unlock decision, biometric availability probing, fallback behavior, lock/unlock result typing.

Does not own: webview navigation, auth callback handling, session cookies/tokens, main content surface UI layout.

### Assets.xcassets
Owns: app icon delivery, accent color, native-shell-only branded assets, overlay state illustrations.

Does not own: hosted web content assets, duplicate icon variants outside canonical flow, unmanaged ad hoc raster assets.

## WrapperViewController contract
- Subclass of UIViewController, conforms to WKNavigationDelegate
- Explicit shell state model (booting, loading, ready, error, locked)
- Typed error states and lock reasons
- Deterministic initial route from Environment
- Allowlist-based host policy with centralized HostPolicy helper
- State-driven, temporary, non-decorative overlays
- No CSS/JS injection for shell styling, no hardcoded URLs outside Environment

## BiometricAuth contract
- Final class wrapping LAContext
- Typed availability (available/unavailable/notEnrolled/lockedOut)
- Typed auth results (success/cancelled/fallbackRequested/failed/unavailable/lockedOut)
- Explicit policy model (enabled, relockAfterSeconds, immediateBackground, biometricSetChange)
- No prompt loops, no untyped booleans, no LAContext leakage across controller

## Assets.xcassets contract
- Canonical app icon source outside catalog (Icon Composer)
- Asset catalog is derived delivery surface
- Semantic naming: AppIcon, AccentColor, Shell/*, Status/*, Brand/*
- SF Symbols for standard shell actions
- No random/timestamped/duplicate naming

## Companion config
- Info.plist: NSFaceIDUsageDescription when biometrics enabled
- Environment.swift: source of base URLs, callback schemes, host allowlists, feature flags

## Code review reject conditions
- Hardcoded production routing in WrapperViewController
- Biometric prompt logic outside BiometricAuth
- Untyped shell state or auth outcomes
- Ad hoc assets without naming discipline
- Bypassed host allowlist logic
- Ambiguous app icon source
- Custom raster symbols where SF Symbols should be used

## Applied contract
Repo-local version: `<project-repo>/docs/skills/ios-wrapper-code-contract.md`
