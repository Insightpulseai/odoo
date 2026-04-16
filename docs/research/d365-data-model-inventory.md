# D365 Finance + Project Operations + Finance Agents — Data Model Inventory

> Complete entity catalog for competitive/parity analysis against IPAI (Odoo CE 18 + OCA + `ipai_*`).
> Sources: Microsoft Learn documentation for D365 Finance, D365 Project Operations (Core + Integrated with ERP), and Microsoft Copilot Finance agents.
> Compiled 2026-04-15.

**Purpose:** map what TBWA\SMP Finance (or any D365 customer) actually gets for
$210 (Finance) + $135 (Project Operations) per user/month, and where IPAI's
Odoo+OCA+`ipai_*` layer needs to reach for true parity.

---

## 1. D365 Finance — core data model

### 1.1 General Ledger (GL)

| Entity | Purpose | Odoo equivalent |
|---|---|---|
| `MainAccount` | Chart of accounts | `account.account` |
| `LedgerChartOfAccounts` | CoA container | — (implicit) |
| `Ledger` | Ledger per legal entity | `res.company` |
| `LedgerJournalTable` | Journal header | `account.move` |
| `LedgerJournalTrans` | Journal line | `account.move.line` |
| `GeneralJournalEntry` | Posted GJE header | `account.move` (posted state) |
| `GeneralJournalAccountEntry` | GJE account line | `account.move.line` |
| `FinancialDimension` | Dim catalog (cost center, project, department) | `account.analytic.account`, tag system |
| `DimensionAttributeValueCombination` | Dim combination | `account.analytic.distribution` |
| `FiscalCalendar` / `FiscalYear` / `FiscalPeriod` | Calendar structure | `account.fiscal.year`, period is implicit |
| `Currency` / `CurrencyExchangeRate` / `ExchangeRateType` | FX | `res.currency`, `res.currency.rate` |
| `LegalEntity` / `CompanyInfo` | Tenant company | `res.company` |

### 1.2 Accounts Payable (AP)

| Entity | Purpose | Odoo equivalent |
|---|---|---|
| `VendGroup` / `VendTable` | Vendor master | `res.partner` with `supplier_rank > 0` |
| `VendorInvoice` / `VendInvoiceJour` / `VendInvoiceTrans` | AP invoice header/line | `account.move` (type=in_invoice) |
| `VendInvoiceInfoTable` | Pending (pre-posting) invoice | `account.move` (state=draft) |
| `PurchTable` / `PurchLine` | PO header/line | `purchase.order` / `purchase.order.line` |
| `VendorPaymentJournal` / `VendPayment` | Payment run | `account.payment` |
| `MatchingReason` / `InvoiceMatching` / `VendMatching` | 2/3-way matching | OCA `account_invoice_three_way_match` |
| `VendorSettlement` | Invoice↔payment settlement | `account.partial.reconcile` |
| `VendInvoiceCapture` | Invoice capture (OCR) | `ipai_*` with Document Intelligence or OCA `account_invoice_import*` |
| `BankRemittance` / `PaymentProposal` | Payment proposal | `account.payment.register` |

### 1.3 Accounts Receivable (AR)

| Entity | Purpose | Odoo equivalent |
|---|---|---|
| `CustGroup` / `CustTable` | Customer master | `res.partner` with `customer_rank > 0` |
| `SalesTable` / `SalesLine` | Sales order header/line | `sale.order` / `sale.order.line` |
| `CustInvoiceJour` / `CustInvoiceTrans` | Customer invoice | `account.move` (type=out_invoice) |
| `CustPaymentJournal` / `CustPayment` | Customer payment | `account.payment` |
| `CustCollectionLetter` / `CollectionLetterAgingPeriod` | Dunning letter | OCA `account_followup_*`, `account_credit_control` |
| `CustInterestJournal` / `Interest` | Interest on overdue | OCA `account_invoice_interest` |
| `CreditLimit` / `CustCreditLimit` | Credit limit | `res.partner.credit_limit`, OCA `account_credit_limit_advanced` |
| `SubscriptionBilling` / `BillingSchedule` / `RecurringBillingLine` | Subscription billing | OCA `subscription_*` / `contract` |
| `CreditTransactionLimit` | Credit mgmt rules | OCA `account_credit_control_*` |

### 1.4 Cash & Bank Management

