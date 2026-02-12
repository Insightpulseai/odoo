#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SSOT_DIR="${ROOT_DIR}/sandbox/dev"
SSOT_FILE="${SSOT_DIR}/compose.yml"

# 1) SSOT file must exist
test -f "${SSOT_FILE}" || { echo "ERROR: Missing SSOT compose file: ${SSOT_FILE}" >&2; exit 1; }

# 2) Disallow other compose files in sandbox/dev
mapfile -t rogue_in_dev < <(find "${SSOT_DIR}" -maxdepth 1 -type f \
  \( -iname "docker-compose*.yml" -o -iname "docker-compose*.yaml" -o -iname "compose*.yaml" -o -iname "compose.*.yml" \) \
  ! -iname "compose.yml" \
  -print | sort)

if (( ${#rogue_in_dev[@]} > 0 )); then
  echo "ERROR: Rogue compose files found in sandbox/dev (SSOT violation):" >&2
  printf ' - %s\n' "${rogue_in_dev[@]}" >&2
  echo "Keep a single SSOT: sandbox/dev/compose.yml" >&2
  exit 1
fi

# 3) Validate compose renders deterministically
pushd "${SSOT_DIR}" >/dev/null
docker compose version
docker compose config >/tmp/compose.rendered.yml

if ! grep -qE '^\s*services:\s*$' /tmp/compose.rendered.yml; then
  echo "ERROR: docker compose config output missing 'services:' block" >&2
  exit 1
fi

echo "[compose-ssot] OK"
popd >/dev/null
