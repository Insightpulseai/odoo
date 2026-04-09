# Skill Pack: Philippines Tax Compliance

> **Status**: Generated seed — partially validated 2026-04-07. Tax rates verified
> against `ipai_bir_tax_compliance/data/rates/ph_rates_2025.json`. Some referenced
> modules (ipai_bir_2307, ipai_bir_returns, ipai_bir_einvoice) describe **target
> state** and do not yet exist. BIR 2307 generation is available in core `l10n_ph`.
> Verify all tax rates against current BIR Revenue Regulations before production use.

## Scope

End-to-end Philippine tax compliance within Odoo 18 CE: VAT computation, expanded
withholding tax (EWT), BIR form generation, Summary List of Sales and Purchases
(SLSP), percentage tax for non-VAT entities, and e-invoicing/e-receipt (CAS/EIS).
Targets parity with SAP FICO localization for Philippines (TAXPH, WHT config).

---

## Concepts

| Concept | SAP Equivalent | Odoo 18 CE Surface |
|---------|---------------|---------------------|
| Output VAT (12%) | Tax Code (A1) | `account.tax` (sale, percent) |
| Input VAT (12%) | Tax Code (V1) | `account.tax` (purchase, percent) |
| Expanded WHT | WHT Type / Tax Code | `account.tax` (purchase, percent, WHT) |
| BIR 2307 (Certificate) | WHT Certificate | Core `l10n_ph` (basic) / planned `ipai_bir_2307` (enhanced) |
| BIR 2550M / 2550Q | VAT Return | Report over `account.move.line` |
| BIR 1601-EQ | Quarterly EWT Remittance | Report over WHT journal entries |
| SLSP | Sales/Purchase Register | Pivot on `account.move` + tax lines |
| Fiscal Position | Tax Jurisdiction | `account.fiscal.position` |
| e-Invoice (CAS) | E-Invoicing | Planned `ipai_bir_einvoice` + CAS integration |

---

## Must-Know Vocabulary

- **BIR**: Bureau of Internal Revenue (Philippine tax authority).
- **TIN**: Tax Identification Number. Format: XXX-XXX-XXX-XXX (12 digits, 3-3-3-3).
- **VAT**: Value Added Tax, standard rate 12%. Applied to sales of goods/services
  exceeding PHP 3,000,000 annual threshold.
- **EWT (Expanded Withholding Tax)**: Buyer withholds tax on behalf of seller.
  Rates: 1%, 2%, 5%, 10% depending on transaction type (ATC codes).
- **ATC (Alphanumeric Tax Code)**: BIR code identifying the tax type/rate
  (e.g., W157 = 1% EWT on purchases of goods, W158 = 2% on services).
- **BIR Form 2307**: Certificate of creditable tax withheld at source. Seller
  receives this to offset against their income tax.
- **SLSP**: Summary List of Sales/Purchases. Monthly attachment to VAT returns.
- **Percentage Tax**: 3% tax for non-VAT registered entities (below threshold).
- **CAS (Computerized Accounting System)**: BIR permit for electronic bookkeeping.
  Required for any ERP-generated official receipts/invoices.
- **TRAIN Law**: Tax Reform for Acceleration and Inclusion (RA 10963). Governs
  current rates and thresholds.

---

## Core Workflows

### 1. Tax Configuration

```
account.tax records needed:
  - "Output VAT 12%"    : type=sale,  amount=12, type_tax_use=sale
  - "Input VAT 12%"     : type=purchase, amount=12, type_tax_use=purchase
  - "EWT 1% Goods"      : type=purchase, amount=-1, type_tax_use=purchase
  - "EWT 2% Services"   : type=purchase, amount=-2, type_tax_use=purchase
  - "EWT 5% Rent"         : type=purchase, amount=-5, type_tax_use=purchase
  - "EWT 10% Professionals": type=purchase, amount=-10, type_tax_use=purchase
```

WHT taxes use negative amounts because they reduce the payable to the vendor.
The withheld amount posts to a WHT payable account (liability to BIR).

### 2. Vendor Bill with EWT

