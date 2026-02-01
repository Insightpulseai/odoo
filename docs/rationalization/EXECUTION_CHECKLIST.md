# Odoo Module Rationalization - Execution Checklist

**Status**: ✅ All scripts and documentation complete - Ready for execution

**Date**: 2026-01-08
**System**: Odoo CE 18.0 on droplet 178.128.112.214

---

## Pre-Execution Requirements

### 1. Backup Current State
```bash
# Database backup
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  pg_dump -h db -U postgres odoo > /backup/odoo_before_rationalization_\$(date +%Y%m%d).sql\
\""

# Addons backup
ssh root@178.128.112.214 "tar -czf /backup/addons_ipai_\$(date +%Y%m%d).tar.gz /opt/odoo-ce/repo/addons/ipai/"
```

**Verification**: ✅ Backup files created
**Rollback plan**: Restore from backup if issues detected

### 2. Verify System Health
```bash
# Check Odoo is running
ssh root@178.128.112.214 "docker exec odoo-erp-prod odoo -d odoo --stop-after-init"

# Check database connection
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo -c 'SELECT COUNT(*) FROM ir_module_module WHERE state='\''installed'\'''\
\""
```

**Verification**: ✅ Odoo boots cleanly, database accessible
**Blocker**: If Odoo fails to start, fix before proceeding

### 3. Remove Invalid Module (Hard Blocker)
```bash
# Already completed - verify removal
ls addons/ipai/ipai_month_end_closing.backup
# Should return: No such file or directory
```

**Status**: ✅ Completed - invalid module removed

---

## Execution Phases

### Phase 1: Baseline Installation (30-45 minutes)

**Script**: `./scripts/install_baseline.sh`

**What it does**:
- Installs Odoo CE core modules (base, web, mail, account, etc.)
- Installs OCA Must-Have modules from PRD Appendix A
- Installs OCA Should-Have modules (optional enhancements)
- Runs health checks and verification

**Verification checkpoints**:
```bash
# 1. Check module installation status
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo -c '\
    SELECT
      CASE
        WHEN name LIKE '\''ipai_%'\'' THEN '\''Custom'\''
        WHEN author LIKE '\''%OCA%'\'' THEN '\''OCA'\''
        ELSE '\''Core'\''
      END as category,
      COUNT(*) as count
    FROM ir_module_module
    WHERE state = '\''installed'\''
    GROUP BY category;\
  '\
\""

# 2. Server boot test
ssh root@178.128.112.214 "docker exec odoo-erp-prod odoo -d odoo --stop-after-init"
```

**Expected outcome**:
- Core: ~15-20 modules
- OCA: ~10 modules
- Custom: Existing ipai_* modules (unchanged)

**Rollback**: None needed - additive only

### Phase 2: OCA Validation Schema (5 minutes)

**Migration**: `db/migrations/20260108_oca_validation.sql`

**What it does**:
- Creates `oca` schema with 4 tables:
  - `oca.module_index` - OCA module catalog
  - `oca.custom_module_signatures` - ipai_* feature signatures
  - `oca.validation_results` - Matching results
  - `oca.module_footprints` - Footprint cache
- Installs validation functions (Jaccard similarity, etc.)
- Seeds OCA module index from PRD Appendix A

**Execution**:
```bash
# On local machine
ssh root@178.128.112.214 "cat > /tmp/oca_validation.sql" < db/migrations/20260108_oca_validation.sql

# Apply migration
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo -f /tmp/oca_validation.sql\
\""
```

**Verification**:
```bash
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo -c 'SELECT COUNT(*) FROM oca.module_index;'\
\""
# Should return: 10 (OCA modules from PRD)
```

**Rollback**: `DROP SCHEMA oca CASCADE;`

### Phase 3: Feature Signature Generation (10-15 minutes)

**Script**: `scripts/generate_module_signatures.py`

**What it does**:
- Queries Odoo database for all installed ipai_* modules
- Extracts feature signatures:
  - Manifest summary
  - Model names
  - View titles
  - Menu labels
  - Action names
  - Keywords (extracted from text)
- Stores in `oca.custom_module_signatures`

**Execution**:
```bash
# Copy script to droplet
scp scripts/generate_module_signatures.py root@178.128.112.214:/tmp/

# Execute on droplet
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  export POSTGRES_HOST=db
  export POSTGRES_PORT=5432
  export POSTGRES_DB=odoo
  export POSTGRES_USER=postgres
  export POSTGRES_PASSWORD=\\\$PGPASSWORD

  python3 /tmp/generate_module_signatures.py\
\""
```

