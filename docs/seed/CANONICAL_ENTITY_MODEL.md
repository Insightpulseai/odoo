# Canonical Entity Model — Seed Data

> Defines the full entity set required for the InsightPulse AI platform seed.
> Reference: `docs/seed/SEED_DATA_STRATEGY.md`

---

## Entity Groups

### Group 0: Foundation (Hand-Authored Configuration)

| Entity | Odoo Model | Records | Source | Cross-System Key |
|--------|------------|---------|--------|-----------------|
| Companies | `res.company` | 2 | Hand-authored | `company.ref` |
| Business Units | `res.company` (child) | 3 | Hand-authored | `company.ref` |
| Users | `res.users` | 5+ | `seed_prod_users.py` | `login` (email) |
| User Groups/Roles | `res.groups` | Odoo-managed | Module install | `xml_id` |
| Currencies | `res.currency` | ~3 (PHP, USD, EUR) | Odoo base | ISO code |
| Countries/States | `res.country`, `res.country.state` | Odoo base | Odoo base | `code` |
| PH Provinces | `res.country.state` | 81 | Odoo `l10n_ph` or manual | `code` |

#### Company Structure

```
InsightPulse AI (PH) [parent]
├── IPAI Digital (PH) [child - digital services]
├── IPAI Retail (PH) [child - retail operations]
└── TBWA\Santiago Mangada Puno (PH) [sibling - agency]
```

### Group 1: Accounting Foundation (Hand-Authored + Public Reference)

| Entity | Odoo Model | Records | Source | Notes |
|--------|------------|---------|--------|-------|
| Chart of Accounts | `account.account` | 200 | UACS/BIR reference + manual | PH-compliant |
| Account Types | `account.account.type` | Odoo-managed | Module install | |
| Journals | `account.journal` | 6 | Hand-authored | Sales, Purchase, Bank, Cash, Misc, Exchange |
| Tax Rates | `account.tax` | 30 | BIR TRAIN law (hand-authored) | Must be exact |
| Fiscal Positions | `account.fiscal.position` | 5 | Hand-authored | VAT, Non-VAT, Exempt, Zero-rated, Government |
| Payment Terms | `account.payment.term` | 5 | Hand-authored | Immediate, 15d, 30d, 60d, End of Month |
| Fiscal Year | `account.fiscal.year` | 2 | Hand-authored | 2025, 2026 |
| Bank Accounts | `res.partner.bank` | 3 | Hand-authored | BDO, BPI, MetroBank |

#### PH Chart of Accounts (Top-Level)

```
1000 Assets
  1100 Current Assets
    1110 Cash and Cash Equivalents
    1120 Trade Receivables
    1130 Inventories
    1140 Prepayments
  1200 Non-Current Assets
    1210 Property, Plant and Equipment
    1220 Intangible Assets

2000 Liabilities
  2100 Current Liabilities
    2110 Trade Payables
    2120 Accrued Expenses
    2130 Tax Payables (BIR)
    2140 SSS/PhilHealth/Pag-IBIG Payable
  2200 Non-Current Liabilities

3000 Equity
  3100 Share Capital
  3200 Retained Earnings

4000 Revenue
  4100 Service Revenue
  4200 Product Sales
  4300 Digital Services Revenue

5000 Cost of Revenue
  5100 Direct Labor
  5200 Direct Materials

6000 Operating Expenses
  6100 Salaries and Wages
  6200 Rent
  6300 Utilities
  6400 Marketing
  6500 Depreciation
  6600 Professional Fees

7000 Other Income/Expenses
  7100 Interest Income
  7200 Foreign Exchange Gain/Loss
```

#### BIR Tax Rates (2025 TRAIN Law)

```
VAT Output Tax:       12% (standard)
VAT Input Tax:        12% (standard)
Withholding Tax:      1%, 2%, 5%, 10%, 15% (by category)
Income Tax:           0-35% progressive (per TRAIN brackets)
SSS Contribution:     5% EE + 10% ER (max base ₱35,000)
PhilHealth:           2.5% EE + 2.5% ER (base ₱10K-₱100K)
Pag-IBIG:             2% EE + 2% ER (max base ₱5,000)
```

