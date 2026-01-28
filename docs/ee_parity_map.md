# EE Parity Map - Odoo CE 19 + OCA + ipai_enterprise_bridge

> **CRITICAL**: This document maps Enterprise Edition features to their open-source replacements.
> NO proprietary Odoo EE code is used. All solutions are 100% open source (CE + OCA + ipai_*).

## Strategy Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│               Enterprise Parity Formula                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   CE 19.0 + OCA v19 + ipai_enterprise_bridge = EE Parity (≥80%)     │
│                                                                      │
│   Where:                                                             │
│     CE 19.0           = Odoo Community Edition 19.0 (base)          │
│     OCA v19           = Odoo Community Association modules (v19)    │
│     ipai_enterprise_  = Thin enterprise-style glue layer            │
│       bridge                                                        │
│                                                                      │
│   NEVER:                                                            │
│     - License Odoo Enterprise                                       │
│     - Use odoo.com IAP services                                     │
│     - Deploy proprietary EE modules                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Docker Image

| Property | Value |
|----------|-------|
| **Image Name** | `ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity` |
| **Base Image** | `odoo:19.0` |
| **Dockerfile** | `docker/Dockerfile.ce19` |
| **Build Script** | `docker/build-ce19.sh` |
| **Test Script** | `docker/test-ce19.sh` |
| **CI Workflow** | `.github/workflows/build-odoo-ce19-ee-parity.yml` |

## EE Feature Mapping Matrix

### Priority 0 - Critical (Must Have for Production)

| EE Feature | EE Module | OCA Replacement | ipai_* Bridge | Parity % |
|------------|-----------|-----------------|---------------|----------|
| **Bank Reconciliation** | `account_accountant` | `account_reconcile_oca` | `ipai_enterprise_bridge` | 95% |
| **Financial Reports** | `account_reports` | `account_financial_report` | `ipai_finance_ppm` | 90% |
| **Asset Management** | `account_asset` | `account_asset_management` | - | 90% |
| **Payroll (Philippines)** | `hr_payroll` | - | `ipai_hr_payroll_ph` | 100% |
| **BIR Tax Compliance** | N/A (PH-specific) | - | `ipai_finance_bir_compliance` | 100% |
| **Approvals Workflow** | `approvals` | - | `ipai_approvals` | 95% |
| **Expense Management** | `hr_expense` | `hr_expense` (CE) | `ipai_expense_ocr` | 90% |

### Priority 1 - High (Needed for Full Operations)

| EE Feature | EE Module | OCA Replacement | ipai_* Bridge | Parity % |
|------------|-----------|-----------------|---------------|----------|
| **Helpdesk** | `helpdesk` | `helpdesk` (OCA) | `ipai_helpdesk` | 90% |
| **Planning** | `planning` | `hr_planning` (OCA) | `ipai_planning_attendance` | 85% |
| **Timesheet Grid** | `timesheet_grid` | `hr_timesheet` (OCA) | - | 85% |
| **Project Forecasting** | `project_forecast` | `project_timeline` (OCA) | - | 80% |
| **Attendance** | `hr_attendance` | `hr_attendance` (CE) | `ipai_planning_attendance` | 95% |
| **Leave Management** | `hr_holidays` | `hr_holidays` (CE) | - | 95% |
| **Recruitment** | `hr_recruitment` | `hr_recruitment` (CE+OCA) | - | 85% |
| **Maintenance** | `maintenance` | `maintenance` (CE) | `ipai_enterprise_bridge` | 90% |

### Priority 2 - Medium (Nice to Have)

| EE Feature | EE Module | OCA Replacement | ipai_* Bridge | Parity % |
|------------|-----------|-----------------|---------------|----------|
| **Documents / DMS** | `documents` | `dms` (OCA) | `ipai_documents_ai` | 80% |
| **Knowledge Base** | `knowledge` | `knowledge` (OCA) | - | 75% |
| **Spreadsheet** | `spreadsheet` | - | Apache Superset | 80% |
| **Dashboards** | `spreadsheet_dashboard` | - | Apache Superset | 85% |
| **Digital Signature** | `sign` | `sign` (OCA) | - | 70% |
| **Appraisals** | `hr_appraisal` | `hr_appraisal` (OCA) | - | 80% |

### Priority 3 - Low (Future Roadmap)

| EE Feature | EE Module | OCA Replacement | ipai_* Bridge | Parity % |
|------------|-----------|-----------------|---------------|----------|
| **Marketing Automation** | `marketing_automation` | - | n8n workflows | 85% |
| **Social Marketing** | `social` | - | n8n + APIs | 70% |
| **Events** | `event_sale` | `event` (CE) | - | 80% |
| **IoT** | `iot` | - | `ipai_enterprise_bridge` | 60% |
| **VoIP** | `voip` | - | - | 65% |
| **Studio** | `studio` | - | `ipai_dev_studio_base` | 70% |
| **Field Service** | `industry_fsm` | - | - | 75% |

## OCA Repositories (v19.0)

The following OCA repositories are included in the CE 19 EE parity image:

| Repository | Purpose | Key Modules |
|------------|---------|-------------|
| `OCA/account-financial-reporting` | Financial reports | `account_financial_report` |
| `OCA/account-financial-tools` | Advanced accounting | `account_reconcile_oca`, `account_asset_management` |
| `OCA/server-auth` | Authentication | `auth_oidc`, `auth_oauth`, `auth_session_timeout` |
| `OCA/server-tools` | Server utilities | `base_technical_user`, `module_auto_update` |
| `OCA/server-ux` | UX improvements | `date_range`, `sequence_reset_period` |
| `OCA/web` | Web enhancements | `web_responsive`, `web_advanced_search` |
| `OCA/project` | Project management | `project_task_default_stage`, `project_timeline` |
| `OCA/hr` | HR modules | `hr_planning`, `hr_timesheet` |
| `OCA/helpdesk` | Support tickets | `helpdesk` |
| `OCA/dms` | Document management | `dms` |
| `OCA/knowledge` | Knowledge base | `knowledge` |
| `OCA/mis-builder` | MIS reporting | `mis_builder` |

## ipai_enterprise_bridge Module

The `ipai_enterprise_bridge` module is the thin glue layer that:

1. **Harmonizes menus and navigation** - Unified enterprise-style menu structure
2. **Provides EE-like access rights** - Security groups mimicking EE features
3. **Bridges OCA modules** - Integration between multiple OCA addons
4. **Adds missing features** - Small features not covered by OCA
5. **IoT integration** - Basic IoT device management without EE dependency

### Key Components

```
addons/ipai/ipai_enterprise_bridge/
├── __manifest__.py          # Module definition (v19.0.1.0.0)
├── models/
│   ├── iot_device.py        # IoT device management (replaces EE iot)
│   ├── ipai_close.py        # Period close workflow
│   └── ipai_policy.py       # Approval policies
├── views/
│   ├── enterprise_bridge_views.xml
│   ├── iot_device_views.xml
│   ├── res_config_settings_views.xml
│   └── ...
├── security/
│   ├── security.xml         # Security groups
│   └── ir.model.access.csv  # Access rights
└── data/
    ├── enterprise_bridge_data.xml
    ├── oauth_providers.xml  # SSO providers
    └── ...
```

### Dependencies

```python
"depends": [
    "base",
    "base_setup",
    "mail",
    "auth_oauth",
    "fetchmail",
    "web",
    "hr_expense",
    "maintenance",
    "project",
]
```

## Self-Hosted Stack Integration

The EE parity strategy relies on self-hosted services for certain features:

| EE Capability | Self-Hosted Replacement |
|---------------|------------------------|
| Reports/Dashboards | PostgreSQL views + Apache Superset |
| Workflow Automation | n8n workflows + `ipai_platform_workflow` |
| Document Management | Supabase Storage + `ipai_documents_ai` |
| Approval Workflows | Custom state machine in `ipai_approvals` |
| AI/ML Features | Hugging Face models on DigitalOcean droplet |
| Real-time Sync | Supabase Realtime + webhooks |
| SSO/Auth | Keycloak + `auth_oidc` (OCA) |
| BI/Analytics | Apache Superset (self-hosted) |

## Parity Score Calculation

```python
# Weighted scoring by priority
weights = {
    "P0_critical": 3.0,   # Must-have for production
    "P1_high": 2.0,       # Needed for full operations
    "P2_medium": 1.0,     # Nice to have
    "P3_low": 0.5         # Future roadmap
}

# Current score (example calculation):
# P0: (95 + 90 + 90 + 100 + 100 + 95 + 90) / 7 = 94.3% * 3.0 = 282.9
# P1: (90 + 85 + 85 + 80 + 95 + 95 + 85 + 90) / 8 = 88.1% * 2.0 = 176.2
# P2: (80 + 75 + 80 + 85 + 70 + 80) / 6 = 78.3% * 1.0 = 78.3
# P3: (85 + 70 + 80 + 60 + 65 + 70 + 75) / 7 = 72.1% * 0.5 = 36.1
#
# Total weighted: (282.9 + 176.2 + 78.3 + 36.1) / (3.0 + 2.0 + 1.0 + 0.5) = 88.3%

# Target: ≥80% weighted parity score ✓
```

## Validation Commands

```bash
# Build the CE 19 EE parity image
./docker/build-ce19.sh

# Run smoke tests
./docker/test-ce19.sh

# Run local instance
./docker/run-local-ce19.sh

# Push to registry
./docker/push-ce19.sh

# Run parity tests
python scripts/test_ee_parity.py --odoo-url http://localhost:8069 --db odoo_core

# CI gate (fails if <80%)
./scripts/ci/ee_parity_gate.sh
```

## Rollback Strategy

1. **Always tag images with immutable version tags** (e.g., `19.0.1`, `19.0.2`)
2. **Keep a CHANGELOG** for each image build
3. **Rollback command:**
   ```bash
   # Example: rollback to previous version
   docker pull ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity-prev
   docker stop odoo-ce19 && docker rm odoo-ce19
   docker run -d --name odoo-ce19 ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity-prev
   ```

## References

- **CLAUDE.md** - Full project documentation with EE parity strategy
- **docs/odoo-apps-parity.md** - Existing parity matrix for Odoo 18
- **addons/ipai/ipai_enterprise_bridge/** - Bridge module source code
- **vendor/oca.lock.json** - OCA module lock file (v18.0, to be updated for v19.0)

---

*Document Version: 19.0.1.0.0*
*Last Updated: 2026-01-28*
