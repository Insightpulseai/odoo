#!/usr/bin/env bash
###############################################################################
# Odoo Baseline-First Rationalization
# Analyzes custom ipai_* modules to identify redundancy with core/OCA
###############################################################################

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DROPLET_IP="${DROPLET_IP:-178.128.112.214}"
DB="${ODOO_DB:-odoo}"
OUTPUT_DIR="docs/rationalization"

echo "================================================================================"
echo "Odoo Baseline-First Rationalization"
echo "================================================================================"
echo ""
echo "Database: $DB"
echo "Droplet: $DROPLET_IP"
echo "Output: $OUTPUT_DIR"
echo ""

mkdir -p "$OUTPUT_DIR"

###############################################################################
# 1. Hard-stop on invalid module names
###############################################################################
echo "1. Checking for invalid module names..."

if find addons -maxdepth 3 -type d -name "*.backup" | grep -q .; then
    echo -e "${RED}ERROR: Found invalid module folder names with dots:${NC}"
    find addons -maxdepth 3 -type d -name "*.backup"
    echo ""
    echo "Odoo module names cannot contain dots. Rename or remove these folders."
    exit 1
fi

echo -e "${GREEN}✓ No invalid module names found${NC}"
echo ""

###############################################################################
# 2. Generate custom module footprint report
###############################################################################
echo "2. Generating custom module footprint report..."

ssh root@"$DROPLET_IP" bash -s <<'REMOTE_SCRIPT' | tee "$OUTPUT_DIR/module_footprint.txt"
set -euo pipefail
DB="${ODOO_DB:-odoo}"

docker exec odoo-erp-prod bash -c "
psql -h db -U postgres -d \"$DB\" -c \"
with custom as (
  select name
  from ir_module_module
  where name like 'ipai_%'
)
select
  imd.module,
  sum((imd.model = 'ir.ui.menu')::int)              as menus,
  sum((imd.model = 'ir.actions.act_window')::int)   as actions,
  sum((imd.model = 'ir.ui.view')::int)              as views,
  sum((imd.model = 'ir.model')::int)                as models,
  sum((imd.model = 'ir.model.fields')::int)         as fields,
  sum((imd.model = 'ir.model.access')::int)         as access_rules,
  sum((imd.model = 'ir.rule')::int)                 as record_rules
from ir_model_data imd
join custom c on c.name = imd.module
group by imd.module
order by imd.module;
\"
"
REMOTE_SCRIPT

echo -e "${GREEN}✓ Footprint report saved to $OUTPUT_DIR/module_footprint.txt${NC}"
echo ""

###############################################################################
# 3. Identify safe retire candidates
###############################################################################
echo "3. Identifying safe retire candidates (UI-only modules)..."

ssh root@"$DROPLET_IP" bash -s <<'REMOTE_SCRIPT' | tee "$OUTPUT_DIR/safe_retire_candidates.txt"
set -euo pipefail
DB="${ODOO_DB:-odoo}"

docker exec odoo-erp-prod bash -c "
psql -h db -U postgres -d \"$DB\" -c \"
with custom as (
  select name
  from ir_module_module
  where name like 'ipai_%'
),
fp as (
  select
    imd.module,
    sum((imd.model = 'ir.ui.menu')::int)              as menus,
    sum((imd.model = 'ir.actions.act_window')::int)   as actions,
    sum((imd.model = 'ir.ui.view')::int)              as views,
    sum((imd.model = 'ir.model')::int)                as models,
    sum((imd.model = 'ir.model.fields')::int)         as fields,
    sum((imd.model = 'ir.model.access')::int)         as access_rules,
    sum((imd.model = 'ir.rule')::int)                 as record_rules
  from ir_model_data imd
  join custom c on c.name = imd.module
  group by imd.module
)
select
  module,
  menus,
  actions,
  views,
  models,
  fields,
  access_rules,
  record_rules,
  CASE
    WHEN models=0 AND fields=0 AND access_rules=0 AND record_rules=0 THEN '✓ SAFE TO RETIRE'
    ELSE 'Contains business logic'
  END as retirement_status
