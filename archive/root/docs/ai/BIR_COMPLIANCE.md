# BIR Compliance (Philippines)
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

## 2025 Contribution Tables

### SSS (Social Security System)

```python
# 15% total: 5% employee, 10% employer
# Maximum Monthly Salary Credit: P35,000
sss_base = min(gross_wage, 35000)
sss_ee = sss_base * 0.05
sss_er = sss_base * 0.10
```

### PhilHealth

```python
# 5% total: 2.5% each
# Minimum base: P10,000, Maximum: P100,000
ph_base = min(max(gross_wage, 10000), 100000)
philhealth_ee = ph_base * 0.025
philhealth_er = ph_base * 0.025
```

### Pag-IBIG

```python
# 2% each, maximum base: P5,000
pi_base = min(gross_wage, 5000)
pagibig_ee = pi_base * 0.02
pagibig_er = pi_base * 0.02
```

## TRAIN Law Tax Table (Monthly)

```python
def compute_bir_tax(taxable_income):
    """2025 Monthly Withholding Tax (TRAIN Law)"""
    if taxable_income <= 20833:
        return 0
    elif taxable_income <= 33333:
        return (taxable_income - 20833) * 0.15
    elif taxable_income <= 66667:
        return 1875 + (taxable_income - 33333) * 0.20
    elif taxable_income <= 166667:
        return 8542 + (taxable_income - 66667) * 0.25
    elif taxable_income <= 666667:
        return 33542 + (taxable_income - 166667) * 0.30
    else:
        return 183542 + (taxable_income - 666667) * 0.35
```

## BIR Forms (ipai_* modules)

| Form | Module | Purpose |
|------|--------|---------|
| 1601-C | `ipai_bir_1601c` | Monthly Withholding Tax |
| 2316 | `ipai_bir_2316` | Certificate of Compensation |
| Alphalist | `ipai_bir_alphalist` | Annual Employee List |
| 2550M/Q | `ipai_bir_vat` | Monthly/Quarterly VAT |
