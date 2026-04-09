# Tasks: Agentic Global Compliance Cloud (AGCC)

> **Spec bundle**: `spec/agentic-global-compliance-cloud/`
> **PRD**: `prd.md`
> **Research**: `docs/knowledge-base/research/ai-compliance-agent-design.md`
> **Skill pack**: `docs/knowledge-base/skill-packs/tax-compliance-ph/SKILL.md`
> **Last updated**: 2026-04-07

---

## Phase 1: MVP -- PH BIR Compliance

Target: Full BIR tax compliance for domestic Philippine transactions.
Timeline: 8-12 weeks. Modules: `ipai_bir_tax_compliance` (enhance), `ipai_bir_2307` (new), `ipai_bir_slsp` (new), `ipai_bir_returns` (new).

### 1.1 Compliance Graph Foundation

- [ ] Design `ipai.compliance.jurisdiction` model (country_id, authority_code, authority_name, effective_date, active)
- [ ] Design `ipai.compliance.policy.rule` model (jurisdiction_id, rule_type selection, logic_python text, effective_from, effective_to, version)
- [ ] Design `ipai.compliance.obligation` model (company_id, jurisdiction_id, obligation_type selection, frequency selection, deadline_day integer, form_code char)
- [ ] Seed PH jurisdiction record (BIR, country=PH, authority_code=BIR)
- [ ] Implement PH jurisdiction pack loader from `ph_rates_2025.json` into policy.rule records
- [ ] Add `effective_from` / `effective_to` date fields on all rate records to support TRAIN Law effective date tracking
- [ ] Implement filing calendar using `ir.cron` to generate `mail.activity` reminders 5 business days before each BIR deadline
- [ ] Pre-load obligation records: 2550M (monthly, 20th), 2550Q (quarterly, 25th), 1601-EQ (quarterly, last day), 1702Q (quarterly, 60 days after quarter)
- [ ] Add JSON schema validation for `ph_rates_2025.json` on module install (fail loudly if schema violated)
- [ ] Add startup server action: validate all `account.tax` records match canonical rates in `ph_rates_2025.json`
- [ ] Add SHA-256 hash verification of `ph_rates_2025.json` on module load (`post_init_hook`); mismatch raises `UserError` (Constitution §4.2)
- [ ] Tests: jurisdiction resolution by country code
- [ ] Tests: policy rule versioning (overlapping effective dates rejected)
- [ ] Tests: deadline computation for all BIR form types across month boundaries

### 1.2 EWT Computation + BIR 2307 Generation

- [ ] Create `ipai_bir_2307` module scaffold (`__manifest__.py`, `__init__.py`, security, views, data dirs)
- [ ] Design `ipai.bir.2307` model (partner_id, period_start, period_end, atc_code, tax_base, tax_withheld, move_id, state selection [draft/confirmed/cancelled], company_id)
- [ ] Add `mail.thread` mixin on `ipai.bir.2307` for audit trail
- [ ] Implement `_compute_from_move()` method: extract WHT tax lines from `account.move.line` and populate 2307 fields
- [ ] Override `account.move.action_post()` to auto-create 2307 record when vendor bill has WHT tax lines
- [ ] Handle credit note scenario: auto-cancel original 2307 and create replacement for net amount
- [ ] Implement BIR 2307 PDF report using `ir.actions.report` with QWeb template matching BIR prescribed layout
- [ ] Map all 2307 PDF fields: payee TIN, payor TIN, ATC code, income payment, tax withheld per month, period, signatory
- [ ] Add `Print 2307` button on vendor bill form view (visible only when 2307 record exists)
- [ ] Add tree view for `ipai.bir.2307` with filters: period, partner, state, ATC code
- [ ] Add form view for `ipai.bir.2307` with readonly fields when state=confirmed
- [ ] Implement cron job: flag vendor bills with WHT tax lines but no linked 2307 record (daily, creates `mail.activity` on the bill)
- [ ] Add 2307 completeness dashboard action: count of bills missing 2307 by period
- [ ] Tests: 2307 auto-creation on bill validation with EWT 2% services (W158)
- [ ] Tests: 2307 auto-creation with multiple WHT lines on single bill (EWT 1% goods + EWT 2% services)
- [ ] Tests: 2307 cancellation and replacement on credit note
- [ ] Tests: PDF generation produces valid PDF with correct field mapping
- [ ] Tests: completeness cron detects bills missing 2307

