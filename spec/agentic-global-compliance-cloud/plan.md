# Implementation Plan: Agentic Global Compliance Cloud (AGCC)

> **Status**: Draft
> **Date**: 2026-04-07
> **Platform**: Odoo 18 CE + OCA + ipai_* on Azure (ACA, PostgreSQL 16, AI Foundry, Databricks)
> **PRD**: `spec/agentic-global-compliance-cloud/prd.md`
> **Research**: `docs/knowledge-base/research/ai-compliance-agent-design.md`
> **Principle**: Deterministic rules first, AI assistance second, human authority always.

---

## Module Naming Reconciliation

The constitution (§6.3) mandates `ipai_agcc_*` as the target naming convention. This plan uses transitional names (`ipai_compliance_*`, `ipai_bir_*`) reflecting the existing codebase. Migration path:

| Current (Plan/Tasks) | Target (Constitution) | Phase |
|-----------------------|----------------------|-------|
| `ipai_compliance_graph` | `ipai_agcc_core` | Phase 0 rename |
| `ipai_bir_tax_compliance` | absorbed into `ipai_agcc_jurisdiction_ph` | Phase 1 |
| `ipai_bir_2307`, `ipai_bir_slsp`, `ipai_bir_returns` | sub-modules of `ipai_agcc_jurisdiction_ph` | Phase 1 |
| `ipai_compliance_evidence` | part of `ipai_agcc_core` | Phase 1 |
| `ipai_avalara_connector` | `ipai_agcc_tax_engine_avalara` | Phase 2 |
| `ipai_compliance_agent` | remains (not AGCC-specific) | Phase 3 |

Implementation uses current names; rename PR ships at end of each phase.

---

## Architecture Overview

```
+------------------------------------------------------------------------+
|                        ODOO 18 CE (Azure Container Apps)               |
|                                                                        |
|  +--------------------+  +-------------------+  +-------------------+  |
|  | COMPLIANCE GRAPH   |  | TAX ENGINE        |  | EVIDENCE ENGINE   |  |
|  | ipai_compliance_   |  | ipai_bir_tax_     |  | ipai_compliance_  |  |
|  | graph              |  | compliance        |  | evidence          |  |
|  +--------+-----------+  +---------+---------+  +---------+---------+  |
|           |                        |                      |            |
|  +--------v-----------+  +--------v----------+  +--------v----------+  |
|  | BIR FORMS          |  | FILING CALENDAR   |  | WORKFLOW/APPROVAL |  |
|  | ipai_bir_2307      |  | ipai_compliance_  |  | base_tier_        |  |
|  | ipai_bir_returns   |  | calendar          |  | validation (OCA)  |  |
|  | ipai_bir_slsp      |  |                   |  |                   |  |
|  +--------+-----------+  +---------+---------+  +---------+---------+  |
|           |                        |                      |            |
+------------------------------------------------------------------------+
            |                        |                      |
   +--------v-----------+  +--------v----------+  +--------v----------+
   | AZURE BLOB STORAGE  |  | AZURE AI FOUNDRY  |  | AVALARA AVATAX   |
   | (Evidence Archive)  |  | (Advisory Agent)  |  | (Phase 2+)       |
   | 10yr immutable      |  | Anomaly explain   |  | US/EU tax calc   |
   +---------------------+  +-------------------+  +-------------------+
            |                        |
   +--------v-----------+  +--------v----------+
   | DATABRICKS          |  | POWER BI          |
   | DLT pipeline        |  | Compliance        |
   | Anomaly detection   |  | control tower     |
   +---------------------+  +-------------------+
```

---

## Phase 1: MVP -- PH BIR Compliance (Months 1-3)

### Objective

Full BIR tax compliance automation for domestic Philippine transactions: VAT, EWT, BIR form generation, SLSP, filing calendar, evidence packs. All deterministic -- no AI in the critical path.

### 1.1 Module: `ipai_compliance_graph`

**Purpose**: Jurisdiction-aware policy graph that links entities, registrations, obligations, and deadlines. Foundation model for all compliance modules.

**Path**: `addons/ipai/ipai_compliance_graph/`

**Models**:

| Model | Fields | Purpose |
|-------|--------|---------|
| `compliance.jurisdiction` | `name`, `code` (ISO 3166), `country_id` (Many2one `res.country`), `authority_name`, `authority_code`, `active`, `notes` | Tax authority registry (e.g., BIR, IRS, HMRC) |
| `compliance.obligation` | `name`, `jurisdiction_id` (Many2one), `obligation_type` (selection: vat/ewt/cit/filing/einvoice/registration), `frequency` (monthly/quarterly/annual), `form_code` (e.g., "2550M"), `due_day` (int), `due_month_offset` (int), `penalty_reference`, `active` | Filing/reporting obligation definition |
| `compliance.registration` | `company_id` (Many2one `res.company`), `jurisdiction_id` (Many2one), `registration_type` (selection: vat/ewt/cas/business_permit), `registration_number`, `effective_date`, `expiry_date`, `status` (selection: active/expired/pending), `document_ids` (One2many `ir.attachment`) | Entity registration tracking |
| `compliance.policy.rule` | `name`, `jurisdiction_id` (Many2one), `obligation_id` (Many2one), `rule_type` (selection: rate/threshold/validation/classification), `python_code` (Text), `effective_from` (Date), `effective_to` (Date), `version`, `notes` | Versioned policy rules with effective dates |

**Dependencies**:
- Odoo core: `base`, `account`
- OCA: none
- External: none

**Verification criteria**:
- `compliance.jurisdiction` record for PH/BIR loads on install
- `compliance.obligation` records for 2550M, 2550Q, 1601-EQ, 1702Q load on install
- All obligation due dates match BIR filing schedule
- `compliance.policy.rule` effective date filtering works correctly (rules outside effective window are excluded)

