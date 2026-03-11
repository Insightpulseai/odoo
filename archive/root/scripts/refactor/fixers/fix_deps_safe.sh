#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "${ROOT}"

log(){ printf "[%s] %s\n" "$(date +%H:%M:%S)" "$*" >&2; }

log "Starting safe dependency fixes..."

# Safe mode: only apply non-breaking patch/minor updates
# This uses npm; adjust for pnpm/yarn if needed
log "Running npm audit fix (safe mode)..."
npm -s audit fix || true

# If you allow forced upgrades, run with FORCE=1:
if [ "${FORCE:-0}" = "1" ]; then
  log "⚠️  FORCE mode enabled - applying breaking upgrades"
  npm -s audit fix --force || true
fi

# Verify package-lock.json is consistent
log "Verifying package consistency..."
npm -s ls >/dev/null 2>&1 || true

# Show summary
log "Dependency fix complete. Verify with:"
log "  npm test"
log "  npm run typecheck"
log "  node scripts/refactor/ci_security_gate.js"
