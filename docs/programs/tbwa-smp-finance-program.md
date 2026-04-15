# TBWA\SMP Finance Transformation — Program + 2 Projects

> **Locked:** 2026-04-15
> **Program boundary:** single engagement, 2 parallel projects under one program
> **Tenant:** `TBWA_SMP` per [`ssot/tenants/tenants-registry.yaml`](../../ssot/tenants/tenants-registry.yaml) (company_id=4, status=prospect)
> **Identity:** [`ssot/tenants/tbwa-smp/identity.yaml`](../../ssot/tenants/tbwa-smp/identity.yaml)
> **Seed data:** [`ssot/tenants/tbwa-smp/seed/`](../../ssot/tenants/tbwa-smp/seed/) (specified below, to be populated on contract)
> **Memory:** `project_tenant_map_20260414.md`, `feedback_d365_displacement_not_development.md`, `project_acceleration_plan_20260414.md`

---

## 1. Program

```
Program:      TBWA\SMP Finance Transformation
Sponsor:      Jake Tolentino (IPAI) + TBWA\SMP CFO (TBD)
Duration:     2026-Q2 → 2027-Q1 (12 months, end-to-end)
First ship:   R2 milestone  2026-07-14
Full ship:    R4 GA         2026-12-15
Stabilized:   2027-Q1
```

**Program objective:** replace TBWA\SMP's D365 Finance + related back-office surface with IPAI's **Odoo CE 18 + OCA + `ipai_*` + Pulser Copilot** stack, shipped as a **private-offer / services-led** engagement, and land the PH Close + BIR Compliance Pack as a productized deliverable.

**Program success = all 4 of:**
1. TBWA\SMP operates month-end close + BIR filings entirely on IPAI stack (no D365 dependency)
2. CFO signs off on first private-offer contract (services-led, 12-month SaaS-per-seat)
3. Audit-complete evidence pack for the 2026 fiscal year close + BIR filings
4. Pulser Finance agents deliver ≥ 20% finance-team productivity lift (measured, not claimed)

---

## 2. Program structure — 2 projects

```
Program: TBWA\SMP Finance Transformation
├── Project A — ERP Displacement (D365 → Odoo CE + OCA + ipai_*)
└── Project B — BIR Compliance Operations (PH Close + BIR Compliance Pack)
```

Two projects, not one, because:
- **Project A is a cutover** (data migration, go-live, deprecate D365)
- **Project B is a recurring operating capability** (close cadence + BIR filings month after month)
- Each has distinct OKRs, milestones, and risk profiles

Aligned to [`feedback_d365_two_plane_doctrine.md`](../../.claude/projects/-Users-tbwa-Documents-GitHub-Insightpulseai/memory/feedback_d365_two_plane_doctrine.md): "Two planes. Never conflate. Two line items in proposals."

---

## 3. Project A — ERP Displacement

### OKR — Project A

**Objective A.1 — TBWA\SMP operates on Odoo+OCA+ipai_* for all core finance functions by R4 GA.**

Key Results:

- **KR-A.1.1** — By **2026-05-30**, TBWA\SMP `res.company` record live on IPAI production Odoo (company_id=4) with PH chart of accounts seeded.
- **KR-A.1.2** — By **2026-06-30**, D365 historical data (GL, AP, AR, vendor master, customer master, open items) imported into Odoo with 100% line reconciliation against D365 close Jun 2026.
- **KR-A.1.3** — By **2026-07-14 (R2)**, GL + AP + AR + bank recon + Pulser Recon Agent v0 operational against TBWA\SMP company context. First test close run parallel to D365.
- **KR-A.1.4** — By **2026-10-14 (R3)**, 2026-Q3 close + BIR 2026-Q3 filings completed 100% on IPAI stack, 0% on D365.
- **KR-A.1.5** — By **2026-12-15 (R4 GA)**, D365 Finance contract signed for non-renewal; IPAI stack is system of record.
- **KR-A.1.6** — By **2027-01-31**, 2026 annual close + 1702 + 1604-CF/EC + eAFS filed from IPAI stack with external CPA sign-off.

**Objective A.2 — Zero data loss + zero regulatory risk during cutover.**

Key Results:

- **KR-A.2.1** — 100% of imported balances reconcile to D365 closing balance as of the cutover date (Jun 2026 close).
- **KR-A.2.2** — 0 BIR filings missed or filed late during cutover period.
- **KR-A.2.3** — 0 audit findings classified as "material" from the 2026 annual audit on IPAI-generated statements.
- **KR-A.2.4** — 100% of finance users retrained (IPAI stack) before D365 read-only mode.