**Data files**:
- `data/jurisdiction_ph.xml` -- BIR jurisdiction + obligations
- `data/policy_rules_ph_2025.xml` -- PH-specific rules seeded from `ph_rates_2025.json`

---

### 1.2 Module: `ipai_bir_2307` (enhanced)

**Purpose**: Auto-generate BIR Form 2307 (Certificate of Creditable Tax Withheld at Source) from vendor bills with WHT tax lines. PDF output matching BIR prescribed layout.

**Path**: `addons/ipai/ipai_bir_2307/`

**Models**:

| Model | Fields | Purpose |
|-------|--------|---------|
| `bir.form.2307` | `name` (Char, sequence), `partner_id` (Many2one `res.partner`), `company_id`, `move_id` (Many2one `account.move`), `period_start` (Date), `period_end` (Date), `state` (selection: draft/confirmed/cancelled), `pdf_file` (Binary), `pdf_filename` (Char) | BIR 2307 certificate record |
| `bir.form.2307.line` | `form_id` (Many2one `bir.form.2307`), `atc_code` (Char), `atc_description` (Char), `tax_base` (Monetary), `tax_rate` (Float), `tax_withheld` (Monetary), `tax_id` (Many2one `account.tax`) | Per-ATC-code line detail |

**Inherits/extends**:
- `account.move`: add `bir_2307_ids` (One2many), `bir_2307_count` (Integer, computed), `bir_2307_missing` (Boolean, computed -- True when WHT lines exist but no 2307)
- `account.tax`: add `atc_code` (Char), `is_withholding` (Boolean)
- `res.partner`: TIN validation constraint `_check_ph_tin` (regex `^\d{3}-\d{3}-\d{3}-\d{3}$`)

**Automation**:
- `account.move.action_post()` override: on vendor bill (`move_type == 'in_invoice'`) with WHT tax lines (`tax_id.is_withholding == True`), auto-create `bir.form.2307` in draft state
- Cron `ir.cron` (daily): detect posted vendor bills with WHT lines but no 2307 record; create `mail.activity` for accountant

**Report**:
- QWeb PDF report `report_bir_2307` matching BIR prescribed layout
- Fields mapped per BIR Form 2307 specification: Part I (withholding agent TIN, name, address), Part II (payee TIN, name, address), Part III (ATC, income payment, tax withheld)

**Dependencies**:
- Odoo core: `account`, `l10n_ph`
- Custom: `ipai_bir_tax_compliance` (for `ph_rates_2025.json` ATC code registry)
- OCA: none

**Verification criteria**:
- Vendor bill PHP 100,000 services + EWT 2% -> auto-creates 2307 with tax_base=100,000, tax_withheld=2,000, atc_code=W158
- PDF output renders all three BIR parts with correct field placement
- Credit note on the same bill -> original 2307 cancelled, replacement 2307 created with net amounts
- Bulk 2307 generation for a given period (all qualifying bills)
- Cron flags bills missing 2307 within 24 hours

**Key risks**:
- BIR 2307 PDF layout must match prescribed format exactly. Validate against BIR sample forms.
- ATC code mapping must be exhaustive for all WHT tax types in use.

---

### 1.3 Module: `ipai_bir_returns`

**Purpose**: Compute BIR 2550M (Monthly VAT Return), BIR 2550Q (Quarterly VAT Return), and BIR 1601-EQ (Quarterly EWT Remittance). Generate data for filing, not the filing itself.

**Path**: `addons/ipai/ipai_bir_returns/`

**Models**:

| Model | Fields | Purpose |
|-------|--------|---------|
| `bir.return` | `name` (Char, sequence), `form_type` (selection: 2550M/2550Q/1601EQ), `company_id`, `period_start` (Date), `period_end` (Date), `state` (selection: draft/computed/reviewed/filed), `reviewer_id` (Many2one `res.users`), `reviewed_date` (Datetime), `notes` (Text) | Return header |
| `bir.return.line` | `return_id` (Many2one `bir.return`), `box_number` (Char), `box_label` (Char), `amount` (Monetary), `source_domain` (Text -- stored Odoo domain filter for traceability) | Computed box/line values |

**Computation logic** (all deterministic, no AI):
- **2550M/Q**:
  - Box 1-14: Output VAT = `sum(account.move.line.balance)` where `tax_group_id.name == 'VAT'` and `move_type in ('out_invoice', 'out_refund')` for the period
  - Box 15-20: Input VAT = same for `move_type in ('in_invoice', 'in_refund')`
  - Box 21: VAT Payable = Output - Input - prior excess credits (from previous return record)
  - Attach SLSP files (from `ipai_bir_slsp`)
- **1601-EQ**:
  - Per ATC code: sum of `tax_withheld` from `bir.form.2307.line` for the quarter
  - Total remittance = sum of all ATC lines

**Inherits/extends**:
- `bir.return` inherits `mail.thread`, `mail.activity.mixin` for audit trail

**Dependencies**:
- Odoo core: `account`
- Custom: `ipai_bir_2307` (for 1601-EQ computation), `ipai_bir_slsp` (for SLSP attachment)
- OCA: `base_tier_validation` (approval gate: return must be reviewed before state -> `reviewed`)

**Verification criteria**:
- 2550M computation for a test month matches manual spreadsheet calculation within PHP 1.00
- 1601-EQ quarterly total matches sum of all 2307 certificates for the quarter
- State transition `draft -> computed -> reviewed -> filed` enforced; `reviewed` requires tier approval from a different user than the preparer
- `source_domain` on each line allows drill-down to source journal entries

**Key risks**:
- Prior excess credit carry-forward logic must handle partial months and amended returns.
- Box numbering must exactly match current BIR form version (2550M last updated per TRAIN Law amendments).

---

### 1.4 Module: `ipai_bir_slsp`

