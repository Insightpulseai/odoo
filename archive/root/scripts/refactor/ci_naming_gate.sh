#!/usr/bin/env bash
set -euo pipefail

# shellcheck disable=SC1091
source "$(dirname "$0")/lib.sh"
load_config

need_cmd rg

# rg ignore args
rg_args=(rg -n --hidden --no-ignore-vcs --glob '!.git/**')
for g in $IGNORE_GLOBS; do rg_args+=(--glob "!${g}"); done

if "${rg_args[@]}" -S --pcre2 "$LEGACY_PATTERNS" . >/dev/null 2>&1; then
  echo "❌ Naming gate failed: legacy references found."
  "${rg_args[@]}" -S --pcre2 "$LEGACY_PATTERNS" . || true
  exit 1
fi

echo "✅ Naming gate passed: no legacy references detected."
