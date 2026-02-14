#!/usr/bin/env bash
set -euo pipefail
# shellcheck disable=SC1091
source "$(dirname "$0")/lib.sh"

usage() {
  cat <<'USAGE'
Usage:
  scripts/refactor/run_naming_refactor.sh [--dry-run]

Behavior:
  - Requires clean git working directory (safety)
  - Runs Phases 1..5 based on scripts/refactor/naming.env (or example defaults)
  - Writes evidence under docs/evidence/<utc>-naming-refactor/
USAGE
}

DRY_RUN=0
if [[ "${1:-}" == "--help" ]]; then usage; exit 0; fi
if [[ "${1:-}" == "--dry-run" ]]; then DRY_RUN=1; fi

load_config
ensure_evidence_dir

need_cmd git
need_cmd rg
need_cmd perl

git_checkpoint_or_die

log "Start naming refactor (dry_run=${DRY_RUN})"
capture pre-tree ls -la
capture pre-git-status git status --porcelain=v1

# ---------------- Phase 1: packages -> pkgs ----------------
if [[ "$PHASE1_PKGS" == "1" ]]; then
  log "Phase 1: packages/ -> pkgs/"
  if [[ "$DRY_RUN" == "0" ]]; then
    git_mv_dir "packages" "pkgs"
    rg_replace "packages/" "pkgs/"
    # common workspace patterns
    if [[ -f "${REPO_ROOT}/pnpm-workspace.yaml" ]]; then
      rg_replace "packages/*" "pkgs/*"
      rg_replace "packages/**" "pkgs/**"
    fi
  else
    warn "dry-run: would move packages -> pkgs and replace refs"
  fi
fi

# ---------------- Phase 2: apps -> web; docs/architecture -> docs/arch ----------------
if [[ "$PHASE2_WEB" == "1" ]]; then
  log "Phase 2A: apps/ -> web/"
  if [[ "$DRY_RUN" == "0" ]]; then
    git_mv_dir "apps" "web"
    rg_replace "apps/" "web/"
    if [[ -f "${REPO_ROOT}/pnpm-workspace.yaml" ]]; then
      rg_replace "apps/*" "web/*"
      rg_replace "apps/**" "web/**"
    fi
  else
    warn "dry-run: would move apps -> web and replace refs"
  fi
fi

if [[ "$PHASE2_DOCS_ARCH" == "1" ]]; then
  log "Phase 2B: docs/architecture/ -> docs/arch/"
  if [[ "$DRY_RUN" == "0" ]]; then
    git_mv_dir "docs/architecture" "docs/arch"
    rg_replace "docs/architecture/" "docs/arch/"
  else
    warn "dry-run: would move docs/architecture -> docs/arch and replace refs"
  fi
fi

# ---------------- Phase 3: supabase -> db ----------------
if [[ "$PHASE3_DB" == "1" ]]; then
  log "Phase 3: supabase/ -> db/"
  if [[ "$DRY_RUN" == "0" ]]; then
    # if supabase is symlink already, don't git mv; convert to real dir if needed
    if [[ -d "${REPO_ROOT}/supabase" && ! -e "${REPO_ROOT}/db" ]]; then
      git_mv_dir "supabase" "db"
      rg_replace "supabase/" "db/"
    else
      log "skip supabase -> db (supabase missing or db exists)"
      # still replace refs if any
      rg_replace "supabase/" "db/"
    fi

    if [[ "$CREATE_SUPABASE_SYMLINK" == "1" ]]; then
      if [[ ! -e "${REPO_ROOT}/supabase" && -d "${REPO_ROOT}/db" ]]; then
        log "Create compatibility symlink: supabase -> db"
        ln -s "db" "${REPO_ROOT}/supabase"
      fi
    fi
  else
    warn "dry-run: would move supabase -> db, replace refs, optional symlink"
  fi
fi