### Milestones — Project A

| # | Milestone | Target date | Ship gate |
|---|---|---|---|
| A.M1 | Contract signed (MSA + SOW for private-offer) | 2026-05-15 | — |
| A.M2 | TBWA\SMP res.company + CoA live | 2026-05-30 | — |
| A.M3 | Data-migration plan + pilot import (sample GL) | 2026-06-15 | — |
| A.M4 | Full historical import reconciled to D365 Jun close | 2026-06-30 | — |
| A.M5 | Parallel close Jun 2026 (D365 authoritative, Odoo shadow) | 2026-07-14 | **R2** |
| A.M6 | Parallel close Jul + Aug 2026 (flip authority Q3) | 2026-08-31 | — |
| A.M7 | Sep 2026 close on IPAI only (D365 read-only) | 2026-10-14 | **R3** |
| A.M8 | D365 non-renewal notice sent | 2026-11-15 | — |
| A.M9 | D365 decommissioned; IPAI is SoR | 2026-12-15 | **R4 GA** |
| A.M10 | 2026 annual close + 1702 + eAFS from IPAI | 2027-01-31 | — |
| A.M11 | External CPA sign-off; audit closed | 2027-Q1 | — |

### Risks — Project A

| ID | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| A.R1 | D365 data extract fails or incomplete | Med | High | Dry-run extract at A.M3; escalate to Microsoft support if API gaps |
| A.R2 | Chart-of-accounts mapping drift (D365 MainAccount → Odoo account.account) | High | High | Build mapping table in `ssot/tenants/tbwa-smp/migration/coa-mapping.yaml`; manual sign-off from TBWA\SMP controller |
| A.R3 | Multi-company consolidation breaks (TBWA\SMP subsidiaries) | Med | Med | Clarify legal entity count on contract; use Odoo multi-company if needed |
| A.R4 | User training gap causes Q3 parallel-close failure | Med | High | Training sprint before A.M6; dedicated IPAI solution engineer on-site |
| A.R5 | Historical FX rate variance between D365 and Odoo | Low | Med | Lock FX rate source (BSP) + load same historical rates |
| A.R6 | TBWA\SMP changes scope mid-migration (e.g. adds Sales module) | Med | Med | Strict change-control process; scope lock at A.M1 |
| A.R7 | D365 Project Operations features used but not mapped | Med | High | Audit D365 module usage in A.M3; OData parity per [`docs/architecture/odata-to-odoo-mapping.md`](../architecture/odata-to-odoo-mapping.md) §7.2 |
| A.R8 | Azure infra cutover delays (PG, ACA) block user readiness | Med | High | Finish sub migration + BOM v2 posture before A.M5 |
| A.R9 | TBWA\SMP requires SAP Ariba or similar procurement integration | Low | High | Scope exclusion in contract; if required, partner engagement for adapter |
| A.R10 | Client-of-client IP confidentiality (advertising agency data) | Med | Med | NDA before A.M2; per-tenant KV secrets; deny-by-default record rules |

---

## 4. Project B — BIR Compliance Operations

### OKR — Project B

**Objective B.1 — TBWA\SMP runs PH Close + BIR Compliance Pack end-to-end on IPAI with audit-grade evidence.**

Key Results:

- **KR-B.1.1** — By **2026-07-14 (R2)**, monthly close cadence Epic 1 operational (31 Issues/month, 2-sprint cadence).
- **KR-B.1.2** — By **2026-07-31**, first month-end BIR filings from IPAI stack: 1601-C + 0619-E + 2550-M + 2307 for June 2026 period, all with evidence pack.
- **KR-B.1.3** — By **2026-10-14 (R3)**, 2026-Q3 BIR filings complete: 2550-Q + 1601-FQ + 1702-Q + SLSP with evidence.
- **KR-B.1.4** — By **2026-12-15 (R4 GA)**, annual BIR registration renewal (0605) + any 2026 interim items filed from IPAI.
- **KR-B.1.5** — By **2027-01-31**, 2316 (per-employee) + 1604-CF (alphalist) generated and filed from IPAI.
- **KR-B.1.6** — By **2027-03-01**, 1604-EC filed from IPAI.
- **KR-B.1.7** — By **2027-04-15**, 1702 annual ITR + eAFS filed from IPAI with CPA sign-off.