### 1.3 SLSP (Summary List of Sales and Purchases)

- [ ] Create `ipai_bir_slsp` module scaffold
- [ ] Design `ipai.bir.slsp` transient model (wizard) with period_start, period_end, company_id
- [ ] Implement sales list query: `account.move` where `move_type in ('out_invoice','out_refund')`, grouped by `partner_id.vat`, summing `amount_untaxed`, output VAT, zero-rated, exempt
- [ ] Implement purchases list query: `account.move` where `move_type in ('in_invoice','in_refund')`, grouped by `partner_id.vat`, summing `amount_untaxed`, input VAT, EWT by ATC
- [ ] Implement CSV export in BIR pipe-delimited format with prescribed column order (TIN|REG_NAME|LAST_NAME|FIRST_NAME|MIDDLE_NAME|ADDRESS|AMOUNT|TAX)
- [ ] Add menu item under Accounting > Reports > BIR > SLSP
- [ ] Implement SLSP reconciliation check: sum of SLSP amounts must equal GL tax account balances for the period
- [ ] Add reconciliation discrepancy report with drill-down to offending entries
- [ ] Tests: SLSP sales list with mix of VATable, zero-rated, exempt invoices
- [ ] Tests: SLSP purchases list with multiple EWT rates
- [ ] Tests: CSV output format matches BIR specification (pipe delimiter, column order, encoding)
- [ ] Tests: reconciliation check passes when data is clean; fails and reports when mismatched

### 1.4 VAT Returns (BIR 2550M / 2550Q)

- [ ] Create `ipai_bir_returns` module scaffold (depends on `ipai_bir_slsp`)
- [ ] Design `ipai.bir.vat.return` model (period_type selection [monthly/quarterly], period_start, period_end, company_id, state selection [draft/computed/reviewed/filed])
- [ ] Implement Box 1-14 computation: Output VAT from sales tax lines by tax group
- [ ] Implement Box 15-20 computation: Input VAT from purchase tax lines by tax group
- [ ] Implement Box 21 computation: VAT Payable = Output VAT - Input VAT - prior excess credits (carry-forward logic)
- [ ] Link SLSP attachment: auto-attach generated SLSP CSV to the VAT return record
- [ ] Add form view with BIR 2550M box layout (readonly computed fields, editable adjustments with audit trail)
- [ ] Add `Compute` button to recalculate from GL data
- [ ] Add `Generate PDF` action producing BIR 2550M form layout
- [ ] Implement carry-forward: excess input VAT from prior period auto-populates next period
- [ ] Tests: 2550M computation with standard domestic transactions
- [ ] Tests: 2550M with zero-rated export sales (refundable input VAT)
- [ ] Tests: quarterly 2550Q aggregates three monthly periods correctly
- [ ] Tests: carry-forward of excess input VAT across periods

### 1.5 EWT Remittance (BIR 1601-EQ)

- [ ] Design `ipai.bir.ewt.return` model (quarter, year, company_id, state, total_tax_base, total_tax_withheld)
- [ ] Design `ipai.bir.ewt.return.line` model (return_id, atc_code, tax_rate, tax_base, tax_withheld, partner_count)
- [ ] Implement computation: aggregate WHT journal entries by ATC code for the quarter
- [ ] Add form view with BIR 1601-EQ schedule layout (lines grouped by ATC code)
- [ ] Add `Compute` button and `Generate PDF` action
- [ ] Cross-validate: total WHT on 1601-EQ must equal sum of all 2307 records for the quarter
- [ ] Tests: 1601-EQ computation with multiple ATC codes
- [ ] Tests: cross-validation between 1601-EQ and 2307 totals