| Entity | Purpose | Odoo equivalent |
|---|---|---|
| `BankAccountTable` | Bank account master | `res.partner.bank` + `account.journal` (type=bank) |
| `BankStatementTable` / `BankStatementDocument` | Bank statement | `account.bank.statement` |
| `BankStatementLine` | Statement line | `account.bank.statement.line` |
| `BankReconciliation` / `AdvancedBankReconciliation` | Reconciliation | `account.reconciliation`, OCA `account_reconciliation_widget` |
| `MatchBankDocumentLine` | Matched pair | `account.partial.reconcile` |
| `CashFlowForecast` / `CashFlowForecastCalc` | Cash flow forecast | OCA `account_cash_flow_forecast` |
| `BankParameters` / `BankNegativePaymAmount` | Bank controls | `account.journal` config |

### 1.5 Fixed Assets

| Entity | Purpose | Odoo equivalent |
|---|---|---|
| `AssetTable` | Asset master | `account.asset` |
| `AssetBook` | Depreciation book per asset | `account.asset` (multiple valuation books via `account_asset_multibook` OCA) |
| `AssetGroup` | Asset group | `account.asset.group` |
| `AssetTrans` | Asset transactions | `account.move.line` linked to asset |
| `AssetDepreciationJournal` | Depreciation run | `account.asset.depreciation.line` |
| `AssetDepreciationProfile` / `AssetDepreciationMethod` | Dep method | `account.asset.profile` |
| `AssetAcquisition` / `AssetDisposal` | Acquisition / disposal events | `account.asset` state transitions |
| `AssetRevaluation` | Revaluation | OCA `account_asset_management_revaluation` |

### 1.6 Asset Leasing

| Entity | Purpose | Odoo equivalent |
|---|---|---|
| `Lease` | Lease master | OCA `account_asset_leasing` or `ipai_lease_*` |
| `LeaseBook` | Lease valuation book | part of OCA |
| `LeasePayment` / `LeaseSchedule` | Payment schedule | OCA |
| `LeaseTransaction` | Lease posting | `account.move.line` |
| `LeaseModification` | Amendment | OCA |
| `RightOfUseAsset` / `LeaseLiability` | ROU asset + liability (IFRS 16) | OCA `account_asset_leasing_*` |

### 1.7 Budgeting

| Entity | Purpose | Odoo equivalent |
|---|---|---|
| `BudgetPlan` / `BudgetPlanScenario` | Budget plan + scenarios | `account.budget.post` / `crossovered.budget` |
| `BudgetControl` / `BudgetControlConfiguration` | Budget control policy | OCA `account_budget_activity` |
| `BudgetSource` / `BudgetSourceTracking` | Budget funding source | OCA |
| `BudgetTransaction` | Budget commitment/reservation | OCA `budget_manager` |
| `PositionBudget` / `PositionForecasting` | HR position budget | OCA `hr_budget` |

### 1.8 Cost Accounting

| Entity | Purpose | Odoo equivalent |
|---|---|---|
| `CostElement` / `CostElementDimension` | Cost element taxonomy | `account.analytic.account` + tags |
| `CostCenter` / `CostObject` | Cost center + object | `account.analytic.account` |
| `CostAllocationRule` / `OverheadCalculation` | Allocation rules | OCA `account_analytic_distribution_rule` |
| `CostEntry` / `CostTrans` | Cost posting | `account.analytic.line` |
| `CostingSheet` / `CostingVersion` | Costing sheet | `product.cost.structure` (OCA) |

### 1.9 Tax

| Entity | Purpose | Odoo equivalent |
|---|---|---|
| `TaxGroup` / `TaxItemGroup` | Tax group + item | `account.tax.group` |
| `TaxTable` | Tax master | `account.tax` |
| `TaxTrans` | Tax transaction | `account.move.line.tax_line_id` |
| `TaxAuthority` / `TaxJurisdiction` | Authority + jurisdiction | `res.partner` (tax authority) |
| `SalesTaxReport` / `ElectronicTaxReport` / `VATReport` | Tax reporting | `account.tax.report`, Odoo localization modules |
| `TaxRegistration` / `TaxCertificate` | Tax reg & cert | Odoo l10n_* modules |
| `ElectronicInvoiceConfiguration` / `EDocument` | E-invoicing | OCA `account_e_invoice_*`, `ipai_*` for PH BIR |

### 1.10 Financial Reporting & Insights

| Entity | Purpose | Odoo equivalent |
|---|---|---|
| `FinancialReport` / `FinancialReportRowDefinition` | Financial report definition | `account.financial.html.report` (OCA) |
| `TrialBalance` / `TrialBalanceAccountBalance` | TB | OCA `account_financial_report` |
| `PowerBIEmbeddedReport` | Embedded PBI | IPAI Power BI integration |
| `PaymentPrediction` / `PaymentDelayPrediction` | ML customer payment prediction | IPAI `ipai_finance_insights_*` (needs build) |
| `CustomerPaymentPrediction` | AR risk score | same |
| `BudgetProposalPrediction` | Budget variance ML | same |

