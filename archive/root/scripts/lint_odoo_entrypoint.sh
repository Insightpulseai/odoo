#!/usr/bin/env bash
set -euo pipefail

# Block calling odoo-bin with python directly anywhere in repo
# Exclude: evidence (historical fix documentation), archives (deprecated content),
#          ODOO_EXECUTION.md (educational guide), test scripts (validation),
#          comments in odoo-bin and README (educational examples of wrong pattern)
# NOTE: Active docs/ and agents/ ARE now checked (to prevent teaching wrong patterns)
bad=$(rg -n --hidden \
  --glob '!.git/*' \
  --glob '!**/node_modules/**' \
  --glob '!docs/evidence/**' \
  --glob '!**/archive/**' \
  --glob '!**/*-archive.md' \
  --glob '!docs/ODOO_EXECUTION.md' \
  --glob '!scripts/tests/odoo-entrypoint-*.sh' \
  'python(3)?\s+(\./)?odoo-bin\b' . \
  | grep -v 'log_warn\|log_info\|echo' \
  | grep -v '^./odoo-bin:.*#.*WRONG' \
  | grep -v '^./README.md:.*❌.*WRONG' \
  || true)

if [[ -n "$bad" ]]; then
  echo "❌ Forbidden: calling odoo-bin via python. Use ./scripts/odoo.sh instead."
  echo "$bad"
  exit 1
fi

echo "✅ odoo entrypoint lint passed"
