# Partner Center Automation Matrix

## Status
Proposed

## Purpose
Define which Partner Center workflows should be:
- API-supported
- portal-first
- defer/manual

This matrix is repo-aware and maps each automation lane to the current Insightpulseai org structure.

> **Companion doc:** [`docs/runbooks/partner-center-integration.md`](../runbooks/partner-center-integration.md) covers Partner Center Lanes A (Partner Program), B (Marketplace Listing), C (Fulfillment + Metering Runtime). This matrix refines Lane B + Lane C with per-workspace automation decisions.

---

## Decision rules

1. Default to **official Microsoft APIs** where Partner Center exposes stable public coverage.
2. Default to **portal-first** where the workflow is workspace-driven, approval-heavy, or not clearly exposed by public APIs.
3. Default to **defer/manual** where the work is business-relationship, narrative, legal, or one-off activation work.
4. Do not build Partner Center automation in the Odoo repo.
5. Keep:
   - control-plane contracts in `platform`
   - jobs/runners in `automations`
   - secrets/identity/network in `infra`
   - agent/operator UX in `agent-platform`
   - reusable CI in `.github`
   - procedures/evidence in `docs`

---

## Canonical repo placement

| Concern | Canonical repo |
|---|---|
| API client contracts, schemas, SSOT, metadata | `platform` |
| Scheduled sync jobs, batch jobs, runbooks | `automations` |
| Azure identity, Key Vault, network, app registrations, deployment IaC | `infra` |
| Operator/assistant surfaces, retrieval, guided workflows | `agent-platform` |
| Reusable workflows / policy gates | `.github` |
| Operational docs, checklists, evidence, marketplace narrative | `docs` |

---

## A. API-supported

These are the only lanes that should be treated as strong candidates for programmatic automation now.

| Partner Center area | Typical workflows | Default mode | Canonical repo(s) | Automation shape | Notes |
|---|---|---|---|---|---|
| Marketplace offers | create/update products, plans, submissions, publish flow | API-supported | `platform`, `automations`, `.github`, `docs` | API client + declarative payloads + CI/manual release gate | Primary first-wave automation target |
| Marketplace offer assets/state sync | pull offer status, submission state, publication metadata | API-supported | `platform`, `automations` | poll/sync jobs + status snapshots | Keep as read-mostly until publishing flow is stable |
| Support requests | get/list/update service requests | API-supported | `platform`, `automations`, `docs` | thin API wrapper + status sync + evidence/log capture | Useful for tracking active Microsoft cases |
| CSP customer/account operations | customer accounts, profiles, agreements, domains, users | API-supported, but only if business motion requires it | `platform`, `automations` | thin wrappers; no UI-first duplication | Lower priority unless acting as CSP operator |
| Orders/subscriptions | carts, orders, subscriptions, upgrades, transitions | API-supported, but only if business motion requires it | `platform`, `automations` | workflow jobs + approval gates | Relevant for CSP-style resale motions, not immediate ISV publishing |
| Billing/report extraction | invoices, invoice summaries, utilization, price/rate data | API-supported | `platform`, `automations`, `data-intelligence` | scheduled ingestion + reporting extracts | Good candidate for reporting and ops visibility |

### API-supported implementation rule

For all API-supported lanes:

- secrets in Key Vault only
- auth/app registration in `infra`
- request/response contracts in `platform`
- batch or scheduled execution in `automations`
- human release/checkpoint workflow in `.github`
- operator documentation in `docs`

---

## B. Portal-first

These should stay portal-driven unless Microsoft later exposes a clear public API path that is worth operationalizing.

| Partner Center area | Typical workflows | Default mode | Canonical repo(s) | Why portal-first | Notes |
|---|---|---|---|---|---|
| Benefits workspace | activate credits, support plans, software benefits, sandbox benefits | portal-first | `docs` | activation is workspace-driven and program-governed | Track status in docs, not custom code |
| Membership workspace | enrollments, membership management, competency/program administration | portal-first | `docs` | approval/program lifecycle is portal-centric | Document state and owners only |
| Legal info / account verification | profile verification, legal changes, vetting | portal-first | `docs`, `infra` | sensitive compliance workflow, not a good first automation target | Infra may support identity evidence, but workflow remains manual |
| Security workspace | role review, security alert review, MFA/security posture tasks | portal-first | `docs`, `infra` | admin/security operations are high-risk and UI/policy driven | Automate evidence capture later, not control actions first |
| Referrals / co-sell workspace | lead review, co-sell opportunity handling | portal-first | `docs` | relationship-heavy workflow | Keep documented, not system-built |
| Partner Center AI assistant | contextual help, support navigation, workspace guidance | portal-first | `docs`, `agent-platform` | Microsoft already provides the assistant in-portal | Use it operationally; do not rebuild it |
| Marketplace editorial/legal completion | wording, screenshots, compliance fields, go-live review | portal-first | `docs`, `web` | content/legal decisions still need human review | Store prepared assets in repo, submit through portal/API as appropriate |

