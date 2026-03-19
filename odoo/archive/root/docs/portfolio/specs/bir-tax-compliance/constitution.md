# BIR Tax Compliance - Constitution

## Non-Negotiables

1. **BIR Form Accuracy**: All 36 BIR forms must compute correctly per latest BIR regulations
2. **Filing Deadlines**: System must track and alert on all statutory deadlines
3. **Audit Trail**: Every tax computation must have complete, immutable audit trail
4. **Data Retention**: 10-year retention for all tax records (BIR requirement)
5. **TIN Validation**: All payee TINs must be validated format (XXX-XXX-XXX-XXX)

## Tax Categories (Philippines)

| Category | Forms | Frequency |
|----------|-------|-----------|
| Income Tax | 1700, 1701, 1701Q, 1702-RT/MX/EX | Annual/Quarterly |
| VAT | 2550M, 2550Q | Monthly/Quarterly |
| Withholding Tax | 1601-C, 1601-E, 1601-F, 1604-CF, 1604-E | Monthly/Annual |
| Percentage Tax | 2551M, 2551Q | Monthly/Quarterly |
| Excise Tax | 2200A, 2200P, 2200T, 2200M, 2200AN | Monthly |
| Capital Gains | 1706, 1707 | Per Transaction |
| Documentary Stamp | 2000, 2000-OT | Per Transaction |

## Compliance Rules

- VAT rate: 12% standard, 0% zero-rated (exports), Exempt (specific services)
- Withholding tax on compensation: Based on BIR tax table (progressive)
- Final withholding tax: 10-25% depending on income type
- Late filing penalty: 25% surcharge + 20% annual interest

## Integration Points

- Odoo Payroll → Forms 1601-C, 1604-CF (withholding on compensation)
- Odoo Sales → Forms 2550M/Q (VAT on sales)
- Odoo Purchases → VAT input credits
- Hire-to-Retire → Final pay tax compliance
- Control Room → Filing status dashboard
