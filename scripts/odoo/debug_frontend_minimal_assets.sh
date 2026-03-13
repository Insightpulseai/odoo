#!/usr/bin/env bash
# Debug web.assets_frontend_minimal compilation failure
# Run inside the Odoo runtime container or a container with the same image
set -euo pipefail

DB="${1:-odoo}"
CONF="${2:-/etc/odoo/odoo.conf}"
LOG="${3:-/tmp/odoo_frontend_minimal_debug.log}"

echo "=== [1/5] Dumping effective config ==="
python3 - <<'PY'
import sys
try:
    from odoo.tools import config
    config.parse_config(['-c', '/etc/odoo/odoo.conf'])
    print("db_name=", config.get('db_name'))
    print("dbfilter=", config.get('dbfilter'))
    print("addons_path=", config.get('addons_path'))
except Exception as e:
    print(f"Config parse failed: {e}", file=sys.stderr)
PY

echo ""
echo "=== [2/5] Rebuilding web assets with debug logging ==="
odoo -c "$CONF" -d "$DB" --stop-after-init --log-level=debug 2>&1 | tee "$LOG" >/dev/null || true

echo ""
echo "=== [3/5] Extracting asset-related failures ==="
grep -Ei "asset|assets_|traceback|error|exception|qweb|template|scss|js.*fail|js.*error" "$LOG" | tail -200 || echo "(no asset errors found)"

echo ""
echo "=== [4/5] Listing custom addons with web assets ==="
python3 - <<'PY'
import os, glob, ast, sys

for mf_path in sorted(glob.glob('/opt/odoo/addons/ipai/*/__manifest__.py') +
                       glob.glob('/mnt/extra-addons/ipai/*/__manifest__.py')):
    try:
        with open(mf_path) as f:
            mf = ast.literal_eval(f.read())
        assets = mf.get('assets', {})
        if assets:
            module = os.path.basename(os.path.dirname(mf_path))
            bundles = list(assets.keys())
            print(f"  {module}: {bundles}")
    except Exception as e:
        print(f"  ERROR reading {mf_path}: {e}", file=sys.stderr)
PY

echo ""
echo "=== [5/5] Done. Full log at $LOG ==="
echo "Review with: grep -i 'assets_frontend_minimal' $LOG"
