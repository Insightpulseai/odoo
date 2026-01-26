# Odoo 19 Migration Strategy for odoo-ce

---

**Purpose**: Document the strategy for integrating Odoo 19 features into odoo-ce (currently Odoo 18 CE).

**Last Updated**: 2026-01-26
**Current Version**: Odoo 18 CE
**Target Version**: Odoo 19 CE (when released)

---

## Current State (Odoo 18 CE)

**Stack**: `~/Documents/GitHub/odoo-ce/`
- **Odoo Version**: 18.0 Community Edition
- **Architecture**: Multi-edition (core, marketing, accounting)
- **Custom Modules**: 80+ IPAI modules (`addons/ipai/`)
- **OCA Integration**: 24+ OCA dependencies (`addons/oca/`)
- **Enterprise Parity**: `ipai_enterprise_bridge` module (EE → CE alternatives)

**Key Components**:
```
odoo-ce/
├── addons/
│   ├── ipai/                  # 80+ custom modules (18.0)
│   │   ├── ipai_enterprise_bridge/  # EE parity module
│   │   ├── ipai_finance_ppm/        # Finance PPM
│   │   ├── ipai_workspace_core/     # Workspace
│   │   └── ...
│   └── oca/                   # OCA modules (18.0)
├── docker-compose.yml         # Multi-edition stack
└── CLAUDE.md                  # Project orchestration rules
```

---

## Migration Options (Odoo 19 Integration)

### Option 1: Direct Upgrade (Canonical Path)

**Strategy**: Upgrade entire odoo-ce stack from 18.0 → 19.0 when Odoo 19 CE is released.

**Process**:
```bash
# 1. Wait for Odoo 19 CE official release
# Expected: Q2-Q3 2026 (based on historical release cycles)

# 2. Update base image
# Dockerfile
FROM odoo:19.0

# 3. Update all IPAI modules
# addons/ipai/*/__manifest__.py
{
    "version": "19.0.1.0.0",  # 18.0.1.0.0 → 19.0.1.0.0
}

# 4. Update OCA dependencies
# oca.lock.json
{
    "version": "19.0",  # 18.0 → 19.0
    "repositories": [...]
}

# 5. Run migration scripts
./scripts/migrate/odoo_18_to_19.sh

# 6. Test in dev sandbox first
cd ~/Documents/GitHub/odoo-ce/sandbox/dev/
docker compose down && docker compose up -d
# Validate all modules install

# 7. Deploy to production
./scripts/deploy-odoo-modules.sh
```

**Timeline**: 3-6 months after Odoo 19 CE release

**Risks**:
- Breaking changes in Odoo 19 API
- OCA modules may not be ready immediately
- Custom modules need migration
- Multi-edition stack complexity

**Mitigations**:
- Parallel dev/prod environments (18 + 19)
- Gradual module migration (prioritize critical modules)
- Comprehensive testing (CI/CD gates)
- Rollback plan (Docker image tags)

---

### Option 2: Enterprise Bridge (Odoo 19 Features → Odoo 18 CE)

**Strategy**: Backport Odoo 19 EE features to Odoo 18 CE via `ipai_enterprise_bridge`.

**Current Enterprise Bridge Capabilities**:
- **Email**: Mailgun SMTP (replaces IAP email)
- **OAuth**: Google/Azure AD (replaces EE OAuth)
- **IoT**: MQTT bridge (replaces EE IoT subscription)

**Odoo 19 Features to Backport** (examples):
```python
# addons/ipai/ipai_enterprise_bridge_19/__manifest__.py
{
    "name": "IPAI Enterprise Bridge 19",
    "version": "18.0.1.0.0",  # Still on Odoo 18 base
    "depends": ["ipai_enterprise_bridge"],
    "description": """
        Backport Odoo 19 Enterprise features to Odoo 18 CE:
        - New accounting features (if applicable)
        - Enhanced project management (if applicable)
        - Improved UI/UX patterns (if applicable)
    """,
}
```

**Implementation**:
1. Monitor Odoo 19 EE release notes
2. Identify valuable enterprise features
3. Implement CE-compatible alternatives
4. Maintain on Odoo 18 base (delay 19 upgrade)

**Benefits**:
- Get Odoo 19 features without full migration
- Control migration timeline
- Maintain stability on 18

