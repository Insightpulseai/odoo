#!/usr/bin/env bash
# docker_contract_check.sh — Fail-fast Docker runtime contract validation
#
# Verifies that the local Docker environment matches the canonical contract.
# Exits non-zero if the runtime is misconfigured.
#
# Usage:
#   ./scripts/dev/docker_contract_check.sh
#
# Canonical contract:
#   - Context: colima-odoo (Mac local dev)
#   - No hardcoded socket paths in DOCKER_HOST
#   - Colima profile "odoo" must be running

set -euo pipefail

CANONICAL_CONTEXT="colima-odoo"
ERRORS=0

echo "=== Docker Runtime Contract Check ==="
echo ""

# 1. Check if DOCKER_HOST is set (should NOT be for context-based routing)
if [ -n "${DOCKER_HOST:-}" ]; then
    echo "FAIL: DOCKER_HOST is set to '${DOCKER_HOST}'"
    echo "      Remove DOCKER_HOST from your shell env. Use Docker contexts instead."
    ERRORS=$((ERRORS + 1))
else
    echo "  OK: DOCKER_HOST is not set (using context-based routing)"
fi

# 2. Check active Docker context
ACTIVE_CONTEXT=$(docker context show 2>/dev/null || echo "unknown")
if [ "$ACTIVE_CONTEXT" = "$CANONICAL_CONTEXT" ]; then
    echo "  OK: Active context is '$CANONICAL_CONTEXT'"
else
    echo "WARN: Active context is '$ACTIVE_CONTEXT' (expected '$CANONICAL_CONTEXT')"
    echo "      This is OK if you are using 'docker --context $CANONICAL_CONTEXT' explicitly."
fi

# 3. Check if canonical context exists
if docker context inspect "$CANONICAL_CONTEXT" >/dev/null 2>&1; then
    echo "  OK: Context '$CANONICAL_CONTEXT' exists"
else
    echo "FAIL: Context '$CANONICAL_CONTEXT' does not exist"
    echo "      Create it with: colima start --profile odoo"
    ERRORS=$((ERRORS + 1))
fi

# 4. Check if Colima odoo profile is running
if command -v colima >/dev/null 2>&1; then
    if colima status --profile odoo >/dev/null 2>&1; then
        echo "  OK: Colima profile 'odoo' is running"
    else
        echo "FAIL: Colima profile 'odoo' is not running"
        echo "      Start it with: colima start --profile odoo"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "SKIP: Colima not installed (CI or non-Mac environment)"
fi

# 5. Check Docker daemon is reachable via canonical context (lightweight ping)
if docker --context "$CANONICAL_CONTEXT" version --format '{{.Server.Version}}' >/dev/null 2>&1; then
    DOCKER_VER=$(docker --context "$CANONICAL_CONTEXT" version --format '{{.Server.Version}}' 2>/dev/null || echo "?")
    echo "  OK: Docker daemon reachable via '$CANONICAL_CONTEXT' (server: $DOCKER_VER)"
else
    echo "FAIL: Cannot reach Docker daemon via '$CANONICAL_CONTEXT'"
    ERRORS=$((ERRORS + 1))
fi

# 6. Check for stale socket path references in repo
STALE_REFS=$(grep -rl '.colima/odoo/docker.sock' . --include='*.json' --include='*.yaml' --include='*.yml' --include='*.sh' --include='*.md' 2>/dev/null | grep -v node_modules | grep -v .git | head -5 || true)
if [ -n "$STALE_REFS" ]; then
    echo "WARN: Stale socket path references found in:"
    echo "$STALE_REFS" | sed 's/^/      /'
    echo "      These should use Docker context instead of hardcoded socket paths."
else
    echo "  OK: No stale socket path references found in repo"
fi

echo ""
if [ "$ERRORS" -gt 0 ]; then
    echo "RESULT: $ERRORS error(s) found. Fix before proceeding."
    exit 1
else
    echo "RESULT: Docker runtime contract is valid."
    exit 0
fi
