#!/usr/bin/env bash
set -euo pipefail

fail() { echo "ERROR: $*" >&2; exit 1; }

# 1) addons rules
if [ -d addons ]; then
  while IFS= read -r -d '' p; do
    b="$(basename "$p")"
    case "$b" in
      ipai_*|_deprecated) : ;;
      .gitkeep) : ;;
      *) fail "addons/ contains non-IPAI module '$b' (move to vendor/ or rename to ipai_*)." ;;
    esac
  done < <(find addons -mindepth 1 -maxdepth 1 -type d -print0)
fi

# 2) forbid OCA folder under addons
if [ -d addons/OCA ] || [ -d addons/oca ]; then
  fail "OCA content must be under vendor/ (e.g., vendor/oca), not under addons/."
fi

echo "OK: repo layout validated."
