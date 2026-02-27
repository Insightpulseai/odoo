# Odoo Mobile iOS — Task Breakdown

## Phase 0 — Repository Skeleton

- [x] Create `apps/odoo-mobile-ios/Package.swift`
- [x] Create `Sources/App/OdooMobileApp.swift`
- [x] Create `Sources/Features/Auth/SSOAuthSession.swift` (stub)
- [x] Create `Sources/Features/Auth/TokenStore.swift` (stub)
- [x] Create `Sources/Features/Biometric/BiometricGate.swift` (stub)
- [x] Create `Sources/Features/DocumentScan/DocumentScanView.swift` (stub)
- [x] Create `Sources/Features/Offline/OfflineQueue.swift` (stub)
- [x] Create `Sources/Features/Push/PushRegistration.swift` (stub)
- [x] Create `Sources/Features/Push/DeepLinkRouter.swift` (stub)
- [x] Create `Sources/Shared/OdooClient.swift` (stub)
- [x] Create `Sources/Shared/NetworkMonitor.swift` (stub)
- [x] Create `fastlane/Fastfile`, `Appfile`, `Matchfile`, `.env.example`
- [x] Create `.github/workflows/ios-appstore.yml`
- [x] Create `docs/ops/ODOO_IOS_APP.md`
- [x] Create `docs/catalog/blueprints/odoo.ios-app.blueprint.yaml`
- [x] Create `docs/catalog/mobile.catalog.json`

## Phase 1 — Auth + Biometric
- [ ] Implement real OIDC flow in SSOAuthSession (requires Odoo OIDC endpoint URL)
- [ ] Implement Keychain operations in TokenStore
- [ ] Implement LAContext evaluation in BiometricGate
- [ ] Unit tests for TokenStore

## Phase 2 — Odoo Client + Offline Queue
- [ ] Implement OdooClient JSON-RPC calls
- [ ] Implement CoreData model for OfflineQueue
- [ ] Implement NWPathMonitor in NetworkMonitor
- [ ] Integration tests

## Phase 3–5
See plan.md for details.
