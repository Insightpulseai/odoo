# Implementation Plan — Odoo iOS Wrapper App

## 1. Delivery Strategy

Deliver V1 as a wrapper-first iOS shell over approved Odoo web/PWA routes.

Sequence:
1. shell + hosted route loading
2. auth/session persistence
3. deep links + push routing
4. upload/share/native bridges
5. denial-path and RBAC hardening
6. hosted workflow UAT for cash advance, OCR-backed expense, liquidation, approvals, and finance routes

## 2. Proposed Architecture

### Client Layer
- Native iOS shell
- WKWebView-hosted Odoo web/PWA
- secure local session storage
- biometric resume gate
- APNs push handling
- deep-link router
- camera/file/share bridge
- telemetry/crash instrumentation

### Hosted App Layer
- approved Odoo web/PWA routes
- mobile-compatible Odoo views and flows
- Odoo-side auth, ACLs, and business logic

### Backend Authority Layer
- Odoo backend as transactional and workflow authority
- audit and authorization enforcement
- hosted OCR/cash advance/liquidation/approval behavior

### Optional Future Extension Layer
- only if wrapper limitations require it:
  - narrow bridge services
  - notification broker
  - upload helper endpoints
  - mobile-specific route metadata
- these are not the primary V1 architecture

## 3. Workstreams

### WS-1 Spec, Route Inventory, and Scope Freeze
Outputs:
- approved route inventory
- route allowlist
- external-navigation policy
- wrapper-first acceptance boundaries

### WS-2 iOS Shell and Session Handling
Outputs:
- native shell
- WKWebView container
- session persistence
- biometric resume policy
- environment configuration

### WS-3 Push, Deep Link, and Route Resolution
Outputs:
- APNs routing model
- deep-link parser
- denial and fallback rules
- invalid target handling

### WS-4 Native Bridge Capabilities
Outputs:
- camera bridge
- file picker bridge
- share extension bridge
- attachment open/download helpers
- JS/native event contract

### WS-5 Security and Access Enforcement
Outputs:
- domain allowlist
- route denial behavior
- revoked-session handling
- Entra-to-role validation evidence
- service-identity non-interactive enforcement

### WS-6 Hosted Workflow Validation
Outputs:
- tested hosted paths for cash advance
- OCR-backed upload and review flows
- expense and liquidation paths
- approval and finance review routes
- route-level evidence pack

### WS-7 Telemetry, QA, and Release Evidence
Outputs:
- wrapper telemetry
- crash capture
- pulse pack
- click-all route coverage
- UAT pack
- release-readiness evidence

## 4. Technical Decisions

### Recommended V1 Baseline
- Native iOS shell
- WKWebView-hosted Odoo web/PWA
- wrapper-first doctrine
- secure local session persistence
- APNs routing
- domain allowlist
- JS/native bridge for upload/share/deep-link helpers
- no primary dependency on a mobile BFF
- no native business workflow replacement by default

### Visual Asset Baseline
- Icons: Fluent System Icons
- Avatars: DiceBear
- Illustrations: unDraw
- Optional richer onboarding/help illustrations: Storyset
- Design tokens and visual treatment should remain consistent with the broader Fluent design direction where applicable. Fluent documents token guidance and design assets across platforms, including iconography and tokens.

### Deferred
- native workflow replacements
- broad mobile-specific DTO/API contracts
- separate BFF-first mobile architecture
- Android client
- tablet-specific layouts
- autonomous mobile business actions

## 5. Route and Bridge Contract Principles

Every hosted route or bridge interaction must define:
- allowed origin/domain
- allowed persona/role scope
- expected route or target shape
- denial behavior
- error behavior
- telemetry events emitted
- user-visible fallback state

Representative surfaces:

### Hosted Route Classes
- `/web`
- approval inbox/detail routes
- expense/request routes
- cash advance and liquidation routes
- document/OCR intake routes
- finance review/exception routes

### Native Bridge Classes
- push notification open
- deep link open
- camera handoff
- file picker handoff
- share extension handoff
- biometric resume
- download/open helper

