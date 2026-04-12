---
name: pulser-d365-migration
description: High-fidelity migration agent for Dynamics 365 Finance & Project Operations. Implements the "Dimension Reduction Protocol" and ADLS Gen2 native landing paths for displacing D365 with Odoo 18 CE.
allowed-tools: Read Write Edit Bash Grep Glob
---

# Pulser — D365 F&O → Odoo Migration

## Core Displacement Principle
Customers off-ramp from D365 F&O to Odoo 18 CE; we displace the complexity of two systems (ProjOps + Finance) with one integrated Odoo instance.

## Module mapping (Odoo 18 CE Parity)

| D365 F&O module | Entities | Odoo 18 CE equivalent | Complexity |
|---|---|---|---|
| General Ledger | \`LedgerJournalTrans\`, \`MainAccount\` | \`account.move\`, \`account.account\` | Medium |
| General Ledger | `LedgerJournalTrans`, `MainAccount` | `account.move`, `account.account` | Medium |
| Accounts Payable | `VendTable`, `VendInvoiceJour` | `res.partner`, `account.move` (bill) | Low |
| Accounts Receivable | `CustTable`, `CustInvoiceJour` | `res.partner`, `account.move` (invoice) | Low |
| Fixed Assets | `AssetTable`, `AssetDepBook` | OCA `account_asset_management` | Medium |
| Budgeting | `BudgetTransactionLine` | `crossovered.budget`, `account.budget.line` | Medium |
| Cost Accounting | `CAMCostAccountingLedger` | Analytic accounts + `account.analytic.line` | High |
| Subscription Billing | `SubBillingContractTable` | OCA `contract` module | High |
| **Project Operations** | `ProjTable`, `ProjEmplTrans` | `project.project`, `account.analytic.line` | High |

## Business Central Displacement (SMB Target)
Microsoft explicitly separates Enterprise (F&O) from SMB (Business Central). IPAI targets the Business Central buyer persona.

### BC Entity Mapping
BC uses a simplified OData v2.0 API.
- **Customer** → `res.partner`
- **Vendor** → `res.partner` (supplier)
- **General_Ledger_Entry** → `account.move.line`
- **Job** → `project.project`
- **Item** → `product.template`

### BC Extraction URL
`https://api.businesscentral.dynamics.com/v2.0/{tenantId}/{envName}/api/v2.0/`

## Financial Dimensions Reduction Protocol
F&O stamped dimensions (Dept, CostCenter, Project) have no direct 1:1 equivalent in Odoo's 2-plan analytic standard.
1. **Catalog**: List all DimensionAttributeValueSets used in the last 2 fiscal years.
2. **Map**: Assign primary dimensions to Odoo **Analytic Plans**.
3. **Flatten**: Assign secondary dimensions to Odoo **Analytic Tags**.
4. **Prune**: Drop legacy/informational dimensions into Odoo **Custom Fields** (non-ledger impacting).

## Extraction Pattern: ADLS Gen2 Native Landing
Preferred for high-volume displacement. No OData v4 extraction needed if the customer uses F&O native ADLS export.
1. **Bronze**: IPAI Principal granted \`Storage Blob Data Reader\` on customer lake.
2. **Landing**: \`stipaidevlake/bronze/f&o/{company}/{entity}/{date}/\`.
3. **Pipeline**: DLT reads Parquet → Odoo model JSON → Batch load.

## Project Operations Displacement Pitch
- **Lite Mode**: Full replacement with Odoo Project + CRM + Timesheet.
- **Integrated Mode**: Strategic displacement. Consolidate F&O GL and ProjOps into one Odoo instance to eliminate dual-licensing and sync latency.