**Limitations**:
- Only works for backportable features (not core changes)
- Requires ongoing maintenance
- May lag behind official releases

---

### Option 3: Selective Module Migration (Hybrid Approach)

**Strategy**: Run Odoo 18 + Odoo 19 in parallel, migrate modules gradually.

**Architecture**:
```
┌─────────────────────────────────────────────────────────────┐
│                     Multi-Version Stack                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Odoo 18 CE (Core)          Odoo 19 CE (New Modules)       │
│   ├── Production modules     ├── Experimental modules       │
│   ├── OCA 18.0               ├── OCA 19.0                   │
│   └── Database: odoo_18      └── Database: odoo_19          │
│                                                              │
│   Shared:                                                    │
│   ├── PostgreSQL 16 (single instance, separate DBs)         │
│   ├── n8n workflows (version-agnostic)                      │
│   └── Apache Superset (queries both DBs)                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Docker Compose**:
```yaml
# docker-compose.yml
services:
  odoo-18:
    image: odoo:18.0
    container_name: odoo-core-18
    ports:
      - "8069:8069"
    environment:
      - DB_NAME=odoo_18
      - HOST=postgres

  odoo-19:
    image: odoo:19.0
    container_name: odoo-core-19
    ports:
      - "8169:8069"  # Different port
    environment:
      - DB_NAME=odoo_19
      - HOST=postgres

  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
```

**Migration Workflow**:
```bash
# 1. Create new module in Odoo 19
cd ~/Documents/GitHub/odoo-ce/addons/ipai/
cp -r ipai_new_module_18/ ipai_new_module_19/

# Edit manifest
# __manifest__.py
{
    "version": "19.0.1.0.0",
    "installable": True,
}

# 2. Test in Odoo 19 container
docker compose exec odoo-19 odoo -d odoo_19 -i ipai_new_module_19 --stop-after-init

# 3. Validate compatibility
./scripts/verify.sh --version 19

# 4. Promote to production Odoo 19 instance
# (when ready to migrate full stack)
```

**Benefits**:
- Zero-risk experimentation
- Learn Odoo 19 while maintaining 18
- Gradual team training
- Independent module evolution

**Drawbacks**:
- Higher infrastructure costs (2x containers)
- Increased complexity (2 versions to maintain)
- Data synchronization challenges (if needed)

---

## Recommended Strategy

**Phase 1: Preparation (Now - Q2 2026)**
- ✅ Monitor Odoo 19 release announcements
- ✅ Create spec bundle: `spec/odoo-19-migration/`
- ✅ Audit IPAI modules for 19 compatibility
- ✅ Test OCA modules in Odoo 19 preview (if available)
- ✅ Update `ipai_enterprise_bridge` for any Odoo 19 EE features

**Phase 2: Pilot (Q2-Q3 2026)**
- ⏳ Set up parallel Odoo 19 dev sandbox
- ⏳ Migrate 3-5 non-critical modules
- ⏳ Validate CI/CD pipelines
- ⏳ Train team on Odoo 19 changes

**Phase 3: Migration (Q3-Q4 2026)**
- ⏳ Migrate all IPAI modules (80+)
- ⏳ Update OCA dependencies
- ⏳ Run full test suite (CI/CD gates)
- ⏳ Deploy to staging environment

**Phase 4: Production (Q4 2026)**
- ⏳ Production deployment (Odoo 18 → 19)
- ⏳ Monitor for regressions
- ⏳ Rollback plan ready (Docker image tags)
- ⏳ Post-migration audit

---

## Breaking Changes to Watch (Odoo 19)

**Typical Breaking Changes** (based on historical Odoo upgrades):

### API Changes
```python
# Example: Odoo 18 → 19 (hypothetical)

# Odoo 18 (old)
self.env['res.partner'].search([('name', '=', 'Test')])

# Odoo 19 (new - if API changes)
self.env['res.partner'].browse([('name', '=', 'Test')])
```

### XML View Changes
```xml
<!-- Odoo 18 -->
<field name="view_mode">list,form</field>

<!-- Odoo 19 (hypothetical new syntax) -->
<field name="view_mode" type="list,form"/>
```

### Migration Scripts Required
```python
# addons/ipai/ipai_finance_ppm/migrations/19.0.1.0.0/pre-migrate.py

