# PH Close + BIR Compliance Pack — Product Positioning

> **Locked:** 2026-04-15
> **Authority:** this file (commercial positioning + ship-readiness gates)
> **Backlog companion:** [`docs/backlog/ph-close-bir-compliance-board-pack.md`](../backlog/ph-close-bir-compliance-board-pack.md)
> **Vertical companion:** [`docs/strategy/data-intelligence-vertical-target-state.md`](../strategy/data-intelligence-vertical-target-state.md)

---

## Decision

```
Worth productizing now            : YES
Public marketplace ready today    : NO
Best near-term path               : Private offer / services-led solution
```

PH Close + BIR is a **real solution domain**, not just an idea. But it's still **operating-model + backlog + module set + automation design + compliance workflow doctrine** — not yet **installable / supportable / self-serve / certifiable** as a SaaS product.

---

## What's already a real solution

| Asset | Evidence |
|---|---|
| Domain modules | `addons/ipai/ipai_bir_2307/`, `ipai_bir_2307_automation/`, `ipai_bir_tax_compliance/`, `ipai_bir_returns/`, `ipai_bir_slsp/`, `ipai_finance_ap_ar/` |
| Recurring work model | [`docs/backlog/ph-close-bir-compliance-board-pack.md`](../backlog/ph-close-bir-compliance-board-pack.md) — 1 Initiative / 6 Epics / 26 Features / 120 Issues |
| Calendarized compliance logic | Monthly / quarterly / annual cadence per BIR form, due-date model |
| Board-pack operating model | Templates + Azure Functions instantiator pattern |
| Automation pattern | `close-period-instantiator`, `bir-period-instantiator`, `overdue-escalation-notifier` |
| Evidence / audit concept | Per-filing evidence pack at `docs/evidence/<YYYYMM>/<form>/`, register in `ipai_bir_tax_compliance` |
| Tax copilot assist | Tax Guru sub-agent (`project_tax_guru_copilot.md`, 7 packages) |

That clears the bar to call this a **solution**, not a concept.

---

## What's NOT yet ready for public marketplace

### 1. Logic is split, not packaged

Today the solution is spread across:
- multiple `ipai_bir_*` modules
- backlog templates + instantiator design
- dashboard widget recommendations
- Tax Guru integration concept

Powerful, but **fragmented**. A marketplace listing needs one canonical SKU.

### 2. Buyer + packaging not yet locked

Candidate SKU shapes (need to pick one canonical first):
- **SME VAT / withholding pack** (smallest)
- **Enterprise finance close + BIR operations pack**
- **Agency finance ops PH pack**
- **Accounting-firm / outsourcer pack**

### 3. Runtime architecture sounds implementation-heavy

Marketplace customers need to understand at install time:
- what gets installed
- what runs in Odoo
- what runs in Azure
- what runs on schedule
- what is optional
- what data leaves Odoo
- what is advisory vs filing/submission

### 4. Regulatory boundaries need sharper statements

Required explicit statements before public listing:
- advisory vs filing submission
- human review requirements
- supported BIR forms list (whitelist)
- supported taxpayer/entity scenarios
- evidence retention policy
- support boundaries
- no guarantee of regulatory acceptance without review

---

## Two-offer model

### Offer 1 — Sell NOW (private / services-led)

```
Name:       PH Close + BIR Compliance Pack
Type:       Partner-led / private offer
Delivery:   Implementation package + managed compliance operations add-on
Buyer:      PH SMEs, agencies, multi-entity operators, accounting-led teams
Channel:    Direct + Microsoft private offer (Partner Center)
```

**Includes:**
- Close cadence setup (Epic 1, 31 Issues)
- Filing calendar setup (Epics 2–4, 69 Issues)
- BIR forms + work items (instantiated per period)
- Evidence + audit dashboards
- Module deployment + tenant onboarding
- Guided Tax Guru assist

**Why this works now:**
- Operating model + recurring work templates + module family + close/filing cadence + audit trail concept = enough for **partner-assisted** delivery
- Not enough for mass self-serve

### Offer 2 — Public marketplace LATER

```
Name:       PH Tax Operations for Odoo
Type:       Public marketplace OR public Odoo app family
Delivery:   Packaged product
Buyer:      Broader Odoo ecosystem
```

Requires stronger packaging + stricter boundaries (see ship-readiness gates below).

---

## Ship-readiness gates (must ALL pass before public listing)

### Product gates

- [ ] One canonical product name (locked)
- [ ] One clear buyer (locked)
- [ ] One clear supported scope (locked)
- [ ] One install/runtime diagram (drawn + signed off)

### Technical gates

- [ ] One meta-package / orchestrated install path
- [ ] Deterministic scheduler + runtime (no manual instantiation steps)
- [ ] Tenant + config isolation per [`docs/architecture/multitenant-saas-target-state.md`](../architecture/multitenant-saas-target-state.md)
- [ ] Fixtures + seeded demo data
- [ ] Regression tests per supported form + cadence
- [ ] Ship to one paying private-offer customer first; soak ≥ 90 days

### Compliance gates

- [ ] Supported forms list explicit (whitelist, not promise-everything)
- [ ] Unsupported cases list explicit
- [ ] Human review gate explicit (Tax Guru is **assist**, not auto-file)
- [ ] Evidence retention + export explicit
- [ ] Advisory vs submission boundary explicit (no auto-submit without human approval)