### 1.6 TIN Validation and Partner Compliance

- [ ] Add `_check_vat_ph` constraint on `res.partner`: validate TIN format `^\d{3}-\d{3}-\d{3}-\d{3}$` when `country_id` is PH
- [ ] Add server action for bulk TIN validation on existing partners (flag invalid TINs via `mail.activity`)
- [ ] Block `account.move` posting when partner has PH country but missing or invalid TIN
- [ ] Add `compliance_status` computed field on `res.partner` (compliant/incomplete/invalid)
- [ ] Add partner list view filter for compliance status
- [ ] Tests: TIN validation rejects invalid formats (too short, letters, wrong separators)
- [ ] Tests: invoice posting blocked for partner with invalid TIN
- [ ] Tests: bulk validation correctly flags all non-compliant partners

### 1.7 Tax Configuration and Fiscal Positions

- [ ] Create `account.tax` records via data XML: Output VAT 12%, Input VAT 12%, EWT 1% (W157), EWT 2% (W158), EWT 5% (W160), EWT 10% (W170), Percentage Tax 3%
- [ ] Add `atc_code` field on `account.tax` (required when tax is WHT type)
- [ ] Create `account.fiscal.position` records: VAT Registered (Domestic), Non-VAT (Below Threshold), Zero-Rated (Export), VAT Exempt, Government Entity, Non-Resident Foreign Corp
- [ ] Create `account.fiscal.position.tax` mappings for each fiscal position
- [ ] Create `account.fiscal.position.rule` records for auto-detection by country and partner type
- [ ] Add fiscal position auto-detection: install and configure OCA `account_fiscal_position_autodetect` (verify 18.0 compatibility first)
- [ ] Tests: fiscal position auto-applies correctly for domestic VAT-registered partner
- [ ] Tests: fiscal position maps 12% VAT to 3% percentage tax for non-VAT entity
- [ ] Tests: fiscal position maps 12% VAT to 0% for export transaction

### 1.8 Approval Workflows and SoD

- [ ] Verify OCA `base_tier_validation` compatibility with Odoo 18 CE; document status
- [ ] If compatible: install and configure tier validation on `account.move` (vendor bills above PHP 500,000 require approval)
- [ ] If not compatible: create `ipai_compliance_approval` module with simple state machine (draft > pending_approval > approved > posted)
- [ ] Configure approval tiers: Accountant prepares, Accounting Manager approves, Controller approves (above PHP 2M)
- [ ] Add `ipai_compliance_officer` security group with access to rate files and filing submissions
- [ ] Add `ipai_compliance_preparer` security group (can compute returns, cannot submit)
- [ ] Add `ipai_compliance_approver` security group (can review and mark as filed)
- [ ] Create `ir.rule` record rules: compliance preparer cannot approve own submissions
- [ ] Verify OCA `base_user_role` compatibility with Odoo 18 CE; configure roles if available
- [ ] Tests: user with preparer role cannot mark return as filed
- [ ] Tests: tier validation blocks posting of high-value bill without approval
- [ ] Tests: SoD enforced -- same user cannot prepare and approve same filing

### 1.9 Compliance Dashboard

- [ ] Create `ipai.compliance.dashboard` action window with kanban/list views
- [ ] Add dashboard cards: open filings count, missing 2307 count, upcoming deadlines (next 30 days), SLSP reconciliation status
- [ ] Add `ir.actions.act_window` shortcuts from dashboard cards to filtered lists
- [ ] Add aging analysis for missing 2307 records (0-15 days, 16-30 days, 30+ days)
- [ ] Add menu item: Accounting > Compliance > Dashboard
- [ ] Tests: dashboard counts match actual record counts

### 1.10 Document Extraction (Azure Document Intelligence)