from fp
order by models, fields, access_rules, record_rules, module;
\"
"
REMOTE_SCRIPT

echo -e "${GREEN}✓ Retire candidates saved to $OUTPUT_DIR/safe_retire_candidates.txt${NC}"
echo ""

###############################################################################
# 4. Generate dependency graph for custom modules
###############################################################################
echo "4. Generating module dependency graph..."

ssh root@"$DROPLET_IP" bash -s <<'REMOTE_SCRIPT' | tee "$OUTPUT_DIR/module_dependencies.txt"
set -euo pipefail
DB="${ODOO_DB:-odoo}"

docker exec odoo-erp-prod bash -c "
psql -h db -U postgres -d \"$DB\" -c \"
SELECT
  m.name as module,
  string_agg(d.name, ', ' ORDER BY d.name) as depends_on
FROM ir_module_module m
LEFT JOIN ir_module_module_dependency md ON m.id = md.module_id
LEFT JOIN ir_module_module d ON md.name = d.name
WHERE m.name LIKE 'ipai_%'
  AND m.state = 'installed'
GROUP BY m.name
ORDER BY m.name;
\"
"
REMOTE_SCRIPT

echo -e "${GREEN}✓ Dependencies saved to $OUTPUT_DIR/module_dependencies.txt${NC}"
echo ""

###############################################################################
# 5. List installed core + OCA modules (baseline)
###############################################################################
echo "5. Listing installed core + OCA modules..."

ssh root@"$DROPLET_IP" bash -s <<'REMOTE_SCRIPT' | tee "$OUTPUT_DIR/baseline_modules.txt"
set -euo pipefail
DB="${ODOO_DB:-odoo}"

docker exec odoo-erp-prod bash -c "
psql -h db -U postgres -d \"$DB\" -c \"
SELECT name, author, latest_version, state
FROM ir_module_module
WHERE state = 'installed'
  AND name NOT LIKE 'ipai_%'
ORDER BY author, name;
\"
"
REMOTE_SCRIPT

echo -e "${GREEN}✓ Baseline modules saved to $OUTPUT_DIR/baseline_modules.txt${NC}"
echo ""

###############################################################################
# 6. Generate rationalization recommendation report
###############################################################################
echo "6. Generating rationalization recommendations..."

cat > "$OUTPUT_DIR/RATIONALIZATION_REPORT.md" <<'EOF'
# Odoo Module Rationalization Report

**Generated**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Database**: ${DB}
**Approach**: Baseline-first (Core + OCA → Delta)

---

## Executive Summary

This report analyzes all `ipai_*` custom modules to identify:
- **KEEP**: Modules with unique business logic (models, fields, security)
- **REDUCE**: Modules that are mostly UI/theme/wiring (convert to thin extensions)
- **RETIRE**: Modules that duplicate core/OCA functionality (uninstall)

---

## Decision Framework

| Category | Criteria | Action |
|----------|----------|--------|
| **KEEP** | Has models/fields/access_rules/record_rules | Preserve as-is |
| **REDUCE** | Mostly UI (views/menus/actions) | Convert to thin glue module |
| **RETIRE** | Duplicates core/OCA + no dependencies | Uninstall and remove |

---

## Module Footprint Analysis

See `module_footprint.txt` for complete data.

Key metrics:
- **Models**: Custom Odoo models (e.g., `ipai.finance.ppm`)
- **Fields**: Custom fields on existing models
- **Access Rules**: Security access control (`ir.model.access`)
- **Record Rules**: Row-level security (`ir.rule`)
- **Views/Menus/Actions**: UI elements (candidates for reduction)

---

## Safe Retire Candidates

See `safe_retire_candidates.txt` for complete list.

Modules with **zero models, zero fields, zero security rules**:
- These are pure UI/theme modules
- Can be safely retired if:
  1. No other modules depend on them
  2. Core/OCA provides equivalent functionality
  3. Business users confirm UI not critical

---

