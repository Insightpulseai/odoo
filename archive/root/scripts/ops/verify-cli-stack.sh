#!/usr/bin/env bash
set -euo pipefail

# CLI Tools Verification Script
# Purpose: Verify all CLI tools are installed and configured
# Usage: ./scripts/ops/verify-cli-stack.sh

echo "════════════════════════════════════════════════════════════════"
echo "CLI Stack Verification - Autonomous Enterprise"
echo "════════════════════════════════════════════════════════════════"
echo

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

check_tool() {
    local name=$1
    local cmd=$2
    local auth_check=${3:-}
    
    echo "─────────────────────────────────────────────────────────────────"
    echo "Checking: $name"
    echo "─────────────────────────────────────────────────────────────────"
    
    if command -v "$cmd" &> /dev/null; then
        version=$($cmd --version 2>&1 | head -n1 || echo "version unknown")
        echo -e "${GREEN}✅ INSTALLED${NC}: $version"
        PASS_COUNT=$((PASS_COUNT + 1))
        
        # Check authentication if provided
        if [ -n "$auth_check" ]; then
            echo "   Testing authentication..."
            if eval "$auth_check" &> /dev/null; then
                echo -e "   ${GREEN}✅ AUTHENTICATED${NC}"
            else
                echo -e "   ${YELLOW}⚠️  NOT AUTHENTICATED${NC}"
                echo "   Run: $cmd auth init / $cmd login"
                WARN_COUNT=$((WARN_COUNT + 1))
            fi
        fi
    else
        echo -e "${RED}❌ NOT INSTALLED${NC}"
        echo "   Install: make install-cli-tools"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
    echo
}

# ═══════════════════════════════════════════════════════════════════
# Core CLI Tools
# ═══════════════════════════════════════════════════════════════════

check_tool "GitHub CLI" "gh" "gh auth status"
check_tool "DigitalOcean CLI" "doctl" "doctl account get"
check_tool "Vercel CLI" "vercel" ""
check_tool "Supabase CLI" "supabase" ""
check_tool "jq (JSON processor)" "jq" ""
check_tool "Docker" "docker" "docker ps"
check_tool "Docker Compose" "docker" "docker compose version"

# ═══════════════════════════════════════════════════════════════════
# Optional Tools
# ═══════════════════════════════════════════════════════════════════

echo "─────────────────────────────────────────────────────────────────"
echo "Optional Tools:"
echo "─────────────────────────────────────────────────────────────────"

if command -v terraform &> /dev/null; then
    echo -e "${GREEN}✅ Terraform${NC}: $(terraform version -json 2>/dev/null | jq -r '.terraform_version' || terraform version | head -n1)"
else
    echo -e "${YELLOW}⚪ Terraform${NC}: Not installed (optional for IaC)"
fi

if command -v ansible &> /dev/null; then
    echo -e "${GREEN}✅ Ansible${NC}: $(ansible --version | head -n1)"
else
    echo -e "${YELLOW}⚪ Ansible${NC}: Not installed (optional for automation)"
fi

if command -v kubectl &> /dev/null; then
    echo -e "${GREEN}✅ kubectl${NC}: $(kubectl version --client --short 2>/dev/null || echo "installed")"
else
    echo -e "${YELLOW}⚪ kubectl${NC}: Not installed (optional for K8s)"
fi

echo

# ═══════════════════════════════════════════════════════════════════
# Environment Variables
# ═══════════════════════════════════════════════════════════════════

echo "─────────────────────────────────────────────────────────────────"
echo "Environment Variables:"
echo "─────────────────────────────────────────────────────────────────"

check_env() {
    local var=$1
    if [ -n "${!var:-}" ]; then
        echo -e "${GREEN}✅ $var${NC}: Set"
    else
        echo -e "${YELLOW}⚠️  $var${NC}: Not set"
        WARN_COUNT=$((WARN_COUNT + 1))
    fi
}

check_env "DIGITALOCEAN_ACCESS_TOKEN"
check_env "GITHUB_TOKEN"
check_env "VERCEL_TOKEN"
check_env "SUPABASE_ACCESS_TOKEN"

echo

# ═══════════════════════════════════════════════════════════════════
# DNS Verification
# ═══════════════════════════════════════════════════════════════════

echo "─────────────────────────────────────────────────────────────────"
echo "DNS Configuration:"
echo "─────────────────────────────────────────────────────────────────"

DOMAIN="insightpulseai.com"

if command -v dig &> /dev/null; then
    NAMESERVERS=$(dig "$DOMAIN" NS +short | head -n 3)
    
    if echo "$NAMESERVERS" | grep -q "digitalocean.com"; then
        echo -e "${GREEN}✅ DNS Delegated to DigitalOcean${NC}"
        echo "$NAMESERVERS"
    else
        echo -e "${YELLOW}⚠️  DNS NOT delegated to DigitalOcean${NC}"
        echo "Current nameservers:"
        echo "$NAMESERVERS"
        echo
        echo "To delegate: make dns-delegate"
        WARN_COUNT=$((WARN_COUNT + 1))
    fi
else
    echo -e "${YELLOW}⚠️  dig not installed (can't check DNS)${NC}"
fi

echo

# ═══════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════

echo "════════════════════════════════════════════════════════════════"
echo "Verification Summary"
echo "════════════════════════════════════════════════════════════════"
echo
echo -e "${GREEN}✅ Passed${NC}:  $PASS_COUNT"
echo -e "${YELLOW}⚠️  Warnings${NC}: $WARN_COUNT"
echo -e "${RED}❌ Failed${NC}:  $FAIL_COUNT"
echo

if [ $FAIL_COUNT -gt 0 ]; then
    echo "❌ Some tools are missing. Run: make install-cli-tools"
    exit 1
elif [ $WARN_COUNT -gt 0 ]; then
    echo "⚠️  Some tools need configuration. Review warnings above."
    exit 0
else
    echo "✅ All tools installed and configured!"
    echo
    echo "Ready for autonomous operations:"
    echo "  make dns-list          # Manage DNS"
    echo "  make gh-repos          # Manage GitHub"
    echo "  make infra-list        # Manage infrastructure"
    echo "  make provision-full-app NAME=myapp SUB=api  # Full provisioning"
    exit 0
fi
