# PPM Seed Data Bundle

Enterprise seed data for TBWA Philippines financial operations, structured using SAP canonical taxonomy with Odoo CE18 mapping layer.

## Architecture

```
seeds/
├── shared/                          # Cross-workstream configurations
│   ├── roles.yaml                   # RACI role definitions
│   ├── calendars.yaml               # PH holiday calendar
│   ├── notification_profiles.yaml   # Email/notification templates
│   ├── approval_policies.yaml       # Workflow rules
│   └── org_units.yaml               # Company structure
│
└── workstreams/
    ├── afc_financial_close/         # SAP AFC equivalent
    │   ├── 00_workstream.yaml       # Workstream definition
    │   ├── 10_templates.yaml        # Close templates (M/Q/Y)
    │   ├── 20_tasks.yaml            # 33 closing tasks
    │   ├── 30_checklists.yaml       # Evidence requirements
    │   ├── 40_kpis.yaml             # Performance metrics
    │   ├── 50_roles_raci.yaml       # RACI assignments
    │   └── 90_odoo_mapping.yaml     # Odoo CE18 model mapping
    │
    └── stc_tax_compliance/          # SAP STC equivalent
        ├── 00_workstream.yaml       # Workstream definition
        ├── 10_worklist_types.yaml   # S4_VAT, S4_VND, S4_INV, S4_WHT
        ├── 20_compliance_checks.yaml # 16 compliance checks
        ├── 30_scenarios.yaml        # Check groupings
        ├── 60_localization_ph.yaml  # PH/BIR overlay
        └── 90_odoo_mapping.yaml     # Odoo CE18 model mapping
```

## Design Principles

### 1. SAP Naming is Canonical

Task and check names follow SAP terminology for SOP/manual consistency:
- AFC tasks use SAP AFC naming conventions
- STC checks use SAP Tax Compliance business content naming

### 2. Odoo Mapping is Separate

Translation to Odoo models happens in `90_odoo_mapping.yaml`:
- Maps SAP concepts to Odoo models
- Lists OCA module dependencies
- Defines field extensions needed

### 3. Localization is Overlay

PH-specific customizations live in `60_localization_ph.yaml`:
- BIR form definitions with deadlines
- ATC (Alphanumeric Tax Codes)
- Threshold adjustments
- Evidence requirements

This keeps the SAP baseline portable while enabling full PH compliance.

## Workstreams

### AFC - Advanced Financial Closing

33 month-end closing tasks across 4 phases:

| Phase | Description | Tasks |
|-------|-------------|-------|
| I | Initial & Compliance | Payroll, Tax, VAT, CA Liquidations |
| II | Accruals & Amortization | Revenue, Expenses, Depreciation, FX |
| III | WIP & Reclassification | WIP Scheduling |
| IV | Final Adjustments & Close | Reversals, Reports, TB Sign-off |

### STC - SAP Tax Compliance

16 compliance checks across 4 worklist types:

| Worklist | Purpose | Checks |
|----------|---------|--------|
| S4_VAT | VAT compliance | TIN validation, tax codes, thresholds |
| S4_VND | Vendor master | TIN, address, bank details |
| S4_INV | Invoice quality | Partner TIN, amounts, dates |
| S4_WHT | Withholding tax | Rates, ATC codes, certificates |

## BIR Forms Covered

| Code | Name | Frequency |
|------|------|-----------|
| 2550M | Monthly VAT Declaration | Monthly |
| 1601C | Compensation WHT | Monthly |
| 1601E | Expanded WHT | Monthly |
| 2551M | Percentage Tax | Monthly |
| 2550Q | Quarterly VAT | Quarterly |
| 1604CF | Alphalist (Compensation) | Annual |
| 1604E | Alphalist (Expanded) | Annual |
| 1702 | Corporate Income Tax | Annual |

## Usage

### Loading Seeds into Odoo

Seeds are designed to be imported via:
1. XML data files (already generated in `ipai_tbwa_finance` module)
2. Python migration scripts
3. n8n workflow automation

### Updating Seeds

1. Edit YAML files in this directory
2. Run seed validation: `python scripts/validate_seeds.py`
3. Generate Odoo XML: `python scripts/generate_odoo_data.py`
4. Test in development environment

## Related

- Odoo Module: `addons/ipai_tbwa_finance/`
- Spec Bundle: `spec/ipai-tbwa-finance/`
- Sync Workflow: n8n workflow ID `notion-odoo-sync`
