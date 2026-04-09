# PH/BIR Vendor Bills, AP, and Tax Return Test Plan

**Version**: 1.0
**Date**: 2026-04-09
**Scope**: Odoo 18 CE — Philippine BIR compliance for Accounts Payable, Vendor Bills, EWT, Form 2307, SAWT, 2550Q
**Status**: Production use
**Module dependency**: `l10n_ph` (OCA or `ipai_ph_bir`) + standard `account` module

---

## Table of Contents

1. Executive Summary
2. PH Tax Architecture in Odoo 18
3. Test Data Design
4. Scenario Matrix
   - A. Vendor Bill Entry and Master Data
   - B. EWT / Withholding Tax on Vendor Bills
   - C. VAT on Purchases (Input VAT / 2550Q)
   - D. AP Aging, Payment Terms, Partial Payments
   - E. Credit Notes and Reversals
   - F. Form 2307 Generation
   - G. SAWT Preparation
   - H. 2550Q VAT Return
   - I. Government Counterparties (BIR as Payee, GOCCs as Vendors)
   - J. Multi-Currency Vendor Bills with Withholding
   - K. Negative and Failure Scenarios
5. Compliance Matrix (Scenario → BIR Form)
6. High-Risk Regression Suite
7. Automation Strategy
8. Top-15 Production Failure Scenarios
9. Gaps and Assumptions

---

## 1. Executive Summary

Philippine BIR compliance on vendor bills involves three interlocked tax mechanics that Odoo 18 must handle correctly in combination:

**EWT (Expanded Withholding Tax)**: Computed on the gross amount of the vendor bill at the applicable ATC rate. The withheld amount reduces the cash paid to the vendor. It creates a liability to BIR (Withholding Tax Payable). Certifiable as BIR Form 2307.

**Input VAT**: 12% VAT charged by VAT-registered vendors is deductible against output VAT. Must be tracked per-vendor per-period for 2550Q filing. Zero-rated and VAT-exempt purchases must be segregated.

**SAWT (Summary Alphalist of Withholding Tax)**: Monthly/quarterly alphalist of all vendors from whom EWT was withheld. Must reconcile to 2307s issued.

Odoo 18 CE handles these via tax groups, withholding tax objects (if `ipai_ph_bir` or OCA `l10n_ph_withholding` is active), and standard tax reports. The primary risks are:

1. ATC code misconfiguration producing wrong EWT rates
2. EWT computed on VAT-inclusive instead of VAT-exclusive base
3. SAWT alphalist missing vendors due to payment-date vs. bill-date mismatch
4. 2550Q input VAT overclaimed due to bills posted in wrong period

---

## 2. PH Tax Architecture in Odoo 18

### ATC Code Taxonomy (key codes for vendor bills)

| ATC Code | Description | Rate | Base |
|----------|-------------|------|------|
| WV010 | Professional fees — individual | 10% | Gross |
| WV011 | Professional fees — corporate | 15% | Gross |
| WC150 | Services rendered by juridical | 2% | Gross |
| WC160 | Rentals — personal property | 5% | Gross |
| WC161 | Rentals — real property | 5% | Gross |
| WC200 | Contractors and subcontractors | 2% | Gross |
| WI020 | Purchases — goods (non-VAT) | 1% | Gross |
| WI030 | Purchases — goods (VAT reg) | 1% | Gross |
| WF090 | Fringe benefits | 35% | Grossed-up |
| EWT-GOV | Government contractors (special) | 2% | Gross |

### VAT Codes (vendor side)

| Code | Description | Rate |
|------|-------------|------|
| VAT-IN-12 | Standard input VAT | 12% |
| VAT-IN-0 | Zero-rated input VAT | 0% |
| VAT-EXEMPT | Exempt from VAT | N/A |
| VAT-IN-12-IMPORT | Input VAT on importation | 12% |

### EWT Computation Rule

```
EWT Amount = Gross Amount (VAT-exclusive) × ATC Rate
Net Payment = Gross Amount + VAT Amount − EWT Amount
```

---

## 3. Test Data Design

### 3.1 Vendor Master Records