**Verification**:
```bash
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo -c 'SELECT COUNT(*) FROM oca.custom_module_signatures;'\
\""
# Should return: Number of installed ipai_* modules
```

**Rollback**: `TRUNCATE oca.custom_module_signatures;`

### Phase 4: OCA Validation Matching (5 minutes)

**What it does**:
- Runs `oca.validate_all_custom_modules()` function
- Matches each ipai_* module against OCA index
- Computes Jaccard similarity scores
- Generates KEEP/REDUCE/RETIRE recommendations

**Execution**:
```bash
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo -c '\
    SELECT * FROM oca.validate_all_custom_modules()\
    ORDER BY highest_confidence DESC;\
  '\
\""
```

**Verification**:
```bash
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo -c 'SELECT COUNT(*) FROM oca.validation_results;'\
\""
# Should return: Number of matches found (varies)
```

**Review**: Check validation_results table for match quality

### Phase 5: Footprint Analysis (10 minutes)

**What it does**:
- Counts menus, actions, views, models, fields, security rules per module
- Flags UI-only modules (zero models/fields/security)
- Stores in `oca.module_footprints`

**Execution**:
```bash
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo -c '\
    INSERT INTO oca.module_footprints (module_name, menus, actions, views, models, fields, access_rules, record_rules)
    SELECT
      imd.module,
      sum((imd.model = '\''ir.ui.menu'\'')::int),
      sum((imd.model = '\''ir.actions.act_window'\'')::int),
      sum((imd.model = '\''ir.ui.view'\'')::int),
      sum((imd.model = '\''ir.model'\'')::int),
      sum((imd.model = '\''ir.model.fields'\'')::int),
      sum((imd.model = '\''ir.model.access'\'')::int),
      sum((imd.model = '\''ir.rule'\'')::int)
    FROM ir_model_data imd
    WHERE imd.module LIKE '\''ipai_%'\''
    GROUP BY imd.module
    ON CONFLICT (module_name) DO UPDATE SET
      menus = EXCLUDED.menus,
      actions = EXCLUDED.actions,
      views = EXCLUDED.views,
      models = EXCLUDED.models,
      fields = EXCLUDED.fields,
      access_rules = EXCLUDED.access_rules,
      record_rules = EXCLUDED.record_rules,
      analyzed_at = NOW();
  '\
\""
```

**Verification**:
```bash
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo -c 'SELECT * FROM oca.module_footprints ORDER BY is_ui_only DESC, models, module_name;'\
\""
```

**Review**: Identify UI-only modules (is_ui_only = TRUE)

### Phase 6: Retire Backlog Generation (5 minutes)

**What it does**:
- Combines footprint analysis + OCA validation
- Generates prioritized RETIRE/REDUCE/KEEP recommendations
- Outputs 6 priority levels

**Execution**:
```bash
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo -c '\
    WITH combined AS (
      SELECT
        fp.module_name,
        fp.is_ui_only,
        fp.models,
        fp.fields,
        fp.access_rules,
        fp.record_rules,
        COALESCE(MAX(vr.match_confidence), 0) AS oca_match_confidence,
        COALESCE((SELECT recommendation FROM oca.validation_results WHERE custom_module = fp.module_name ORDER BY match_confidence DESC LIMIT 1), '\''KEEP'\'') AS recommendation,
        COALESCE((SELECT oca_module FROM oca.validation_results WHERE custom_module = fp.module_name ORDER BY match_confidence DESC LIMIT 1), '\'\'\'') AS best_oca_match
      FROM oca.module_footprints fp
      LEFT JOIN oca.validation_results vr ON fp.module_name = vr.custom_module
      GROUP BY fp.module_name, fp.is_ui_only, fp.models, fp.fields, fp.access_rules, fp.record_rules
    )
    SELECT
      module_name,
      CASE
        WHEN is_ui_only AND oca_match_confidence >= 0.7 THEN '\''RETIRE (UI-only + high OCA match)'\''
        WHEN is_ui_only AND oca_match_confidence >= 0.4 THEN '\''REDUCE (UI-only + medium OCA match)'\''
        WHEN is_ui_only THEN '\''REDUCE (UI-only, no OCA match)'\''
        WHEN oca_match_confidence >= 0.7 THEN '\''RETIRE (high OCA match)'\''
        WHEN oca_match_confidence >= 0.4 THEN '\''REDUCE (medium OCA match)'\''
        ELSE '\''KEEP (unique business logic)'\''
      END AS final_recommendation,
      is_ui_only,
      models,
      fields,
      oca_match_confidence,
      best_oca_match
    FROM combined
    ORDER BY
      CASE
        WHEN is_ui_only AND oca_match_confidence >= 0.7 THEN 1
        WHEN is_ui_only AND oca_match_confidence >= 0.4 THEN 2
        WHEN is_ui_only THEN 3
        WHEN oca_match_confidence >= 0.7 THEN 4
        WHEN oca_match_confidence >= 0.4 THEN 5
        ELSE 6
      END,
      module_name;\
  '\
\" | tee docs/rationalization/retire_backlog.txt"
```

