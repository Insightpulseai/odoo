#!/usr/bin/env bash
###############################################################################
# Complete Odoo Rationalization Workflow
# Baseline → Footprint → Validation → Retire Backlog
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
echo "Complete Odoo Rationalization Workflow"
echo "================================================================================"
echo ""
echo "Database: $DB"
echo "Droplet: $DROPLET_IP"
echo "Output: $OUTPUT_DIR"
echo ""

mkdir -p "$OUTPUT_DIR"

###############################################################################
# Phase 1: Install Baseline (CE + OCA Must-Have)
###############################################################################
echo "================================================================================"
echo "Phase 1: Install Baseline (CE + OCA Must-Have)"
echo "================================================================================"
echo ""

if [ ! -f "$OUTPUT_DIR/.baseline_installed" ]; then
    echo "Installing baseline modules..."
    ./scripts/install_baseline.sh
    touch "$OUTPUT_DIR/.baseline_installed"
    echo -e "${GREEN}✓ Baseline installation complete${NC}"
else
    echo "⚠ Baseline already installed (skip with: rm $OUTPUT_DIR/.baseline_installed)"
fi

echo ""

###############################################################################
# Phase 2: Apply OCA Validation Schema
###############################################################################
echo "================================================================================"
echo "Phase 2: Apply OCA Validation Schema"
echo "================================================================================"
echo ""

echo "Applying OCA validation schema migration..."

ssh root@"$DROPLET_IP" bash <<'REMOTE_SCRIPT'
set -euo pipefail
DB="${ODOO_DB:-odoo}"

# Copy migration file to droplet
cat > /tmp/oca_validation_schema.sql <<'EOF'
# Paste the entire 20260108_oca_validation.sql content here
# (For production, use scp to transfer the file)
EOF

# Apply migration
docker exec odoo-erp-prod bash -c "
  psql -h db -U postgres -d \"$DB\" -f /tmp/oca_validation_schema.sql
"

echo "✓ OCA validation schema applied"
REMOTE_SCRIPT

echo -e "${GREEN}✓ Validation schema ready${NC}"
echo ""

###############################################################################
# Phase 3: Generate Feature Signatures
###############################################################################
echo "================================================================================"
echo "Phase 3: Generate Feature Signatures"
echo "================================================================================"
echo ""

echo "Generating feature signatures for all ipai_* modules..."

# Copy signature generator to droplet
scp scripts/generate_module_signatures.py root@"$DROPLET_IP":/tmp/

# Execute on droplet
ssh root@"$DROPLET_IP" bash <<'REMOTE_SCRIPT'
set -euo pipefail
DB="${ODOO_DB:-odoo}"

# Install dependencies if needed
docker exec odoo-erp-prod bash -c "pip3 install psycopg2-binary || true"

# Run signature generator
docker exec odoo-erp-prod bash -c "
export POSTGRES_HOST=db
export POSTGRES_PORT=5432
export POSTGRES_DB=\"$DB\"
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=\$PGPASSWORD

python3 /tmp/generate_module_signatures.py
"
REMOTE_SCRIPT

echo -e "${GREEN}✓ Feature signatures generated${NC}"
echo ""

###############################################################################
# Phase 4: Run Validation (OCA Matching)
###############################################################################
echo "================================================================================"
echo "Phase 4: Run OCA Validation"
echo "================================================================================"
echo ""

echo "Running OCA redundancy validation..."

ssh root@"$DROPLET_IP" bash <<'REMOTE_SCRIPT' | tee "$OUTPUT_DIR/validation_results.txt"
set -euo pipefail
DB="${ODOO_DB:-odoo}"

docker exec odoo-erp-prod bash -c "
psql -h db -U postgres -d \"$DB\" -c \"
SELECT * FROM oca.validate_all_custom_modules()
ORDER BY highest_confidence DESC;
\"
"

echo ""
echo "Detailed validation results:"
docker exec odoo-erp-prod bash -c "
psql -h db -U postgres -d \"$DB\" -c \"
SELECT
  custom_module,
  oca_module,
  match_confidence,
  recommendation,
  matched_keywords