### Group 2: Master Data — Partners

| Entity | Odoo Model | Records | Source | Key Fields |
|--------|------------|---------|--------|------------|
| Customers (PH) | `res.partner` | 8,000 | Faker('fil_PH') | name, email, phone, street, city, state_id, vat |
| Customers (intl) | `res.partner` | 2,000 | Olist adapted | name, email, country_id |
| Vendors (PH) | `res.partner` (supplier) | 400 | Faker('fil_PH') | name, email, vat, supplier_rank |
| Vendors (intl) | `res.partner` (supplier) | 100 | Olist sellers adapted | name, country_id |

#### Partner Distribution

| Segment | % | Count | Avg Revenue/yr |
|---------|---|-------|---------------|
| Enterprise | 5% | 500 | ₱2M+ |
| Mid-market | 15% | 1,500 | ₱200K-2M |
| SMB | 40% | 4,000 | ₱20K-200K |
| Micro/Individual | 40% | 4,000 | <₱20K |

#### Geographic Distribution (PH)

| Region | % | Notes |
|--------|---|-------|
| NCR (Metro Manila) | 55% | Makati, BGC, Quezon City, Pasig |
| CALABARZON | 15% | Cavite, Laguna, Batangas |
| Central Luzon | 10% | Pampanga, Bulacan |
| Central Visayas | 8% | Cebu |
| Davao Region | 5% | Davao City |
| Others | 7% | Distributed |

### Group 3: Master Data — Products

| Entity | Odoo Model | Records | Source | Key Fields |
|--------|------------|---------|--------|------------|
| Product Categories | `product.category` | 200 | Olist categories + PH retail | name, parent_id |
| Products (goods) | `product.template` | 3,000 | Olist + Superstore adapted | name, type=consu, categ_id, list_price |
| Products (services) | `product.template` | 1,500 | Synthetic | name, type=service, list_price |
| Products (digital) | `product.template` | 500 | Synthetic | name, type=service, list_price |

#### Price Distribution

| Range (PHP) | % of Products |
|-------------|---------------|
| 0-500 | 30% |
| 500-2,000 | 35% |
| 2,000-10,000 | 20% |
| 10,000-50,000 | 10% |
| 50,000+ | 5% |

### Group 4: Master Data — HR

| Entity | Odoo Model | Records | Source |
|--------|------------|---------|--------|
| Departments | `hr.department` | 15 | IBM HR + PH-adapted |
| Job Positions | `hr.job` | 40 | IBM HR + PH-adapted |
| Employees | `hr.employee` | 300 | IBM HR + HR Set + Faker PH |
| Contracts | `hr.contract` | 300 | Synthetic (PH labor law) |

#### Department Distribution

| Department | Employees | Notes |
|-----------|-----------|-------|
| Engineering | 80 | Software, DevOps, QA |
| Sales | 50 | Account execs, SDRs |
| Finance | 30 | Accounting, Treasury, Tax |
| Marketing | 25 | Digital, Creative, Analytics |
| Operations | 30 | Logistics, Support |
| HR | 15 | Recruitment, Compensation |
| Executive | 10 | C-suite, Directors |
| Customer Success | 20 | CSMs, Implementation |
| Product | 15 | PMs, Designers |
| Legal/Compliance | 10 | Legal, Audit |
| IT | 15 | Infra, Security |

### Group 5: Transactional — Sales

| Entity | Odoo Model | Records | Source | Date Range |
|--------|------------|---------|--------|------------|
| Sales Orders | `sale.order` | 10,000 | Olist + UCI adapted | 2025-01 to 2026-03 |
| Sales Order Lines | `sale.order.line` | 25,000 | Olist adapted (avg 2.5 lines/order) | |
| Customer Invoices | `account.move` (out_invoice) | 8,000 | Derived from sales | |
| Customer Payments | `account.payment` | 6,000 | Olist payments adapted | |

### Group 6: Transactional — Purchasing