# ---------------- Phase 4: addons/ipai -> addons/x ----------------
if [[ "$PHASE4_ADDONS_X" == "1" ]]; then
  log "Phase 4: addons/ipai/ -> addons/x/"
  if [[ "$DRY_RUN" == "0" ]]; then
    if [[ -d "${REPO_ROOT}/addons/ipai" && ! -e "${REPO_ROOT}/addons/x" ]]; then
      mkdir -p "${REPO_ROOT}/addons"
      git_mv_dir "addons/ipai" "addons/x"
      rg_replace "addons/ipai/" "addons/x/"
      # update common addon_path occurrences
      rg_replace "addons/ipai" "addons/x"
    else
      log "skip move addons/ipai -> addons/x (src missing or dst exists)"
      rg_replace "addons/ipai/" "addons/x/"
      rg_replace "addons/ipai" "addons/x"
    fi

    if [[ "$CREATE_IPAI_SYMLINK" == "1" ]]; then
      if [[ ! -e "${REPO_ROOT}/addons/ipai" && -d "${REPO_ROOT}/addons/x" ]]; then
        log "Create compatibility symlink: addons/ipai -> addons/x"
        mkdir -p "${REPO_ROOT}/addons"
        ln -s "x" "${REPO_ROOT}/addons/ipai"
      fi
    fi
  else
    warn "dry-run: would move addons/ipai -> addons/x and replace refs"
  fi
fi

# ---------------- Phase 5: docs + CI enforcement ----------------
if [[ "$PHASE5_ENFORCE" == "1" ]]; then
  log "Phase 5: write docs/NAMING.md + CI gate"
  if [[ "$DRY_RUN" == "0" ]]; then
    cat > "${REPO_ROOT}/docs/NAMING.md" <<'MD'
# Repository Naming Convention (Enforced)

This repo uses deterministic folder names to avoid collisions with Odoo terminology and to keep tooling predictable.

## Canonical folders
- `pkgs/` — workspace packages (shared libraries)
- `web/` — web applications (frontends)
- `docs/arch/` — architecture documentation
- `db/` — Supabase project directory (migrations, functions, config)
- `addons/x/` — organization addon collection (module names remain `ipai_*`)

## Compatibility notes
- If present, `supabase` may be a symlink to `db` for tooling compatibility.
- Avoid textual references to legacy paths. CI blocks PRs that reintroduce:
  - `packages/`, `apps/`, `docs/architecture/`, `supabase/`, `addons/ipai/`

## How to run the refactor
- Install config: copy `scripts/refactor/naming.env.example` → `scripts/refactor/naming.env`
- Execute: `scripts/refactor/run_naming_refactor.sh`
- Verify: `scripts/refactor/checks.sh`

MD

    cat > "${REPO_ROOT}/scripts/refactor/ci_naming_gate.sh" <<'CI'
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
CI
    chmod +x "${REPO_ROOT}/scripts/refactor/ci_naming_gate.sh"

    cat > "${REPO_ROOT}/.github/workflows/naming-gate.yml" <<'YML'
name: naming-gate

on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  naming-gate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install ripgrep
        run: sudo apt-get update && sudo apt-get install -y ripgrep

      - name: Install pnpm
        run: corepack enable && corepack prepare pnpm@latest --activate

      - name: Run naming gate (no legacy refs)
        run: ./scripts/refactor/ci_naming_gate.sh
YML
  else
    warn "dry-run: would write docs/NAMING.md and CI gate"
  fi
fi

# ---------------- Post: show diff + run checks ----------------
if [[ "$DRY_RUN" == "0" ]]; then
  capture post-git-status git status --porcelain=v1
  capture post-diffstat git diff --stat
  log "Run checks (will fail if legacy refs remain)"
  "${REPO_ROOT}/scripts/refactor/checks.sh" || die "Checks failed. See evidence dir: ${EVIDENCE_DIR}"
  log "SUCCESS. Evidence: ${EVIDENCE_DIR}"
else
  log "Dry run complete."
fi
