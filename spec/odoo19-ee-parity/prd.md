# Odoo 19 Enterprise Edition Parity - Product Requirements Document

**Version**: 1.0.0
**Created**: 2026-01-28
**Status**: Planning
**Repository**: https://github.com/jgtolentino/odoo-ce

---

## Executive Summary

This document specifies the upgrade path from **Odoo 18 CE** to **Odoo 19 CE + OCA modules** to achieve **Enterprise Edition feature parity** without Enterprise licensing costs. The strategy uses:

1. **Odoo 19 Community Edition** (base)
2. **OCA 19.x modules** (EE-parity addons)
3. **Minimal `ipai_enterprise_bridge`** (glue layer for gaps)

**Cost Savings**: ~$30,000/year (avoiding Odoo Enterprise licenses for 25 users @ $36/user/month)

---

## 1. Current State Assessment

### 1.1 Existing Stack (Odoo 18 CE)

```yaml
odoo_version: 18.0
deployment: Docker (ghcr.io/jgtolentino/odoo-ce:latest)
database: PostgreSQL 16
custom_modules: 80+ ipai_* modules
architecture: Immutable image + persistent volumes
```

### 1.2 Current Custom Modules

- `ipai_workspace_core` - Core workspace functionality
- `ipai_finance_ppm` - Finance PPM with ECharts
- `ipai_ai_agents` - AI agent orchestration
- `ipai_approvals` - Multi-stage approval workflows
- `ipai_dev_studio_base` - Studio-like development tools
- [70+ additional modules]

---

## 2. Odoo 19 Upgrade Strategy

### 2.1 Strategy Selection: **Container-First (Strategy B)**

**Rationale**:
- Safer migration path (keeps Odoo 18 stack intact during transition)
- Easier rollback (restore previous compose file)
- Cleaner separation: Official Odoo 19 image + mounted OCA + ipai_*
- Aligns with CI/CD immutable image philosophy

### 2.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  Odoo 19 EE-Parity Stack                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Official Odoo 19 Image (odoo:19.0)                          │
│       ↓ mounts                                               │
│  ┌──────────────────┬──────────────────┬─────────────────┐  │
│  │ OCA 19.x Modules │ ipai_* Modules   │ ipai_enterprise │  │
│  │ (500+ addons)    │ (80+ existing)   │ _bridge (new)   │  │
│  └──────────────────┴──────────────────┴─────────────────┘  │
│       ↓ uses                                                 │
│  PostgreSQL 16 (shared with Odoo 18 during transition)       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Enterprise Edition Feature Mapping

### 3.1 EE Features → OCA Module Map

| EE Feature | OCA Module(s) | Status | Notes |
|------------|---------------|--------|-------|
| **Accounting** |||
| Advanced invoicing | `account-invoicing` (OCA) | ✅ Available | Full invoice layouts |
| Bank reconciliation | `account-reconcile` (OCA) | ✅ Available | Rule-based matching |
| Assets management | `account-financial-tools` | ✅ Available | Depreciation, disposal |
| Budget management | `account-budgeting` (OCA) | ✅ Available | Budget vs actuals |
| Analytic accounting | `account-analytic` (OCA) | ✅ Available | Multi-dimensional |
| **Studio** |||
| Model builder | `ipai_dev_studio_base` (existing) | ✅ Available | Custom models/views |
| Automation rules | `server-tools` (OCA) | ⚠️ Partial | Needs `ipai_bridge` |
| **Documents** |||
| DMS | `dms` (OCA) | ✅ Available | Full document management |
| OCR | Existing `ipai_ocr` integration | ✅ Available | PaddleOCR-VL |
| **Project** |||
| Gantt view | `web_timeline` (OCA) | ✅ Available | Timeline visualization |
| Resource planning | `project-agile` (OCA) | ✅ Available | Scrum/Kanban |
| Timesheets | `hr-timesheet` (OCA) | ✅ Available | Project time tracking |
| **HR** |||
| Appraisals | `hr` (OCA) | ⚠️ Partial | Basic only |
| Referrals | `hr` (OCA) | ⚠️ Partial | Needs custom |
| **Marketing** |||
| Email marketing | `social` (OCA) | ✅ Available | Mass mailing |
| SMS marketing | `sms` (OCA) | ⚠️ Partial | Limited providers |
| Social media | `social` (OCA) | ✅ Available | Multi-platform |
| **Manufacturing** |||
| MRP | `manufacture` (OCA) | ✅ Available | Bill of materials |
| PLM | `product-attribute` (OCA) | ⚠️ Partial | Basic PLM |
| **Website** |||
| Website builder | CE includes | ✅ Available | Core feature |
| eCommerce | CE includes | ✅ Available | Core feature |
| Blog | CE includes | ✅ Available | Core feature |

