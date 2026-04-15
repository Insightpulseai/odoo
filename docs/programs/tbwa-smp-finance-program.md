# TBWA\SMP Finance Transformation — OKR + PPM Plan

> **Status:** `TEMPLATE` — tenant is in `prospect` state per [`ssot/tenants/tenants-registry.yaml`](../../ssot/tenants/tenants-registry.yaml). No contract signed, no directory imported, no D365 audit run. Flip to `ACTIVE` only after contract + first data audit.
>
> **Template source:** [`_PROGRAM_OKR_TEMPLATE.md`](./_PROGRAM_OKR_TEMPLATE.md)
> **Structure:** PMBOK 7th ed + Clarity PPM OKR cookbook + Logframe
> **Locked at:** 2026-04-15 (as template)
> **Sponsor:** Jake Tolentino (IPAI), <TBWA\SMP CFO TBD>
> **Program ID:** `tbwa-smp-finance-transformation`
> **Tenant:** `TBWA_SMP` (company_id=4) — see [`ssot/tenants/tbwa-smp/identity.yaml`](../../ssot/tenants/tbwa-smp/identity.yaml)

---

## 0. What's ground-truth in this document vs what's TEMPLATE

| Ground-truth | Source |
|---|---|
| R2 / R3 / R4 ship dates | [`project_acceleration_plan_20260414.md`](../../.claude/projects/-Users-tbwa-Documents-GitHub-Insightpulseai/memory/project_acceleration_plan_20260414.md) |
| 14 BIR form list (1601-C, 0619-E, 2550-M, 2307, 2550-Q, 1601-FQ, 1702-Q, SLSP, 1702, 2316, 1604-CF, 1604-EC, eAFS, 0605) | [`ssot/domain/tax_bir_inventory.yaml`](../../ssot/domain/tax_bir_inventory.yaml) + [`project_bir_eservices_matrix.md`](../../.claude/projects/-Users-tbwa-Documents-GitHub-Insightpulseai/memory/project_bir_eservices_matrix.md) |
| 6 `ipai_bir_*` modules | `addons/ipai/` directory |
| Odoo models (`project.project`, `project.task`, `account.analytic.line`, `account.move`, `res.company`, `hr.expense`) | Odoo CE 18 core |
| Tenant stub | [`ssot/tenants/tbwa-smp/identity.yaml`](../../ssot/tenants/tbwa-smp/identity.yaml) |
| Two-plane doctrine (D365 Finance + Copilot Finance agents) | [`feedback_d365_two_plane_doctrine.md`](../../.claude/projects/-Users-tbwa-Documents-GitHub-Insightpulseai/memory/feedback_d365_two_plane_doctrine.md) |
| D365 displacement posture (not development) | [`feedback_d365_displacement_not_development.md`](../../.claude/projects/-Users-tbwa-Documents-GitHub-Insightpulseai/memory/feedback_d365_displacement_not_development.md) |

| TEMPLATE (needs real input before ACTIVE) | Unblocked by |
|---|---|
| Contract date, billing model, SOW scope | Private-offer contract signed with TBWA\SMP |
| CFO name, controller name, CPA firm | Introduction meeting |
| TIN, RDO, primary domain, legal entity count | Client directory + BIR registration sharing |
| Productivity lift target (%, hours baseline) | D365 timesheet baseline month of cutover |
| Chart-of-account mapping specifics | D365 MainAccount export |
| Specific risk probabilities / impacts | Kickoff workshop risk-rating session |
| Specific KR target dates between R2 / R3 / R4 | Work-plan workshop with TBWA delivery team |
| Confidence scores per KR | Sponsor + delivery team scoring at kickoff |

Everywhere below, placeholder tokens are `<…>`. Do not interpret a placeholder as a commitment.

---

## 1. Program charter