| Vendor ID | Name | Type | VAT Reg | TIN | ATC | Currency |
|-----------|------|------|---------|-----|-----|----------|
| V-001 | Dela Cruz Law Office | Individual | N | 123-456-789-000 | WV010 | PHP |
| V-002 | Santos & Associates Corp | Corporate | Y | 234-567-890-000 | WV011 | PHP |
| V-003 | Metro IT Solutions Inc | Corporate | Y | 345-678-901-000 | WC150 | PHP |
| V-004 | Realty Leasing Corp | Corporate | Y | 456-789-012-000 | WC161 | PHP |
| V-005 | BuildRight Contractors | Corporate | Y | 567-890-123-000 | WC200 | PHP |
| V-006 | Office Supplies Depot | Corporate | Y | 678-901-234-000 | WI030 | PHP |
| V-007 | Global Tech Inc | Corporate | Y | 789-012-345-000 | WC150 | USD |
| V-008 | BIR — Internal Revenue | Government | N | 000-000-000-000 | N/A | PHP |
| V-009 | DOH Procurement | GOCC | N | 000-111-222-000 | EWT-GOV | PHP |
| V-010 | Non-VAT Freelancer | Individual | N | 890-123-456-000 | WV010 | PHP |

### 3.2 Tax Code Configuration

| Tax ID | Type | Amount | Account DR | Account CR | Applies to |
|--------|------|--------|-----------|-----------|------------|
| T-VAT-IN | percent | 12% | 1140 Input VAT | — | Vendor lines |
| T-EWT-WV010 | percent | -10% | — | 2120 EWT Payable | Bill total |
| T-EWT-WV011 | percent | -15% | — | 2120 EWT Payable | Bill total |
| T-EWT-WC150 | percent | -2% | — | 2120 EWT Payable | Bill total |
| T-EWT-WC161 | percent | -5% | — | 2120 EWT Payable | Bill total |
| T-EWT-WC200 | percent | -2% | — | 2120 EWT Payable | Bill total |
| T-EWT-WI030 | percent | -1% | — | 2120 EWT Payable | Bill total |
| T-EWT-GOV | percent | -2% | — | 2120 EWT Payable | Bill total |

### 3.3 Payment Terms

| ID | Name | Structure |
|----|------|-----------|
| PT-IMM | Immediate | 100% on bill date |
| PT-30 | Net 30 | 100% in 30 days |
| PT-60 | Net 60 | 100% in 60 days |
| PT-INST | 3-installment | 33.33% / 30d / 60d |
| PT-GOV | Government terms | 15 days after COA release |

### 3.4 Journals

| Journal | Type | Currency | Account |
|---------|------|----------|---------|
| APPHP | purchase | PHP | 2100 AP — Trade |
| APUSD | purchase | USD | 2101 AP — Foreign |
| EWTP | general | PHP | 2120 EWT Payable |
| BANKPHP | bank | PHP | 1010 Cash — PHP |
| BANKUSD | bank | USD | 1011 Cash — USD |

---

## 4. Scenario Matrix

### A. Vendor Bill Entry and Master Data

| ID | Description | Priority | Auto? |
|----|-------------|----------|-------|
| AP-A-001 | Create vendor bill for VAT-registered corporate vendor, standard 12% VAT, no withholding | P1 | Yes |
| AP-A-002 | Create vendor bill for VAT-registered vendor with EWT (WC150 2%) — verify VAT base excludes EWT | P1 | Yes |
| AP-A-003 | Create vendor bill for non-VAT individual professional (WV010 10%) | P1 | Yes |
| AP-A-004 | Create vendor bill with both input VAT and EWT — verify journal entry has 4 lines | P1 | Yes |
| AP-A-005 | Create vendor bill with multiple product lines, different ATC codes per line | P2 | Yes |
| AP-A-006 | Create vendor bill for VAT-exempt purchase (medical, agriculture) | P2 | Yes |
| AP-A-007 | Create vendor bill for zero-rated purchase (export-related services) | P2 | Yes |
| AP-A-008 | Validate TIN format enforcement on vendor partner (999-999-999-999) | P2 | No |
| AP-A-009 | Create vendor bill with non-standard ATC requiring manual override | P3 | No |
| AP-A-010 | Verify fiscal position auto-assignment based on vendor TIN / address (PH domestic vs foreign) | P2 | Yes |

