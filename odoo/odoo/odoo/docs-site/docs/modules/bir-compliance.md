# BIR compliance

The BIR (Bureau of Internal Revenue) compliance layer handles Philippine tax reporting, withholding computation, and regulatory filing for InsightPulse AI.

## Modules

| Module | Purpose |
|--------|---------|
| `ipai_bir_tax_compliance` | Core tax computation and form generation |
| `ipai_bir_notifications` | Filing deadline alerts and reminders |
| `ipai_bir_plane_sync` | Sync compliance tasks to Plane project board |

## Supported forms

### 1601-C — Monthly withholding tax remittance

Filed monthly. Reports total compensation paid and taxes withheld for all employees.

- Due date: 10th of the following month
- Output: PDF form + CSV data file
- Auto-populated from payroll records

### 2316 — Certificate of compensation payment / tax withheld

Issued annually to each employee. Summarizes total compensation and tax withheld for the calendar year.

- Due date: January 31 of the following year
- Output: PDF per employee
- Includes SSS, PhilHealth, Pag-IBIG deductions

### Alphalist

Alphabetical list of employees with compensation and tax data. Submitted with 2316 forms.

- Format: BIR-specified DAT file
- Sorted alphabetically by surname
- Includes terminated employees who received compensation

### 2550M / 2550Q — VAT declarations

| Form | Frequency | Due date |
|------|-----------|----------|
| 2550M | Monthly | 20th of the following month |
| 2550Q | Quarterly | 25th of the month following the quarter |

## TRAIN Law withholding computation

The TRAIN (Tax Reform for Acceleration and Inclusion) Law defines the withholding tax brackets. The computation uses annualized rates divided by 12 for monthly withholding.

```python
from decimal import Decimal

TRAIN_BRACKETS = [
    (Decimal("20833"), Decimal("0"), Decimal("0")),
    (Decimal("33332"), Decimal("0.15"), Decimal("0")),
    (Decimal("66666"), Decimal("0.20"), Decimal("1875")),
    (Decimal("166666"), Decimal("0.25"), Decimal("8541.80")),
    (Decimal("666666"), Decimal("0.30"), Decimal("33541.80")),
    (Decimal("Infinity"), Decimal("0.35"), Decimal("183541.80")),
]


def compute_monthly_tax(taxable_income: Decimal) -> Decimal:
    """Compute monthly withholding tax per TRAIN Law."""
    prev_bracket = Decimal("0")
    for ceiling, rate, base_tax in TRAIN_BRACKETS:
        if taxable_income <= ceiling:
            excess = taxable_income - prev_bracket
            return base_tax + (excess * rate)
        prev_bracket = ceiling
    return Decimal("0")
```

!!! warning "Use `Decimal`, not `float`"
    All monetary and tax computations must use `Decimal` with 4-digit precision. Floating-point arithmetic causes rounding errors in tax filings.

## SSS contribution computation (2025)

```python
from decimal import Decimal

def compute_sss(monthly_salary: Decimal) -> tuple[Decimal, Decimal]:
    """Return (employee_share, employer_share) for SSS."""
    if monthly_salary < Decimal("4250"):
        return Decimal("180.00"), Decimal("390.00")

    # Bracket computation: salary credits in 500-peso increments
    bracket = min(
        int((monthly_salary - Decimal("4250")) / Decimal("500")),
        52  # Max bracket index
    )
    salary_credit = Decimal("4500") + (bracket * Decimal("500"))
    employee_share = salary_credit * Decimal("0.045")
    employer_share = salary_credit * Decimal("0.095")
    return employee_share.quantize(Decimal("0.01")), \
           employer_share.quantize(Decimal("0.01"))
```

## PhilHealth contribution computation (2025)

```python
from decimal import Decimal

PHILHEALTH_RATE = Decimal("0.05")
PHILHEALTH_CEILING = Decimal("100000")


def compute_philhealth(monthly_salary: Decimal) -> tuple[Decimal, Decimal]:
    """Return (employee_share, employer_share) for PhilHealth."""
    base = min(monthly_salary, PHILHEALTH_CEILING)
    total = (base * PHILHEALTH_RATE).quantize(Decimal("0.01"))
    share = (total / 2).quantize(Decimal("0.01"))
    return share, share
```

## Pag-IBIG contribution computation

```python
from decimal import Decimal

PAG_IBIG_MAX = Decimal("200.00")


def compute_pagibig(monthly_salary: Decimal) -> tuple[Decimal, Decimal]:
    """Return (employee_share, employer_share) for Pag-IBIG."""
    if monthly_salary <= Decimal("1500"):
        ee = (monthly_salary * Decimal("0.01")).quantize(Decimal("0.01"))
    else:
        ee = (monthly_salary * Decimal("0.02")).quantize(Decimal("0.01"))
    er = (monthly_salary * Decimal("0.02")).quantize(Decimal("0.01"))
    return min(ee, PAG_IBIG_MAX), min(er, PAG_IBIG_MAX)
```

## Data retention

!!! danger "7-year retention requirement"
    BIR requires all tax records, filings, and supporting documents to be retained for 7 years from the date of filing. The system enforces this by:

    - Preventing deletion of tax-related records within the retention period
    - Archiving (not deleting) records past retention
    - Recording all access to tax records in the audit log
