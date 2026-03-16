---
title: "VAT Compliance Guide"
kb_scope: "bir-compliance"
group_ids: ["group-guid-placeholder"]
last_updated: "2026-03-15"
---

# VAT Compliance Guide

## Overview

This guide covers Value Added Tax (VAT) compliance for Philippine businesses using Odoo CE 19.0. It covers VAT registration, computation, filing of BIR Forms 2550M and 2550Q, and proper tax handling in the Odoo system.

**Legal Basis**: National Internal Revenue Code (NIRC), as amended by the TRAIN Law (RA 10963, effective January 1, 2018) and CREATE Law (RA 11534, effective April 11, 2021).

---

## VAT Registration

### Who Must Register for VAT

The following taxpayers are required to register for VAT:

1. **Mandatory VAT Registration**:
   - Any person or entity whose gross annual sales or receipts exceed PHP 3,000,000
   - Importers of goods
   - Persons registered as VAT taxpayers regardless of sales level

2. **Optional VAT Registration**:
   - Taxpayers with gross annual sales below PHP 3,000,000 may opt to register for VAT
   - Once registered, must remain VAT-registered for at least 3 years

### VAT Registration in Odoo

1. **Company Tax Configuration**
   - Navigate to Accounting > Configuration > Settings
   - Under "Taxes", set the default sales and purchase tax
   - Default Sales Tax: VAT 12% (Output)
   - Default Purchase Tax: VAT 12% (Input)

2. **Tax Account Mapping**
   - Output VAT account (liability): typically 211001
   - Input VAT account (asset): typically 114001
   - VAT Payable account (net): typically 211002

3. **Fiscal Positions**
   - Create fiscal positions to handle different tax treatments:
     - **Domestic Sale**: 12% VAT
     - **Export Sale**: 0% VAT (zero-rated)
     - **VAT-Exempt Sale**: No VAT
     - **Government Sale**: 12% VAT with 5% final withholding VAT

---

## VAT Rates

### Standard Rate

The standard VAT rate in the Philippines is **12%**, applied to:
- Sale of goods in the Philippines
- Sale of services performed in the Philippines
- Importation of goods

### Zero-Rated Sales (0%)

Zero-rated sales are VAT-taxable but at 0%. The seller can claim input VAT credits. Zero-rated transactions include:

1. **Export Sales**:
   - Direct export of goods
   - Sale of goods to PEZA/ecozones/freeport-registered enterprises
   - Foreign currency-denominated sales to non-resident buyers

2. **Services**:
   - Services rendered to persons or entities outside the Philippines
   - Processing, manufacturing, or repacking goods for export
   - Services by a resident to a non-resident when paid in foreign currency

3. **Other**:
   - Sale of power/fuel to PEZA enterprises
   - Transactions under international agreements (subject to conditions)

### VAT-Exempt Transactions

VAT-exempt transactions are not subject to VAT. The seller cannot claim input VAT credits on related purchases. Exempt transactions include:

1. **Agricultural products** in their original state (rice, corn, vegetables, fruits, fish, meat, eggs, milk)
2. **Educational services** by accredited schools
3. **Medical, dental, hospital, and veterinary services**
4. **Employment services** (salaries are not subject to VAT)
5. **Financial services** (lending, securities dealing — some exceptions)
6. **Sale or lease of residential dwelling** valued at PHP 3,199,200 or below
7. **Cooperatives** dealing exclusively with members
8. **Associations** non-stock, non-profit
9. **Government transactions** (some, subject to specific rules)
10. **Senior citizen and PWD discounts** (the discount portion is VAT-exempt)

---

## VAT Computation

### Output VAT

Output VAT is the tax collected on sales:

```
Output VAT = Selling Price (VAT-exclusive) x 12%
```

Or, if the price is VAT-inclusive:

```
VAT-exclusive Price = VAT-inclusive Price / 1.12
Output VAT = VAT-inclusive Price - VAT-exclusive Price
```

**Example:**
- Invoice amount (VAT-inclusive): PHP 112,000
- VAT-exclusive amount: PHP 112,000 / 1.12 = PHP 100,000
- Output VAT: PHP 12,000