## Module Dependencies

See `module_dependencies.txt` for complete graph.

Before retiring a module:
1. Check if other `ipai_*` modules depend on it
2. If yes, refactor dependents first or keep as thin base
3. If no dependencies, safe to uninstall

---

## Baseline Modules

See `baseline_modules.txt` for complete list.

Current installed modules (core + OCA):
- Compare against custom modules to identify duplication
- Example: If `ipai_sale_order_portal` exists and `portal_sale_order_search` (OCA) is installed → retire custom

---

## OCA "Must Have" List

Reference: https://odoo-community.org/oca-for-functional-consultants

Functional areas:
- **Accounting**: `account_*` modules
- **Sales**: `sale_*`, `portal_*` modules
- **CRM**: `crm_*` modules
- **Project**: `project_*` modules
- **HR**: `hr_*` modules

**Action**: Install OCA "Must Have" modules for your functional areas **before** installing custom modules.

---

## Recommended Actions

### Immediate (Block Deployment)

1. ✅ Remove `ipai_month_end_closing.backup` (invalid module name)
2. Review `safe_retire_candidates.txt` for obvious duplicates
3. Identify modules with zero dependencies (easiest to retire)

### Short-Term (Next Sprint)

1. Install baseline: `base`, `web`, `mail`, `account`, `sale_management`, `purchase`, `stock`, `crm`, `project`, `hr_timesheet`
2. Install OCA "Must Have" modules for your functional areas
3. Compare custom modules against OCA equivalents
4. Create retirement plan for duplicates

### Medium-Term (Next Quarter)

1. For each **REDUCE** candidate:
   - Extract business logic into new thin module
   - Remove UI/theme bloat
   - Keep only unique wiring/configuration
2. Test reduced modules in staging environment
3. Deploy to production after validation

### Long-Term (Continuous)

1. Establish policy: **OCA first, custom second**
2. Before creating new `ipai_*` module:
   - Check if OCA module exists
   - Check if core module can be configured
   - Only create custom if truly unique requirement
3. Regular reviews (quarterly) to identify new rationalization opportunities

---

## Next Steps

1. Review this report with functional team
2. Get business user approval for retire candidates
3. Create GitHub issues for each retirement/reduction
4. Execute in staging environment first
5. Monitor for regressions
6. Deploy to production after validation

---

**Maintainer**: Jake Tolentino <business@insightpulseai.com>
EOF

# Substitute variables in the report
sed -i.bak "s/\$(date -u +\"%Y-%m-%d %H:%M:%S UTC\")/$(date -u +"%Y-%m-%d %H:%M:%S UTC")/g" "$OUTPUT_DIR/RATIONALIZATION_REPORT.md"
sed -i.bak "s/\${DB}/$DB/g" "$OUTPUT_DIR/RATIONALIZATION_REPORT.md"
rm "$OUTPUT_DIR/RATIONALIZATION_REPORT.md.bak"

echo -e "${GREEN}✓ Report saved to $OUTPUT_DIR/RATIONALIZATION_REPORT.md${NC}"
echo ""

###############################################################################
# Summary
###############################################################################
echo "================================================================================"
echo "Rationalization Analysis Complete"
echo "================================================================================"
echo ""
echo "Generated files:"
echo "  - $OUTPUT_DIR/module_footprint.txt"
echo "  - $OUTPUT_DIR/safe_retire_candidates.txt"
echo "  - $OUTPUT_DIR/module_dependencies.txt"
echo "  - $OUTPUT_DIR/baseline_modules.txt"
echo "  - $OUTPUT_DIR/RATIONALIZATION_REPORT.md"
echo ""
echo "Next steps:"
echo "  1. Review RATIONALIZATION_REPORT.md"
echo "  2. Identify safe retire candidates with zero dependencies"
echo "  3. Install OCA 'Must Have' modules"
echo "  4. Create retirement plan for duplicates"
echo ""
echo "View report: cat $OUTPUT_DIR/RATIONALIZATION_REPORT.md"
echo ""
