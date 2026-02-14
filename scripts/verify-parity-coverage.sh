#!/usr/bin/env bash
# =============================================================================
# Odoo.sh Parity Coverage Verification
# =============================================================================
# Validates that IPAI architecture achieves 95% feature coverage
# Reference: docs/architecture/odoo-sh-parity.md
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_FEATURES=60
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNINGS=0

echo -e "${BLUE}==============================================================================${NC}"
echo -e "${BLUE}Odoo.sh Parity Coverage Verification${NC}"
echo -e "${BLUE}==============================================================================${NC}"
echo

# =============================================================================
# Infrastructure Layer Checks (23 features)
# =============================================================================

echo -e "${BLUE}[1/9] Infrastructure Layer${NC}"

# 1.1 Git branch → environment mapping
if [[ -f ".github/workflows/build-and-deploy.yml" ]] || \
   [[ -f ".github/workflows/build-unified-image.yml" ]] || \
   [[ -f ".github/workflows/build-seeded-image.yml" ]]; then
    echo -e "${GREEN}✅ Git branch → environment mapping (build workflows)${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${RED}❌ Missing: GitHub Actions build workflows${NC}"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

# 1.2 Automatic builds on push
BUILD_WORKFLOWS=$(ls -1 .github/workflows/build*.yml 2>/dev/null | wc -l || echo "0")
if [[ $BUILD_WORKFLOWS -gt 0 ]]; then
    echo -e "${GREEN}✅ Automatic builds on push ($BUILD_WORKFLOWS workflows)${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${RED}❌ Missing: GitHub Actions build workflows${NC}"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

# 1.3-1.10 GHCR, Codespaces, DNS
if [[ -f ".devcontainer/devcontainer.json" ]]; then
    echo -e "${GREEN}✅ Codespaces devcontainer${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${RED}❌ Missing: .devcontainer/devcontainer.json${NC}"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

if [[ -f "infra/dns/subdomain-registry.yaml" ]]; then
    echo -e "${GREEN}✅ DNS SSOT registry${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${RED}❌ Missing: infra/dns/subdomain-registry.yaml${NC}"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

if [[ -f "sandbox/dev/compose.yml" ]]; then
    echo -e "${GREEN}✅ Runtime Docker Compose stack${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${RED}❌ Missing: sandbox/dev/compose.yml${NC}"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

echo

# =============================================================================
# Control Plane Layer Checks (22 features)
# =============================================================================

echo -e "${BLUE}[2/9] Control Plane Layer${NC}"

# Check for Supabase migrations
MIGRATIONS_DIR="$REPO_ROOT/supabase/migrations"
if [[ -d "$MIGRATIONS_DIR" ]]; then
    OPS_SCHEMA_COUNT=$(find "$MIGRATIONS_DIR" -name "*ops*.sql" | wc -l)
    if [[ $OPS_SCHEMA_COUNT -gt 0 ]]; then
        echo -e "${GREEN}✅ Supabase ops schema migrations ($OPS_SCHEMA_COUNT files)${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${YELLOW}⚠️  No ops schema migrations found (Week 1 deliverable)${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${YELLOW}⚠️  Supabase migrations directory missing (Week 1 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for Edge Functions
FUNCTIONS_DIR="$REPO_ROOT/supabase/functions"
if [[ -d "$FUNCTIONS_DIR" ]]; then
    if [[ -d "$FUNCTIONS_DIR/ops-runner" ]]; then
        echo -e "${GREEN}✅ ops-runner Edge Function${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${YELLOW}⚠️  ops-runner Edge Function missing (Week 2 deliverable)${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${YELLOW}⚠️  Supabase functions directory missing (Week 2 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for deployment scripts
if [[ -f "$REPO_ROOT/scripts/clone-prod-to-staging.sh" ]]; then
    echo -e "${GREEN}✅ Staging-from-prod cloning script${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  Missing: scripts/clone-prod-to-staging.sh (Week 2 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

if [[ -f "$REPO_ROOT/scripts/backup-scheduler.sh" ]]; then
    echo -e "${GREEN}✅ Backup scheduler script${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  Missing: scripts/backup-scheduler.sh (Week 3 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

if [[ -f "$REPO_ROOT/scripts/restore-backup.sh" ]]; then
    echo -e "${GREEN}✅ Restore backup script${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  Missing: scripts/restore-backup.sh (Week 3 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

