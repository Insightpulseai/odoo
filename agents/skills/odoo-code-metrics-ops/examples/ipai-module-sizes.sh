#!/usr/bin/env bash
# Example: Measure IPAI module sizes
set -euo pipefail

echo "=== IPAI module line counts ==="
# Using cloc with path (no database needed)
# ~/.pyenv/versions/odoo-19-dev/bin/python vendor/odoo/odoo-bin cloc --path addons/ipai

echo "=== Quick file-based count ==="
for module_dir in addons/ipai/ipai_*/; do
  MODULE=$(basename "${module_dir}")
  PY_LINES=$(find "${module_dir}" -name "*.py" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
  XML_LINES=$(find "${module_dir}" -name "*.xml" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
  JS_LINES=$(find "${module_dir}" -name "*.js" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
  TOTAL=$((${PY_LINES:-0} + ${XML_LINES:-0} + ${JS_LINES:-0}))

  # Size classification
  if [ "${TOTAL}" -lt 500 ]; then SIZE="small"
  elif [ "${TOTAL}" -lt 2000 ]; then SIZE="medium"
  elif [ "${TOTAL}" -lt 5000 ]; then SIZE="large"
  else SIZE="VERY LARGE"
  fi

  printf "%-45s %6d lines (%s)\n" "${MODULE}" "${TOTAL}" "${SIZE}"
done | sort -t'(' -k1 -rn
