#!/usr/bin/env bash
# shellcheck shell=bash
# =============================================================================
# Workspace & DNS SSOT Verification Script
# =============================================================================
# Validates that workspace naming and DNS SSOT are correctly configured
#
# Usage:
#   ./scripts/verify-workspace-dns.sh
#
# Exit Codes:
#   0 - All checks passed
#   1 - One or more checks failed
#   2 - Missing required dependency
# =============================================================================

set -euo pipefail
trap 'echo "❌ FAILED at line ${LINENO}: ${BASH_COMMAND}" >&2' ERR

require_cmd() {
  local c="$1"
  command -v "$c" >/dev/null 2>&1 || {
    echo "❌ Missing required command: $c" >&2
    exit 2
  }
}

optional_cmd() {
  local c="$1"
  command -v "$c" >/dev/null 2>&1
}

DOCKER_OK=0
if optional_cmd docker; then
  if docker info >/dev/null 2>&1; then
    DOCKER_OK=1
  fi
fi

echo "== Preflight =="
require_cmd bash
require_cmd python3
optional_cmd jq || echo "⚠️ jq not found (some JSON checks may be skipped)"
optional_cmd yq || echo "⚠️ yq not found (some YAML checks may be skipped)"
optional_cmd dig || echo "⚠️ dig not found (DNS resolution checks may be skipped)"
if [ "$DOCKER_OK" -eq 1 ]; then
  echo "✅ Docker daemon reachable"
else
  echo "⚠️ Docker daemon NOT reachable — skipping docker-runtime checks"
fi
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PASS_COUNT=0
FAIL_COUNT=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================================================="
echo "Workspace & DNS SSOT Verification"
echo "========================================================================="
echo ""

# =============================================================================
# Workspace Naming Checks
# =============================================================================
echo "📦 Workspace Naming Checks"
echo "-------------------------"

# Check Docker Compose project name
if grep -q "^name: ipai$" "$REPO_ROOT/docker-compose.yml"; then
    echo -e "${GREEN}✅${NC} Docker Compose project: ipai"
    : $((PASS_COUNT++))
else
    echo -e "${RED}❌${NC} Docker Compose project: Expected 'ipai', got:"
    grep "^name:" "$REPO_ROOT/docker-compose.yml" || echo "  (not found)"
    : $((FAIL_COUNT++))
fi

# Check network name
if grep -q "name: ipai-network" "$REPO_ROOT/docker-compose.yml"; then
    echo -e "${GREEN}✅${NC} Network name: ipai-network"
    : $((PASS_COUNT++))
else
    echo -e "${RED}❌${NC} Network name: Expected 'ipai-network', got:"
    grep "name:.*network" "$REPO_ROOT/docker-compose.yml" || echo "  (not found)"
    : $((FAIL_COUNT++))
fi

# Check volume names
EXPECTED_VOLUMES=("ipai-pgdata" "ipai-redisdata" "ipai-web-data" "ipai-pgadmin-data")
for vol in "${EXPECTED_VOLUMES[@]}"; do
    if grep -q "name: $vol" "$REPO_ROOT/docker-compose.yml"; then
        echo -e "${GREEN}✅${NC} Volume: $vol"
        : $((PASS_COUNT++))
    else
        echo -e "${RED}❌${NC} Volume: $vol not found"
        : $((FAIL_COUNT++))
    fi
done

# Check DevContainer name
if grep -q '"name": "ipai-devcontainer"' "$REPO_ROOT/.devcontainer/devcontainer.json"; then
    echo -e "${GREEN}✅${NC} DevContainer name: ipai-devcontainer"
    : $((PASS_COUNT++))
else
    echo -e "${RED}❌${NC} DevContainer name: Expected 'ipai-devcontainer', got:"
    grep '"name":' "$REPO_ROOT/.devcontainer/devcontainer.json" || echo "  (not found)"
    : $((FAIL_COUNT++))
fi

echo ""

# =============================================================================
# DNS SSOT Checks
# =============================================================================
echo "🌐 DNS SSOT Checks"
echo "------------------"

# Check SSOT file exists
if [ -f "$REPO_ROOT/infra/dns/subdomain-registry.yaml" ]; then
    echo -e "${GREEN}✅${NC} SSOT file: subdomain-registry.yaml exists"
    : $((PASS_COUNT++))
else
    echo -e "${RED}❌${NC} SSOT file: subdomain-registry.yaml not found"
    : $((FAIL_COUNT++))
fi

