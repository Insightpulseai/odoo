# Industries Coverage via OCA — Odoo 18 All-Industries Mapping

> **Locked:** 2026-04-15
> **Authority:** this file (which Odoo industries IPAI can serve via CE + OCA, without going to EE or custom)
> **Reference:** [Odoo — All Industries](https://www.odoo.com/es_ES/all-industries)
> **Doctrine:** "We fan out to industries via OCA, not EE, not proliferated custom code."
> **Companions:**
> - [`capability-source-map.md`](./capability-source-map.md) — what we consume today
> - [`revised-bom-target-state.md`](./revised-bom-target-state.md) — BOM v2
> - [`ssot/governance/upstream-adoption-register.yaml`](../../ssot/governance/upstream-adoption-register.yaml)

---

## Position

Odoo markets itself to **~25 industries**. Most verticals need **little-to-no bespoke code** — they're combinations of CE apps (accounting / project / sale / inventory / etc.) with OCA repos for depth and a thin `ipai_*` shim only where truly needed.

**IPAI rule:** adopt via OCA before building. All-at-once scale-out is via **new submodule adds + config**, not new `ipai_*` modules.

---

## Industry coverage matrix

Columns:
- **Core CE apps** — Odoo CE modules always present
- **OCA repos (installed)** — repos we already have in `addons/oca/` (from [`capability-source-map.md`](./capability-source-map.md))
- **OCA repos to add** — additional submodule adds if we target this industry
- **`ipai_*` needed?** — bespoke delta required
- **Coverage** — %

| # | Industry | Core CE apps | OCA (installed) | OCA (to add) | `ipai_*`? | Coverage |
|---|---|---|---|---|---|---|
| 1 | **Services / Agencies** (TBWA\SMP, W9 Studio) | `project`, `sale`, `sale_timesheet`, `account`, `hr_timesheet`, `hr_expense`, `appointment` | `project`, `timesheet`, `hr-expense`, `sale-workflow`, `sale-reporting`, `credit-control`, `account-*` (5 repos), `knowledge`, `dms` | — | `ipai_finance_ppm` + `ipai_bir_*` | **~100%** via installed + `ipai_*` |
| 2 | **Retail / eCommerce** | `website_sale`, `sale`, `stock`, `account`, `pos`, `delivery` | `sale-workflow`, `sale-reporting`, `account-invoicing`, `dms` | `e-commerce`, `stock-logistics-workflow`, `stock-logistics-warehouse`, `pos`, `multi-warehouse` | None if pure retail | ~85% with additions |
| 3 | **Manufacturing** | `mrp`, `stock`, `quality`, `maintenance`, `purchase`, `account` | `purchase-workflow` | `manufacture`, `manufacture-reporting`, `stock-logistics-workflow`, `quality-control`, `maintenance` | None | ~90% with additions |
| 4 | **Food & Agriculture** | `mrp`, `stock`, `account`, `pos`, `website`, `quality` | `purchase-workflow`, `account-*` | `agriculture` (no OCA repo; likely `stock-logistics-workflow` + traceability OCA modules) | Maybe thin `ipai_traceability` | ~75% with OCA adds |
| 5 | **Construction** | `project`, `hr_expense`, `stock`, `account` | `project`, `hr-expense`, `account-*` | `construction` (check OCA; often `project-reporting` + `field-service` covers most) | Maybe thin | ~80% with `field-service` + `project-reporting` |
| 6 | **Real Estate** | `project`, `crm`, `sale`, `account` | `partner-contact`, `sale-workflow` | `real-estate` (if exists), `property-management`, `rental` | Likely thin | ~75% |
| 7 | **Professional Services / Consulting** | `project`, `sale_timesheet`, `hr_expense`, `sign` | `project`, `timesheet`, `hr-expense`, `credit-control` | `contract` (OCA — for retainers) | — | **~100%** via installed |
| 8 | **Healthcare (admin, not clinical)** | `project`, `account`, `appointment`, `hr` | `project`, `timesheet`, `partner-contact` | `vertical-medical` (OCA — has clinical; needs `regulated_scope` gate) | **Not by default per BOM doctrine** — `regulated_scope: none` | 0% until gate lifted (see §Regulated) |
| 9 | **Hospitality — Hotel** | `appointment`, `website`, `sale`, `account` | `appointment` (OCA ext.), `dms` | `vertical-hotel` (check OCA), `website-appointment` extensions | Maybe thin | ~70% with additions |
| 10 | **Hospitality — Restaurant** | `pos`, `sale`, `mrp`, `stock`, `account` | `sale-workflow` | `vertical-restaurant` or `pos-*`, `stock-logistics-workflow`, `menu-management` | Maybe thin | ~70% |
| 11 | **Education** | `website`, `website_event`, `mail`, `hr` | `knowledge`, `partner-contact` | `edi` (for learning records), `vertical-education` (if exists), OCA `hr-*` | Maybe thin | ~65% |
| 12 | **Non-profit / NGO** | `account`, `project`, `donation` (none in CE — OCA) | `account-*`, `partner-contact` | `donation`, `grant-management` (OCA), `vertical-ngo` | Likely thin | ~60% |
| 13 | **Legal** | `project`, `sign`, `account`, `hr_expense` | `project`, `credit-control`, `knowledge`, `dms` | `matter-management` (if exists), `contract`, OCA `sign-*` | Likely thin | ~75% |
| 14 | **Media / Publishing** | `project`, `website`, `sale`, `website_event` | `project`, `knowledge`, `dms` | `publishing` (likely custom), OCA `media-*` | Thin | ~70% |
| 15 | **Logistics / Transportation** | `stock`, `fleet`, `sale`, `delivery`, `account` | `account-*` | `fleet`, `stock-logistics-*` (multiple), `delivery-carrier` | Maybe thin | ~80% |
| 16 | **Field Service** | `field_service` (EE) **→ OCA `field-service`** | — | `field-service` (OCA) | Thin | ~75% with OCA |
| 17 | **Subscription / SaaS** | `sale`, `account`, `subscription` (EE) **→ OCA `contract`** | — | `contract`, `website-appointment`, `account-*` | Thin | ~85% with OCA |
| 18 | **Rental** | `rental` (EE) **→ OCA `rental`** | — | `rental` (OCA), `stock-logistics-workflow` | Thin | ~80% |
| 19 | **E-learning** | `website_slides` (partial EE) | — | `edi`, `vertical-education`, OCA `knowledge` | Thin | ~60% |
| 20 | **Distribution / Wholesale** | `stock`, `purchase`, `sale`, `account` | `purchase-workflow`, `sale-workflow`, `account-*` | `stock-logistics-workflow`, `multi-warehouse` | — | ~90% |
| 21 | **Marketing / Advertising** | `crm`, `marketing_automation` (EE), `mass_mailing`, `social` | `social`, `sale-reporting`, `partner-contact` | OCA `marketing-*` if exists; n8n/Azure Logic for automation replacement | Thin — **we displace EE via Pulser** | ~70% via Pulser strategy |
| 22 | **Recruitment / HR Staffing** | `recruitment`, `hr`, `hr_expense` | `hr-expense` | OCA `hr-*`, `hr-recruitment-*` | Thin | ~75% |
| 23 | **Financial Services / Banking-adjacent** | `account`, `sign`, `documents` | `account-*` (5 repos), `dms` | `account-banking-*`, `banking-operations` | Likely significant | ~65% |
| 24 | **Government / Public Sector** | `account`, `project`, `hr`, `sign` | `account-*`, `project`, `knowledge` | `vertical-government` (unlikely), OCA `l10n_*` per country | Thin per-country | ~60% |
| 25 | **Insurance** | `account`, `sign`, `contract` | `account-*` | `insurance` (rarely in OCA), OCA `contract` | Likely significant | ~50% |

---

## Coverage rollup by tier

| Tier | Industries | Coverage | Notes |
|---|---|---|---|
| **Tier 1 — cover today** | Services/Agencies, Professional Services | **~100%** | Already in scope (TBWA\SMP, W9) |
| **Tier 2 — cover with OCA adds only** | Retail, Manufacturing, Distribution, Legal, Hospitality, Field Service, Subscription, Rental, Logistics | **75–90%** | Add 3–6 OCA repos each; no new `ipai_*` unless truly bespoke |
| **Tier 3 — cover with OCA + thin `ipai_*`** | Food & Agriculture, Construction, Real Estate, Education, NGO, Media, Marketing (Pulser displacement), Recruitment | **60–80%** | 1–2 thin adapters per industry |
| **Tier 4 — partial, needs work** | E-learning, Government, Insurance, Banking-adjacent | **50–65%** | Industry-specific OCA less mature; country-specific localization needed |
| **Tier 5 — gated** | Healthcare clinical | **0% by default** | Requires `regulated_scope` upgrade per [`revised-bom-target-state.md`](./revised-bom-target-state.md) Research plane; not in default BOM |

---

## All-at-once OCA adoption strategy

Rather than adding OCA repos one at a time as customers show up, **pre-stage the adoption register** for all Tier 1–2 industries:

### Phase 1 (immediate — what's already installed)

27 repos cover Services, Professional Services, and most of Finance/Accounting.
**No action.**

### Phase 2 (add in one batch to enable 75%+ of industries)

~8 new submodule adds unlock Retail / Manufacturing / Distribution / Hospitality / Field Service / Subscription / Rental / Legal:

```
addons/oca/stock-logistics-workflow
addons/oca/stock-logistics-warehouse
addons/oca/e-commerce
addons/oca/pos
addons/oca/manufacture
addons/oca/manufacture-reporting
addons/oca/field-service
addons/oca/contract
addons/oca/rental
addons/oca/delivery-carrier
```

**Posture:** `consume_directly` (same as the other 27). Pinned via `git submodule add`. Each needs test-install per [`.claude/rules/oca-governance.md`](../../.claude/rules/oca-governance.md) quality gates before install baseline.

### Phase 3 (add per customer demand)

Country localization (`l10n_*`), industry-specific verticals (`vertical-*`), regulated scope (`vertical-medical` behind `regulated_scope` gate).

---

## The 5 quality gates before any OCA adoption (per `oca-governance.md`)

1. 18.0 branch exists and CI green on OCA repo
2. `development_status >= Stable` in `__manifest__.py`
3. Test install in disposable DB (`test_<module>`)
4. No conflicts with existing `ipai_*` modules
5. Document in `config/addons.manifest.yaml` with repo / tier / provenance

Rejection of these quality gates = DO NOT adopt.

---

## When to build `ipai_*` instead of adopting more OCA

Per CLAUDE.md decision order:
```
CE 18 → property fields → OCA same-domain → adjacent OCA → compose → ipai_* last
```

`ipai_*` only when:
- The capability is **truly IPAI-specific** (e.g. `ipai_bir_*` for PH regulatory)
- Cross-system integration that can't be composed (e.g. `ipai_mail_plugin_bridge`)
- Thin overlay to a platform service (e.g. `ipai_ask_ai_azure`)

**Industry scale-out is NOT in this list.** Use OCA.

---

## Decision when a customer asks for an industry we don't cover

```
1. Check this table — does OCA cover it?
   YES → add the OCA repo(s), document in addons.manifest.yaml, ship
   NO  → go to step 2

2. Is coverage >= 75% via existing OCA + CE?
   YES → ship the 75% + document gaps, negotiate scope reduction
   NO  → go to step 3

3. Is the gap truly bespoke to IPAI doctrine?
   YES → build a thin `ipai_*` module (single-concern, < 500 LOC)
   NO  → decline the industry; don't take the deal

4. Never: build a competing EE clone or fork Odoo
```

---

## Regulated-scope gate

Industries that require PHI / clinical / regulated data (Healthcare clinical, some Financial Services, Insurance):

Per [`ssot/azure/tagging-standard.yaml`](../../ssot/azure/tagging-standard.yaml) v3 `regulated_scope`:

```
none         → default
research     → PrismaLab + public-health analytics
health       → non-PHI health data (wellness, public health)
clinical     → PHI/EHR/imaging; requires HDS + FHIR adoption
```

Healthcare clinical, insurance claims with PHI, any banking data with PII-over-threshold → **require governance approval + infrastructure uplift** before accepting.

---

## Anti-patterns

- Adopting Odoo EE module to cover an industry — violates CE-only doctrine
- Building an `ipai_<industry>` module when OCA covers it — violates no-custom doctrine
- Taking on a Healthcare clinical customer without `regulated_scope` upgrade — governance violation
- Forking Odoo to tweak for an industry — never
- Proliferating country-specific `l10n_*` forks instead of contributing upstream

---

## Bottom line

```
Odoo CE 18 + 27 installed OCA repos today      → 3 industries at ~100%
+ 10 OCA repos in Phase 2 batch adoption        → 12 more industries at 75-90%
+ thin ipai_* per demand                        → Tier 3 industries covered
+ regulated_scope gate                          → Tier 5 gated until infra uplift

All-at-once OCA adoption doctrine: when we move to a new industry,
we scale out via submodule adds, not bespoke modules.
```

---

*Last updated: 2026-04-15*
