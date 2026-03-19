#!/usr/bin/env bash
set -euo pipefail

# Parse OCA must-have modules from config/addons.manifest.yaml
# Returns comma-separated list of module names for Odoo installer.
# Replaces legacy JSON manifest consumption with YAML via python3.

MANIFEST_FILE="${MANIFEST_FILE:-config/addons.manifest.yaml}"

if [ ! -f "${MANIFEST_FILE}" ]; then
  echo "ERROR: Manifest file not found: ${MANIFEST_FILE}" >&2
  exit 1
fi

if ! python3 -c "import yaml" 2>/dev/null; then
  echo "ERROR: PyYAML required. Install: pip install pyyaml" >&2
  exit 1
fi

# Extract all must-have modules from all OCA repos, sorted, comma-separated
python3 -c "
import yaml
with open('${MANIFEST_FILE}') as f:
    m = yaml.safe_load(f)
modules = set()
for r in m.get('oca_repositories', []):
    for mod in r.get('must_have', []) or []:
        modules.add(mod)
print(','.join(sorted(modules)))
"