### Visual Surface Rules
- Wrapper-native controls must use the approved primary icon set
- Hosted Odoo extension surfaces, where customized, should prefer the same icon family for consistency
- Placeholder avatars in wrapper or hosted extension surfaces should use deterministic generated seeds
- Illustrations are allowed only for empty/help/onboarding/maintenance states and must not interfere with core transaction density

## 5A. Hosted Workflow Validation Targets

The wrapper must validate successful hosting of these workflow families:
- cash advance request, approval, issuance, outstanding monitoring
- OCR-backed receipt/invoice/document intake
- expense submission against advances
- liquidation submission and review
- overdue and exception handling
- approval inbox actioning
- finance settlement and closure routes

These remain hosted Odoo workflows, not native rebuilds.

## 5B. Lifecycle and State-Transition Matrix — Hosted Workflow Validation

The wrapper must respect and validate the hosted business state machines for:
- cash advance request, issuance, overdue, and closure
- OCR review before bind
- expense creation and approval
- liquidation submission, rework, approval, and settlement
- exception entry and resolution

The wrapper does not become the source of truth for these states; it must correctly host, route, display, and not bypass them.

## 6. Testing Strategy

### Wrapper Tests
- app launch and bootstrap
- hosted route open
- session persist/expire/recover
- domain allowlist enforcement
- external navigation handling
- biometric resume
- push/deep-link routing
- upload/share bridge correctness

### Hosted Workflow Tests
- cash advance request path
- OCR-backed receipt upload path
- expense submit path
- liquidation path
- finance exception path
- approval action path

### Access and Denial Tests
- denied route access
- hidden deep-link denial
- revoked-user/session denial
- service-principal interactive denial
- admin-read vs finance-mutate separation

## 6A. Cohesive Testing Strategy — Pulse, UAT, and Click-All Coverage

Testing must validate wrapper readiness across:
- shell and hosted route loading
- auth/session behavior
- push/deep links
- upload/share bridges
- hosted cash advance/OCR/expense/liquidation/approval flows
- denial paths
- accessibility and regression coverage

### Test Lanes

#### 1. Pulse Tests
Minimum pulse pack:
- app bootstrap loads
- authenticated user reaches allowed hosted route
- push/deep link resolves correctly
- camera/file upload handoff succeeds
- one hosted approval route opens
- one hosted cash advance route opens
- one hosted OCR-backed upload path works
- one hosted liquidation route is reachable
- denial path works for blocked finance route
- telemetry events are emitted

#### 2. Click-All Navigation Tests
Coverage includes:
- all wrapper-native controls
- all visible hosted entry points exposed by the app
- notification/deep-link entry paths
- upload/share launch actions
- retry/recovery actions
- blocked/hidden route attempts

Outcome classification:
- success
- blocked_by_policy
- expected_empty
- expected_disabled
- defect

#### 3. UAT Packs
Required UAT personas:
- employee / claimant
- approver / manager
- finance reviewer
- admin/support

Required UAT scenario families:
- cash advance request and approval
- receipt capture/upload and OCR review path
- expense submit against advance
- liquidation and rework
- overdue/exception review
- push-to-approval routing
- offline/reconnect recovery
- denial and revoked-session behavior

#### 4. Release Candidate Regression Pack
Must include:
- wrapper pulse pack
- click-all pack
- hosted workflow golden paths
- denial-path coverage
- upload/share bridge coverage
- push/deep-link routing
- telemetry/crash verification
- persisted session regression checks

### Test Evidence Doctrine
Each lane must produce:
- build/version
- environment
- persona
- scenario id
- route/target
- pass/fail outcome
- screenshots/videos where applicable
- logs/correlation IDs
- defect linkage if failed

### Exit Gates
A build cannot advance unless:
- pulse pack is green
- click-all pack shows no untriaged defects on primary routes
- hosted workflow UAT critical scenarios are signed off
- denial-path tests are green
- upload/share bridge evidence exists
- audit/correlation evidence exists for financially significant hosted actions

## 6B. Odoo iOS Test Matrix — Persona, Workflow, and Route Coverage

### Persona Set
- `employee_claimant`
- `manager_approver`
- `finance_reviewer`
- `admin_support`
- `svc_mobile_bff`
- `svc_scheduler`

### Outcome Classification
- `pass`
- `fail`
- `blocked_by_policy`
- `expected_denial`
- `expected_empty`
- `expected_disabled`

