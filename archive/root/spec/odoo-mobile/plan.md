# Odoo Mobile iOS — Implementation Plan

## Phase 0 — Repository Skeleton (this PR)

- `Package.swift` — Swift Package manifest with no external dependencies
- `Sources/App/OdooMobileApp.swift` — `@main` App struct + ContentView routing
- All 5 feature stubs with `// TODO: implement` comments
- Fastlane configuration files (Fastfile, Appfile, Matchfile, .env.example)
- CI workflow: `.github/workflows/ios-appstore.yml`

## Phase 1 — Auth + Biometric

- Implement `SSOAuthSession.swift` (real OIDC flow)
- Implement `TokenStore.swift` (Keychain read/write)
- Implement `BiometricGate.swift` (LAContext evaluation)
- Unit tests for TokenStore Keychain operations

## Phase 2 — Odoo Client + Offline Queue

- Implement `OdooClient.swift` (JSON-RPC `/web/dataset/call_kw`)
- Implement `OfflineQueue.swift` (CoreData entity + sync logic)
- Implement `NetworkMonitor.swift` (NWPathMonitor)
- Integration test: queue + sync round-trip

## Phase 3 — Document Scan

- Implement `DocumentScanView.swift` (VNDocumentCameraViewController sheet)
- Wire scan result to `OdooClient` document upload endpoint
- Unit test: image compression before upload

## Phase 4 — Push + Deep Links

- Implement `PushRegistration.swift` (APNs token registration to Odoo server)
- Implement `DeepLinkRouter.swift` (universal link → in-app navigation)
- Configure `apple-app-site-association` on Odoo server (documented, not automated)

## Phase 5 — App Store Submission

- Run Mobile Release Readiness workbook (`/advisor/workbooks/mobile`)
- Complete Privacy Nutrition Labels
- Submit to TestFlight via `fastlane build_testflight`
- Submit to App Store via `fastlane release_appstore` after external beta
