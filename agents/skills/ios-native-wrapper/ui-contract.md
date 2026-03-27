# iOS Wrapper UI Contract (Canonical)

## Purpose
Reusable UI contract for native iOS wrapper shells that host product content in `WKWebView` while applying Apple-native shell behavior for navigation, materials, auth, biometrics, and icon assets.

## Shell design principles
- The hosted web product is the primary content layer
- The native wrapper owns: app entry, shell navigation, auth handoff, biometric re-entry, file/document integration, external routing, transient progress/error states, native share/upload/system actions
- No persistent branded native header duplicating the hosted app header
- No decorative glass overlays directly on hosted HTML content
- No unrestricted browsing behavior
- No DOM-scripted auth as primary strategy

## WrapperViewController
- Single orchestration surface for WKWebView lifecycle, route policy, loading/error/lock states, external navigation handoff, file picker/upload/share, auth callback re-entry
- WKWebView fills available safe-area content region
- Overlays are temporary, dismissible, and state-driven
- Allowlist-based primary hosts with explicit external-host policy

## BiometricAuth
- Re-entry gating, LAContext orchestration, passcode fallback, lock timing
- No repeated prompt loops
- Shield fully obscures protected content during locked state
- Failure/cancel state must remain recoverable

## Native chrome
- Compact, no stacked top bars unless functionally required
- Prefer sheets/popovers/menus for native-only actions
- Preserve edge-to-edge content emphasis

## Auth handoff
- ASWebAuthenticationSession or approved equivalent for external identity flows
- Restore user to intended post-login destination
- Clear local protected state on sign-out

## App icon assets
- Icon Composer for multilayer authoring
- SF Symbols for native shell iconography
- One canonical source icon definition
- Xcode asset catalog as delivery surface

## Code review gates
Reject if it:
- adds persistent ornamental shell chrome
- treats Liquid Glass as decoration instead of functional material
- pushes auth back into brittle web scripting
- widens route permissions without explicit policy update
- introduces icon drift outside canonical pipeline

## Applied contract
Repo-local version: `<project-repo>/docs/skills/ios-wrapper-ui-contract.md`
