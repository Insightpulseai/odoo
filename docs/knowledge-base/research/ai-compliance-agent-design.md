# AI Compliance Agent Design for Odoo 18 CE

> **Status**: Research report -- decision-ready draft
> **Date**: 2026-04-07
> **Platform**: Odoo 18 CE + OCA + ipai_* on Azure (ACA, PostgreSQL, AI Foundry, Databricks)
> **Primary jurisdiction**: Philippines (BIR, TRAIN Law, CREATE Law)
> **Secondary scope**: Cross-border, multi-jurisdiction, OECD BEPS

---

## Executive Summary

An AI compliance agent for an ERP platform must solve a specific problem: ensuring that every financial transaction processed by the system conforms to the tax, reporting, and regulatory requirements of every jurisdiction the business operates in -- without introducing hallucinated legal conclusions or automating decisions that require human judgment.

This report defines the compliance scope, maps required capabilities to Odoo 18 CE surfaces, recommends a target architecture on Azure, and provides a phased implementation plan. The core design principle is **deterministic rules first, AI assistance second, human authority always**. Tax determination and document validation are automatable. Legal interpretation, filing submission, and policy exceptions are not.

The minimum viable agent covers Philippine BIR compliance (VAT, EWT, BIR forms 2307/2550M/Q/1601-EQ, SLSP, TIN validation) using the existing `ipai_bir_tax_compliance` module and `ph_rates_2025.json` as the canonical rates authority. Cross-border and multi-jurisdiction support are Phase 2+ concerns that benefit from external tax engines (Avalara AvaTax) rather than custom rule maintenance.

---

## 1. Compliance Scope

### 1.1 Local Compliance -- Philippines

Philippine compliance for a business ERP spans five regulatory bodies and their overlapping requirements:

| Authority | Domain | Key Requirements |
|-----------|--------|-----------------|
| **BIR** (Bureau of Internal Revenue) | Tax | VAT (12%), EWT (1-10%), final WHT, BIR forms (2307, 2550M/Q, 1601-EQ, 1702Q), SLSP, CAS permit, e-invoicing |
| **TRAIN Law** (RA 10963) | Tax rates/brackets | Graduated income tax, VAT threshold (PHP 3M), percentage tax (3%), excise tax |
| **CREATE Law** (RA 11534) | Corporate tax | 25% CIT (standard), 2% MCIT, reduced rates for SMEs, fiscal incentives |
| **SEC** (Securities & Exchange Commission) | Corporate governance | Annual financial statements (PFRS/PAS), GIS, beneficial ownership, related party disclosures |
| **BSP** (Bangko Sentral ng Pilipinas) | FX and payments | Cross-border remittance documentation, FX transaction reporting (if applicable) |
| **NPC** (National Privacy Commission) | Data privacy | RA 10173 (Data Privacy Act): consent, retention limits, breach notification, DPO appointment |

The BIR compliance surface is the largest and most automatable. The canonical rates are already codified in `ph_rates_2025.json` with ATC codes (W010-W170 for EWT, F001-F005 for final WHT) and graduated income tax brackets from TRAIN Law.

### 1.2 International Compliance

Cross-border compliance requirements for an ERP platform:

| Domain | Requirement | Complexity |
|--------|------------|------------|
| **Cross-border VAT/GST** | Determine if VAT applies on import/export, reverse charge mechanism, place of supply rules | High -- jurisdiction-specific |
| **Transfer pricing** | Arm's length pricing for related-party transactions, documentation (TP study) | Very high -- requires specialist |
| **OECD BEPS** | Pillar One/Two (global minimum tax 15%), country-by-country reporting (CbCR) | High -- evolving regulation |
| **E-invoicing mandates** | EU (ViDA), India (e-way bill), Saudi (ZATCA), Brazil (NF-e) -- each with unique schema | Very high -- per-country |
| **Withholding on cross-border payments** | Treaty rates, beneficial ownership, Forms W-8BEN (US), tax reclaim | High -- treaty network |
| **Customs and duties** | HS codes, origin determination, trade agreements (RCEP, AFTA) | Medium -- external systems |
| **Sanctions screening** | OFAC, EU sanctions lists, UN consolidated list | Medium -- external API |
| **FX and repatriation** | BSP reporting, FX gain/loss treatment, hedging documentation | Medium |

### 1.3 Compliance Domains Ranked by ERP Agent Value

Ordered by automation potential and business impact:

| Rank | Domain | Automation Potential | Business Impact |
|------|--------|---------------------|----------------|
| 1 | Indirect tax (VAT/EWT) determination | High | Critical |
| 2 | Invoice and document validation | High | Critical |
| 3 | Withholding tax computation and 2307 generation | High | Critical |
| 4 | Audit trail and evidence generation | High | High |
| 5 | Filing calendar and deadline management | High | High |
| 6 | Vendor/customer tax classification | Medium | High |
| 7 | Statutory report preparation (SLSP, 2550M/Q) | Medium | Critical |
| 8 | Internal controls and approval enforcement | Medium | High |
| 9 | Cross-border transaction classification | Low-Medium | Medium |
| 10 | Data privacy and records retention | Low | Medium |

---

## 2. Capability Map

### 2.1 Agent Capabilities

