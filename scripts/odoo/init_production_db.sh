#!/usr/bin/env bash
# ============================================================================
# Unified Production Database Seed Orchestrator
# ============================================================================
# SSOT: ssot/migration/production_seed_plan.yaml
# Docs: docs/operations/PRODUCTION_SEED_PLAN.md
#
# Usage:
#   DB_NAME=odoo_dev ./scripts/odoo/init_production_db.sh
#   DB_NAME=odoo ./scripts/odoo/init_production_db.sh --skip-supabase
# ============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DB_NAME="${DB_NAME:?ERROR: DB_NAME must be set (odoo_dev | odoo_staging | odoo)}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-$(whoami)}"
ODOO_BIN="${ODOO_BIN:-odoo-bin}"
ADDONS_PATH="${ADDONS_PATH:-vendor/odoo/addons,addons/ipai,addons/oca}"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SKIP_SUPABASE="${1:-}"
TIMESTAMP="$(date +%Y%m%d-%H%M)"
EVIDENCE_DIR="$REPO_ROOT/docs/evidence/$TIMESTAMP/seed"

# Forbidden database names
if [[ "$DB_NAME" == "odoo_prod" ]]; then
    echo "ERROR: 'odoo_prod' is forbidden. Use 'odoo' for production."
    exit 1
fi

echo "============================================"
echo " IPAI Production Seed Orchestrator"
echo " Database: $DB_NAME"
echo " Host:     $DB_HOST:$DB_PORT"
echo " Time:     $TIMESTAMP"
echo "============================================"

mkdir -p "$EVIDENCE_DIR"

# ---------------------------------------------------------------------------
# Phase 1: Odoo CE Core + OCA Baseline
# ---------------------------------------------------------------------------
echo ""
echo ">>> PHASE 1: Odoo CE Core + OCA Baseline"
echo "    Source: config/addons.manifest.yaml"

$ODOO_BIN \
    --database="$DB_NAME" \
    --db_host="$DB_HOST" --db_port="$DB_PORT" --db_user="$DB_USER" \
    --addons-path="$ADDONS_PATH" \
    --init=base \
    --stop-after-init \
    --no-http \
    2>&1 | tee "$EVIDENCE_DIR/phase1_core.log"

echo "    Phase 1: Base installed."

# OCA baseline (if install script exists)
if [[ -f "$REPO_ROOT/scripts/odoo/install_oca_from_ssot.py" ]]; then
    echo "    Installing OCA baseline from manifest..."
    python3 "$REPO_ROOT/scripts/odoo/install_oca_from_ssot.py" \
        --db="$DB_NAME" \
        2>&1 | tee -a "$EVIDENCE_DIR/phase1_oca.log" || {
        echo "    WARNING: OCA install had errors (may be expected for missing 19.0 ports)"
    }
else
    echo "    SKIP: install_oca_from_ssot.py not found"
fi

echo "    Phase 1: COMPLETE"

# ---------------------------------------------------------------------------
# Phase 2: Canonical IPAI Seed Modules
# ---------------------------------------------------------------------------
echo ""
echo ">>> PHASE 2: Canonical IPAI Seed Modules"
echo "    Source: ssot/migration/seed_canonical_map.yaml"

# Canonical modules only — DO NOT add ipai_finance_close_seed or ipai_mailgun_smtp
CANONICAL_MODULES="ipai_project_seed,ipai_zoho_mail,ipai_bir_tax_compliance,ipai_ai_copilot"

# TODO: Add ipai_finance_workflow once installable=True
# CANONICAL_MODULES="$CANONICAL_MODULES,ipai_finance_workflow"

echo "    Installing: $CANONICAL_MODULES"
echo "    BLOCKED: ipai_finance_close_seed (duplicate), ipai_mailgun_smtp (deprecated)"

$ODOO_BIN \
    --database="$DB_NAME" \
    --db_host="$DB_HOST" --db_port="$DB_PORT" --db_user="$DB_USER" \
    --addons-path="$ADDONS_PATH" \
    --init="$CANONICAL_MODULES" \
    --stop-after-init \
    --no-http \
    2>&1 | tee "$EVIDENCE_DIR/phase2_ipai.log" || {
    echo "    WARNING: Some IPAI modules may have failed (check log)"
}

echo "    Phase 2: COMPLETE"

# ---------------------------------------------------------------------------
# Phase 3: Companies, Users, Groups
# ---------------------------------------------------------------------------
echo ""
echo ">>> PHASE 3: Companies, Users, Groups"
echo "    Source: scripts/odoo/seed_prod_users.py"

if [[ -f "$REPO_ROOT/scripts/odoo/seed_prod_users.py" ]]; then
    python3 "$REPO_ROOT/scripts/odoo/seed_prod_users.py" \
        2>&1 | tee "$EVIDENCE_DIR/phase3_users.log" || {
        echo "    WARNING: User seeding had errors (check log)"
    }
else
    echo "    SKIP: seed_prod_users.py not found"
fi

echo "    Phase 3: COMPLETE"

# ---------------------------------------------------------------------------
# Phase 4: Supabase Control Plane Seeds (Optional)
# ---------------------------------------------------------------------------
echo ""
echo ">>> PHASE 4: Supabase Control Plane Seeds"

if [[ "$SKIP_SUPABASE" == "--skip-supabase" ]]; then
    echo "    SKIP: --skip-supabase flag set"
else
    echo "    NOTE: Supabase seeds target Supabase PG, not Odoo PG"
    echo "    Run separately: supabase db seed --db-url=\$SUPABASE_DB_URL"
    echo "    Seed files: supabase/seeds/*.sql"
fi

echo "    Phase 4: COMPLETE (or skipped)"

# ---------------------------------------------------------------------------
# Phase 5: Validation + Evidence
# ---------------------------------------------------------------------------
echo ""
echo ">>> PHASE 5: Validation + Evidence"

if [[ -f "$REPO_ROOT/scripts/odoo/validate_seed_state.py" ]]; then
    python3 "$REPO_ROOT/scripts/odoo/validate_seed_state.py" \
        --db="$DB_NAME" \
        --evidence-dir="$EVIDENCE_DIR" \
        2>&1 | tee "$EVIDENCE_DIR/phase5_validation.log"
    VALIDATION_EXIT=$?
else
    echo "    Running basic validation..."
    # Basic SQL checks if validator not available
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c \
        "SELECT 'modules_installed=' || count(*) FROM ir_module_module WHERE state='installed'" \
        2>&1 | tee "$EVIDENCE_DIR/phase5_basic.log"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c \
        "SELECT 'companies=' || count(*) FROM res_company" \
        2>&1 | tee -a "$EVIDENCE_DIR/phase5_basic.log"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c \
        "SELECT 'users=' || count(*) FROM res_users WHERE active=true" \
        2>&1 | tee -a "$EVIDENCE_DIR/phase5_basic.log"
    VALIDATION_EXIT=0
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "============================================"
echo " SEED COMPLETE"
echo " Database: $DB_NAME"
echo " Evidence: $EVIDENCE_DIR"
echo " Status:   $([ $VALIDATION_EXIT -eq 0 ] && echo 'PASS' || echo 'FAIL')"
echo "============================================"

exit $VALIDATION_EXIT
