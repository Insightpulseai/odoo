# Odoo Mobile iOS

Native SwiftUI iOS client for [Odoo ERP](https://erp.insightpulseai.com).

## Requirements

- Xcode 15.2+
- iOS 17.0+ target device or simulator
- Apple Developer account (for device builds and App Store)
- Ruby 3.2+ and Bundler (for Fastlane)

## Setup

```bash
# Clone repo
git clone https://github.com/Insightpulseai/odoo.git
cd odoo/apps/odoo-mobile-ios

# Open in Xcode via Swift Package
open Package.swift

# Install Fastlane dependencies (from repo root)
cd ../../
bundle install
```

## Configuration

Copy `.env.example` in the `fastlane/` directory and fill in:

| Variable | Purpose |
|----------|---------|
| `APP_STORE_CONNECT_API_KEY_ID` | App Store Connect API Key ID |
| `APP_STORE_CONNECT_API_KEY_ISSUER_ID` | Issuer ID for ASC API Key |
| `MATCH_GIT_URL` | Git repo URL for Fastlane match certificates |
| `MATCH_PASSWORD` | Encryption password for match repo |

## Building

```bash
# Run tests
fastlane ios test

# Build TestFlight beta
fastlane ios build_testflight

# Release to App Store
fastlane ios release_appstore
```

## Architecture

```
Sources/
├── App/
│   └── OdooMobileApp.swift      # @main entry point, AuthState, ContentView
├── Features/
│   ├── Auth/
│   │   ├── SSOAuthSession.swift  # ASWebAuthenticationSession → Odoo OIDC
│   │   └── TokenStore.swift      # Keychain access/refresh token storage
│   ├── Biometric/
│   │   └── BiometricGate.swift   # Face ID / Touch ID lock screen
│   ├── DocumentScan/
│   │   └── DocumentScanView.swift # VNDocumentCameraViewController + Odoo upload
│   ├── Offline/
│   │   └── OfflineQueue.swift    # CoreData action queue with sync-on-reconnect
│   └── Push/
│       ├── PushRegistration.swift # APNs token → Odoo server
│       └── DeepLinkRouter.swift   # Universal link → in-app navigation
└── Shared/
    ├── OdooClient.swift           # JSON-RPC /web/dataset/call_kw client
    └── NetworkMonitor.swift       # NWPathMonitor connectivity publisher
```

## Spec

See `spec/odoo-mobile/` for:
- `constitution.md` — non-negotiable constraints
- `prd.md` — product requirements
- `plan.md` — phased implementation plan
- `tasks.md` — task breakdown

## Advisor Workbook

The [Mobile Release Readiness workbook](/advisor/workbooks/mobile) in ops-console
evaluates 10 rules before App Store submission (CI green, match configured, ATS,
TestFlight group exists, crash-free rate, etc.).