**Legend**:
- ✅ **Available**: OCA module provides full EE parity
- ⚠️ **Partial**: OCA module covers 60-80% of EE features
- ❌ **Missing**: No OCA equivalent (requires `ipai_enterprise_bridge`)

---

## 4. OCA Module Selection

### 4.1 Required OCA Repositories (19.0 branch)

```yaml
oca_repos:
  - repo: account-financial-tools
    branch: 19.0
    modules:
      - account_asset_management
      - account_budget
      - account_cost_center
      - account_move_budget

  - repo: account-financial-reporting
    branch: 19.0
    modules:
      - account_financial_report
      - mis_builder
      - bi_sql_editor

  - repo: account-invoicing
    branch: 19.0
    modules:
      - account_invoice_triple_discount
      - sale_order_invoicing_grouping_criteria

  - repo: account-reconcile
    branch: 19.0
    modules:
      - account_reconcile_oca
      - base_bank_account_number_unique

  - repo: server-tools
    branch: 19.0
    modules:
      - base_automation
      - base_technical_features
      - database_cleanup

  - repo: web
    branch: 19.0
    modules:
      - web_timeline
      - web_widget_x2many_2d_matrix
      - web_advanced_search

  - repo: project
    branch: 19.0
    modules:
      - project_task_default_stage
      - project_template
      - project_timesheet_time_control

  - repo: hr
    branch: 19.0
    modules:
      - hr_employee_document
      - hr_employee_service
      - hr_holidays_public

  - repo: dms
    branch: 19.0
    modules:
      - dms
      - dms_field

  - repo: social
    branch: 19.0
    modules:
      - mass_mailing_event
      - mail_tracking
```

**Total OCA Modules**: ~50 (from 10 repositories)

### 4.2 Fallback Strategy for Missing 19.0 Branches

If OCA 19.0 branches are not yet available:

1. **Use 18.0 branch** with clear TODO markers
2. **Test compatibility** with Odoo 19 API
3. **Port critical modules** to 19.0 if needed
4. **Document gaps** in `docs/OCA_19_PARITY_MATRIX.md`

---

## 5. ipai_enterprise_bridge Module

### 5.1 Purpose

Minimal glue layer to:
- Fill gaps where OCA modules don't provide full EE parity
- Extend OCA modules with custom behavior
- Maintain compatibility between ipai_* modules and OCA addons

### 5.2 Module Structure

```
addons/ipai/ipai_enterprise_bridge/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── automation_rule_extension.py    # Extends base_automation (OCA)
│   ├── studio_model_extension.py       # Extends ipai_dev_studio_base
│   └── hr_appraisal_extension.py       # Custom appraisal logic
├── views/
│   ├── automation_rule_views.xml
│   └── hr_appraisal_views.xml
├── security/
│   └── ir.model.access.csv
└── README.md
```

### 5.3 Dependencies

```python
{
    'name': 'InsightPulse AI Enterprise Bridge',
    'version': '19.0.1.0.0',
    'category': 'Technical',
    'depends': [
        # OCA dependencies
        'base_automation',          # server-tools
        'account_asset_management', # account-financial-tools
        'dms',                      # dms
        'web_timeline',             # web

        # ipai dependencies
        'ipai_dev_studio_base',
        'ipai_workspace_core',
    ],
    'installable': True,
}
```

---

## 6. Migration Phases

### 6.1 Phase 1: Environment Setup (Week 1)

- [ ] ODOO19-001: Clone OCA repositories (19.0 branch or nearest)
- [ ] ODOO19-002: Create `docker-compose.odoo19.yml`
- [ ] ODOO19-003: Build Odoo 19 base image with OCA modules
- [ ] ODOO19-004: Create test database `odoo19_test`
- [ ] ODOO19-005: Scaffold `ipai_enterprise_bridge` module

**Acceptance**: Odoo 19 stack runs locally with base + OCA modules

### 6.2 Phase 2: Module Porting (Week 2)

- [ ] ODOO19-006: Update all ipai_* manifests to `19.0.x.y.z`
- [ ] ODOO19-007: Fix deprecated API calls (Odoo 18 → 19)
- [ ] ODOO19-008: Port ipai_finance_ppm to Odoo 19
- [ ] ODOO19-009: Port ipai_ai_agents to Odoo 19
- [ ] ODOO19-010: Port ipai_dev_studio_base to Odoo 19

