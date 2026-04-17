# Common Data Model (CDM) ↔ Odoo — Canonical Mapping

> IPAI's CDM adoption posture + full entity mapping for Fabric / Power BI / M365 Copilot interop.
> SSOT for the mapping: `platform/contracts/cdm-entity-map.yaml`.
> Implementation pipeline: `data-intelligence/pipelines/odoo_cdm_export.py`.
> Parent: `docs/architecture/data-model-erd.md` §11.
> Locked 2026-04-15.

---

## 0. Adoption posture — what IPAI takes from CDM (and what it leaves)

CDM is Microsoft's shared data language across D365, Power Platform, Power BI, Fabric.
Critical architectural fact: **CDM data can live in ADLS Gen2 as CDM folders (manifest JSON + CSV/Parquet data), entirely outside Dataverse.** That's the path IPAI takes.

| Aspect | IPAI decision | Why |
|---|---|---|
| CDM entity schema (names, attributes, relationships) | **ADOPT as projection target only** | Unlocks native Fabric / Power BI / M365 Copilot interop |
| CDM folder format on ADLS Gen2 | **ADOPT** — Databricks Gold layer exports CDM folders | Makes `stipaidevlake/gold/*` natively readable by Fabric + Synapse + Power BI |
| CDM entity naming in `platform/contracts/*.yaml` | **ADOPT** | Canonical cross-system reference |
| Dataverse as backing store | **REJECT** | Would fork SOR; Odoo stays canonical |
| CDM shape applied to `pg-ipai-odoo.public` | **REJECT** | Would rename Odoo models; breaks OCA compatibility |
| CDM semantic model views in Fabric Silver/Gold | **ADOPT** | Projection layer, not materialized in OLTP |

### Result — three-layer architecture

```
pg-ipai-odoo.public          (Odoo SOR — canonical names)
         ↓ Databricks DLT (reads via MCP or Fabric mirror)
stipaidevlake/bronze         (Odoo-shaped raw landing — CSV/Parquet, Odoo naming)
         ↓ DLT Silver transformation
stipaidevlake/silver         (cleaned, typed, Odoo naming preserved)
         ↓ DLT Gold + CDM manifest generation
stipaidevlake/gold/          (CDM folder format — CDM names, CDM manifests)
  Account/model.json           ← res.partner (is_company=true)
  Contact/model.json           ← res.partner (is_company=false)
  Invoice/model.json           ← account.move out_invoice
  ...
         ↓ Fabric fcipaidev mirror consumes CDM folders
Fabric OneLake               (CDM-aware; natively typed)
         ↓ Power BI / Fabric Data Agent
Power BI semantic models, M365 Copilot Analyst, Fabric Data Agent MCP
```

---

## 1. CDM adoption wins — what it unlocks

| Consumer | Without CDM export | With CDM export |
|---|---|---|
| Power BI | Manual schema mapping per field, per report | Drop-in CDM entities; zero mapping |
| Fabric `fcipaidev` | Custom shortcut schemas | Native CDM ingestion |
| Fabric Data Agent | Cannot expose Odoo data as queryable agent | Wraps CDM Gold entities → MCP endpoint |
| M365 Copilot Analyst | No access to Odoo financials | Queries via Fabric Data Agent MCP |
| Future Azure Synapse | Schema negotiation required | CDM-native read |
| D365 migration (inbound) | Heavy ETL from customer's CDM → Odoo | Reverse CDM mapping for master-data import |

---

## 2. Full Odoo → CDM entity mapping

### 2.1 Core business entities

| CDM entity | Odoo model | Key attribute alignment | Discriminator |
|---|---|---|---|
| `Account` | `res.partner` | `name`, `vat` (→ TIN), address fields, `ref` | `is_company=True` |
| `Contact` | `res.partner` | `name`, `parent_id` → Account, `email`, `phone` | `is_company=False` |
| `Lead` | `crm.lead` | `name`, `partner_name`, `contact_name`, `email_from` | `type='lead'` |
| `Opportunity` | `crm.lead` | same + `expected_revenue`, `probability` | `type='opportunity'` |
| `Product` | `product.template` | `name`, `list_price`, `categ_id`, `default_code` | — |
| `ProductCategory` | `product.category` | `name`, `parent_id` | — |
| `BusinessUnit` | `res.company` | `name`, `currency_id`, `country_id` | — |
| `Employee` / `Worker` | `hr.employee` | `name`, `job_id`, `department_id`, `work_email` | — |
| `Case` | `helpdesk.ticket` (CE) | `name`, `partner_id`, `stage_id`, `description` | — |
| `Campaign` | `utm.campaign` | `name`, `stage_id` | — |
| `PriceList` | `product.pricelist` | `name`, `currency_id` | — |
| `Currency` | `res.currency` | `name`, `rate`, `symbol` | — |
| `TaxCode` | `account.tax` | `name`, `amount`, `type_tax_use` | — |
| `BankAccount` | `res.partner.bank` + `account.journal` | `acc_number`, `bank_id` | — |