**Expected journal entry for AP-A-004 (e.g., PHP 100,000 professional fees + 12% VAT, 15% EWT on gross):**
```
DR  Expense Account        100,000.00
DR  Input VAT (1140)        12,000.00
    CR  EWT Payable (2120)   15,000.00  (15% × 100,000)
    CR  AP — Trade (2100)    97,000.00  (112,000 − 15,000)
```

### B. EWT / Withholding Tax on Vendor Bills

| ID | Description | Priority | Auto? |
|----|-------------|----------|-------|
| AP-B-001 | EWT computed on VAT-exclusive base (not on gross+VAT total) | P1 | Yes |
| AP-B-002 | EWT at WV010 (10%) — individual professional, non-VAT | P1 | Yes |
| AP-B-003 | EWT at WV011 (15%) — corporate professional, VAT-registered | P1 | Yes |
| AP-B-004 | EWT at WC150 (2%) — juridical service provider | P1 | Yes |
| AP-B-005 | EWT at WC161 (5%) — real property rental | P1 | Yes |
| AP-B-006 | EWT at WC200 (2%) — contractor | P1 | Yes |
| AP-B-007 | EWT at WI030 (1%) — goods purchase from VAT-registered seller | P1 | Yes |
| AP-B-008 | EWT on mixed bill: professional fee + goods — separate ATC per line | P2 | Yes |
| AP-B-009 | Fringe benefit tax (WF090 35%) — grossed-up computation | P2 | No |
| AP-B-010 | EWT not applied when vendor is below threshold (< PHP 10,000 cumulative) | P2 | No |
| AP-B-011 | Verify EWT Payable account carries balance until BIR remittance payment | P1 | Yes |
| AP-B-012 | Manually adjust EWT amount on posted bill — confirm re-posting workflow | P2 | No |

### C. VAT on Purchases (Input VAT / 2550Q)

| ID | Description | Priority | Auto? |
|----|-------------|----------|-------|
| AP-C-001 | Input VAT posted to correct account on bill posting | P1 | Yes |
| AP-C-002 | Input VAT report shows correct total for period (pre-2550Q reconciliation) | P1 | Yes |
| AP-C-003 | VAT-exempt purchase does not create input VAT entry | P1 | Yes |
| AP-C-004 | Zero-rated purchase creates zero-amount VAT line but appears in 2550Q section | P2 | Yes |
| AP-C-005 | Input VAT on importation (with BIR import entry document reference) | P2 | No |
| AP-C-006 | Proportionate input VAT claim (mixed taxable and exempt activities) | P3 | No |
| AP-C-007 | Input VAT reversal on credit note — negative entry in same period | P1 | Yes |
| AP-C-008 | Late-filed bill: input VAT claimed in month of posting, not invoice date | P2 | No |
| AP-C-009 | 2550Q quarter aggregation: 3 monthly periods summed correctly | P1 | Yes |
| AP-C-010 | Input VAT carryover from prior quarter appears in current 2550Q | P2 | Yes |

### D. AP Aging, Payment Terms, Partial Payments

| ID | Description | Priority | Auto? |
|----|-------------|----------|-------|
| AP-D-001 | AP aging report shows open bills by bucket (current, 1-30, 31-60, 61-90, >90) | P1 | Yes |
| AP-D-002 | Payment term Net 30 creates correct due date on bill | P1 | Yes |
| AP-D-003 | 3-installment payment term creates 3 move lines with distinct due dates | P1 | Yes |
| AP-D-004 | Partial payment reduces open balance without closing bill | P1 | Yes |
| AP-D-005 | Partial payment on bill with EWT — net payment = AP balance minus prior EWT | P1 | Yes |
| AP-D-006 | Two partial payments fully reconcile bill (sum = AP balance) | P1 | Yes |
| AP-D-007 | AP aging excludes fully paid/reconciled bills | P1 | Yes |
| AP-D-008 | Government payment term (15d after COA approval) creates correct due date | P2 | No |
| AP-D-009 | Overdue bills appear correctly in aging after period close | P2 | Yes |
| AP-D-010 | AP aging by vendor group (trade vs GOCC vs government) | P2 | Yes |
| AP-D-011 | Installment bill: partial payment on first installment only — aging reflects balance | P2 | Yes |
| AP-D-012 | Payment with early settlement discount — verify discount account posting | P3 | No |