**Purpose**: Generate Summary List of Sales and Purchases as BIR-compliant pipe-delimited CSV.

**Path**: `addons/ipai/ipai_bir_slsp/`

**Models**:

| Model | Fields | Purpose |
|-------|--------|---------|
| `bir.slsp` | `name` (Char, sequence), `slsp_type` (selection: sales/purchases), `company_id`, `period_month` (Integer), `period_year` (Integer), `state` (selection: draft/generated/validated/attached), `csv_file` (Binary), `csv_filename` (Char), `line_count` (Integer, computed), `total_amount` (Monetary, computed) | SLSP report header |
| `bir.slsp.line` | `slsp_id` (Many2one), `partner_id` (Many2one `res.partner`), `partner_tin` (Char, related), `partner_name` (Char, related), `registered_address` (Char), `amount_gross` (Monetary), `amount_exempt` (Monetary), `amount_zero_rated` (Monetary), `amount_taxable` (Monetary), `amount_vat` (Monetary), `amount_ewt` (Monetary) | Per-partner summary |

**CSV format**: Pipe-delimited (`|`), BIR-prescribed column order:
```
TIN|REGISTERED_NAME|LAST_NAME|FIRST_NAME|MIDDLE_NAME|ADDRESS|
AMOUNT_OF_GROSS_SALES|AMOUNT_OF_EXEMPT_SALES|AMOUNT_OF_ZERO_RATED_SALES|
AMOUNT_OF_TAXABLE_SALES|AMOUNT_OF_OUTPUT_TAX|...
```

**Data source**: Aggregation of `account.move` + `account.move.line` for the period, grouped by `partner_id`, split by tax group (VATable, zero-rated, exempt).

**Validation**:
- `_validate_slsp_totals()`: sum of SLSP lines must equal GL balances for Output VAT / Input VAT accounts for the period. Discrepancy > PHP 1.00 blocks state transition to `validated`.

**Dependencies**:
- Odoo core: `account`
- Custom: `ipai_bir_tax_compliance`
- OCA: none

**Verification criteria**:
- CSV output opens in BIR eFPS upload without parse errors
- Sales SLSP total matches Output VAT GL account balance for the period
- Purchases SLSP total matches Input VAT GL account balance for the period
- Partners without TIN are flagged as exceptions (not silently omitted)
- Handles credit notes correctly (netted against original partner)

---

### 1.5 Module: `ipai_compliance_evidence`

**Purpose**: Generate and store evidence packs (PDF + CSV bundles) for any compliance action. Immutable once sealed.

**Path**: `addons/ipai/ipai_compliance_evidence/`

**Models**:

| Model | Fields | Purpose |
|-------|--------|---------|
| `compliance.evidence.pack` | `name` (Char, sequence), `pack_type` (selection: filing/2307/slsp/audit/exception), `company_id`, `period_start` (Date), `period_end` (Date), `state` (selection: draft/sealed), `sealed_date` (Datetime), `sealed_by` (Many2one `res.users`), `sha256_hash` (Char), `attachment_ids` (Many2many `ir.attachment`), `source_model` (Char), `source_id` (Integer), `notes` (Text) | Evidence pack container |
| `compliance.evidence.log` | `pack_id` (Many2one), `timestamp` (Datetime), `action` (Char), `user_id` (Many2one `res.users`), `detail` (Text) | Append-only audit trail within pack |

**Behavior**:
- On `state -> sealed`: compute SHA-256 hash of all attachments concatenated; write `sha256_hash`; mark all attachments as `res_model='compliance.evidence.pack'` with immutable flag
- `sealed` state is terminal -- no transition back to `draft`; no attachment add/remove after seal
- Azure Blob archival: server action on seal triggers upload to Azure Blob Storage container `compliance-evidence` with immutable retention policy (10 years per BIR requirement)

**Integration**:
- `bir.return` seal action -> auto-creates evidence pack containing: return PDF, SLSP CSVs, source GL trial balance for the period
- `bir.form.2307` confirm action -> auto-creates evidence pack containing: 2307 PDF, source vendor bill PDF

**Dependencies**:
- Odoo core: `base`, `account`
- Azure: Azure Blob Storage SDK (`azure-storage-blob` Python package)
- Custom: none (consumed by other modules)

**Verification criteria**:
- Evidence pack for a 2550M filing contains: return summary PDF, sales SLSP CSV, purchases SLSP CSV, GL trial balance PDF
- SHA-256 hash is deterministic (same inputs produce same hash)
- Sealed pack rejects attachment modification (raises `UserError`)
- Azure Blob upload succeeds with immutable retention metadata
- Evidence pack retrieval from Azure Blob returns byte-identical content

**Key risks**:
- Azure Blob SDK must be installed in the Odoo container image. Add to `requirements.txt`.
- Immutable retention policy must be configured at the Azure Storage container level, not just in Odoo code.

---

### 1.6 Module: `ipai_compliance_calendar`

**Purpose**: Filing deadline tracking with automated Odoo activity scheduling. Generates `mail.activity` reminders tied to `compliance.obligation` deadlines.

**Path**: `addons/ipai/ipai_compliance_calendar/`

**Models**:

| Model | Fields | Purpose |
|-------|--------|---------|
| `compliance.filing.deadline` | `obligation_id` (Many2one `compliance.obligation`), `company_id`, `period_start` (Date), `period_end` (Date), `due_date` (Date, computed from obligation rules), `state` (selection: upcoming/due/overdue/filed/waived), `responsible_id` (Many2one `res.users`), `activity_id` (Many2one `mail.activity`), `return_id` (Many2one `bir.return`, optional), `notes` (Text) | Concrete filing deadline instance |

