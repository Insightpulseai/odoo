# Odoo Module Rationalization System

**Purpose**: Systematic retirement of redundant `ipai_*` modules using evidence-based OCA validation

**Policy**: Config → OCA → Delta (ipai_*)

---

## Quick Start

```bash
# Complete workflow (all phases)
./scripts/execute_rationalization.sh

# Or run phases individually:
./scripts/install_baseline.sh              # Phase 1: Install CE + OCA
./scripts/generate_module_signatures.py    # Phase 3: Feature signatures
./scripts/odoo_rationalization.sh          # Phase 5: Footprint analysis
```

---

## System Architecture

### Components

1. **Baseline Installer** (`scripts/install_baseline.sh`)
   - Installs Odoo CE core modules
   - Installs OCA Must-Have modules (from PRD Appendix A)
   - Verifies installation health

2. **OCA Validation Engine** (`db/migrations/20260108_oca_validation.sql`)
   - PostgreSQL schema: `oca.module_index`, `oca.custom_module_signatures`, `oca.validation_results`
   - Feature signature matching with Jaccard similarity
   - Keyword extraction and model name overlap detection
   - Recommendation engine: KEEP / REDUCE / RETIRE

3. **Feature Signature Generator** (`scripts/generate_module_signatures.py`)
   - Extracts manifest summary, models, views, menus, actions
   - Generates keywords from all text fields
   - Computes signature hash for change detection
   - Stores in `oca.custom_module_signatures` table

4. **Footprint Analyzer** (`scripts/odoo_rationalization.sh`)
   - Counts menus, actions, views, models, fields, security rules
   - Flags UI-only modules (zero models/fields/security)
   - Generates dependency graph
   - Produces retire candidate list

5. **End-to-End Workflow** (`scripts/execute_rationalization.sh`)
   - Orchestrates all phases: Baseline → Signatures → Validation → Footprint → Backlog
   - Generates comprehensive final report
   - Produces prioritized retire backlog

### Data Flow

```
Odoo Database (ir_module_module, ir_model_data)
    ↓
Feature Signature Generator (Python)
    ↓
oca.custom_module_signatures (PostgreSQL)
    ↓
OCA Validation Engine (SQL Functions)
    ↓
oca.validation_results (match confidence, recommendations)
    ↓
Footprint Analyzer (SQL Queries)
    ↓
oca.module_footprints (is_ui_only flag)
    ↓
Retire Backlog (Prioritized List: RETIRE → REDUCE → KEEP)
```

---

## Decision Framework

### Recommendation Categories

| Category | Criteria | Action |
|----------|----------|--------|
| **RETIRE** | UI-only + OCA match ≥0.7 | Uninstall → Remove from filesystem |
| **REDUCE** | UI-only + OCA match ≥0.4 OR UI-heavy | Extract thin wrapper → Remove bloat |
| **KEEP** | Unique models/fields/security | Preserve as-is → Document justification |

### Priority Levels

1. **Priority 1**: RETIRE (UI-only + high OCA match ≥0.7) - **Safest to retire**
2. **Priority 2**: REDUCE (UI-only + medium OCA match ≥0.4)
3. **Priority 3**: REDUCE (UI-only, no OCA match - likely themes)
4. **Priority 4**: RETIRE (high OCA match ≥0.7, has models - data migration required)
5. **Priority 5**: REDUCE (medium OCA match ≥0.4, has models)
6. **Priority 6**: KEEP (unique business logic - no OCA equivalent)

---

## Validation Engine Details

### Feature Signature Structure

```json
{
  "module_name": "ipai_example",
  "manifest_summary": "Example module for demonstration",
  "model_names": ["ipai.example.model"],
  "view_titles": ["Example Form View", "Example List View"],
  "menu_labels": ["Example Menu", "Example Submenu"],
  "action_names": ["Example Action"],
  "keywords": ["example", "demonstration", "sample"],
  "signature_hash": "sha256..."
}
```

### OCA Module Index Schema

```sql
CREATE TABLE oca.module_index (
  name TEXT UNIQUE,           -- Module technical name
  repo TEXT,                  -- GitHub repository
  version TEXT,               -- Odoo version (18.0)
  summary TEXT,               -- Brief description
  keywords TEXT[],            -- Extracted keywords for matching
  category TEXT,              -- Functional category
  github_url TEXT             -- GitHub URL
);
```