### E. Credit Notes and Reversals

| ID | Description | Priority | Auto? |
|----|-------------|----------|-------|
| AP-E-001 | Create credit note for full vendor bill — AP balance zeroed | P1 | Yes |
| AP-E-002 | Create partial credit note — open balance = original − credit note | P1 | Yes |
| AP-E-003 | Credit note reverses input VAT in same period | P1 | Yes |
| AP-E-004 | Credit note reverses EWT — EWT Payable account reduced | P1 | Yes |
| AP-E-005 | Credit note applied against different vendor bill (set-off) | P2 | Yes |
| AP-E-006 | Reverse posted vendor bill via standard reversal — locked period check | P2 | Yes |
| AP-E-007 | Credit note in prior period — verify fiscal lock prevents back-dated posting | P1 | Yes |
| AP-E-008 | Credit note with EWT: 2307 issued must reflect net transaction | P2 | No |
| AP-E-009 | Partial credit note on multi-line bill — line-level allocation | P2 | Yes |

### F. Form 2307 Generation

| ID | Description | Priority | Auto? |
|----|-------------|----------|-------|
| AP-F-001 | Generate 2307 for single vendor, single quarter — correct amounts | P1 | No |
| AP-F-002 | Generate 2307 for vendor with multiple bills in quarter — aggregated per ATC | P1 | No |
| AP-F-003 | 2307 shows vendor TIN, name, address, ATC code, gross income, EWT amount | P1 | No |
| AP-F-004 | 2307 not generated for zero-EWT vendors (VAT-exempt, goods below threshold) | P2 | No |
| AP-F-005 | 2307 amounts reconcile with EWT Payable ledger for period | P1 | No |
| AP-F-006 | 2307 re-generated after credit note — corrected net amount | P2 | No |
| AP-F-007 | Bulk 2307 generation for all vendors in a quarter — no duplicates | P2 | No |
| AP-F-008 | 2307 date range: January 1 – March 31 for Q1, correct period label | P1 | No |
| AP-F-009 | 2307 printed output matches BIR-prescribed layout (column alignment) | P3 | No |

### G. SAWT Preparation

| ID | Description | Priority | Auto? |
|----|-------------|----------|-------|
| AP-G-001 | SAWT alphalist includes all vendors with EWT in the period | P1 | No |
| AP-G-002 | SAWT total EWT per ATC ties to EWT Payable account movement | P1 | No |
| AP-G-003 | SAWT excludes vendors with no withholding in the period | P1 | No |
| AP-G-004 | SAWT shows TIN, vendor name, gross income, ATC, EWT per vendor | P1 | No |
| AP-G-005 | SAWT credit note adjustment: vendor with credit note shows reduced gross | P2 | No |
| AP-G-006 | SAWT export to BIR DAT format (tab-delimited, BIR-specified columns) | P2 | No |
| AP-G-007 | SAWT reconciliation: sum of all 2307s = SAWT total | P1 | No |
| AP-G-008 | SAWT for mixed-currency vendors — PHP equivalent at BSP rate | P2 | No |
| AP-G-009 | Monthly SAWT vs quarterly SAWT — correct period grouping | P2 | No |

### H. 2550Q VAT Return

| ID | Description | Priority | Auto? |
|----|-------------|----------|-------|
| AP-H-001 | 2550Q shows total taxable purchases (Box 20A) matching AP ledger | P1 | Yes |
| AP-H-002 | 2550Q shows total input VAT (Box 20B) matching Input VAT account | P1 | Yes |
| AP-H-003 | 2550Q zero-rated purchases appear in correct box (Box 20C) | P2 | Yes |
| AP-H-004 | 2550Q exempt purchases in Box 20D — not included in input VAT claim | P2 | Yes |
| AP-H-005 | 2550Q prior quarter carryover input VAT correctly carried forward | P2 | Yes |
| AP-H-006 | 2550Q payable/creditable amount computed: Output VAT − Input VAT | P1 | Yes |
| AP-H-007 | 2550Q period lock: bills posted after quarter-end excluded from return | P1 | Yes |
| AP-H-008 | 2550Q adjustment for input VAT on capital goods (amortization over 60 months) | P3 | No |
| AP-H-009 | 2550Q with transitional input VAT (beginning inventory) | P3 | No |