**Automation**:
- Cron `ir.cron` (daily): for each active `compliance.obligation` + `compliance.registration`, compute next deadline if not already created. Create `compliance.filing.deadline` + `mail.activity` assigned to `responsible_id` with due date = filing due date minus 5 business days.
- Cron `ir.cron` (daily): update state to `overdue` for deadlines past `due_date` with state still `upcoming` or `due`. Escalation: create `mail.activity` for the responsible user's manager.

**Calendar view**: Odoo calendar view on `compliance.filing.deadline` showing all deadlines color-coded by state (green=filed, yellow=upcoming, orange=due, red=overdue).

**Dependencies**:
- Odoo core: `mail`
- Custom: `ipai_compliance_graph` (for obligation definitions)
- OCA: none

**Verification criteria**:
- Install with PH jurisdiction data -> deadlines auto-created for current and next 3 months
- 2550M deadline for March 2026 = April 20, 2026 (20th of following month)
- Activity created 5 business days before due date, assigned to configured responsible user
- Overdue state triggers escalation activity to manager
- Filing a `bir.return` for the period transitions corresponding deadline to `filed`

---

### 1.7 Enhancement: `ipai_bir_tax_compliance` (existing)

**Path**: `addons/ipai/ipai_bir_tax_compliance/` (existing module, enhance)

**Enhancements**:
- **Rate validation server action**: On module install/update, compare all `account.tax` records tagged with PH jurisdiction against `ph_rates_2025.json`. Log mismatches as `mail.activity` for compliance officer.
- **ATC code registry model**: `bir.atc.code` with fields `code`, `description`, `rate`, `tax_base_type`, `effective_from`, `effective_to`. Seeded from `ph_rates_2025.json`.
- **Compliance dashboard**: `ir.actions.act_window` with custom tree/kanban view showing: open 2307s pending confirmation, missing 2307 exceptions, upcoming deadlines, SLSP generation status, return preparation status.
- **TIN bulk validation**: Transient model `bir.tin.validator.wizard` that scans all `res.partner` records with PH transactions and flags invalid/missing TINs.

**Dependencies**: No new external dependencies. Uses existing `ph_rates_2025.json`.

---

### Phase 1 Integration Points

| Integration | Source | Target | Mechanism |
|------------|--------|--------|-----------|
| Vendor bill WHT -> 2307 | `account.move` (in_invoice) | `bir.form.2307` | `action_post()` override |
| 2307 lines -> 1601-EQ | `bir.form.2307.line` | `bir.return` (1601EQ) | Domain query aggregation |
| GL entries -> SLSP | `account.move.line` | `bir.slsp` | SQL aggregation |
| GL entries -> 2550M/Q | `account.move.line` | `bir.return` (2550M/Q) | SQL aggregation |
| Return filing -> evidence | `bir.return` | `compliance.evidence.pack` | Server action on state change |
| Obligation -> deadline | `compliance.obligation` | `compliance.filing.deadline` | Daily cron |
| Deadline -> activity | `compliance.filing.deadline` | `mail.activity` | Auto-create on deadline creation |
| Approval gate | `bir.return` | `tier.review` | OCA `base_tier_validation` |
| Rate validation | `ph_rates_2025.json` | `account.tax` | Server action on install/update |

### Phase 1 OCA Dependencies

| OCA Module | Repository | 18.0 Status | Purpose |
|-----------|------------|-------------|---------|
| `base_tier_validation` | `server-ux` | Verify | Approval workflow for returns and high-value bills |
| `account_fiscal_position_autodetect` | `account-financial-tools` | Verify | Auto-apply PH fiscal positions |
| `base_user_role` | `server-backend` | Verify | SoD role enforcement for compliance users |

**Action required**: Verify each OCA module has an 18.0-compatible branch. If not, assess migration effort from 17.0 or 16.0.

### Phase 1 Azure Dependencies

| Service | Resource | Purpose | Configuration |
|---------|----------|---------|---------------|
| Azure Blob Storage | Container: `compliance-evidence` | Evidence pack archival | Immutable retention policy: 3650 days (10 years). Access tier: Hot for current year, Cool after 1 year. |
| Azure Key Vault | `kv-ipai-dev` | Store Blob Storage connection string | Secret: `compliance-blob-connection-string` |

### Phase 1 Acceptance Gates

1. **Tax computation accuracy**: 50 test vendor bills with varying WHT rates; all 2307 certificates match manual calculation.
2. **SLSP reconciliation**: Monthly SLSP totals equal GL VAT account balances within PHP 1.00 for 3 consecutive test months.
3. **2550M accuracy**: Computed return matches accountant's manual spreadsheet for a real month's data.
4. **Filing calendar**: All BIR deadlines for 2026 correctly generated with proper due dates.
5. **Evidence integrity**: Sealed evidence pack SHA-256 hash is reproducible; Azure Blob retrieval returns identical content.
6. **Approval workflow**: `base_tier_validation` enforces review on `bir.return` state transition; same user cannot prepare and approve.
7. **Exception detection**: Cron detects 100% of vendor bills with WHT lines but no 2307 within 24 hours.

### Phase 1 Key Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| BIR 2307 PDF layout rejected by vendors/BIR | Medium | High | Obtain BIR sample forms; pixel-compare output; test with actual vendor acceptance |
| SLSP CSV rejected by eFPS upload | Medium | High | Test against BIR eFPS test environment if available; validate column order against BIR specification |
| OCA `base_tier_validation` incompatible with 18.0 | Medium | Medium | Early verification; fallback: implement minimal approval mixin in `ipai_compliance_graph` |
| `ph_rates_2025.json` missing ATC codes for edge-case WHT types | Low | Medium | Cross-reference against complete BIR ATC code list (BIR website); add missing codes before MVP |
| Azure Blob SDK adds container image size | Low | Low | `azure-storage-blob` is ~1MB; negligible impact |

---

## Phase 2: Cross-Border + External Engine (Months 4-6)

### Objective