```
+------------------------------------------------------------------+
|                    AI COMPLIANCE AGENT                             |
|                                                                   |
|  +-----------------------+  +---------------------------+         |
|  | KNOWLEDGE LAYER       |  | DETECTION LAYER           |        |
|  | - Regulation ingestion|  | - Jurisdiction detection   |        |
|  | - Rate updates        |  | - Transaction classification|       |
|  | - Policy versioning   |  | - Anomaly/risk scoring     |        |
|  +-----------------------+  +---------------------------+         |
|                                                                   |
|  +-----------------------+  +---------------------------+         |
|  | COMPUTATION LAYER     |  | VALIDATION LAYER          |        |
|  | - Tax determination   |  | - Document completeness   |        |
|  | - WHT calculation     |  | - TIN format/existence    |        |
|  | - FX conversion       |  | - ATC code matching       |        |
|  +-----------------------+  +---------------------------+         |
|                                                                   |
|  +-----------------------+  +---------------------------+         |
|  | REPORTING LAYER       |  | WORKFLOW LAYER            |        |
|  | - BIR form generation |  | - Filing reminders        |        |
|  | - SLSP export         |  | - Approval routing        |        |
|  | - Evidence packs      |  | - Escalation to human     |        |
|  | - Audit trail         |  | - Policy change alerts    |        |
|  +-----------------------+  +---------------------------+         |
+------------------------------------------------------------------+
```

### 2.2 Capability Detail

| Capability | Description | Data Source | Odoo Surface |
|-----------|-------------|-------------|--------------|
| **Regulatory knowledge ingestion** | Parse and version tax rates, thresholds, ATC codes from BIR issuances | `ph_rates_2025.json`, BIR RR/RMC publications | `ir.config_parameter`, custom rates model |
| **Jurisdiction detection** | Determine applicable tax jurisdiction from partner country, fiscal position, transaction type | `res.partner.country_id`, `account.fiscal.position` | `account.fiscal.position.rule` |
| **Transaction classification** | Map invoice lines to correct tax treatment (VATable, zero-rated, exempt, EWT rate) | Product category, partner type, fiscal position | `account.tax`, `account.tax.group`, `product.template.taxes_id` |
| **Tax determination** | Compute VAT, EWT, percentage tax, final WHT on each transaction | Rates from `ph_rates_2025.json`, fiscal position | `account.tax._compute_amount()` |
| **Document validation** | Verify invoice completeness: TIN present, ATC code assigned, amounts reconcile | `account.move` fields, partner master | Custom validation on `account.move.write()` |
| **Anomaly/risk detection** | Flag missing WHT on qualifying bills, VAT mismatches, unusual patterns | GL balances, historical patterns | Cron + Databricks anomaly detection |
| **Filing/remittance support** | Prepare BIR forms (2307, 2550M/Q, 1601-EQ), SLSP CSV, deadline tracking | `account.move.line` aggregation | `ipai_bir_returns` (planned), `ipai_bir_2307` (planned) |
| **Evidence and audit trail** | Immutable log of every tax decision, approval, and filing action | `ir.logging`, `mail.tracking.value` | `mail.thread` on compliance models |
| **Escalation** | Route ambiguous or high-risk items to human reviewers | Risk score threshold | `base_tier_validation`, `mail.activity` |
| **Policy update detection** | Monitor for new BIR issuances and flag stale rates | External feed or manual update | Agent alert + `ir.config_parameter` version check |

---

## 3. Automation Boundaries

This is the most critical design decision. The agent must never fully automate regulated decisions that carry legal liability.

### 3.1 Fully Automated (No Human Gate)

| Action | Justification | Control |
|--------|--------------|---------|
| VAT computation (12% on VATable lines) | Deterministic math on codified rates | Unit-tested tax computation |
| EWT computation (1/2/5/10% by ATC) | Deterministic lookup from `ph_rates_2025.json` | ATC-to-rate mapping is canonical |
| TIN format validation (regex) | Pattern match: `^\d{3}-\d{3}-\d{3}-\d{3}$` | Constraint on `res.partner.vat` |
| Fiscal position auto-apply | Country/partner-type rules | `account.fiscal.position.rule` |
| Filing deadline reminders | Calendar math from BIR schedule | `ir.cron` + `mail.activity` |
| SLSP data aggregation | SQL aggregation of posted entries | Read-only report over `account.move.line` |
| Audit trail logging | Append-only event capture | `ir.logging` + `mail.tracking.value` |
| Document completeness check | Required field validation | `_check_*` constraints on `account.move` |

### 3.2 Human-in-the-Loop (Agent Prepares, Human Approves)

| Action | Why Human Required | Workflow |
|--------|-------------------|----------|
| BIR form filing submission | Legal filing carries penalties for errors | Agent generates form; accountant reviews and submits |
| Vendor tax classification change | Affects all future transactions for that vendor | Agent recommends; accounting manager approves via tier validation |
| Fiscal position override | Exception to standard rules | Agent flags deviation; supervisor approves |
| Credit note with WHT reversal | Affects previously issued 2307 | Agent prepares replacement 2307; accountant confirms |
| VAT threshold crossing response | Requires BIR registration change | Agent detects threshold; compliance officer initiates registration |
| Monthly tax remittance amounts | Remitted amounts must match BIR records exactly | Agent computes; accountant verifies before remittance |

