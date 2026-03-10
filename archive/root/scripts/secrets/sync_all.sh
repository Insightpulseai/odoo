#!/usr/bin/env bash
set -euo pipefail

# -----------------------------------------------------------------------------
# SSOT Secret Registry Sync (metadata-only registry)
# - Reads infra/secrets/registry.yaml
# - Pushes secret VALUES from env vars into configured stores (GitHub, Supabase)
# - Never reads/writes secret values to disk
#
# Usage:
#   ./scripts/secrets/sync_all.sh               # sync everything possible
#   ONLY=github ./scripts/secrets/sync_all.sh   # sync only GitHub
#   ONLY=supabase ./scripts/secrets/sync_all.sh # sync only Supabase
#
# Requirements:
#   - python3
#   - pip install pyyaml (or run via CI that installs it)
#   - GitHub: gh authenticated (GITHUB_TOKEN acceptable in CI)
#   - Supabase: supabase authenticated (SUPABASE_ACCESS_TOKEN in CI or login)
# -----------------------------------------------------------------------------

REG="infra/secrets/registry.yaml"
ONLY="${ONLY:-all}"

die() { echo "ERROR: $*" >&2; exit 2; }
info() { echo "==> $*"; }

[[ -f "$REG" ]] || die "Missing $REG"

# Preflight tools
command -v python3 >/dev/null 2>&1 || die "python3 is required"
python3 -c "import yaml" >/dev/null 2>&1 || die "pyyaml missing. Install: python3 -m pip install pyyaml"

# Validate registry always
info "Validating SSOT secret registry"
./scripts/secrets/validate_registry.py

# Determine if tools exist
HAS_GH=0
HAS_SUPABASE=0
command -v gh >/dev/null 2>&1 && HAS_GH=1 || true
command -v supabase >/dev/null 2>&1 && HAS_SUPABASE=1 || true

# Print planned actions (no values)
info "Planning sync actions from registry (metadata only)"
python3 - <<'PY'
from pathlib import Path
import yaml
data = yaml.safe_load(Path("infra/secrets/registry.yaml").read_text())
for s in data.get("secrets", []):
    print(f"- {s.get('name')} -> store={s.get('store')} env_var={s.get('env_var')} required={bool(s.get('required'))}")
PY

# Helper: execute lines produced by scripts, but never echo values.
run_generated() {
  local script="$1"
  # shellcheck disable=SC2016
  local cmds
  cmds="$("$script")"
  if [[ -z "$cmds" ]]; then
    info "No commands produced by $script (nothing to sync)"
    return 0
  fi
  info "Executing commands from $script"
  # Execute line-by-line so failures are isolated
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    # Avoid printing secrets: line may contain ${ENVVAR} only
    info "RUN: ${line%%=*}..."
    eval "$line"
  done <<<"$cmds"
}

# GitHub sync
if [[ "$ONLY" == "all" || "$ONLY" == "github" ]]; then
  if [[ "$HAS_GH" -ne 1 ]]; then
    info "Skipping GitHub sync (gh not installed)"
  else
    info "Syncing GitHub Actions secrets"
    # Ensure gh auth is valid (CI can use GITHUB_TOKEN)
    if ! gh auth status >/dev/null 2>&1; then
      info "gh not authenticated; in CI set GITHUB_TOKEN or run: gh auth login"
      die "GitHub secret sync requires gh auth"
    fi
    run_generated "./scripts/secrets/sync_github_secrets.sh"
  fi
fi

# Supabase sync (Edge secrets)
if [[ "$ONLY" == "all" || "$ONLY" == "supabase" ]]; then
  if [[ "$HAS_SUPABASE" -ne 1 ]]; then
    info "Skipping Supabase sync (supabase CLI not installed)"
  else
    info "Syncing Supabase Edge secrets"
    # supabase CLI auth differs by environment; we just attempt a lightweight call
    # Link happens in the generated script; failure will be clear.
    run_generated "./scripts/secrets/sync_supabase_secrets.sh"
  fi
fi

info "Done."