Support international transactions via external tax engine integration (Avalara AvaTax), e-invoicing adapter framework, and cross-border VAT/GST policy rules. PH compliance remains on the local deterministic engine.

### 2.1 Module: `ipai_tax_engine_adapter`

**Purpose**: Abstraction layer that routes tax determination requests to either the local PH engine or an external tax engine (Avalara) based on jurisdiction.

**Path**: `addons/ipai/ipai_tax_engine_adapter/`

**Models**:

| Model | Fields | Purpose |
|-------|--------|---------|
| `tax.engine.provider` | `name` (Char), `provider_type` (selection: local/avalara/custom), `api_endpoint` (Char), `api_key_vault_ref` (Char -- Key Vault secret name, not the key itself), `jurisdiction_ids` (Many2many `compliance.jurisdiction`), `active` (Boolean), `timeout_ms` (Integer, default 5000), `fallback_policy` (selection: block/use_local/manual) | Tax engine provider configuration |
| `tax.engine.request` | `provider_id` (Many2one), `move_id` (Many2one `account.move`), `request_payload` (Text, JSON), `response_payload` (Text, JSON), `status` (selection: pending/success/error/timeout), `response_time_ms` (Integer), `timestamp` (Datetime) | Request/response log for auditability |

**Routing logic**:
1. On `account.move` tax computation, determine jurisdiction from `partner_id.country_id` + `fiscal_position_id`
2. Look up `tax.engine.provider` where `jurisdiction_ids` contains the target jurisdiction
3. If `provider_type == 'local'`: use standard Odoo `account.tax._compute_amount()`
4. If `provider_type == 'avalara'`: call Avalara AvaTax REST API via `ipai_avalara_connector`
5. Log request/response in `tax.engine.request` for audit trail
6. On timeout/error: apply `fallback_policy`

**Dependencies**:
- Odoo core: `account`
- Custom: `ipai_compliance_graph` (for jurisdiction definitions)

**Verification criteria**:
- PH domestic transaction -> routes to local engine (no external API call)
- US transaction -> routes to Avalara
- Avalara timeout -> fallback policy applied (block or local)
- Every external tax call logged in `tax.engine.request` with full payload

---

### 2.2 Module: `ipai_avalara_connector`

**Purpose**: Avalara AvaTax REST API v2 integration for multi-jurisdiction tax determination.

**Path**: `addons/ipai/ipai_avalara_connector/`

**Integration surface**:
- Avalara AvaTax REST API v2: `POST /api/v2/transactions/create`
- Authentication: API key from Azure Key Vault (secret: `avalara-api-key`)
- Sandbox: `sandbox-rest.avatax.com` (dev/staging)
- Production: `rest.avatax.com`

**Models**:

| Model | Fields | Purpose |
|-------|--------|---------|
| `avalara.config` | `company_id` (Many2one `res.company`), `account_id` (Char), `license_key_vault_ref` (Char), `environment` (selection: sandbox/production), `company_code` (Char), `enabled` (Boolean) | Per-company Avalara configuration |
| `avalara.tax.code.mapping` | `product_categ_id` (Many2one `product.category`), `avalara_tax_code` (Char), `description` (Char) | Product category to Avalara tax code mapping |

**Behavior**:
- Maps `account.move.line` to Avalara `CreateTransactionModel` fields: `lines[].itemCode`, `lines[].amount`, `addresses.shipFrom`, `addresses.shipTo`
- Receives tax determination result; creates/updates `account.tax` lines on the move
- Caches determination results for identical transaction parameters (configurable TTL)

**Dependencies**:
- Odoo core: `account`, `sale`, `purchase`
- Custom: `ipai_tax_engine_adapter`
- External: Avalara AvaTax account (subscription)
- Azure: Key Vault for API credentials
- Python: `requests` (already in Odoo dependencies)

**Verification criteria**:
- Sandbox transaction for a US interstate sale returns correct state+county tax
- Tax code mapping applied from product category
- API credentials never appear in logs or `tax.engine.request.request_payload` (masked)
- Error response from Avalara surfaces as user-facing warning, not silent failure

---

### 2.3 Module: `ipai_compliance_einvoice`

**Purpose**: E-invoicing adapter framework. Phase 2 delivers the framework and a PH CAS adapter stub. Actual country adapters plug in later.

**Path**: `addons/ipai/ipai_compliance_einvoice/`

**Models**:

| Model | Fields | Purpose |
|-------|--------|---------|
| `einvoice.adapter` | `name` (Char), `country_id` (Many2one `res.country`), `adapter_class` (Char -- Python class path), `schema_version` (Char), `endpoint_url` (Char), `active` (Boolean) | Adapter registry |
| `einvoice.document` | `move_id` (Many2one `account.move`), `adapter_id` (Many2one `einvoice.adapter`), `state` (selection: draft/validated/submitted/accepted/rejected), `submission_ref` (Char), `xml_content` (Text), `validation_errors` (Text), `submitted_date` (Datetime) | E-invoice document lifecycle |

**Adapter interface** (Python abstract class):
```python
class EInvoiceAdapter:
    def validate(self, move) -> (bool, list[str])  # pre-submission validation
    def render(self, move) -> str                    # generate XML/JSON
    def submit(self, document) -> str                # submit to authority, return ref
    def check_status(self, document) -> str          # poll for acceptance
```

**Phase 2 delivers**:
- Framework + adapter registry
- PH CAS adapter stub (validation + render only; submit deferred until BIR EIS specification stabilizes)

**Dependencies**:
- Odoo core: `account`
- Custom: `ipai_compliance_graph`

---

### 2.4 Module: `ipai_compliance_crossborder`

**Purpose**: Cross-border VAT/GST rules: reverse charge, place of supply, zero-rating for exports, non-resident WHT.

**Path**: `addons/ipai/ipai_compliance_crossborder/`

**Models**:

| Model | Fields | Purpose |
|-------|--------|---------|
| `crossborder.rule` | `name` (Char), `source_jurisdiction_id` (Many2one `compliance.jurisdiction`), `target_jurisdiction_id` (Many2one), `transaction_type` (selection: goods/services/digital), `rule_type` (selection: reverse_charge/zero_rate/exempt/standard), `fiscal_position_id` (Many2one `account.fiscal.position`), `effective_from` (Date), `effective_to` (Date), `notes` (Text) | Cross-border tax treatment rules |

**Behavior**:
- On invoice creation with cross-border partner (different `country_id` than company), look up applicable `crossborder.rule`
- Auto-suggest or auto-apply fiscal position based on rule match
- For reverse charge: set tax amount to 0 on supplier invoice, add note referencing reverse charge article
- For non-resident WHT (PH outbound): apply final WHT rates from `ph_rates_2025.json` non-resident section

**Dependencies**:
- Odoo core: `account`
- Custom: `ipai_compliance_graph`, `ipai_bir_tax_compliance`
- OCA: `account_fiscal_position_autodetect`

**Verification criteria**:
- Export sale from PH company -> zero-rated VAT fiscal position auto-applied
- Service purchase from US vendor -> correct non-resident WHT applied (per treaty rate or default 25%)
- Intra-ASEAN goods sale -> correct fiscal position based on AFTA rules

---

### Phase 2 Additional Integration Points

| Integration | Source | Target | Mechanism |
|------------|--------|--------|-----------|
| Tax determination routing | `account.move` | `tax.engine.provider` | Jurisdiction-based routing |
| Avalara API call | `ipai_avalara_connector` | Avalara REST API | HTTPS, API key from Key Vault |
| Document Intelligence | Scanned vendor invoice | `account.move` | Azure AI Document Intelligence prebuilt-invoice model; extract TIN, amounts, tax |
| Cross-border rule | `res.partner.country_id` | `crossborder.rule` | Lookup on invoice creation |

### Phase 2 Azure Dependencies

| Service | Resource | Purpose |
|---------|----------|---------|
| Azure Key Vault | `kv-ipai-dev` | Avalara API key: `avalara-api-key`, `avalara-account-id` |
| Azure AI Document Intelligence | `di-ipai-compliance` | Vendor invoice OCR extraction (prebuilt-invoice model) |

### Phase 2 Acceptance Gates

1. **Tax engine routing**: 100 test transactions across PH, US, EU jurisdictions; each routed to correct engine with zero misroutes.
2. **Avalara accuracy**: 20 US interstate transactions match Avalara sandbox expected results.
3. **Cross-border WHT**: Non-resident vendor payments apply correct WHT rate per `ph_rates_2025.json` treaty section.
4. **E-invoice framework**: PH CAS adapter validates a standard invoice XML against BIR schema without errors.
5. **Document Intelligence**: OCR extraction of TIN + amount from 20 sample vendor invoices achieves >90% field accuracy.
6. **Audit trail**: Every external API call (Avalara, Document Intelligence) logged with request/response payload (credentials masked).

### Phase 2 Key Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Avalara per-transaction cost exceeds budget | Medium | High | Negotiate volume pricing; cache results for identical parameters; limit to jurisdictions with >5 tax rules |
| Avalara API latency degrades invoice posting UX | Medium | Medium | Async tax determination with background job (`queue_job`); or timeout with fallback |
| BIR CAS/EIS specification changes before adapter completion | High | Medium | Build adapter as framework; defer PH submit until spec stabilizes; validate-only mode |
| Document Intelligence accuracy below 90% for PH invoices | Medium | Medium | Fine-tune with PH invoice samples; manual review fallback for low-confidence extractions |

---

## Phase 3: Multi-Jurisdiction + AI Advisory (Months 7-12)

### Objective

Add AI advisory layer, predictive compliance analytics, regulatory change monitoring, and multi-entity consolidation. AI is advisory-only -- never in the deterministic tax computation path.

### 3.1 Module: `ipai_compliance_agent`

**Purpose**: AI compliance advisor exposed via MCP tools. Answers policy questions, explains anomalies, drafts remediation recommendations. Never executes tax determinations or filing submissions.

**Path**: `addons/ipai/ipai_compliance_agent/`

**Models**:

| Model | Fields | Purpose |
|-------|--------|---------|
| `compliance.agent.session` | `user_id` (Many2one `res.users`), `start_time` (Datetime), `end_time` (Datetime), `query_count` (Integer), `state` (selection: active/closed) | Agent session tracking |
| `compliance.agent.query` | `session_id` (Many2one), `query_text` (Text), `response_text` (Text), `response_sources` (Text -- JSON list of cited rules/documents), `confidence` (Float), `delegation_level` (selection: advisory/draft/execute_with_approval), `timestamp` (Datetime) | Query/response log |

**MCP Tools** (exposed via `ipai_compliance_agent` as MCP server):
- `compliance_policy_lookup(jurisdiction, obligation_type)` -> returns applicable rules from `compliance.policy.rule`
- `compliance_exception_explain(move_id)` -> explains why a transaction was flagged, citing specific rules
- `compliance_deadline_status(company_id, period)` -> returns filing deadline status
- `compliance_rate_check(atc_code, effective_date)` -> returns canonical rate from `ph_rates_2025.json`
- `compliance_evidence_summary(pack_id)` -> returns evidence pack contents and hash

**Delegation tiers** (from PRD 7.3):
- **Advisory only**: Agent answers questions, cites rules. No data mutation.
- **Draft generation**: Agent prepares a draft (e.g., draft 2307, draft return). Human reviews before posting.
- **Execute-with-approval**: Agent submits action; `base_tier_validation` gate requires human approval before effect.
- **Post-review**: Low-risk only (e.g., filing reminder creation). Agent executes; human reviews within SLA.