### I. Government Counterparties

| ID | Description | Priority | Auto? |
|----|-------------|----------|-------|
| AP-I-001 | Government agency as vendor — EWT at 2% (EWT-GOV) on all payments | P1 | Yes |
| AP-I-002 | BIR as payee for EWT remittance — bill created against BIR vendor | P1 | No |
| AP-I-003 | BIR remittance bill: debit EWT Payable, credit AP/Bank — correct flow | P1 | Yes |
| AP-I-004 | GOCC vendor with PhilGEPS reference number on vendor bill | P2 | No |
| AP-I-005 | Government vendor: VAT treatment — most GOCCs are non-VAT | P2 | Yes |
| AP-I-006 | BIR Form 1601-EQ (quarterly EWT return) amount ties to SAWT total | P1 | No |
| AP-I-007 | Final withholding tax on dividends paid to non-resident — 25% FWT | P3 | No |
| AP-I-008 | Government vendor payment: COA-required approval workflow simulation | P2 | No |

### J. Multi-Currency Vendor Bills with Withholding

| ID | Description | Priority | Auto? |
|----|-------------|----------|-------|
| AP-J-001 | USD vendor bill: EWT computed on PHP equivalent at BSP rate on bill date | P1 | Yes |
| AP-J-002 | USD vendor bill paid at different rate — forex gain/loss posted correctly | P1 | Yes |
| AP-J-003 | EWT on foreign vendor bill — PHP withholding against USD-denominated AP | P1 | Yes |
| AP-J-004 | SAWT includes foreign-currency vendor in PHP equivalent | P2 | No |
| AP-J-005 | 2307 for foreign vendor shows PHP equivalent of gross income | P2 | No |
| AP-J-006 | Multi-currency AP aging shows both original currency and PHP equivalent | P2 | Yes |
| AP-J-007 | Currency revaluation of USD AP — unrealized forex posted, not EWT-impacted | P2 | Yes |
| AP-J-008 | Partial payment on foreign bill — EWT applied once at bill posting, not per payment | P1 | Yes |

### K. Negative and Failure Scenarios

| ID | Description | Priority | Auto? |
|----|-------------|----------|-------|
| AP-K-001 | Post vendor bill with no ATC code assigned — system must warn or block | P1 | No |
| AP-K-002 | EWT rate mismatch: ATC code on bill differs from vendor master — alert | P2 | No |
| AP-K-003 | Post bill in locked fiscal period — must be blocked | P1 | Yes |
| AP-K-004 | Duplicate vendor bill (same number, same vendor) — duplicate detection | P1 | Yes |
| AP-K-005 | Vendor TIN missing on bill — 2307 generation must fail with clear error | P1 | No |
| AP-K-006 | EWT Payable account balance mismatch vs SAWT total — reconciliation alert | P1 | No |
| AP-K-007 | Zero-amount EWT due to threshold — verify bill still posts correctly | P2 | Yes |
| AP-K-008 | Vendor bill with VAT but vendor marked as non-VAT in master — warning | P2 | No |
| AP-K-009 | Payment reconciled against wrong bill — unreconcile and reapply | P2 | No |
| AP-K-010 | 2307 generated with wrong quarter date range — boundary date validation | P2 | No |

---

## 5. Compliance Matrix (Scenario → BIR Form)

| BIR Form | Description | Scenarios Covered |
|----------|-------------|-------------------|
| Form 2307 | Certificate of Creditable Tax Withheld at Source | AP-B-001–012, AP-F-001–009, AP-J-004–005 |
| SAWT | Summary Alphalist of Withholding Tax at Source | AP-G-001–009, AP-B-011, AP-J-004 |
| BIR Form 1601-EQ | Quarterly Remittance Return of EWT | AP-I-002–003, AP-I-006, AP-G-007 |
| BIR Form 2550Q | Quarterly VAT Return | AP-C-009–010, AP-H-001–009 |
| BIR Form 2550M | Monthly VAT Return | AP-C-001–008 |
| BIR Form 1604-E | Annual Information Return of EWT | AP-F-007, AP-G-002 |
| ORB (Official Receipts) | Vendor ORs attached to bills | AP-A-001–004, AP-K-004 |

