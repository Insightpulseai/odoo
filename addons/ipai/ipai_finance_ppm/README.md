# IPAI Finance PPM

## 1. Overview
Finance Project Portfolio Management (Notion Parity).

**Technical Name**: `ipai_finance_ppm`
**Category**: Accounting/Finance
**Version**: 18.0.1.0.0
**Author**: InsightPulseAI

## 2. Functional Scope
No description provided.

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `base`
- `mail`
- `project`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- `record.displayrecord.name or `
- `ipai.bir.form.schedule`
- `ipai.finance.bir_schedule`
- `workstreamfields.Char(string=Workstream Name)`
- `ipai.finance.task.template`
- `phasephase.get(name, phase.get(phase_name))`
- `categorycategory.get(`
- `ipai.close.generation.run`
- `phasefields.Char(string=Phase Name, required=True)`
- `ipai.bir.process.step`
- `_reccode`
- `_recform_code`
- `ipai.finance.logframe`
- `ipai.close.task.step`
- `record.displayf{record.name} - {record.period_covered}`
- `_recdisplay_name`
- `finance.bir.deadline`
- `ipai.finance.person`
- `categoryfields.Char(string=Category Name)`
- `finance.ppm.dashboard`
- `ipai.close.generator`
- `ipai.close.generated.map`
- `displayfields.Char(compute=_compute_display_name, store=True)`
- `ipai.close.task.template`
- `stepfields.Char(`
- `workstreamworkstream.get(`
- `taskself._render_task_name(`
- `taskf[{category_label}] {template.name}`
- `_recname`

## 6. User Interface
- **Views**: 10 files
- **Menus**: (Audit Pending)

## 7. Security
- **Access Rules**: `ir.model.access.csv` found
- **Groups**: `security.xml` not found

## 8. Integrations
- (Audit Pending)

## 9. Verification Steps
```bash
# Install
odoo-bin -d <db> -i ipai_finance_ppm --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_finance_ppm --stop-after-init
```