**Dependencies**:
- Odoo core: `mail`
- Custom: `ipai_compliance_graph`, `ipai_compliance_evidence`
- Azure: Azure AI Foundry (model deployment for advisory LLM)
- Python: MCP SDK

**Verification criteria**:
- Policy lookup returns correct rule for a given jurisdiction + obligation
- Exception explanation cites specific rule IDs and data fields, not hallucinated reasons
- Agent cannot execute `bir.return` state transition without tier approval
- Every query/response pair logged in `compliance.agent.query` with sources

**Key risks**:
- LLM hallucination of tax positions. Mitigation: agent retrieves rules from `compliance.policy.rule` and `ph_rates_2025.json`; never generates tax rates from training data. All responses carry "not legal advice" framing.

---

### 3.2 Module: `ipai_compliance_analytics`

**Purpose**: Databricks-powered compliance analytics. WHT leakage detection, VAT mismatch trends, threshold monitoring, predictive filing.

**Path**: `addons/ipai/ipai_compliance_analytics/`

**This module is primarily a Databricks DLT pipeline, not an Odoo module.** The Odoo-side component is a dashboard connector.

**Databricks components** (managed in `infra/databricks/`):
- DLT pipeline `compliance_analytics`:
  - Bronze: JDBC extract from `account_move_line`, `bir_form_2307`, `bir_return`, `compliance_filing_deadline`
  - Silver: Cleansed, joined views with jurisdiction enrichment
  - Gold:
    - `wht_leakage`: Vendor bills with qualifying amounts but no WHT applied
    - `vat_mismatch`: Input/Output VAT ratio anomalies by period
    - `threshold_monitor`: Entities approaching VAT registration threshold (PHP 3M)
    - `filing_readiness`: Predicted monthly VAT payable (ML model, >5% accuracy target)

**Odoo model**:

| Model | Fields | Purpose |
|-------|--------|---------|
| `compliance.analytics.alert` | `alert_type` (selection: wht_leakage/vat_mismatch/threshold/filing_prediction), `severity` (selection: info/warning/critical), `description` (Text), `source_ref` (Char -- Databricks job run ID), `move_ids` (Many2many `account.move`), `state` (selection: new/acknowledged/resolved), `assigned_to` (Many2one `res.users`) | Analytics-generated alerts pushed to Odoo |

**Integration**:
- Databricks job (weekly) writes alerts to Odoo via JSON-RPC (`/jsonrpc` endpoint)
- Odoo surfaces alerts in compliance dashboard with drill-down to source transactions

**Dependencies**:
- Databricks: Unity Catalog, DLT, JDBC connector to PostgreSQL
- Odoo core: `account`
- Power BI: Compliance control tower dashboard (reads from Databricks gold tables)

---

### 3.3 Module: `ipai_compliance_drift`

**Purpose**: Regulatory change monitoring. Surfaces new BIR issuances, rate changes, and deadline modifications for human review.

**Path**: `addons/ipai/ipai_compliance_drift/`

**Models**:

| Model | Fields | Purpose |
|-------|--------|---------|
| `compliance.regulation.update` | `jurisdiction_id` (Many2one `compliance.jurisdiction`), `title` (Char), `source_url` (Char), `source_type` (selection: bir_rr/bir_rmc/sec_mc/law/executive_order), `publication_date` (Date), `effective_date` (Date), `summary` (Text), `impact_assessment` (Text), `state` (selection: new/assessed/applied/not_applicable), `assessed_by` (Many2one `res.users`), `applied_date` (Date) | Regulatory change tracker |

**Monitoring sources**:
- BIR website RSS/scrape (cron, weekly) for new Revenue Regulations (RR) and Revenue Memorandum Circulars (RMC)
- Manual entry for regulations discovered outside automated monitoring

**Workflow**:
1. New issuance detected -> `compliance.regulation.update` created in `new` state
2. AI Foundry agent generates draft `impact_assessment` (advisory, human reviews)
3. Compliance officer reviews, sets state to `assessed`
4. If applicable: officer updates `ph_rates_2025.json` and/or `compliance.policy.rule`, sets state to `applied`

**Dependencies**:
- Odoo core: `mail`
- Custom: `ipai_compliance_graph`
- Azure: AI Foundry (for impact assessment generation)
- Python: `requests`, `beautifulsoup4` (for BIR website monitoring)

**Verification criteria**:
- Monitoring cron detects a simulated new BIR RR publication
- Impact assessment generated by AI cites specific affected rate codes and obligations
- Rate update workflow: regulation -> assessment -> `ph_rates_2025.json` update -> rate validation re-run

---

### Phase 3 Azure Dependencies

| Service | Resource | Purpose |
|---------|----------|---------|
| Azure AI Foundry | `ipai-copilot-resource` (East US 2) | Advisory agent LLM deployment; impact assessment generation |
| Databricks | Unity Catalog + DLT | Compliance analytics pipeline |
| Power BI | Embedded workspace | Compliance control tower dashboard |

### Phase 3 Acceptance Gates

1. **Agent advisory accuracy**: 50 compliance policy questions; agent returns correct rule citations for >90% of queries.
2. **Agent safety**: Agent cannot execute tax rate changes, filing submissions, or journal entry modifications without human approval gate.
3. **WHT leakage detection**: Databricks pipeline identifies >95% of intentionally planted leakage test cases.
4. **Predictive filing**: Monthly VAT payable prediction within 5% of actual for 3 consecutive months.
5. **Regulatory drift**: Simulated new BIR issuance detected and surfaced within 48 hours; impact assessment generated.
6. **Control tower**: Power BI dashboard shows filing readiness, exception aging, jurisdiction risk across all entities.

