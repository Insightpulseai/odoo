# Seed Data Strategy — InsightPulse AI Platform

> SSOT: `ssot/migration/production_seed_plan.yaml`
> Public registry: `docs/research/seed-data-registry.md`
> Entity model: `docs/seed/CANONICAL_ENTITY_MODEL.md`
> Synthetic spec: `docs/seed/SYNTHETIC_GAP_SPEC.md`

---

## 1. Executive Summary

This strategy produces a realistic demo/simulation environment across Odoo, Supabase, Databricks, and Plane using a **public-first, synthesize-only-the-gaps** approach.

**Principle**: If a suitable public dataset exists, use it. Only synthesize what is genuinely missing.

**Scale targets**:
- Minimum viable seed pack: ~50K records across 30 entities (demo-ready)
- Full simulation seed pack: ~500K records across 50+ entities (BI/agent/forecast-ready)

**Platform write model**: Odoo is the canonical write surface for all transactional entities. Supabase, Databricks, and Plane receive projections — never originate canonical records.

---

## 2. Public-Source-First Dataset Registry

Full registry with URLs, licenses, schemas, and fit analysis: [`docs/research/seed-data-registry.md`](../research/seed-data-registry.md)

### Top Picks by Domain

| Domain | Dataset | Source | License | Records | Decision |
|--------|---------|--------|---------|---------|----------|
| **Retail/Commerce** | Olist Brazilian E-Commerce | [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) | CC BY-NC-SA 4.0 | 100K orders, 8 CSVs | **Transform** (locale BR→PH) |
| **Retail/Commerce** | UCI Online Retail II | [UCI](https://archive.ics.uci.edu/dataset/502/online+retail+ii) | CC BY 4.0 | 1M transactions | **Transform** (flat→relational) |
| **Retail/Commerce** | Superstore | [Kaggle](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) | Public domain | 10K rows | **Use as-is** (demo) |
| **Marketing** | Campaign Performance | [Kaggle](https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset) | Public | 200K rows | **Transform** (→utm.campaign) |
| **Marketing** | Email Campaign SME | [Kaggle](https://www.kaggle.com/datasets/loveall/email-campaign-management-for-sme) | CC BY-NC-SA 4.0 | 2.5K rows | **Transform** (→mailing.trace) |
| **Finance** | Financial Transactions | [Kaggle](https://www.kaggle.com/datasets/cankatsrc/financial-transactions-dataset) | Public | 100K rows | **Transform** (→account.move.line) |
| **Finance** | Invoices | [Kaggle](https://www.kaggle.com/datasets/cankatsrc/invoices) | Public | 10K rows | **Transform** (→account.move) |
| **Finance** | SEC EDGAR | [SEC.gov](https://www.sec.gov/dera/data/financial-statement-data-sets) | Public domain | Thousands of cos | **Partial-use** (CoA reference only) |
| **HR** | IBM HR Analytics | [Kaggle](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) | Public | 1,470 employees | **Transform** (→hr.employee) |
| **HR** | Human Resources Set | [Kaggle](https://www.kaggle.com/datasets/rhuebner/human-resources-data-set) | CC BY-SA 4.0 | 300 employees | **Transform** (→hr.employee + manager hierarchy) |
| **Support** | Customer Support Tickets | [Kaggle](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset) | Public | 50K tickets | **Transform** (→helpdesk.ticket) |
| **Media** | MovieLens | [GroupLens](https://grouplens.org/datasets/movielens/) | Research/education | 20M ratings | **Partial-use** (content catalog) |
| **Pipeline** | Jaffle Shop | [GitHub](https://github.com/dbt-labs/jaffle-shop-data) | Apache 2.0 | Scalable | **Use as-is** (lakehouse testing) |
| **CRM** | CRM Dataset | [Kaggle](https://www.kaggle.com/datasets/gaurobsaha/customer-relationship-management-dataset) | Public | 5K rows | **Transform** (→crm.lead) |
| **PH Reference** | PSA OpenStat | [PSA](https://openstat.psa.gov.ph/) | PH Gov | Aggregate | **Partial-use** (reference data) |
| **PH Reference** | UACS Chart of Accounts | [UACS](https://uacs.gov.ph/resources/uacs/object-code/chart-of-accounts) | PH Gov | ~500 codes | **Transform** (→account.account) |

### Rejected Datasets

| Dataset | Reason |
|---------|--------|
| Instacart Market Basket | No pricing data; grocery-only categories |
| Amazon Products 1.4M | No transactions; too large for demo |
| Shopee Product Matching | Competition data restrictions; no transactions |
| AI Workforce Dataset | Aggregate industry data; not task-level |

---

## 3. Coverage and Gap Analysis

### Coverage Matrix

| Target Entity | Odoo Model | Public Data | Partially Covered | Must Synthesize | Hand-Author |
|--------------|------------|:-----------:|:-----------------:|:---------------:|:-----------:|
| **Companies/BUs** | `res.company` | | | | x |
| **Users/Roles** | `res.users` | | | | x |
| **Customers/Contacts** | `res.partner` | x | | | |
| **Products/SKUs** | `product.template` | x | | | |
| **Product Categories** | `product.category` | | x | | |
| **Sales Orders** | `sale.order` | x | | | |
| **Sales Order Lines** | `sale.order.line` | x | | | |
| **Invoices (AR)** | `account.move` (out) | x | | | |
| **Invoices (AP)** | `account.move` (in) | | | x | |
| **Payments** | `account.payment` | | x | | |
| **Journal Entries** | `account.move.line` | x | | | |
| **Chart of Accounts** | `account.account` | | x | | |
| **PH Tax Tables** | `account.tax` | | | | x |
| **Employees** | `hr.employee` | x | | | |
| **Departments** | `hr.department` | x | | | |
| **Job Positions** | `hr.job` | x | | | |
| **Payroll (PH)** | `hr.payslip` | | | x | |
| **Opportunities** | `crm.lead` | | x | | |
| **Campaigns** | `utm.campaign` | x | | | |
| **Mass Mailings** | `mailing.mailing` | | x | | |
| **Projects** | `project.project` | | | | x |
| **Tasks** | `project.task` | | | x | |
| **Milestones** | `project.milestone` | | | x | |
| **Vendors** | `res.partner` (supplier) | | x | | |
| **Purchase Orders** | `purchase.order` | | | x | |
| **Expenses** | `hr.expense` | | | x | |
| **Support Tickets** | `helpdesk.ticket` | x | | | |
| **Content Catalog** | custom media model | x | | | |
| **Subscriptions** | `sale.subscription` | | | x | |
| **KPI/OKR** | custom/Plane | | | x | |
| **Roadmap** | Plane projection | | | x | |
| **Agent Context** | Supabase + Databricks | | | x | |
| **Audit/History** | `mail.message` | | | x | |

### Summary

| Classification | Count | % |
|---------------|-------|---|
| Covered by public data | 12 | 36% |
| Partially covered | 7 | 21% |
| Must be synthesized | 11 | 33% |
| Hand-authored config/master | 4 | 12% |

---

## 4. Canonical Entity Model

Full entity model: [`docs/seed/CANONICAL_ENTITY_MODEL.md`](CANONICAL_ENTITY_MODEL.md)

### Entity Groups (Summary)

```
FOUNDATION (hand-authored)
├── res.company (2: InsightPulse AI, TBWA\SMP)
├── res.users (5: CEO, DevOps, Finance, PM, Portal)
├── res.country.state (PH provinces — from Odoo base)
└── account.tax (PH BIR tax rates — hand-authored)

MASTER DATA (public + synthesized)
├── res.partner (10K customers + 500 vendors)
├── product.template (5K products)
├── product.category (200 categories)
├── hr.employee (300 employees)
├── hr.department (15 departments)
└── account.account (200 accounts — PH CoA)

TRANSACTIONAL (public-sourced + synthesized)
├── sale.order + lines (10K orders)
├── purchase.order + lines (2K POs)
├── account.move (15K invoices/bills)
├── account.payment (8K payments)
├── crm.lead (5K opportunities)
├── project.task (500 tasks)
├── helpdesk.ticket (5K tickets)
└── hr.expense (1K expenses)

ANALYTICAL (synthesized for lakehouse)
├── utm.campaign (200 campaigns)
├── mailing.mailing (500 mailings)
├── content.catalog (1K media items — custom)
└── agent.task.log (10K agent events — Supabase)

PROJECTIONS (derived, not seeded directly)
├── Plane: issues/sprints/roadmap
├── Supabase: read mirror of Odoo entities
└── Databricks: bronze/silver/gold tables
```

---

## 5. Public Dataset Usage and Seeding Instructions

### 5.1 Olist Brazilian E-Commerce → Odoo Sales/Products/Partners

**Ingestion approach**: Download 8 CSVs from Kaggle → Python transformation script → Odoo XML-RPC import

**Field mapping**:

| Olist Field | Odoo Model.Field | Transformation |
|-------------|------------------|----------------|
| `customer_id` | `res.partner.ref` | Prefix `OLIST_` |
| `customer_city` | `res.partner.city` | Map BR→PH cities via lookup table |
| `customer_state` | `res.partner.state_id` | Map BR states→PH provinces |
| `order_id` | `sale.order.client_order_ref` | Prefix `OLIST_` |
| `order_status` | `sale.order.state` | delivered→sale, canceled→cancel, shipped→sale |
| `order_purchase_timestamp` | `sale.order.date_order` | Normalize to UTC, shift to 2025-2026 range |
| `product_id` | `product.template.default_code` | Prefix `OLIST_` |
| `product_category_name_english` | `product.category.name` | Direct map |
| `price` | `sale.order.line.price_unit` | BRL→PHP at 10.5 rate |
| `freight_value` | `sale.order.line` (delivery product) | BRL→PHP |
| `payment_type` | `account.payment.journal_id` | credit_card→Bank, boleto→Cash, voucher→Cash |
| `payment_value` | `account.payment.amount` | BRL→PHP |
| `review_score` | `mail.message` (rating) | Direct 1-5 scale |

**Date normalization**: Shift all timestamps forward by +N years to land in 2025-01 to 2026-03 range. Preserve day-of-week and seasonality.

**ID strategy**: All imported records get `ref` field with `OLIST_<original_id>`. Odoo assigns internal IDs. Cross-system key: `ref` field.

**Deduplication**: Match on `ref` field. Upsert pattern: search by ref, create if missing, skip if exists.

**Privacy**: Olist dataset is already anonymized (no real names/emails). Generate synthetic Filipino names via Faker for `res.partner.name`.

**Seeding into systems**:
- **Odoo**: `scripts/seed/import_olist.py` — XML-RPC import via `odoo-bin shell` or JSON-RPC
- **Supabase**: After Odoo import, CDC via `scripts/seed/sync_odoo_to_supabase.py`
- **Databricks**: Ingest raw CSVs to `bronze.olist_*`, transform to `silver.sales_*`, aggregate to `gold.sales_summary`
- **Plane**: Not applicable (no project/task data)

### 5.2 IBM HR Analytics → Odoo HR

**Field mapping**:

| IBM Field | Odoo Model.Field | Transformation |
|-----------|------------------|----------------|
| `Age` | `hr.employee.birthday` | Compute from current_date - Age |
| `Department` | `hr.department.name` | Direct map (Sales, R&D, HR) |
| `JobRole` | `hr.job.name` | Direct map |
| `MonthlyIncome` | `hr.contract.wage` | USD→PHP at 56 rate |
| `Gender` | `hr.employee.gender` | Male→male, Female→female |
| `MaritalStatus` | `hr.employee.marital` | Single→single, Married→married, Divorced→divorced |
| `Education` | `hr.employee.study_level` | 1→Below Secondary, 2→Bachelor, 3→Master, 4→Doctor |
| `YearsAtCompany` | `hr.employee.first_contract_date` | Compute from current_date - years |

**Date normalization**: Compute dates from relative fields (Age, YearsAtCompany) against 2026-03-17.

**Seeding**: XML-RPC import. Assign employees to PH-localized departments.

### 5.3 Support Tickets → Odoo Helpdesk

**Field mapping**:

| Ticket Field | Odoo Model.Field | Transformation |
|-------------|------------------|----------------|
| `Ticket_ID` | `helpdesk.ticket.name` | Prefix `SEED_` |
| `Customer_Name` | `res.partner.name` (link) | Match or create partner |
| `Customer_Email` | `res.partner.email` | Direct |
| `Ticket_Type` | `helpdesk.ticket.category_id` | Map Technical/Billing/General |
| `Ticket_Subject` | `helpdesk.ticket.name` | Direct |
| `Ticket_Description` | `helpdesk.ticket.description` | Direct |
| `Ticket_Status` | `helpdesk.ticket.stage_id` | Map Open/Pending/Closed to stages |
| `Ticket_Priority` | `helpdesk.ticket.priority` | Map Low→0, Medium→1, High→2, Critical→3 |
| `Customer_Satisfaction_Rating` | `rating.rating.rating` | Direct 1-5 |

### 5.4 Campaign Performance → Odoo Marketing

**Field mapping**:

| Campaign Field | Odoo Model.Field |
|---------------|------------------|
| `Campaign_ID` | `utm.campaign.name` |
| `Campaign_Type` | `utm.medium.name` (Email/Social/Display/Search) |
| `Channel_Used` | `utm.source.name` |
| `Conversion_Rate` | Custom field on `utm.campaign` |
| `ROI` | Custom field on `utm.campaign` |
| `Clicks` / `Impressions` | Databricks gold table (not in Odoo) |

### 5.5 Jaffle Shop → Databricks Lakehouse

**No Odoo import needed**. Jaffle Shop seeds directly into Databricks:

```
bronze.jaffle_raw_customers  ← raw_customers.csv
bronze.jaffle_raw_orders     ← raw_orders.csv
bronze.jaffle_raw_payments   ← raw_payments.csv

silver.jaffle_customers      ← cleaned, deduplicated
silver.jaffle_orders         ← joined with payments
silver.jaffle_payments       ← categorized

gold.jaffle_customer_summary ← lifetime value, order count, recency
```

---

## 6. Synthetic Generation Spec for Uncovered Gaps

Full specification: [`docs/seed/SYNTHETIC_GAP_SPEC.md`](SYNTHETIC_GAP_SPEC.md)

### Summary of What Must Be Synthesized

| Entity | Rows | Generator | Rationale |
|--------|------|-----------|-----------|
| PH Customer/Vendor Partners | 10K+500 | `Faker('fil_PH')` | No public PH transactional data |
| PH Chart of Accounts | 200 | Manual from UACS/BIR | No machine-readable PH CoA exists |
| BIR Tax Tables | 30 | Hand-authored | Regulatory — must be exact |
| Purchase Orders | 2K | PyDataFaker | No public PO datasets with Odoo-compatible schema |
| Vendor Bills | 3K | PyDataFaker | No public AP datasets |
| PH Payroll | 300/mo × 12 | Custom generator | PH-specific SSS/PhilHealth/Pag-IBIG/BIR brackets |
| Expenses | 1K | PyDataFaker + Faker | No public expense datasets |
| CRM Pipeline | 5K | Faker + stage distribution | No public dataset with Odoo CRM stages |
| Project Tasks | 500 | Hand-authored + generated | Domain-specific to IPAI operations |
| Milestones | 50 | Hand-authored | Domain-specific |
| Subscriptions | 200 | Custom generator | No public subscription lifecycle data |
| KPI/OKR | 100 | Hand-authored | Domain-specific |
| Agent Task Logs | 10K | Custom generator | No public MCP agent datasets exist |
| Audit Trail | derived | Post-seed `mail.message` generation | Odoo generates automatically on record changes |

**All synthetic data clearly labeled**: Every synthetic record gets `ref` field prefixed `SYNTH_` and `note` field containing `[SYNTHETIC] Generated for demo/testing purposes`.

---

## 7. Environment Seeding Order

### Dependency Order (must be sequential)

```
Phase 0: Foundation (hand-authored)
  ├── 0.1 res.company (2 companies)
  ├── 0.2 res.users (5 users + groups)
  ├── 0.3 account.account (PH CoA, 200 accounts)
  ├── 0.4 account.tax (BIR tax rates, 30 records)
  ├── 0.5 account.journal (6 journals)
  └── 0.6 account.fiscal.position (PH fiscal positions)

Phase 1: Master Data (public + synthetic)
  ├── 1.1 product.category (200 categories — from Olist + synthetic)
  ├── 1.2 product.template (5K products — from Olist + Amazon subset + synthetic)
  ├── 1.3 res.partner [customers] (10K — from Olist adapted + Faker PH)
  ├── 1.4 res.partner [vendors] (500 — synthetic PH)
  ├── 1.5 hr.department (15 — from IBM + PH-adapted)
  ├── 1.6 hr.job (40 — from IBM + PH-adapted)
  ├── 1.7 hr.employee (300 — from IBM + HR Set + Faker PH)
  └── 1.8 utm.campaign + utm.source + utm.medium (200+50+10 — from Campaign dataset)

Phase 2: Transactional Data (public-sourced + synthetic)
  ├── 2.1 sale.order + sale.order.line (10K orders — from Olist + UCI adapted)
  ├── 2.2 account.move [out_invoice] (8K — derived from sales)
  ├── 2.3 account.payment [customer] (6K — from Olist payments adapted)
  ├── 2.4 purchase.order + purchase.order.line (2K — synthetic)
  ├── 2.5 account.move [in_invoice] (3K — derived from purchases)
  ├── 2.6 account.payment [vendor] (2K — synthetic)
  ├── 2.7 crm.lead (5K — from CRM dataset adapted)
  ├── 2.8 hr.expense (1K — synthetic)
  └── 2.9 hr.payslip (3.6K — synthetic PH, 300 employees × 12 months)

Phase 3: Operational Data (synthetic + public)
  ├── 3.1 project.project (20 — hand-authored IPAI projects)
  ├── 3.2 project.task (500 — synthetic + existing finance/BIR tasks)
  ├── 3.3 project.milestone (50 — hand-authored)
  ├── 3.4 helpdesk.ticket (5K — from Support Tickets dataset)
  ├── 3.5 mailing.mailing (500 — from Email Campaign adapted)
  └── 3.6 sale.subscription (200 — synthetic)

Phase 4: Intelligence Layer (Supabase + Databricks)
  ├── 4.1 Supabase: mirror Odoo master data (CDC script)
  ├── 4.2 Supabase: agent task logs (10K — synthetic)
  ├── 4.3 Databricks bronze: raw CSVs (Olist, Jaffle Shop, UCI)
  ├── 4.4 Databricks silver: cleaned/joined tables
  ├── 4.5 Databricks gold: aggregated metrics
  └── 4.6 Databricks semantic: agent-ready context tables

Phase 5: Projections
  ├── 5.1 Plane: projects → issues/sprints (scripted via Plane API)
  ├── 5.2 Plane: roadmap items → quarterly milestones
  └── 5.3 Plane: KPI/OKR structures

Phase 6: Validation
  ├── 6.1 scripts/odoo/validate_seed_state.py
  ├── 6.2 Referential integrity checks
  ├── 6.3 Record count assertions
  ├── 6.4 Cross-system consistency checks
  └── 6.5 Evidence emission to docs/evidence/
```

### Environment Split

| Environment | Seed Pack | Scale | Purpose |
|-------------|-----------|-------|---------|
| `dev` (`odoo_dev`) | Minimum viable | ~5K records | Inner-loop development |
| `test` (`test_seed`) | Minimum viable (disposable) | ~5K records | Automated testing |
| `staging/demo` (`odoo_staging`) | Full simulation | ~50K records | Demos, stakeholder reviews |
| `simulation sandbox` (`odoo_dev_demo`) | Full simulation + anomalies | ~500K records | BI, forecasting, agent grounding |

### Idempotency Rules

- All seed scripts use search-or-create pattern (match on `ref` or business key)
- Re-running a seed script on an already-seeded DB is a no-op
- Upsert: match on `ref` field, update if changed, create if missing
- Never delete-and-recreate — only additive operations

### Rollback/Reset Strategy

```bash
# Full reset (dev only — NEVER production)
dropdb odoo_dev && createdb odoo_dev
python3 scripts/seed/run_full_seed.py --env=dev --plan=ssot/migration/production_seed_plan.yaml

# Partial reset (remove synthetic data only)
python3 scripts/seed/reset_synthetic.py --db=odoo_dev --prefix=SYNTH_

# Verify state after reset
python3 scripts/odoo/validate_seed_state.py --db=odoo_dev
```

---

## 8. Validation and Realism Checklist

### Data Quality Checks

- [ ] **Referential integrity**: Every `sale.order.partner_id` points to existing `res.partner`
- [ ] **No orphans**: Every `sale.order.line` has a valid `order_id`
- [ ] **Date consistency**: `invoice_date` >= `order_date` for linked records
- [ ] **Amount consistency**: Invoice totals match sum of order lines × unit price
- [ ] **Status distribution**: Not all records in same state (realistic mix)
- [ ] **Currency**: All PH transactions in PHP; multi-currency for international
- [ ] **Tax calculation**: BIR tax amounts match TRAIN law brackets
- [ ] **Multi-company**: Records properly isolated by company

### Realism Checks

- [ ] **Cardinality**: Average 2.5 lines per order (not 1, not 50)
- [ ] **Seasonality**: Higher sales in Nov-Dec (holiday season), lower in Jan-Feb
- [ ] **Status distribution**: ~60% completed, ~25% in-progress, ~10% cancelled, ~5% draft
- [ ] **Payment terms**: Mix of immediate (30%), 15 days (40%), 30 days (25%), 60 days (5%)
- [ ] **Revenue distribution**: Pareto — top 20% customers = 80% revenue
- [ ] **Geographic distribution**: 60% NCR, 15% CALABARZON, 10% Central Luzon, 15% others
- [ ] **Employee tenure**: Mean 3.5 years, skewed right (many new, few tenured)
- [ ] **Null/error conditions**: 2-5% missing phone numbers, 1% duplicate emails, 0.5% invalid addresses

### Cross-System Consistency

- [ ] Odoo `res.partner` count matches Supabase `partners` view
- [ ] Odoo `sale.order` totals match Databricks `gold.sales_summary`
- [ ] Plane issue count matches Odoo `project.task` count for synced projects
- [ ] Agent context in Databricks covers all Odoo master data entities

---

## 9. Risks / Assumptions / Limitations

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Olist CC BY-NC-SA license restricts commercial use | Medium | Used for internal demos only; not redistributed |
| UCI dataset is UK-centric | Low | Locale adaptation transforms geography |
| PH chart of accounts requires manual build | High | Start from UACS + BIR references; validate with PH accountant |
| Synthetic data may not reflect real PH market patterns | Medium | Use PSA OpenStat for realistic distributions |
| Databricks sample datasets may change across workspace versions | Low | Pin to known dataset versions; copy to managed tables |

### Assumptions

1. Odoo 19 CE `base` module provides country/state/currency data for PH
2. `Faker('fil_PH')` provides realistic Filipino names, addresses, phone numbers
3. BRL→PHP currency conversion at 10.5 is acceptable for demo purposes
4. All demo environments are private; no public-facing demo with real dataset names
5. Odoo demo data (`--demo=all`) provides base module structure but insufficient volume

### Limitations

1. No public PH transactional retail dataset exists — synthetic generation required
2. No public Odoo-native demo data beyond built-in ~50-100 records per module
3. MCP agent orchestration data must be fully synthesized — no public benchmarks
4. PayPal/Stripe-style payment gateway data not available publicly
5. Real BIR filing data cannot be used — synthetic tax transactions only

---

## 10. Final Recommendation

### Minimum Viable Seed Pack (Phase 1 — immediate)

| Source | Records | Target | Effort |
|--------|---------|--------|--------|
| Odoo `--demo=all` | ~500 | Base module structure | 5 min |
| `seed_prod_users.py` | 7 | Companies + users | 2 min |
| Existing IPAI seed modules | 488 | Finance/project/AI/BIR | 10 min |
| Olist (adapted, 10% sample) | ~10K | Sales + products + partners | 2 hrs |
| IBM HR (adapted) | 300 | Employees + departments | 1 hr |
| Faker PH partners | 1K | PH-localized contacts | 30 min |
| **Total** | **~12K** | | **~4 hrs** |

### Full Simulation Seed Pack (Phase 2 — 1-2 weeks)

| Source | Records | Target | Effort |
|--------|---------|--------|--------|
| Everything in MVP | 12K | Base | included |
| Olist (full, adapted) | ~100K | Sales pipeline | 1 day |
| UCI Online Retail II | ~200K | High-volume invoicing | 1 day |
| Support Tickets | 50K | Helpdesk | 4 hrs |
| Campaign Performance | 200K | Marketing analytics | 4 hrs |
| Faker PH (full) | 10K+500 | Partners + vendors | 2 hrs |
| Synthetic POs/expenses | 3K | Procurement | 4 hrs |
| Synthetic payroll (12 months) | 3.6K | HR/BIR | 1 day |
| Jaffle Shop → Databricks | scalable | Lakehouse validation | 4 hrs |
| Agent task logs → Supabase | 10K | Agent testing | 4 hrs |
| **Total** | **~500K** | | **~1-2 weeks** |

---

## Required Output Artifacts

| Artifact | Location | Status |
|----------|----------|--------|
| Seed data strategy (this doc) | `docs/seed/SEED_DATA_STRATEGY.md` | Created |
| Public dataset registry | `docs/research/seed-data-registry.md` | Created |
| Canonical entity model | `docs/seed/CANONICAL_ENTITY_MODEL.md` | Created |
| Synthetic gap spec | `docs/seed/SYNTHETIC_GAP_SPEC.md` | Created |
| Existing seed inventory | `docs/architecture/SEED_DATA_INVENTORY.md` | Exists (465 lines) |
| Production seed plan | `ssot/migration/production_seed_plan.yaml` | Exists (180 lines) |
| Dedup canonical map | `ssot/migration/seed_canonical_map.yaml` | Exists (120 lines) |
| Seed validation script | `scripts/odoo/validate_seed_state.py` | Exists |
| User seed script | `scripts/odoo/seed_prod_users.py` | Exists |
| Transformation scripts | `scripts/seed/import_*.py` | TODO |
| Faker PH generator | `scripts/seed/generate_ph_partners.py` | TODO |
| Synthetic PO generator | `scripts/seed/generate_purchase_orders.py` | TODO |
| Payroll generator | `scripts/seed/generate_ph_payroll.py` | TODO |
| Databricks seed notebooks | `data-intelligence/seeds/` | TODO |
| Supabase seed SQL | `supabase/seeds/` | Partial (3 files exist) |
| Seed integrity tests | `tests/data/test_seed_integrity.py` | TODO |

---

*Last updated: 2026-03-17*
