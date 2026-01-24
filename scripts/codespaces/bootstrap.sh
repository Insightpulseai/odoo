#!/usr/bin/env bash
# ============================================================================
# Codespaces Bootstrap Script
# ============================================================================
# Description: Initializes the development environment in Codespaces or
#              compatible container environments (Claude Code Web, Codex, etc.)
# Usage: Called automatically by postCreateCommand in devcontainer.json
# ============================================================================

set -euo pipefail

echo "[codespaces] Bootstrap starting..."

# ============================================================================
# System Dependencies
# ============================================================================

if command -v apt-get >/dev/null 2>&1; then
  echo "[codespaces] Installing system dependencies..."
  sudo apt-get update -y
  sudo apt-get install -y --no-install-recommends \
    jq \
    curl \
    ripgrep \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    postgresql-client
fi

# ============================================================================
# Node.js Dependencies
# ============================================================================

if [ -f "package.json" ]; then
  echo "[codespaces] Installing Node.js dependencies..."
  npm ci || npm install
fi

# ============================================================================
# Python Dependencies
# ============================================================================

if [ -f "requirements.txt" ]; then
  echo "[codespaces] Installing Python dependencies..."
  pip3 install --user -r requirements.txt
fi

if [ -f "requirements-dev.txt" ]; then
  pip3 install --user -r requirements-dev.txt
fi

# ============================================================================
# Pre-commit Hooks
# ============================================================================

if [ -f ".pre-commit-config.yaml" ]; then
  echo "[codespaces] Installing pre-commit hooks..."
  pip3 install --user pre-commit
  pre-commit install || true
fi

# ============================================================================
# Supabase CLI (if not present)
# ============================================================================

if ! command -v supabase >/dev/null 2>&1; then
  echo "[codespaces] Installing Supabase CLI..."
  npm install -g supabase@latest || true
fi

# ============================================================================
# Docker Compose (Odoo stack)
# ============================================================================

DEV_COMPOSE_FILE="${DEV_COMPOSE_FILE:-docker-compose.yml}"
DEV_COMPOSE_PROJECT="${DEV_COMPOSE_PROJECT:-odoo-dev}"

if [ -f "$DEV_COMPOSE_FILE" ]; then
  echo "[codespaces] Pulling Docker images for development stack..."
  docker compose -p "$DEV_COMPOSE_PROJECT" -f "$DEV_COMPOSE_FILE" pull || true
else
  echo "[codespaces] WARN: DEV_COMPOSE_FILE not found: $DEV_COMPOSE_FILE"
  echo "[codespaces] Set DEV_COMPOSE_FILE to your canonical compose path"
fi

# ============================================================================
# Git Configuration
# ============================================================================

echo "[codespaces] Configuring Git..."
git config --global --add safe.directory /workspaces/odoo-ce
git config --global pull.rebase false

# ============================================================================
# Create local .env if not exists
# ============================================================================

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  echo "[codespaces] Creating .env from .env.example..."
  cp .env.example .env
fi

# ============================================================================
# Summary
# ============================================================================

echo "[codespaces] Bootstrap complete!"
echo ""
echo "Available commands:"
echo "  npm run dev           - Start development server"
echo "  docker compose up -d  - Start Odoo stack"
echo "  supabase start        - Start local Supabase"
echo ""
echo "Forwarded ports:"
echo "  8069  - Odoo Core"
echo "  54321 - Supabase API"
echo "  54323 - Supabase Studio"
echo "  3000  - Web app"