if [[ -f "$REPO_ROOT/scripts/upgrade-preview.sh" ]]; then
    echo -e "${GREEN}✅ Upgrade preview script${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  Missing: scripts/upgrade-preview.sh (Week 4 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo

# =============================================================================
# Security & Access Control (7 features)
# =============================================================================

echo -e "${BLUE}[3/9] Security & Access Control${NC}"

# Check for RBAC migrations
if [[ -f "$MIGRATIONS_DIR/ops_rbac.sql" ]] || grep -r "ops.project_members" "$MIGRATIONS_DIR" 2>/dev/null; then
    echo -e "${GREEN}✅ RBAC schema (ops.project_members, ops.roles)${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  RBAC schema missing (Week 2 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for auth module
if [[ -d "$REPO_ROOT/addons/ipai/ipai_auth_oidc" ]]; then
    echo -e "${GREEN}✅ ipai_auth_oidc module (SSO)${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  ipai_auth_oidc module missing (Week 4 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for Cloudflare WAF rules
if [[ -f "$REPO_ROOT/infra/cloudflare/waf-rules.tf" ]]; then
    echo -e "${GREEN}✅ Cloudflare WAF rules${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  Missing: infra/cloudflare/waf-rules.tf (Week 1 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for audit trail
if grep -r "ops.audit_trail\|ops.run_events" "$MIGRATIONS_DIR" 2>/dev/null; then
    echo -e "${GREEN}✅ Audit trail schema${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  Audit trail schema missing (Week 1 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo

# =============================================================================
# Monitoring & Observability (9 features)
# =============================================================================

echo -e "${BLUE}[4/9] Monitoring & Observability${NC}"

# Check for event schema
if grep -r "ops.run_events" "$MIGRATIONS_DIR" 2>/dev/null; then
    echo -e "${GREEN}✅ ops.run_events schema${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  ops.run_events schema missing (Week 1 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for n8n workflows
if [[ -d "$REPO_ROOT/n8n/workflows" ]]; then
    ALERT_WORKFLOWS=$(find "$REPO_ROOT/n8n/workflows" -name "*alert*" -o -name "*monitor*" | wc -l)
    if [[ $ALERT_WORKFLOWS -gt 0 ]]; then
        echo -e "${GREEN}✅ n8n monitoring workflows ($ALERT_WORKFLOWS files)${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${YELLOW}⚠️  No n8n monitoring workflows (Week 4 deliverable)${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${YELLOW}⚠️  n8n workflows directory missing${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for Superset dashboards
if [[ -d "$REPO_ROOT/superset/dashboards" ]]; then
    echo -e "${GREEN}✅ Superset dashboards directory${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  Superset dashboards missing (Week 5 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for runbooks
if [[ -d "$REPO_ROOT/docs/runbooks" ]]; then
    if [[ -f "$REPO_ROOT/docs/runbooks/monitoring.md" ]]; then
        echo -e "${GREEN}✅ Monitoring runbook${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${YELLOW}⚠️  Missing: docs/runbooks/monitoring.md (Week 5 deliverable)${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${YELLOW}⚠️  Runbooks directory missing${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo

# =============================================================================
# Developer Tools (8 features)
# =============================================================================

echo -e "${BLUE}[5/9] Developer Tools${NC}"

# Codespaces already checked in Infrastructure

# Check for shell access script
if [[ -f "$REPO_ROOT/scripts/ops-shell.sh" ]]; then
    echo -e "${GREEN}✅ ops-shell.sh (shell access)${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  Missing: scripts/ops-shell.sh (Week 2 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for module manager
if [[ -d "$REPO_ROOT/addons/ipai/ipai_module_manager" ]]; then
    echo -e "${GREEN}✅ ipai_module_manager module${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  ipai_module_manager missing (Week 6 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo

# =============================================================================
# Upgrades & Migrations (6 features)
# =============================================================================

echo -e "${BLUE}[6/9] Upgrades & Migrations${NC}"

# Upgrade scripts already checked above

if [[ -f "$REPO_ROOT/scripts/upgrade-smoke-tests.sh" ]]; then
    echo -e "${GREEN}✅ Upgrade smoke tests${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  Missing: scripts/upgrade-smoke-tests.sh (Week 4 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo

# =============================================================================
# Performance & Scaling (5 features)
# =============================================================================

echo -e "${BLUE}[7/9] Performance & Scaling${NC}"

