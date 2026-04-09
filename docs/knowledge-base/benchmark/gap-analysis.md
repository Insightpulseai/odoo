# Gap Analysis: SAP-Grade vs Odoo 18 CE + OCA

## Methodology

Each gap is classified:
- **F** = Fit (Odoo CE covers this natively)
- **C** = Config (achievable through Odoo configuration, no code)
- **O** = OCA (covered by OCA module at 18.0)
- **D** = Delta (requires ipai_* custom module)
- **E** = External (requires Azure/external service)
- **G** = Gap (no clear path, document and defer)

## Gap Summary by Domain

### Finance & Accounting

| Capability | Classification | Notes |
|-----------|---------------|-------|
| General ledger | F | Native Odoo accounting |
| Multi-company accounting | F | Native multi-company |
| Accounts payable | F | Native + OCA payment order |
| Accounts receivable | F | Native invoicing + follow-up |
| Bank reconciliation | O | OCA statement import + reconcile models |
| Fixed assets | O | OCA account_asset_management |
| Financial reports (TB, BS, P&L) | O | OCA account_financial_report |
| Management reports (custom) | O | OCA mis_builder |
| Parallel ledgers | G | Not available in CE; low priority for current scope |
| Automated period close | D | ipai_finance_ppm for close workflow |
| Cash forecasting | E | Databricks analytics |
| Intercompany elimination | O | OCA inter_company_rules (basic) |

### Procurement

| Capability | Classification | Notes |
|-----------|---------------|-------|
| Purchase orders | F | Native purchase module |
| Purchase requisitions | O | OCA purchase_request |
| Multi-level approval | O | OCA base_tier_validation |
| Blanket orders | O | OCA purchase_blanket_order |
| 3-way matching | O | OCA purchase_stock_picking_invoice_link (partial) |
| Vendor evaluation/scoring | D | Needs ipai_* or external |
| Source lists / quota arrangement | G | Not available; low priority |
| Contract lifecycle management | G | Basic in CE; full CLM needs external tool |

### Sales & CRM

| Capability | Classification | Notes |
|-----------|---------------|-------|
| Lead/opportunity management | F | Native CRM |
| Sales pipeline | F | Native CRM stages |
| Quotation management | F | Native sales |
| Pricelists | F | Native pricelist engine |
| Sales approval | O | OCA sale_tier_validation |
| Order type classification | O | OCA sale_order_type |
| Territory management | G | Not available; workaround via sales teams |
| Commission management | G | Not in CE; needs external or ipai_* |
| Complex pricing conditions | D | Pricelists cover 80%; complex conditions need custom |

### Inventory & Supply Chain

| Capability | Classification | Notes |
|-----------|---------------|-------|
| Multi-warehouse | F | Native |
| Lot/serial tracking | F | Native |
| Routes and rules | F | Native (strong in CE) |
| Multi-step picking | F | Native |
| MRP | F | Native (CE includes MRP) |
| Reordering rules | F | Native |
| Barcode scanning | D/E | CE has basic; EE has advanced; OCA stock_barcodes |
| Wave picking | G | Not in CE |
| Cross-docking | C | Configurable via routes |
| Demand planning | E | Databricks ML |
| Consignment stock | G | Not natively supported |

### HR & Payroll

| Capability | Classification | Notes |
|-----------|---------------|-------|
| Employee master data | F | Native HR |
| Leave management | F | Native |
| Attendance | F | Native |
| Basic payroll | F | Native (very basic) |
| PH SSS computation | D | ipai_hr_ph_sss needed |
| PH PhilHealth | D | ipai_hr_ph_philhealth needed |
| PH Pag-IBIG | D | ipai_hr_ph_pagibig needed |
| PH BIR withholding on compensation | D | ipai_hr_ph_bir needed |
| Talent management | G | Not in CE; EE has appraisals |
| Position management | G | Not available; basic via hr.job |

### Tax & Compliance

| Capability | Classification | Notes |
|-----------|---------------|-------|
| VAT computation | F | Native tax engine |
| Withholding tax (basic) | F | Native tax with WHT type |
| PH expanded WHT (BIR 2307) | D | ipai_bir_2307 needed |
| PH SLSP | D | ipai_bir_slsp needed |
| E-invoicing | D/G | Depends on BIR requirements |
| SoD matrix | D | Custom validation on groups |
| Audit trail | F | Native via mail.thread |
| Document retention | O | OCA dms |

### Integration & Platform

| Capability | Classification | Notes |
|-----------|---------------|-------|
| REST API | O | OCA base_rest / fastapi |
| XML-RPC / JSON-RPC | F | Native |
| Async job processing | O | OCA queue_job |
| Document intelligence | E | Azure Document Intelligence |
| Identity federation | O | OCA auth_oidc + Entra ID |
| Enterprise BI | E | Power BI + Databricks |
| AI copilot | E | Azure AI Foundry |
| Container deployment | E | Azure Container Apps |
| IaC | E | Bicep templates |

## Priority Classification

### P1 — Required Now (Day 1-30)
All **F** and **O** classifications for finance, procurement, sales, inventory.
These form the operational baseline.

### P2 — Required Next Quarter (Day 31-60)
All **D** classifications for PH tax compliance, management accounting.
Platform layer (ACA, Entra ID, monitoring).

### P3 — Required Later
HR/payroll PH statutory compliance.
Advanced reporting and BI.
AI integration.

### P4 — Future / Deferred
Items classified as **G** (gaps) with no clear path.
These should be documented but not block progress.

## Risk: Gaps That Matter Most

1. **PH tax compliance**: BIR 2307/SLSP are legally required for most businesses. No OCA solution exists. Must build ipai_* modules. **High priority, non-deferrable.**

2. **Management accounting depth**: MIS Builder covers 70% of CO-level reporting. Complex allocation and transfer pricing need Databricks. **Medium priority, Databricks dependency.**

3. **3-way matching enforcement**: Currently manual in Odoo. Risk of paying for undelivered goods. **Medium priority, process control dependency.**

4. **SoD enforcement**: No native SoD matrix. Risk of audit findings. **Medium priority, governance dependency.**