### Validation Query

```sql
SELECT * FROM oca.validate_custom_module('ipai_example');
-- Returns:
-- oca_module | match_confidence | match_reason | matched_keywords | recommendation
```

### Batch Validation

```sql
SELECT * FROM oca.validate_all_custom_modules();
-- Returns summary:
-- custom_module | oca_matches | highest_confidence | recommendation
```

---

## Footprint Analysis

### Footprint Metrics

```sql
SELECT
  module_name,
  is_ui_only,          -- TRUE if no models/fields/security
  models,              -- Count of custom models
  fields,              -- Count of custom fields
  access_rules,        -- Count of ir.model.access records
  record_rules,        -- Count of ir.rule records
  menus + actions + views AS ui_elements
FROM oca.module_footprints
ORDER BY is_ui_only DESC, models;
```

### UI-Only Detection

```sql
-- Auto-computed generated column
is_ui_only BOOLEAN GENERATED ALWAYS AS (
  models = 0 AND fields = 0 AND access_rules = 0 AND record_rules = 0
) STORED
```

---

## Execution Workflow

### Phase 1: Install Baseline

```bash
./scripts/install_baseline.sh
```

**Installs**:
- CE baseline: base, web, mail, account, sale_management, purchase, stock, crm, project
- OCA Must-Have: account_financial_report, account_lock_date_update, account_fiscal_year, base_tier_validation, mass_editing, report_xlsx
- OCA Should-Have: sale_order_type, purchase_order_type, auditlog, web_responsive

**Verification**:
```sql
SELECT
  CASE
    WHEN name LIKE 'ipai_%' THEN 'Custom'
    WHEN author LIKE '%OCA%' THEN 'OCA'
    ELSE 'Core'
  END as category,
  COUNT(*) as count
FROM ir_module_module
WHERE state = 'installed'
GROUP BY category;
```

### Phase 2: Apply Validation Schema

```bash
# On local machine
psql "$POSTGRES_URL" -f db/migrations/20260108_oca_validation.sql

# Or on droplet
ssh root@178.128.112.214
docker exec odoo-erp-prod bash -c "
  psql -h db -U postgres -d odoo -f /tmp/oca_validation.sql
"
```

### Phase 3: Generate Feature Signatures

```bash
# Copy script to droplet
scp scripts/generate_module_signatures.py root@178.128.112.214:/tmp/

# Execute on droplet
ssh root@178.128.112.214
docker exec odoo-erp-prod bash -c "
  python3 /tmp/generate_module_signatures.py
"
```

**Output**: Feature signatures stored in `oca.custom_module_signatures`

### Phase 4: Run Validation

```sql
-- On droplet PostgreSQL
docker exec odoo-erp-prod bash -c "
  psql -h db -U postgres -d odoo -c '
    SELECT * FROM oca.validate_all_custom_modules()
    ORDER BY highest_confidence DESC;
  '
"
```

**Output**: Validation results stored in `oca.validation_results`

### Phase 5: Generate Footprint Analysis

```bash
./scripts/odoo_rationalization.sh
```

**Output**:
- `docs/rationalization/module_footprint.txt`
- `docs/rationalization/safe_retire_candidates.txt`
- `docs/rationalization/module_dependencies.txt`

### Phase 6: Generate Retire Backlog

```sql
-- Combined footprint + validation query
SELECT
  fp.module_name,
  CASE
    WHEN fp.is_ui_only AND MAX(vr.match_confidence) >= 0.7 THEN 'RETIRE (Priority 1)'
    WHEN fp.is_ui_only AND MAX(vr.match_confidence) >= 0.4 THEN 'REDUCE (Priority 2)'
    WHEN fp.is_ui_only THEN 'REDUCE (Priority 3)'
    WHEN MAX(vr.match_confidence) >= 0.7 THEN 'RETIRE (Priority 4)'
    WHEN MAX(vr.match_confidence) >= 0.4 THEN 'REDUCE (Priority 5)'
    ELSE 'KEEP (Priority 6)'
  END AS recommendation,
  fp.models,
  fp.fields,
  MAX(vr.match_confidence) AS oca_match,
  (SELECT oca_module FROM oca.validation_results
   WHERE custom_module = fp.module_name
   ORDER BY match_confidence DESC LIMIT 1) AS best_oca_match
FROM oca.module_footprints fp
LEFT JOIN oca.validation_results vr ON fp.module_name = vr.custom_module
GROUP BY fp.module_name, fp.is_ui_only, fp.models, fp.fields
ORDER BY
  CASE
    WHEN fp.is_ui_only AND MAX(vr.match_confidence) >= 0.7 THEN 1
    ELSE 6
  END;
```