### 2.2 Sales + Procurement

| CDM entity | Odoo model | Discriminator |
|---|---|---|
| `Quote` | `sale.order` | `state in ['draft','sent']` |
| `SalesOrder` | `sale.order` | `state in ['sale','done']` |
| `SalesOrderDetail` / `SalesOrderLine` | `sale.order.line` | — |
| `PurchaseOrder` | `purchase.order` | `state in ['purchase','done']` |
| `PurchaseOrderDetail` | `purchase.order.line` | — |

### 2.3 Finance / GL

| CDM entity | Odoo model | Discriminator |
|---|---|---|
| `Invoice` / `CustomerInvoice` | `account.move` | `move_type='out_invoice'` |
| `CustomerRefund` | `account.move` | `move_type='out_refund'` |
| `Bill` / `VendorInvoice` | `account.move` | `move_type='in_invoice'` |
| `VendorRefund` | `account.move` | `move_type='in_refund'` |
| `InvoiceLine` | `account.move.line` | parent move_type |
| `Journal` / `LedgerJournal` | `account.journal` | — |
| `GeneralLedgerAccount` | `account.account` | — |
| `GeneralLedger` / `GeneralJournalAccountEntry` | `account.move.line` | `move_id.state='posted'` |
| `Payment` | `account.payment` | — |
| `BankStatement` | `account.bank.statement` | — |
| `BankStatementLine` | `account.bank.statement.line` | — |
| `Budget` | `account.budget` / OCA `account_budget_oca` | — |
| `BudgetLine` | `account.budget.line` | — |
| `FinancialDimension` | `account.analytic.plan` | — |
| `DimensionValue` | `account.analytic.account` | — |
| `FiscalYear` | `account.fiscal.year` | — |
| `Project` | `project.project` | — |
| `ProjectTask` | `project.task` | — |
| `TimeEntry` | `account.analytic.line` | `project_id IS NOT NULL` |
| `ExpenseReport` | `hr.expense.sheet` | — |
| `ExpenseTransaction` | `hr.expense` | — |

### 2.4 Industry accelerators — relevance to IPAI

| CDM accelerator | IPAI relevance |
|---|---|
| Financial Services (Banking Account, Loan, KYC) | Use when TBWA\SMP clients in FSI vertical — not core |
| Healthcare | Out of scope |
| Automotive | Out of scope |
| Nonprofit | Use when `w9studio` or `prismalab` customer is nonprofit — low priority |

---

## 3. IPAI CDM extensions (PH-specific — no CDM standard equivalent)

These are custom CDM entities IPAI defines in the `IPAI_*` namespace. Never force-map to generic CDM entities because it loses PH BIR specificity.

| IPAI CDM entity | Odoo source | Why custom |
|---|---|---|
| `IPAI_BIRFiling` | `ipai_bir_filing_run` | BIR filing state machine; no CDM tax-filing entity covers PH form lifecycle |
| `IPAI_BIRFormLine` | `ipai_bir_2307_line` | 2307 line detail with ATC + withholding |
| `IPAI_ATCCode` | `account.tax` extension (custom field `atc_code`) | PH Alphanumeric Tax Code taxonomy |
| `IPAI_TINNumber` | `res.partner.vat` + branch suffix field | PH TIN with branch suffix pattern (NNN-NNN-NNN-NNN) |
| `IPAI_ExpenseLiquidation` | `ipai_expense_liquidation` | PH OR / CWT extension of `ExpenseReport` |
| `IPAI_EWTRate` | `account.tax` with PH tax_use | Expanded withholding tax rate catalogue |
| `IPAI_AuditEvent` | `platform.audit_event` | Cross-schema audit trail |

### Extension pattern

Each `IPAI_*` entity's manifest references a parent CDM entity where one exists:

```json
{
  "manifest": {
    "entityName": "IPAI_ExpenseLiquidation",
    "extends": "ExpenseReport",   // CDM parent where possible
    "attributes": [
      {"name": "ph_or_number", "dataType": "string"},
      {"name": "cwt_amount", "dataType": "decimal"},
      {"name": "atc_code", "dataType": "string"},
      {"name": "bir_receipt_number", "dataType": "string"}
    ]
  }
}
```

---

## 4. CDM folder format specification for IPAI