**Output**: `docs/rationalization/retire_backlog.txt`

**Review**: Manual review required before execution

### Phase 7: Final Report Generation (2 minutes)

**What it does**:
- Generates comprehensive markdown report
- Summarizes findings and recommendations
- Provides execution plan for each priority level

**Execution**: Automatic - part of workflow script

**Output**: `docs/rationalization/FINAL_RATIONALIZATION_REPORT.md`

**Review**: Business approval required

---

## Automated Execution (All Phases)

**Single-command execution**:
```bash
./scripts/execute_rationalization.sh
```

**Duration**: ~60-90 minutes total

**Outputs**:
- `docs/rationalization/validation_results.txt`
- `docs/rationalization/footprint_analysis.txt`
- `docs/rationalization/retire_backlog.txt`
- `docs/rationalization/FINAL_RATIONALIZATION_REPORT.md`

**Safety**: Script creates marker file `.baseline_installed` to prevent re-running baseline

---

## Post-Execution Review

### 1. Review Reports

**Priority 1 modules (safest to retire)**:
```bash
grep "RETIRE (UI-only + high OCA match)" docs/rationalization/retire_backlog.txt
```

**Review criteria**:
- ✅ Zero models/fields/security (UI-only)
- ✅ OCA match confidence ≥ 0.7
- ✅ OCA module identified and installable
- ✅ No dependencies from other modules

### 2. Business Approval

**Stakeholder review required for**:
- All Priority 1 modules (before retirement)
- Priority 2-3 modules (thin wrapper strategy)
- Priority 4 modules (data migration required)

**Approval checklist**:
- [ ] Functionality covered by OCA module verified
- [ ] No custom business logic lost
- [ ] User workflows unaffected
- [ ] Documentation updated
- [ ] Training plan (if needed)

### 3. Staging Environment Testing

**Before production retirement**:
```bash
# Clone production database to staging
# Run retirement workflow on staging
# Verify no breakage for 48 hours
# Get user acceptance testing
```

---

## Module Retirement Execution

### Priority 1: RETIRE (Safest - UI-only + high OCA match)

**For each Priority 1 module**:

```bash
MODULE="ipai_example_ui_only"

# 1. Verify no dependencies
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo -c '\
    SELECT m.name
    FROM ir_module_module m
    INNER JOIN ir_module_module_dependency md ON m.id = md.module_id
    WHERE md.name = '\''$MODULE'\'' AND m.state = '\''installed'\'';\
  '\
\""

# 2. Uninstall module
ssh root@178.128.112.214 "docker exec odoo-erp-prod odoo -d odoo -u $MODULE --stop-after-init"

# 3. Verify uninstall success
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo -c '\
    SELECT state FROM ir_module_module WHERE name = '\''$MODULE'\'';\
  '\
\""
# Should return: uninstalled

# 4. Remove from filesystem
rm -rf addons/ipai/$MODULE

# 5. Commit change
git add addons/ipai/
git commit -m "chore: retire redundant module $MODULE (replaced by OCA)"

# 6. Verify system health
ssh root@178.128.112.214 "docker exec odoo-erp-prod odoo -d odoo --stop-after-init"
```

**Verification**: Odoo boots cleanly, no errors in logs

### Priority 2-3: REDUCE (UI-heavy modules)

**Strategy**: Create thin wrapper, remove UI bloat

```bash
MODULE="ipai_example_ui_heavy"

# 1. Create new lite module
mkdir addons/ipai/${MODULE}_lite

# 2. Copy only essential business logic
cp addons/ipai/$MODULE/models/*.py addons/ipai/${MODULE}_lite/models/
cp addons/ipai/$MODULE/security/*.csv addons/ipai/${MODULE}_lite/security/

# 3. Create minimal manifest
cat > addons/ipai/${MODULE}_lite/__manifest__.py <<EOF
{
    'name': 'Example Lite',
    'version': '18.0.1.0.0',
    'depends': ['base', 'oca_equivalent_module'],
    'data': ['security/ir.model.access.csv'],
}
EOF

# 4. Test in staging
ssh root@178.128.112.214 "docker exec odoo-erp-prod odoo -d odoo -i ${MODULE}_lite --stop-after-init"

# 5. After validation, retire original
# (Follow Priority 1 steps for original module)
```

