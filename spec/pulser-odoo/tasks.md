# Tasks — Pulser for Odoo

Implementation roadmap for Pulser, tracking baseline ERP/AI work through SaaS platform readiness and the Go-Live Factory.

---

## Block 1: ERP and AI Foundation (Phases 1-32)

### Core ERP and IPAI Bridges
- [x] Integrate Odoo 18 CE + OCA stack.
- [x] Implement `ipai_finance_ppm` and `ipai_odoo_copilot`.
- [x] Configure Odoo Documents as the grounding vault.
## Phase 27 — Umbrella / child-bundle alignment

- [x] Register `pulser-project-to-profit` as the bounded Project Operations-derived child bundle
- [x] Register `pulser-record-to-report` as the bounded Finance-derived child bundle
- [x] Define the cross-bundle signal contract from Project-to-Profit to Record-to-Report
- [x] Define umbrella-owned cross-cutting rules that child bundles must inherit
- [x] Add Verify checks for child-bundle consistency with umbrella rules

## Phase 28 — Microsoft 365 optional channel surfaces

- [x] Define approved M365 channel-surface use cases for Project-to-Profit
- [x] Define approved M365 channel-surface use cases for Record-to-Report
- [x] Keep Teams / Outlook / Word / Excel surfaces behind canonical Pulser APIs
- [x] Ensure channel actions respect Pulser behavior matrix and RBAC
- [x] Ensure channel packaging/tooling does not become runtime authority

## Phase 29 — Microsoft 365 Declarative Agent packaging

- [x] Align M365 distribution model with Custom-Engine identity
- [ ] Create **Declarative Agent** manifest for Project-to-Profit (Teams/Outlook)
- [ ] Create **Declarative Agent** manifest for Record-to-Report (Teams/Outlook)
- [ ] Define **API Plugin** definitions for canonical project and finance actions
- [ ] Link M365 surfaces to `copilot_gateway.py` via authorized API Plugin bridges

## Phase 30 — Canonical Identity Alignment

- [x] Harmonize `constitution.md` with "custom-engine, policy-gated" identity
- [x] Harmonize `prd.md` with "system-of-action copilot" functional type
- [x] Normalize "One Core, Three Shells" terminology across Spec Kit
- [x] Verify multi-agent orchestration topology (Planner/Specialist/Validator)

### Azure AI and Reasoning
- [x] Provision Azure AI Foundry, OpenAI, and AI Search.
- [x] Implement specialist agents for AP, Tax, Close, and Reporting.

### Governance Baseline
- [x] **Phase 31 (P0)**: Execute IAM remediation and RBAC cleanup (`PULSER-IAM-GATE-01`).
- [x] Phase 32: Finance Ops Benchmark alignment (MB-500).

---

## Block 2: SaaS Platform and Scale (Phases 33-37)

### SaaS Control Plane (Ph 33)
- [x] SCP-01: Define SCP/TMP responsibility matrix.
- [x] SCP-02: Formalize 4-phase onboarding protocol.
- [x] SCP-03: Codify stamp rollout sequence.

### Deployment Stamps (Ph 34-35)
- [x] STMP-01: Define stamp architecture and isolation rules.
- [x] STMP-02: Implement multiple-revision Bicep module.
- [x] STMP-03: Create stamp promotion/rollout script.
- [ ] STMP-04: Verify multi-tenant isolation through smoke tests.

### Channel SDKs (Ph 37)
- [x] SHL-01: Formalize "One Core, Three Shells" architecture.
- [x] SHL-02: Define Microsoft Agents (Enterprise) integration contract.
- [x] SHL-03: Define GitHub Copilot (Internal) integration contract.

---

## Block 3: Scenario and Reporting Alignment (Phases 38-40)

### Office Benchmarks (Ph 38)
- [x] OFC-01: Formalize Office Studio functional requirements.
- [x] OFC-02: Map Office connectivity to Integration Capability Matrix.
- [x] OFC-03: Define Context-aware sidebar behavior for Enterprise Shell.

### E2E Business Scenarios (Ph 39-40)
- [x] BIZ-01: Map capabilities to Project-to-Profit and Record-to-Report.
- [x] BIZ-02: Formalize Accrual and Card Hygiene reporting logic.
- [x] BIZ-03: Align logic with SAP Concur benchmarks.