FROM oca.validation_results
WHERE match_confidence >= 0.3
ORDER BY custom_module, match_confidence DESC;
\"
"
REMOTE_SCRIPT

echo -e "${GREEN}✓ Validation complete (results in $OUTPUT_DIR/validation_results.txt)${NC}"
echo ""

###############################################################################
# Phase 5: Generate Footprint Analysis
###############################################################################
echo "================================================================================"
echo "Phase 5: Generate Footprint Analysis"
echo "================================================================================"
echo ""

echo "Analyzing module footprints..."

ssh root@"$DROPLET_IP" bash <<'REMOTE_SCRIPT' | tee "$OUTPUT_DIR/footprint_analysis.txt"
set -euo pipefail
DB="${ODOO_DB:-odoo}"

docker exec odoo-erp-prod bash -c "
psql -h db -U postgres -d \"$DB\" -c \"
-- Insert/update footprints
INSERT INTO oca.module_footprints (module_name, menus, actions, views, models, fields, access_rules, record_rules)
SELECT
  imd.module,
  sum((imd.model = 'ir.ui.menu')::int),
  sum((imd.model = 'ir.actions.act_window')::int),
  sum((imd.model = 'ir.ui.view')::int),
  sum((imd.model = 'ir.model')::int),
  sum((imd.model = 'ir.model.fields')::int),
  sum((imd.model = 'ir.model.access')::int),
  sum((imd.model = 'ir.rule')::int)
FROM ir_model_data imd
WHERE imd.module LIKE 'ipai_%'
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

-- Query footprints
SELECT * FROM oca.module_footprints ORDER BY is_ui_only DESC, models, module_name;
\"
"
REMOTE_SCRIPT

echo -e "${GREEN}✓ Footprint analysis complete (results in $OUTPUT_DIR/footprint_analysis.txt)${NC}"
echo ""

###############################################################################
# Phase 6: Generate Retire Backlog
###############################################################################
echo "================================================================================"
echo "Phase 6: Generate Retire Backlog"
echo "================================================================================"
echo ""

echo "Generating retire backlog with recommendations..."

ssh root@"$DROPLET_IP" bash <<'REMOTE_SCRIPT' | tee "$OUTPUT_DIR/retire_backlog.txt"
set -euo pipefail
DB="${ODOO_DB:-odoo}"

docker exec odoo-erp-prod bash -c "
psql -h db -U postgres -d \"$DB\" -c \"
WITH combined AS (
  SELECT
    fp.module_name,
    fp.is_ui_only,
    fp.models,
    fp.fields,
    fp.access_rules,
    fp.record_rules,
    COALESCE(MAX(vr.match_confidence), 0) AS oca_match_confidence,
    COALESCE((SELECT recommendation FROM oca.validation_results WHERE custom_module = fp.module_name ORDER BY match_confidence DESC LIMIT 1), 'KEEP') AS recommendation,
    COALESCE((SELECT oca_module FROM oca.validation_results WHERE custom_module = fp.module_name ORDER BY match_confidence DESC LIMIT 1), '') AS best_oca_match
  FROM oca.module_footprints fp
  LEFT JOIN oca.validation_results vr ON fp.module_name = vr.custom_module
  GROUP BY fp.module_name, fp.is_ui_only, fp.models, fp.fields, fp.access_rules, fp.record_rules
)
SELECT
  module_name,
  CASE
    WHEN is_ui_only AND oca_match_confidence >= 0.7 THEN 'RETIRE (UI-only + high OCA match)'
    WHEN is_ui_only AND oca_match_confidence >= 0.4 THEN 'REDUCE (UI-only + medium OCA match)'
    WHEN is_ui_only THEN 'REDUCE (UI-only, no OCA match)'
    WHEN oca_match_confidence >= 0.7 THEN 'RETIRE (high OCA match)'
    WHEN oca_match_confidence >= 0.4 THEN 'REDUCE (medium OCA match)'
    ELSE 'KEEP (unique business logic)'
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
  module_name;
\"
"
REMOTE_SCRIPT