### Scenario Matrix

| Scenario ID | Persona | Workflow | Expected Result |
|---|---|---|---|
| AUTH-001 | employee_claimant | Sign in and session bootstrap | pass |
| AUTH-002 | manager_approver | Sign in and session bootstrap | pass |
| AUTH-003 | finance_reviewer | Sign in and session bootstrap | pass |
| AUTH-004 | admin_support | Sign in and session bootstrap | pass |
| AUTH-005 | removed/disabled user | Refresh token/session continuation | expected_denial |
| HOME-001 | employee_claimant | Open allowed hosted claimant route | pass |
| HOME-002 | manager_approver | Open allowed hosted approval route | pass |
| HOME-003 | finance_reviewer | Open allowed hosted finance route | pass |
| HOME-004 | admin_support | Open allowed hosted support route | pass |
| HOME-005 | employee_claimant | Open finance-only route by deep link | expected_denial |
| CA-001 | employee_claimant | Create hosted cash advance draft | pass |
| CA-002 | employee_claimant | Submit hosted cash advance request | pass |
| CA-003 | manager_approver | Approve hosted cash advance request | pass |
| CA-004 | finance_reviewer | Issue approved cash advance in hosted route | pass |
| CA-005 | employee_claimant | Attempt finance issuance action | expected_denial |
| OCR-001 | employee_claimant | Upload receipt image through bridge into hosted flow | pass |
| OCR-002 | employee_claimant | Confirm/correct OCR in hosted flow | pass |
| OCR-003 | employee_claimant | Attempt bind with unreviewed OCR | blocked_by_policy |
| EXP-001 | employee_claimant | Submit hosted expense | pass |
| EXP-002 | finance_reviewer | Link expense to cash advance in hosted flow | pass |
| LIQ-001 | employee_claimant | Submit hosted liquidation | pass |
| LIQ-002 | finance_reviewer | Finalize hosted settlement branch | pass |
| EXC-001 | finance_reviewer | View overdue/exception hosted queue | pass |
| NAV-001 | all human personas | Click-all traversal of visible wrapper and hosted entry paths | pass |
| OFF-001 | employee_claimant | Save/recover hosted work after reconnect where supported | pass |
| PUSH-001 | manager_approver | Open push notification into hosted approval route | pass |
| AUD-001 | finance_reviewer | Hosted mutation emits audit/correlation evidence | pass |
| RBAC-001 | employee_claimant | Employee sees only self-scope hosted records | pass |
| RBAC-005 | svc_mobile_bff | Interactive login attempt | expected_denial |
| RBAC-006 | svc_scheduler | Interactive login attempt | expected_denial |

Mandatory coverage must include:
- return_pending path
- reimbursement_pending path
- exact-close path
- overdue path
- duplicate receipt exception
- low-confidence extraction exception
- at least one denied route per human persona

## 7. Environments

- dev
- staging
- production

Each environment must define:
- hosted Odoo base URL
- allowed domains
- push/deep-link config
- telemetry config
- test/build audience controls

## 8. Security and Access Controls

- trusted-origin allowlist
- external-origin handling policy
- secure session storage
- revoked-user handling
- Entra-backed group and role mapping
- service identity non-interactive enforcement
- admin visibility separated from finance mutation authority

## 8A. Minimum Persona and RBAC Test Baseline

### Human Test Users
- 1 Employee / Claimant
- 1 Manager / Approver
- 1 Finance Reviewer
- 1 Admin / Support / Auditor

### Entra Groups
- ipai-mobile-employees
- ipai-mobile-approvers
- ipai-mobile-finance
- ipai-mobile-admins
- ipai-mobile-testers

### Service Identities
- svc_mobile_bff
- svc_scheduler

This is the minimum acceptable baseline to validate:
- claimant flows
- approval segregation
- finance issuance and settlement authority
- audit/support visibility
- Entra group-to-role mapping
- permission denial on hidden or blocked routes

## 8B. Entra Group to App Role Mapping

Identity authority is split as follows:
- Entra ID = user identity, group membership, app assignment
- wrapper/BFF layer if present = claim normalization and session context
- Odoo = business authorization and record-level enforcement

