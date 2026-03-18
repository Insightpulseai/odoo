---
paths:
  - "addons/**"
  - "scripts/test_ee_parity*"
---

# Enterprise Parity Strategy

> Achieve >=80% Odoo Enterprise Edition feature parity via CE + OCA + ipai_* modules.

---

## Overview

**Target**: >=80% Odoo Enterprise Edition feature parity
**Current verified parity**: ~35-45% (audited 2026-03-08). 5 key modules do not yet exist. Most implemented modules lack test coverage.

**Philosophy**: We do NOT deploy Odoo EE. We BUILD our own solutions to replicate EE capabilities.

### Parity Formula

```
CE + OCA + ipai_* = Enterprise Parity (>=80%)

Where:
  CE      = Odoo Community Edition (base, free, open source)
  OCA     = Odoo Community Association modules (community-built)
  ipai_*  = InsightPulse AI CUSTOM-BUILT modules (our IP)

NEVER:
  - License Odoo Enterprise
  - Use odoo.com IAP services
  - Deploy proprietary EE modules
```

---

## EE Feature Mapping (Audited 2026-03-08)

> Status: **Live** = code exists with models | **Scaffolded** = stub/minimal code | **OCA** = OCA module (not yet hydrated) | **Planned** = module does not exist yet

| Odoo EE Feature | EE Module | CE/OCA/IPAI Replacement | Status | Parity | Tests |
|-----------------|-----------|-------------------------|--------|--------|-------|
| **Accounting** | | | | | |
| Bank Reconciliation | `account_accountant` | `account_reconcile_oca` | OCA | TBD | N/A |
| Financial Reports | `account_reports` | `account_financial_report` | OCA | TBD | N/A |
| Asset Management | `account_asset` | `account_asset_management` | OCA | TBD | N/A |
| Budget Management | `account_budget` | `ipai_finance_ppm` | Live | ~40% | No |
| Consolidation | `account_consolidation` | `ipai_finance_consolidation` | Planned | 0% | -- |
| **HR & Payroll** | | | | | |
| Payroll | `hr_payroll` | `ipai_hr_payroll_ph` | Live | ~70% | No |
| Attendance | `hr_attendance` | `ipai_hr_attendance` | Planned | 0% | -- |
| Leave Management | `hr_holidays` | `ipai_hr_leave` | Planned | 0% | -- |
| Expense Management | `hr_expense` | `hr_expense` (OCA) | OCA | TBD | N/A |
| Recruitment | `hr_recruitment` | `hr_recruitment` (OCA) | OCA | TBD | N/A |
| Appraisals | `hr_appraisal` | `ipai_hr_appraisal` | Planned | 0% | -- |
| **Services** | | | | | |
| Helpdesk | `helpdesk` | `ipai_helpdesk` | Live | ~40% | No |
| Approvals | `approvals` | `ipai_approvals` | **Planned** | 0% | -- |
| Planning | `planning` | `ipai_planning` | **Planned** | 0% | -- |
| Timesheet Grid | `timesheet_grid` | `ipai_timesheet` | **Planned** | 0% | -- |
| Field Service | `industry_fsm` | `ipai_field_service` | Planned | 0% | -- |
| **Studio & Customization** | | | | | |
| Studio | `studio` | `ipai_dev_studio_base` | **Planned** | 0% | -- |
| Spreadsheet | `spreadsheet` | Superset | Scaffolded | ~20% | No |
| Dashboards | `spreadsheet_dashboard` | Superset | Scaffolded | ~30% | No |
| **Documents & Knowledge** | | | | | |
| Documents | `documents` | `ipai_documents_ai` | Live | ~30% | No |
| Knowledge | `knowledge` | `ipai_knowledge_base` | **Planned** | 0% | -- |
| Sign | `sign` | `ipai_sign` | Live | ~20% | No |
| **Marketing** | | | | | |
| Marketing Automation | `marketing_automation` | n8n workflows | Scaffolded | ~30% | No |
| Social Marketing | `social` | -- | Planned | 0% | -- |
| Events | `event_sale` | `event` (CE) | CE only | ~50% | No |
| **Integrations** | | | | | |
| IoT | `iot` | -- | Planned | 0% | -- |
| VoIP | `voip` | -- | Planned | 0% | -- |
| **BIR Compliance (PH-specific)** | | | | | |
| 1601-C / Tax | N/A | `ipai_bir_tax_compliance` | Live | ~60% | No |
| Notifications | N/A | `ipai_bir_notifications` | Live | ~50% | No |
| Plane Sync | N/A | `ipai_bir_plane_sync` | Live | ~50% | No |

> **Bold Planned** = modules previously documented as implemented but confirmed missing on 2026-03-08 audit.

---

## Parity Validation