**Objective B.2 — Pulser Tax Guru delivers measurable productivity lift.**

Key Results:

- **KR-B.2.1** — Tax Guru preflight run on ≥ 90% of filing Issues before submission (instrumented via [`docs/ops/azure-boards-reporting.md`](../ops/azure-boards-reporting.md) Tier 1 widgets).
- **KR-B.2.2** — Finance-team time-per-filing reduced ≥ 30% vs D365 baseline (measured via timesheet on compliance tasks).
- **KR-B.2.3** — 0 filings submitted without human review + approval gate.
- **KR-B.2.4** — 100% evidence pack compliance (per-filing folder at `docs/evidence/<YYYYMM>/<form>/` with filed PDF + acknowledgment number + payment receipt + GL reconciliation).

### Milestones — Project B

| # | Milestone | Target date | Ship gate |
|---|---|---|---|
| B.M1 | BIR compliance register baseline (map current TBWA\SMP BIR posture) | 2026-06-15 | — |
| B.M2 | 6 IPAI BIR modules installed in TBWA\SMP company context | 2026-06-30 | — |
| B.M3 | Close-period instantiator function deployed (Azure Function per [`ph-close-bir-compliance-board-pack.md`](../backlog/ph-close-bir-compliance-board-pack.md) Epic 5) | 2026-07-07 | — |
| B.M4 | First monthly BIR filings from IPAI (June 2026 period) | 2026-07-14 | **R2** |
| B.M5 | Tax Guru preflight integration live | 2026-07-31 | — |
| B.M6 | First quarterly BIR filings from IPAI (2026-Q3) | 2026-10-14 | **R3** |
| B.M7 | 90-day soak complete — defect curve captured | 2026-10-31 | — |
| B.M8 | Annual BIR registration renewal (0605) from IPAI | 2026-12-31 | — |
| B.M9 | 2316 + 1604-CF from IPAI | 2027-01-31 | — |
| B.M10 | 1604-EC from IPAI | 2027-03-01 | — |
| B.M11 | 1702 + eAFS from IPAI with CPA sign-off | 2027-04-15 | — |
| B.M12 | Productization readiness review (per [`ph-close-bir-compliance-pack-positioning.md`](../product/ph-close-bir-compliance-pack-positioning.md)) | 2027-Q2 | — |

### Risks — Project B

| ID | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| B.R1 | BIR form format changes mid-engagement | High | Med | Tax Guru remote regulation source; quarterly form-update SLA; Tax Guru package releases |
| B.R2 | eBIRForms / eFPS portal outage during due date | Med | High | Prepare + submit 48h before due; keep manual fallback |
| B.R3 | CPA sign-off delay on annual AFS | Med | High | Engage CPA early (M8); provide quarterly unaudited drafts |
| B.R4 | Tax Guru incorrect preflight causing wrong filing | Low | High | **Human review gate mandatory** — Tax Guru is assist only; sign-off required before submit |
| B.R5 | Client 2307 distribution fails to vendors | Med | Med | Zoho SMTP delivery tracking; escalation workflow; manual fallback |
| B.R6 | Evidence pack incomplete at audit time | Low | High | Issue close requires evidence-attachment criterion (Epic 6 of board pack) |
| B.R7 | Multi-entity TBWA\SMP structure requires multiple TINs | Med | High | Audit entity list in B.M1; extend board-pack templates per entity if needed |
| B.R8 | Penalty exposure on late filings during cutover | Med | High | Parallel-run with D365 through Q3; don't flip authority until A.M7 (Sep 2026 close) |
| B.R9 | Tax Guru grounded corpus drifts from current regulation | Med | Med | Quarterly corpus refresh; version-pin per release; PH hierarchy per `project_ph_grounding_hierarchy.md` |
| B.R10 | Audit scope extends beyond IPAI coverage (e.g. prior-period adjustments) | Low | Med | Scope exclusion in contract; advisory-only outside pack |

---

## 5. Cross-project dependencies

| Predecessor | Successor | Link type |
|---|---|---|
| A.M2 (company live) | B.M2 (6 BIR modules installed) | Predecessor |
| A.M4 (historical import reconciled) | B.M1 (BIR register baseline) | Predecessor |
| A.M5 (R2 parallel close) | B.M4 (first monthly BIR filings) | Predecessor |
| A.M7 (R3 Sep close on IPAI only) | B.M6 (Q3 quarterly BIR from IPAI) | Predecessor |
| A.M9 (R4 GA — D365 decom) | B.M8 (annual 0605 from IPAI) | Predecessor |
| A.M10 (2026 annual close IPAI) | B.M11 (1702 + eAFS from IPAI) | Predecessor |

