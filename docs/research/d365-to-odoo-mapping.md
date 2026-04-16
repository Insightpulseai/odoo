# D365 → Odoo 18 CE + OCA + `ipai_*` — Full Data Model & Business Logic Mapping

> Canonical mapping for every D365 Finance, Project Operations, and Finance Agents
> entity + business process to its Odoo 18 CE implementation.
> Doctrine per `CLAUDE.md`: CE → OCA → thin `ipai_*` delta. Never fork core.
> Companion: `docs/research/d365-data-model-inventory.md` (entity catalog only).
> Compiled 2026-04-15.

---

## 0. Stack doctrine

Every mapping follows the 3-layer order:

| Layer | Scope | Examples |
|---|---|---|
| 1. Odoo CE 18 | Built-in models + workflows | `account.move`, `project.project`, `hr.expense` |
| 2. OCA | Vetted community extensions | `account_asset_management`, `account_budget_oca`, `project_wbs` |
| 3. `ipai_*` | PH-specific / bridge / overlay only | `ipai_bir_tax_compliance`, `ipai_expense_liquidation` |

**Rule:** if a mapping requires only Layer 1+2, never build Layer 3.

---

## 1. D365 Finance → Odoo mapping

### 1.1 General Ledger

| D365 entity | D365 process | Odoo CE model | OCA ext | `ipai_*` | Business logic alignment |
|---|---|---|---|---|---|
| `MainAccount` | Define CoA | `account.account` | `account_financial_report` (report structure) | — | CE supports hierarchical CoA; `internal_group` + `internal_type` cover D365's `MainAccountType` |
| `Ledger` | Ledger per LE | `res.company` + `account.journal` | `account_consolidation` (multi-entity) | — | One Odoo company = one Ledger; multi-company enabled by `multi_company_ids` |
| `LedgerJournalTable` | Journal header | `account.move` | — | — | CE's `account.move` is the universal journal header (covers GL, AP, AR, bank) |
| `LedgerJournalTrans` | Journal line | `account.move.line` | — | — | CE supports debit/credit + dimensions via `analytic_distribution` |
| `FinancialDimension` | Cost center, project, dept dims | `account.analytic.account` + `account.analytic.plan` | `account_analytic_distribution_rule` | — | CE 18 supports multiple analytic plans (matches D365's multi-dim) |
| `DimensionAttributeValueCombination` | Dim combination | `account.analytic.distribution` (JSON) | — | — | CE 18 stores distributions as JSON on move lines |
| `FiscalCalendar` / `FiscalYear` / `FiscalPeriod` | Calendar structure | `account.fiscal.year` + period derived | — | — | CE uses continuous fiscal year with period locks via `fiscalyear_lock_date` / `tax_lock_date` |
| `Currency` | Multi-currency | `res.currency` | — | — | CE has full multi-currency |
| `CurrencyExchangeRate` | FX rates | `res.currency.rate` | `currency_rate_update` (auto-fetch) | — | OCA `currency_rate_update` auto-pulls from BSP, ECB, etc. |

**Business process — Period close:**
- D365: period-end close wizard, consolidation, FX revaluation, year-end carry-forward
- Odoo: `fiscalyear_lock_date` + `tax_lock_date` + `account_closing` (OCA) covers equivalent workflow
- `ipai_*` delta: none — CE+OCA sufficient

### 1.2 Accounts Payable

| D365 entity | D365 process | Odoo CE model | OCA ext | `ipai_*` | Alignment |
|---|---|---|---|---|---|
| `VendTable` | Vendor master | `res.partner` (supplier_rank>0) | `partner_firstname`, `partner_contact_*` | — | CE unifies customer+vendor partner; flag via `supplier_rank` |
| `PurchTable` / `PurchLine` | PO header/line | `purchase.order` / `purchase.order.line` | `purchase_*` series | — | Full purchase module in CE |
| `VendorInvoice` / `VendInvoiceTrans` | AP invoice | `account.move` (move_type=in_invoice) | — | — | — |
| `VendInvoiceInfoTable` | Pending invoice | `account.move` (state=draft) | `account_invoice_pending_to_post` | — | Draft = pending; post = approved |
| `MatchingReason` / `InvoiceMatching` | 2/3-way match | — | `account_invoice_three_way_match` | — | OCA adds receipt+invoice+PO matching |
| `VendorPaymentJournal` | Payment run | `account.payment` + `account.batch.payment` | `account_banking_sepa_credit_transfer`, `account_payment_partner` | — | SEPA/ACH/local via OCA |
| `VendorSettlement` | Invoice↔payment | `account.partial.reconcile` | — | — | Auto-reconciliation on payment register |
| `VendInvoiceCapture` | OCR invoice capture | — | `account_invoice_import_ocr` | `ipai_apiscan` (Document Intelligence bridge) | OCA has Tesseract-based; `ipai_*` wires Azure Document Intelligence |
| `BankRemittance` | Payment remittance | `account.payment` with journal | `account_banking_mandate`, `account_banking_sepa_direct_debit` | — | — |

**Business process — Invoice approval + payment:**
1. Vendor submits invoice → `account.move` (draft, in_invoice)
2. 3-way match: PO + receipt + invoice via OCA `account_invoice_three_way_match`
3. Tiered approval via OCA `base_tier_validation`
4. Post → state=posted
5. Batch payment proposal via OCA `account_payment_order`
6. Payment run → `account.payment` + bank file generated
7. Reconciliation auto-matches on bank statement import

### 1.3 Accounts Receivable

| D365 entity | D365 process | Odoo CE model | OCA ext | `ipai_*` | Alignment |
|---|---|---|---|---|---|
| `CustTable` | Customer master | `res.partner` (customer_rank>0) | — | — | — |
| `SalesTable` / `SalesLine` | Sales order | `sale.order` / `sale.order.line` | `sale_order_*` series | — | Full sale module in CE |
| `CustInvoiceJour` / `CustInvoiceTrans` | Customer invoice | `account.move` (move_type=out_invoice) | — | — | — |
| `CustPayment` | Customer payment | `account.payment` | `account_payment_partner` | — | — |
| `CustCollectionLetter` | Dunning letter | — | `account_credit_control` (primary), `account_followup_*` | `ipai_collections_ph` (optional) | OCA provides policy engine; `ipai_*` only if PH-specific tone/language |
| `CustInterestJournal` | Overdue interest | — | `account_invoice_interest` | — | OCA |
| `CreditLimit` / `CustCreditLimit` | Credit limit | `res.partner.credit_limit` | `account_credit_control_advanced`, `sale_order_credit_limit` | — | CE 18 has basic; OCA extends with hold-release |
| `SubscriptionBilling` | Subscription billing | — (Enterprise-only `sale_subscription`) | `contract` (OCA — full replacement) | `ipai_subscription_ph_tax` | Use OCA `contract` — avoids EE |
| `CreditTransactionLimit` | Block order on limit | — | `sale_order_credit_limit_oca` | — | Block-at-quote pattern |

**Business process — Order-to-cash:**
1. Lead → Opportunity (`crm.lead`) → Quote (`sale.order` state=draft)
2. Credit check via OCA `sale_order_credit_limit_oca` blocks over-limit orders
3. Order confirmed → `sale.order` state=sale
4. Delivery/service → `stock.picking` OR timesheet hours (project-based billing)
5. Invoice → `account.move` (out_invoice)
6. Dunning cycle via OCA `account_credit_control` runs on aging buckets
7. Payment received → `account.payment` + auto-reconciliation
8. For PH: `ipai_bir_tax_compliance` auto-generates BIR 2307 when customer withholds tax

### 1.4 Cash & Bank Management

| D365 entity | D365 process | Odoo CE model | OCA ext | `ipai_*` | Alignment |
|---|---|---|---|---|---|
| `BankAccountTable` | Bank account | `account.journal` (type=bank) + `res.partner.bank` | — | — | — |
| `BankStatementTable` / `BankStatementLine` | Statement header/line | `account.bank.statement` / `account.bank.statement.line` | `account_bank_statement_import_*` (CAMT53, OFX, MT940) | `ipai_bank_sync_ph` (BPI/BDO/Metrobank/Unionbank connectors) | CE has import framework; PH banks need custom parsers |
| `BankReconciliation` | Auto-reconciliation | `account.reconciliation` widget | `account_reconciliation_widget_*` | — | CE 18 has modern reconciliation widget |
| `CashFlowForecast` | Cash flow forecast | — | `account_cash_flow_forecast`, `account_cash_flow_report` | — | — |
| `MatchBankDocumentLine` | Matched pair | `account.partial.reconcile` | — | — | — |

**Business process — Bank reconciliation:**
1. Statement imported (manual upload or OCA auto-fetch)
2. Auto-match via `ir.model.reconcile.model` rules
3. Manual review on unmatched
4. Post → updates GL via journal entry
5. Cash flow forecast computed from open invoices + payment patterns

### 1.5 Fixed Assets

| D365 entity | D365 process | Odoo CE model | OCA ext | `ipai_*` | Alignment |
|---|---|---|---|---|---|
| `AssetTable` | Asset master | — (EE-only in CE) | `account_asset_management` (full replacement) | — | Use OCA; never EE |
| `AssetBook` | Multi-valuation book | — | `account_asset_management_multibook` | — | — |
| `AssetGroup` | Asset category | — | `account.asset.profile` | — | OCA's `profile` = D365's `AssetGroup` |
| `AssetDepreciationJournal` | Depreciation run | — | `account_asset_management` (`account.asset.depreciation.line.run`) | — | Monthly cron + manual run |
| `AssetDepreciationMethod` | Dep method | — | OCA (SL, DB, units-of-prod, custom) | — | All major methods supported |
| `AssetRevaluation` | Revaluation | — | `account_asset_management_revaluation` | — | — |
| `AssetDisposal` | Disposal | — | `account_asset_management` (removal flow) | — | — |

**Business process — Asset lifecycle:**
1. Acquisition via AP invoice → auto-create asset via OCA link (`account_asset_create_from_invoice`)
2. Monthly depreciation via cron → posts journal entries
3. Revaluation event → `account_asset_management_revaluation`
4. Disposal → calculate gain/loss, post, remove from register
5. `ipai_*` delta: none — OCA covers IFRS + PFRS

### 1.6 Asset Leasing (IFRS 16)

| D365 entity | Odoo CE model | OCA ext | `ipai_*` | Alignment |
|---|---|---|---|---|
| `Lease` | — | `account_asset_leasing` (OCA lease-wg) | `ipai_lease_ph` (if PH PFRS 16 specifics needed) | OCA covers ROU + liability |
| `LeaseBook` | — | `account_asset_leasing` | — | — |
| `LeasePayment` / `LeaseSchedule` | — | `account_asset_leasing` payment schedule | — | — |
| `LeaseModification` | — | `account_asset_leasing_modification` | — | — |

**Business process — IFRS 16 lease:**
1. Lease created → OCA generates ROU asset + lease liability on commencement
2. Monthly: interest expense on liability + depreciation on ROU
3. Modification: reassessment of liability + adjustment to ROU
4. Termination: derecognition with gain/loss

### 1.7 Budgeting

| D365 entity | Odoo CE model | OCA ext | `ipai_*` | Alignment |
|---|---|---|---|---|
| `BudgetPlan` | `crossovered.budget` (CE has basic) | `account_budget_oca` (preferred full feature) | — | OCA is superior; use it |
| `BudgetPlanScenario` | — | `account_budget_oca` scenarios | — | — |
| `BudgetControl` | — | `account_budget_activity`, `budget_control` | — | Commitment + reservation |
| `BudgetTransaction` | — | `budget_manager` | — | — |
| `PositionBudget` | — | `hr_employee_firstname` + `hr_budget` | — | HR position cost planning |

**Business process — Budget cycle:**
1. Create budget plan per period + analytic plan
2. Allocate amounts per account + analytic
3. Post commitments on PO / expense approval (reservation pattern)
4. Actual vs budget report via OCA `account_financial_report`
5. Variance analysis + reforecast

### 1.8 Cost Accounting

| D365 entity | Odoo CE model | OCA ext | `ipai_*` | Alignment |
|---|---|---|---|---|
| `CostElement` | `account.analytic.account` | — | — | Analytic account IS the cost element |
| `CostCenter` / `CostObject` | `account.analytic.account` (grouping) | `account_analytic_distribution_rule` | — | — |
| `CostAllocationRule` | — | `account_analytic_distribution_rule` | — | Rule-based distribution |
| `OverheadCalculation` | — | `account_analytic_*_overhead` | — | — |
| `CostingSheet` | `product.cost.structure` | OCA `product_cost_structure` | — | Product cost hierarchy |

### 1.9 Tax (PH-critical section)

| D365 entity | Odoo CE model | OCA ext | `ipai_*` | Alignment |
|---|---|---|---|---|
| `TaxGroup` | `account.tax.group` | — | — | — |
| `TaxTable` | `account.tax` | — | — | — |
| `TaxTrans` | `account.move.line.tax_line_id` / `tax_ids` | — | — | — |
| `TaxAuthority` / `TaxJurisdiction` | `res.partner` (tagged as tax authority) | — | — | — |
| `SalesTaxReport` | — | `l10n_ph` reports | `ipai_bir_tax_compliance` | `l10n_ph` covers basic; `ipai_*` adds BIR forms + DAT gen |
| BIR Form 2307 (Certificate of Creditable Tax Withheld) | — | — | `ipai_expense_liquidation` (already in repo), `ipai_bir_tax_compliance` | PH-specific; no CE/OCA equivalent |
| BIR Form 2550M (Monthly VAT Declaration) | — | — | `ipai_bir_tax_compliance` | Custom |
| BIR Form SAWT (Summary Alphalist Withholding Tax) | — | — | `ipai_bir_tax_compliance` | DAT file output via Code Interpreter |
| BIR Form QAP (Quarterly Alphabetical List of Payees) | — | — | `ipai_bir_tax_compliance` | Custom |
| BIR Form SLSP (Summary List of Sales & Purchases) | — | — | `ipai_bir_tax_compliance` | DAT file output |
| BIR Form 1601-C (Compensation Withholding) | — | — | `ipai_bir_tax_compliance` | Custom |
| BIR Form 1601-E (Expanded Withholding) | — | — | `ipai_bir_tax_compliance` | Custom |
| eFPS/eBIRForms submission | — | — | `ipai_bir_tax_compliance` + Foundry Browser Automation | Replaces D365's ElectronicInvoicing engine |

**Business process — Monthly BIR close:**
1. Period close triggers `ipai_bir_tax_compliance.generate_2550m()` → reads `account.move.line` where tax is VAT
2. Code Interpreter (Foundry tool) generates 2550M PDF + validated DAT
3. Cross-check against `sale.order` / `purchase.order` for VAT basis
4. Browser Automation submits to eBIRForms portal
5. Submission receipt stored in `ipai_bir_filing_runs` audit table (Odoo, not Supabase)
6. 2307 auto-generated per vendor payment when CWT applies

### 1.10 Financial Reporting

| D365 entity | Odoo CE model | OCA ext | `ipai_*` | Alignment |
|---|---|---|---|---|
| `FinancialReport` (TB, BS, IS) | `account.financial.html.report` | `account_financial_report` (OCA) | — | OCA provides full suite |
| `PowerBIEmbeddedReport` | — | — | Power BI integration (not a module, connection config) | Power BI semantic model connects to Odoo PG via service account |
| `PaymentPrediction` (ML) | — | — | `ipai_finance_insights_payment` (build) | Azure ML model trained on AR aging patterns |
| `CustomerPaymentPrediction` | — | — | same as above | — |
| `BudgetProposalPrediction` | — | — | `ipai_finance_insights_budget` (build) | — |

---

## 2. D365 Project Operations → Odoo mapping

### 2.1 Project Operations Core (Dataverse entities)

| D365 entity | Odoo CE model | OCA ext | `ipai_*` | Business logic alignment |
|---|---|---|---|---|
| `Lead` | `crm.lead` | — | — | — |
| `Opportunity` | `crm.lead` (stage=opportunity) | — | — | Odoo uses single `crm.lead` with stages |
| `Quote` | `sale.order` (state=sent/draft) | — | — | — |
| `SalesOrder` | `sale.order` (state=sale) | — | — | — |
| `Invoice` (project-linked) | `account.move` linked to `project.project` | `sale_project` (CE), `account_analytic_sale` (OCA) | — | — |
| `PriceList` / `PriceListItem` | `product.pricelist` / `product.pricelist.item` | — | — | CE has full pricelist with variants + rules |
| `msdyn_project` | `project.project` | — | — | — |
| `msdyn_projecttask` | `project.task` | `project_wbs`, `project_timeline` | — | CE has hierarchical tasks; OCA adds WBS and Gantt |
| `msdyn_projectteammember` | `project.project.allowed_user_ids` / `hr.employee` | — | — | — |
| `msdyn_projectstage` | `project.task.type` (kanban stage) | — | — | — |
| `msdyn_milestone` | `project.milestone` | — | — | CE 18 has native `project.milestone` |
| `msdyn_bookableresource` | `hr.employee` + `resource.resource` | `resource_booking` | — | OCA adds booking calendar |
| `msdyn_resourcerequirement` | — | `project_resource_requirement` | — | OCA |
| `msdyn_resourceassignment` | `project.task.user_ids` + `account.analytic.line` | — | — | — |
| `msdyn_resourcebookingrequest` | — | `resource_booking` | — | OCA |
| `msdyn_timeentry` | `account.analytic.line` (type=timesheet) | `sale_timesheet`, `project_timesheet_*` | — | CE has full timesheet via `hr_timesheet` |
| `msdyn_expense` | `hr.expense` | `hr_expense_*` | `ipai_expense_liquidation` | CE + PH overlay |
| `msdyn_expensecategory` | `hr.expense.category` (product) | — | — | — |
| `msdyn_projectapproval` | — | `base_tier_validation`, `project_approval` | — | OCA |
| `msdyn_actual` | `account.analytic.line` (posted) | — | — | — |
| `msdyn_actualpendingjournaltransaction` | — | `account_analytic_pending` | — | Odoo typically posts immediately; OCA adds pending state |
| `msdyn_estimatelineitem` | `project.task.planned_hours` | `project_timeline` | — | CE has basic estimates; OCA adds line-item |

### 2.2 Project Operations Integrated with ERP (F&O `Proj*` entities)

| D365 entity | Odoo CE model | OCA ext | `ipai_*` | Alignment |
|---|---|---|---|---|
| `ProjTable` | `project.project` | — | — | — |
| `ProjPlan` / `ProjWBS` | `project.task` hierarchy | `project_wbs`, `project_hierarchy` | — | OCA adds formal WBS codes |
| `ProjActivity` | `project.task` | `project_activity_task` (OCA) | — | — |
| `ProjTransBudget` | — | `project_budget`, `account_budget_oca` | — | — |
| `ProjTransPosting` | `account.analytic.line` | — | — | — |
| `ProjJournalTable` / `ProjJournalTrans` | `account.move` + analytic | — | — | — |
| `ProjEmplTrans` (time) | `account.analytic.line` (type=timesheet) | `hr_timesheet_sheet` (if needed) | — | — |
| `ProjCostTrans` | `account.analytic.line` (cost) | — | — | — |
| `ProjRevenueTrans` | `account.analytic.line` + `account.move.line` | `project_pm_revenue_recognition` | — | OCA adds formal rev rec |
| `ProjInvoiceJour` / `ProjInvoiceLine` | `account.move` linked to project | `project_sale_invoice` | — | — |
| `ProjInvoiceProposal` | `sale.order` → `account.move.line` preview | `project_invoicing`, `sale_project_invoice_policy` | — | OCA adds invoice proposal workflow |
| `ProjFundingSource` / `ProjContract` | `project.project.partner_id` + `project.contract` (OCA) | `project_contract`, `project_funding` | — | — |
| `ProjSubContract` | `purchase.order` linked to project | `project_purchase_link` | — | — |
| `ProjWorkerAllocation` | `resource.resource` + `project.task.user_ids` | `resource_allocation` | — | — |
| `ProjPercentComplete` / `ProjRevenueRecognition` | — | `project_pm_revenue_recognition` | `ipai_project_rev_rec_ph` (PFRS 15 nuances) | OCA + optional PH overlay |
| `ProjForecast*` | — | `project_forecast_*`, `project_forecast_line` | — | OCA comprehensive forecast |
| `ProjExpenseTrans` | `hr.expense` linked to project | — | — | — |

**Business process — Project lifecycle (services/agency):**
1. Opportunity won → `sale.order` created with project template
2. Project auto-created with WBS via OCA `project_wbs_template`
3. Resources allocated via `resource.resource` + `project.task.user_ids`
4. Time entered via `account.analytic.line` (timesheet)
5. Expenses captured via `hr.expense` + `ipai_expense_liquidation`
6. Percentage-of-completion computed via OCA `project_pm_revenue_recognition`
7. Invoice proposal generated based on contract terms
8. Customer invoice posted + AR aging begins
9. Project close: variance analysis, final cost+revenue

---

## 3. Microsoft Copilot Finance agents → Pulser agents

### 3.1 Financial Reconciliation agent

| D365 Copilot surface | Pulser equivalent | Tool stack | Storage |
|---|---|---|---|
| Excel-hosted reconciliation | `pulser-finance` agent | PG MCP (read `account.bank.statement`, `account.move.line`) + Code Interpreter (match logic) + AI Search (rule grounding) | `stipaidevagent` (output Excel) |
| Auto-matching rules | `account.reconciliation.model` + agent-suggested new rules | Agent reads historical matches, proposes rule updates | — |
| Unmatched queue | `account.bank.statement.line` where `is_reconciled=False` | PG MCP query + agent prioritization | — |
| Operator corrections | Human-in-loop on agent suggestions | Via Odoo UI; agent logs corrections to `ops.reconciliation_feedback` (Postgres `ops` schema) | — |

**Business process — Reconciliation with Pulser:**
1. Bank statement imported → `account.bank.statement.line` records in draft
2. `pulser-finance` agent invoked via schedule or on-demand
3. Agent queries open statement lines via PG MCP
4. For each line: searches `account.move.line` for candidate matches, runs fuzzy match, scores confidence
5. Auto-matches high-confidence pairs → creates `account.partial.reconcile`
6. Low-confidence pairs → flagged for human review in Odoo UI
7. Operator decision logged as preference data for future DPO fine-tuning

### 3.2 Collections in Outlook agent

| D365 Copilot surface | Pulser equivalent | Tool stack | Storage |
|---|---|---|---|
| Outlook email draft | `pulser-finance` skill `ar_collections` | Azure AI Search (customer history), PG MCP (`account.move` overdue, `res.partner`), Foundry MCP (model eval), `stipaidevagent` (email template) | — |
| AR aging bucket read | PG MCP query on `account.move` where `invoice_date_due < today` | — | — |
| Customer contact lookup | PG MCP query on `res.partner` + `res.partner.title` | — | — |
| Follow-up task creation | `mail.activity` on `res.partner` | Odoo activity model, not Outlook | — |
| Email logging | `mail.mail` + `mail.message` linked to partner + invoice | Odoo mail infrastructure | — |

**Business process — Collections with Pulser:**
1. Daily cron triggers `ar_collections` skill
2. Agent queries overdue invoices via PG MCP, grouped by customer
3. For each customer: reads prior follow-up history + payment patterns
4. Drafts tiered email (1st reminder / 2nd / final demand) based on aging bucket
5. Pushes draft to Odoo as `mail.activity` for AR clerk approval
6. On approval: `mail.mail.send()` via Odoo's `ir.mail_server` (Zoho SMTP)
7. Agent logs activity, schedules next-step follow-up

---

## 4. Gaps where `ipai_*` thin layer is required

After CE + OCA, these are the only modules `ipai_*` needs to build:

| Module | Scope | Why OCA/CE insufficient |
|---|---|---|
| `ipai_bir_tax_compliance` | All BIR forms (2307, 2550M, SAWT, QAP, SLSP, 1601-C, 1601-E, 1702) + DAT + PDF + eBIRForms submission | No OCA module covers PH BIR; tax authority-specific |
| `ipai_expense_liquidation` (already in repo) | PH expense liquidation + OR/CWT handling | CE `hr.expense` + OCA doesn't handle PH OR requirements or 2307 overlay |
| `ipai_bank_sync_ph` | BPI/BDO/Metrobank/Unionbank bank statement connectors | OCA has CAMT/OFX; PH banks use proprietary file formats |
| `ipai_subscription_ph_tax` | Subscription billing with 2307/CWT overlay | OCA `contract` is generic; PH tax overlay needed |
| `ipai_einvoice_ph` | BIR-compliant e-OR generation (when BIR mandate lands) | OCA e-invoice generic; BIR e-OR spec is PH-specific |
| `ipai_finance_insights_payment` | Customer payment prediction ML | No OCA equivalent; `ipai_*` bridges to Azure ML / Foundry |
| `ipai_finance_insights_budget` | Budget variance prediction ML | Same |
| `ipai_project_rev_rec_ph` (optional) | PFRS 15 specifics beyond OCA `project_pm_revenue_recognition` | Only if customer needs strict PFRS 15; otherwise OCA alone |
| `ipai_apiscan` (OCR bridge) | Wire Azure Document Intelligence to AP invoice capture | OCA `account_invoice_import_ocr` uses Tesseract; Azure DI is more accurate for PH receipts |
| `ipai_lease_ph` (optional) | PFRS 16 specifics beyond OCA `account_asset_leasing` | Only if needed; OCA first |

**No other `ipai_*` modules should exist for the D365 parity use case.**

---

## 5. D365 features IPAI explicitly does NOT chase

| D365 feature | Why skip |
|---|---|
| Regulatory Configuration Service (RCS) | Enterprise-only; localization maintained in open OCA modules for IPAI markets |
| Public sector fund accounting | Not IPAI's market (TBWA\SMP, W9, PrismaLab — all private sector) |
| IoT-integrated asset management | Out of scope |
| Retail commerce (D365 Commerce) | Different product category |
| Mobile workspace SDK | Odoo web responsive + iOS wrapper per `docs/skills/ios-native-wrapper.md` cover this |
| Electronic Invoicing generic engine | OCA covers EU/LATAM; PH-specific is small `ipai_einvoice_ph` |

---

## 6. Pulser agent ↔ Odoo model binding summary

| Pulser agent | Primary Odoo models | Write posture | Tools |
|---|---|---|---|
| `pulser-finance` | `account.move`, `account.move.line`, `account.payment`, `account.bank.statement*`, `res.partner`, `account.analytic.line`, `hr.expense` | Read-first; writes via Odoo JSON-RPC with operator approval | PG MCP, Code Interpreter, Browser Automation, Azure AI Search, Document Intelligence, File Search |
| `pulser-ops` | `ir.cron`, `ir.module.module`, `ir.logging` (read); Azure resources (write via Azure MCP) | Read Odoo; mutate Azure only | Azure MCP, ADO MCP, Foundry MCP, GitHub MCP |
| `pulser-research` | `ir.attachment`, `mail.message`, `project.project.description` | Read-only | AI Search, Bing Search, File Search, GitHub MCP |

---

## 7. Migration / onboarding flow (D365 → IPAI)

For a customer migrating off D365 Finance + Project Operations to IPAI:

1. **Chart of accounts** → export D365 `MainAccount` + `FinancialDimension` → import to `account.account` + `account.analytic.plan`
2. **Master data** → vendors + customers from D365 → `res.partner` (tagged supplier_rank / customer_rank)
3. **Open items** → AR/AP open invoices → `account.move` with opening balance journal
4. **Asset register** → D365 `AssetTable` + `AssetBook` → OCA `account.asset` with historical depreciation pre-loaded
5. **Project masters** → D365 `msdyn_project` / `ProjTable` → `project.project` with WBS via `project_wbs`
6. **Time & expense history** → archive in Odoo as historical analytic lines or keep in D365 read-only during transition
7. **BIR history** → new system starts clean; historical DAT files retained in `stipaidevagent`
8. **Cutover** → parallel run 30 days, reconciliation of GL/AR/AP, then switch

---

## 8. Related

- `docs/research/d365-data-model-inventory.md` — entity catalog (this file's source)
- `CLAUDE.md` §"Odoo extension and customization doctrine" — CE → OCA → `ipai_*` rule
- Memory: `feedback_odoo_module_selection_doctrine`, `feedback_no_custom_default`
- Runbook: `docs/runbooks/foundry-connections-and-tools.md`

---

*Compiled 2026-04-15. Living document — update as Odoo 18 CE / OCA / `ipai_*` modules ship.*
