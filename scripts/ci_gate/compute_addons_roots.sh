#!/usr/bin/env bash
# compute_addons_roots.sh - Compute addons roots in OCA-style repo
#
# Outputs newline-separated roots for gating.
# Used by gate_modules.sh to find all module locations.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Main addons directory
echo "$ROOT/addons"

# IPAI custom modules
if [ -d "$ROOT/addons/ipai" ]; then
  echo "$ROOT/addons/ipai"
fi

# OCA modules (each subdirectory is a separate repo)
OCA="$ROOT/addons/OCA"
if [ -d "$OCA" ]; then
  for d in "$OCA"/*; do
    [ -d "$d" ] && echo "$d"
  done
fi

# OCA lowercase (if exists)
OCA_LOWER="$ROOT/addons/oca"
if [ -d "$OCA_LOWER" ]; then
  for d in "$OCA_LOWER"/*; do
    [ -d "$d" ] && echo "$d"
  done
fi