---

## 6. High-Risk Regression Suite

The following 20 scenarios form the minimum regression gate before any production deployment touching AP, EWT, or tax configuration:

**Tier 1 — Run on every deployment:**
- AP-A-002, AP-A-004 (EWT + VAT combined entry)
- AP-B-001 (EWT base = VAT-exclusive amount)
- AP-B-003, AP-B-004 (rate correctness by ATC)
- AP-B-011 (EWT Payable carries balance)
- AP-C-001, AP-C-003 (input VAT posting, VAT-exempt)
- AP-D-001, AP-D-004 (AP aging, partial payment)
- AP-E-001, AP-E-004 (credit note reverses EWT)
- AP-F-001, AP-F-005 (2307 amounts and reconciliation)
- AP-G-002, AP-G-007 (SAWT ties to ledger and to 2307s)
- AP-H-001, AP-H-002 (2550Q input VAT totals)
- AP-I-003 (BIR remittance flow)
- AP-J-001, AP-J-008 (multi-currency EWT)
- AP-K-003, AP-K-004 (locked period, duplicate detection)

---

## 7. Automation Strategy

### Automatable (Odoo test framework / Python unit tests)

Scenarios marked `Auto? = Yes` in the matrix above. These use:
- `account.move` create/post/validate flows
- Tax computation assertions on journal entry lines
- AP aging report data assertions via `account.aged.payable`
- Reconciliation engine assertions

**Test module**: `addons/ipai/ipai_ph_bir/tests/`

```python
# Example pattern for AP-B-001
def test_ewt_computed_on_vat_exclusive_base(self):
    bill = self.env['account.move'].create({
        'move_type': 'in_invoice',
        'partner_id': self.vendor_corporate.id,
        'invoice_line_ids': [(0, 0, {
            'name': 'IT Services',
            'quantity': 1,
            'price_unit': 100000,
            'tax_ids': [(6, 0, [self.tax_vat_in.id, self.tax_ewt_wc150.id])],
        })],
    })
    bill.action_post()
    ewt_line = bill.line_ids.filtered(
        lambda l: l.account_id.code == '2120'
    )
    # 2% × 100,000 = 2,000 (not 2% × 112,000)
    self.assertAlmostEqual(abs(ewt_line.balance), 2000.0, places=2)
```

### Manual Only

Scenarios marked `Auto? = No`:
- 2307 PDF layout and BIR-prescribed column alignment
- SAWT DAT file export format validation (requires BIR-side verification)
- ATC code override and warning behavior (UI-dependent)
- Government approval workflow simulation
- Cross-period credit note on BIR 2307 correction

### Semi-Automated (data setup automated, assertion manual)

- AP-F-007 (bulk 2307 generation): automate data creation, manually verify output
- AP-G-006 (SAWT DAT format): automate data, manually compare to BIR template
- AP-H-008 (capital goods VAT amortization): automate journal entries, verify schedule manually

---

## 8. Top-15 Production Failure Scenarios

Ranked by probability × impact based on PH BIR audit exposure and Odoo deployment patterns:

| Rank | Scenario | Root Cause | BIR Risk |
|------|----------|------------|----------|
| 1 | EWT computed on VAT-inclusive total (AP-B-001) | Tax sequence misconfiguration — EWT tax must be marked `price_include=False` and computed before VAT round | Overpayment to vendor, underpayment to BIR |
| 2 | SAWT total does not tie to EWT Payable ledger (AP-G-002) | Bills posted and partially paid across periods; report uses payment date vs. posting date | BIR alphalist rejection, 2307 disallowed |
| 3 | 2307 not generated for vendor due to missing TIN (AP-K-005) | Vendor master incomplete at go-live data migration | Criminal liability — failure to issue 2307 |
| 4 | Input VAT overclaimed on 2550Q — VAT-exempt items included (AP-C-003) | Tax code misconfiguration: exempt items mapped to VAT-IN-12 fiscal position | BIR deficiency assessment |
| 5 | Partial payment creates incorrect AP residual — EWT deducted twice (AP-D-005) | EWT posted at bill level; payment auto-deducts again if reconciliation logic double-counts | Vendor dispute, GL imbalance |
| 6 | Multi-currency EWT in USD instead of PHP (AP-J-001) | Currency not forced to PHP on EWT tax lines | BIR 2307 in wrong currency, rejected |
| 7 | Credit note EWT reversal missing from SAWT (AP-E-04) | Credit note posts EWT debit but SAWT report uses only debit-side filter | Overstated SAWT, 2307 amount mismatch |
| 8 | Installment payment term rounding leaves PHP 0.01 residual (AP-D-003) | 33.33% × 3 = 99.99% due to floor rounding | Open AP item, aging report noise |
| 9 | Locked period bypass via back-dated bill entry (AP-K-003) | Finance user has lock period override permission; permission not revoked at go-live | BIR audit trail violation |
| 10 | Duplicate vendor bill posted (AP-K-004) | Vendor sends duplicate OR; no BIR OR number uniqueness check configured | Duplicate input VAT claim |
| 11 | ATC code not mapped for new vendor type — bill posts with zero EWT (AP-K-001) | Missing ATC default on vendor fiscal position | EWT under-remittance; BIR surcharge |
| 12 | 2550Q prior-quarter carryover not carried forward (AP-C-010) | Period close without proper carry-forward — input VAT balance account not cleared | Double-paying VAT liability |
| 13 | Foreign vendor TIN format rejected by SAWT (AP-G-008) | BIR SAWT requires Philippine TIN; foreign TINs not handled | SAWT file rejected on submission |
| 14 | BIR remittance bill reconciled against wrong EWT Payable account (AP-I-003) | Multiple EWT accounts per ATC code; remittance hits catch-all account | Reconciliation gap; auditor finding |
| 15 | Government vendor bill EWT at wrong rate (2% vs. 10%) (AP-I-001) | Government contractor rate not configured in fiscal position; defaults to professional fee rate | BIR deficiency — rate difference |

---

## 9. Gaps and Assumptions

### Assumptions

1. `l10n_ph` or `ipai_ph_bir` module is installed and ATC codes are pre-seeded as tax objects in Odoo.
2. EWT taxes are configured with `type_tax_use = purchase`, negative amounts, and the EWT Payable account (2120) as the tax account.
3. BSP exchange rates are updated daily in Odoo's currency rate table for multi-currency EWT PHP conversion.
4. The `account_withholding_tax` OCA module (if used) does not conflict with `l10n_ph` tax group ordering.
5. Vendor TINs are mandatory fields enforced at vendor creation time (not at bill time).
6. Fiscal year aligns to calendar year (January–December) per standard PH BIR requirement.
7. The 2307 and SAWT outputs are generated via Odoo QWeb reports or a custom `ipai_ph_bir` wizard; PDF layout verification is out of scope for automated tests.

### Known Gaps

| Gap | Impact | Mitigation |
|-----|--------|------------|
| No native BIR DAT file exporter in Odoo 18 CE | SAWT submission requires manual reformatting | `ipai_ph_bir` must provide DAT export; manual QA required |
| EWT threshold enforcement (< PHP 10,000) not in standard l10n_ph | Under-threshold vendors may incorrectly have EWT applied | Manual vendor-level override + test AP-B-010 |
| Capital goods input VAT amortization (60-month rule) not automated | 2550Q Box adjustment manual | Deferred to ipai_ph_bir v2 |
| BIR eFPS / eBIRForms electronic submission API | Manual filing still required | Out of scope; covered by separate integration spec |
| Government PhilGEPS integration for PO/bill matching | GOCC vendor bills may lack PO reference validation | Manual process; no Odoo-side automation |
| Form 1604-E (annual EWT information return) generation | Year-end manual compilation from SAWT | Deferred; manual process acceptable for Year 1 |

---

*Last updated: 2026-04-09 | Owner: QA / Finance Functional | Related modules: `l10n_ph`, `ipai_ph_bir`, `account`*
