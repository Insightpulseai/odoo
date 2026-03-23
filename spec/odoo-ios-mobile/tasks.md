# Tasks — Odoo iOS Wrapper App

## Phase 0 — Spec Realignment and Scope Freeze
- [x] Approve wrapper-first Constitution, PRD, Plan, and Tasks bundle
- [x] Freeze wrapper-first doctrine: hosted Odoo remains primary workflow UX
- [x] Remove native-first assumptions from prior bundle
- [x] Define approved route inventory and domain allowlist
- [x] Define explicit non-goals for native workflow replacement in V1
- [ ] Adopt Asset Doctrine (Fluent System Icons, DiceBear, unDraw)

## Phase 0A — Asset Doctrine and Visual Standardization
- [ ] Standardize the primary icon system as Fluent System Icons
- [ ] Standardize generated avatars on DiceBear with deterministic seed rules
- [ ] Standardize default illustrations on unDraw
- [ ] Limit Storyset usage to onboarding, help, or marketing-style surfaces only
- [ ] Define no-mix icon rule for product UI
- [ ] Define avatar seed rules for users, tenants, and placeholder entities
- [ ] Define illustration allowlist surfaces: empty, onboarding, blocked, help, maintenance
- [ ] Validate finance-critical and approval-critical surfaces remain data-first rather than artwork-first

## Phase 1 — iOS Shell Foundation
- [x] Create native iOS wrapper project structure
- [x] Implement WKWebView shell
- [x] Implement environment configuration strategy
- [x] Implement hosted base-URL selection and route bootstrap
- [x] Implement shell loading, retry, offline, and generic error states

## Phase 2 — Auth and Session Handling
- [x] Implement approved auth/session bootstrap
- [x] Implement secure session persistence
- [ ] Implement session-expired and revoked-user recovery flows
- [x] Implement biometric resume/re-entry where policy-approved
- [ ] Validate logout and session-clear behavior

## Phase 3 — Push, Deep Link, and Route Governance
- [x] Implement APNs registration and notification intake
- [x] Implement deep-link parser and route resolver
- [ ] Implement domain allowlist and external navigation handling
- [ ] Implement hidden-route and unauthorized-route denial behavior
- [ ] Implement fallback behavior for invalid or stale route targets

## Phase 4 — Native Bridge Capabilities
- [ ] Implement camera handoff into hosted Odoo upload flows
- [ ] Implement file picker handoff into hosted Odoo upload flows
- [ ] Implement share extension into approved Odoo intake targets
- [ ] Implement safe attachment open/download helpers
- [ ] Define JS/native bridge contract and error mapping
- [ ] Add telemetry for all bridge launches and failures

## Phase 5 — Hosted Workflow Validation
- [ ] Validate hosted cash advance request routes
- [ ] Validate hosted approval routes
- [ ] Validate hosted OCR-backed receipt/invoice/document intake routes
- [ ] Validate hosted expense submission routes
- [ ] Validate hosted liquidation routes
- [ ] Validate hosted overdue and finance exception review routes
- [ ] Validate hosted settlement closure routes

## Phase 6 — Security, RBAC, and Denial Paths
- [ ] Provision 4 human test users: employee, approver, finance, admin/support
- [ ] Provision Entra groups for employees, approvers, finance, admins, and testers
- [ ] Provision service identities for wrapper backend/orchestration and scheduler if used
- [ ] Define server-side group-to-role derivation rules
- [ ] Define normalized session claim contract including Odoo user/employee resolution
- [ ] Validate denied access for out-of-scope routes/actions per persona
- [ ] Validate hidden-link denial and revoked-session denial
- [ ] Validate admin visibility vs finance mutation separation
- [ ] Validate service identities as non-interactive only

## Phase 7 — Pulse, UAT, and Click-All Coverage
- [ ] Define pulse test pack for bootstrap, hosted route open, upload bridge, push, denial, and telemetry
- [ ] Define click-all traversal inventory for wrapper controls and visible hosted entry paths
- [ ] Classify traversal outcomes as success, blocked_by_policy, expected_empty, expected_disabled, or defect
- [ ] Define UAT packs for employee, approver, finance, and admin/support personas
- [ ] Create golden-path UAT for request → approval → issuance → expense → liquidation → settlement
- [ ] Create exception-path UAT for overdue, duplicate receipt, low-confidence extraction, and amount mismatch
- [ ] Add offline/reconnect UAT where hosted workflows support recovery
- [ ] Add evidence capture contract for screenshots, logs, videos, and correlation IDs
- [ ] Define release gating thresholds for pulse, click-all, UAT, and regression packs

## Phase 8 — Telemetry, Evidence, and Release Governance
- [ ] Add wrapper telemetry instrumentation
- [ ] Add crash reporting instrumentation
- [ ] Validate correlation support for hosted business actions where available
- [ ] Build release-readiness evidence pack
- [ ] Publish production-readiness test matrix with signoff fields
- [ ] Validate production configuration isolation
- [ ] Publish known limitations of wrapper-first V1

## Phase 9 — Future Native Exception Assessment
- [ ] Identify hosted workflow pain points that wrapper-only V1 cannot solve adequately
- [ ] Define criteria for approving a native exception in later phases
- [ ] Document any candidate exception with explicit justification, cost, and risk