Captured as **Predecessor** links in Azure Boards per [`azure-boards-portfolio-target-state.md`](../backlog/azure-boards-portfolio-target-state.md) dependency rules.

---

## 6. Program-level risks (span both projects)

| ID | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| P.R1 | TBWA\SMP signs then delays kickoff > 60 days | Med | High | Scope start-date in contract; if delayed, re-baseline all milestones |
| P.R2 | TBWA\SMP changes CFO / stakeholder mid-engagement | Low | High | RACI locked at kickoff; executive sponsor from TBWA holding group if possible |
| P.R3 | Azure platform instability (sub migration incomplete) | Low | High | Complete sub consolidation before A.M2; BOM v2 posture verified |
| P.R4 | IPAI delivery capacity constrained (single engineer bandwidth) | Med | High | Two-role delivery team: solution engineer + finance SME; partner engagement if needed |
| P.R5 | Regulatory + audit risk (advisory vs submission boundary blurred) | Med | High | Explicit statements per [`ph-close-bir-compliance-pack-positioning.md`](../product/ph-close-bir-compliance-pack-positioning.md) §Risk register |
| P.R6 | Data isolation leak (TBWA data visible to IPAI cross-tenant) | Low | Very High | Record-rule validation per [`ssot/tenants/tbwa-smp/identity.yaml`](../../ssot/tenants/tbwa-smp/identity.yaml); pen-test before A.M5 |
| P.R7 | Client-of-client IP exposure (TBWA client advertising material) | Med | High | NDA + per-client record rules; encrypt uploads; per-tenant KV |
| P.R8 | Pulser Tax Guru makes a demonstrable error in production advice | Med | High | Human-review gate; disclaimer in UI; liability cap in contract |
| P.R9 | Marketplace productization delay impacts TBWA perception of "product vs bespoke" | Low | Low | Position as private-offer from day one per `ph-close-bir-compliance-pack-positioning.md`; no false claim of "self-serve SaaS" |
| P.R10 | Competitive displacement attempt by Microsoft partner during engagement | Low | Med | Co-sell posture with Microsoft where possible; don't burn the Microsoft bridge |

---

## 7. Seed data specification

Data to seed the TBWA\SMP tenant (`company_id=4`) in Odoo `odoo_dev`. Staged at **[`ssot/tenants/tbwa-smp/seed/`](../../ssot/tenants/tbwa-smp/seed/)** (to be populated on contract).

### 7.1 Company (`res.company`)

```yaml
# ssot/tenants/tbwa-smp/seed/res_company.yaml
id: 4
name: "TBWA\\SMP"
parent_id: null           # independent legal entity in Odoo multi-company sense
partner_id: <res.partner id for the company's own supplier/customer record>
currency_id: PHP
country_id: PH
chart_of_accounts: ph_standard   # seed from l10n_ph (OCA or upstream)
fiscal_country_code: PH
vat: <TIN; to confirm on contract>
company_registry: <BIR registration number; to confirm>
email: <finance@tbwasmp.com or TBD>
phone: <TBD>
website: <TBD>
street: <TBD>              # TBWA\SMP Makati address — to confirm
```

### 7.2 Chart of Accounts (`account.account`)

```yaml
# ssot/tenants/tbwa-smp/seed/coa.yaml
source: l10n_ph (PH standard)
extensions:
  - agency-specific revenue codes:
      - 4001  Agency Fee Revenue (creative services)
      - 4002  Media Buying Revenue (passthrough + margin)
      - 4003  Production Revenue
      - 4004  Digital / Tech Revenue
      - 4005  Retainer Revenue
      - 4006  Pitch / Win Fee Revenue
  - agency-specific cost codes:
      - 5001  Media Pass-Through (matches 4002)
      - 5002  Talent / Freelance COGS
      - 5003  Production Vendor COGS
      - 5004  Client Reimbursables
mapping_file: ssot/tenants/tbwa-smp/migration/coa-mapping.yaml   # D365 MainAccount → Odoo account.account
```

### 7.3 Partners (`res.partner`) — seed set