### 3.3 Advisory Only (Agent Suggests, Human Decides and Acts)

| Action | Why Advisory Only | Output |
|--------|------------------|--------|
| Transfer pricing assessment | Requires specialist judgment, not rule application | Risk flag + recommendation to engage TP consultant |
| Tax treaty rate selection | Beneficial ownership determination is legal judgment | Suggested rate + treaty reference for tax counsel |
| CAS permit application | BIR administrative process | Checklist of requirements + status tracker |
| SEC filing preparation | Financial statement audit required | Deadline reminder + document checklist |
| Cross-border structuring | Tax planning is legal counsel territory | Jurisdictional summary for advisor |

### 3.4 Blocked Unless Explicitly Approved

| Action | Approver | Mechanism |
|--------|----------|-----------|
| Override computed tax amount | CFO or Tax Manager | `base_tier_validation` with mandatory comment |
| Delete or modify posted journal entry | Controller | Odoo lock date + `res.groups` restriction |
| Submit filing to BIR (when e-filing is implemented) | Authorized tax signatory | Digital signature + 2FA gate |
| Change canonical tax rates (`ph_rates_2025.json`) | Compliance officer | PR review + CI validation of rate schema |
| Grant compliance-role access | System administrator | Entra ID group assignment |

---

## 4. Local vs International Comparison

### 4.1 Where Rules Are Similar

| Area | PH Rule | International Equivalent | Shared Logic |
|------|---------|------------------------|--------------|
| VAT on domestic sales | 12% output VAT | EU VAT, India GST, etc. | Percentage-of-base computation |
| Invoice required fields | TIN, address, date, amount, tax | Most jurisdictions require similar | Document validation framework |
| WHT on services | 2% EWT on services (W158) | Many countries withhold on payments to non-residents | Withholding calculation engine |
| Filing deadlines | 2550M due 20th of following month | All jurisdictions have periodic filing | Calendar + reminder engine |
| Audit trail | CAS requirement for ERP | SOX (US), GDPR (EU) require audit trails | Immutable logging |

These similarities mean the core computation and validation engine can be jurisdiction-agnostic, with jurisdiction-specific configuration.

### 4.2 Where Rules Diverge Sharply

| Area | PH Specifics | International Differences | Impact |
|------|-------------|--------------------------|--------|
| **WHT system** | Buyer withholds on domestic purchases; BIR 2307 certificate required | Most countries only withhold on cross-border payments | PH needs a domestic WHT engine unique among ASEAN |
| **ATC codes** | BIR-specific alphanumeric codes (W157, W158, etc.) | No equivalent in most countries | PH-specific data model |
| **BIR forms layout** | Prescribed exact PDF layouts (2307, 2550M/Q) | Each country has unique form formats | Per-jurisdiction report templates |
| **SLSP** | Monthly purchase/sales list attached to VAT return | Some countries require SAF-T, others VAT ledger | Report format varies completely |
| **E-invoicing** | CAS permit + planned EIS/CAS integration | EU Peppol, India GST e-way bill, Saudi ZATCA -- all different | Cannot build a single e-invoicing connector |
| **Percentage tax** | 3% for non-VAT entities below PHP 3M threshold | No direct equivalent in most jurisdictions | PH-specific fiscal position |

### 4.3 Configuration vs Custom Logic

| Approach | When Sufficient | Examples |
|----------|----------------|---------|
| **Configuration only** | Rate changes, threshold updates, deadline shifts | VAT rate from 12% to a future rate; filing date changes |
| **Fiscal position mapping** | Different tax treatment by partner type | Zero-rated exports, VAT-exempt, government entity |
| **Custom PH logic (`ipai_bir_*`)** | BIR-specific forms, ATC codes, 2307 generation, SLSP format | These have no OCA or Odoo CE equivalent |
| **External tax engine (Avalara)** | Multi-state US sales tax, EU VAT MOSS, cross-border determination | Jurisdiction count exceeds maintainable custom rules |
| **Custom international logic** | OECD BEPS reporting, transfer pricing documentation | Rare, low-volume, specialist-driven |

---

## 5. Recommended Architecture

### 5.1 Architecture Diagram