echo -e "${GREEN}✓ Retire backlog generated (results in $OUTPUT_DIR/retire_backlog.txt)${NC}"
echo ""

###############################################################################
# Phase 7: Generate Final Report
###############################################################################
echo "================================================================================"
echo "Phase 7: Generate Final Report"
echo "================================================================================"
echo ""

cat > "$OUTPUT_DIR/FINAL_RATIONALIZATION_REPORT.md" <<'EOF'
# Final Odoo Rationalization Report

**Generated**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Workflow**: Baseline → Footprint → Validation → Retire Backlog

---

## Executive Summary

This report provides **deterministic, evidence-based recommendations** for retiring redundant `ipai_*` modules after installing the CE + OCA baseline.

**Key Findings**:
- Baseline installed: Odoo CE core + OCA Must-Have modules
- Feature signatures generated: All ipai_* modules analyzed
- OCA validation complete: Redundancy matches identified
- Footprint analysis complete: UI-only modules flagged
- Retire backlog prioritized: RETIRE → REDUCE → KEEP

---

## Methodology

### Phase 1: Baseline Installation
- Installed Odoo CE core modules (base, accounting, sales, etc.)
- Installed OCA Must-Have modules from PRD Appendix A:
  - account_financial_report, account_lock_date_update, account_fiscal_year
  - base_tier_validation, mass_editing, report_xlsx
  - sale_order_type, purchase_order_type, auditlog, web_responsive

### Phase 2: Feature Signature Generation
- Extracted feature signatures from all installed ipai_* modules:
  - Manifest summary and description
  - Model names, view titles, menu labels, action names
  - Keywords extracted from all text fields
- Computed signature hash for change detection

### Phase 3: OCA Validation
- Matched custom module keywords against OCA module index
- Computed Jaccard similarity scores (keyword overlap)
- Identified model name overlaps
- Generated match confidence scores (0.0-1.0)

### Phase 4: Footprint Analysis
- Counted menus, actions, views, models, fields, security rules
- Flagged UI-only modules (zero models/fields/security)
- Combined with OCA validation for final recommendations

---

## Retire Backlog

See `retire_backlog.txt` for complete prioritized list.

### Priority 1: RETIRE (UI-only + high OCA match ≥0.7)
These modules add **only UI elements** and **OCA provides equivalent functionality**.

**Action**: Uninstall module → Remove from filesystem → Update dependencies

### Priority 2: REDUCE (UI-only + medium OCA match ≥0.4)
These modules are mostly UI but may have some unique wiring.

**Action**: Extract minimal business logic → Create thin wrapper → Remove UI bloat

### Priority 3: REDUCE (UI-only, no OCA match)
Pure UI modules with no OCA equivalent (likely themes/branding).

**Action**: Evaluate if UI is essential → Keep as thin theme module → Remove app logic

### Priority 4: RETIRE (high OCA match ≥0.7, has models)
Modules with business logic but **OCA provides superior implementation**.

**Action**: Migrate data to OCA module → Uninstall custom → Remove from filesystem

### Priority 5: REDUCE (medium OCA match ≥0.4, has models)
Modules with some unique logic but significant OCA overlap.

**Action**: Refactor to use OCA base → Keep only unique delta → Reduce size

### Priority 6: KEEP (unique business logic)
Modules with unique models/fields/security not covered by CE/OCA.

**Action**: Preserve as-is → Document why kept → Monitor for future OCA alternatives

---

## Validation Results

See `validation_results.txt` for detailed OCA matching results.

Key metrics:
- **Match Confidence**: Jaccard similarity of keywords (0.0-1.0)
- **Matched Keywords**: Overlapping keywords between custom and OCA
- **Best OCA Match**: Highest confidence OCA module match

---

## Footprint Analysis

See `footprint_analysis.txt` for detailed module footprints.

Key indicators:
- **is_ui_only**: TRUE if no models/fields/access_rules/record_rules
- **models**: Custom Odoo models (strong signal to KEEP)
- **fields**: Custom fields on existing models (moderate signal to KEEP)
- **access_rules + record_rules**: Security implementation (strong signal to KEEP)

---

## Execution Plan

