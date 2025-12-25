# IPAI Module Suite - Technical Documentation Index

**Last Updated**: 2025-12-26
**Total Modules**: 21
**Odoo Version**: 18.0 CE
**OCA Compliance**: ✅ AGPL-3 licensed

---

## Documentation Overview

This directory contains comprehensive, engineering-grade technical documentation for 21 IPAI custom modules. Each module documentation is extracted directly from source code and Odoo metadata patterns - no guessing, only verifiable facts.

**Documentation Standards**:
- ✅ **Evidence-Based**: All content extracted from source code analysis
- ✅ **File Citations**: Every component includes file path references
- ✅ **XML ID Extraction**: Complete XML IDs for records, menus, views, actions
- ✅ **Odoo 18 Compatibility**: Flags deprecated constructs (e.g., `ir.cron.numbercall`, `type="xml"`)
- ✅ **Deterministic**: Repeatable documentation generation from source code
- ✅ **Verification SQL**: Concrete SQL queries to verify installation and data integrity

---

## Quick Navigation

### By Layer

**WorkOS (9 modules)** - Workspace Operating System (Notion/AFFiNE parity)
- [ipai_workos_affine](./ipai_workos_affine.md) - AFFiNE workspace integration
- [ipai_workos_core](./ipai_workos_core.md) - Core workspace engine
- [ipai_workos_blocks](./ipai_workos_blocks.md) - Block-based content system
- [ipai_workos_canvas](./ipai_workos_canvas.md) - Canvas editing interface
- [ipai_workos_collab](./ipai_workos_collab.md) - Real-time collaboration
- [ipai_workos_db](./ipai_workos_db.md) - Workspace databases
- [ipai_workos_search](./ipai_workos_search.md) - Full-text search engine
- [ipai_workos_templates](./ipai_workos_templates.md) - Workspace templates
- [ipai_workos_views](./ipai_workos_views.md) - View system (list, kanban, calendar)

**Platform (5 modules)** - Platform utilities and infrastructure
- [ipai_platform_approvals](./ipai_platform_approvals.md) - Approval workflow engine
- [ipai_platform_audit](./ipai_platform_audit.md) - Audit trail and logging
- [ipai_platform_permissions](./ipai_platform_permissions.md) - Role-based access control
- [ipai_platform_theme](./ipai_platform_theme.md) - Customizable UI themes
- [ipai_platform_workflow](./ipai_platform_workflow.md) - Workflow orchestration

**Finance (6 modules)** - BIR compliance, PPM, month-end closing
- [ipai_bir_tax_compliance](./ipai_bir_tax_compliance.md) - BIR tax filing automation
- [ipai_close_orchestration](./ipai_close_orchestration.md) - Close cycle orchestration
- [ipai_finance_ppm_golive](./ipai_finance_ppm_golive.md) - Finance PPM go-live automation
- [ipai_month_end](./ipai_month_end.md) - Month-end closing workflows
- [ipai_ppm_a1](./ipai_ppm_a1.md) - A1 Control Center (logframe + BIR schedule)
- [ipai_tbwa_finance](./ipai_tbwa_finance.md) - TBWA finance operations ⚠️ **Odoo 18 Fix Required**

**CRM (1 module)** - Customer relationship management
- [ipai_crm_pipeline](./ipai_crm_pipeline.md) - CRM pipeline management

---

## Installation Order

**Critical**: Install modules in dependency order to avoid circular dependency errors.

### Phase 1: Platform Utilities (No dependencies)
```bash
# Install platform utilities first
odoo -d <database> -i ipai_platform_permissions,ipai_platform_audit,ipai_platform_theme --stop-after-init
```

**Modules**:
- `ipai_platform_permissions` - Required by other platform modules
- `ipai_platform_audit` - Logging foundation
- `ipai_platform_theme` - UI customization

---

### Phase 2: Platform Workflows
```bash
# Install workflow engines
odoo -d <database> -i ipai_platform_approvals,ipai_platform_workflow --stop-after-init
```

**Modules**:
- `ipai_platform_approvals` - Approval workflow engine
- `ipai_platform_workflow` - Generic workflow orchestration

---

### Phase 3: WorkOS Core
```bash
# Install WorkOS foundation
odoo -d <database> -i ipai_workos_core,ipai_workos_blocks,ipai_workos_db --stop-after-init
```

