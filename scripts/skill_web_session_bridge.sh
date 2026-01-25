#!/usr/bin/env bash
# =============================================================================
# Web Session Command Bridge - Skill Entrypoint
# =============================================================================
# Prints environment-aware command templates for any change request.
# This is the canonical output surface for the "web-session-command-bridge" skill.
#
# Usage: ./scripts/skill_web_session_bridge.sh
# =============================================================================

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}== Web Session Command Bridge ==${NC}"
echo ""

# =============================================================================
# Environment Detection
# =============================================================================

env_kind="local"
[ -n "${CLAUDE_PROJECT_DIR:-}" ] && env_kind="claude-web"
[ -n "${CI:-}" ] && env_kind="ci"

has_docker="no"
command -v docker >/dev/null 2>&1 && has_docker="yes"

has_pnpm="no"
command -v pnpm >/dev/null 2>&1 && has_pnpm="yes"

has_python="no"
command -v python3 >/dev/null 2>&1 && has_python="yes"

echo -e "${GREEN}Environment:${NC}"
echo "  env_kind   = ${env_kind}"
echo "  docker     = ${has_docker}"
echo "  pnpm       = ${has_pnpm}"
echo "  python3    = ${has_python}"
echo ""

# =============================================================================
# Command Templates
# =============================================================================

echo -e "${YELLOW}### APPLY${NC}"
echo '```bash'
echo "git status"
echo "git add -A"
echo 'git commit -m "<type>(<scope>): <description>"'
echo '```'
echo ""

echo -e "${YELLOW}### TEST / VERIFY${NC}"
echo '```bash'
if [ -x ./scripts/ci/run_all.sh ]; then
    echo "./scripts/ci/run_all.sh"
elif [ -x ./scripts/verify_all.sh ]; then
    echo "./scripts/verify_all.sh"
elif [ -x ./scripts/ci_local.sh ]; then
    echo "./scripts/ci_local.sh"
else
    echo "# TODO: add ./scripts/ci/run_all.sh"
    echo "npm run lint && npm run test && npm run build"
fi
echo '```'
echo ""

echo -e "${YELLOW}### DOCS REFRESH${NC}"
echo '```bash'
if [ -x ./scripts/docs_refresh.sh ]; then
    echo "./scripts/docs_refresh.sh"
else
    echo "# (optional) add ./scripts/docs_refresh.sh"
fi
echo '```'
echo ""

echo -e "${YELLOW}### DEPLOY / MIGRATE${NC}"
echo '```bash'
if [ "${has_docker}" = "yes" ]; then
    if [ -f docker-compose.yml ] || [ -f deploy/docker-compose.yml ]; then
        echo "# Docker path available"
        echo "docker compose up -d"
        echo "docker compose logs -f --tail=100"
    else
        echo "# Docker available but no compose file found"
        echo "# Add docker-compose.yml for container deployments"
    fi
else
    echo "# No Docker - use platform deploy scripts or CI"
    if [ -f supabase/migrations ]; then
        echo "supabase db push"
    fi
    if [ -x ./scripts/deploy.sh ]; then
        echo "./scripts/deploy.sh"
    fi
fi
echo '```'
echo ""

echo -e "${YELLOW}### VALIDATE${NC}"
echo '```bash'
echo "git diff --exit-code"
if [ -x ./scripts/repo_health.sh ]; then
    echo "./scripts/repo_health.sh"
fi
if [ "${has_docker}" = "yes" ] && [ -f docker-compose.yml ]; then
    echo "docker compose ps"
    echo 'curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/health'
fi
echo '```'
echo ""

echo -e "${YELLOW}### ROLLBACK${NC}"
echo '```bash'
echo "git revert --no-edit HEAD"
echo "git push"
if [ "${has_docker}" = "yes" ] && [ -f docker-compose.yml ]; then
    echo "docker compose down && docker compose up -d"
fi
echo '```'
echo ""

# =============================================================================
# Available Scripts
# =============================================================================

echo -e "${GREEN}Available Repo Scripts:${NC}"
for script in \
    scripts/ci/run_all.sh \
    scripts/docs_refresh.sh \
    scripts/repo_health.sh \
    scripts/spec_validate.sh \
    scripts/ci_local.sh \
    scripts/verify_local.sh; do
    if [ -x "$script" ]; then
        echo "  ✓ $script"
    else
        echo "  · $script (not found)"
    fi
done
echo ""

echo -e "${BLUE}== Skill Contract: skills/web-session-command-bridge/skill.md ==${NC}"
