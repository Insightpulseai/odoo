# Pulser Product Packaging — Marketplace-Aligned Thin-Delta Strategy

> Based on the 16-marketplace competitive survey (`docs/competitive/d365-marketplace-coverage.md`),
> the Microsoft ecosystem rewards **narrow, attachable, workflow-specific extensions** — not
> platform replacements. This doc locks IPAI's go-to-market packaging accordingly.
> Locked 2026-04-15.

---

## 0. Thesis

> **Win with thin, painful, sellable extensions — not by rebuilding Microsoft or Odoo wholesale.**

The Microsoft / AppSource marketplace pattern validates IPAI's thin-delta doctrine. Winning listings cluster around:

- **Specific business pain** (collections, bank recon, expense liquidation, BIR filing)
- **Clear attach points** (Business Central, F&O, Odoo, SharePoint, Teams)
- **Vertical relevance** (country packs, industry packs, niche operational bundles)
- **Fast time-to-value** (days, not quarters)
- **Workflow augmentation**, not platform replacement

---

## 1. Four canonical packs

IPAI ships four product packs, each a thin bundle on top of Odoo CE + OCA with zero competing ERP claim:

### Pack 1 — Pulser Finance Ops

| Capability | Implementation |
|---|---|
| GL assistance + analytic breakdown | Odoo `account.move` + OCA `account_financial_report` + Pulser Finance agent |
| Bank reconciliation agent | OCA `account_reconcile_oca` + Bank Recon agent (`id-ipai-agent-bank-recon-dev`) |
| Collections / credit control | OCA `account_credit_control` + `ipai_ar_collections` (Issue 12) + Pulser Finance agent |
| Invoice capture + AP automation | `ipai-ocr-dev` + Document Intelligence + AP Invoice agent + OCA `account_invoice_three_way_match` |
| Expense liquidation (PH-aware) | `ipai_expense_liquidation` (canonical name per Issue 8) + Doc Intel agent |
| BIR 2307 auto-generation on CWT vendor payments | `ipai_bir_tax_compliance` (Issue 9) + Code Interpreter |
| KPIs (DSO, DPO, Days-to-close) | Unity Catalog metrics views (Issue 28) + Power BI |

**AppSource comparables:** Continia Finance, Collect 365, Multi-Entity Management, Ramp, OneStream (condensed).

---

### Pack 2 — Pulser Project Services

| Capability | Implementation |
|---|---|
| Project management + WBS | Odoo `project.project` + OCA `project_wbs` + `project_timeline` (Gantt) |
| PSA / professional services | OCA `project_*` family (invoicing, forecast, rev rec) |
| Resource scheduling | OCA `resource_planning` + `resource_booking` |
| Time & expense | Odoo `hr_timesheet` + `hr_expense` + `ipai_expense_liquidation` |
| Project profitability KPIs | `ipai_finance_ppm` (exists in repo) + `mis_builder` + UC metrics |
| Revenue recognition (services) | OCA `project_pm_revenue_recognition` |

**AppSource comparables:** Progressus Advanced Projects, PPM 365, Visual Jobs Scheduler, Plumbline, STAEDEAN Project Lifecycle Suite.

---

### Pack 3 — Pulser Document & Audit

| Capability | Implementation |
|---|---|
| Document generation (DOCX, PDF, XLSX, DAT) | Foundry Code Interpreter (built-in) + `stipaidevagent` Storage |
| Controlled attachments + storage | Odoo `ir.attachment` + OCA `attachment_storage_external` → Azure Blob |
| Document management | OCA `dms` full suite |
| Audit packet generation | `platform.audit_event` schema + Code Interpreter PDF render |
| Evidence/export flows | Pulser skills writing to `stipaidevagent`; governed by `platform.audit_event` |
| OCR / document intelligence | `docai-ipai-dev` + `ipai-ocr-dev` + Doc Intel agent |
| Email workflow + bulk send | Odoo `mail.thread` + `mail.mail` + Zoho SMTP |

**AppSource comparables:** Advanced-Forms, Click2Export, Attach2Dynamics, DMS Add-On, Continia Document Capture / Output, dvelop base.

---

### Pack 4 — PH Localization / Compliance