### Canonical Entra Groups
- `ipai-mobile-employees`
- `ipai-mobile-approvers`
- `ipai-mobile-finance`
- `ipai-mobile-admins`
- `ipai-mobile-testers`

### App Roles
- `employee_claimant`
- `manager_approver`
- `finance_reviewer`
- `admin_support`
- `test_access`
- `service_mobile_bff`
- `service_scheduler`

### Mapping Table

| Entra Group / Identity | App Role | Wrapper Scope | Odoo Permission Intent |
|---|---|---|---|
| `ipai-mobile-employees` | `employee_claimant` | claimant hosted routes | own requests, own expenses, own liquidation |
| `ipai-mobile-approvers` | `manager_approver` | approval hosted routes | approve/reject scoped records |
| `ipai-mobile-finance` | `finance_reviewer` | finance hosted routes | issuance, settlement, exception review |
| `ipai-mobile-admins` | `admin_support` | support/audit routes | read broad support surfaces, mutate only if explicitly granted |
| `ipai-mobile-testers` | `test_access` | test build access | no business privilege by itself |
| `svc_mobile_bff` | `service_mobile_bff` | non-interactive backend scope | orchestration only |
| `svc_scheduler` | `service_scheduler` | non-interactive job scope | reminders/escalations only |

### Claim Model
```json
{
  "sub": "entra-object-id",
  "upn": "user@company.com",
  "tenant_id": "entra-tenant-id",
  "groups": ["ipai-mobile-employees", "ipai-mobile-testers"],
  "app_roles": ["employee_claimant", "test_access"],
  "persona": "employee_claimant",
  "is_human": true,
  "is_service": false,
  "odoo_user_id": 123,
  "odoo_employee_id": 42,
  "session_id": "uuid",
  "device_id": "uuid"
}
```

### Mapping Rules

* app roles are derived server-side from group membership
* client-supplied role claims are never authoritative
* Odoo identifiers are resolved server-side
* `test_access` is additive only
* service identities must remain non-interactive
* admin/support visibility does not imply finance mutation authority

### Route Policy Matrix

| Route / Action                  | employee_claimant | manager_approver |                finance_reviewer |      admin_support |
| ------------------------------- | ----------------: | ---------------: | ------------------------------: | -----------------: |
| Open own hosted dashboard/route |             allow |            allow |                           allow |              allow |
| Submit cash advance request     |             allow |         optional |                        optional |           optional |
| Approve cash advance            |              deny |            allow |                        optional |    deny by default |
| Issue cash advance              |              deny |             deny |                           allow |    deny by default |
| Confirm own receipt OCR         |             allow |             deny | allow in finance review context |    deny by default |
| Review invoice OCR intake       |              deny |             deny |                           allow | read-only optional |
| Submit own expense              |             allow |             deny |                        optional |    deny by default |
| Link expense to advance         |              deny |             deny |                           allow |    deny by default |
| Submit liquidation              |             allow |             deny |               optional assisted |    deny by default |
| Finalize settlement             |              deny |             deny |                           allow |    deny by default |
| View audit/correlation traces   |          own only |      scoped only |                  scoped finance |    allow read-only |

### Denial Doctrine

Every route and action must support:

* authenticated but unauthorized denial
* hidden-route direct-link denial
* revoked-session denial
* non-leaky protected-record denial
* service-principal interactive denial

## 9. Milestones

### M1 — Shell Foundation

* wrapper spec freeze
* route inventory
* WKWebView shell
* environment config

### M2 — Session and Routing

* auth/session persistence
* biometric resume
* push/deep-link routing
* denial-path baseline

### M3 — Native Bridges

* camera/file/share helpers
* download/open helpers
* hosted route validation for upload-heavy flows

### M4 — Hosted Workflow Readiness

* cash advance, OCR, expense, liquidation, approval, finance route validation
* telemetry/crash evidence
* UAT signoff
* release readiness

## 10. Exit Criteria

V1 is release-candidate ready when:

* wrapper shell is stable
* session, push, deep link, and upload bridges are verified
* hosted critical workflows pass UAT
* denied routes behave correctly
* service identities are non-interactive
* telemetry/crash evidence is live
* release evidence pack is complete
