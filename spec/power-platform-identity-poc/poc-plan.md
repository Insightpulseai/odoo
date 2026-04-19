# Power Platform Identity PoC — Plan

Canonical source: this file.
Status: **proposed — awaiting go/no-go approval**.
Last updated: 2026-04-19.

## Purpose

Prove that the IPAI multi-tenant identity matrix ([`ssot/identity/saas-multitenant-identity-matrix.yaml`](../../ssot/identity/saas-multitenant-identity-matrix.yaml)) is implementable in code, using Power Platform as the PoC surface. Validates two things at once:

1. **Identity matrix** — 8 actors × 5 lanes × 9 scenarios can be modeled, instrumented, and governed.
2. **Power Platform as operational-admin surface** — does PP meet IPAI's requirements for internal ops workflows (NOT customer-facing product; Pulser-on-Odoo remains the product).

## What this PoC does NOT prove

- **Not** that Pulser for Odoo should run on Power Platform. Odoo CE remains canonical ERP per `CLAUDE.md`.
- **Not** that customer-facing Pulser agents should move to Copilot Studio. MAF on Foundry remains canonical runtime per [`agent_framework_adoption.yaml`](../../ssot/agent-platform/agent_framework_adoption.yaml).
- **Not** a reversal of `power-platform-adoption.yaml`'s bounded posture. This PoC is admin-operational, not product.

## Target tenant

**D365 Partner Sandbox tenant** (ISV Success benefit, already redeemed per [`isv-success-program-engagement.yaml`](../../ssot/governance/isv-success-program-engagement.yaml)). 25 seats, 0 assigned. Isolated from `insightpulseai.com` production tenant.

- Rationale: sandbox is explicitly designed for PoC / demo / discretionary use
- Zero production-data risk — sandbox tenant has no customer data
- Dataverse included — gives the PoC a relational data plane without provisioning Azure PG

## Scope (5 deliverables, kept small on purpose)

### D1 — Dataverse schema (identity matrix data model)

Tables:

- `IpaiTenant` — synthetic customer tenant records (Acme-demo, BigLaw-demo, TBWA-demo)
- `IpaiUser` — synthetic users spanning the 8 actor classes
- `IpaiRole` — role assignments per user per tenant
- `IpaiScenario` — which of the 9 scenarios each user falls into
- `IpaiAuditEvent` — simulated audit events per actor action

All records are synthetic. Naming: `*-demo` suffix. No real customer data.

### D2 — Power App (admin dashboard)

- Grid view of synthetic tenants
- Drill-down to users per tenant
- Scenario classification filter (S1–S9)
- Identity provider lane filter (L1–L5)
- Audit log timeline per user

**Not in scope**: customer self-service, marketplace integration, real auth.

### D3 — Power Automate flows (3 flows)

- **Flow 1**: Simulate SMB self-service signup (S3) → creates synthetic tenant record + admin user record + audit event
- **Flow 2**: Simulate IPAI inviting a guest (S2) → creates guest user with B2B-guest role + audit event
- **Flow 3**: Simulate cross-tenant isolation test → attempts user-A-reads-user-B-data → expected denial + audit event

### D4 — Copilot Studio agent (doctrine Q&A)

- Indexes the identity matrix YAML + parent identity SSOTs
- Answers natural-language questions: "Which lane does a customer admin with Okta use?" "What's the review cadence for guests?" "Is S9 enabled?"
- **Bounded to doctrine Q&A only** — does not mutate state, does not orchestrate real workflows. Validates Copilot Studio's retrieval capability over structured governance docs.

### D5 — Evidence pack

Location: `docs/evidence/<YYYYMMDD-HHMM>/pp-identity-poc/`

- Screenshots of each scenario execution
- Exported Dataverse table contents
- Flow run histories
- Copilot Studio conversation logs
- Cross-tenant isolation test results
- Lessons learned document — what Power Platform did well, what it didn't

## Non-goals

- No connection to production IPAI Entra tenant
- No connection to real customer data
- No Odoo integration (Pulser-on-Odoo is product, not PoC scope)
- No connection to Foundry (runtime is separate concern)
- No attempt to replace Pulser's MAF runtime with Copilot Studio

## Success criteria

| ID | Criterion | Target |
|---|---|---|
| POC-1 | All 5 deliverables complete in D365 sandbox | 100% |
| POC-2 | Cross-tenant isolation test (S9 disabled-by-default) passes | Isolation enforced |
| POC-3 | Copilot Studio answers 10 doctrine questions correctly | ≥ 80% accuracy |
| POC-4 | Evidence pack captures all 9 scenarios at least in synthetic form | 9/9 |
| POC-5 | Lessons learned document produced with explicit recommendation | Continue / expand / drop |

## Timeline (estimate)

- Day 1: D1 Dataverse schema + seed synthetic data
- Day 2: D2 Power App dashboard (canvas app, 3–4 screens)
- Day 3: D3 Power Automate flows + run simulations
- Day 4: D4 Copilot Studio agent setup + doctrine indexing
- Day 5: D5 evidence collection + lessons learned

**Total: ~5 days of focused PoC work**. Fits inside the 25 D365 sandbox seats + does not require Azure provisioning.

## Decision output

At end of PoC, decide:

- **Continue**: expand PP admin-ops surface for IPAI internal use (e.g. tenant provisioning dashboard, identity audit console)
- **Bounded reuse**: use PP for specific admin tasks (e.g. access reviews) but do not expand
- **Drop**: PP doesn't meet IPAI operational needs; stay with canonical Azure + custom UI

## Governance guardrails

- PoC artifacts live in D365 Partner Sandbox tenant **only**
- No data synchronization to production IPAI Entra tenant
- No production identity credentials used in sandbox
- PoC account identities are synthetic (`demo-*@acme-demo.ipai-demo.com`)
- Delete sandbox Dataverse tables at end of PoC if "Drop" is the decision

## Prerequisites before starting

- [ ] D365 Partner Sandbox tenant access confirmed (per `isv-success-program-engagement.yaml`)
- [ ] PoC owner designated (recommend: Jake as sole contributor for PoC scope)
- [ ] Review this plan + approve go/no-go
- [ ] Time-box explicitly (5 days — do not let scope creep)

## Related

- [Identity matrix SSOT](../../ssot/identity/saas-multitenant-identity-matrix.yaml)
- [Power Platform adoption doctrine](../../ssot/governance/power-platform-adoption.yaml)
- [Power Platform admin surface](../../ssot/governance/power-platform-admin-surface.yaml)
- [ISV Success program engagement](../../ssot/governance/isv-success-program-engagement.yaml)
- [SaaS tenancy model](../../ssot/governance/saas-tenancy-model-pulser-for-odoo.yaml)