### 1.11 Public Sector (optional module)

| Entity | Purpose | Odoo equivalent |
|---|---|---|
| `FundClass` / `FundType` / `Fund` | Fund accounting | OCA `account_fund_accounting` |
| `DerivedFinancialHierarchy` | Fund hierarchy | OCA |
| `BudgetRegisterEntry` | Public sector budget | OCA |
| `AppropriationAccount` | Appropriation tracking | OCA |

---

## 2. D365 Project Operations — core data model

### 2.1 Project Operations Core (Dataverse / CDS entities, `msdyn_*` prefix)

| Entity | Purpose | Odoo equivalent |
|---|---|---|
| `Lead` / `Opportunity` | CRM lead + oppty | `crm.lead` |
| `Quote` / `QuoteDetail` | Quote header + line | `sale.order` (state=draft/quote) |
| `SalesOrder` / `SalesOrderDetail` | Order header + line | `sale.order` |
| `Invoice` / `InvoiceDetail` | Project invoice | `account.move` + link to `project.project` |
| `PriceList` / `PriceListItem` | Price list | `product.pricelist` / `product.pricelist.item` |
| `msdyn_project` | Project | `project.project` |
| `msdyn_projecttask` | Task / WBS node | `project.task` + OCA `project_wbs` |
| `msdyn_projectteammember` | Team member | `project.project.allowed_user_ids` |
| `msdyn_projectstage` / `msdyn_milestone` | Stage + milestone | `project.stage` |
| `msdyn_bookableresource` | Bookable resource | `hr.employee` + `resource.resource` |
| `msdyn_resourcerequirement` | Resource requirement | OCA `project_resource_requirement` |
| `msdyn_resourceassignment` | Resource assignment | `project.task.user_ids` + workload |
| `msdyn_resourcebookingrequest` | Booking request | — (not core in Odoo) |
| `msdyn_timeentry` | Time entry | `account.analytic.line` (timesheet) |
| `msdyn_expense` / `msdyn_expensecategory` | Expense record | `hr.expense` / `hr.expense.category` |
| `msdyn_projectapproval` | Approval record | OCA `project_approval` + `ipai_*` for PH |
| `msdyn_actualpendingjournaltransaction` | Pending actuals | — (Odoo posts immediately) |
| `msdyn_actual` | Posted actual | `account.analytic.line` |
| `msdyn_estimatelineitem` | Estimate line | OCA `project_timeline` |

### 2.2 Project Operations Integrated with ERP (F&O entities, `Proj*` prefix)

| Entity | Purpose | Odoo equivalent |
|---|---|---|
| `ProjTable` | Project master | `project.project` |
| `ProjPlan` / `ProjWBS` / `ProjActivity` | Plan + WBS + activity | `project.task` hierarchy |
| `ProjTransBudget` | Project budget transaction | OCA `project_budget` |
| `ProjTransPosting` | Project posting | `account.analytic.line` |
| `ProjJournalTable` / `ProjJournalTrans` | Project journal | `account.move` + analytic |
| `ProjEmplTrans` | Time transaction | `account.analytic.line` (type=timesheet) |
| `ProjCostTrans` | Cost transaction | `account.analytic.line` |
| `ProjRevenueTrans` | Revenue transaction | `account.analytic.line` + `account.move.line` |
| `ProjInvoiceJour` / `ProjInvoiceTable` / `ProjInvoiceLine` | Project invoice | `account.move` linked to project |
| `ProjInvoiceProposal` / `ProjInvoiceProposalLine` | Invoice proposal | OCA `project_invoicing` |
| `ProjFundingSource` / `ProjContract` | Funding + contract | OCA `project_contract` |
| `ProjSubContract` | Subcontract | OCA `project_subcontract` |
| `ProjWorkerAllocation` | Worker allocation | `hr.employee` + `resource.resource` |
| `ProjRevenueRecognition` / `ProjPercentComplete` | POC / rev rec | OCA `project_pm_revenue_recognition` |
| `ProjExpenseTrans` | Expense txn | `hr.expense` |
| `ProjForecast*` (multiple) | Forecast records (cost, hours, revenue) | OCA `project_forecast` |

---

## 3. Microsoft Copilot Finance agents — data access model

### 3.1 Financial Reconciliation agent

| Entity / Data surface | Purpose | Source |
|---|---|---|
| `FinancialReconciliation_RunInstance` | Run instance per reconciliation job | D365 F&O |
| `ReconciliationLineItem` / `ReconciliationMatch` | Line + match record | D365 F&O (bank recon, GL recon) |
| `ReconciliationRule` | Rule for auto-matching | D365 config |
| `ReconciliationException` | Unmatched item | D365 F&O |
| Excel range bindings | Excel-hosted data (operator works in Excel) | M365 Graph API |
| Prompt/response telemetry | Conversation history | Copilot runtime |

