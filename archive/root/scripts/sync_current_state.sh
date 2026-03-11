#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "=== Sync Current State ==="
echo "Ensuring repository artifacts match current code/configuration."

echo "[1/7] Preflight Check"
git status --porcelain >/dev/null || true

echo "[2/7] Regenerate Repo Tree"
if [ -f scripts/gen_repo_tree.sh ]; then
  bash scripts/gen_repo_tree.sh
else
  echo "SKIP: scripts/gen_repo_tree.sh not found"
fi

echo "[3/7] Regenerate Odoo DBML"
if [ -f scripts/generate_odoo_dbml.py ]; then
  # DBML generation requires DB connection. Prefer container if available, otherwise best-effort local.
  set +e
  if [ -f /.dockerenv ]; then
    python3 scripts/generate_odoo_dbml.py
    rc=$?
  elif command -v docker >/dev/null 2>&1 && docker ps --format '{{.Names}}' | grep -qE '^odoo-core$'; then
    echo "Running DBML gen inside odoo-core container..."
    docker exec -i odoo-core python3 scripts/generate_odoo_dbml.py
    rc=$?
  else
    # Best-effort local run (may succeed if DB env is available)
    python3 scripts/generate_odoo_dbml.py
    rc=$?
  fi
  set -e

  if [ "${rc:-0}" -ne 0 ]; then
    echo "SKIP: DBML generation failed (likely no DB access)."
  fi
else
  echo "SKIP: scripts/generate_odoo_dbml.py not found"
fi

echo "[4/7] Regenerate Finance Close Seeds"
if [ -f scripts/seed_finance_close_from_xlsx.py ]; then
  python3 scripts/seed_finance_close_from_xlsx.py
else
  echo "SKIP: scripts/seed_finance_close_from_xlsx.py not found"
fi

echo "[5/7] Feature Inventory Introspection"
if [ -f scripts/ci/introspect_feature_inventory.py ]; then
  # Helper to check if we are inside a container
  if [ -f /.dockerenv ]; then
    # Inside container, run directly
    python3 scripts/ci/introspect_feature_inventory.py
  elif command -v docker >/dev/null 2>&1 && docker ps --format '{{.Names}}' | grep -qE '^odoo-core$'; then
    echo "Running introspection inside odoo-core container..."
    cat scripts/ci/introspect_feature_inventory.py | docker exec -i odoo-core odoo shell -d odoo_core --no-http
  else
    echo "SKIP: Odoo environment not accessible (not in container and odoo-core not running)"
  fi
else
  echo "SKIP: scripts/ci/introspect_feature_inventory.py not found"
fi

echo "[6/7] Enforce Spec Kit Bundle"
if [ ! -d spec/odoo-ce ]; then
  echo "WARNING: spec/odoo-ce directory missing!"
fi

echo "[7/7] Checking for Drift"
if git status --porcelain | grep -q . ; then
  echo "⚠️  Drift detected! The following files were updated:"
  git status --porcelain
  echo ""
  echo "Please commit these changes to sync the repository state."
else
  echo "✅ No drift detected. Repository is in sync."
fi
