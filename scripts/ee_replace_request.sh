#!/usr/bin/env bash
set -euo pipefail

# -----------------------------------------------------------------------------
# EE Replacement Request
# -----------------------------------------------------------------------------
# Usage:
#   EE_AREA="Sign" OUTPUT=markdown ./scripts/ee_replace_request.sh
# -----------------------------------------------------------------------------

EE_AREA="${EE_AREA:-}"
OUTPUT="${OUTPUT:-markdown}"
MATRIX_FILE="spec/ipai_enterprise_bridge/ee-replacement-matrix.yaml"

if [[ -z "$EE_AREA" ]]; then
  echo "Error: EE_AREA environment variable required."
  exit 1
fi

if [[ ! -f "$MATRIX_FILE" ]]; then
  echo "Error: Matrix file not found at $MATRIX_FILE"
  exit 1
fi

# Use heredoc with single quotes to prevent variable expansion of backticks or $
PYTHON_SCRIPT=$(cat <<'EOF'
import sys, yaml, os

area_query = os.environ.get('EE_AREA')
output_fmt = os.environ.get('OUTPUT')

try:
    with open('spec/ipai_enterprise_bridge/ee-replacement-matrix.yaml', 'r') as f:
        data = yaml.safe_load(f)
except Exception as e:
    print(f'Error parsing yaml: {e}')
    sys.exit(1)

found = None
for item in data.get('areas', []):
    if item['ee_area'].lower() == area_query.lower():
        found = item
        break

if not found:
    print(f'❌ EE Area "{area_query}" not found in matrix.')
    print('Action: Add it to spec/ipai_enterprise_bridge/ee-replacement-matrix.yaml')
    sys.exit(1)

if output_fmt == 'markdown':
    print(f'# Replacement Plan: {found["ee_area"]}')
    print('')
    print('## 1. Native CE 18 Coverage')
    if found['ce_18_coverage']:
        for i in found['ce_18_coverage']:
            print(f'- {i}')
    else:
        print('- None')

    print('')
    print('## 2. Recommended OCA Modules')
    if found['oca_18_candidates']:
        for i in found['oca_18_candidates']:
            print(f'- {i}')
    else:
        print('- None')

    print('')
    print('## 3. Bridge Work (ipai_enterprise_bridge)')
    if found['bridge_required']:
        print(f'**Scope**: {found.get("bridge_scope", "N/A")}')
        print('')
        print('### Implementation Instructions')
        print('1. Modify `addons/ipai/ipai_enterprise_bridge/__manifest__.py` to depend on OCA modules.')
        print('2. Add glue code in `addons/ipai/ipai_enterprise_bridge/models/`.')
    else:
        print('✅ No bridge work required.')

    if found.get('forbidden'):
        print('')
        print('## ⚠️ Forbidden Features')
        for i in found['forbidden']:
            print(f'- {i}')

else:
    # YAML or JSON output could go here
    print(found)
EOF
)

python3 -c "$PYTHON_SCRIPT"
