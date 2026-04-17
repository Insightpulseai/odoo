# PRD — Odoo iOS Wrapper App

## 1. Product Summary

Build a production-grade iOS wrapper app for the existing governed Odoo web/PWA experience.

The app is a branded iPhone shell that hosts approved Odoo routes inside WKWebView and adds only the native capabilities that materially improve the mobile experience:
- push notifications
- deep links
- camera/file upload handoff
- share extension intake
- biometric resume
- secure session persistence
- telemetry/crash capture

This is not a full native Odoo mobile client in V1.

## 2. Problem Statement

Odoo web/PWA can be used on mobile, but the raw browser/PWA path often falls short on iPhone in ways that matter operationally:
- session/login behavior is less controlled than in a dedicated app shell
- push notification routing is weaker or inconsistent
- camera/file/share flows are less ergonomic
- deep linking into approved workflows is harder to govern
- crash/error evidence is weaker
- users want a branded, installable iOS surface with better operational stability

The opportunity is to improve the hosted Odoo mobile experience without rebuilding ERP workflows natively.

## 3. Product Goals

### Primary Goals
- Deliver a stable branded iOS shell for Odoo web/PWA
- Improve mobile login, resume, and deep-link reliability
- Improve receipt/invoice/document upload ergonomics on iPhone
- Support governed push notification routing into Odoo workflows
- Preserve Odoo as the sole transactional and workflow authority
- Create a wrapper foundation that can later host carefully approved native exceptions

### Non-Goals
- Full native reimplementation of Odoo workflows
- A new mobile BFF-first business application
- Duplicating Odoo approvals, expenses, liquidation, or finance flows natively in V1
- Parallel business logic or mobile-only ERP state
- Replacing Odoo as source of truth

## 4. Target Users

### Persona A — Employee / Claimant
Needs:
- stable access to mobile Odoo flows
- easier receipt/document upload
- deep links into requests, expenses, and liquidation
- reliable session resume on iPhone

### Persona B — Manager / Approver
Needs:
- open approval links from notifications
- stable access to approval inbox/routes
- fast route loading and reliable hosted actions

### Persona C — Finance Reviewer
Needs:
- access to issuance, OCR review, exception, and settlement routes in hosted Odoo
- reliable document handling
- traceable mobile-originated actions

### Persona D — Admin / Support / Auditor
Needs:
- visibility into route, session, audit, and error behavior
- deterministic denial paths and support diagnostics
- wrapper-level telemetry and crash evidence

## 5. V1 Scope

### In Scope
1. Native iOS shell application
2. WKWebView container for approved Odoo web/PWA routes
3. Session bootstrap and secure persistence
4. Biometric resume/re-entry gate where policy-approved
5. Domain allowlist and route governance
6. Push notification receipt and deep-link routing into Odoo
7. Camera and file picker bridge for hosted Odoo upload workflows
8. Share extension into approved Odoo intake flows
9. Attachment open/download helpers where safe and approved
10. Error, offline, session-expired, and recovery shell states
11. Telemetry, crash capture, and correlation support
12. RBAC-aware route denial and hidden-link denial behavior
13. Wrapper validation of hosted workflows including:
   - cash advance request
   - OCR-backed expense/document intake
   - liquidation submission
   - approval actions
   - finance review routes

### Explicitly Out of Scope for V1
- native dashboard replacement
- native expense forms
- native liquidation forms
- native approval inbox replacement
- native finance cockpit
- mobile-specific workflow engines outside hosted Odoo
- Supabase-backed mobile BFF as the primary V1 runtime
- broad mobile-only DTO/API surface unless forced by wrapper limitations

## 6. Key User Stories

### Employee
- As an employee, I want to open the iOS app and resume my Odoo session quickly so I can continue mobile work without repeated browser friction.
- As an employee, I want to upload receipts from camera, files, or share sheet into the correct hosted Odoo flow.

### Approver
- As an approver, I want to tap a push notification and land directly in the correct hosted approval route.

### Finance
- As a finance reviewer, I want hosted Odoo finance routes to work reliably in the app shell, including document-heavy flows.

### Admin / Support
- As support, I want wrapper telemetry, denial-path evidence, and crash traces so mobile issues can be diagnosed quickly.

## 7. Functional Requirements

### FR-1 iOS Shell Hosting
- Host approved Odoo web/PWA routes inside WKWebView
- Enforce domain allowlist and external-navigation handling
- Prevent untrusted navigation from silently opening inside the app shell

### FR-2 Authentication and Session Handling
- Support approved sign-in/session architecture
- Persist session securely
- Support session-expired recovery
- Support revoked-user and disabled-user denial paths

### FR-3 Deep Links and Push Routing
- Open push notification targets into governed Odoo routes
- Resolve deep links deterministically
- Deny or reroute unauthorized/invalid targets safely

### FR-4 Camera / File Upload Bridge
- Support launching camera or file picker from hosted flow context
- Return selected/captured file to the governed Odoo upload path
- Preserve safe attachment metadata and error handling

### FR-5 Share Extension Intake
- Support sharing supported files/images into approved Odoo destinations
- Require explicit route or intake target mapping
- Prevent ambiguous or unsafe share targets

### FR-6 Biometric Resume
- Support optional biometric gate for app resume/re-entry
- Never bypass server-side authorization because of biometric success

### FR-7 Attachment Open / Download Handling
- Support opening approved file types safely
- Enforce download/open policies
- Prevent unsafe executable handling

### FR-8 Hosted Workflow Validation
The wrapper must successfully host and validate key Odoo workflows, including:
- cash advance request and approval routes
- OCR-backed receipt/invoice/document upload flows
- expense submission routes
- liquidation routes
- finance exception/review routes