```yaml
purpose: >
  Replace TBWA\SMP's D365 Finance + related back-office surface with IPAI's
  Odoo CE 18 + OCA + ipai_* + Pulser Copilot stack, shipped as a private-offer /
  services-led engagement. Land the PH Close + BIR Compliance Pack as a
  productized deliverable.

objective: >
  TBWA\SMP operates month-end close + BIR filings entirely on IPAI stack,
  with CFO sign-off, audit-complete evidence, and measurable productivity lift.

success_criteria: >
  Defined after kickoff workshop. Must meet all 4:
    1. CFO sign-off on private-offer SOW
    2. Historical data reconciles to D365 baseline (A.M4)
    3. 2026 fiscal year close + BIR filings from IPAI with CPA acceptance
    4. Measured finance productivity lift vs D365 baseline (target set at kickoff)

duration: <ISO start after contract> → <ISO end; target 2027-Q1>
budget:   TBD on contract
approach: Private-offer + services-led delivery. Two planes per doctrine —
          ERP Displacement + Copilot Finance agents. Do not conflate.
non_goals:
  - SAP / Ariba procurement integration (scope exclusion)
  - E-invoicing adoption (separate BIR program, deferred)
  - Multi-country expansion (PH only per data-intelligence vertical doctrine)
  - Auto-submission of BIR filings without human review
  - Acquisition of TBWA\SMP data beyond engagement scope
```

---

## 2. Stakeholder register (RACI)

| Role | Name | Responsibility | RACI |
|---|---|---|---|
| Program Sponsor | Jake Tolentino | Accountable — program success | A |
| Client Sponsor (TBWA) | `<CFO TBD>` | Accountable — TBWA-side decisions | A |
| Delivery lead (IPAI) | `<TBD>` | Responsible — solution engineering + migration | R |
| Finance SME (client) | `<Controller TBD>` | Responsible — domain + workflow validation | R |
| Technical lead (IPAI) | `<TBD>` | Responsible — Odoo architecture + integrations | R |
| External CPA | `<Firm TBD>` | Consulted — annual audit + eAFS sign-off | C |
| Tax advisor | Tax Guru (Pulser) + `<external counsel TBD>` | Consulted — BIR interpretation | C |
| Legal (client) | `<TBD>` | Consulted — NDA + contract | C |
| Holding group (TBWA) | `<TBD if applicable>` | Informed — consolidation implications | I |

**Exactly one `A` per row of responsibility.** Two `A`s above (program sponsor + client sponsor) is intentional — shared accountability, split domains. Conflicts resolve via escalation clause in contract.

---

## 3. OKRs

### Objective O.1 — IPAI stack becomes TBWA\SMP's system of record for finance by R4 GA

**3–5 KRs (TEMPLATE — target dates inside R2–R4 fill at kickoff):**

- **KR-1.1** Complete `res.company` + PH chart-of-accounts + fiscal calendar + BIR compliance register for `company_id=4` by `<A.M2 date>`.
- **KR-1.2** Achieve 100% line-level reconciliation of D365 historical GL/AP/AR/vendor/customer master against Odoo after migration by `<A.M4 date>`.
- **KR-1.3** Run first parallel monthly close (D365 authoritative, Odoo shadow) by **2026-07-14 (R2)**.
- **KR-1.4** Flip to Odoo-authoritative close for 2026-Q3 by **2026-10-14 (R3)**.
- **KR-1.5** Decommission D365 Finance; Odoo is SoR by **2026-12-15 (R4 GA)**.

### Objective O.2 — Monthly close + BIR compliance runs end-to-end on IPAI with audit-grade evidence

- **KR-2.1** Generate + file first month of BIR compliance from IPAI (1601-C + 0619-E + 2550-M + 2307 issuance) for June 2026 period, 100% with evidence pack, by `<B.M4 date ≈ R2>`.
- **KR-2.2** File 2026-Q3 quarterly BIR (2550-Q + 1601-FQ + 1702-Q + SLSP) from IPAI with evidence by **2026-10-14 (R3)**.
- **KR-2.3** File annual 2026 BIR (1702 + 2316 + 1604-CF + 1604-EC + eAFS + 0605 + registration renewal) from IPAI with CPA sign-off by `<A.M11 date ≈ 2027-04-15>`.
- **KR-2.4** Tax Guru preflight invocation rate ≥ `<target set at kickoff>` on BIR filing Stories; 100% of preflight outputs reviewed by human before submission.

### Objective O.3 — Zero regulatory penalty + zero material audit finding across the engagement

- **KR-3.1** Zero BIR filings submitted late during engagement (tracked via `ipai_bir_tax_compliance` register).
- **KR-3.2** Zero "material" audit findings on IPAI-generated statements from 2026 annual audit.
- **KR-3.3** 100% evidence pack compliance per filing (filed PDF + acknowledgment + payment receipt + GL reconciliation attached to Boards Story).

