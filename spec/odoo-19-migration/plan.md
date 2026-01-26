# Odoo 19 Migration — Implementation Plan

---

**Status**: DRAFT
**Created**: 2026-01-26
**Approach**: Phased migration with parallel environments

---

## Overview

This plan outlines the step-by-step implementation for migrating odoo-ce from Odoo 18 CE to Odoo 19 CE.

```
┌─────────────────────────────────────────────────────────────────┐
│                    MIGRATION ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   PHASE 0: PREPARATION                                          │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│   │ Audit IPAI  │───▶│ Update Tests│───▶│ Document    │         │
│   │ Modules     │    │ Suite       │    │ Baseline    │         │
│   └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                  │
│   PHASE 1: SANDBOX                                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│   │ Odoo 19 Dev │───▶│ Port Core   │───▶│ Validate    │         │
│   │ Environment │    │ Modules     │    │ OCA Deps    │         │
│   └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                  │
│   PHASE 2: STAGING                                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│   │ Full Module │───▶│ Integration │───▶│ Load        │         │
│   │ Migration   │    │ Testing     │    │ Testing     │         │
│   └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                  │
│   PHASE 3: PRODUCTION                                           │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│   │ Backup &    │───▶│ Execute     │───▶│ Verify &    │         │
│   │ Freeze      │    │ Migration   │    │ Monitor     │         │
│   └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 0: Preparation

### 0.1 Module Audit

**Objective**: Catalog all IPAI modules and assess Odoo 19 compatibility.

```bash
# Generate module inventory
python scripts/audit_ipai_modules.py --output docs/IPAI_MODULE_AUDIT.md

# Check for deprecated API usage
python scripts/check_odoo_api_compat.py --target-version 19.0
```

**Deliverables**:
- `docs/IPAI_MODULE_AUDIT.md` — Complete inventory with compatibility status
- `docs/API_CHANGES_ODOO_19.md` — Breaking changes affecting IPAI modules

### 0.2 OCA Dependency Check

**Objective**: Verify all OCA dependencies have 19.0 branches.

```bash
# Check OCA branch availability
./scripts/check_oca_branches.sh 19.0

# Update oca.lock.json with 19.0 targets
python scripts/update_oca_lock.py --target 19.0 --dry-run
```

**Deliverables**:
- Updated `oca.lock.json` with 19.0 branch mappings
- List of OCA modules without 19.0 branches (need alternatives)

### 0.3 Test Suite Enhancement

**Objective**: Ensure comprehensive test coverage before migration.

```bash
# Run current test coverage analysis
./scripts/ci/run_odoo_tests.sh --coverage

# Generate coverage report
python scripts/generate_coverage_report.py
```

**Deliverables**:
- Test coverage report (target: 80%+ for critical modules)
- New tests for uncovered migration-critical paths

### 0.4 Baseline Documentation

**Objective**: Document current state for comparison.

```bash
# Capture current performance baseline
./scripts/performance_baseline.sh --output docs/PERFORMANCE_BASELINE_18.md

# Document integration endpoints
./scripts/document_integrations.sh --output docs/INTEGRATION_BASELINE.md
```

**Deliverables**:
- `docs/PERFORMANCE_BASELINE_18.md`
- `docs/INTEGRATION_BASELINE.md`
- Database schema snapshot

---

## Phase 1: Sandbox Testing

### 1.1 Odoo 19 Development Environment

**Objective**: Set up isolated Odoo 19 development environment.

```bash
# Create Odoo 19 development branch
git checkout -b feat/odoo-19-migration

# Update Docker configuration
cat > docker/Dockerfile.odoo19 << 'EOF'
FROM odoo:19.0
# Custom configuration for IPAI stack
COPY --chown=odoo:odoo addons/ipai /mnt/extra-addons/ipai
COPY --chown=odoo:odoo config/odoo19.conf /etc/odoo/odoo.conf
EOF

# Start development environment
docker compose -f docker-compose.odoo19.yml up -d
```

**Deliverables**:
- `docker/Dockerfile.odoo19` — Odoo 19 container definition
- `docker-compose.odoo19.yml` — Development compose file
- Working Odoo 19 dev environment

### 1.2 Core Module Porting

**Objective**: Port foundation IPAI modules to Odoo 19.

**Priority Order**:
1. `ipai_dev_studio_base` — Base dependencies
2. `ipai_workspace_core` — Core workspace
3. `ipai_ce_branding` — CE branding layer
4. `ipai_ai_core` — AI framework

```bash
# For each module, run compatibility check and fix
for module in ipai_dev_studio_base ipai_workspace_core ipai_ce_branding ipai_ai_core; do
    ./scripts/migrate_module.sh $module --target 19.0
    ./scripts/ci/run_odoo_tests.sh $module
done
```

**Common Migration Patterns**:

```python
# Pattern 1: API.v8 → API.v19 changes
# Before (Odoo 18)
from odoo import api, fields, models