### FR-9 Error / Offline / Recovery States
- Show deterministic shell states for no-network, session expiry, blocked route, and unexpected host failure
- Provide safe retry and recovery actions

### FR-10 Telemetry and Audit Support
- Emit wrapper telemetry for launch, auth, route open, upload bridge usage, notification open, denial, and failure events
- Preserve correlation support for hosted business actions where available

## 8. Non-Functional Requirements

### NFR-1 Performance
- fast app launch and hosted route resume
- acceptable hosted page load on mobile network
- no excessive shell overhead over direct web use

### NFR-2 Reliability
- stable session persistence
- safe bridge retry behavior
- no silent upload loss
- predictable deep-link outcomes

### NFR-3 Security
- secure storage
- trusted-origin controls
- denial-path correctness
- no plaintext secrets in repo or app bundle

### NFR-4 Accessibility
- usable hosted viewport behavior
- accessible native shell controls
- predictable navigation and error messaging

### NFR-5 Observability
- structured wrapper telemetry
- crash capture
- route/open/error evidence
- correlation ID propagation where available

## 9. Data and Integration Requirements

### Canonical Request Path
iOS Wrapper → Hosted Odoo Web/PWA → Odoo Backend

### Native Bridge Responsibilities
- session persistence helpers
- push/deep-link routing
- upload/share handoff
- biometric gate
- telemetry/crash capture
- safe open/download helpers

### Odoo Responsibilities
- workflow rendering and business actions
- authentication/authorization outcomes
- approvals, expenses, OCR-backed intake, liquidation, and finance processing
- transactional and audit authority

### Optional Future Extensions
Any future use of a BFF or mobile-specific contract surface must be justified by a concrete wrapper limitation and separately approved.

## 10. UX Principles

- Wrapper-first, not redesign-first
- Hosted Odoo remains primary
- Native only where iOS materially improves the experience
- Safe routing over clever routing
- Fast resume over repeated login friction
- Reliable upload/share over custom native workflow sprawl
- Clear denial and recovery states
- Confidence-aware handling for OCR-backed hosted workflows
- Exception-first visibility for cash advance and liquidation review paths when surfaced in hosted Odoo
- One primary icon system across wrapper and hosted extension surfaces
- Deterministic generated avatars for placeholders, test users, and seeded identities
- Illustration use limited to empty, onboarding, blocked, help, or maintenance states
- No decorative illustration-heavy treatment inside finance-critical hosted workflows

## 10A. Visual Asset Standard

### Icons
The default icon system is Fluent System Icons, aligned to the broader Fluent design language and suited to product UI usage. Fluent’s iconography guidance defines system, product launch, and file icon collections for application use.

### Avatars
The default avatar system is DiceBear for deterministic generated avatars. DiceBear provides 30+ avatar styles and supports seed-based generation suitable for placeholders, demo tenants, and non-uploaded user identities.

### Illustrations
The default illustration source is unDraw for lightweight, brand-tintable empty-state and onboarding artwork. unDraw describes its library as open-source and supports customizable colors.

### Secondary Illustration Source
Storyset is approved only for richer onboarding, help, or marketing-style visual surfaces where customizable or animated illustrations add value. Storyset explicitly supports customization and downloadable illustrations.

### Asset Guardrails
- Product UI must not mix multiple primary icon systems
- Avatar generation must remain deterministic for placeholders and seeded identities
- Illustration usage must stay low-frequency and non-blocking
- Finance, approvals, OCR review, cash advance, liquidation, and settlement flows should remain data-first and action-first rather than artwork-first

## 11. Success Metrics

### Business Metrics
- increased mobile completion rate for approved hosted workflows
- reduced user friction for receipt/document upload
- improved push-to-action conversion for approvals
- reduced mobile session failure rate

### Product Metrics
- launch success rate
- session resume success rate
- deep-link success rate
- upload bridge success rate
- crash-free sessions
- hosted route load success rate

### Quality Metrics
- pulse pass rate for wrapper critical path
- click-all route coverage percentage across visible wrapper and hosted entry paths
- UAT pass rate for critical hosted business scenarios
- defect escape rate from staging/UAT to release candidate
- median time to detect route regression
- median time to recover from failed upload/session interruption

### Access Quality Metrics
- percentage of routes with explicit allow/deny policy coverage by persona
- time to revoke access after Entra disablement or group removal
- percentage of denied-route tests producing correct non-leaky behavior
- percentage of service identities verified as non-interactive
- percentage of business mutations attributable to a resolved human or service actor with correlation id

## 12. Risks

- hosted Odoo pages may still have mobile UX constraints the wrapper alone cannot solve
- route/deep-link governance may drift if Odoo routes change
- file upload bridge edge cases may vary across document types
- session behavior may differ between browser and wrapper contexts
- OCR quality remains dependent on document capture quality and hosted workflow design
- cash advance and liquidation complexity may expose hosted Odoo UX limits that later justify native exceptions

## 13. Open Decisions

- exact auth/session approach in wrapper context
- cookie/token handling constraints for hosted Odoo
- APNs payload-to-route mapping
- share extension target mapping
- exact offline/error-state strategy
- whether any specific hosted workflow needs a later native exception

## 14. Benchmark Doctrine — OCR and Cash Advance

The wrapper must successfully host workflows benchmarked against:
- Azure AI Document Intelligence for OCR/IDP capability
- SAP Concur Expense / ExpenseIt for receipt-led capture expectations
- SAP Concur Cash Advance for request, issuance, outstanding balance, and reconciliation expectations

In V1, these are hosted Odoo workflow validation targets, not native rebuild commitments.
