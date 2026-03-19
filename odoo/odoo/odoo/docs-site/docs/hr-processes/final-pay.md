# Final pay calculation

Final pay is the total amount owed to a separating employee. Philippine law (Labor Advisory 06-20) requires release within 30 days of separation. InsightPulse AI targets 7 business days.

## Master formula

```
Final Pay = Additions - Deductions
```

Where:

- **Additions** = Pro-rated salary + Leave conversion + Pro-rated 13th month + Reimbursements + Other benefits
- **Deductions** = Outstanding advances + Unreturned assets + Tax adjustment + Government contributions

## Addition components

### 1. Pro-rated salary

Compute salary for days worked in the final pay period.

```
Pro-rated Salary = (Monthly Wage / 22) x Days Worked
```

!!! note
    22 working days per month is the standard divisor per DOLE guidelines. Adjust if the employee's contract specifies a different divisor.

### 2. Leave conversion

Convert unused leave credits to cash at separation.

```
Leave Conversion = (Unused VL + Unused SL) x Daily Rate
Daily Rate = Monthly Wage / 22
```

| Leave type | Convertible | Basis |
|------------|-------------|-------|
| Vacation leave (VL) | Yes | Company policy or CBA |
| Sick leave (SL) | Yes, if policy allows | Company policy |
| Service incentive leave (SIL) | Yes, if unused | Labor Code Article 95 |

### 3. Pro-rated 13th month pay

```
Pro-rated 13th Month = YTD Basic Salary / 12
```

!!! info
    Per PD 851, 13th month pay covers basic salary only. Allowances, overtime, and other monetary benefits are excluded unless contractually included.

### 4. Reimbursements

Sum of all approved but unpaid expense claims.

```
Reimbursements = SUM(approved_expense_claims WHERE state = 'approved' AND payment_state = 'not_paid')
```

### 5. Other benefits

| Benefit | Condition | Computation |
|---------|-----------|-------------|
| Separation pay | Authorized causes (Art. 298-299) | 1 month per year of service or 0.5 month per year, depending on cause |
| Retirement pay | RA 7641 (60+ years, 5+ years service) | 22.5 days per year of service x daily rate |
| Pro-rated bonuses | If contractually guaranteed | Per contract terms |

## Deduction components

### 1. Outstanding advances

```
Advances = SUM(hr.salary.advance WHERE state = 'approved' AND remaining_balance > 0)
```

### 2. Unreturned assets

| Asset type | Valuation method |
|------------|-----------------|
| Laptop / equipment | Net book value from `account.asset` |
| Company phone | Net book value or replacement cost |
| Access cards / keys | Fixed penalty per company policy |
| Uniforms | Prorated cost if within retention period |

### 3. Tax adjustment (annualization)

Apply BIR RR 11-2018 annualization on separation.

```
Annual Taxable Income = YTD Gross - YTD Non-taxable - YTD Contributions
Tax Due = BIR Tax Table(Annual Taxable Income)
Tax Adjustment = Tax Due - YTD Tax Withheld
```

!!! warning
    If `Tax Adjustment` is negative (employee was over-withheld), the amount becomes a **refund** and moves to the Additions side.

### 4. Government contributions

Final month contributions for the employee share.

| Agency | Basis | Reference |
|--------|-------|-----------|
| SSS | Monthly salary credit table | RA 11199 |
| PhilHealth | 5% of basic salary (employee share = 2.5%) | RA 11223 |
| Pag-IBIG | PHP 100 (employee share, capped) | RA 9679 |

## Worked example

??? example "Sample final pay: PHP 66,869.38"

    **Employee profile:**

    - Monthly wage: PHP 45,000
    - Daily rate: PHP 45,000 / 22 = PHP 2,045.45
    - Last working day: March 15 (11 working days in March)
    - Unused VL: 5 days, Unused SL: 3 days
    - YTD basic salary (Jan-Mar): PHP 100,909.09
    - Outstanding cash advance: PHP 5,000
    - YTD tax withheld: PHP 8,500

    **Additions:**

    | Component | Computation | Amount |
    |-----------|------------|--------|
    | Pro-rated salary | 2,045.45 x 11 | PHP 22,500.00 |
    | Leave conversion | (5 + 3) x 2,045.45 | PHP 16,363.64 |
    | Pro-rated 13th month | 100,909.09 / 12 | PHP 8,409.09 |
    | Reimbursements | Approved claims | PHP 3,200.00 |
    | **Total additions** | | **PHP 50,472.73** |

    **Deductions:**

    | Component | Computation | Amount |
    |-----------|------------|--------|
    | Cash advance | Outstanding balance | PHP 5,000.00 |
    | Tax adjustment | Annualized tax - YTD withheld | PHP 1,203.35 |
    | SSS (employee share) | Per salary credit table | PHP 900.00 |
    | PhilHealth (employee share) | 45,000 x 2.5% | PHP 1,125.00 |
    | Pag-IBIG (employee share) | Fixed cap | PHP 100.00 |
    | **Total deductions** | | **PHP 8,328.35** |

    **Final pay = PHP 50,472.73 - PHP 8,328.35 = PHP 42,144.38**

    *Note: Actual amounts vary based on current contribution tables and BIR tax brackets.*

## Legal references

| Reference | Scope |
|-----------|-------|
| Labor Advisory 06-20 | Final pay release within 30 days; defines components |
| PD 851 | 13th month pay computation and coverage |
| BIR RR 11-2018 | Withholding tax annualization procedures |
| Labor Code Articles 298-299 | Separation pay for authorized causes |
| RA 7641 | Retirement pay law |
| RA 11199 | SSS contribution schedule |
| RA 11223 | PhilHealth contribution schedule |
| RA 9679 | Pag-IBIG contribution schedule |

## Common errors

| Error | Symptom | Fix |
|-------|---------|-----|
| Wrong daily rate divisor | Final pay over/under by 5-10% | Confirm divisor (22 or per contract) in `hr.contract` |
| 13th month includes allowances | Overpayment | Filter YTD computation to `basic` salary category only |
| Tax not annualized | Under-withholding, BIR exposure | Enable annualization flag in `ipai_hr_final_pay` |
| Leave balance stale | Incorrect leave conversion | Run `hr.leave.allocation` accrual before computation |
| Separation pay miscalculated | Wrong year-of-service count | Use `employee.service_duration` from contract start, not hire date |
| Government contributions missed | Under-deduction | Verify active enrollment in SSS, PhilHealth, Pag-IBIG |