- [ ] Design `ipai.document.extraction` model (source_file binary, extraction_result JSON, partner_id, move_id, state)
- [ ] Implement Azure Document Intelligence client using prebuilt invoice model (REST API call from server action)
- [ ] Extract fields: vendor name, TIN, invoice number, date, line items, amounts, tax amounts
- [ ] Map extracted fields to `account.move` draft creation
- [ ] Add confidence scoring: flag fields with <90% confidence for manual review
- [ ] Store API endpoint and key in `ir.config_parameter` (values from env vars, never hardcoded)
- [ ] Tests: extraction result correctly maps to vendor bill fields (mock API response)
- [ ] Tests: low-confidence fields flagged for review

### 1.11 Evidence and Audit Trail

- [ ] Add `mail.thread` and `mail.activity.mixin` on all `ipai.bir.*` models
- [ ] Configure `mail.tracking.value` on compliance-critical fields (state changes, amount overrides, ATC code changes)
- [ ] Implement evidence pack generator: for a given filing period, bundle all source transactions, 2307 PDFs, SLSP CSVs, approval records into a ZIP
- [ ] Add `Generate Evidence Pack` button on VAT return and EWT return forms
- [ ] Store evidence packs as `ir.attachment` with immutable flag
- [ ] Tests: state change on 2307 record creates tracking message
- [ ] Tests: evidence pack contains all expected artifacts for a given period

---

## Phase 2: Cross-Border + Avalara Integration

Target: International transactions, external tax engine, enhanced detection.
Timeline: 12-16 weeks after Phase 1. Modules: `ipai_tax_avalara` (new), `ipai_bir_einvoice` (new).

### 2.1 Avalara AvaTax Integration

- [ ] Create `ipai_tax_avalara` module scaffold
- [ ] Design `ipai.tax.avalara.config` model (api_url, company_code, sandbox_mode boolean) -- credentials from env vars via `ir.config_parameter`
- [ ] Implement AvaTax REST API client: `POST /api/v2/transactions/create` for tax calculation
- [ ] Override `account.tax._compute_amount()` to route non-PH transactions through Avalara
- [ ] Implement tax result caching: store Avalara response per `account.move` to avoid redundant API calls
- [ ] Add fiscal position rule: transactions with non-PH jurisdiction use Avalara engine
- [ ] PH transactions continue using local deterministic engine (no Avalara dependency)
- [ ] Handle Avalara API errors gracefully: queue for retry, do not block invoice posting
- [ ] Add Avalara transaction void/adjust for credit notes and cancellations
- [ ] Add Avalara health check server action (test connection + credentials)
- [ ] Tests: US multi-state transaction routed to Avalara, PH transaction uses local engine
- [ ] Tests: Avalara API timeout falls back to queued retry without blocking
- [ ] Tests: credit note triggers Avalara void for original transaction

### 2.2 Cross-Border Fiscal Positions

- [ ] Create fiscal position records for ASEAN countries: SG, ID, MY, TH, VN (zero-rated export + reverse charge)
- [ ] Create fiscal position records for major trade partners: US, EU (single position), JP, AU
- [ ] Create fiscal position rules: auto-detect by partner `country_id`
- [ ] Map tax treatments per fiscal position: domestic rate, zero-rated export, reverse charge, exempt
- [ ] Add non-resident foreign corp fiscal position with final WHT rates (15%-30% per `ph_rates_2025.json`)
- [ ] Tests: ASEAN partner auto-gets zero-rated export fiscal position
- [ ] Tests: non-resident service provider gets correct final WHT rate

### 2.3 Non-Resident WHT

- [ ] Extend `ph_rates_2025.json` with non-resident WHT rates (final WHT: 15% dividends, 20% interest, 25% royalties, etc.)
- [ ] Add final WHT `account.tax` records with correct ATC codes (F001-F005)
- [ ] Implement BIR Form 1601-F computation for non-resident WHT remittance
- [ ] Map fiscal position "Non-Resident Foreign Corp" to final WHT taxes
- [ ] Tests: vendor bill to non-resident foreign corp applies correct final WHT
- [ ] Tests: 1601-F computation aggregates non-resident WHT correctly

### 2.4 Multi-Currency Tax Handling

