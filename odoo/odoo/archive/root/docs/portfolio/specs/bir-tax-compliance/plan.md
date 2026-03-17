# BIR Tax Compliance - Implementation Plan

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Odoo CE 18 + OCA                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   account   │  │  hr_payroll │  │    stock    │     │
│  │  (GL, Tax)  │  │ (Salaries)  │  │ (Inventory) │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                │                │             │
│         └────────┬───────┴────────┬───────┘             │
│                  ▼                ▼                     │
│  ┌───────────────────────────────────────────────────┐ │
│  │           ipai_bir_tax_compliance                 │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │ │
│  │  │   VAT    │ │Withholding│ │  Excise  │          │ │
│  │  │  Engine  │ │  Engine   │ │  Engine  │          │ │
│  │  └──────────┘ └──────────┘ └──────────┘          │ │
│  │  ┌──────────────────────────────────────┐        │ │
│  │  │      BIR Form Generator              │        │ │
│  │  │  (2550M, 1601-C, 2200T, etc.)       │        │ │
│  │  └──────────────────────────────────────┘        │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│                    n8n Orchestration                    │
│  • Deadline alerts (5 days before)                      │
│  • Form generation triggers                             │
│  • Filing status sync to Control Room                   │
└─────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│                 Control Room Dashboard                  │
│  • Filing calendar                                      │
│  • Compliance status by tax type                        │
│  • Exception management                                 │
└─────────────────────────────────────────────────────────┘
```

## Module Structure

```
addons/ipai_bir_tax_compliance/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── bir_tax_return.py         # Base return model
│   ├── bir_vat.py                # VAT computation
│   ├── bir_withholding.py        # Withholding tax
│   ├── bir_income_tax.py         # Income tax
│   ├── bir_excise.py             # Excise tax
│   ├── bir_form_line.py          # Form line items
│   └── res_partner_bir.py        # TIN validation
├── views/
│   ├── bir_vat_views.xml
│   ├── bir_withholding_views.xml
│   ├── bir_dashboard_views.xml
│   └── menu.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   ├── bir_tax_rates.xml         # Tax rate master data
│   ├── bir_filing_deadlines.xml  # Deadline calendar
│   └── ir_cron.xml               # Deadline alerts
├── reports/
│   ├── bir_2550m_report.xml      # VAT Monthly
│   ├── bir_1601c_report.xml      # WHT Compensation
│   └── bir_1604cf_report.xml     # Annual Alphalist
└── wizard/
    ├── generate_vat_return.py
    └── generate_wht_return.py
```

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
- Base bir.tax.return model
- TIN validation on res.partner
- Filing deadline calendar
- Basic dashboard

### Phase 2: VAT Module (Week 2)
- VAT computation from account.move
- Form 2550M generation
- Form 2550Q generation
- Input/Output reconciliation

### Phase 3: Withholding Tax (Week 3)
- Compensation WHT (payroll integration)
- Expanded WHT (suppliers)
- Forms 1601-C, 1601-E
- Annual alphalist (1604-CF)

### Phase 4: Other Taxes (Week 4)
- Income tax returns
- Excise tax tracking
- Capital gains
- Documentary stamp

### Phase 5: Integration (Week 5)
- n8n deadline alerts
- Control Room sync
- Testing & validation

## Dependencies

- account (Odoo CE native)
- hr_payroll (OCA)
- account_tax_python (OCA)
- mail (notifications)