### Input VAT

Input VAT is the tax paid on purchases:

```
Input VAT = Purchase Price (VAT-exclusive) x 12%
```

Input VAT can be claimed as a credit against Output VAT, provided:
1. The purchase is directly attributable to VAT-taxable sales
2. The purchase is supported by a valid VAT invoice or official receipt
3. The invoice/receipt contains the seller's TIN and the word "VAT"

### Net VAT Payable

```
Net VAT Payable = Output VAT - Input VAT
```

- If positive: remit to BIR
- If negative: carry forward as excess input VAT credit to the next period (or apply for refund in specific cases)

---

## Invoicing Requirements

### VAT Invoice Requirements

A valid VAT invoice must contain:

1. The word "INVOICE" prominently displayed
2. Seller's registered name, TIN, and address
3. Buyer's name, TIN, and address
4. Date of transaction
5. Quantity, unit of measure, and description of goods/services
6. Unit price (VAT-exclusive) and total amount
7. VAT amount separately shown
8. Total amount payable (VAT-inclusive)
9. BIR Permit to Print number (ATP)
10. Invoice serial number (pre-printed, sequential)

### Official Receipt Requirements

For services, an Official Receipt (OR) is issued instead of an invoice. It must contain the same information as above plus:
- The words "OFFICIAL RECEIPT" prominently displayed
- OR serial number

### Odoo Invoice Configuration

In Odoo, ensure invoices include all BIR-required fields:

1. **Company TIN**: Set in Settings > Companies > Company Information
2. **Customer TIN**: Set in the partner's record (Contacts > Partner > Accounting tab)
3. **Tax Display**: Set to "Tax-Included" or "Tax-Excluded" per company preference
4. **Sequence**: Configure invoice numbering to be sequential and without gaps (BIR requirement)
5. **Print Layout**: Customize the invoice report template to include all required BIR fields

---

## BIR Form 2550M — Monthly VAT Return

### Who Files

All VAT-registered taxpayers file 2550M for non-quarter-ending months:
- January, February (Q1)
- April, May (Q2)
- July, August (Q3)
- October, November (Q4)

Quarter-ending months (March, June, September, December) are covered by the quarterly return (2550Q).

### Filing Deadline

25th of the month following the taxable month. eFPS filers get a 5-day extension.

### Preparation in Odoo

1. **Run Tax Balance Report**
   - Navigate to Accounting > Reporting > Tax Balance
   - Set the period to the filing month
   - The report shows:
     - Output VAT: total VAT collected on sales
     - Input VAT: total VAT paid on purchases
     - Net VAT: payable or excess credit

2. **Extract Data for Form Fields**

   | 2550M Line | Odoo Source | Description |
   |-----------|-------------|-------------|
   | Line 12 | Output VAT total | Total Output VAT |
   | Line 15 | Input VAT total | Total Input VAT |
   | Line 16 | Carry-forward from prior period | Excess input VAT credit (if any) |
   | Line 20 | Computed | VAT Payable (Line 12 - Line 15 - Line 16) |
   | Line 23 | Computed | Total amount due (including penalties if late) |

3. **Review and Validate**
   - Cross-check output VAT against the sales journal
   - Cross-check input VAT against the purchase journal
   - Verify the carry-forward balance matches the prior period's excess credit

4. **File via eFPS or eBIRForms**
   - Enter the Odoo-generated figures into the BIR filing platform
   - Pay via authorized agent bank, GCash, or Maya (for small amounts)

---

## BIR Form 2550Q — Quarterly VAT Return

### Who Files

All VAT-registered taxpayers file 2550Q for each quarter.

### Filing Deadline

25th of the month following the quarter end. eFPS filers get a 5-day extension.

### Additional Data Required

The quarterly return includes more detail than the monthly return:

1. **Schedule of Sales**
   - Taxable sales (12%)
   - Zero-rated sales
   - Exempt sales
   - Sales to government (subject to 5% final withholding VAT)