```
Vendor bill: PHP 100,000 (services)
  Line 1: Service expense          100,000
  Tax applied: Input VAT 12%       +12,000  (to Input VAT receivable)
  Tax applied: EWT 2% Services     -2,000   (to EWT Payable account)
  Amount due to vendor:            110,000   (112,000 - 2,000)
```

The PHP 2,000 is remitted to BIR via Form 1601-EQ. A BIR 2307 certificate is
issued to the vendor covering the PHP 2,000 withheld.

### 3. BIR 2307 Generation

Core `l10n_ph` provides basic BIR 2307 generation linked to `account.move`.
Planned `ipai_bir_2307` will enhance with auto-generation and PDF layout.

Target model fields: `partner_id` (vendor TIN), `period_start`, `period_end`,
`atc_code`, `tax_base`, `tax_withheld`, `move_id`.

Workflow: On vendor bill validation with WHT tax lines, auto-create 2307 record.
Print as PDF matching BIR layout. Vendor receives copy; agent retains file copy.

### 4. SLSP (Summary List of Sales and Purchases)

Monthly report required as attachment to BIR 2550M:
- **Sales**: All customer invoices with TIN, amount, VAT.
- **Purchases**: All vendor bills with TIN, amount, Input VAT, EWT.

Query: `account.move` where `move_type in ('out_invoice','out_refund')` grouped
by `partner_id.vat`, summing `amount_untaxed`, tax amounts by tax group.

Export format: CSV per BIR specification (pipe-delimited, specific column order).

### 5. VAT Return (BIR 2550M / 2550Q)

Computed fields:
- Box 1-14: Output VAT from sales tax lines
- Box 15-20: Input VAT from purchase tax lines
- Box 21: VAT Payable = Output VAT - Input VAT - prior excess credits
- Attach: SLSP files

### 6. Fiscal Position Mapping

```
account.fiscal.position records:
  - "VAT Registered (Domestic)"     : default, maps standard taxes
  - "Non-VAT (Below Threshold)"     : maps 12% VAT -> 3% Percentage Tax
  - "Zero-Rated (Export)"           : maps 12% VAT -> 0% VAT
  - "VAT Exempt"                    : maps 12% VAT -> exempt (no tax)
  - "Government Entity"             : maps EWT rates per gov't schedule
```

Fiscal positions auto-apply via `partner_id.property_account_position_id` or
country-based rules on `account.fiscal.position.rule`.

---

## Edge Cases

1. **Mixed VAT/Non-VAT in one bill**: Rare but legal. Use multiple invoice lines
   with different tax mappings. Validate that SLSP correctly splits amounts.
2. **Debit/credit notes**: Must reference original invoice. WHT on credit notes
   reverses the original 2307. Issue a replacement 2307 for the net amount.
3. **Foreign vendor (no TIN)**: Use fiscal position "Non-Resident Foreign Corp"
   with final WHT (up to 20% per `ph_rates_2025.json`; verify higher rates for
   specific transaction types against current BIR RR). No 2307 needed; use BIR
   Form 1601-F instead.
4. **Threshold crossing mid-year**: Entity crosses PHP 3M threshold and must
   register for VAT. Change fiscal position; prior transactions remain under
   percentage tax. Effective date management is critical.
5. **Advance payments**: WHT applies on payment, not on billing. If advance
   payment precedes the vendor bill, the 2307 date follows the payment date.

---

## Controls & Compliance

| Control | Implementation |
|---------|---------------|
| TIN validation | Regex constraint on `res.partner.vat`: `^\d{3}-\d{3}-\d{3}-\d{3}$` |
| Mandatory ATC on WHT | Required field on `account.tax` for WHT-type taxes |
| 2307 completeness check | Cron job: flag vendor bills with WHT lines but no 2307 record |
| SLSP reconciliation | Monthly: sum of SLSP must equal GL tax account balances |
| Filing deadline alerts | Automated activities: 2550M due 20th of following month |
| CAS audit trail | `ir.logging` + immutable journal entries (no draft reset after post) |

---

## Odoo/OCA Implementation Surfaces

