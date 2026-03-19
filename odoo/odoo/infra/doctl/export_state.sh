#!/usr/bin/env bash
set -euo pipefail

# run from anywhere, always resolve to repo root
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${ROOT}" ]]; then
  echo "ERROR: must be run inside a git repo" >&2
  exit 1
fi
cd "${ROOT}"

OUT_DIR="inventory"
mkdir -p "${OUT_DIR}"

ts="$(date -u +"%Y%m%dT%H%M%SZ")"
run_dir="${OUT_DIR}/runs/${ts}"
mkdir -p "${run_dir}"

require() { command -v "$1" >/dev/null 2>&1 || { echo "missing: $1" >&2; exit 1; }; }
require doctl
require jq

# sanity: doctl auth
doctl account get >/dev/null 2>&1 || { echo "ERROR: doctl not authenticated" >&2; exit 1; }

echo "→ exporting DigitalOcean inventory to ${run_dir}"

# Apps
doctl apps list --output json | tee "${run_dir}/apps.list.json" >/dev/null
jq -r '.[].id' "${run_dir}/apps.list.json" | while read -r id; do
  doctl apps get "${id}" --output json > "${run_dir}/apps.${id}.json"
done

# Agents (DO AI Agents)
# Some accounts expose via "doctl ai" or "doctl agents". Try both.
if doctl ai --help >/dev/null 2>&1; then
  doctl ai agents list --output json > "${run_dir}/agents.list.json" || echo "WARN: ai agents list failed" >&2
elif doctl agents --help >/dev/null 2>&1; then
  doctl agents list --output json > "${run_dir}/agents.list.json" || echo "WARN: agents list failed" >&2
else
  echo "WARN: doctl has no ai/agents namespace; skipping agents export" >&2
  echo "[]" > "${run_dir}/agents.list.json"
fi

# Droplets
doctl compute droplet list --output json > "${run_dir}/droplets.list.json"

# Projects
doctl projects list --output json > "${run_dir}/projects.list.json" 2>/dev/null || echo "[]" > "${run_dir}/projects.list.json"

# Databases (if available)
doctl databases list --output json > "${run_dir}/databases.list.json" 2>/dev/null || echo "[]" > "${run_dir}/databases.list.json"

# Summary "latest" pointers
ln -sfn "runs/$(basename "${run_dir}")" "${OUT_DIR}/latest"

echo "✅ export complete"
echo "   latest -> ${OUT_DIR}/latest"
