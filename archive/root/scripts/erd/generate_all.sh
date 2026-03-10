#!/usr/bin/env bash
# generate_all.sh — Orchestrate DBML + ORM crosswalk generation.
#
# Steps:
#   1. Export pg_catalog → DBML  (requires DATABASE_URL or PG* vars)
#   2. Export ORM graph  → docs/data_model/schema.json
#      (skipped if SKIP_ORM_EXPORT=1 or runner not available)
#   3. Build crosswalk   → docs/erd/odoo_crosswalk.json
#
# Environment variables:
#   DATABASE_URL          PostgreSQL DSN (required for steps 1 + 3)
#   SKIP_ORM_EXPORT       Set to "1" to skip ORM step (CI without live Odoo DB)
#
# Usage (local):
#   export DATABASE_URL="postgresql://postgres:pass@localhost:5432/odoo"
#   bash scripts/erd/generate_all.sh
#
# Usage (CI):
#   SKIP_ORM_EXPORT=1 DATABASE_URL="${{ secrets.DATABASE_URL }}" \
#     bash scripts/erd/generate_all.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "=== ERD Generation ==="
echo "Repo root: $REPO_ROOT"
echo ""

# ---------------------------------------------------------------------------
# Step 1: DBML from pg_catalog
# ---------------------------------------------------------------------------
echo "--- Step 1: pg_catalog → DBML ---"
if python3 scripts/erd/export_dbml.py; then
    echo "✅ DBML export complete"
else
    EXIT=$?
    echo "❌ DBML export failed (exit $EXIT)"
    echo "   Set DATABASE_URL or PG* env vars for a live database connection."
    echo "   In CI without a DB, this step is advisory — see erd-drift-check.yml."
    exit $EXIT
fi

echo ""

# ---------------------------------------------------------------------------
# Step 2: ORM graph (optional / skippable)
# ---------------------------------------------------------------------------
echo "--- Step 2: ORM graph (schema.json) ---"
if [ "${SKIP_ORM_EXPORT:-0}" = "1" ]; then
    echo "ℹ️  SKIP_ORM_EXPORT=1 — skipping ORM export"
elif [ -x "$REPO_ROOT/scripts/odoo/run_export_schema.sh" ]; then
    echo "Running scripts/odoo/run_export_schema.sh …"
    bash "$REPO_ROOT/scripts/odoo/run_export_schema.sh"
    echo "✅ ORM export complete"
else
    echo "ℹ️  scripts/odoo/run_export_schema.sh not found — running export_schema.py directly"
    if python3 tools/odoo_schema/export_schema.py; then
        echo "✅ ORM export complete"
    else
        echo "⚠️  ORM export failed — crosswalk will have empty ORM side"
        echo "   This is expected in CI (SKIP_ORM_EXPORT=1 suppresses this warning)."
    fi
fi

echo ""

# ---------------------------------------------------------------------------
# Step 3: Crosswalk
# ---------------------------------------------------------------------------
echo "--- Step 3: DBML + schema.json → crosswalk ---"
if python3 scripts/erd/export_crosswalk.py; then
    echo "✅ Crosswalk export complete"
else
    EXIT=$?
    echo "❌ Crosswalk export failed (exit $EXIT)"
    exit $EXIT
fi

echo ""
echo "=== ERD generation complete ==="
echo "Artifacts:"
echo "  docs/erd/odoo.dbml"
echo "  docs/erd/odoo_crosswalk.json"
echo "  docs/data_model/schema.json  (if ORM step ran)"