- [ ] Verify `account.tax._compute_amount()` handles multi-currency correctly (tax in transaction currency, converted to PHP for reporting)
- [ ] Add FX rate source configuration: BSP reference rate vs bank rate
- [ ] Implement FX gain/loss on tax amounts when payment date differs from invoice date
- [ ] Add currency conversion audit trail on tax computations
- [ ] Tests: USD invoice tax computed at invoice-date BSP rate
- [ ] Tests: FX gain/loss posted on WHT payment at different rate

### 2.5 Databricks Anomaly Detection Pipeline

- [ ] Create Databricks DLT notebook: JDBC extract from PostgreSQL (`account_move_line`, `account_tax`, `ipai_bir_2307`)
- [ ] Implement WHT leakage detection: vendor bills with qualifying product categories but no EWT applied
- [ ] Implement VAT input/output mismatch trend analysis: monthly I/O ratio deviation from historical baseline
- [ ] Implement VAT threshold monitoring: track cumulative revenue against PHP 3M threshold for non-VAT entities
- [ ] Schedule weekly DLT pipeline run via Databricks workflow
- [ ] Publish anomaly results back to Odoo via REST API (create `mail.activity` on flagged records)
- [ ] Tests: WHT leakage detection correctly flags service bill without EWT
- [ ] Tests: threshold monitor alerts when entity reaches 80% of PHP 3M

### 2.6 E-Invoicing Foundation (BIR CAS/EIS)

- [ ] Create `ipai_bir_einvoice` module scaffold
- [ ] Design `ipai.bir.einvoice` model (move_id, xml_content text, transmission_status, response_code, timestamp)
- [ ] Research current BIR EIS/CAS specification (document findings in `docs/knowledge-base/research/`)
- [ ] Implement invoice XML schema generation per BIR CAS requirements
- [ ] Add QR code generation on printed invoices (BIR requirement for CAS-permitted systems)
- [ ] Add CAS permit number configuration in `ir.config_parameter`
- [ ] Implement sequential invoice numbering enforcement (BIR requirement: no gaps)
- [ ] Tests: XML schema validates against BIR CAS XSD (when available)
- [ ] Tests: QR code contains required fields (TIN, invoice number, amount, date)
- [ ] Tests: sequential numbering rejects gap in invoice sequence

### 2.7 Evidence Archival (Azure Blob Storage)

- [ ] Create Azure Blob Storage container `bir-compliance-archive` with immutable retention policy (10 years)
- [ ] Implement archive server action: upload 2307 PDFs and SLSP CSVs to Blob Storage after filing
- [ ] Add `archive_url` and `archive_date` fields on `ipai.bir.2307` and `ipai.bir.slsp`
- [ ] Implement retrieval action: download archived document from Blob for re-printing
- [ ] Store Azure Blob connection string in `ir.config_parameter` (value from Key Vault env var)
- [ ] Tests: archive upload creates blob with correct path (year/month/form_type/filename)
- [ ] Tests: immutable retention prevents deletion of archived blob

### 2.8 Security Hardening

- [ ] Audit all `ir.model.access.csv` files across `ipai_bir_*` modules for least-privilege
- [ ] Add `ir.rule` domain rules: users see only their company's compliance records (multi-company)
- [ ] Add field-level access: `tax_withheld` and `tax_base` on 2307 are readonly after confirmation
- [ ] Implement rate file integrity check: SHA-256 hash of `ph_rates_2025.json` verified on module load
- [ ] Add `ir.logging` entries for all compliance-critical actions (rate changes, manual overrides, filing state changes)
- [ ] Verify no compliance data leaks via Odoo API (test with unprivileged user via JSON-RPC)
- [ ] Tests: unprivileged user cannot read 2307 records of other company
- [ ] Tests: rate file hash mismatch raises `UserError` on module load

---

## Phase 3: AI Agent Layer + Analytics

Target: AI advisory, predictive analytics, multi-entity, ASEAN expansion.
Timeline: 16-24 weeks after Phase 2. Services: Azure AI Foundry, Databricks ML.

