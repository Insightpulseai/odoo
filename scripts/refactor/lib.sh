#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
NOW_UTC="$(date -u +%Y%m%d-%H%M%S)"
EVIDENCE_DIR="${REPO_ROOT}/docs/evidence/${NOW_UTC}-naming-refactor"

log()  { printf "\n[refactor] %s\n" "$*"; }
warn() { printf "\n[refactor][WARN] %s\n" "$*" >&2; }
die()  { printf "\n[refactor][ERROR] %s\n" "$*" >&2; exit 1; }

need_cmd() { command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"; }

# Load config if present; otherwise use example defaults.
load_config() {
  local cfg="${REPO_ROOT}/scripts/refactor/naming.env"
  local ex="${REPO_ROOT}/scripts/refactor/naming.env.example"
  if [[ -f "$cfg" ]]; then
    # shellcheck disable=SC1090
    source "$cfg"
  else
    warn "Config not found at scripts/refactor/naming.env; using example defaults (copy naming.env.example -> naming.env to customize)."
    # shellcheck disable=SC1090
    source "$ex"
  fi

  : "${PHASE1_PKGS:=1}"
  : "${PHASE2_WEB:=1}"
  : "${PHASE2_DOCS_ARCH:=1}"
  : "${PHASE3_DB:=1}"
  : "${PHASE4_ADDONS_X:=1}"
  : "${PHASE5_ENFORCE:=1}"
  : "${CREATE_SUPABASE_SYMLINK:=1}"
  : "${CREATE_IPAI_SYMLINK:=0}"
  : "${LEGACY_PATTERNS:=packages/|apps/|docs/architecture/|supabase/|addons/ipai/}"
  : "${IGNORE_GLOBS:=docs/evidence/** node_modules/** .git/** **/*.lock}"
}

ensure_evidence_dir() {
  mkdir -p "$EVIDENCE_DIR"
  printf "%s\n" "timestamp_utc=${NOW_UTC}" > "${EVIDENCE_DIR}/meta.txt"
}

git_is_clean() {
  [[ -z "$(git status --porcelain)" ]]
}

git_checkpoint_or_die() {
  if ! git_is_clean; then
    die "Working directory not clean. Commit or stash before running (recommended: checkpoint branch + commit)."
  fi
}

# Move directory with git mv if exists and target doesn't already exist.
git_mv_dir() {
  local src="$1" dst="$2"
  if [[ -e "${REPO_ROOT}/${src}" && ! -e "${REPO_ROOT}/${dst}" ]]; then
    log "git mv ${src} -> ${dst}"
    git mv "${src}" "${dst}"
  else
    log "skip move ${src} -> ${dst} (src missing or dst exists)"
  fi
}

# Replace text references across repo (safe, idempotent)
rg_replace() {
  local from="$1" to="$2"
  log "replace: ${from} -> ${to}"
  local rg_args=(rg -n --hidden --no-ignore-vcs --glob '!.git/**')
  # ignore globs
  for g in $IGNORE_GLOBS; do rg_args+=(--glob "!${g}"); done

  if "${rg_args[@]}" -l "$from" >/dev/null 2>&1; then
    "${rg_args[@]}" -l "$from" | while IFS= read -r f; do
      # portable sed (macOS/BSD): use perl instead
      perl -0777 -i -pe "s/\Q${from}\E/${to}/g" "$f"
    done
  else
    log "no matches for '${from}'"
  fi
}

write_file() {
  local path="$1"
  shift
  mkdir -p "$(dirname "${REPO_ROOT}/${path}")"
  cat > "${REPO_ROOT}/${path}" <<'EOF'
EOF
  # overwrite with provided stdin by caller using heredoc via function? (not used)
  :
}

capture() {
  local name="$1"; shift
  ( set +e; "$@" ) > "${EVIDENCE_DIR}/${name}.out" 2> "${EVIDENCE_DIR}/${name}.err" || true
}
