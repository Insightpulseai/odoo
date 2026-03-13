#!/usr/bin/env bash
# IPAI Secrets Audit Script
# Verifies secrets are properly configured across all platforms
# Does NOT expose secret values - only checks presence and structure
#
# Usage:
#   ./scripts/check_secrets.sh
#   REPO_ROOT=/path/to/repo ./scripts/check_secrets.sh

set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$REPO_ROOT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo "== IPAI Secrets Audit =="
echo "Repo root: $REPO_ROOT"
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

missing=0
warnings=0

# -----------------------------------------------------------------------------
# [1/5] Repo secret scan (no secrets in git)
# -----------------------------------------------------------------------------
echo -e "${GREEN}== [1/5] Repo secret scan (no secrets in git) ==${NC}"
if [[ -x scripts/secret-scan.sh ]]; then
  if scripts/secret-scan.sh; then
    echo -e "${GREEN}PASS: No secrets detected in repository${NC}"
  else
    echo -e "${RED}FAIL: scripts/secret-scan.sh reported issues${NC}"
    missing=1
  fi
else
  echo -e "${YELLOW}WARN: scripts/secret-scan.sh not found or not executable${NC}"
  warnings=$((warnings + 1))
fi
echo

# -----------------------------------------------------------------------------
# [2/5] Supabase secrets (control plane, Vault/Edge Functions)
# -----------------------------------------------------------------------------
echo -e "${GREEN}== [2/5] Supabase secrets (Edge Functions) ==${NC}"
if command -v supabase >/dev/null 2>&1; then
  if [[ -f supabase/config.toml ]]; then
    if supabase secrets list 2>/dev/null; then
      echo -e "${GREEN}PASS: Supabase secrets accessible${NC}"
    else
      echo -e "${YELLOW}WARN: supabase secrets list failed (may need auth or project link)${NC}"
      warnings=$((warnings + 1))
    fi
  else
    echo -e "${YELLOW}WARN: supabase/config.toml not found - skipping Supabase check${NC}"
    warnings=$((warnings + 1))
  fi
else
  echo -e "${YELLOW}WARN: supabase CLI not installed (npm i -g supabase)${NC}"
  warnings=$((warnings + 1))
fi
echo

# -----------------------------------------------------------------------------
# [3/5] Vercel env vars (Next.js apps, AI Gateway)
# -----------------------------------------------------------------------------
echo -e "${GREEN}== [3/5] Vercel project env vars ==${NC}"
if command -v vercel >/dev/null 2>&1; then
  if vercel env ls 2>/dev/null; then
    echo -e "${GREEN}PASS: Vercel env accessible${NC}"
  else
    echo -e "${YELLOW}WARN: vercel env ls failed (may need project link or auth)${NC}"
    warnings=$((warnings + 1))
  fi
else
  echo -e "${YELLOW}WARN: vercel CLI not installed (npm i -g vercel)${NC}"
  warnings=$((warnings + 1))
fi
echo

# -----------------------------------------------------------------------------
# [4/5] GitHub Secrets (CI/CD only)
# -----------------------------------------------------------------------------
echo -e "${GREEN}== [4/5] GitHub secrets (repo + org) ==${NC}"
if command -v gh >/dev/null 2>&1; then
  # Check auth status
  if gh auth status >/dev/null 2>&1; then
    echo "-- Repo secrets: jgtolentino/odoo-ce --"
    if gh secret list --repo jgtolentino/odoo-ce 2>/dev/null; then
      echo -e "${GREEN}PASS: Repo secrets accessible${NC}"
    else
      echo -e "${YELLOW}WARN: Unable to list repo secrets${NC}"
      warnings=$((warnings + 1))
    fi
    echo
    echo "-- Org secrets: insightpulseai-net --"
    if gh secret list --org insightpulseai-net 2>/dev/null; then
      echo -e "${GREEN}PASS: Org secrets accessible${NC}"
    else
      echo -e "${YELLOW}WARN: Unable to list org secrets (may need admin scope)${NC}"
      warnings=$((warnings + 1))
    fi
  else
    echo -e "${YELLOW}WARN: GitHub CLI not authenticated${NC}"
    warnings=$((warnings + 1))
  fi
else
  echo -e "${YELLOW}WARN: GitHub CLI 'gh' not installed${NC}"
  warnings=$((warnings + 1))
fi
echo

# -----------------------------------------------------------------------------
# [5/5] Local .env files structure check
# -----------------------------------------------------------------------------
echo -e "${GREEN}== [5/5] Local .env structure check ==${NC}"

# Check that .env files exist but are gitignored
env_files=(.env .env.local .env.production .env.development)
for ef in "${env_files[@]}"; do
  if [[ -f "$ef" ]]; then
    if git check-ignore -q "$ef" 2>/dev/null; then
      echo -e "${GREEN}OK: $ef exists and is gitignored${NC}"
    else
      echo -e "${RED}FAIL: $ef exists but is NOT gitignored - security risk!${NC}"
      missing=1
    fi
  fi
done

# Check .env.example exists
if [[ -f .env.example ]]; then
  echo -e "${GREEN}OK: .env.example exists (template for local setup)${NC}"
else
  echo -e "${YELLOW}WARN: .env.example not found (recommended for onboarding)${NC}"
  warnings=$((warnings + 1))
fi

# Check secrets inventory exists
if [[ -f config/secrets_inventory.md ]]; then
  echo -e "${GREEN}OK: config/secrets_inventory.md exists (secrets inventory)${NC}"
else
  echo -e "${YELLOW}WARN: config/secrets_inventory.md not found${NC}"
  warnings=$((warnings + 1))
fi
echo

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo "== SUMMARY =="
if [[ "$missing" -ne 0 ]]; then
  echo -e "${RED}RESULT: Secrets audit FAILED - $missing critical issue(s)${NC}"
  exit 1
elif [[ "$warnings" -gt 0 ]]; then
  echo -e "${YELLOW}RESULT: Secrets audit COMPLETED with $warnings warning(s)${NC}"
  echo "Warnings are non-blocking but should be addressed."
  exit 0
else
  echo -e "${GREEN}RESULT: Secrets audit PASSED - all checks green${NC}"
  exit 0
fi