### Objective O.4 — Deliver measurable productivity lift vs D365 baseline

- **KR-4.1** Capture D365 finance-team hours-per-close baseline before cutover (target: full month of timesheet data).
- **KR-4.2** Achieve productivity lift target `<% set at kickoff>` measured via `account.analytic.line` finance-task hours per close cycle, rolling 3-month average.
- **KR-4.3** `<optional 3rd KR>` — e.g. close-cycle days reduced from baseline by `<target>`, set at kickoff.

**Total: 4 Objectives, 15 KRs** (within the 6–20 band).

---

## 4. WBS + milestone alignment (PMBOK)

> Dates marked `<R2>`, `<R3>`, `<R4 GA>` are **ground-truth ship gates** from the acceleration plan. All other dates fill at kickoff.

| WBS code | Deliverable | Parent | Milestone | Target date | KR link | Owner |
|---|---|---|---|---|---|---|
| 1.0 | ERP Displacement (Project A) | root | — | — | — | Delivery lead |
| 1.1 | Contract + SOW signed | 1.0 | A.M1 | `<TBD>` | KR-1.1 | Sponsor |
| 1.2 | Company + CoA live | 1.0 | A.M2 | `<TBD>` | KR-1.1 | Delivery lead |
| 1.3 | Data-migration plan + pilot | 1.0 | A.M3 | `<TBD>` | KR-1.2 | Technical lead |
| 1.4 | Historical import reconciled | 1.0 | A.M4 | `<TBD>` | KR-1.2 | Technical lead |
| 1.5 | Parallel close June 2026 | 1.0 | A.M5 | **2026-07-14 (R2)** | KR-1.3 | Controller + Delivery lead |
| 1.6 | Parallel close July–Aug | 1.0 | A.M6 | `<TBD>` | KR-1.3 | Controller |
| 1.7 | Sep 2026 close IPAI only | 1.0 | A.M7 | **2026-10-14 (R3)** | KR-1.4 | Controller |
| 1.8 | D365 non-renewal notice | 1.0 | A.M8 | `<TBD>` | KR-1.5 | Client sponsor |
| 1.9 | D365 decommissioned | 1.0 | A.M9 | **2026-12-15 (R4 GA)** | KR-1.5 | Technical lead |
| 1.10 | 2026 annual close from IPAI | 1.0 | A.M10 | `<TBD ≈ 2027-01-31>` | KR-2.3 | Controller |
| 1.11 | CPA sign-off; audit closed | 1.0 | A.M11 | `<TBD ≈ 2027-04-15>` | KR-2.3, KR-3.2 | CPA + Controller |
| 2.0 | BIR Compliance Operations (Project B) | root | — | — | — | Delivery lead |
| 2.1 | Baseline current BIR posture | 2.0 | B.M1 | `<TBD>` | KR-2.1 | Controller |
| 2.2 | 6 `ipai_bir_*` modules installed | 2.0 | B.M2 | `<TBD>` | KR-2.1 | Technical lead |
| 2.3 | Instantiator function deployed | 2.0 | B.M3 | `<TBD>` | KR-2.1 | Technical lead |
| 2.4 | First monthly BIR filings | 2.0 | B.M4 | **2026-07-14 (R2)** | KR-2.1 | Controller |
| 2.5 | Tax Guru preflight live | 2.0 | B.M5 | `<TBD>` | KR-2.4 | Technical lead |
| 2.6 | First quarterly BIR filings | 2.0 | B.M6 | **2026-10-14 (R3)** | KR-2.2 | Controller |
| 2.7 | 90-day soak complete | 2.0 | B.M7 | `<TBD>` | KR-3.1 | Delivery lead |
| 2.8 | Annual 0605 + 2316 + 1604-CF | 2.0 | B.M9 | `<TBD ≈ 2027-01-31>` | KR-2.3 | Controller |
| 2.9 | 1604-EC | 2.0 | B.M10 | `<TBD ≈ 2027-03-01>` | KR-2.3 | Controller |
| 2.10 | 1702 + eAFS | 2.0 | B.M11 | `<TBD ≈ 2027-04-15>` | KR-2.3, KR-3.2 | Controller + CPA |
| 2.11 | Productization readiness review | 2.0 | B.M12 | `<TBD ≈ 2027-Q2>` | KR-4.2 | Sponsor |

**Baseline schedule** locks at kickoff PR. Changes require change-request per §7.

