#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "Verifying refactor subagents setup..."

# Check script exists and is executable
if [ ! -x "${ROOT}/scripts/refactor/run_refactor_subagents.sh" ]; then
  echo "❌ Main script not executable"
  exit 1
fi
echo "✅ Main script exists and is executable"

# Check output directory can be created
mkdir -p "${ROOT}/out/refactor"
if [ ! -d "${ROOT}/out/refactor" ]; then
  echo "❌ Cannot create output directory"
  exit 1
fi
echo "✅ Output directory ready"

# Check CI workflow exists
if [ ! -f "${ROOT}/.github/workflows/refactor-subagents.yml" ]; then
  echo "❌ CI workflow not found"
  exit 1
fi
echo "✅ CI workflow configured"

# Check for required tools (informational)
echo ""
echo "Checking available tools (informational):"
command -v npm >/dev/null 2>&1 && echo "  ✅ npm" || echo "  ⚠️  npm not found"
command -v node >/dev/null 2>&1 && echo "  ✅ node" || echo "  ⚠️  node not found"
command -v rg >/dev/null 2>&1 && echo "  ✅ ripgrep" || echo "  ⚠️  ripgrep not found (will skip some checks)"

# Check package.json exists
if [ ! -f "${ROOT}/package.json" ]; then
  echo "  ⚠️  No package.json (script may need adjustments for Python-only repos)"
fi

echo ""
echo "✅ Refactor subagents setup verified"
echo ""
echo "Usage:"
echo "  Local: ./scripts/refactor/run_refactor_subagents.sh"
echo "  CI: Push to branch and create PR (workflow will run automatically)"
echo "  Results: out/refactor/ACTION_PLAN.md"
