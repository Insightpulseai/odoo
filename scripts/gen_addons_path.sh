#!/usr/bin/env bash
# =============================================================================
# gen_addons_path.sh — Deterministic Odoo addons-path generator
# =============================================================================
# Enumerates OCA repos (addons/oca/<repo>) and custom addons (addons/ipai)
# to produce a single, deterministic addons_path string.
#
# OCA-canonical: each OCA repo is its own folder in the addons path.
# This avoids module flattening at dev time while matching the Docker build
# strategy that flattens into /mnt/addons/oca at image build time.
#
# Outputs:
#   infra/odoo/addons-path.txt  — one path per line (human-readable)
#   infra/odoo/addons-path.env  — ODOO_ADDONS_PATH=comma,separated
#
# Usage:
#   ./scripts/gen_addons_path.sh            # generate from addons/oca/
#   ./scripts/gen_addons_path.sh --docker   # output Docker mount paths
# =============================================================================
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

DOCKER_MODE="${1:-}"

# ---------------------------------------------------------------------------
# Base paths (always included)
# ---------------------------------------------------------------------------
if [[ "$DOCKER_MODE" == "--docker" ]]; then
  # Paths inside the Docker container
  CORE="/usr/lib/python3/dist-pkgs/odoo/addons"
  IPAI="/mnt/extra-addons/ipai"
  OCA_PREFIX="/mnt/extra-addons/oca"
else
  # Paths relative to repo root (for odoo-bin local dev)
  CORE="."  # odoo core handled by odoo binary itself
  IPAI="addons/ipai"
  OCA_PREFIX="addons/oca"
fi

BASE=()
[[ "$DOCKER_MODE" == "--docker" ]] && BASE+=("$CORE")
BASE+=("$IPAI")

# ---------------------------------------------------------------------------
# OCA repos: enumerate addons/oca/<repo> alphabetically
# ---------------------------------------------------------------------------
# Cloned by: gitaggregate -c oca-aggregate.yml
OCA_REPOS=()
OCA_DIR="addons/oca"
if [[ -d "$OCA_DIR" ]]; then
  while IFS= read -r -d '' d; do
    name="$(basename "$d")"
    # Skip hidden dirs
    [[ "$name" == .* ]] && continue
    # Only include dirs that contain at least one __manifest__.py
    if find "$d" -maxdepth 2 -name "__manifest__.py" -print -quit 2>/dev/null | grep -q .; then
      OCA_REPOS+=("$OCA_PREFIX/$name")
    fi
  done < <(find "$OCA_DIR" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)
fi

ALL=("${BASE[@]}" "${OCA_REPOS[@]}")

# ---------------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------------
mkdir -p infra/odoo

printf "%s\n" "${ALL[@]}" > infra/odoo/addons-path.txt

# Comma-separated for odoo.conf / env var
JOINED=$(IFS=,; echo "${ALL[*]}")
echo "ODOO_ADDONS_PATH=$JOINED" > infra/odoo/addons-path.env

echo "Wrote:"
echo "  infra/odoo/addons-path.txt  (${#ALL[@]} paths)"
echo "  infra/odoo/addons-path.env"
echo ""
echo "Paths:"
printf "  %s\n" "${ALL[@]}"