def migrate(cr, version):
    """Migrate Finance PPM from 18.0 to 19.0"""
    # Update deprecated fields
    cr.execute("""
        UPDATE ir_model_fields
        SET deprecated = TRUE
        WHERE model = 'ipai.finance.bir_schedule'
        AND name = 'old_field_name'
    """)
```

---

## Testing Strategy

### Unit Tests
```bash
# Test all IPAI modules in Odoo 19
./scripts/ci/run_odoo_tests.sh --version 19

# Expected: All tests pass or documented failures
```

### Integration Tests
```bash
# Test critical workflows
./scripts/ci/integration_tests.sh --workflow "BIR filing"
./scripts/ci/integration_tests.sh --workflow "Month-end close"
```

### Visual Parity
```bash
# Ensure UI consistency (18 → 19)
./scripts/snap.js --version 19 --routes "/expenses,/tasks"
./scripts/ssim.js --baseline odoo-18 --compare odoo-19
```

### Performance Benchmarks
```bash
# Compare performance (18 vs 19)
./scripts/benchmark.sh --version 18 > results_18.json
./scripts/benchmark.sh --version 19 > results_19.json
diff results_18.json results_19.json
```

---

## Rollback Plan

**Scenario**: Odoo 19 migration fails in production

**Rollback Steps**:
```bash
# 1. Stop Odoo 19 containers
docker compose down

# 2. Restore Odoo 18 image
docker compose --profile odoo-18 up -d

# 3. Restore database snapshot
psql "$POSTGRES_URL" -f backups/odoo_18_pre_migration.sql

# 4. Verify services
./scripts/verify.sh --version 18

# 5. Notify stakeholders
curl -X POST "$MATTERMOST_WEBHOOK_URL" \
  -d '{"text": "⚠️ Rolled back to Odoo 18 due to migration issues"}'
```

**Rollback Criteria**:
- Critical workflow broken (BIR filing, month-end close)
- Data loss detected
- Performance degradation >50%
- Visual parity SSIM <0.95

---

## Cost Estimate

**Development Effort**:
- Module migration: 80 modules × 2 hours = 160 hours
- Testing: 40 hours
- Documentation: 20 hours
- Training: 10 hours
- **Total**: 230 hours (~6 weeks for 1 developer)

**Infrastructure**:
- Parallel environments (dev + staging): +$200/month
- Production downtime: 4-8 hours (weekend deployment)

**Risk Budget**:
- Rollback scenarios: 20 hours
- Bug fixes post-migration: 40 hours

---

## Acceptance Criteria

**Pre-Migration**:
- ✅ All IPAI modules have 19.0 manifests
- ✅ OCA dependencies available for 19.0
- ✅ Spec bundle complete (`spec/odoo-19-migration/`)
- ✅ Rollback plan documented and tested

**Post-Migration**:
- ✅ All CI/CD gates pass (47 workflows)
- ✅ Visual parity SSIM ≥0.97 (mobile), ≥0.98 (desktop)
- ✅ BIR compliance workflows functional (1601-C, 2550Q)
- ✅ Month-end close completes in <5 business days
- ✅ Zero data loss (validated via audit scripts)
- ✅ Performance benchmarks within 10% of Odoo 18

---

## Related Documentation

**Spec Bundles**:
- `spec/odoo-19-migration/` - Complete migration spec (to be created)
- `spec/ipai-enterprise-bridge/` - Enterprise parity features

**Migration Scripts**:
- `scripts/migrate/odoo_18_to_19.sh` - Main migration script
- `addons/ipai/*/migrations/19.0.*/` - Per-module migrations

**Testing**:
- `.github/workflows/odoo-19-ci.yml` - Odoo 19 CI pipeline
- `scripts/benchmark.sh` - Performance benchmarks

---

## Next Steps

1. ✅ Document migration strategy (this file)
2. ⏳ Create spec bundle: `spec/odoo-19-migration/prd.md`
3. ⏳ Monitor Odoo 19 release announcements
4. ⏳ Set up Odoo 19 dev sandbox (when released)
5. ⏳ Pilot migration with 3-5 modules
6. ⏳ Full migration (Q3-Q4 2026)

---

**Status**: PLANNING - Odoo 19 CE not yet released
**Owner**: Jake Tolentino
**Timeline**: 6-12 months post Odoo 19 release
