# Enterprise Parity Strategy
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

**Goal**: Achieve >=80% Odoo Enterprise Edition feature parity by **building custom replacements** using CE + OCA + ipai_* modules.

**Philosophy**: We do NOT deploy Odoo EE. We BUILD our own solutions that replicate and often exceed EE capabilities.

## Parity Formula

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

## EE Feature Mapping

| Odoo EE Feature | EE Module | CE/OCA/IPAI Replacement | Parity |
|-----------------|-----------|-------------------------|--------|
| **Accounting** | | | |
| Bank Reconciliation | `account_accountant` | `account_reconcile_oca` | 95% |
| Financial Reports | `account_reports` | `account_financial_report` | 90% |
| Asset Management | `account_asset` | `account_asset_management` | 90% |
| Budget Management | `account_budget` | `ipai_finance_ppm` | 85% |
| Consolidation | `account_consolidation` | `ipai_finance_consolidation` | 80% |
| **HR & Payroll** | | | |
| Payroll | `hr_payroll` | `ipai_hr_payroll_ph` | 100% |
| Attendance | `hr_attendance` | `ipai_hr_attendance` | 95% |
| Leave Management | `hr_holidays` | `ipai_hr_leave` | 95% |
| Expense Management | `hr_expense` | `hr_expense` (OCA) | 90% |
| Recruitment | `hr_recruitment` | `hr_recruitment` (OCA) | 85% |
| Appraisals | `hr_appraisal` | `ipai_hr_appraisal` | 80% |
| **Services** | | | |
| Helpdesk | `helpdesk` | `ipai_helpdesk` | 90% |
| Approvals | `approvals` | `ipai_approvals` | 95% |
| Planning | `planning` | `ipai_planning` | 85% |
| Timesheet Grid | `timesheet_grid` | `ipai_timesheet` | 85% |
| Field Service | `industry_fsm` | `ipai_field_service` | 75% |
| **Studio & Customization** | | | |
| Studio | `studio` | `ipai_dev_studio_base` | 70% |
| Spreadsheet | `spreadsheet` | `ipai_spreadsheet` + Superset | 80% |
| Dashboards | `spreadsheet_dashboard` | Superset + `ipai_dashboard` | 85% |
| **Documents & Knowledge** | | | |
| Documents | `documents` | `ipai_connector_supabase` | 80% |
| Knowledge | `knowledge` | `ipai_knowledge_base` | 75% |
| Sign | `sign` | `ipai_digital_signature` | 70% |
| **Marketing** | | | |
| Marketing Automation | `marketing_automation` | n8n + `ipai_marketing` | 85% |
| Social Marketing | `social` | `ipai_social_connector` | 70% |
| Events | `event_sale` | `event` (CE) + `ipai_events` | 80% |
| **Integrations** | | | |
| IoT | `iot` | `ipai_iot_connector` | 60% |
| VoIP | `voip` | `ipai_voip_connector` | 65% |
| **BIR Compliance (PH-specific)** | | | |
| 1601-C Generation | N/A | `ipai_bir_1601c` | 100% |
| 2316 Certificates | N/A | `ipai_bir_2316` | 100% |
| Alphalist Export | N/A | `ipai_bir_alphalist` | 100% |
| VAT Reports | N/A | `ipai_bir_vat` | 100% |

## Parity Validation

Run EE parity tests before any major release:

```bash
# Run parity test suite
python scripts/test_ee_parity.py --odoo-url http://localhost:8069 --db odoo_core

# Generate HTML report
python scripts/test_ee_parity.py --report html --output docs/evidence/parity_report.html

# CI gate (fails if <80%)
./scripts/ci/ee_parity_gate.sh
```

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

## Self-Hosted ipai_* Modules (Built In-House)

We BUILD everything ourselves using open-source tools on self-hosted infrastructure:

| ipai_* Module | Replaces EE Feature | Self-Hosted Stack |
|---------------|---------------------|-------------------|
| `ipai_finance_reports` | EE Financial Reports | PostgreSQL + Superset |
| `ipai_finance_consolidation` | EE Consolidation | Custom Python + PostgreSQL views |
| `ipai_finance_forecast` | EE Forecasting | scikit-learn on DO droplet |
| `ipai_expense_intelligence` | EE Expense approval | Custom Python rules engine |
| `ipai_bir_validator` | (no EE equivalent) | Custom compliance pipelines |
| `ipai_approvals` | EE Approvals | Custom workflow engine |
| `ipai_helpdesk` | EE Helpdesk | OCA + custom enhancements |
| `ipai_planning` | EE Planning | OCA hr_planning + custom |

**Key Principle**: We own the code, we own the IP, we control the costs. No vendor lock-in.

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

## Module Parity Certification Checklist

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

## Parity CI Gate

The CI pipeline enforces parity thresholds:

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

## EE Feature Replacement Patterns

| EE Capability | Self-Hosted Replacement Pattern |
|---------------|--------------------------------|
| **Reports/Dashboards** | PostgreSQL views + Superset dashboards |
| **Workflow Automation** | n8n workflows + `ipai_platform_workflow` |
| **Document Management** | Supabase Storage + `ipai_documents` |
| **Approval Workflows** | Custom state machine in `ipai_approvals` |
| **AI/ML Features** | scikit-learn + Hugging Face on DO droplet |
| **Real-time Sync** | Supabase Realtime + webhooks |
| **SSO/Auth** | Keycloak + `ipai_auth_keycloak` |
| **BI/Analytics** | Apache Superset (self-hosted) |
| **Scheduling** | n8n cron + `ipai_scheduler` |
| **Notifications** | Slack + `ipai_notifications` |

## Testing EE Parity Claims

```bash
# Run full parity test suite
python scripts/test_ee_parity.py --odoo-url http://localhost:8069 --db odoo_core

# Test specific module parity
python scripts/test_ee_parity.py --module ipai_finance_ppm

# Generate parity report
python scripts/test_ee_parity.py --report html --output docs/evidence/parity_report.html

# CI gate (fails if <80%)
./scripts/ci/ee_parity_gate.sh
```

## Parity Score Calculation

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
