#!/usr/bin/env bash
set -euo pipefail

echo "== basics =="
pwd
python3 -V || true
which python3 || true
python3 -c "import sys; print('sys.executable:', sys.executable); print('sys.path[0:5]:', sys.path[0:5])"

echo
echo "== check if pip 'odoo' package is shadowing source checkout =="
python3 - <<'PY'
import importlib.util, sys
spec = importlib.util.find_spec("odoo")
print("find_spec('odoo'):", spec)
if spec and spec.origin:
  print("odoo origin:", spec.origin)
PY

echo
echo "== find common shadowing filenames (cause circular imports) =="
# If you have files named like core modules, they can shadow imports.
find . -maxdepth 4 -type f \( -name "odoo.py" -o -name "base.py" -o -name "rpc.py" -o -name "web.py" -o -name "http.py" \) -print || true

echo
echo "== check compiled caches (stale .pyc can bite) =="
find . -type d -name "__pycache__" | head -n 50 || true

echo
echo "== check addons manifest presence =="
test -f addons/ipai_ppm_okr/__manifest__.py && echo "OK: addons/ipai_ppm_okr/__manifest__.py found" || echo "MISSING: addons/ipai_ppm_okr/__manifest__.py"

echo
echo "== print odoo-bin header (shim vs python entry) =="
head -n 5 ./odoo-bin || true

echo
echo "== done =="