2. **Schedule of Purchases**
   - Domestic purchases of goods
   - Domestic purchases of services
   - Importation of goods
   - Purchases not qualifying for input tax credit
   - Capital goods exceeding PHP 1,000,000 (amortized over 60 months)

3. **Summary of VAT Withheld by Government**
   - If you sell to government agencies, they withhold 5% final VAT
   - This amount is creditable against your output VAT

### Preparation in Odoo

1. Run the Tax Balance Report for the full quarter
2. Prepare the sales schedule by filtering invoices by tax type:
   - Filter: Tax = VAT 12% (for taxable sales)
   - Filter: Tax = VAT 0% (for zero-rated)
   - Filter: Tax = VAT Exempt (for exempt)
3. Prepare the purchase schedule similarly
4. Summarize by the categories required in Form 2550Q

---

## Input VAT Rules and Restrictions

### Claimable Input VAT

Input VAT is claimable if:
- The purchase is directly attributable to taxable sales
- Supported by a valid VAT invoice or OR with the seller's TIN
- Claimed in the period the invoice was issued (or within the next quarter)

### Non-Claimable Input VAT

Input VAT cannot be claimed on:
- Purchases from non-VAT registered suppliers (no VAT shown on invoice)
- Purchases for personal use (not business-related)
- Purchases for VAT-exempt activities (must be allocated)
- Entertainment, amusement, and recreation expenses exceeding the allowable limits
- Purchases without valid supporting documents

### Allocation of Input VAT (Mixed Transactions)

If a business has both VAT-taxable and VAT-exempt sales, input VAT must be allocated:

```
Claimable Input VAT = Total Input VAT x (Taxable Sales / Total Sales)
```

Non-claimable input VAT becomes an expense (cost of goods sold or operating expense).

### Capital Goods Rule

For capital goods (assets) with an aggregate acquisition cost exceeding PHP 1,000,000 in a 12-month period:
- Input VAT is amortized over 60 months (or the useful life, if shorter)
- Monthly claimable amount = Total Input VAT on capital goods / 60

---

## VAT on Government Sales

When selling to the Philippine government (national or local), a special rule applies:

1. The government withholds **5% final withholding VAT** on the gross payment
2. The remaining **7% VAT** is the seller's responsibility to remit
3. The seller receives BIR Form 2306 from the government agency
4. This 5% withheld amount is filed with Form 2550Q under the government sales section

**Odoo Configuration:**
- Create a fiscal position "Government Sale"
- Map the standard 12% VAT to a special "VAT Government 12% (5% withheld)" tax
- The tax computes 12% but records 5% as withholding and 7% as payable

---

## Record Keeping

### Retention Period

All VAT-related records must be retained for **10 years** from the date of the last entry:

- Sales invoices (issued and cancelled)
- Official receipts (issued and cancelled)
- Purchase invoices and receipts
- Import entries and customs documents
- Books of account (general journal, general ledger, subsidiary ledgers)
- VAT returns (2550M, 2550Q) with proof of filing and payment

### Books of Account

VAT-registered taxpayers must maintain:
1. General journal
2. General ledger
3. Sales journal (with VAT column)
4. Purchase journal (with VAT column)
5. Cash receipts journal
6. Cash disbursements journal

These are automatically maintained by Odoo through its journal entry system. Ensure the journal configuration properly separates VAT transactions.

---

## Common VAT Issues and Resolutions

| Issue | Resolution |
|-------|-----------|
| Vendor invoice missing VAT breakdown | Request a corrected invoice from the vendor; input VAT cannot be claimed without proper documentation |
| Excess input VAT accumulating | Carry forward to next period; apply for refund only for zero-rated sales (BIR Form 1914) |
| VAT on imported goods | Claim based on the Import Entry and Internal Revenue Declaration (IEIRD) |
| VAT on senior citizen/PWD discount | The 20% discount is VAT-exempt; remaining 80% is subject to VAT |
| Late filing of VAT return | 25% surcharge + 12% interest; file immediately and pay penalties |
| Wrong period for input VAT claim | Input VAT must be claimed within the quarter of issuance or the next quarter |
