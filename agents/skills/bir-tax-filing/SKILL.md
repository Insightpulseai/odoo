---
name: bir-tax-filing
description: Guides BIR tax return preparation and filing for Philippine compliance
version: 1.0.0
author: InsightPulse AI
tags: [tax, bir, compliance, philippines, withholding]
---

# BIR Tax Filing Skill

## Overview

This skill provides comprehensive guidance for Bureau of Internal Revenue (BIR) tax compliance, including preparation, validation, and filing of various tax returns required for Philippine businesses.

## Supported Forms

| Form | Name | Frequency |
|------|------|-----------|
| 1601-C | Monthly Withholding Tax on Compensation | Monthly |
| 1601-E | Monthly Expanded Withholding Tax | Monthly |
| 2550M | Monthly VAT Declaration | Monthly |
| 2550Q | Quarterly VAT Return | Quarterly |
| 1601-Q | Quarterly Income Tax | Quarterly |
| 1702 | Annual Income Tax Return | Annual |
| 1604-CF | Annual Alphalist (Compensation) | Annual |
| 2307 | Certificate of Creditable Tax Withheld | As needed |

## Workflow by Form Type

### Form 1601-C (Monthly Withholding - Compensation)

**Deadline**: 10th of following month

**Data Sources**:
```
Odoo hr.payslip → Compute withholding tax
Fields: employee_id, date_from, date_to, net_wage, tax_withheld
```

**Preparation Steps**:
1. Export payroll data for the period
2. Summarize by tax bracket
3. Reconcile to payroll register
4. Generate BIR format data
5. Review and validate

**Validation Checks**:
```python
validations = [
    ("Total employees matches payroll", lambda x: x.employee_count == payroll.count),
    ("Tax withheld > 0", lambda x: x.total_tax > 0),
    ("Dates within period", lambda x: x.date_range_valid),
    ("TIN format valid", lambda x: re.match(r'\d{3}-\d{3}-\d{3}-\d{3}', x.tin)),
]
```

### Form 1601-E (Monthly Expanded Withholding Tax)

**Deadline**: 10th of following month

**Data Sources**:
```
Odoo account.move → Vendor invoices with EWT
Filter: tax_ids contains EWT tax codes
```

**EWT Rate Reference**:
| Payment Type | Rate |
|--------------|------|
| Professional fees (individuals) | 10% |
| Professional fees (corporations) | 15% |
| Rent | 5% |
| Contractors | 2% |

**Preparation Steps**:
1. Query vendor invoices with EWT taxes
2. Group by tax rate / ATC code
3. Generate payee listing (Alphalist)
4. Summarize totals
5. Validate against GL

### Form 2550Q (Quarterly VAT Return)

**Deadline**: 25th of month following quarter end

**Data Sources**:
```
Odoo account.move →
  Output VAT: move_type='out_invoice', tax like '%VAT%'
  Input VAT: move_type='in_invoice', tax like '%VAT%'
```

**VAT Computation**:
```
Output VAT = Sum of VAT on sales
Input VAT = Sum of VAT on purchases (claimable)
VAT Payable = Output VAT - Input VAT
```

**Validation**:
- Output VAT ties to sales register
- Input VAT ties to purchase register
- VAT creditable percentage applied correctly
- Zero-rated sales documented

## Automation Support

### n8n Workflow: BIR Deadline Reminder

The `bir_deadline_reminder.json` workflow:
- Runs daily at 8 AM
- Calculates upcoming deadlines
- Posts to #bir-alerts channel
- Tags urgent items (< 3 days)

### Data Export Query

```sql
-- EWT Summary for 1601-E
SELECT
    p.vat AS payee_tin,
    p.name AS payee_name,
    at.name AS tax_type,
    at.amount AS tax_rate,
    SUM(aml.debit) AS gross_amount,
    SUM(aml.debit * at.amount / 100) AS tax_withheld
FROM account_move_line aml
JOIN account_move am ON aml.move_id = am.id
JOIN res_partner p ON am.partner_id = p.id
JOIN account_tax at ON aml.tax_line_id = at.id
WHERE am.state = 'posted'
  AND am.move_type = 'in_invoice'
  AND at.name LIKE '%EWT%'
  AND am.date BETWEEN '2026-01-01' AND '2026-01-31'
GROUP BY p.vat, p.name, at.name, at.amount;
```

## Filing Process

### eFPS Filing

1. Log in to [efps.bir.gov.ph](https://efps.bir.gov.ph)
2. Select form type
3. Enter header information (TIN, period)
4. Upload data file (CSV/XML)
5. Review summary
6. Submit and pay
7. Save confirmation receipt

### eBIRForms Filing

1. Download offline software
2. Select form
3. Enter data manually or import
4. Validate locally
5. Generate submission file
6. Upload to BIR portal
7. Process payment separately

## Certificate Generation (Form 2307)

**When Required**: Within 20 days of withholding

**Data Required**:
- Payee TIN
- Payee name and address
- Period covered
- Income paid
- Tax withheld
- ATC code

**Odoo Integration**:
```python
# Generate 2307 from vendor bill
def generate_2307(move_id):
    move = env['account.move'].browse(move_id)
    return {
        'payee_tin': move.partner_id.vat,
        'payee_name': move.partner_id.name,
        'period': move.date.strftime('%m/%Y'),
        'income_payment': move.amount_untaxed,
        'tax_withheld': sum(move.tax_line_ids.mapped('amount')),
    }
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Invalid TIN | Format error | Verify TIN with payee |
| Duplicate filing | Already submitted | Check eFPS history |
| Amount mismatch | Data error | Reconcile to source |
| System timeout | BIR server issue | Retry during off-peak |

## Compliance Calendar

```markdown
## January 2026
- Jan 10: 1601-C, 1601-E (Dec 2025)
- Jan 20: 2550M (Dec 2025)
- Jan 25: 2550Q (Q4 2025)
- Jan 31: 1604-CF (2025 Annual)

## February 2026
- Feb 10: 1601-C, 1601-E (Jan)
- Feb 20: 2550M (Jan)

## March 2026
- Mar 1: 1604-E (2025 Annual)
- Mar 10: 1601-C, 1601-E (Feb)
```

## Related Skills

- [Finance Month-End](../finance-month-end/SKILL.md)
- [Expense Processing](../expense-processing/SKILL.md)

## References

- [BIR Website](https://www.bir.gov.ph)
- [eFPS Portal](https://efps.bir.gov.ph)
- [Tax Code Reference](https://www.bir.gov.ph/taxcode)

## Changelog

- **v1.0.0** (2026-01-06): Initial release