---

## 5. Risk register (with KR-confidence linkage)

> Confidence scores set at kickoff — do not fabricate values before then.

| Risk ID | Description | P | I | KR impacted | Confidence | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|---|
| R-A1 | D365 data extract fails / incomplete | `<>` | `<>` | KR-1.2 | `<>` | Dry-run extract at A.M3 | Technical lead | Open |
| R-A2 | CoA mapping drift between D365 MainAccount and Odoo `account.account` | `<>` | `<>` | KR-1.2 | `<>` | Build mapping in `ssot/tenants/tbwa-smp/migration/coa-mapping.yaml`; controller sign-off | Technical lead | Open |
| R-A3 | Multi-company consolidation breaks | `<>` | `<>` | KR-1.1 | `<>` | Clarify legal entity count at kickoff; use Odoo multi-company if needed | Technical lead | Open |
| R-A4 | User-training gap causes parallel-close failure | `<>` | `<>` | KR-1.3, KR-1.4 | `<>` | Training sprint before A.M6 | Delivery lead | Open |
| R-A5 | Scope change mid-migration | `<>` | `<>` | multiple | `<>` | Change-control clause in SOW | Sponsor | Open |
| R-A6 | Azure infra cutover delays block readiness | `<>` | `<>` | KR-1.3 | `<>` | Finish sub migration + BOM v2 posture before A.M5 | Technical lead | Open |
| R-A7 | Client-of-client IP confidentiality | `<>` | `<>` | KR-3.2 | `<>` | NDA before A.M2; per-tenant KV secrets; deny-by-default record rules | Legal + Technical lead | Open |
| R-B1 | BIR form format changes mid-engagement | `<>` | `<>` | KR-2.1, KR-2.2, KR-2.3 | `<>` | Tax Guru remote regulation source; quarterly form-update SLA | Technical lead | Open |
| R-B2 | eBIRForms / eFPS portal outage near due date | `<>` | `<>` | KR-2.1, KR-3.1 | `<>` | Submit 48h before due; manual fallback | Controller | Open |
| R-B3 | CPA sign-off delay | `<>` | `<>` | KR-2.3, KR-3.2 | `<>` | Engage CPA early; quarterly unaudited drafts | CPA + Controller | Open |
| R-B4 | Tax Guru incorrect preflight | `<>` | `<>` | KR-2.4, KR-3.1 | `<>` | Human review gate mandatory; Tax Guru is assist only | Technical lead | Open |
| R-B5 | Evidence pack incomplete at audit time | `<>` | `<>` | KR-3.3 | `<>` | Evidence-attachment criterion required to close Story | Delivery lead | Open |
| R-B6 | Multi-entity structure requires multiple TINs | `<>` | `<>` | KR-2.1 | `<>` | Audit entity list at B.M1 | Controller | Open |
| R-B7 | Penalty exposure during cutover | `<>` | `<>` | KR-3.1 | `<>` | Parallel-run through Q3; don't flip authority until A.M7 | Controller | Open |
| R-P1 | Sponsor / stakeholder turnover mid-engagement | `<>` | `<>` | all | `<>` | RACI locked at kickoff; escalation to holding group | Sponsor | Open |
| R-P2 | Delivery capacity constrained | `<>` | `<>` | all | `<>` | Two-role team; partner engagement if needed | Sponsor | Open |
| R-P3 | Data isolation leak (cross-tenant visibility) | `<>` | `<>` | KR-3.2 | `<>` | Record-rule validation; pen-test before A.M5 | Technical lead | Open |
| R-P4 | Pulser Tax Guru production-advice error | `<>` | `<>` | KR-2.4, KR-3.1, KR-3.2 | `<>` | Human review gate; disclaimer in UI; liability cap in contract | Legal + Technical lead | Open |

Rule enforcement (per template Gate 4):
- Every KR with confidence < 0.7 appears in ≥ 1 risk row. ✅ All KRs linked.
- Every risk with Impact ≥ Med links to ≥ 1 KR. ✅ All rows linked.

---

## 6. Scoring log

> Initialized empty. First entry on kickoff; append monthly.

```yaml
# Append-only scoring log. Newest last.
# Each entry: date, review_type, scores per KR, program objective rollup.
- date: <kickoff date>
  review_type: kickoff
  scores: []       # no activity yet; confidence set at kickoff in §5
  program_objective_rollup: []
  comment: "Scoring initialized at kickoff. First real entry at first sprint close."
```