```bash
# Run parity test suite
python scripts/test_ee_parity.py --odoo-url http://localhost:8069 --db odoo_dev

# Generate HTML report
python scripts/test_ee_parity.py --report html --output docs/evidence/parity_report.html

# Test specific module parity
python scripts/test_ee_parity.py --module ipai_finance_ppm

# CI gate (fails if <80%)
./scripts/ci/ee_parity_gate.sh
```

---

## Priority for EE Feature Development

1. **P0 - Critical** (must have for production)
   - Bank Reconciliation, Financial Reports, Payroll, Approvals
   - BIR Compliance (Philippines regulatory requirement)

2. **P1 - High** (needed for full operations)
   - Helpdesk, Planning, Timesheet, Asset Management

3. **P2 - Medium** (nice to have)
   - Documents, Knowledge, Spreadsheet integration

4. **P3 - Low** (future roadmap)
   - IoT, VoIP, advanced Marketing Automation

---

## Self-Hosted ipai_* Modules (Built In-House)

| ipai_* Module | Replaces EE Feature | Self-Hosted Stack |
|---------------|---------------------|-------------------|
| `ipai_finance_reports` | EE Financial Reports | PostgreSQL + Superset |
| `ipai_finance_consolidation` | EE Consolidation | Custom Python + PostgreSQL views |
| `ipai_finance_forecast` | EE Forecasting | scikit-learn on Azure |
| `ipai_expense_intelligence` | EE Expense approval | Custom Python rules engine |
| `ipai_bir_validator` | (no EE equivalent) | Custom compliance pipelines |
| `ipai_approvals` | EE Approvals | Custom workflow engine |
| `ipai_helpdesk` | EE Helpdesk | OCA + custom enhancements |
| `ipai_planning` | EE Planning | OCA hr_planning + custom |

**Key Principle**: We own the code, we own the IP, we control the costs. No vendor lock-in.

---

## EE Feature Replacement Patterns

| EE Capability | Self-Hosted Replacement Pattern |
|---------------|--------------------------------|
| **Reports/Dashboards** | PostgreSQL views + Superset dashboards |
| **Workflow Automation** | n8n workflows + `ipai_platform_workflow` |
| **Document Management** | Supabase Storage + `ipai_documents` |
| **Approval Workflows** | Custom state machine in `ipai_approvals` |
| **AI/ML Features** | scikit-learn + Hugging Face on Azure |
| **Real-time Sync** | Supabase Realtime + webhooks |
| **SSO/Auth** | Keycloak + `ipai_auth_keycloak` |
| **BI/Analytics** | Apache Superset (self-hosted) |
| **Scheduling** | n8n cron + `ipai_scheduler` |
| **Notifications** | Slack + `ipai_notifications` |

---

## Parity Development Workflow

Every ipai_* module that claims EE parity must follow this workflow:

```
1. IDENTIFY   -> Document which EE feature(s) are being replaced
2. SPECIFY    -> Create spec bundle with acceptance criteria
3. IMPLEMENT  -> Build using CE + OCA + custom code
4. TEST       -> Verify against EE behavior checklist
5. MEASURE    -> Run parity test, document score
6. CERTIFY    -> Add to parity matrix, update CLAUDE.md
```

### Module Parity Certification Checklist

Before claiming parity for any ipai_* module:

```markdown
## Parity Certification: ipai_<module_name>

- [ ] **Spec Bundle**: spec/<module>/prd.md documents EE feature being replaced
- [ ] **Functional Tests**: tests/ cover 80%+ of EE feature behavior
- [ ] **UI/UX Parity**: User workflow matches or improves on EE
- [ ] **Data Model**: Compatible with EE migration path (if applicable)
- [ ] **Performance**: Benchmarked against EE baseline
- [ ] **Documentation**: User docs in docs/<module>/
- [ ] **CI Gate**: Added to scripts/test_ee_parity.py
```

### Parity CI Gate

```yaml
# .github/workflows/ee-parity-gate.yml
name: EE Parity Gate
on: [push, pull_request]
jobs:
  parity-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run parity tests
        run: python scripts/test_ee_parity.py --threshold 80
      - name: Fail if below threshold
        run: |
          score=$(cat docs/evidence/latest/parity_score.txt)
          if (( $(echo "$score < 80" | bc -l) )); then
            echo "Parity score $score% below 80% threshold"
            exit 1
          fi
```

### Parity Score Calculation

```python
# Weighted scoring by priority
weights = {
    "P0_critical": 3.0,   # Must-have for production
    "P1_high": 2.0,       # Needed for full operations
    "P2_medium": 1.0,     # Nice to have
    "P3_low": 0.5         # Future roadmap
}

# Score = sum(feature_parity * weight) / sum(weight)
# Target: >=80% weighted parity score
```

---

*Last updated: 2026-03-16*