### Commercial gates

- [ ] Packaging tiers defined
- [ ] Support model defined (SLAs, channels, hours)
- [ ] Onboarding path documented
- [ ] Implementation prerequisites listed
- [ ] Terms / disclaimers reviewed by counsel

---

## Roadmap to marketplace

```
Today                       Private offer ready (services-led)
2026-Q3                     First private-offer customer signs (target: TBWA\SMP or similar PH F&B/agency)
2026-Q3 → Q4                Soak 90 days; capture defect curve + support load
2026-Q4                     Microsoft private offer listed (Partner Center)
2027-Q1 (earliest)          Public Odoo app family listing for narrower module subsets
2027-Q2 (earliest)          Public marketplace SaaS listing — only if all ship gates pass
```

Aligned with locked dates per [`project_acceleration_plan_20260414.md`](../../.claude/projects/-Users-tbwa-Documents-GitHub-Insightpulseai/memory/project_acceleration_plan_20260414.md):
- R3 (2026-10-14) PH BIR cutover for first customer = first private-offer ship
- R4 (2026-12-15) GA = private-offer + Microsoft private offer ready
- 2027 = public marketplace candidate

---

## Single product boundary (for Offer 1)

```
PH Close + BIR Compliance Pack
├─ Odoo modules
│   ├─ ipai_bir_2307
│   ├─ ipai_bir_2307_automation
│   ├─ ipai_bir_tax_compliance
│   ├─ ipai_bir_returns
│   ├─ ipai_bir_slsp
│   └─ ipai_finance_ap_ar
├─ Recurring instantiator (Azure Functions)
│   ├─ close-period-instantiator
│   ├─ bir-period-instantiator
│   └─ overdue-escalation-notifier
├─ Dashboard pack (Azure Boards Tier 1 + Tier 2)
├─ Evidence + audit exports (per-filing evidence pack)
└─ Tax Guru assist (Pulser sub-agent, 7 packages)
```

This is the boundary to **lock as one SKU** for Offer 1 sales motion.

---

## Risk register (must mitigate before public listing)

| Risk | Mitigation |
|---|---|
| Customer expects auto-filing | Make advisory vs submission boundary explicit in onboarding + UI |
| BIR form changes (regulatory drift) | Tax Guru calls remote regulation source; quarterly form-update SLA |
| Customer multi-entity scenarios beyond scope | Whitelist supported scenarios; reject unsupported during onboarding |
| Customer expects unsupported cadence (e.g. weekly) | Lock to monthly/quarterly/annual; document non-goals |
| Customer expects integration with non-Odoo ERP | Out of scope; integration is partner engagement |
| Customer expects e-Invoicing (separate BIR program) | Out of scope for v1; track for v2 |
| Customer expects multi-country expansion | Out of scope; PH-only per `project_data_intelligence_vertical_20260415.md` (PH localization first) |

---

## What this changes for the backlog

The [120-Issue board pack](../backlog/ph-close-bir-compliance-board-pack.md) doesn't change in scope — but it gains a **commercial frame**:

- **Epics 1–4 (close + monthly + quarterly + annual filings)** → **Offer 1 deliverable scope**
- **Epic 5 (calendar automation)** → **Offer 1 productization gate** (must be deterministic for sale)
- **Epic 6 (evidence + audit)** → **Offer 1 compliance gate** + evidence-export feature for public-listing later

Add a new Epic **7 — Productization & Ship-Readiness** when ready:
- One canonical SKU name + branding
- Install diagram + runtime diagram
- Onboarding wizard
- Support SLAs + escalation
- Pricing tiers
- Public website page
- Microsoft Partner Center listing materials

---

## Doctrine alignment

- Per [`feedback_d365_displacement_not_development.md`](../../.claude/projects/-Users-tbwa-Documents-GitHub-Insightpulseai/memory/feedback_d365_displacement_not_development.md): IPAI displaces D365 Finance for PH customers. PH Close + BIR is the **wedge** that proves the displacement.
- Per [`project_taxpulse_ph_pack_positioning.md`](../../.claude/projects/-Users-tbwa-Documents-GitHub-Insightpulseai/memory/project_taxpulse_ph_pack_positioning.md): "TaxPulse-PH-Pack = PH BIR pack" — this product positioning operationalizes that strategy.
- Per [`docs/strategy/data-intelligence-vertical-target-state.md`](../strategy/data-intelligence-vertical-target-state.md): PH-localized first; multi-country only after PH wedge proves out.

---

## Recommendation

```
Yes, productize immediately as Offer 1 (private / services-led).
Do not rush Offer 2 (public marketplace) — soak Offer 1 for ≥ 90 days first.
Ship to first private-offer customer in 2026-Q3.
Microsoft private offer in 2026-Q4.
Public marketplace candidate review in 2027-Q1.
```

## Next milestone

Turn the backlog pack + module family + instantiator design into **one canonical SKU package** with clear boundary:

- **`PH Close + BIR Compliance Pack`** as the public-facing name
- One install + runtime diagram
- One pricing tier table
- One support + onboarding playbook
- Add Epic 7 to the board pack

Then evaluate:
1. **Microsoft private offer** first (2026-Q4)
2. **Public marketplace** second (2027-Q1+)
3. **Odoo Apps packaging** later for narrower module subsets

---

*Last updated: 2026-04-15*