```
+-----------------------------------------------------------------------+
|                          ODOO 18 CE (ACA)                             |
|                                                                       |
|  +------------------+  +-------------------+  +--------------------+  |
|  | account.move     |  | account.tax       |  | account.fiscal     |  |
|  | account.move.line|  | account.tax.group |  | .position          |  |
|  | res.partner      |  | (ph_rates_2025)   |  | .position.rule     |  |
|  +--------+---------+  +---------+---------+  +---------+----------+  |
|           |                      |                       |            |
|  +--------v---------+  +--------v----------+  +---------v----------+  |
|  | VALIDATION        |  | TAX ENGINE        |  | JURISDICTION       |  |
|  | LAYER             |  | (Deterministic)   |  | DETECTOR           |  |
|  | ipai_compliance_  |  | ipai_bir_tax_     |  | account.fiscal     |  |
|  | validator         |  | compliance        |  | .position.rule     |  |
|  +--------+---------+  +---------+---------+  +--------------------+  |
|           |                      |                                    |
|  +--------v---------+  +--------v----------+                         |
|  | WORKFLOW /        |  | REPORTING          |                        |
|  | APPROVAL          |  | ipai_bir_returns   |                        |
|  | base_tier_        |  | ipai_bir_2307      |                        |
|  | validation        |  | (SLSP, 2550M/Q)    |                        |
|  +--------+---------+  +---------+---------+                         |
|           |                      |                                    |
+-----------------------------------------------------------------------+
            |                      |
   +--------v---------+  +--------v----------+  +--------------------+
   | AZURE AI FOUNDRY  |  | AZURE DOCUMENT    |  | AVALARA AVATAX    |
   | (Advisory Agent)  |  | INTELLIGENCE      |  | (Phase 2)         |
   |                   |  | (OCR/extraction)  |  | (Cross-border)    |
   | - Anomaly explain |  | - Vendor invoice  |  | - US sales tax    |
   | - Policy Q&A      |  |   extraction      |  | - EU VAT          |
   | - Risk narrative   |  | - TIN extraction  |  | - GST/HST         |
   +--------+----------+  +---------+---------+  +--------------------+
            |                      |
   +--------v---------+  +--------v----------+
   | DATABRICKS        |  | AZURE BLOB        |
   | (Analytics)       |  | (Archive)         |
   | - WHT leakage     |  | - BIR 2307 PDFs   |
   | - VAT mismatch    |  | - SLSP CSVs       |
   | - Threshold watch  |  | - 10yr retention  |
   +-------------------+  +-------------------+
```

### 5.2 Component Responsibilities

| Component | Technology | Responsibility |
|-----------|-----------|----------------|
| **Core compliance policy engine** | `ipai_bir_tax_compliance` + `ph_rates_2025.json` | Canonical tax rates, ATC codes, computation rules. Deterministic, no AI. |
| **Jurisdiction knowledge base** | `account.fiscal.position` + `account.fiscal.position.rule` + future `jurisdiction.profile` model | Maps partner/country/transaction to applicable tax regime |
| **ERP integration layer** | Odoo `account.move`, `account.tax`, `res.partner` | Standard Odoo accounting models -- the compliance agent operates ON these, never replaces them |
| **Tax engine integration** | Avalara AvaTax REST API (Phase 2) | Multi-jurisdiction tax determination for US/EU/cross-border; replaces manual rate tables for non-PH |
| **Document/OCR validation** | Azure Document Intelligence (prebuilt invoice model) | Extract TIN, amounts, tax lines from scanned vendor invoices; feed into `account.move` creation |
| **Audit/event logging** | `ir.logging` + `mail.thread` + `mail.tracking.value` | Immutable record of every compliance decision, override, and approval |
| **Workflow/approval orchestration** | OCA `base_tier_validation` + `mail.activity` | Route high-risk items to human reviewers; enforce SoD |
| **Reporting and evidence packs** | `ipai_bir_returns` (planned) + Azure Blob (immutable) | Generate BIR forms, SLSP, evidence archives with 10-year retention |
| **Regulatory update monitoring** | Azure AI Foundry agent + manual review | Flag when `ph_rates_2025.json` may be stale; surface new BIR issuances for human review |
| **Analytics and anomaly detection** | Databricks (DLT pipeline) | Detect WHT leakage, VAT input/output mismatch, threshold approach, unusual patterns |

### 5.3 Key Odoo Models and OCA Modules

| Model / Module | Source | Role in Compliance Agent |
|---------------|--------|--------------------------|
| `account.move` | Core | Primary transaction record; all tax computations attach here |
| `account.move.line` | Core | Tax line details; source data for all BIR reports |
| `account.tax` | Core | Tax rate definitions; agent validates these match `ph_rates_2025.json` |
| `account.tax.group` | Core | Tax grouping (VAT, EWT, Final WHT, Percentage Tax) |
| `account.fiscal.position` | Core | Jurisdiction-based tax mapping |
| `account.fiscal.position.rule` | Core | Auto-detection rules (country, partner type) |
| `res.partner` | Core | TIN (`vat` field), fiscal position, country, tax classification |
| `l10n_ph` | Core | Philippine chart of accounts, basic BIR 2307 |
| `account_tax_python` | Core | Python-computed taxes for complex WHT rules |
| `base_tier_validation` | OCA | Approval workflows for compliance-gated actions |
| `account_fiscal_position_autodetect` | OCA | Auto-apply fiscal position by partner/country |
| `account_payment_order` | OCA | Batch payment processing for tax remittances |
| `mis_builder` | OCA | Management reporting; basis for BIR form data extraction |
| `account_financial_report` | OCA | Trial balance, GL reports for SEC/BIR |
| `base_user_role` | OCA | Role-based access for compliance SoD |
| `ipai_bir_tax_compliance` | Custom | Tax rates data, ATC codes, rate validation |
| `ipai_bir_2307` | Custom (planned) | Enhanced BIR 2307 generation with PDF layout |
| `ipai_bir_returns` | Custom (planned) | BIR 2550M/Q, 1601-EQ computation and export |
| `ipai_bir_einvoice` | Custom (planned) | CAS-compliant e-invoicing |
| `ipai_compliance_validator` | Custom (proposed) | Cross-cutting validation agent orchestrator |

---

## 6. Data Requirements

### 6.1 Data Inputs

