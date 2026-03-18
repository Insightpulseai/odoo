#!/usr/bin/env bash
set -euo pipefail

# Repo-agnostic "best effort" verifier for code reviews.
# Runs whichever tooling is detected in the repository.
# Usage: .agent/skills/code-review/scripts/review_verify.sh

run_if() { command -v "$1" >/dev/null 2>&1 && "$@"; }

echo "🔍 Code Review Verification"
echo "=============================="
echo ""

# Git status
echo "📋 Git Status"
echo "-------------"
git status -sb || true
echo ""

# Python toolchain (Odoo, general Python)
if [ -f pyproject.toml ] || [ -f requirements.txt ] || [ -f setup.py ]; then
  echo "🐍 Python Toolchain Detected"
  echo "----------------------------"

  # Ruff (fast linter)
  if run_if ruff --version; then
    echo "Running ruff..."
    ruff check . || true
  fi

  # Black (formatter check)
  if run_if black --version; then
    echo "Running black..."
    black --check . || true
  fi

  # Flake8 (alternative linter)
  if run_if flake8 --version; then
    echo "Running flake8..."
    flake8 . || true
  fi

  # Pylint (comprehensive linter)
  if run_if pylint --version; then
    echo "Running pylint..."
    pylint --rcfile=.pylintrc addons/ || true
  fi

  # MyPy (type checking)
  if run_if mypy --version; then
    echo "Running mypy..."
    mypy . || true
  fi

  # Pytest (tests)
  if run_if pytest --version; then
    echo "Running pytest..."
    pytest -q || true
  fi

  echo ""
fi

# Node.js toolchain (frontend, OWL components)
if [ -f package.json ]; then
  echo "📦 Node.js Toolchain Detected"
  echo "-----------------------------"

  # Detect package manager
  if run_if pnpm -v; then
    PKG_MGR="pnpm"
  elif run_if yarn -v; then
    PKG_MGR="yarn"
  elif run_if npm -v; then
    PKG_MGR="npm"
  else
    echo "⚠️  No package manager found"
    PKG_MGR=""
  fi

  if [ -n "$PKG_MGR" ]; then
    # ESLint
    if grep -q '"lint"' package.json; then
      echo "Running $PKG_MGR lint..."
      $PKG_MGR run lint || true
    fi

    # Tests
    if grep -q '"test"' package.json; then
      echo "Running $PKG_MGR test..."
      $PKG_MGR test || true
    fi

    # Build
    if grep -q '"build"' package.json; then
      echo "Running $PKG_MGR build..."
      $PKG_MGR run build || true
    fi
  fi

  echo ""
fi

# Odoo-specific checks
if [ -d "addons" ] || [ -f "odoo-bin" ]; then
  echo "🔧 Odoo-Specific Checks"
  echo "----------------------"

  # Check for common Odoo issues
  echo "Checking for common anti-patterns..."

  # Check for hardcoded IDs
  if grep -r "id=\"[0-9]" addons/ 2>/dev/null | grep -v ".pyc" | head -5; then
    echo "⚠️  Found hardcoded IDs (use ref() instead)"
  fi

  # Check for sudo() without comments
  if grep -r "\.sudo()" addons/ 2>/dev/null | grep -v ".pyc" | grep -v "#" | head -5; then
    echo "⚠️  Found sudo() calls without justification comments"
  fi

  # Check for SQL injection risks
  if grep -r "execute.*%" addons/ 2>/dev/null | grep -v ".pyc" | head -5; then
    echo "⚠️  Potential SQL injection risk (use parameterized queries)"
  fi

  # Check for missing __init__.py
  find addons/ -type d -not -path "*/\.*" | while read -r dir; do
    if [ ! -f "$dir/__init__.py" ] && [ -n "$(find "$dir" -maxdepth 1 -name "*.py" 2>/dev/null)" ]; then
      echo "⚠️  Missing __init__.py in $dir"
    fi
  done

  echo ""
fi

# Pre-commit hooks
if [ -f .pre-commit-config.yaml ]; then
  echo "🪝 Pre-commit Hooks"
  echo "------------------"
  if run_if pre-commit --version; then
    echo "Running pre-commit..."
    pre-commit run --all-files || true
  fi
  echo ""
fi

# Security checks
echo "🔒 Security Checks"
echo "-----------------"

# Bandit (Python security)
if run_if bandit --version; then
  echo "Running bandit..."
  bandit -r . -ll || true
fi

# Safety (Python dependency vulnerabilities)
if run_if safety --version; then
  echo "Running safety..."
  safety check || true
fi

# npm audit (Node.js vulnerabilities)
if [ -f package.json ] && run_if npm -v; then
  echo "Running npm audit..."
  npm audit || true
fi

echo ""
echo "✅ Verification Complete"
echo "======================="
echo ""
echo "Review the output above for any issues."
echo "Address BLOCKER and MAJOR findings before merging."