---

## Block 4: Go-Live Factory (Phases 41-44) [NEW]

## Phase 41: Implementation & Onboarding (BOM 12)
- [x] FACT-01: Formalize Go-Live Factory phases and activation gates.
- [x] FACT-02: Create implementation playbook for Project-to-Profit (80).
- [x] FACT-03: Create implementation playbook for Record-to-Report (90).

## Phase 42: Migration & Data Management (BOM 13)
- [x] MGR-01: Formalize Migration Inventory and Protocol.
- [x] MGR-02: Define conversion logic for analytic account mapping.
- [x] MGR-03: Codify cutover balance-validation routine.

## Phase 43: UAT and Cutover Controls (BOM 13)
- [x] UAT-01: Formalize Scenario-based UAT methodology.
- [x] UAT-02: Define Cutover Window Checklist (T-minus sequence).
- [x] UAT-03: Codify UAT sign-off and activation authorization log.

## Phase 44: Stabilization and First-Close (BOM 13)
- [x] STB-01: Formalize Stabilization Window and Hypercare protocol.
- [x] STB-02: Define First-Close Review and Sign-off criteria.
- [x] STB-03: Codify stabilization exit authorization log.

---

## Block 5: Persona and Governance (Phases 45-47) [NEW]
- [x] RBAC-01: Codify 5-layer Finance RBAC architecture.
- [x] RBAC-02: Map 12 canonical roles to cockpits and action scopes.
- [x] RBAC-03: Formalize evidence visibility and approval bands.

---

---

## Phase 50 — Finance RBAC Matrix Implementation
- [ ] RBAC-DET-01: Map Entra ID Role Groups for 12 canonical roles.
- [ ] RBAC-DET-02: Configure Approval Bands (A-E) in Odoo/Foundry logic.
- [ ] RBAC-DET-03: Implement Evidence Visibility Scopes (Self to Consolidated).
- [ ] RBAC-DET-04: Implement Agent Action Scope tool-call guards.
- [ ] RBAC-DET-05: Provision default Cockpits (Close, AP, Tax) based on role.
- [ ] RBAC-DET-06: Verify separation of Platform-Admin from Business-Approver.
- [ ] RBAC-DET-07: Verify Audit-Viewer read-only immutability.

---

## Phase 51 — Website & DNS Restoration [OPS]
- [x] OPS-DNS-01: Correct Front Door routing (Fix root redirect).
- [x] OPS-DNS-02: Update subdomain registry for standalone website.
- [ ] OPS-DNS-03: Verify NS delegation in Squarespace.
- [ ] OPS-DNS-04: Verify landing page 200 OK at root.

---

## Phase 52 — Entra Governance Baseline [SECURITY]

- [x] ENT-GOV-01: Add `ssot/identity/entra-governance-policy.yaml` (risk, PIM, governance scope SSOT). ✅ *Shipped 2026-04-16*
- [ ] ENT-GOV-02: Separate sign-in risk and user risk into distinct Conditional Access policies (RPB-01).
- [ ] ENT-GOV-03: Roll all risk policies out in report-only before switching to enforce (RPB-02).
- [ ] ENT-GOV-04: Exclude break-glass / emergency access accounts from all risk policies (RPB-03).
- [x] ENT-GOV-05: Define PIM baseline for privileged roles (JIT, eligible assignments, approval, MFA at activation). ✅ *Shipped 2026-04-16 — `ssot/identity/pim-role-baseline.yaml`*
- [ ] ENT-GOV-06: Verify emergency access account posture — two cloud-only Global Admin accounts, FIDO2/TAP MFA, no CA exclusion gaps, and pilot/rollback plan documented (PIM-06, PIM-07).
- [ ] ENT-GOV-07: Migrate legacy ID Protection risk policies to Conditional Access before 2026-10-01 retirement deadline.
- [ ] ENT-GOV-08: Execute PIM rollout — Phase 1 pilot (SG-IPAI-Admin) → Phase 2 all tier0/tier1 → Phase 3 access reviews. Blocked by: Entra P2 licensing.

---

*Last updated: 2026-04-16*