| Data Category | Odoo Model / Source | Fields Required | Quality Gate |
|--------------|--------------------|--------------------|--------------|
| **Chart of accounts** | `account.account` (l10n_ph) | Account code, type, tax-relevant flag | Must match BIR prescribed chart |
| **Tax codes (ATC)** | `ph_rates_2025.json` | ATC code, rate, description, effective dates | Version-controlled; schema-validated |
| **Customer/vendor master** | `res.partner` | `vat` (TIN), `country_id`, `property_account_position_id`, `company_type` | TIN regex validated; fiscal position assigned |
| **Product/service classification** | `product.template` | `taxes_id` (default taxes), `categ_id` | Every product must have default tax assigned |
| **Invoice/receipt data** | `account.move` + `account.move.line` | All standard fields + tax lines | Completeness check on validation |
| **Transaction metadata** | `account.move` | `date`, `invoice_date`, `currency_id`, `company_id` | Date within open fiscal period |
| **Geographic/jurisdiction** | `res.partner.country_id` + `res.partner.state_id` | Country, state/province | Required for fiscal position detection |
| **Approval history** | `tier.review` (base_tier_validation) | Reviewer, status, date, comment | Immutable after approval |
| **Filing calendars** | `bir.filing.deadline` (ipai_bir_tax_compliance) | Form type, due date, period | Pre-loaded from BIR schedule |
| **Bank statements** | `account.bank.statement.line` | Amount, date, partner, reference | For reconciliation and cash basis VAT |

### 6.2 Data Quality Requirements

| Requirement | Implementation | Enforcement |
|------------|---------------|-------------|
| Every partner with PH transactions has a valid TIN | `_check_vat` constraint on `res.partner` | Block invoice posting without TIN |
| Every vendor bill has correct EWT applied | Cron: `ipai_bir_tax_compliance` flags bills missing WHT | Daily exception report |
| Tax rates match canonical source | Startup check: `account.tax` rates vs `ph_rates_2025.json` | CI validation + Odoo server action |
| SLSP totals reconcile to GL | Monthly: sum(SLSP) == sum(GL tax accounts) | Automated reconciliation report |
| BIR 2307 exists for every WHT transaction | Cron: vendor bills with WHT lines but no 2307 record | Exception queue with aging |

---

## 7. Risks and Controls

### 7.1 Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| R1 | **Hallucinated legal conclusions** -- AI agent states incorrect legal position | High (inherent to LLMs) | Critical | AI layer is advisory-only; all legal/tax positions sourced from codified rules (`ph_rates_2025.json`), never from LLM generation. LLM outputs carry explicit "not legal advice" framing. |
| R2 | **Outdated regulations** -- `ph_rates_2025.json` becomes stale after BIR issuance | Medium | High | Version field + `effective_to` date on rate records. Agent checks version on every tax computation. Quarterly manual review by compliance officer. Monitoring agent for new BIR RR/RMC. |
| R3 | **Incorrect tax classification** -- Wrong ATC code applied to transaction | Medium | High | Default taxes on product templates. Fiscal position auto-detection. Exception report for transactions with no or unusual tax treatment. |
| R4 | **False positives in anomaly detection** -- Agent flags legitimate transactions as suspicious | High | Medium | Risk score threshold tuning. Human review queue (not auto-block). Feedback loop to improve scoring. |
| R5 | **False negatives** -- Agent misses a non-compliant transaction | Medium | Critical | Multiple detection layers: real-time validation + daily cron + monthly reconciliation. No single point of failure. |
| R6 | **Over-automation** -- Agent files or remits without human confirmation | Low (by design) | Critical | Architecture explicitly blocks filing submission without human approval. `base_tier_validation` enforces gates. |
| R7 | **Weak auditability** -- Cannot reconstruct why a tax decision was made | Medium | High | Every tax computation logged with input parameters and output. `mail.tracking.value` on all compliance fields. Immutable journal entries (no draft reset after posting). |
| R8 | **Poor segregation of duties** -- Same user prepares and approves filings | Medium | High | OCA `base_user_role` + Entra ID group mapping. `base_tier_validation` requires different user for preparation vs approval. |
| R9 | **Cross-border complexity explosion** -- Attempt to maintain tax rules for too many jurisdictions | Medium | High | Phase 2 uses Avalara for non-PH jurisdictions. Never build custom rate tables for countries with >5 tax rules. |
| R10 | **Data privacy violation** -- TIN or financial data exposed or retained beyond legal period | Low | Critical | RA 10173 compliance: data classification on `res.partner` fields, retention policies on Azure Blob (10yr for BIR, then purge), access logging via `ir.logging`. |
| R11 | **Rate file tampering** -- Unauthorized change to `ph_rates_2025.json` | Low | Critical | File is version-controlled in Git. Changes require PR review. CI validates against JSON schema. Hash check on module load. |

### 7.2 Control Framework

```
Layer 1: Preventive Controls
  - Input validation (TIN regex, required fields, tax assignment)
  - Fiscal position auto-detection (prevents wrong jurisdiction)
  - Tier validation approval gates (prevents unauthorized actions)
  - Role-based access (SoD enforcement)

Layer 2: Detective Controls
  - Daily cron: missing WHT on qualifying transactions
  - Monthly reconciliation: SLSP vs GL balances
  - Anomaly detection: unusual tax patterns (Databricks)
  - Rate staleness check: version/date on ph_rates_2025.json

Layer 3: Corrective Controls
  - Exception queue with aging and escalation
  - Credit note workflow for incorrect tax treatment
  - Replacement 2307 generation
  - Compliance officer override with mandatory audit trail
```