Data handling per Microsoft: agent reads from F&O ledger + GL + subledgers + bank statements; writes go through F&O data-entity endpoints with the operator's credentials; results surface inline in Excel or Outlook.

### 3.2 Collections in Outlook agent

| Entity / Data surface | Purpose |
|---|---|
| `CollectionsSuggestion` | Agent-generated follow-up suggestion |
| `CollectionEmailDraft` | Drafted customer email |
| `CustInvoiceAgingBucket` | Aging bucket reads from AR |
| `CustContact` | Customer contact lookup |
| `ContactConversationHistory` | Prior correspondence |
| `FollowUpTask` | Outlook task created by agent |

Agent surface: Outlook email + Teams chat (shown earlier in your screenshots). Reads: AR aging, customer contacts, prior emails. Writes: drafts emails, creates follow-up tasks, logs activities back to CRM/F&O.

### 3.3 Data handling summary (from MS Learn "Data handling in Finance agents")

- Agents read via the Common Data Service (Dataverse) + F&O data-entity endpoints.
- Operator auth flows via Entra ID; least-privilege role assignments apply.
- Agent prompts and responses are logged for audit.
- Data never leaves the customer's Microsoft tenancy boundary (per Microsoft's data-residency commitment).
- Fine-tuning on customer data is not performed (per current Copilot doctrine).

---

## 4. IPAI parity gap — what needs a thin `ipai_*` layer

Running this catalog against what Odoo CE 18 + OCA already provides:

### Areas where Odoo+OCA already covers ≥80% of D365 functionality
- GL, AP, AR (core)
- Bank reconciliation (via OCA `account_reconciliation_widget`)
- Fixed Assets (OCA `account_asset_management*`)
- Project management, WBS, time entry, expense (core + OCA `project_*`)
- Cost accounting via analytic accounting
- CRM (lead → opportunity → quote → order)

### Areas where OCA is partial and `ipai_*` delta needed
- **PH-specific BIR compliance** (2307, 2550M, SAWT, QAP, SLSP, 1601-C, 1601-E) — `ipai_bir_tax_compliance`
- **Philippine expense liquidation + OR/CWT** — `ipai_expense_liquidation` (already in repo per prior memory)
- **Finance insights ML predictions** (customer payment, budget variance) — `ipai_finance_insights_*` (build)
- **Subscription billing with PH tax complexity** — OCA `subscription` + `ipai_*` for 2307/CWT overlays
- **E-invoicing for BIR-compliant electronic OR** — `ipai_einvoice_ph`
- **Rev rec for services/project billing (ASC 606 / PFRS 15)** — OCA `project_pm_revenue_recognition` + `ipai_*` for PH GAAP

### Areas where D365 leads but IPAI should NOT chase
- **Asset Leasing full IFRS 16 ROU/liability posting workflows** — unless a customer needs it, skip
- **Public sector fund accounting** — not IPAI's market
- **Electronic Invoicing (generic engine)** — OCA covers EU/LATAM; IPAI only needs PH overlay
- **Regulatory configuration service (RCS)** — D365 enterprise-only; not worth cloning

### The pitch structure

For a TBWA\SMP Finance-sized customer (11 users), D365 Finance ($210) + Project Operations ($135) = **$45,540/year** for feature coverage that Odoo CE + ~15 OCA modules + 3-4 `ipai_*` modules delivers at **zero license cost**, with **PH-native BIR compliance** that D365 doesn't ship.

---

## 5. Pulser agent binding implications

Given the data model, here is which Pulser agent should own which D365-equivalent capability:

| D365 capability | Pulser agent | Primary data source (IPAI) |
|---|---|---|
| Financial Reconciliation agent | `pulser-finance` | `account.bank.statement`, `account.move.line` via PG MCP |
| Collections in Outlook | `pulser-finance` | `account.move` (overdue AR), `res.partner` via PG MCP |
| BIR filing (no D365 equivalent) | `pulser-finance` | `ipai_bir_tax_compliance` + PG MCP + Code Interpreter + Browser Automation |
| Project cost roll-up | `pulser-finance` | `account.analytic.line`, `project.project` via PG MCP |
| Resource booking suggestions | `pulser-ops` or a future `pulser-projects` | `hr.employee`, `resource.resource` |
| Payment prediction | `pulser-finance` | AR aging + ML (build via Azure ML or in-Foundry) |

---

*Compiled 2026-04-15. Living document — append as Microsoft releases new modules or as IPAI maps additional entities.*