| Entity | Odoo Model | Records | Source | Date Range |
|--------|------------|---------|--------|------------|
| Purchase Orders | `purchase.order` | 2,000 | Synthetic | 2025-01 to 2026-03 |
| Purchase Order Lines | `purchase.order.line` | 5,000 | Synthetic | |
| Vendor Bills | `account.move` (in_invoice) | 3,000 | Derived from purchases | |
| Vendor Payments | `account.payment` | 2,000 | Synthetic | |

### Group 7: Transactional — CRM

| Entity | Odoo Model | Records | Source |
|--------|------------|---------|--------|
| Leads/Opportunities | `crm.lead` | 5,000 | CRM Dataset + synthetic |
| Sales Teams | `crm.team` | 5 | Hand-authored |
| Lost Reasons | `crm.lost.reason` | 10 | Hand-authored |

#### Pipeline Stage Distribution

| Stage | % | Records |
|-------|---|---------|
| New | 15% | 750 |
| Qualified | 20% | 1,000 |
| Proposition | 15% | 750 |
| Negotiation | 10% | 500 |
| Won | 25% | 1,250 |
| Lost | 15% | 750 |

### Group 8: Transactional — Projects & Tasks

| Entity | Odoo Model | Records | Source |
|--------|------------|---------|--------|
| Projects | `project.project` | 20 | Hand-authored (IPAI operations) |
| Tasks | `project.task` | 500 | Existing seed (BIR/finance) + synthetic |
| Task Stages | `project.task.type` | 5 per project | Existing seed |
| Milestones | `project.milestone` | 50 | Hand-authored |
| Activities | `mail.activity` | 200 | Synthetic |

### Group 9: Transactional — Support

| Entity | Odoo Model | Records | Source |
|--------|------------|---------|--------|
| Helpdesk Tickets | `helpdesk.ticket` | 5,000 | Customer Support Tickets dataset |
| Ticket Categories | `helpdesk.ticket.category` | 10 | Hand-authored |
| SLA Policies | `helpdesk.sla` | 5 | Hand-authored |

### Group 10: Transactional — HR Payroll

| Entity | Odoo Model | Records | Source |
|--------|------------|---------|--------|
| Payslips | `hr.payslip` | 3,600 | Synthetic (300 EE × 12 months) |
| Payslip Lines | `hr.payslip.line` | 25,200 | Synthetic (7 lines/slip avg) |
| Expenses | `hr.expense` | 1,000 | Synthetic PH |
| Leave Allocations | `hr.leave.allocation` | 300 | Synthetic |

### Group 11: Marketing & Campaigns

| Entity | Odoo Model | Records | Source |
|--------|------------|---------|--------|
| UTM Campaigns | `utm.campaign` | 200 | Campaign Performance dataset |
| UTM Sources | `utm.source` | 50 | Campaign Performance dataset |
| UTM Mediums | `utm.medium` | 10 | Campaign Performance dataset |
| Mass Mailings | `mailing.mailing` | 500 | Email Campaign dataset adapted |
| Mailing Contacts | `mailing.contact` | 5,000 | Derived from res.partner |

### Group 12: Intelligence Layer (Non-Odoo)

| Entity | System | Records | Source |
|--------|--------|---------|--------|
| Agent Task Logs | Supabase `agent.task_log` | 10,000 | Synthetic |
| Agent Sessions | Supabase `agent.session` | 1,000 | Synthetic |
| Content Catalog | Databricks `gold.content_catalog` | 1,000 | MovieLens adapted |
| Sales Summary | Databricks `gold.sales_summary` | Derived | From Odoo CDC |
| Customer 360 | Databricks `gold.customer_360` | Derived | From Odoo CDC |

### Group 13: Cross-System Identifiers

| Source System | Target System | Key Type | Pattern |
|--------------|---------------|----------|---------|
| Odoo | Supabase | `odoo_id` | Integer (Odoo record ID) |
| Odoo | Databricks | `odoo_ref` | String (`OLIST_xxx`, `SYNTH_xxx`) |
| Odoo | Plane | `odoo_task_id` | Integer (project.task ID) |
| Supabase | Databricks | `supabase_id` | UUID |
| All | All | `platform_ref` | `{system}_{entity}_{id}` |

---

*Last updated: 2026-03-17*
