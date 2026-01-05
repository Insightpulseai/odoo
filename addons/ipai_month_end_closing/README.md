# IPAI Month-End Closing & BIR Tax Filing

SAP AFC-style month-end closing with BIR tax compliance for TBWA Finance.

## What you get (seeded on install)

- **2 Projects**: Month-End Close, BIR Tax Filing
- **6 OKR-scored Stages**: Backlog → Preparation → Review → Approval → Done → Blocked
- **10 Milestones**: Phase gates + Key Results
- **56 Tasks**: 34 closing + 22 tax
- **26 Tags**: PMBOK + Phases + BIR Forms
- **45 PH Holidays**: 2025–2027

## Module Metadata

- **Technical Name:** `ipai_month_end_closing`
- **Version:** 18.0.1.0.0
- **Category:** Accounting/Accounting
- **License:** AGPL-3
- **Author:** InsightPulse AI
- **Application:** No
- **Installable:** Yes

## Business Use Case

Complete month-end financial closing workflow based on SAP Advanced Financial Closing (AFC) best practices, tailored for TBWA Finance operations.

### Features

- 36 pre-configured closing tasks organized by functional area
- Employee assignments mapped to TBWA Finance team (RIM, BOM, JPAL, LAS, JLI, RMQB, JAP, JRMO)
- Three-tier approval workflow: Preparation → Review → Approval
- Task dependencies matching SAP AFC workflow patterns
- BIR tax filing calendar with automated deadlines (1601-C, 1601-EQ, 2550Q, 1702-RT/EX, 1702Q)

### BIR Compliance

- Monthly: 1601-C (Compensation), 0619-E (Creditable EWT)
- Quarterly: 1601-EQ (EWT), 2550Q (VAT), 1702Q (Income Tax)
- Annual: 1702-RT/EX (Income Tax Return)

## Installation & Dependencies

### Dependencies

- `project` (CE Core)
- `hr` (CE Core)

### Install / Upgrade (odoo-bin)

```bash
# Install module
odoo-bin -d <database> -i ipai_month_end_closing --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_month_end_closing --stop-after-init
```

### Install (Docker example)

```bash
docker exec -it odoo odoo -d <database> -i ipai_month_end_closing --stop-after-init
```

## Configuration

No specific configuration required.

## Security

* Access rules are defined in `security/ir.model.access.csv`.

## Data Files

* `security/ir.model.access.csv`
* `data/ipai_users.xml`
* `data/project_config.xml`
* `data/ipai_closing_tasks.xml`
* `data/ipai_bir_tasks.xml`