### 3.1 AI Advisory Agent (Azure AI Foundry)

- [ ] Create `ipai_compliance_agent` module scaffold
- [ ] Design `ipai.compliance.agent.query` model (user_id, query_text, response_text, sources JSON, timestamp, confidence_score)
- [ ] Implement Azure AI Foundry agent client (REST API to Foundry endpoint)
- [ ] Build compliance knowledge index: ingest BIR Revenue Regulations, Revenue Memorandum Circulars, TRAIN Law, CREATE Law into Foundry search index
- [ ] Implement anomaly explanation: agent receives flagged transaction context, returns plain-language explanation of why it was flagged
- [ ] Implement policy Q&A: "What ATC code applies to consulting services?" answered from indexed regulations
- [ ] Add explicit "Not legal advice" framing on all agent responses
- [ ] Implement risk narrative generation for audit evidence packs
- [ ] Add Odoo widget: compliance chat panel on `account.move` form view (agent answers questions about that specific transaction)
- [ ] Store Foundry endpoint and key in `ir.config_parameter` (values from env vars)
- [ ] Tests: agent response includes source citations from indexed regulations
- [ ] Tests: agent refuses to provide definitive legal conclusions (returns advisory framing)
- [ ] Tests: anomaly explanation references specific rule and data that triggered the flag

### 3.2 Predictive Compliance Analytics

- [ ] Create Databricks ML notebook: predict monthly VAT payable from partial month data (by day 10)
- [ ] Train model on historical `account.move.line` data (12+ months required)
- [ ] Implement accuracy tracking: compare prediction to actual for each month
- [ ] Create Databricks notebook: predict quarterly EWT remittance from partial quarter data
- [ ] Publish predictions to Odoo compliance dashboard via REST API
- [ ] Add "Predicted VAT Payable" card on compliance dashboard with confidence interval
- [ ] Tests: prediction within 5% of actual for test dataset
- [ ] Tests: prediction updates daily as more transactions post

### 3.3 Regulatory Change Monitoring

- [ ] Implement BIR issuance monitor: Azure AI Foundry agent with web search capability checks BIR website for new RR/RMC
- [ ] Design `ipai.compliance.regulation.update` model (source_url, title, summary, impact_assessment, effective_date, status selection [new/reviewed/applied/dismissed])
- [ ] Create scheduled action: run monitor weekly, create records for new issuances
- [ ] Implement impact assessment: agent analyzes new issuance against current `ph_rates_2025.json` and flags affected rates/rules
- [ ] Add notification to compliance officer when new issuance detected
- [ ] Tests: monitor detects simulated new BIR issuance (mock response)
- [ ] Tests: impact assessment correctly identifies affected ATC codes

### 3.4 Multi-Entity Tax Consolidation

- [ ] Enable Odoo multi-company on all `ipai_bir_*` models (add `company_id` field with proper defaults)
- [ ] Implement consolidated VAT return: aggregate 2550M data across entities with intercompany elimination
- [ ] Implement consolidated EWT return: aggregate 1601-EQ across entities
- [ ] Add inter-company transaction identification and elimination rules
- [ ] Add consolidated compliance dashboard: one view across all entities
- [ ] Tests: consolidated return correctly sums individual entity returns
- [ ] Tests: intercompany transactions excluded from consolidated totals

### 3.5 OECD BEPS Pillar Two Monitoring

- [ ] Create Databricks notebook: compute effective tax rate (ETR) per jurisdiction from GL data
- [ ] Implement 15% minimum tax threshold alerting: flag jurisdictions with ETR below 15%
- [ ] Add country-by-country reporting data extraction (revenue, profit, tax paid, employees by jurisdiction)
- [ ] Publish BEPS dashboard to Power BI with jurisdiction ETR heat map
- [ ] Tests: ETR computation matches manual calculation for test data
- [ ] Tests: alert fires when test jurisdiction ETR drops below 15%

### 3.6 Transfer Pricing Documentation Support