### Phase 3 Key Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| LLM hallucination of compliance advice | High (inherent) | Critical | Agent retrieves from codified rules only; "not legal advice" framing on all outputs; human review mandatory for any action |
| Databricks JDBC latency on large GL datasets | Medium | Medium | Incremental extraction (last N days); DLT handles deduplication |
| BIR website structure changes break scraper | High | Low | Monitoring is supplementary; manual entry fallback; scraper is resilient to minor DOM changes |
| Predictive model accuracy insufficient for user trust | Medium | Medium | Start with simple heuristics (3-month moving average); ML model is an enhancement, not a requirement |

---

## Module Dependency Graph

```
ipai_compliance_graph          (Phase 1, foundation)
  |
  +-- ipai_bir_tax_compliance  (Phase 1, enhance existing)
  |     |
  |     +-- ipai_bir_2307      (Phase 1)
  |     |     |
  |     |     +-- ipai_bir_returns  (Phase 1, depends on 2307 for 1601-EQ)
  |     |
  |     +-- ipai_bir_slsp      (Phase 1)
  |           |
  |           +-- ipai_bir_returns  (Phase 1, depends on SLSP for attachment)
  |
  +-- ipai_compliance_evidence (Phase 1, consumed by all)
  |
  +-- ipai_compliance_calendar (Phase 1)
  |
  +-- ipai_tax_engine_adapter  (Phase 2)
  |     |
  |     +-- ipai_avalara_connector      (Phase 2)
  |
  +-- ipai_compliance_einvoice (Phase 2)
  |
  +-- ipai_compliance_crossborder (Phase 2)
  |
  +-- ipai_compliance_agent    (Phase 3)
  |
  +-- ipai_compliance_analytics (Phase 3, primarily Databricks)
  |
  +-- ipai_compliance_drift    (Phase 3)
```

---

## Build Order (Recommended)

### Phase 1 (Months 1-3)

| Week | Deliverable | Module |
|------|------------|--------|
| 1-2 | Compliance graph foundation + PH jurisdiction data | `ipai_compliance_graph` |
| 2-3 | ATC code registry + rate validation + TIN validation | `ipai_bir_tax_compliance` (enhance) |
| 3-5 | BIR 2307 auto-generation + PDF report | `ipai_bir_2307` |
| 5-6 | SLSP generation + CSV export + GL reconciliation | `ipai_bir_slsp` |
| 6-8 | BIR returns (2550M/Q, 1601-EQ) + tier approval | `ipai_bir_returns` |
| 8-9 | Evidence pack generation + Azure Blob archival | `ipai_compliance_evidence` |
| 9-10 | Filing calendar + activity automation | `ipai_compliance_calendar` |
| 10-12 | Integration testing + compliance dashboard + UAT | All Phase 1 modules |

### Phase 2 (Months 4-6)

| Week | Deliverable | Module |
|------|------------|--------|
| 1-2 | Tax engine adapter framework | `ipai_tax_engine_adapter` |
| 2-4 | Avalara AvaTax connector + sandbox testing | `ipai_avalara_connector` |
| 4-5 | Cross-border rules + fiscal position automation | `ipai_compliance_crossborder` |
| 5-7 | E-invoicing framework + PH CAS stub | `ipai_compliance_einvoice` |
| 7-8 | Azure Document Intelligence integration | Enhancement to `ipai_bir_2307` |
| 8-9 | Integration testing + multi-jurisdiction UAT | All Phase 2 modules |

### Phase 3 (Months 7-12)

| Week | Deliverable | Module |
|------|------------|--------|
| 1-4 | Databricks DLT pipeline + analytics alerts | `ipai_compliance_analytics` |
| 4-6 | AI compliance advisor + MCP tools | `ipai_compliance_agent` |
| 6-8 | Regulatory drift monitoring | `ipai_compliance_drift` |
| 8-10 | Power BI control tower dashboard | Power BI workspace |
| 10-12 | Multi-entity consolidation + Phase 3 UAT | All modules |

---

## Test Strategy

### Unit Tests (per module)

Each module includes `tests/` directory with:
- `test_models.py`: Model CRUD, constraint validation, computed field correctness
- `test_computation.py`: Tax computation accuracy against known test vectors
- `test_workflow.py`: State transitions, approval gates, automation triggers

### Integration Tests

- `test_phase1_e2e.py`: Full cycle: vendor bill -> WHT -> 2307 -> SLSP -> 2550M -> evidence pack -> Azure Blob
- `test_phase2_routing.py`: Transaction routing: PH -> local engine, US -> Avalara, timeout -> fallback
- `test_phase3_agent.py`: Agent query -> rule retrieval -> response with citations -> no data mutation

### Test Data

- `test_vendor_bills_ph.csv`: 50 vendor bills with varying WHT rates, amounts, partner types
- `test_invoices_crossborder.csv`: 20 cross-border transactions (PH-US, PH-SG, PH-EU)
- Disposable test DB: `test_ipai_compliance` (never shared, destroyed after test run)

---

## Success Metrics (from PRD, operationalized)

| PRD Metric | Phase | Measurement |
|-----------|-------|-------------|
| 50% reduction in manual compliance exception handling | Phase 1 | Time-to-resolve for missing-2307 exceptions: before vs after |
| 70% reduction in time-to-root-cause for filing exceptions | Phase 1 | Median time from exception detection to identification of root cause |
| 100% audit trail coverage | Phase 1 | Zero compliance actions without `mail.tracking.value` or evidence pack |
| >95% low-risk determinations without manual re-entry | Phase 1 | Percentage of vendor bills where 2307 auto-generated correctly |
| <15 min median evidence pack generation | Phase 1 | Time from `bir.return` state=reviewed to evidence pack sealed |
| Time to first jurisdiction activation <14 days | Phase 2 | Time to add a new jurisdiction configuration (US via Avalara) |
| >80% exceptions routed with recommended remediation | Phase 3 | Percentage of analytics alerts with agent-generated remediation recommendation |

---

*Last updated: 2026-04-07*