class MyModel(models.Model):
    @api.multi  # Deprecated in 19
    def my_method(self):
        pass

# After (Odoo 19)
from odoo import api, fields, models

class MyModel(models.Model):
    def my_method(self):  # @api.multi removed
        pass
```

```xml
<!-- Pattern 2: View inheritance changes -->
<!-- Before (Odoo 18) -->
<record id="view_form_inherit" model="ir.ui.view">
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='name']" position="after">
            <field name="custom_field"/>
        </xpath>
    </field>
</record>

<!-- After (Odoo 19) - OWL 2.x compatible -->
<record id="view_form_inherit" model="ir.ui.view">
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='name']" position="after">
            <field name="custom_field" widget="char"/>
        </xpath>
    </field>
</record>
```

**Deliverables**:
- 4 core modules ported and tested
- Migration patterns documented
- Automated migration script for common changes

### 1.3 OCA Dependency Validation

**Objective**: Verify OCA modules work with Odoo 19.

```bash
# Clone OCA 19.0 branches
./scripts/clone_oca_branches.sh 19.0

# Install and test each OCA module
for repo in web account sale purchase; do
    ./scripts/test_oca_module.sh $repo --branch 19.0
done
```

**Deliverables**:
- All OCA dependencies verified on 19.0
- Forks created for modules without 19.0 branches
- `oca.lock.json` updated with 19.0 pins

---

## Phase 2: Staging Migration

### 2.1 Full Module Migration

**Objective**: Port all 80+ IPAI modules to Odoo 19.

```bash
# Batch migration script
./scripts/migrate_all_ipai_modules.sh --target 19.0

# Run full test suite
./scripts/ci/run_odoo_tests.sh --all-modules
```

**Module Migration Checklist**:

| Domain | Module Count | Priority |
|--------|--------------|----------|
| AI/Agents | 10 | P0 |
| Finance | 15 | P0 |
| Platform | 12 | P0 |
| Workspace | 8 | P1 |
| Studio | 10 | P1 |
| Industry | 6 | P1 |
| WorkOS | 8 | P2 |
| Theme/UI | 5 | P2 |
| Integrations | 6 | P0 |

**Deliverables**:
- All 80+ modules ported
- 100% unit test pass rate
- Migration log with changes

### 2.2 Data Migration Testing

**Objective**: Validate data migration with production-equivalent data.

```bash
# Create anonymized production snapshot
./scripts/create_migration_snapshot.sh

# Run migration on snapshot
./scripts/run_migration.sh --database odoo_migration_test

# Validate data integrity
./scripts/validate_data_integrity.sh --database odoo_migration_test
```

**Validation Checks**:
- Record count comparison (pre/post)
- Financial balance verification
- Attachment integrity check
- User/permission validation

**Deliverables**:
- Data migration validated
- Integrity report generated
- Migration time measured

### 2.3 Integration Testing

**Objective**: Verify all external integrations work with Odoo 19.

```bash
# Test n8n integration
./scripts/test_n8n_integration.sh --target staging

# Test Mattermost integration
./scripts/test_mattermost_integration.sh --target staging

# Test MCP server connections
./scripts/test_mcp_connections.sh --target staging

# Test Supabase sync
./scripts/test_supabase_sync.sh --target staging
```

**Integration Test Matrix**:

| Integration | Endpoint | Test |
|-------------|----------|------|
| n8n | XML-RPC | Create/read/update records |
| n8n | REST API | Authentication, CRUD |
| Mattermost | Webhooks | Slash commands, notifications |
| MCP | JSON-RPC | Agent queries, tool calls |
| Supabase | PostgreSQL | Sync triggers, data flow |

**Deliverables**:
- Integration test report
- API compatibility confirmed
- Performance benchmarks

### 2.4 Load Testing

**Objective**: Verify Odoo 19 meets performance requirements.

```bash
# Run load test suite
./scripts/load_test.sh --target staging --users 50 --duration 30m

# Compare with baseline
./scripts/compare_performance.sh docs/PERFORMANCE_BASELINE_18.md
```

**Performance Targets**:
- Page load: ≤2s (P95)
- API response: ≤500ms (P95)
- Concurrent users: 50+
- Batch jobs: ≤10% regression

**Deliverables**:
- Load test report
- Performance comparison
- Optimization recommendations

### 2.5 User Acceptance Testing

**Objective**: Validate with representative users.

**UAT Checklist**:
- [ ] Login/logout flow
- [ ] Dashboard rendering
- [ ] Core workflows (quotes, orders, invoices)
- [ ] Reports generation
- [ ] Custom views/filters
- [ ] Mobile responsiveness

**Deliverables**:
- UAT sign-off
- Bug list (if any)
- User feedback

---

## Phase 3: Production Migration

### 3.1 Pre-Migration

**Objective**: Prepare production for migration.

```bash
# Announce maintenance window
./scripts/notify_maintenance.sh --start "2026-MM-DD 02:00 UTC" --duration "4h"