### Portal-first implementation rule

- prepare inputs in repo
- track status in repo
- execute the sensitive workspace action in Partner Center
- store evidence and follow-up notes in `docs`

---

## C. Defer/manual

These should not be automated in the current wave.

| Area | Typical workflows | Default mode | Canonical repo(s) | Why defer/manual | Notes |
|---|---|---|---|---|---|
| ISV Success engagement flow | orientation, EM coordination, advisory-session follow-up | defer/manual | `docs` | relationship/process work, not a system integration lane | Keep as brief/checklist/evidence |
| Benefit-blocker escalation | support escalation around blocked sponsorship/benefits | defer/manual | `docs` | case-by-case exception handling | API may help track a ticket, not resolve activation policy issues |
| Demo narrative and business summary | solution summary, business context, demo framing | defer/manual | `docs`, `web` | narrative packaging work | Repo should store the artifacts, not automate authorship blindly |
| Transactable vs non-transactable go/no-go | commercial packaging decision | defer/manual | `docs` | business decision, not automation | Record decision and rationale only |
| First publication readiness signoff | final business/legal/ops approval | defer/manual | `docs`, `.github` | requires human signoff | CI can gate inputs, not replace approval |

---

## Current-wave recommendation

### Build now

1. **Marketplace offer automation path**
   - start with read/write support for offer lifecycle and submission state
   - keep human publish gate

2. **Support request tracking**
   - list/read/update service request state for active Microsoft cases
   - sync into operational docs or internal status views

3. **Billing/report extraction**
   - only if it supports Marketplace or partner-ops visibility immediately

### Do not build now

- benefits activation automation
- membership automation
- legal verification automation
- co-sell/referrals automation
- custom replacement for Partner Center AI assistant

---

## Recommended repo execution split

| Workstream | Repo-ready location |
|---|---|
| Partner Center API client contracts | `platform/partner-center/` |
| Scheduled sync jobs / runners | `automations/partner-center/` |
| Azure app registration / secrets / deployment | `infra/azure/partner-center/` |
| Internal operator surface or assistant wrapper | `agent-platform/partner-center/` |
| Publication runbooks / benefit checklists / evidence | `docs/marketplace/` |
| CI gates for release readiness | `.github/workflows/` |

---

## Minimum viable automation backlog

### Phase 1
- marketplace-offer-state reader
- support-request status sync
- marketplace publication checklist and evidence model

### Phase 2
- marketplace submission/update writer
- billing/report ingestion for partner ops
- internal operator dashboard or assistant surface

### Phase 3
- CSP/customer/subscription automations only if business model requires them

---

## Final rule

Automate **Marketplace publishing and operational tracking** first.
Keep **benefits, membership, verification, and ISV Success relationship workflows** portal-first or manual until Microsoft exposes a clear, durable public automation path that is worth owning.

---

## Source basis

- Partner Center workspaces (APIs, Marketplace offers, Benefits, Membership, Help+support, Security, Referrals, Partner Center AI assistant): https://learn.microsoft.com/en-us/partner-center/
- Microsoft Marketplace submission API overview: https://learn.microsoft.com/en-us/partner-center/marketplace-offers/submission-api-overview
- Product Ingestion API (recommended modern path; SaaS, VMs, private offers, container offers, AI Apps and Agents preview): https://learn.microsoft.com/en-us/partner-center/marketplace-offers/product-ingestion-api
- Partner Center REST API scenarios (customer accounts, orders, subscriptions, support, billing): https://learn.microsoft.com/en-us/rest/api/partner-center-rest/

## Anchors

- **Companion runbook:** [`docs/runbooks/partner-center-integration.md`](../runbooks/partner-center-integration.md)
- **Auth model:** Memory `reference_partner_center_auth.md` — IPAI is ISV (not CSP/CPV) → app-only + certificate auth; MFA enforcement live 2026-04-01; no PAT tokens
- **Marketplace gap matrix:** [`ssot/azure/marketplace_readiness_gap_matrix.csv`](../../ssot/azure/marketplace_readiness_gap_matrix.csv)
- **Upstream adoption:** [`ssot/governance/upstream-adoption-register.yaml`](../../ssot/governance/upstream-adoption-register.yaml) §K Partner Center references
- **Doctrine:** `CLAUDE.md` § Engineering Execution Doctrine (build only the delta)
