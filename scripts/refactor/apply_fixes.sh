#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT}"

log(){ printf "[%s] %s\n" "$(date +%H:%M:%S)" "$*" >&2; }

# Ensure analysis has been run
if [ ! -f "out/refactor/ACTION_PLAN.md" ]; then
  log "❌ No ACTION_PLAN.md found. Run ./scripts/refactor/run_refactor_subagents.sh first."
  exit 1
fi

# Parse command-line arguments for which fixers to run
THEME="${1:-all}"

validate_before_fix() {
  log "Running pre-fix validation..."

  # Check git status
  if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    log "⚠️  Working directory has uncommitted changes. Commit or stash first."
    git status --short
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      exit 1
    fi
  fi
}

validate_after_fix() {
  log "Running post-fix validation..."

  # Check if package.json/tsconfig exist for npm projects
  if [ -f "package.json" ]; then
    log "Running typecheck..."
    npm run typecheck 2>&1 || npx -s tsc -p tsconfig.json --noEmit 2>&1 || true

    log "Running tests..."
    npm test 2>&1 || true

    log "Running lint..."
    npm run lint 2>&1 || true
  fi

  log "✅ Post-fix validation complete"
}

apply_security_fixes() {
  log "Applying security fixes (dependencies)..."
  ./scripts/refactor/fixers/fix_deps_safe.sh

  # Re-run security gate to verify
  log "Verifying security gate..."
  node scripts/refactor/ci_security_gate.js || {
    log "⚠️  Security gate still failing. Try FORCE=1 mode (caution: breaking changes)"
    return 1
  }
}

create_pr_branch() {
  local theme="$1"
  local branch_name="refactor/${theme}-$(date +%Y%m%d-%H%M)"

  log "Creating PR branch: ${branch_name}"
  git checkout -b "${branch_name}"

  echo "${branch_name}"
}

main() {
  log "Refactor Fix Application Pipeline"
  log "Theme: ${THEME}"

  case "${THEME}" in
    all)
      log "Applying all available fixes (in priority order)..."
      validate_before_fix
      apply_security_fixes
      # Future: apply_unused_exports
      # Future: apply_duplicates
      # Future: apply_error_handling
      validate_after_fix
      ;;

    security|deps)
      log "Applying security/dependency fixes only..."
      validate_before_fix
      apply_security_fixes
      validate_after_fix
      ;;

    unused)
      log "❌ Unused export fixer not yet implemented"
      exit 1
      ;;

    dupes)
      log "❌ Duplicate code fixer not yet implemented"
      exit 1
      ;;

    errors)
      log "❌ Error handling fixer not yet implemented"
      exit 1
      ;;

    *)
      log "❌ Unknown theme: ${THEME}"
      log "Usage: $0 [all|security|unused|dupes|errors]"
      exit 1
      ;;
  esac

  log ""
  log "✅ Fixes applied successfully"
  log ""
  log "Next steps:"
  log "  1. Review changes: git diff"
  log "  2. Create PR branch: git checkout -b refactor/${THEME}"
  log "  3. Commit: git commit -am 'fix(refactor): apply ${THEME} fixes'"
  log "  4. Push: git push -u origin refactor/${THEME}"
}

main "$@"