```yaml
# ssot/tenants/tbwa-smp/seed/partners.yaml
customers:
  type: typical_ph_agency_clients
  examples:
    - Multi-national consumer brands (FMCG, Telco, Banking, QSR)
    - Local PH enterprises
    - Government accounts (if any)
  note: Actual customer list imported from D365 on A.M4
vendors:
  type: typical_ph_agency_vendors
  examples:
    - Media channels (TV networks, OOH vendors, digital platforms)
    - Production houses
    - Talent agencies
    - Freelance creatives
    - Tech platforms (subscriptions)
  note: Actual vendor list imported from D365 on A.M4
self:
  - name: "TBWA\\SMP"
    id: res.partner linked to company_id=4
    vat: <TIN>
```

### 7.4 Products (`product.product`) — agency service SKUs

```yaml
# ssot/tenants/tbwa-smp/seed/products.yaml
services:
  - code: SVC-CREATIVE-HR
    name: Creative Services — Hourly
    type: service
    uom: hours
    standard_price: <TBD>
    tax_ids: [VAT_12%]
  - code: SVC-CREATIVE-PROJECT
    name: Creative Services — Project
    type: service
    uom: unit
  - code: SVC-MEDIA-BUY
    name: Media Buy Pass-Through + Margin
    type: service
    account_ids: [4002 Media Buying Revenue]
  - code: SVC-PRODUCTION
    name: Production Services
    type: service
    account_ids: [4003 Production Revenue]
  - code: SVC-DIGITAL
    name: Digital / Tech Services
    type: service
    account_ids: [4004 Digital / Tech Revenue]
  - code: SVC-RETAINER
    name: Monthly Retainer
    type: service
    account_ids: [4005 Retainer Revenue]
  - code: SVC-PITCH-WIN
    name: Pitch / Win Fee
    type: service
    account_ids: [4006 Pitch / Win Fee Revenue]
```

### 7.5 Projects (`project.project`) — seed campaigns

```yaml
# ssot/tenants/tbwa-smp/seed/projects.yaml
note: Actual project list imported from D365 Project Operations if used,
      or created fresh from client roster.
seed_pattern:
  - One project per (client × campaign) pair
  - Use client account as partner_id
  - Use project stage = active for ongoing, closed for past
  - Seed ~5 demo projects for user training
```

### 7.6 Users (`res.users`) + Employees (`hr.employee`)

```yaml
# ssot/tenants/tbwa-smp/seed/users.yaml
source: TBWA\SMP active directory export (via Entra, if M365)
company_ids_whitelist: [4]   # strict — TBWA users see ONLY TBWA company
groups_assignment:
  - Finance: [CFO, controller, AP clerks, AR clerks, payroll]
  - Projects: [project managers, creative leads]
  - Portal: [client-facing read-only accounts]
authentication: Entra OIDC (per [`ssot/tenants/tbwa-smp/identity.yaml`](../../ssot/tenants/tbwa-smp/identity.yaml))
note: Actual user list imported from TBWA directory on A.M1+A.M2
```

### 7.7 Fiscal calendar (`account.fiscal.year`)

```yaml
# ssot/tenants/tbwa-smp/seed/fiscal_calendar.yaml
fiscal_year: calendar  # TBWA\SMP on calendar FY (confirm at A.M1)
fiscal_year_2026:
  start: 2026-01-01
  end: 2026-12-31
  periods: monthly (12)
fiscal_year_2027:
  start: 2027-01-01
  end: 2027-12-31
  periods: monthly (12)
```

### 7.8 BIR compliance seed (`ipai_bir_tax_compliance`)

```yaml
# ssot/tenants/tbwa-smp/seed/bir_compliance.yaml
tin: <TIN>                # confirm on contract
rdo_code: <RDO code>      # BIR Revenue District Office
bir_forms_enrolled:
  - 1601-C (monthly)
  - 0619-E (monthly)
  - 2550-M (monthly)      # VAT-registered assumed; confirm
  - 2550-Q (quarterly)
  - 1601-FQ (quarterly)
  - 1702-Q (quarterly)
  - 1702-RT (annual)      # assume reg-rate; confirm
  - 2316 (annual, per-employee)
  - 1604-CF (annual)
  - 1604-EC (annual)
  - 0605 (annual registration)
  - eAFS (annual, with 1702)
  - SLSP (quarterly)
efps_enrolled: tbd
ebirforms_enrolled: assumed_yes
```

### 7.9 Seed data governance