Per Microsoft CDM spec, each entity folder on ADLS Gen2 contains:
- `model.json` OR `manifest.cdm.json` — CDM metadata
- One or more data files (CSV or Parquet)
- Optional `resolved.cdm.json` for resolved schema

### IPAI layout — `stipaidevlake/gold/`

```
stipaidevlake/gold/
├── manifest.cdm.json          ← top-level manifest listing all IPAI entities
├── Account/
│   ├── Account.cdm.json        ← entity definition
│   └── partitions/
│       └── Account-<date>.parquet
├── Contact/
│   ├── Contact.cdm.json
│   └── partitions/...
├── Invoice/
├── VendorInvoice/
├── Payment/
├── BankStatementLine/
├── Project/
├── ExpenseReport/
├── ...                          ← all CDM-standard entities from §2
│
├── IPAI_BIRFiling/             ← IPAI extensions (§3)
│   ├── IPAI_BIRFiling.cdm.json
│   └── partitions/...
├── IPAI_BIRFormLine/
├── IPAI_ExpenseLiquidation/
└── ...
```

**Refresh cadence:** Databricks DLT pipeline on `dbw-ipai-dev` runs hourly for transactional entities (Invoice, Payment, BankStatementLine), daily for master data (Account, Product).

**Partitioning:** date-based partitioning on `created_at` or `invoice_date`. Parquet (Snappy) is the format — smaller than CSV, CDM-spec compliant.

---

## 5. Fabric Data Agent integration (the strategic unlock)

Once CDM Gold is populated:

```
stipaidevlake/gold/Invoice/ (CDM)
    ↓ Fabric mirror shortcut (no data movement)
fcipaidev workspace OneLake
    ↓ Fabric Data Agent wraps the OneLake tables as queryable agent
    ↓ Exposes MCP endpoint: https://fcipaidev.fabric.microsoft.com/mcp
    ↓ Register in Pulser tools + (optionally) M365 Copilot agent catalog
M365 Copilot Analyst queries Odoo finance data via natural language
    without leaving Copilot Chat
```

This is what makes IPAI's Odoo data first-class in the M365 ecosystem — a TBWA user on M365 Copilot can ask "What's our DSO last quarter?" and get a Fabric Data Agent-grounded answer sourced from Odoo through CDM.

**Blocker:** `fcipaidev` Fabric workspace is not ARM-registered today (per validation). Fabric capacity provisioning is the gating dependency (Fabric trial expires ~2026-05-20 per memory).

---

## 6. Implementation plan

### Phase 1 — Export pipeline (`data-intelligence/pipelines/odoo_cdm_export.py`)

Databricks notebook / DLT pipeline:

1. Read Bronze (Odoo-shaped) from `stipaidevlake/bronze/`
2. Transform to Silver (typed, cleaned, Odoo naming preserved)
3. Transform to Gold with CDM entity split (one Odoo model may fan out to multiple CDM entities via discriminator per §2)
4. Emit `{Entity}.cdm.json` manifest per Gold folder
5. Emit top-level `manifest.cdm.json` listing all entities

### Phase 2 — Fabric ingestion

1. Provision Fabric capacity (blocked on `fcipaidev` — Issue 26 below)
2. Create shortcut from Fabric workspace → `stipaidevlake/gold/`
3. Verify CDM entities auto-surface in Fabric with correct types

### Phase 3 — Fabric Data Agent

1. Create Fabric Data Agent wrapping the CDM entities
2. Expose MCP endpoint
3. Register MCP endpoint in Pulser tool catalog per `docs/runbooks/foundry-connections-and-tools.md` §3

### Phase 4 — Power BI semantic model

1. Semantic model on Fabric OneLake CDM tables
2. DAX measures for 9 KPIs per `docs/research/d365-to-odoo-mapping.md` §5
3. Publish Finance PPM workspace

---

## 7. SSOT contract

`platform/contracts/cdm-entity-map.yaml` is the machine-readable version of §§2–3. Every change to the mapping MUST update the YAML via PR before code is modified.

---

## 8. Related

- `docs/architecture/data-model-erd.md` §11 — CDM positioning summary
- `docs/architecture/d365-displacement-map.md` — D365 entity catalog side
- `docs/research/d365-to-odoo-mapping.md` — Odoo ↔ D365 (not CDM) mapping
- `docs/backlog/open-issues-20260415.md` — Issue 26 (CDM export pipeline)
- Memory: `project_fabric_finance_ppm` (Fabric trial expiry ~2026-05-20)

---

*Locked 2026-04-15. CDM adoption is ADLS-folder path only — Dataverse remains rejected.*
