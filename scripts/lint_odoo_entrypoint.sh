#!/usr/bin/env bash
set -euo pipefail

# Block calling odoo-bin with python directly anywhere in repo
# Exclude: docs (historical/explanatory), evidence (fix documentation), agent docs, log messages
bad=$(rg -n --hidden \
  --glob '!.git/*' \
  --glob '!**/node_modules/**' \
  --glob '!docs/**' \
  --glob '!**/evidence/**' \
  --glob '!agents/**/*.md' \
  'python(3)?\s+(\./)?odoo-bin\b' . \
  | grep -v 'log_warn\|log_info\|echo' \
  || true)

if [[ -n "$bad" ]]; then
  echo "❌ Forbidden: calling odoo-bin via python. Use ./scripts/odoo.sh instead."
  echo "$bad"
  exit 1
fi

echo "✅ odoo entrypoint lint passed"