**Modules**:
- `ipai_workos_core` - Core workspace engine
- `ipai_workos_blocks` - Block-based content system
- `ipai_workos_db` - Workspace databases

---

### Phase 4: WorkOS Collaboration
```bash
# Install collaboration features
odoo -d <database> -i ipai_workos_collab,ipai_workos_canvas,ipai_workos_views --stop-after-init
```

**Modules**:
- `ipai_workos_collab` - Real-time collaboration
- `ipai_workos_canvas` - Canvas editing
- `ipai_workos_views` - View system (list, kanban, calendar)

---

### Phase 5: WorkOS Advanced
```bash
# Install advanced WorkOS features
odoo -d <database> -i ipai_workos_search,ipai_workos_templates,ipai_workos_affine --stop-after-init
```

**Modules**:
- `ipai_workos_search` - Full-text search
- `ipai_workos_templates` - Workspace templates
- `ipai_workos_affine` - AFFiNE workspace integration

---

### Phase 6: Finance Base
```bash
# Install finance foundation modules
odoo -d <database> -i ipai_bir_tax_compliance,ipai_close_orchestration --stop-after-init
```

**Modules**:
- `ipai_bir_tax_compliance` - BIR tax filing automation
- `ipai_close_orchestration` - Close cycle orchestration

---

### Phase 7: Finance PPM
```bash
# Install Finance PPM stack
# ⚠️ CRITICAL: Fix ipai_tbwa_finance BEFORE installing (see Odoo 18 Compatibility below)
odoo -d <database> -i ipai_ppm_a1,ipai_month_end,ipai_finance_ppm_golive --stop-after-init
```

**Modules**:
- `ipai_ppm_a1` - A1 Control Center (logframe + BIR schedule)
- `ipai_month_end` - Month-end closing workflows
- `ipai_finance_ppm_golive` - Finance PPM go-live automation

---

### Phase 8: CRM (Optional)
```bash
# Install CRM pipeline
odoo -d <database> -i ipai_crm_pipeline --stop-after-init
```

**Modules**:
- `ipai_crm_pipeline` - CRM pipeline management

---

### Phase 9: TBWA Finance (⚠️ Requires Fix)
```bash
# ⚠️ ONLY install after applying Odoo 18 fix (see below)
odoo -d <database> -i ipai_tbwa_finance --stop-after-init
```

**Modules**:
- `ipai_tbwa_finance` - TBWA finance operations

---

## ⚠️ Odoo 18 Compatibility Issues

### Critical Issue: ipai_tbwa_finance - Deprecated `numbercall` Field

**Status**: 🚨 MUST FIX BEFORE INSTALLATION

**Affected Module**: `ipai_tbwa_finance`

**Issue**: Module uses deprecated `ir.cron.numbercall` field in `data/ir_cron.xml`, causing installation failure on Odoo 18.

**Error Message**:
```
odoo.exceptions.ValidationError: Invalid field `numbercall` on `ir.cron`
```

**Fix Procedure**:
```bash
# 1. Edit the file
$EDITOR addons/ipai/ipai_tbwa_finance/data/ir_cron.xml

# 2. Remove this line:
# <field name="numbercall">-1</field>

# 3. Commit fix
git add addons/ipai/ipai_tbwa_finance/data/ir_cron.xml
git commit -m "fix(tbwa_finance): drop ir.cron numbercall for Odoo 18"

# 4. Push to repository
git push origin main

# 5. Now safe to install
odoo -d <database> -i ipai_tbwa_finance --stop-after-init
```

**Verification**:
```sql
-- Verify cron job installed correctly
SELECT id, name, active, nextcall
FROM ir_cron
WHERE id IN (
  SELECT res_id FROM ir_model_data
  WHERE module='ipai_tbwa_finance' AND model='ir.cron'
);
-- Should return cron job records without errors
```

---

## Documentation Structure

Each module documentation file contains the following sections:

### 1. Overview
- Module metadata (version, category, license, author)
- Summary and description
- Installability and application status

### 2. Dependencies
- Odoo core module dependencies
- IPAI module dependencies
- Implicit dependencies

### 3. Data Model
- Python models with class names and file paths
- Fields with types and locations
- Constraints and indexes (where declared)

### 4. Security
- Security groups with XML IDs
- Access rules (`ir.model.access.csv`)
- Record rules (`ir.rule`) with domains and groups

