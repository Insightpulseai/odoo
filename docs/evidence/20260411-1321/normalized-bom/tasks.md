# Tasks — Pulser for Odoo

Implementation roadmap for Pulser, tracking baseline ERP/AI work through SaaS platform readiness and the Go-Live Factory.

---

## Block 1: ERP and AI Foundation (Phases 1-32)

### Core ERP and IPAI Bridges
- [x] Integrate Odoo 18 CE + OCA stack.
- [x] Implement `ipai_finance_ppm` and `ipai_odoo_copilot`.
- [x] Configure Odoo Documents as the grounding vault.

### Azure AI and Reasoning
- [x] Provision Azure AI Foundry, OpenAI, and AI Search.
- [x] Implement specialist agents for AP, Tax, Close, and Reporting.

### Governance Baseline
- [/] **Phase 31 (P0)**: Execute IAM remediation and RBAC cleanup (`PULSER-IAM-GATE-01`).
- [ ] Phase 32: Finance Ops Benchmark alignment (MB-500).

---

## Block 2: SaaS Platform and Scale (Phases 33-37)

### SaaS Control Plane (Ph 33)
- [ ] Define service-level vs tenant-level plane responsibilities.
- [ ] Map control-plane logic into `agent-platform`.

### Deployment Stamps (Ph 34-35)
- [ ] Define stamp topology and tenant-to-stamp assignment rules.
- [ ] Implement ACA multi-revision label-based safe rollout.

### Channel SDKs (Ph 37)
- [ ] Align Microsoft Agents (Enterprise) and GitHub Copilot (Internal) shell boundaries.

---

## Block 3: Scenario and Reporting Alignment (Phases 38-40)

### Office Benchmarks (Ph 38)
- [ ] Implement high-fidelity Excel (Reconciliation) and Outlook (Collections) adapters.

### E2E Business Scenarios (Ph 39-40)
- [ ] Map all Pulser capabilities to Project to Profit and Record to Report scenarios.
- [ ] Implement SAP Concur-grade reporting for accruals and card hygiene.

---

## Block 4: Go-Live Factory (Phases 41-44) [NEW]

## Phase 41: Implementation & Onboarding (BOM 12)
- [ ] Define project space and onboarding wizard for new production tenants.
- [ ] Create implementation playbooks and scenario-based templates.
- [ ] Document team roles, milestones, and activation gates (SC-PH-16, 17).

## Phase 42: Migration & Data Management (BOM 13)
- [ ] Implement structured import/export and staging validation for tenant data.
- [ ] Define cutover strategy for open invoices, bills, and inventory (SC-PH-18).

## Phase 43: UAT and Cutover Controls (BOM 13)
- [ ] Execute scenario-based UAT with tenant sign-off (SC-PH-19).
- [ ] Implement mandatory balance reconciliation checks for AR, AP, and Trial Balance (SC-PH-20, 21).

## Phase 44: Stabilization and First-Close (BOM 13)
- [ ] Monitor first-month transactions and reconcile first-close activities.
- [ ] Execute performance review and stabilization sign-off (SC-PH-22, 34).

---

*Last updated: 2026-04-11*
