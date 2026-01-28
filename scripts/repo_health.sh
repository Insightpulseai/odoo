#!/usr/bin/env bash
# =============================================================================
# Repository Health Check
# Quick validation of repo structure and agent-readiness.
#
# Usage:
#   ./scripts/repo_health.sh
# =============================================================================
set -euo pipefail

echo "== Repository Health Check =="
echo ""

# Git status
echo "Git Status:"
git status --porcelain=v1 2>/dev/null || echo "  (not a git repo or git not available)"
echo ""

# Required files
echo "Required Files:"
required=(
  "CLAUDE.md"
  "package.json"
)

for f in "${required[@]}"; do
  if [ -f "$f" ]; then
    echo "  OK: $f"
  else
    echo "  MISSING: $f"
  fi
done
echo ""

# Agent infrastructure
echo "Agent Infrastructure:"
agent_files=(
  ".claude/settings.json"
  ".claude/settings.local.json"
  ".claude/commands/plan.md"
  ".claude/commands/implement.md"
  ".claude/commands/verify.md"
  ".claude/commands/ship.md"
)

for f in "${agent_files[@]}"; do
  if [ -f "$f" ]; then
    echo "  OK: $f"
  else
    echo "  OPTIONAL: $f"
  fi
done
echo ""

# Spec bundles
echo "Spec Bundles:"
if [ -d "spec" ]; then
  bundles=$(find spec -mindepth 2 -maxdepth 2 -type f -name constitution.md -print 2>/dev/null | wc -l | tr -d ' ')
  echo "  Found: $bundles bundle(s)"
  if [ "$bundles" -gt 0 ]; then
    find spec -mindepth 2 -maxdepth 2 -type f -name constitution.md -print 2>/dev/null | while read -r cfile; do
      echo "    - $(dirname "$cfile" | xargs basename)"
    done
  fi
else
  echo "  No spec/ directory"
fi
echo ""

# Monorepo structure
echo "Monorepo Structure:"
mono_files=(
  "pnpm-workspace.yaml"
  "turbo.json"
  "apps/"
  "packages/"
)

for f in "${mono_files[@]}"; do
  if [ -e "$f" ]; then
    echo "  OK: $f"
  else
    echo "  OPTIONAL: $f"
  fi
done
echo ""

# Verification scripts
echo "Verification Scripts:"
verify_scripts=(
  "scripts/verify.sh"
  "scripts/ci_local.sh"
  "scripts/spec_validate.sh"
  "scripts/repo_health.sh"
)

for f in "${verify_scripts[@]}"; do
  if [ -f "$f" ]; then
    echo "  OK: $f"
  else
    echo "  OPTIONAL: $f"
  fi
done
echo ""

# Secret management infrastructure
echo "Secret Management:"
secret_files=(
  "scripts/claude/load_secrets_local.sh"
  "scripts/claude/load_secrets_remote.sh"
  "scripts/claude/run_agent.sh"
  "scripts/claude/setup_keychain.sh"
  "docs/SECRET_MANAGEMENT.md"
)

for f in "${secret_files[@]}"; do
  if [ -f "$f" ]; then
    echo "  OK: $f"
  else
    echo "  MISSING: $f"
  fi
done
echo ""

# Security audit (check for leaked secrets)
echo "Security Audit:"
echo "  Checking for leaked secrets in Git..."

# Common secret patterns
secret_patterns=(
  "sk-ant-"                           # Claude API keys
  "sk-proj-"                          # OpenAI API keys
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"  # JWT tokens (base64)
  "ghp_"                              # GitHub personal access tokens
  "gho_"                              # GitHub OAuth tokens
  "postgres://.+:.+@"                 # Connection strings with passwords
)

leaked=0
for pattern in "${secret_patterns[@]}"; do
  if git grep -nE "$pattern" -- ':!*.md' ':!*.example' ':!*.sample' 2>/dev/null | grep -v "SECRET_MANAGEMENT.md" | grep -v "repo_health.sh" > /dev/null; then
    echo "  ⚠ WARNING: Potential secret pattern found: $pattern"
    leaked=$((leaked + 1))
  fi
done

if [ "$leaked" -eq 0 ]; then
  echo "  ✅ No leaked secrets detected"
else
  echo "  ❌ CRITICAL: $leaked potential secret leak(s) detected!"
  echo "     Run: git grep -nE 'sk-ant-|eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9|ghp_|postgres://.+:.+@' to investigate"
fi
echo ""

echo "== Health Check Complete =="
