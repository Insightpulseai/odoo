#!/usr/bin/env bash
set -euo pipefail
# shellcheck disable=SC1091
source "$(dirname "$0")/lib.sh"

load_config
ensure_evidence_dir

need_cmd git
need_cmd rg
need_cmd node || true
need_cmd pnpm || true
need_cmd python3 || true
need_cmd supabase || true

log "Checks: repo cleanliness (for CI, this can be dirty)"
capture git-status git status --porcelain=v1
capture git-branch git rev-parse --abbrev-ref HEAD
capture git-head git rev-parse HEAD

log "Check: legacy textual references must be zero"
# Build rg ignore args
rg_args=(rg -n --hidden --no-ignore-vcs --glob '!.git/**')
for g in $IGNORE_GLOBS; do rg_args+=(--glob "!${g}"); done

# Count matches
set +e
matches="$("${rg_args[@]}" -S --pcre2 "$LEGACY_PATTERNS" . 2>/dev/null | wc -l | tr -d ' ')"
set -e
printf "%s\n" "legacy_matches=${matches}" > "${EVIDENCE_DIR}/legacy_matches.txt"

if [[ "${matches}" != "0" ]]; then
  "${rg_args[@]}" -S --pcre2 "$LEGACY_PATTERNS" . > "${EVIDENCE_DIR}/legacy_hits.txt" || true
  die "Legacy references found: ${matches}. See ${EVIDENCE_DIR}/legacy_hits.txt"
fi

log "Check: workspace loads (pnpm list)"
if command -v pnpm >/dev/null 2>&1; then
  capture pnpm-list pnpm -s list --depth 0
else
  warn "pnpm not found; skipping pnpm list"
fi

log "Check: supabase CLI works (status)"
# If renamed supabase -> db, try workdir, else try default. Also tolerate symlink strategy.
if command -v supabase >/dev/null 2>&1; then
  if [[ -d "${REPO_ROOT}/db" ]]; then
    # Try modern workdir flag; if unsupported, fall back to default 'supabase' dir or symlink.
    if supabase --help 2>/dev/null | rg -q -- '--workdir'; then
      capture supabase-status supabase --workdir db status
    else
      capture supabase-status supabase status
    fi
  else
    capture supabase-status supabase status
  fi
else
  warn "supabase CLI not found; skipping supabase status"
fi

log "Check: Odoo addons discovered (scripts/odoo_list_addons.py if present)"
if [[ -f "${REPO_ROOT}/scripts/odoo_list_addons.py" ]]; then
  capture odoo-list-addons python3 "${REPO_ROOT}/scripts/odoo_list_addons.py"
else
  warn "scripts/odoo_list_addons.py not found; skipping"
fi

log "Checks complete. Evidence: ${EVIDENCE_DIR}"