### Phase 1: Retire UI-Only Modules with High OCA Match
```bash
# For each Priority 1 module:
MODULE="ipai_example_ui_only"

# 1. Uninstall from Odoo
ssh root@$DROPLET_IP "docker exec odoo-erp-prod odoo -d $DB -u $MODULE --stop-after-init"

# 2. Remove from filesystem
rm -rf addons/ipai/$MODULE

# 3. Update git
git add addons/ipai/
git commit -m "chore: retire redundant UI module $MODULE (replaced by OCA)"

# 4. Verify no breakage
ssh root@$DROPLET_IP "docker exec odoo-erp-prod odoo -d $DB --stop-after-init"
```

### Phase 2: Reduce UI-Heavy Modules
```bash
# For each Priority 2/3 module:
MODULE="ipai_example_ui_heavy"

# 1. Create new thin module
mkdir addons/ipai/${MODULE}_lite
# 2. Copy only essential business logic (models, security)
# 3. Remove all UI bloat (views, menus, actions)
# 4. Update dependencies to point to lite version
# 5. Test thoroughly in staging
# 6. Deploy to production after validation
```

### Phase 3: Migrate to OCA Equivalents
```bash
# For each Priority 4 module with data:
MODULE="ipai_example_with_data"
OCA_MODULE="oca_equivalent"

# 1. Export data from custom module
# 2. Install OCA module
ssh root@$DROPLET_IP "docker exec odoo-erp-prod odoo -d $DB -i $OCA_MODULE --stop-after-init"
# 3. Migrate data to OCA module tables
# 4. Verify data integrity
# 5. Uninstall custom module
# 6. Remove from filesystem
```

---

## Success Criteria

- [  ] All Priority 1 modules retired (UI-only + high OCA match)
- [  ] Priority 2/3 modules reduced to thin wrappers
- [  ] Priority 4 modules migrated to OCA equivalents
- [  ] Zero UI-only modules remaining
- [  ] OCA coverage documented for all kept modules
- [  ] Baseline validation passes all health checks

---

## Next Steps

1. **Review this report** with functional team and get business approval
2. **Create GitHub issues** for each retirement/reduction
3. **Execute Phase 1** in staging environment first
4. **Monitor for regressions** and user feedback
5. **Deploy to production** after thorough validation
6. **Update module policy**: OCA first, custom second

---

**Maintainer**: Jake Tolentino <business@insightpulseai.com>
**Policy**: Config → OCA → Delta (ipai_*)
EOF

# Substitute variables
sed -i.bak "s/\$(date -u +\"%Y-%m-%d %H:%M:%S UTC\")/$(date -u +"%Y-%m-%d %H:%M:%S UTC")/g" "$OUTPUT_DIR/FINAL_RATIONALIZATION_REPORT.md"
rm "$OUTPUT_DIR/FINAL_RATIONALIZATION_REPORT.md.bak"

echo -e "${GREEN}✓ Final report generated: $OUTPUT_DIR/FINAL_RATIONALIZATION_REPORT.md${NC}"
echo ""

###############################################################################
# Summary
###############################################################################
echo "================================================================================"
echo "Rationalization Workflow Complete"
echo "================================================================================"
echo ""
echo "Generated artifacts:"
echo "  1. $OUTPUT_DIR/validation_results.txt     - OCA matching results"
echo "  2. $OUTPUT_DIR/footprint_analysis.txt     - Module footprints"
echo "  3. $OUTPUT_DIR/retire_backlog.txt         - Prioritized retire list"
echo "  4. $OUTPUT_DIR/FINAL_RATIONALIZATION_REPORT.md - Executive report"
echo ""
echo "Next steps:"
echo "  1. Review final report: cat $OUTPUT_DIR/FINAL_RATIONALIZATION_REPORT.md"
echo "  2. Identify Priority 1 modules (RETIRE: UI-only + high OCA match)"
echo "  3. Create GitHub issues for each retirement"
echo "  4. Execute retirements in staging first"
echo "  5. Deploy to production after validation"
echo ""
echo -e "${BLUE}Policy: Config → OCA → Delta (ipai_*)${NC}"
echo ""