### 5. UI (Menus, Actions, Views)
- Menu definitions with XML IDs and hierarchy
- Actions (window actions, server actions)
- Views (tree, form, kanban, search, graph, pivot, calendar)
- Odoo 18 compatibility flags (deprecated `type="xml"` attribute)

### 6. Automation
- Scheduled actions (`ir.cron`) with intervals and functions
- Server actions and automated actions
- Odoo 18 compatibility flags (deprecated `numbercall` field)

### 7. Integrations
- HTTP controllers with routes
- Webhooks and external API endpoints
- RPC methods and custom APIs

### 8. Configuration
- Data files (XML, CSV)
- Demo data files
- System parameters and settings

### 9. Operational
- Installation commands
- Upgrade procedures
- Odoo 18 compatibility issues (if any)
- Troubleshooting

### 10. Verification
- SQL queries to verify module installation
- Data model verification (table counts)
- Menu and view accessibility checks
- Scheduled action verification

---

## Usage Patterns

### Finding Modules by Feature

**Workspace Management**:
- Block-based editing → [ipai_workos_blocks](./ipai_workos_blocks.md)
- Real-time collaboration → [ipai_workos_collab](./ipai_workos_collab.md)
- Database views → [ipai_workos_db](./ipai_workos_db.md)
- Full-text search → [ipai_workos_search](./ipai_workos_search.md)

**Finance Operations**:
- BIR tax filing → [ipai_bir_tax_compliance](./ipai_bir_tax_compliance.md)
- Month-end closing → [ipai_month_end](./ipai_month_end.md)
- PPM logframe → [ipai_ppm_a1](./ipai_ppm_a1.md)
- Close orchestration → [ipai_close_orchestration](./ipai_close_orchestration.md)

**Platform Utilities**:
- Approval workflows → [ipai_platform_approvals](./ipai_platform_approvals.md)
- Audit logging → [ipai_platform_audit](./ipai_platform_audit.md)
- Role-based access → [ipai_platform_permissions](./ipai_platform_permissions.md)
- UI theming → [ipai_platform_theme](./ipai_platform_theme.md)

---

## Cross-Module Dependencies

### Platform Layer Dependencies
- `ipai_platform_approvals` → requires `ipai_platform_permissions`
- `ipai_platform_workflow` → requires `ipai_platform_permissions`

### WorkOS Layer Dependencies
- `ipai_workos_collab` → requires `ipai_workos_core`
- `ipai_workos_canvas` → requires `ipai_workos_core`, `ipai_workos_blocks`
- `ipai_workos_views` → requires `ipai_workos_core`, `ipai_workos_db`
- `ipai_workos_search` → requires `ipai_workos_core`
- `ipai_workos_templates` → requires `ipai_workos_core`, `ipai_workos_blocks`
- `ipai_workos_affine` → requires `ipai_workos_core`

### Finance Layer Dependencies
- `ipai_ppm_a1` → requires `ipai_bir_tax_compliance`, `ipai_close_orchestration`
- `ipai_finance_ppm_golive` → requires `ipai_ppm_a1`, `ipai_month_end`
- `ipai_tbwa_finance` → requires `ipai_ppm_a1`, `ipai_bir_tax_compliance`

---

## Verification Procedures

### Post-Installation Verification

After installing all modules, run the following verification checks:

```sql
-- 1. Verify all 21 modules installed
SELECT name, state, latest_version
FROM ir_module_module
WHERE name IN (
  'ipai_workos_affine', 'ipai_workos_core', 'ipai_workos_blocks',
  'ipai_workos_canvas', 'ipai_workos_collab', 'ipai_workos_db',
  'ipai_workos_search', 'ipai_workos_templates', 'ipai_workos_views',
  'ipai_platform_approvals', 'ipai_platform_audit', 'ipai_platform_permissions',
  'ipai_platform_theme', 'ipai_platform_workflow',
  'ipai_bir_tax_compliance', 'ipai_close_orchestration', 'ipai_finance_ppm_golive',
  'ipai_month_end', 'ipai_ppm_a1', 'ipai_tbwa_finance',
  'ipai_crm_pipeline'
)
AND state != 'installed'
ORDER BY name;
-- Expected: 0 rows (all installed)

-- 2. Verify no deprecated cron fields
SELECT id, name
FROM ir_cron
WHERE id IN (
  SELECT res_id FROM ir_model_data
  WHERE module IN (
    'ipai_workos_affine', 'ipai_workos_core', 'ipai_workos_blocks',
    'ipai_workos_canvas', 'ipai_workos_collab', 'ipai_workos_db',
    'ipai_workos_search', 'ipai_workos_templates', 'ipai_workos_views',
    'ipai_platform_approvals', 'ipai_platform_audit', 'ipai_platform_permissions',
    'ipai_platform_theme', 'ipai_platform_workflow',
    'ipai_bir_tax_compliance', 'ipai_close_orchestration', 'ipai_finance_ppm_golive',
    'ipai_month_end', 'ipai_ppm_a1', 'ipai_tbwa_finance',
    'ipai_crm_pipeline'
  )
  AND model='ir.cron'
);
-- Should execute without errors (no deprecated numbercall field)

-- 3. Verify menus accessible
SELECT COUNT(*)
FROM ir_ui_menu
WHERE id IN (
  SELECT res_id FROM ir_model_data
  WHERE module IN (
    'ipai_workos_affine', 'ipai_workos_core', 'ipai_workos_blocks',
    'ipai_workos_canvas', 'ipai_workos_collab', 'ipai_workos_db',
    'ipai_workos_search', 'ipai_workos_templates', 'ipai_workos_views',
    'ipai_platform_approvals', 'ipai_platform_audit', 'ipai_platform_permissions',
    'ipai_platform_theme', 'ipai_platform_workflow',
    'ipai_bir_tax_compliance', 'ipai_close_orchestration', 'ipai_finance_ppm_golive',
    'ipai_month_end', 'ipai_ppm_a1', 'ipai_tbwa_finance',
    'ipai_crm_pipeline'
  )
  AND model='ir.ui.menu'
);
-- Should return >0 (menus created)
```

---

## Support and Documentation

**Primary Maintainer**: Jake Tolentino (Finance SSC Manager / Odoo Developer)
**Organization**: InsightPulse AI (TBWA)
**Repository**: https://github.com/jgtolentino/odoo-ce
**Documentation Home**: `docs/ipai/` (master documentation)

**For Issues**:
1. Check module-specific documentation for troubleshooting
2. Review [INSTALLATION.md](../ipai/INSTALLATION.md) for installation procedures
3. Review [OPERATIONS_RUNBOOK.md](../ipai/OPERATIONS_RUNBOOK.md) for operational procedures
4. Open issue in GitHub repository with:
   - Module name and version
   - Odoo version
   - Error message and stack trace
   - Steps to reproduce

**For Migration Help**:
1. Review [CHANGELOG.md](../ipai/CHANGELOG.md) for version history and breaking changes
2. Test in staging environment first
3. Follow pre-migration checklist completely
4. Keep Odoo 17 backups until Odoo 18 verified stable

---

## Automation and Tooling

### Documentation Generation

All module documentation is generated using `scripts/generate_module_docs.py`:

```bash
# Regenerate all 21 module documentation files
python3 scripts/generate_module_docs.py

# Output: docs/modules/<module_name>.md (21 files)
# Output: docs/modules/generation_summary.json (metadata)
```

**Generation Rules**:
- Evidence-based: Only document what can be proven from source code
- File citations: Include file paths for all extracted components
- XML ID extraction: Complete XML IDs for records, menus, views, actions
- Odoo 18 compatibility: Flag deprecated constructs automatically
- Deterministic: Same source code = same documentation output

**Generation Metadata**: See [generation_summary.json](./generation_summary.json)

---

## Related Documentation

**Master Documentation** (`docs/ipai/`):
- [README.md](../ipai/README.md) - Overview and quick start
- [INSTALLATION.md](../ipai/INSTALLATION.md) - Installation procedures, upgrade paths, troubleshooting
- [ARCHITECTURE.md](../ipai/ARCHITECTURE.md) - System architecture, data flow, integration points
- [SECURITY_MODEL.md](../ipai/SECURITY_MODEL.md) - Security groups, access control, RLS policies
- [OPERATIONS_RUNBOOK.md](../ipai/OPERATIONS_RUNBOOK.md) - Operational procedures, monitoring, backup/restore
- [CHANGELOG.md](../ipai/CHANGELOG.md) - Version history and migration notes

**Per-Module Documentation** (`docs/modules/`):
- 21 module-specific technical documentation files (this directory)

---

**Last Updated**: 2025-12-26
**Document Version**: 1.0.0
**Generated By**: Automated module documentation system (`scripts/generate_module_docs.py`)