- [ ] Implement TP documentation template generator: agent pre-fills intercompany transaction summary from Odoo data
- [ ] Add related-party transaction identification: flag transactions where both partners share parent company
- [ ] Generate arm's-length analysis data pack: comparable transaction prices, margin analysis
- [ ] Add advisory output: "Consider engaging TP consultant for [reason]" when transaction volume or risk exceeds threshold
- [ ] Tests: related-party flag correctly identifies intercompany transactions
- [ ] Tests: TP template includes all required transaction data fields

### 3.7 ASEAN Jurisdiction Packs

- [ ] Create `ipai_tax_sg` module scaffold: Singapore GST (9%), input tax credit, GST F5 return
- [ ] Create `ipai_tax_id` module scaffold: Indonesia PPN (11%), WHT (PPh 23), e-Faktur integration placeholder
- [ ] Create `ipai_tax_vn` module scaffold: Vietnam VAT (8%/10%), FCT on foreign contractors
- [ ] For each jurisdiction: load rates JSON, create fiscal positions, create tax records, create filing obligations
- [ ] Use Avalara for tax determination where supported; local engine for filing/forms
- [ ] Tests: each jurisdiction pack installs cleanly and creates correct tax configuration
- [ ] Tests: fiscal position auto-detection works for each ASEAN country

### 3.8 Compliance Control Tower

- [ ] Design unified dashboard: global compliance readiness across all jurisdictions
- [ ] Add KPI cards: filings on time %, exceptions resolved %, audit pack completeness %
- [ ] Add drill-down from KPI to specific filing, exception, or evidence gap
- [ ] Add SLA tracking: time to resolve compliance exceptions (target <5 business days)
- [ ] Implement jurisdiction risk heat map: color-coded by number of open exceptions
- [ ] Add Power BI embedded report for executive compliance summary
- [ ] Tests: KPI calculations match underlying record counts
- [ ] Tests: drill-down navigation reaches correct filtered record list

### 3.9 Documentation and Evidence

- [ ] Write `spec/agentic-global-compliance-cloud/plan.md` implementation plan
- [ ] Write `spec/agentic-global-compliance-cloud/constitution.md` non-negotiable constraints
- [ ] Document all model schemas in `docs/knowledge-base/research/agcc-data-model.md`
- [ ] Create test evidence bundle template: `docs/evidence/YYYYMMDD-HHMM/agcc/`
- [ ] Document Avalara integration architecture in `docs/architecture/avalara-integration.md`
- [ ] Document automation boundary matrix (fully automated / human-in-loop / advisory only) in spec bundle
- [ ] Add module README.md for each `ipai_bir_*` module with install and config instructions

---

## Dependency Map

```
Phase 1:
  ipai_bir_tax_compliance (enhance) -- no new deps
  ipai_bir_2307 -- depends on: l10n_ph, account, ipai_bir_tax_compliance
  ipai_bir_slsp -- depends on: account, ipai_bir_tax_compliance
  ipai_bir_returns -- depends on: ipai_bir_slsp, ipai_bir_2307
  OCA base_tier_validation -- verify 18.0 compat first
  OCA base_user_role -- verify 18.0 compat first
  OCA account_fiscal_position_autodetect -- verify 18.0 compat first

Phase 2:
  ipai_tax_avalara -- depends on: account, Avalara sandbox account
  ipai_bir_einvoice -- depends on: account, BIR CAS/EIS spec
  Azure Blob archival -- depends on: Azure subscription, Key Vault
  Databricks pipeline -- depends on: Databricks workspace, JDBC access

Phase 3:
  ipai_compliance_agent -- depends on: Azure AI Foundry, all Phase 1 modules
  Predictive analytics -- depends on: Databricks ML, 12+ months historical data
  ASEAN packs -- depends on: ipai_tax_avalara (Phase 2)
  BEPS monitoring -- depends on: multi-company, Databricks
```

---

*Source class: local (prd.md + ai-compliance-agent-design.md + SKILL.md)*
