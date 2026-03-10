#!/usr/bin/env bash
set -euo pipefail

# Smoke test: Verify Odoo can be imported after editable install
# Fast alternative to Docker-based smoke test for CI

echo "========================================="
echo "  Odoo Import Smoke Test (pip -e)"
echo "========================================="

# Show Python environment
echo "Python version:"
python -V

echo ""
echo "Upgrading pip/setuptools/wheel..."
python -m pip install -U pip setuptools wheel --quiet

# Check if setup.py or pyproject.toml exists
if [ ! -f setup.py ] && [ ! -f pyproject.toml ]; then
  echo "⚠️  No setup.py or pyproject.toml found - editable install not supported"
  echo "   This is expected for Odoo CE repos that use Docker-only deployment"
  echo "   Use scripts/ci/smoke_odoo_container.sh instead"
  exit 0  # Exit gracefully - not a failure
fi

echo ""
echo "Installing Odoo in editable mode..."
if python -m pip install -e . --quiet; then
  echo "✅ pip install -e . succeeded"
else
  echo "❌ pip install -e . failed"
  exit 1
fi

echo ""
echo "Testing import odoo..."
python - <<'PY'
try:
    import odoo
    print("✅ import odoo ok:", getattr(odoo, "__file__", None))
    print("   version:", getattr(odoo, "release", {}).get("version", "unknown"))
except ImportError as e:
    print("❌ import odoo failed:", e)
    exit(1)
PY

echo ""
echo "========================================="
echo "  ✅ Import smoke test passed"
echo "========================================="
