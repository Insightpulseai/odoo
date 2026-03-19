# Skill: SAP Concur Parity — Odoo CE + IPAI Replacement Map

## Metadata

| Field | Value |
|-------|-------|
| **id** | `sap-concur-parity` |
| **domain** | `finance_ops` |
| **source** | https://www.concur.com/products/travel-expense |
| **extracted** | 2026-03-15 |
| **applies_to** | odoo, agents, automations |
| **tags** | concur, expense, travel, invoice, parity, replacement, ee-surpass |

---

## Why This Exists

SAP Concur is the incumbent IPAI is replacing. This skill maps every Concur capability to its Odoo CE + OCA + IPAI equivalent, identifies gaps, and defines the build plan for parity.

## Concur Product → IPAI Replacement Matrix

### Expense Management

| Concur Feature | IPAI Equivalent | Status | Gap? |
|---------------|-----------------|--------|------|
| **Concur Expense** (core expense reporting) | Odoo `hr_expense` + OCA `hr_expense_*` | Deployed | No |
| **ExpenseIt** (mobile receipt scanning AI) | ADE (LandingAI) + Azure DI `prebuilt-receipt` → `hr.expense` | Planned | **Build**: n8n workflow for receipt → expense |
| **Bank Card Feeds** | OCA `account_bank_statement_import` + bank API | Partial | **Build**: automated bank feed import |
| **Company Bill Statements** | Odoo `account.move` (vendor bills) | Deployed | No |
| **Budget Management** | OCA `account_move_budget` + `mis_builder` | Deployed | No |
| **Concur Detect** (AI fraud detection) | `ipai_expense_anomaly` (planned) | Not started | **Build**: anomaly detection agent |
| **Concur Benefits Assurance** | N/A (Philippines context: PhilHealth/SSS) | N/A | Out of scope |
| **Concur Tax Assurance** | `ipai_bir_tax_compliance` + BIR engine | In progress | Partial — BIR-specific |
| **Intelligent Audit** (outsourced audit) | Agent-based expense audit workflow | Not started | **Build**: eval-driven audit agent |
| **Verify** (expense verification) | Odoo approval workflows + manager review | Deployed | No |
| **Drive** (mileage tracking) | Odoo `fleet` + OCA `hr_expense_fleet` | Available | Needs configuration |
| **Mileage Calculator** | Google Maps API + Odoo fleet | Not started | **Build**: distance calculation |

### Travel Management

| Concur Feature | IPAI Equivalent | Status | Gap? |
|---------------|-----------------|--------|------|
| **Concur Travel** (booking) | Not in scope | N/A | Defer — use external booking tools |
| **Concur Request** (pre-approval) | Odoo `purchase.request` + approval workflow | Deployed | No |
| **TripLink** (outside booking capture) | N/A | N/A | Defer |
| **Event Management** | Odoo `event` module | Available | Needs configuration |
| **TMC Integration** | N/A | N/A | Out of scope |
| **TravPay Hotel** | N/A | N/A | Out of scope |

### Invoice & Payment

| Concur Feature | IPAI Equivalent | Status | Gap? |
|---------------|-----------------|--------|------|
| **Concur Invoice** | Odoo `account.move` (vendor bills) + OCA `account_invoice_*` | Deployed | No |
| **Three-Way Match** | OCA `purchase_stock_picking_invoice_link` + `account_move_line_purchase_info` | Available | **Configure**: enable 3-way matching |
| **Purchase Request** | OCA `purchase_request` | Available | Needs install |
| **Payment Providers** | Odoo payment acquirers + bank transfers | Deployed | No |
| **AP Automation** | n8n workflow: ADE/DI extract → `account.move` create | Planned | **Build**: end-to-end AP pipeline |

### Data & Analytics

| Concur Feature | IPAI Equivalent | Status | Gap? |
|---------------|-----------------|--------|------|
| **Analytics Dashboard** | Apache Superset (`superset.insightpulseai.com`) | Deployed | No |
| **Budget Intelligence** | MIS Builder + Superset dashboards | Partial | **Build**: budget vs actual views |
| **Consultative Intelligence** | ipai-odoo-copilot-azure (Foundry agent) | Staging | Deploy copilot |
| **Data Delivery Service** | Databricks Medallion → Gold views | Planned | **Build**: ETL pipeline |
| **Joule** (SAP AI assistant) | ipai-odoo-copilot-azure | Staging | Our equivalent of Joule |