| Module | Source | Status | Purpose |
|--------|--------|--------|---------|
| `account` | Core | Available | Journal entries, taxes, fiscal positions |
| `l10n_ph` | Core | Available | Philippine chart of accounts + basic BIR 2307 |
| `account_tax_python` | Core | Available | Python-computed taxes for complex WHT rules |
| `account_fiscal_position_autodetect` | OCA | Verify 18.0 | Auto-apply fiscal position by partner/country |
| `l10n_ph_ewt` | OCA | **Not on disk** | Expanded withholding tax (check OCA l10n-philippines repo) |
| `l10n_ph_bir_2307` | OCA | **Not on disk** | BIR 2307 certificate (check OCA l10n-philippines repo) |
| `l10n_ph_slsp` | OCA | **Not on disk** | SLSP report (check OCA l10n-philippines repo) |
| `ipai_bir_tax_compliance` | Custom | Available | Tax rates data (`ph_rates_2025.json`) |
| `ipai_bir_2307` | Custom | **Planned** | Enhanced 2307 with auto-generation and PDF layout |
| `ipai_bir_returns` | Custom | **Planned** | BIR 2550M/Q, 1601-EQ computation and export |
| `ipai_bir_einvoice` | Custom | **Planned** | CAS-compliant e-invoicing |

---

## Azure/Platform Considerations

- **Document Intelligence**: Extract vendor TIN, amounts, and tax lines from
  scanned vendor invoices (pre-built invoice model). Feed into vendor bill creation.
- **Databricks**: Quarterly tax analytics -- identify WHT leakage (bills missing
  EWT), VAT input/output mismatch trends, threshold monitoring.
- **Azure Blob Storage**: Archive BIR 2307 PDFs and SLSP CSVs with immutable
  retention policy (10-year BIR requirement).
- **Power BI**: Real-time tax liability dashboard: VAT payable, EWT payable by
  ATC, filing deadline countdown.

---

## Exercises

### Exercise 1: Basic EWT Setup
Configure `account.tax` for EWT 2% on services (ATC: W158). Create a vendor bill
for PHP 50,000 services. Apply Input VAT 12% and EWT 2%. Verify: vendor payable =
PHP 55,000 (56,000 - 1,000 WHT). Verify WHT payable account balance = PHP 1,000.

### Exercise 2: BIR 2307 Generation
Using the vendor bill from Exercise 1, generate a BIR 2307 certificate. Verify fields:
vendor TIN, ATC code, tax base (PHP 50,000), tax withheld (PHP 1,000), period.
Export as PDF. Verify layout matches BIR prescribed format.

### Exercise 3: SLSP Report
Create 5 customer invoices and 5 vendor bills for a given month with varying tax
treatments (VATable, zero-rated, exempt). Generate the SLSP. Verify: sales list
total matches `account.move.line` credit sum for output VAT account. Purchase list
total matches debit sum for input VAT account.

### Exercise 4: Fiscal Position Auto-Switch
Create a partner with fiscal position "Non-VAT". Create an invoice -- verify 3%
percentage tax applied. Change partner fiscal position to "VAT Registered". Create
new invoice -- verify 12% VAT applied. Confirm old invoices unchanged.

---

## Test Prompts for Agents

1. "Set up the full Philippine tax configuration for a VAT-registered trading company.
   Include output VAT, input VAT, and EWT rates for goods (1%), services (2%),
   rent (5%), and professionals (10%). Show the tax records created."

2. "We received a vendor bill from a professional consultant for PHP 200,000.
   Apply the correct taxes (VAT + EWT 10%). Generate the BIR 2307. What is the
   net amount payable to the vendor?"

3. "Generate the SLSP for March 2026. Export as BIR-compliant CSV. Cross-check
   totals against the GL balances for Output VAT and Input VAT accounts."

4. "Our annual revenue just crossed PHP 3,000,000. What tax configuration changes
   are needed? Migrate from percentage tax to VAT without affecting historical records."

5. "A government agency is our client. They will withhold 2% EWT on our invoice.
   How do we record the customer-side withholding and the 2307 we receive from them?"