---

## 7. Schedule control (PMBOK)

```yaml
baseline_schedule:     <reference to Odoo project.project record + milestones once A.M2 complete>
baseline_locked_at:    <ISO date after baseline approved by sponsor + controller>
variance_threshold:
  green:  |variance_days| <= 5
  amber:  5 < |variance_days| <= 14
  red:    |variance_days| > 14 → change request required
change_control:
  trigger: red variance
  authority: sponsor + technical lead
  artifact: PR with updated milestone dates + justification
earned_value_tracking: not_enabled_in_v1   # turn on for >USD 100k; revisit at contract
```

---

## 8. Dashboards

See [`tbwa-smp-okr-milestones-dashboard.md`](./tbwa-smp-okr-milestones-dashboard.md) (also `TEMPLATE` status until contract signs).

Three dashboards + one OKR scoring widget:

| Dashboard | Audience | Cadence |
|---|---|---|
| Executive OKR | Sponsors | Monthly |
| Milestone Timeline | Delivery leads | Weekly |
| Operations Health | Finance team | Daily |
| + OKR Scoring widget on Executive OKR | Sponsors | Renders latest scoring log entry |

---

## 9. References

Internal:
- [`_PROGRAM_OKR_TEMPLATE.md`](./_PROGRAM_OKR_TEMPLATE.md) — canonical pattern
- [`tbwa-smp-okr-milestones-dashboard.md`](./tbwa-smp-okr-milestones-dashboard.md) — dashboard spec
- [`ssot/tenants/tbwa-smp/identity.yaml`](../../ssot/tenants/tbwa-smp/identity.yaml)
- [`ssot/tenants/tbwa-smp/seed/ppm_tasks.yaml`](../../ssot/tenants/tbwa-smp/seed/ppm_tasks.yaml)
- [`ssot/tenants/tbwa-smp/seed/calendar_notifications.yaml`](../../ssot/tenants/tbwa-smp/seed/calendar_notifications.yaml)
- [`docs/backlog/ph-close-bir-compliance-board-pack.md`](../backlog/ph-close-bir-compliance-board-pack.md)
- [`docs/product/ph-close-bir-compliance-pack-positioning.md`](../product/ph-close-bir-compliance-pack-positioning.md)
- [`docs/architecture/multitenant-saas-target-state.md`](../architecture/multitenant-saas-target-state.md)
- Memory anchors: `project_acceleration_plan_20260414.md`, `feedback_d365_displacement_not_development.md`, `feedback_d365_two_plane_doctrine.md`, `project_tenant_map_20260414.md`

External:
- [Clarity PPM — Objectives and Key Results (OKRs)](https://techdocs.broadcom.com/us/en/ca-enterprise-software/business-management/clarity-project-and-portfolio-management-ppm-on-premise/16-1-1/introducing-clarity-cookbooks/clarity-cookbook--objectives-and-key-results--okrs-.html)
- PMBOK 7th ed (schedule control, WBS, risk response chapters)

---

## 10. Flip-to-ACTIVE checklist

Reject ACTIVE status until all boxes checked:

- [ ] Contract + SOW signed
- [ ] CFO, controller, CPA named (remove `<TBD>` placeholders in §2)
- [ ] TIN, RDO, primary domain, legal entity count captured (§1 + tenant identity.yaml)
- [ ] Productivity lift target and baseline methodology agreed (KR-4.1, KR-4.2)
- [ ] Specific target dates filled for all non-R2/R3/R4 milestones (§4 WBS table)
- [ ] Confidence scores assigned per KR at kickoff workshop (§3 + §5)
- [ ] Probability / Impact ratings filled per risk at kickoff workshop (§5)
- [ ] Baseline schedule locked via PR (§7)
- [ ] First scoring log entry committed (§6)
- [ ] 5 OKR gates passed (SMART / 3–5 KR / scoring ready / risk linkage / WBS alignment) — see checklist in [`_PROGRAM_OKR_TEMPLATE.md`](./_PROGRAM_OKR_TEMPLATE.md) §Authoring checklist

Only when all 10 boxes are checked, update the **Status:** banner from `TEMPLATE` → `ACTIVE`.

---

*Last updated: 2026-04-15 (template instantiation)*