# Create production backup
./scripts/backup_production.sh --full

# Verify backup
./scripts/verify_backup.sh --latest
```

**Pre-Migration Checklist**:
- [ ] Maintenance window announced (48h advance)
- [ ] Full backup created and verified
- [ ] Rollback procedure tested
- [ ] On-call team assembled
- [ ] Monitoring dashboards ready

### 3.2 Migration Execution

**Objective**: Execute production migration.

```bash
# Stop production services
docker compose -f docker-compose.prod.yml down

# Run database migration
./scripts/run_migration.sh --database odoo_core --production

# Deploy Odoo 19 containers
docker compose -f docker-compose.prod.odoo19.yml up -d

# Run post-migration scripts
./scripts/post_migration.sh --production
```

**Migration Runbook**:

| Step | Command | Expected Duration | Rollback |
|------|---------|-------------------|----------|
| 1. Stop services | `docker compose down` | 2 min | N/A |
| 2. Backup | `pg_dump` | 30 min | N/A |
| 3. Schema migration | `odoo -u all` | 60 min | Restore backup |
| 4. Data migration | `./migrate_data.sh` | 45 min | Restore backup |
| 5. Start Odoo 19 | `docker compose up` | 5 min | Start Odoo 18 |
| 6. Verification | `./verify.sh` | 15 min | Rollback |

### 3.3 Post-Migration Verification

**Objective**: Verify production migration success.

```bash
# Health checks
./scripts/health_check.sh --production

# Integration verification
./scripts/verify_integrations.sh --production

# Smoke tests
./scripts/smoke_tests.sh --production

# Announce completion
./scripts/notify_completion.sh
```

**Verification Checklist**:
- [ ] All services healthy
- [ ] Database accessible
- [ ] User login working
- [ ] Core workflows functional
- [ ] Integrations connected
- [ ] Performance acceptable

### 3.4 Rollback Procedure

**If migration fails, execute rollback**:

```bash
# Stop Odoo 19
docker compose -f docker-compose.prod.odoo19.yml down

# Restore database backup
./scripts/restore_backup.sh --latest

# Start Odoo 18
docker compose -f docker-compose.prod.yml up -d

# Verify rollback
./scripts/health_check.sh --production
```

---

## Phase 4: Stabilization

### 4.1 Monitoring

**Objective**: Intensive monitoring for 30 days post-migration.

```bash
# Enhanced monitoring
./scripts/enable_enhanced_monitoring.sh

# Daily health reports
./scripts/daily_health_report.sh | mail -s "Odoo 19 Health Report" team@example.com
```

**Monitoring Dashboard**:
- Error rates
- Response times
- Database performance
- User activity
- Integration health

### 4.2 Bug Fixes

**Objective**: Rapid response to post-migration issues.

**Severity Response Times**:
- P0 (Critical): 1 hour
- P1 (High): 4 hours
- P2 (Medium): 24 hours
- P3 (Low): 1 week

### 4.3 Documentation Update

**Objective**: Update all documentation for Odoo 19.

```bash
# Update CLAUDE.md
sed -i 's/Odoo 18/Odoo 19/g' CLAUDE.md

# Update architecture docs
./scripts/update_docs.sh --version 19.0
```

**Documentation Updates**:
- CLAUDE.md version references
- API documentation
- Module documentation
- Deployment guides

### 4.4 Parallel Environment Decommission

**Objective**: Clean up Odoo 18 parallel environment.

```bash
# After 30 days, decommission Odoo 18
./scripts/decommission_odoo18.sh

# Archive final backup
./scripts/archive_backup.sh --tag "odoo18-final"
```

---

## Scripts to Create

| Script | Purpose |
|--------|---------|
| `scripts/audit_ipai_modules.py` | Module compatibility audit |
| `scripts/check_odoo_api_compat.py` | API compatibility checker |
| `scripts/migrate_module.sh` | Single module migration |
| `scripts/migrate_all_ipai_modules.sh` | Batch module migration |
| `scripts/run_migration.sh` | Database migration runner |
| `scripts/validate_data_integrity.sh` | Data validation |
| `scripts/test_*_integration.sh` | Integration test scripts |
| `scripts/load_test.sh` | Performance load testing |
| `scripts/health_check.sh` | Health verification |
| `scripts/rollback.sh` | Rollback procedure |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| OCA module not available | Fork and maintain internally |
| API breaking changes | Abstraction layer, early testing |
| Data corruption | Multiple backups, checksums |
| Extended downtime | Parallel environment, fast rollback |
| Performance regression | Load testing, optimization sprint |

---

## Success Criteria

Migration is successful when:

1. All 80+ IPAI modules passing tests on Odoo 19
2. All OCA dependencies on 19.0 branches
3. All integrations verified working
4. Performance meets or exceeds baselines
5. Zero P0/P1 bugs in first 7 days
6. User acceptance confirmed
7. Documentation updated

---

*Plan Version: 1.0*
*Last Updated: 2026-01-26*