---

## 8. Implementation Roadmap

### Phase 1: Philippine Compliance Automation (MVP)

**Timeline**: 8-12 weeks
**Scope**: Full BIR tax compliance for domestic Philippine transactions

| Deliverable | Module | Dependencies | Success Criteria |
|------------|--------|-------------|-----------------|
| Tax rate validation engine | `ipai_bir_tax_compliance` (enhance existing) | `ph_rates_2025.json` schema validation | All `account.tax` records match canonical rates on module install |
| BIR 2307 auto-generation | `ipai_bir_2307` (new) | `l10n_ph`, `account` | 2307 record auto-created on vendor bill validation with WHT; PDF matches BIR layout |
| SLSP report | `ipai_bir_slsp` (new) | `account` | Monthly SLSP CSV export matches BIR pipe-delimited format; totals reconcile to GL |
| VAT return preparation | `ipai_bir_returns` (new) | `account`, `ipai_bir_slsp` | BIR 2550M data computed correctly; SLSP attached |
| EWT remittance report | `ipai_bir_returns` | `account` | BIR 1601-EQ quarterly computation matches GL WHT payable |
| TIN validation | `ipai_bir_tax_compliance` (enhance) | `res.partner` | Regex constraint active; bulk validation on existing partners |
| Filing deadline alerts | `ipai_bir_tax_compliance` (enhance) | `mail.activity`, `ir.cron` | Activities created 5 business days before each deadline |
| Compliance dashboard | `ipai_bir_tax_compliance` (enhance) | All above | Single view: open filings, missing 2307s, SLSP status, upcoming deadlines |
| Document extraction | Azure Document Intelligence | Azure subscription | Vendor invoice OCR extracts TIN + amounts with >90% accuracy |
| Approval workflow | OCA `base_tier_validation` | `purchase`, `account` | Vendor bills above PHP 500K require tier approval before posting |

**Key risks**: BIR 2307 PDF layout must match prescribed format exactly (pixel-level). SLSP CSV column order is strict. Test with actual BIR eFPS upload.

**Dependencies**: OCA `base_tier_validation` must be verified for Odoo 18 CE compatibility.

### Phase 2: Cross-Border and External Tax Engine

**Timeline**: 12-16 weeks after Phase 1
**Scope**: International transactions, Avalara integration, enhanced anomaly detection

| Deliverable | Module / Service | Dependencies | Success Criteria |
|------------|-----------------|-------------|-----------------|
| Avalara AvaTax integration | `ipai_tax_avalara` (new) | Avalara account, API key | Tax determination for US/EU transactions uses Avalara; PH transactions continue using local engine |
| Cross-border fiscal positions | Configuration | `account.fiscal.position` | Fiscal positions for ASEAN, EU, US with correct tax mapping |
| Non-resident WHT | `ipai_bir_tax_compliance` (enhance) | `ph_rates_2025.json` (add non-resident rates) | Correct final WHT on payments to non-resident foreign corps |
| FX gain/loss on tax | `account` configuration | Multi-currency setup | Tax amounts correctly computed in PHP equivalent |
| Databricks anomaly pipeline | Databricks DLT | JDBC to PostgreSQL | Weekly anomaly report: WHT leakage, VAT mismatch, threshold approach |
| E-invoicing foundation | `ipai_bir_einvoice` (new) | CAS permit, BIR EIS specification | Invoice XML schema matches BIR CAS requirements |
| Evidence archival | Azure Blob + lifecycle | Immutable storage policy | 2307 PDFs and SLSP CSVs archived with 10-year retention, tamper-proof |

**Key risks**: Avalara pricing model (per-transaction fees). CAS/EIS specification may change. Multi-currency WHT computation edge cases.

**Dependencies**: Avalara sandbox account. BIR CAS permit application (administrative prerequisite). Databricks workspace provisioned.

### Phase 3: Multi-Jurisdiction and Predictive Compliance

**Timeline**: 16-24 weeks after Phase 2
**Scope**: OECD BEPS awareness, predictive analytics, multi-entity

| Deliverable | Module / Service | Dependencies | Success Criteria |
|------------|-----------------|-------------|-----------------|
| Multi-entity tax consolidation | Configuration + custom | Multi-company Odoo setup | Consolidated VAT/WHT reporting across entities |
| Transfer pricing documentation support | Advisory agent (AI Foundry) | TP policy documentation | Agent generates TP documentation templates with transaction data pre-filled |
| BEPS Pillar Two monitoring | Databricks analytics | Multi-entity financial data | Effective tax rate computation per jurisdiction; flag if below 15% |
| Predictive filing | Databricks ML | Historical filing data | Predict monthly VAT payable within 5% accuracy by day 10 of month |
| Regulatory change monitoring | AI Foundry agent + web monitoring | BIR RSS/publication feeds | New BIR issuances surfaced within 48 hours with impact assessment |
| Additional jurisdiction packs | `ipai_tax_*` per country | Avalara for tax; local for forms | Support for SG GST, ID VAT, VN VAT (ASEAN expansion) |