# Check generator script exists and is executable
if [ -x "$REPO_ROOT/scripts/generate-dns-artifacts.sh" ]; then
    echo -e "${GREEN}✅${NC} Generator: generate-dns-artifacts.sh exists and is executable"
    : $((PASS_COUNT++))
else
    echo -e "${RED}❌${NC} Generator: generate-dns-artifacts.sh not found or not executable"
    : $((FAIL_COUNT++))
fi

# Check CI workflow exists
if [ -f "$REPO_ROOT/.github/workflows/dns-sync-check.yml" ]; then
    echo -e "${GREEN}✅${NC} CI workflow: dns-sync-check.yml exists"
    : $((PASS_COUNT++))
else
    echo -e "${RED}❌${NC} CI workflow: dns-sync-check.yml not found"
    : $((FAIL_COUNT++))
fi

# Check generated files exist
GENERATED_FILES=(
    "infra/cloudflare/envs/prod/subdomains.auto.tfvars"
    "docs/architecture/runtime_identifiers.json"
    "infra/dns/dns-validation-spec.json"
)

for file in "${GENERATED_FILES[@]}"; do
    if [ -f "$REPO_ROOT/$file" ]; then
        echo -e "${GREEN}✅${NC} Generated: $file exists"
        : $((PASS_COUNT++))
    else
        echo -e "${RED}❌${NC} Generated: $file not found"
        : $((FAIL_COUNT++))
    fi
done

# Check subdomain count consistency (requires yq and jq)
if command -v yq &> /dev/null && command -v jq &> /dev/null; then
    YAML_COUNT=$(yq eval '.subdomains | length' "$REPO_ROOT/infra/dns/subdomain-registry.yaml")
    JSON_COUNT=$(jq '.services | length' "$REPO_ROOT/docs/architecture/runtime_identifiers.json")

    if [ "$YAML_COUNT" -ge "$JSON_COUNT" ]; then
        echo -e "${GREEN}✅${NC} Subdomain count: YAML=$YAML_COUNT, JSON=$JSON_COUNT (consistent)"
        : $((PASS_COUNT++))
    else
        echo -e "${RED}❌${NC} Subdomain count mismatch: YAML=$YAML_COUNT, JSON=$JSON_COUNT"
        : $((FAIL_COUNT++))
    fi
else
    echo -e "${YELLOW}⚠️${NC}  Subdomain count check skipped (yq or jq not installed)"
fi

echo ""

# =============================================================================
# Documentation Checks
# =============================================================================
echo "📚 Documentation Checks"
echo "-----------------------"

# Check workspace naming docs
if [ -f "$REPO_ROOT/docs/ai/WORKSPACE_NAMING.md" ]; then
    echo -e "${GREEN}✅${NC} Workspace naming docs exist"
    : $((PASS_COUNT++))
else
    echo -e "${RED}❌${NC} Workspace naming docs not found"
    : $((FAIL_COUNT++))
fi

# Check DNS SSOT docs
if [ -f "$REPO_ROOT/infra/dns/README.md" ]; then
    echo -e "${GREEN}✅${NC} DNS SSOT docs exist"
    : $((PASS_COUNT++))
else
    echo -e "${RED}❌${NC} DNS SSOT docs not found"
    : $((FAIL_COUNT++))
fi

# Check CLAUDE.md references
if grep -q "ipai" "$REPO_ROOT/CLAUDE.md" && grep -q "subdomain-registry.yaml" "$REPO_ROOT/CLAUDE.md"; then
    echo -e "${GREEN}✅${NC} CLAUDE.md references workspace and DNS SSOT"
    : $((PASS_COUNT++))
else
    echo -e "${RED}❌${NC} CLAUDE.md missing workspace or DNS SSOT references"
    : $((FAIL_COUNT++))
fi

echo ""

# =============================================================================
# Summary
# =============================================================================
echo "========================================================================="
echo "Verification Summary"
echo "========================================================================="
TOTAL=$((PASS_COUNT + FAIL_COUNT))
echo "Total checks: $TOTAL"
echo -e "${GREEN}Passed: $PASS_COUNT${NC}"
if [ $FAIL_COUNT -gt 0 ]; then
    echo -e "${RED}Failed: $FAIL_COUNT${NC}"
else
    echo "Failed: $FAIL_COUNT"
fi
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "Workspace naming and DNS SSOT are correctly configured."
    exit 0
else
    echo -e "${RED}❌ Some checks failed.${NC}"
    echo ""
    echo "Please review the failures above and fix the issues."
    exit 1
fi
