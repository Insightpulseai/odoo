#!/bin/bash
# OdooForge Codex Cloud Environment Setup
# Runs on Codex Cloud or Claude Code Web to bootstrap the environment

set -euo pipefail

echo "==> OdooForge Codex Setup"

# Upgrade pip and core tools
python -m pip install -U pip wheel setuptools --quiet

# Install dev dependencies
if [ -f requirements-dev.txt ]; then
  echo "==> Installing dev dependencies..."
  pip install -r requirements-dev.txt --quiet
elif [ -f requirements.txt ]; then
  echo "==> Installing base dependencies..."
  pip install -r requirements.txt --quiet
fi

# Install kit CLI dependencies
if [ -f kit-cli/requirements.txt ]; then
  echo "==> Installing kit CLI dependencies..."
  pip install -r kit-cli/requirements.txt --quiet
fi

# Install pre-commit hooks if available
if command -v pre-commit >/dev/null 2>&1; then
  echo "==> Setting up pre-commit hooks..."
  pre-commit install -f || true
fi

# Make scripts executable
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x kit-cli/kit.py 2>/dev/null || true

# Create symlink for kit command if not exists
if [ ! -L /usr/local/bin/kit ] && [ -f kit-cli/kit.py ]; then
  ln -sf "$(pwd)/kit-cli/kit.py" /usr/local/bin/kit 2>/dev/null || true
fi

# Verify kit is accessible
if command -v kit >/dev/null 2>&1 || python kit-cli/kit.py version >/dev/null 2>&1; then
  echo "==> Kit CLI: OK"
else
  echo "==> Kit CLI: Will use 'python kit-cli/kit.py'"
fi

echo "==> Codex setup complete"