**Key risks**: BEPS Pillar Two rules are still evolving. Transfer pricing is inherently advisory. Multi-entity introduces intercompany elimination complexity.

---

## 9. Benchmark Insights

### 9.1 SAP GRC / Tax Engine Capabilities

SAP enterprise compliance includes:

| SAP Component | Capability | Enterprise Expectation |
|--------------|-----------|----------------------|
| **Tax Engine** | Multi-jurisdiction tax determination with condition tables, withholding tax types, tax reporting | Automatic tax code assignment based on material/vendor/country matrix; support for 100+ countries |
| **GRC Access Control** | SoD matrix, access risk analysis, emergency access, role mining | Preventive SoD checks on role assignment; continuous monitoring of violations |
| **GRC Process Control** | Continuous monitoring of financial controls, automated testing | Real-time control testing against GL postings; exception dashboard |
| **GRC Audit Management** | Audit planning, execution tracking, issue management | Full audit lifecycle from planning through remediation tracking |
| **Document Compliance** | Country-specific form generation, e-invoicing (SAP DRC) | Peppol, ZATCA, NF-e, e-way bill -- all from single framework |

### 9.2 Odoo 18 CE + OCA Native Coverage

| SAP Equivalent | Odoo CE + OCA Coverage | Gap Size |
|---------------|----------------------|----------|
| Tax Engine (single country) | `account.tax` + fiscal positions + `l10n_ph` -- **adequate for PH** | Small -- needs `ipai_bir_*` for BIR forms |
| Tax Engine (multi-country) | Fiscal positions handle basics; no condition tables | Large -- needs Avalara for >3 jurisdictions |
| GRC Access Control | `res.groups` + `ir.rule` + OCA `base_user_role` -- basic | Large -- no SoD matrix, no risk analysis |
| GRC Process Control | None native | Very large -- custom build or Databricks |
| GRC Audit Management | `mail.thread` + `mail.activity` -- basic trail | Large -- no audit lifecycle management |
| Document Compliance | None for country-specific forms | Large per country -- each needs custom module |
| E-invoicing | None in CE | Very large -- needs per-country connector |

### 9.3 Where Avalara Adds Most Value

| Scenario | Build Custom | Use Avalara | Recommendation |
|---------|-------------|-------------|----------------|
| PH domestic VAT/EWT | Simple, well-defined rates | Overkill (Avalara has limited PH depth) | **Build custom** (`ipai_bir_*`) |
| US multi-state sales tax | 11,000+ jurisdictions, nexus rules | Core strength of Avalara | **Use Avalara** |
| EU VAT (cross-border, MOSS) | 27 member states, place of supply rules | Strong Avalara coverage | **Use Avalara** |
| ASEAN cross-border | Limited Avalara coverage | Varies by country | **Hybrid** -- Avalara where supported, custom for gaps |
| WHT on cross-border payments | Treaty rates are complex but low volume | Avalara supports some; not all treaties | **Advisory + lookup table** |
| E-invoicing (EU, Saudi, India) | Per-country effort is massive | Avalara partners offer this | **Buy** (Avalara or specialized provider) |

### 9.4 What Must Remain Custom (`ipai_*`)

These cannot be bought or configured -- they require custom Philippine-specific logic:

| Module | Reason |
|--------|--------|
| `ipai_bir_2307` | BIR-prescribed form layout; links to domestic WHT workflow unique to PH |
| `ipai_bir_returns` | BIR 2550M/Q and 1601-EQ computation from Odoo GL data; BIR-specific boxes and schedules |
| `ipai_bir_slsp` | Pipe-delimited CSV in BIR-prescribed column order |
| `ipai_bir_einvoice` | CAS/EIS integration per BIR specifications (once finalized) |
| `ipai_bir_tax_compliance` | ATC code registry, rate validation, PH-specific controls |
| `ipai_compliance_validator` | Cross-cutting agent orchestrator: routes transactions through correct validation pipeline |

---

## 10. Final Recommendations

### 10.1 Target Operating Model

```
Deterministic Rules Engine (80% of compliance work)
  |
  +-- Codified rates (ph_rates_2025.json)
  +-- Odoo tax computation (account.tax)
  +-- Fiscal position auto-detection
  +-- Document validation constraints
  +-- Filing calendar automation
  |
AI Advisory Layer (15% of compliance work)
  |
  +-- Anomaly explanation (why was this flagged?)
  +-- Policy Q&A (what ATC code applies to this transaction?)
  +-- Risk narrative generation for audit packs
  +-- Regulatory change impact assessment
  |
Human Authority Layer (5% of compliance work, 100% of liability)
  |
  +-- Filing submission approval
  +-- Tax position interpretation
  +-- Exception and override decisions
  +-- Regulatory registration changes
  +-- Cross-border structuring decisions
```

### 10.2 Build vs Buy