| Capability | Implementation |
|---|---|
| Odoo PH localization baseline | Odoo `l10n_ph` (upstream) |
| BIR forms (2307, 2550M/Q, SAWT, QAP, SLSP, 1601-C/E, 1702) | `ipai_bir_tax_compliance` (Issue 9 Phase 1; Issue 16 Phase 2 eBIRForms; Issue 24 Phase 3) |
| eBIRForms / eFPS submission | Foundry Browser Automation (Phase 2) |
| Multi-branch TIN + ATC taxonomy | `ipai_bir_tax_compliance` + branch_suffix custom field on `res.partner` |
| BSP FX rate auto-feed | `ipai_bsp_fx_rate` (Issue 15) |
| PH expense liquidation + OR/CWT | `ipai_expense_liquidation` |
| BIR CAS certification (direct eFPS) | Issue 25 — P3 strategic; months-long regulatory path |

**AppSource comparables:** Portugal/Italy/Hungary/Latvia localization packs (pattern validation; PH has no direct competitor).

---

## 2. Packaging sequence (sales + build order)

```
Q2 2026 — ship Pack 1 (Finance Ops) + Pack 4 (PH Localization Core)
  Rationale: highest pain density, clearest ROI narrative,
             structural moat (no D365/AvaTax alternative for PH BIR)

Q3 2026 — add Pack 3 (Document & Audit)
  Rationale: attach to Pack 1 customers needing audit evidence

Q4 2026 — add Pack 2 (Project Services)
  Rationale: TBWA\SMP + agency customers need project billing;
             requires OCA `project_*` hardening first
```

This aligns with:
- `project_acceleration_plan_20260414` memory (R2 Jul 14 Finance slice, R3 Oct 14 BIR, R4 Dec 15 GA)
- Backlog Issues 9, 12, 16, 18, 26, 28, 29

---

## 3. What IPAI explicitly does NOT ship

Reinforced from the 16-marketplace survey findings:

| Anti-pattern | Why rejected |
|---|---|
| All-in-one "AI ERP" pitch | Marketplace rewards thin; competing with Odoo or D365 dilutes the thin-delta thesis |
| Broad platform-clone strategy | OCA + `ipai_*` already wins the coverage argument; no reason to rebuild |
| "Generic agent platform" as the product | Pulser is the enabling layer, NOT the sold product. Packs are sold. |
| Broad undifferentiated vertical scope | IPAI's 3 active verticals (Services, Photo/Video, Research) are the edges; stay inside them |
| Competing with Microsoft M365 Copilot | Per `project_ms_agent_competitive_map` — coexist, don't replace M365 |
| SAP / Oracle displacement | Not IPAI's segment (large enterprise) |

---

## 4. Azure Marketplace listing strategy

Per `docs/competitive/d365-marketplace-coverage.md §11` and Issue 29:

| Listing | Contents | Priority |
|---|---|---|
| `ipai_odoo_on_aca` | Base: Odoo 18 CE on Azure Container Apps + PG Flex + Front Door | **P2 — publish first as private offer** |
| `ipai_pulser_finance_ops_pack` | Pack 1 add-on for above | After Pack 1 ships |
| `ipai_pulser_ph_compliance_pack` | Pack 4 add-on for above | After Pack 4 ships; differentiates vs AvaTax |
| `ipai_pulser_document_audit_pack` | Pack 3 add-on | After Pack 3 ships |
| `ipai_pulser_project_services_pack` | Pack 2 add-on | After Pack 2 ships |

Each pack = separate transactable SKU with its own pricing line. Follows the Continia / Binary Stream / Elite Dynamics multi-pack pattern that dominates AppSource.

---

## 5. Related artifacts

- `docs/competitive/d365-marketplace-coverage.md` — 16-marketplace survey
- `docs/research/d365-to-odoo-mapping.md` — Odoo+OCA+`ipai_*` coverage
- `docs/backlog/open-issues-20260415.md` — Issues 8, 9, 12, 16, 18, 26, 28, 29
- `ssot/foundry/runtime-contract.yaml` — fine-tune roadmap feeding Pack 1 quality

---

*Locked 2026-04-15. Packaging thesis: thin deltas, not platform clones. Ship Pack 1 + Pack 4 first.*
