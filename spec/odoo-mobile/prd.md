# Odoo Mobile iOS — Product Requirements

## Purpose

A native iOS client for Odoo that extends ERP productivity to mobile users, enabling secure access, document capture, offline task management, and push notifications without requiring a browser.

## Target Users

- Field staff and sales teams using Odoo on the go
- Finance approvers needing to review and approve records from iPhone
- Operations managers tracking project status and expense approvals

## 5 Native Capabilities

| # | Capability | Framework | Value |
|---|-----------|-----------|-------|
| 1 | **SSO Authentication** | `ASWebAuthenticationSession` → Odoo OIDC | Single sign-on; no password stored on device |
| 2 | **Biometric Gate** | `LocalAuthentication` (Face ID / Touch ID) | Secure app re-entry without re-auth |
| 3 | **Document Scan → Upload** | `VNDocumentCameraViewController` → `/api/v2/documents/` | Receipt and document capture without leaving the app |
| 4 | **Offline Action Queue** | CoreData | Queue mutations (approvals, expense entries) when offline; sync on reconnect |
| 5 | **Push Notifications + Deep Links** | APNs + Universal Links | Approve expense, view task, navigate to record directly from notification |

## Release Criteria

- [ ] TestFlight build passes on iPhone 14 and 15 Pro simulators
- [ ] All 5 native capabilities implemented (stubs acceptable for v0.1)
- [ ] Crash-free rate ≥ 99.5% after 100 TestFlight sessions
- [ ] Privacy Nutrition Labels complete and accurate
- [ ] App Store screenshots for 6.7" and 5.5" device sizes
- [ ] Fastlane `build_testflight` lane executes without manual steps