| Component | Decision | Rationale |
|-----------|----------|-----------|
| PH BIR compliance (VAT, EWT, forms) | **Build** (ipai_bir_*) | PH-specific, low volume of jurisdictions, existing module foundation, no adequate commercial product for Odoo CE |
| Multi-jurisdiction indirect tax | **Buy** (Avalara AvaTax) | Maintaining tax rules for US/EU/ASEAN is unsustainable custom; Avalara's core product |
| Document OCR/extraction | **Buy** (Azure Document Intelligence) | Pre-built invoice model is production-ready; building OCR is not core competency |
| Anomaly detection | **Build** (Databricks) | Domain-specific anomalies (WHT leakage, VAT mismatch) require custom logic on proprietary data |
| Approval workflows | **Adopt OCA** (base_tier_validation) | Well-maintained, configurable, covers 90% of approval needs |
| SoD and access governance | **Build** (ipai_platform_audit) | OCA `base_user_role` provides foundation; SoD matrix is custom to organization |
| E-invoicing (non-PH) | **Buy** (when needed) | Per-country e-invoicing connectors are too expensive to build; buy from specialized vendors |
| Audit trail | **Configure** (Odoo native + OCA) | `mail.thread`, `mail.tracking.value`, `ir.logging` are adequate with proper configuration |

### 10.3 Minimum Viable Compliance Agent

The MVP agent is not an LLM. It is a deterministic rules engine with structured data:

1. `ph_rates_2025.json` as the single source of truth for PH tax rates
2. `account.tax` records validated against canonical rates on every module update
3. `account.fiscal.position` rules that auto-detect jurisdiction
4. `_check_*` constraints on `account.move` that prevent posting non-compliant invoices
5. Cron jobs that detect missing 2307s, WHT gaps, and SLSP mismatches
6. `base_tier_validation` gates on high-value transactions
7. Filing deadline `mail.activity` reminders
8. BIR 2307 PDF generation from posted vendor bills

The LLM layer (Azure AI Foundry) comes second, adding:
- Natural language explanations of flagged exceptions
- Regulatory knowledge Q&A (sourced from indexed BIR issuances, not hallucinated)
- Risk narrative generation for audit evidence packs

### 10.4 Highest-Priority Compliance Workflows (Implementation Order)

| Priority | Workflow | Module | Rationale |
|----------|----------|--------|-----------|
| 1 | EWT computation + BIR 2307 generation | `ipai_bir_2307` | Most frequent compliance task; every vendor bill |
| 2 | SLSP monthly report | `ipai_bir_slsp` | Required attachment to monthly VAT return |
| 3 | VAT return preparation (2550M) | `ipai_bir_returns` | Monthly filing obligation |
| 4 | TIN validation on all partners | `ipai_bir_tax_compliance` | Foundation for all tax documents |
| 5 | Filing deadline automation | `ipai_bir_tax_compliance` | Prevents penalties from missed deadlines |
| 6 | WHT remittance report (1601-EQ) | `ipai_bir_returns` | Quarterly filing obligation |
| 7 | Vendor invoice OCR extraction | Azure Document Intelligence | Reduces manual data entry errors |
| 8 | Approval gates for high-value transactions | `base_tier_validation` | Internal control requirement |

### 10.5 What Must Never Be Fully Delegated to the Agent

| Decision | Why | Required Human Role |
|----------|-----|---------------------|
| BIR filing submission | Legal liability; penalties for incorrect filing | Authorized tax signatory |
| Tax position on ambiguous transactions | Legal interpretation, not rule application | Tax manager or external counsel |
| Transfer pricing determination | Requires economic analysis and specialist judgment | TP consultant |
| Tax treaty rate application | Beneficial ownership is a legal determination | Tax counsel |
| Regulatory registration changes (VAT, CAS) | Administrative act with BIR | Compliance officer |
| Override of computed tax amount | Exception to rules requires documented justification | CFO or Tax Manager with audit trail |
| Data privacy breach response | RA 10173 requires specific notification procedures | DPO |
| Cross-border structuring decisions | Tax planning requires legal and business context | CFO + external advisor |

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| ATC | Alphanumeric Tax Code -- BIR code identifying transaction type and applicable WHT rate |
| BIR | Bureau of Internal Revenue -- Philippine national tax authority |
| CAS | Computerized Accounting System -- BIR permit for ERP-generated official receipts/invoices |
| CREATE Law | Corporate Recovery and Tax Incentives for Enterprises Act (RA 11534) |
| EIS | Electronic Invoicing System -- planned BIR e-invoicing platform |
| EWT | Expanded Withholding Tax -- buyer-side withholding on domestic purchases |
| MCIT | Minimum Corporate Income Tax -- 2% of gross income, alternative to regular CIT |
| OECD BEPS | Base Erosion and Profit Shifting -- international tax framework |
| SLSP | Summary List of Sales and Purchases -- monthly BIR attachment |
| TIN | Tax Identification Number -- format XXX-XXX-XXX-XXX |
| TRAIN Law | Tax Reform for Acceleration and Inclusion Act (RA 10963) |

## Appendix B: Key File References

| File | Purpose |
|------|---------|
| `addons/ipai/ipai_bir_tax_compliance/data/rates/ph_rates_2025.json` | Canonical PH tax rates (SSOT) |
| `docs/knowledge-base/skill-packs/tax-compliance-ph/SKILL.md` | PH tax compliance skill pack for agents |
| `docs/knowledge-base/benchmark/sap-to-odoo-matrix.yaml` | SAP-to-Odoo capability benchmark |

---

*Source class: local + domain research synthesis*
*Generated: 2026-04-07*