### Compliance & Tax

| Concur Feature | IPAI Equivalent | Status | Gap? |
|---------------|-----------------|--------|------|
| **Global tax management** | `ipai_bir_tax_compliance` (PH-specific) | In progress | PH-only, not global |
| **Statutory compliance** | BIR eFiling + withholding tax | In progress | Partial |
| **VAT reclaim** | Odoo `account_tax` + BIR VAT rules | Available | Needs BIR mapping |
| **Per diem management** | Odoo `hr_expense` + per diem rules | Available | Needs configuration |

## Parity Scorecard

| Category | Concur Features | IPAI Covered | Parity % |
|----------|----------------|-------------|----------|
| Expense Management | 12 | 7 | 58% |
| Travel Management | 6 | 1 | 17% |
| Invoice & Payment | 4 | 3 | 75% |
| Data & Analytics | 5 | 3 | 60% |
| Compliance & Tax | 4 | 2 | 50% |
| **Total** | **31** | **16** | **52%** |

**Note**: Travel management is intentionally deferred (not in IPAI scope). Excluding travel:

| Category (excl. Travel) | Concur Features | IPAI Covered | Parity % |
|--------------------------|----------------|-------------|----------|
| **Total (excl. Travel)** | **25** | **15** | **60%** |

## Top 5 Gaps to Close (Priority Order)

### 1. Receipt → Expense Automation (ExpenseIt equivalent)
**What**: Mobile receipt photo → OCR → structured data → `hr.expense` record
**How**: ADE parse → ADE extract (Pydantic schema) → n8n → Odoo XML-RPC
**Effort**: 1 week
**Impact**: Eliminates manual expense entry for all employees

### 2. Invoice → Vendor Bill Automation (AP Automation)
**What**: Vendor invoice PDF → extract → `account.move` (vendor bill)
**How**: Azure DI `prebuilt-invoice` → n8n → Odoo XML-RPC → manager approval
**Effort**: 1 week
**Impact**: Eliminates manual invoice data entry

### 3. Three-Way Match
**What**: Auto-match PO → receipt → invoice
**How**: Install + configure OCA `purchase_stock_picking_invoice_link`
**Effort**: 2 days
**Impact**: Catch billing discrepancies automatically

### 4. AI Expense Audit (Concur Detect equivalent)
**What**: Flag anomalous expenses (duplicate, out-of-policy, suspicious patterns)
**How**: Agent workflow: query expense data → apply rules + LLM reasoning → flag
**Effort**: 2 weeks
**Impact**: Reduces fraud risk without manual audit labor

### 5. Budget vs Actual Dashboard
**What**: Real-time budget tracking with variance analysis
**How**: MIS Builder reports + Superset dashboard
**Effort**: 3 days
**Impact**: Replaces Concur budget intelligence

## IPAI Advantages Over Concur

| Advantage | Details |
|-----------|---------|
| **Cost** | Odoo CE is free. Concur is $8-25/user/month + per-transaction fees |
| **BIR compliance** | Native PH tax compliance. Concur has no BIR integration |
| **Full ERP** | Expense + Accounting + Sales + Inventory + HR in one system |
| **AI flexibility** | Claude + ADE + Azure DI vs locked-in Joule/SAP AI |
| **Data ownership** | Self-hosted on Azure. Concur holds your data |
| **Customization** | Open source (OCA + ipai_*). Concur is closed SaaS |

## Concur Features Intentionally NOT Replicated

| Feature | Reason |
|---------|--------|
| Concur Travel (booking) | Not in IPAI scope — use external booking tools |
| TripLink | Requires TMC partnerships — not relevant for PH SME |
| Event Management | Low priority — Odoo `event` available if needed |
| Benefits Assurance | US-specific — PH uses PhilHealth/SSS/Pag-IBIG |
| Global multi-country tax | IPAI is PH-focused — BIR only |
