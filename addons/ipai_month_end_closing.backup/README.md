# IPAI Month-End Closing & BIR Tax Filing

Odoo 18 CE module for TBWA Finance month-end closing workflow and BIR tax compliance.

## Overview

This module implements SAP AFC (Advanced Financial Closing) best practices for Philippine corporate finance operations. It provides:

- **36 pre-configured closing tasks** organized by functional area
- **BIR tax filing calendar** with automated deadline tracking
- **Three-tier approval workflow**: Preparation → Review → Approval
- **Employee assignments** mapped to TBWA Finance team structure

## Installation

```bash
# Copy to your addons folder
cp -r ipai_month_end_closing /mnt/extra-addons/

# Update apps list and install
docker exec -it odoo-web odoo -d your_db -u base --stop-after-init
docker exec -it odoo-web odoo -d your_db -i ipai_month_end_closing --stop-after-init
```

## Dependencies

- `project` (Odoo core)
- `hr` (Odoo core)

## Module Structure

```
ipai_month_end_closing/
├── __manifest__.py
├── __init__.py
├── security/
│   └── ir.model.access.csv
└── data/
    ├── hr_employees.xml          # TBWA Finance team
    ├── project_config.xml        # Stages, tags, project templates
    ├── closing_tasks.xml         # 36 month-end tasks
    └── tax_filing_tasks.xml      # BIR filing calendar
```

## Employee Codes

| Code | Name | Role |
|------|------|------|
| CKVC | Khalil Veracruz | Finance Director |
| RIM | Rey Meran | Senior Finance Manager |
| BOM | Beng Manalo | Finance Supervisor |
| JPAL | Jinky Paladin | Finance Supervisor |
| LAS | Amor Lasaga | Senior Finance Associate |
| JLI | Jerald Loterte | Finance Associate |
| RMQB | RMQB | Finance Associate |
| JAP | JAP | Finance Associate - VAT |
| JRMO | JRMO | Finance Associate - Accruals |

## Workflow Stages

1. **Not Started** - Task pending initiation
2. **Preparation** - Preparer working (1 day)
3. **Review** - Reviewer validating (0.5 day)
4. **Approval** - Finance Director sign-off (0.5 day)
5. **Completed** - Task finished
6. **Blocked** - Waiting on dependencies

## Functional Areas

- Payroll & Personnel
- Tax & Provisions
- Rent & Leases
- Accruals & Expenses
- Prior Period Review
- Amortization & Corporate
- Insurance
- Treasury & Other
- Client Billings & WIP/OOP
- VAT & Taxes
- CA Liquidations
- AR/AP Aging
- Regional Reporting

## BIR Forms Covered

| Form | Description | Frequency |
|------|-------------|-----------|
| 1601-C | Withholding Tax on Compensation | Monthly |
| 0619-E | Creditable EWT | Monthly |
| 1601-EQ | Quarterly EWT Remittance | Quarterly |
| 2550Q | Quarterly VAT Return | Quarterly |
| 1702Q | Quarterly Income Tax | Quarterly |
| 1702-RT/EX | Annual Income Tax Return | Annual |

## Smart Delta Architecture

This module follows the `ipai_*` Smart Delta pattern:
- Extends core Odoo `project` module
- No monkey-patching or forks
- OCA-compatible, marketplace-ready
- AGPL-3 licensed

## License

AGPL-3 (OCA-compatible)

## Author

InsightPulse AI - https://insightpulseai.net