| Rule | Enforcement |
|---|---|
| All seed YAMLs live under `ssot/tenants/tbwa-smp/seed/` | `roadmap-ssot-guard` skill + PR review |
| No real PII in seed YAMLs before contract | Reviewed at commit time |
| Real data imported via migration scripts, not committed | `scripts/migration/tbwa-smp-import.py` (to author) |
| All seed changes tracked in git | Each change is a PR with A.M reference |
| Seed diff vs D365 reconciled at A.M4 | Manual controller sign-off |

---

## 8. RACI

| Role | Responsibility |
|---|---|
| **Accountable** | Jake Tolentino (IPAI CEO) — program sponsor |
| **Responsible — Delivery** | IPAI solution engineer (TBD hire or Jake hands-on for v1) |
| **Responsible — Finance SME** | TBWA\SMP controller (client-side) |
| **Consulted — CPA** | External CPA firm (for annual audit + eAFS) |
| **Consulted — Tax advisor** | Tax Guru (Pulser) + optionally external PH tax counsel |
| **Informed** | TBWA\SMP CFO, TBWA holding group (if consolidation required) |

---

## 9. Success criteria (program level)

- [ ] TBWA\SMP signs private-offer SOW (A.M1)
- [ ] Historical data reconciles to D365 baseline (A.M4)
- [ ] R2 ship: first monthly BIR filings from IPAI (A.M5 + B.M4)
- [ ] R3 ship: Q3 close + quarterly BIR from IPAI only (A.M7 + B.M6)
- [ ] R4 GA: D365 decommissioned (A.M9)
- [ ] 2026 annual close + 1702 + eAFS from IPAI with CPA sign-off (A.M10 + A.M11 + B.M11)
- [ ] 0 BIR late-filing penalties during engagement
- [ ] 0 material audit findings on IPAI-generated statements
- [ ] Finance-team productivity ≥ 20% lift (KR-B.2.2)
- [ ] Evidence pack 100% compliance (KR-B.2.4)

---

## 10. Azure Boards mapping

Per [`docs/backlog/azure-boards-portfolio-target-state.md`](../backlog/azure-boards-portfolio-target-state.md):

```
Initiative: InsightPulseAI — Multitenant SaaS Platform Buildout
  Epic 1: Core Operations Plane                 (\InsightPulseAI\CoreOps)
    Feature: TBWA\SMP ERP Displacement           ← Project A of this program
    Feature: TBWA\SMP BIR Compliance Operations  ← Project B of this program
```

Plus cross-cutting:
- Epic 5 (Shared SaaS Control Plane) — tenant model, KV, metering for TBWA\SMP
- Epic 6 (Delivery / Platform Engineering) — Azure Pipelines for TBWA\SMP deploys
- Epic 7 (FinOps / Governance) — per-tenant billing_scope + cost allocation

All Stories under these Features tagged:
- `tenant_scope: single-tenant`
- `billing_scope: customer`
- `product: odoo` or `pulser` per plane
- `customer_code: tbwa_smp` (optional tag)

Visible in the **Product Delivery Plan** (Feature + Story level) and the **Executive Portfolio Plan** (rolled up to this program).

---

## References

- [`ssot/tenants/tenants-registry.yaml`](../../ssot/tenants/tenants-registry.yaml)
- [`ssot/tenants/tbwa-smp/identity.yaml`](../../ssot/tenants/tbwa-smp/identity.yaml)
- [`docs/tenants/TENANCY_MODEL.md`](../tenants/TENANCY_MODEL.md)
- [`docs/backlog/ph-close-bir-compliance-board-pack.md`](../backlog/ph-close-bir-compliance-board-pack.md)
- [`docs/product/ph-close-bir-compliance-pack-positioning.md`](../product/ph-close-bir-compliance-pack-positioning.md)
- [`docs/architecture/multitenant-saas-target-state.md`](../architecture/multitenant-saas-target-state.md)
- [`docs/architecture/odata-to-odoo-mapping.md`](../architecture/odata-to-odoo-mapping.md)
- Memory: `project_tenant_map_20260414.md`
- Memory: `feedback_d365_displacement_not_development.md`
- Memory: `feedback_d365_two_plane_doctrine.md`
- Memory: `project_acceleration_plan_20260414.md`
- Memory: `project_tax_guru_copilot.md`
- Memory: `project_taxpulse_ph_pack_positioning.md`

---

*Last updated: 2026-04-15*
