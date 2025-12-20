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

echo "== Health Check Complete =="