---

## Retirement Execution

### Priority 1: RETIRE (Safest)

```bash
# For each Priority 1 module (UI-only + high OCA match):
MODULE="ipai_example_ui_only"

# 1. Verify no dependencies
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"
  psql -h db -U postgres -d odoo -c \\\"
    SELECT m.name
    FROM ir_module_module m
    INNER JOIN ir_module_module_dependency md ON m.id = md.module_id
    WHERE md.name = '$MODULE' AND m.state = 'installed';
  \\\"
\""

# 2. Uninstall module
ssh root@178.128.112.214 "docker exec odoo-erp-prod odoo -d odoo -u $MODULE --stop-after-init"

# 3. Remove from filesystem
rm -rf addons/ipai/$MODULE

# 4. Commit change
git add addons/ipai/
git commit -m "chore: retire redundant module $MODULE (replaced by OCA)"

# 5. Verify system health
ssh root@178.128.112.214 "docker exec odoo-erp-prod odoo -d odoo --stop-after-init"
```

### Priority 2-3: REDUCE

```bash
# For UI-heavy modules:
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

```bash
# For modules with data:
MODULE="ipai_example_with_data"
OCA_MODULE="oca_equivalent"

# 1. Export data
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"
  psql -h db -U postgres -d odoo -c \\\"
    COPY (SELECT * FROM ${MODULE}_table) TO '/tmp/${MODULE}_data.csv' CSV HEADER;
  \\\"
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

---

## Health Checks

### After Each Retirement

```bash
# 1. Database health
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"
  psql -h db -U postgres -d odoo -c 'SELECT 1;'
\""

# 2. Module registry sanity
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"
  psql -h db -U postgres -d odoo -c \\\"
    SELECT state, COUNT(*) FROM ir_module_module
    WHERE name LIKE 'ipai_%' GROUP BY state;
  \\\"
\""

# 3. Server boots clean
ssh root@178.128.112.214 "docker exec odoo-erp-prod odoo -d odoo --stop-after-init"

# 4. UI accessibility test
curl -I https://erp.insightpulseai.com
```

---

## Troubleshooting

### Issue: Module dependencies prevent uninstall

**Symptoms**: "Module X depends on module Y" error

**Solution**:
```sql
-- Find all dependencies
SELECT m.name, md.name AS depends_on
FROM ir_module_module m
INNER JOIN ir_module_module_dependency md ON m.id = md.module_id
WHERE md.name = 'problematic_module' AND m.state = 'installed';

-- Retire dependents first, then retry
```

### Issue: OCA module not found

**Symptoms**: "Module not found in addons path"

**Solution**:
```bash
# Verify OCA addons_path in odoo.conf
ssh root@178.128.112.214 "docker exec odoo-erp-prod cat /etc/odoo/odoo.conf | grep addons_path"

# Update module list
ssh root@178.128.112.214 "docker exec odoo-erp-prod odoo -d odoo -u base --stop-after-init"
```

### Issue: Data loss during migration

**Symptoms**: Records missing after retirement

**Solution**:
```bash
# Always backup before retirement
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"
  pg_dump -h db -U postgres odoo > /backup/odoo_before_retirement_\$(date +%Y%m%d).sql
\""

# Test retirement in staging first
# Verify data integrity with SQL queries
```

---

## References

- **PRD**: `spec/*/prd-odoo-module-pipeline*.md` (OCA validation specification)
- **OCA Community**: https://odoo-community.org/oca-for-functional-consultants
- **GitHub**: https://github.com/OCA
- **Odoo Apps Store**: https://apps.odoo.com/apps (search for OCA modules)

---

**Last Updated**: 2026-01-08
**Maintainer**: Jake Tolentino <business@insightpulseai.com>
**Policy**: Config → OCA → Delta (ipai_*)