### Priority 4: RETIRE with Data Migration

**Strategy**: Migrate data to OCA module first

```bash
MODULE="ipai_example_with_data"
OCA_MODULE="oca_equivalent"

# 1. Export data
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo -c '\
    COPY (SELECT * FROM ${MODULE}_table) TO '\''/tmp/${MODULE}_data.csv'\'' CSV HEADER;\
  '\
\""

# 2. Install OCA module
ssh root@178.128.112.214 "docker exec odoo-erp-prod odoo -d odoo -i $OCA_MODULE --stop-after-init"

# 3. Migrate data (custom SQL script)
# ... data transformation logic ...

# 4. Verify data integrity
# ... validation queries ...

# 5. Uninstall custom module
ssh root@178.128.112.214 "docker exec odoo-erp-prod odoo -d odoo -u $MODULE --stop-after-init"

# 6. Remove from filesystem
rm -rf addons/ipai/$MODULE
```

**Critical**: Always verify data integrity before removing custom module

---

## Health Checks (After Each Retirement)

```bash
# 1. Database health
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo -c 'SELECT 1;'\
\""

# 2. Module registry sanity
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo -c '\
    SELECT state, COUNT(*) FROM ir_module_module
    WHERE name LIKE '\''ipai_%'\'' GROUP BY state;\
  '\
\""

# 3. Server boots clean
ssh root@178.128.112.214 "docker exec odoo-erp-prod odoo -d odoo --stop-after-init"

# 4. UI accessibility test
curl -I https://erp.insightpulseai.com
```

**All checks must pass** before proceeding to next module

---

## Rollback Procedures

### If Odoo fails to start
```bash
# 1. Restore database from backup
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo < /backup/odoo_before_rationalization_YYYYMMDD.sql\
\""

# 2. Restore addons from backup
ssh root@178.128.112.214 "tar -xzf /backup/addons_ipai_YYYYMMDD.tar.gz -C /opt/odoo-ce/repo/addons/"

# 3. Restart Odoo
ssh root@178.128.112.214 "docker restart odoo-erp-prod"
```

### If specific module causes issues
```bash
# Re-install module from git history
git checkout HEAD~1 -- addons/ipai/$MODULE

# Re-install in Odoo
ssh root@178.128.112.214 "docker exec odoo-erp-prod odoo -d odoo -i $MODULE --stop-after-init"
```

---

## Success Criteria

### Overall Goals
- [ ] All Priority 1 modules retired (UI-only + high OCA match)
- [ ] Priority 2-3 modules reduced to thin wrappers
- [ ] Priority 4 modules migrated to OCA equivalents
- [ ] Zero UI-only modules remaining
- [ ] OCA coverage documented for all kept modules
- [ ] Baseline validation passes all health checks

### Metrics
- **Module Count Reduction**: Target 20-30% reduction in ipai_* modules
- **Code Maintainability**: Reduced custom code footprint
- **OCA Adoption**: Increased use of community-maintained modules
- **System Health**: Zero regressions in core functionality

### Documentation Updates
- [ ] Update module dependency tree
- [ ] Document OCA module replacements
- [ ] Update user guides (if needed)
- [ ] Update developer documentation

---

## Timeline Estimate

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Pre-Execution (Backup) | 15 min | 15 min |
| Phase 1: Baseline Install | 30-45 min | 45-60 min |
| Phase 2: Schema Migration | 5 min | 50-65 min |
| Phase 3: Signature Generation | 10-15 min | 60-80 min |
| Phase 4: Validation Matching | 5 min | 65-85 min |
| Phase 5: Footprint Analysis | 10 min | 75-95 min |
| Phase 6: Retire Backlog | 5 min | 80-100 min |
| Phase 7: Report Generation | 2 min | 82-102 min |
| **Review & Approval** | 1-2 days | - |
| Module Retirements (Priority 1) | Varies | - |

**Total automated execution**: ~80-100 minutes

**Total project duration**: 1-2 weeks (including review and staged retirements)

---

## Contact & Support

**Project Owner**: Jake Tolentino
**Documentation**: `docs/rationalization/README.md`
**Scripts**: `scripts/execute_rationalization.sh`
**Policy**: Config → OCA → Delta (ipai_*)

**References**:
- OCA Community: https://odoo-community.org
- PRD: `spec/*/prd-odoo-module-pipeline*.md`
- GitHub: https://github.com/OCA

---

**Last Updated**: 2026-01-08
**Status**: ✅ Ready for execution