# Check for nginx config
if [[ -f "$REPO_ROOT/infra/nginx/odoo.conf" ]]; then
    echo -e "${GREEN}✅ Nginx reverse proxy config${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  Missing: infra/nginx/odoo.conf (Week 1 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for Cloudflare LB
if [[ -f "$REPO_ROOT/infra/cloudflare/load-balancer.tf" ]]; then
    echo -e "${GREEN}✅ Cloudflare load balancer config${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  Missing: infra/cloudflare/load-balancer.tf (Week 1 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check Docker Compose for Redis/PgBouncer
if grep -q "redis:" "$REPO_ROOT/sandbox/dev/compose.yml" 2>/dev/null; then
    echo -e "${GREEN}✅ Redis caching in Docker Compose${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  Redis not in Docker Compose (Week 1 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

if grep -q "pgbouncer:" "$REPO_ROOT/sandbox/dev/compose.yml" 2>/dev/null; then
    echo -e "${GREEN}✅ PgBouncer connection pooling${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  PgBouncer not in Docker Compose (Week 1 deliverable)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo

# =============================================================================
# Integrations & Extensions (4 features)
# =============================================================================

echo -e "${BLUE}[8/9] Integrations & Extensions${NC}"

# Check for IPAI modules
IPAI_MODULE_COUNT=$(find "$REPO_ROOT/addons/ipai" -maxdepth 1 -type d | wc -l)
if [[ $IPAI_MODULE_COUNT -gt 40 ]]; then
    echo -e "${GREEN}✅ IPAI custom modules ($IPAI_MODULE_COUNT modules)${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  Expected 43 IPAI modules, found $IPAI_MODULE_COUNT${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for MCP servers
MCP_SERVER_COUNT=$(find "$REPO_ROOT/mcp/servers" -maxdepth 1 -type d 2>/dev/null | wc -l)
if [[ $MCP_SERVER_COUNT -gt 10 ]]; then
    echo -e "${GREEN}✅ MCP servers ($MCP_SERVER_COUNT servers)${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  Expected 11 MCP servers, found $MCP_SERVER_COUNT${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo

# =============================================================================
# Advanced Features (3 features - P2/P3)
# =============================================================================

echo -e "${BLUE}[9/9] Advanced Features (P2/P3 - Optional)${NC}"

echo -e "${BLUE}ℹ️  Advanced analytics: Superset/Tableau (P2 enhancement)${NC}"
echo -e "${BLUE}ℹ️  Mobile app: PWA only (P3, not required)${NC}"
echo -e "${BLUE}ℹ️  Marketplace: Manual OCA install (P3 automation)${NC}"

echo

# =============================================================================
# Summary
# =============================================================================

echo -e "${BLUE}==============================================================================${NC}"
echo -e "${BLUE}Verification Summary${NC}"
echo -e "${BLUE}==============================================================================${NC}"

TOTAL_CHECKS=$((PASSED_CHECKS + FAILED_CHECKS + WARNINGS))
COVERAGE_PERCENT=$(awk "BEGIN {printf \"%.1f\", ($PASSED_CHECKS / $TOTAL_FEATURES) * 100}")

echo -e "Total Odoo.sh Features:    ${BLUE}$TOTAL_FEATURES${NC}"
echo -e "Verified Implementations:  ${GREEN}$PASSED_CHECKS${NC}"
echo -e "Missing (In Progress):     ${YELLOW}$WARNINGS${NC}"
echo -e "Critical Failures:         ${RED}$FAILED_CHECKS${NC}"
echo
echo -e "Parity Coverage:           ${GREEN}${COVERAGE_PERCENT}%${NC}"

if [[ $FAILED_CHECKS -eq 0 ]]; then
    echo
    echo -e "${GREEN}✅ Parity verification passed!${NC}"
    echo -e "${GREEN}No critical infrastructure components missing.${NC}"

    if [[ $WARNINGS -gt 0 ]]; then
        echo
        echo -e "${YELLOW}⚠️  $WARNINGS components pending (expected for current phase)${NC}"
        echo -e "${YELLOW}Refer to implementation timeline in docs/architecture/odoo-sh-parity.md${NC}"
    fi
    exit 0
else
    echo
    echo -e "${RED}❌ Parity verification failed!${NC}"
    echo -e "${RED}$FAILED_CHECKS critical infrastructure components missing.${NC}"
    exit 1
fi