**Acceptance**: Critical ipai_* modules install on Odoo 19 without errors

### 6.3 Phase 3: Database Migration (Week 3)

- [ ] ODOO19-011: Backup production Odoo 18 database
- [ ] ODOO19-012: Create staging database clone
- [ ] ODOO19-013: Run Odoo 19 migration (`-u all`)
- [ ] ODOO19-014: Install OCA modules
- [ ] ODOO19-015: Install ipai_enterprise_bridge
- [ ] ODOO19-016: Run data migration scripts

**Acceptance**: Staging database fully migrated with no data loss

### 6.4 Phase 4: Testing & Validation (Week 4)

- [ ] ODOO19-017: Run automated tests (pytest + Odoo tests)
- [ ] ODOO19-018: Manual UAT (accounting, project, HR, CRM workflows)
- [ ] ODOO19-019: Performance benchmarking (vs Odoo 18 baseline)
- [ ] ODOO19-020: EE parity matrix validation

**Acceptance**: All critical workflows functional, performance ≥ Odoo 18

### 6.5 Phase 5: Production Deployment (Week 5)

- [ ] ODOO19-021: Build production Docker image
- [ ] ODOO19-022: Push to GHCR
- [ ] ODOO19-023: Deploy to staging (DigitalOcean droplet)
- [ ] ODOO19-024: Run smoke tests
- [ ] ODOO19-025: Deploy to production (blue-green deployment)

**Acceptance**: Production Odoo 19 running with zero downtime migration

---

## 7. Success Metrics

### 7.1 Functional Metrics

- **EE Parity Score**: ≥85% of EE features covered by CE + OCA + ipai_*
- **Module Installation Success**: 100% of ipai_* modules install on Odoo 19
- **Data Migration Completeness**: 100% of records migrated (0 data loss)
- **Workflow Coverage**: 95% of critical business processes functional

### 7.2 Performance Metrics

- **Page Load Time**: ≤ Odoo 18 baseline (avg <2s for list views)
- **Database Query Performance**: P95 ≤ 500ms
- **Module Upgrade Time**: <10 minutes for full stack upgrade
- **Container Startup Time**: <60 seconds

### 7.3 Cost Metrics

- **License Cost Savings**: $30,000/year (25 users × $36/user/month × 12 months)
- **Implementation Cost**: $15,000 (160 hours × $94/hour)
- **ROI**: 200% in year 1

---

## 8. Risk Register

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| OCA 19.0 branches unavailable | High | Medium | Use 18.0 + manual porting |
| API breaking changes (18→19) | High | Low | Comprehensive testing |
| Data migration failures | Critical | Low | Multiple backups + staging |
| Performance degradation | Medium | Low | Benchmarking gates |
| OCA module bugs | Medium | Medium | Contribute fixes upstream |

---

## 9. Rollback Strategy

### 9.1 Database Rollback

```bash
# Restore Odoo 18 database from backup
pg_restore -h db -U odoo -d odoo backups/odoo18_pre_migration.dump
```

### 9.2 Container Rollback

```bash
# Revert to Odoo 18 compose file
git checkout feat/production-docs docker-compose.prod.yml

# Restart with Odoo 18 image
docker compose -f deploy/docker-compose.prod.yml up -d
```

### 9.3 Rollback Time Budget

- **Database restore**: <15 minutes
- **Container rollback**: <5 minutes
- **Total downtime**: <20 minutes

---

## 10. Documentation Requirements

- [ ] `docs/ODOO19_MIGRATION_GUIDE.md` - Step-by-step migration instructions
- [ ] `docs/OCA_19_PARITY_MATRIX.md` - EE feature coverage matrix
- [ ] `docs/ODOO19_API_CHANGES.md` - Breaking changes documentation
- [ ] `addons/ipai/ipai_enterprise_bridge/README.md` - Bridge module usage
- [ ] `scripts/README_ODOO19.md` - Automation script documentation

---

## Appendix A: OCA Repository URLs

```bash
# Account
https://github.com/OCA/account-financial-tools.git
https://github.com/OCA/account-financial-reporting.git
https://github.com/OCA/account-invoicing.git
https://github.com/OCA/account-reconcile.git

# Server
https://github.com/OCA/server-tools.git
https://github.com/OCA/web.git

# Business
https://github.com/OCA/project.git
https://github.com/OCA/hr.git
https://github.com/OCA/dms.git
https://github.com/OCA/social.git
```

---

**Version History**:
- 1.0.0 (2026-01-28): Initial PRD
