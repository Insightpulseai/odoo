# InsightPulse Expense — iOS App

Native iOS app for the SAP Concur replacement T&E + cash-advance flow.
WKWebView wrapper around the deployed expense-companion PWA, with native
services (biometric, camera, OCR, mileage, keychain, queue, push) bridged
to the web layer via a `window.__nativeBridge` JS shim.

## What it is

A native iOS shell — Swift / UIKit / SwiftUI (Liquid Glass on iOS 26+),
Xcode 16, deployment target iOS 16.0 — that loads the deployed PWA at
`https://ipai-expense-pwa.…azurecontainerapps.io/` and exposes platform
capabilities the browser can't reach:

| Native service | Bridge handler | What the PWA can do |
|---|---|---|
| `BiometricAuth` (Face ID / Touch ID) | `biometricAuth` | Approve expenses with biometric |
| `CameraCaptureBridge` | `captureReceipt` | Native camera with focus/flash |
| `OCRService` (proxies to PWA `/api/ocr/receipt`) | `ocrAnalyze` | Receipt extraction |
| `ReceiptQueueManager` | `queueReceipt`, `queuePending` | Offline-first capture |
| `MileageTracker` (CoreLocation) | `mileageStart`, `mileageStop`, `mileageStatus` | Concur Drive parity |
| `KeychainService` | `keychainSet`, `keychainGet` | Secure session storage |
| Haptics (`UIImpactFeedbackGenerator`) | `haptic` | Native feedback |

The PWA detects native context via `window.__nativeBridge.isNative === true`
and gracefully falls back to browser APIs otherwise.

## What it is not

- **NOT** a React Native / Expo / Supabase app. (An older README claimed that
  stack — it was wrong; nothing in `Sources/` uses RN or Supabase, and
  Supabase is fully deprecated per the org's CLAUDE.md.)
- **NOT** a standalone native app reimplementing the PWA's screens. UI lives
  in the PWA so we maintain one codebase across web + iOS + (future) Android.

## Tech stack

- Swift 5.9 / Xcode 16
- UIKit + SwiftUI (Liquid Glass on iOS 26+)
- WKWebView for content layer
- AppIntents for Siri Shortcuts (iOS 16+)
- BackgroundTasks for offline receipt sync
- CoreLocation for mileage
- LocalAuthentication for Face ID
- AuthenticationServices for Sign in with Apple
- UserNotifications for push

## Project structure

```
Sources/
├── AppDelegate.swift           # APNS, BG tasks
├── SceneDelegate.swift         # Window, Liquid Glass tab, biometric resume
├── WrapperViewController.swift # WKWebView host + JS bridge wiring
├── JSBridge.swift              # Native ↔ PWA message handlers
├── Environment.swift           # PWA URL config (dev/staging/prod)
├── BiometricAuth.swift         # Face ID / Touch ID
├── CameraCaptureBridge.swift   # UIImagePicker
├── OCRService.swift            # Proxies to PWA /api/ocr/receipt
├── ReceiptQueueManager.swift   # Offline receipt queue (Documents dir)
├── MileageTracker.swift        # CoreLocation distance tracking
├── KeychainService.swift       # Secure storage + SessionManager
├── BackgroundSyncService.swift # BGTaskScheduler — drains queue
├── AppleSignInService.swift    # Sign in with Apple (App Store guideline 4.8)
├── Shortcuts.swift             # AppIntents — "Hey Siri, log expense"
├── LiquidGlassTabView.swift    # iOS 26 native tab bar
├── GlassEffectComponents.swift # Liquid Glass UI primitives
├── Theme.swift                 # Design tokens
├── Info.plist                  # Permissions, scene manifest, BG tasks
├── OdooWrapper.entitlements    # APS, associated domains, app groups
└── PrivacyInfo.xcprivacy       # App Store privacy manifest
```

## Configuration

`Environment.swift` controls which PWA URL the wrapper loads:

| Env | URL |
|---|---|
| dev / staging / production | `https://ipai-expense-pwa.delightfuldesert-2840ce02.southeastasia.azurecontainerapps.io/` |

When `expense.insightpulseai.com` ships, point all envs at that domain and
keep the ACA URL as a fallback.

## Build

Requires Xcode 16, macOS 14+. Project is generated from `project.yml` via
[XcodeGen](https://github.com/yonaskolb/XcodeGen):

```bash
cd web/mobile
xcodegen generate
open OdooWrapper.xcodeproj
```

In Xcode, set your team (Signing & Capabilities), pick a tethered iPhone,
press ⌘R to sideload. For TestFlight, use Product → Archive.

## Bridge contract (PWA-side usage)

```ts
declare global {
  interface Window {
    __nativeBridge?: {
      isNative: boolean;
      biometricAuth: () => Promise<{ authenticated: boolean }>;
      captureReceipt: () => Promise<{ imageBase64: string }>;
      ocrAnalyze: (imageBase64: string) => Promise<ReceiptData>;
      queueReceipt: (imageBase64: string) => Promise<{ entryId: string }>;
      queuePending: () => Promise<{ pending: string[] }>;
      mileageStart: () => Promise<{ tracking: boolean }>;
      mileageStop: () => Promise<{ distanceMeters: number; distanceKilometers: number }>;
      mileageStatus: () => Promise<{ distanceMeters: number; distanceKilometers: number }>;
      keychainSet: (key: string, value: string) => Promise<{ ok: boolean }>;
      keychainGet: (key: string) => Promise<{ value: string | null }>;
      haptic: (style?: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => Promise<{ ok: boolean }>;
    };
  }
}

if (window.__nativeBridge?.isNative) {
  // Use native handlers — better UX, biometric, on-device queue
} else {
  // Browser fallback — getUserMedia, fetch, idb
}
```

## Permissions

All Info.plist usage descriptions are localized in plain English. Update
strings before localizing for non-English markets.

## App Store readiness

- ✅ Camera / Photo / Face ID / Location usage descriptions
- ✅ Sign in with Apple wired (AppleSignInService) — required by guideline 4.8
- ✅ PrivacyInfo.xcprivacy declared
- ✅ App Transport Security strict (no arbitrary loads)
- ✅ Push notifications (aps-environment)
- ✅ Universal Links (associated domains)
- ⏳ App icons + screenshots
- ⏳ Apple Developer Program enrollment + provisioning profile
- ⏳ TestFlight beta + App Store review

## Pairs with

- `web/apps/expense-companion-pwa/` — the PWA shipped at the URL this app loads
- `Insightpulse-ai/odoo` `addons/ipai/ipai_hr_expense_liquidation/` — backend
- See memory `project_pwa_concur_replacement_deployed_20260508` for context
