#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo "[postCreate] Setting up odoo-ce-18-dev"
echo "========================================"
echo ""

# --- System packages needed by Odoo & tooling ---
echo "[postCreate] Installing system dependencies..."
sudo apt-get update -y
sudo apt-get install -y \
  git \
  build-essential \
  libpq-dev \
  libxml2-dev \
  libxslt1-dev \
  libjpeg-dev \
  zlib1g-dev \
  libldap2-dev \
  libsasl2-dev \
  libffi-dev \
  libssl-dev \
  nodejs \
  npm \
  wkhtmltopdf \
  curl \
  netcat-openbsd \
  jq

# --- Install pnpm for monorepo management ---
echo "[postCreate] Installing pnpm..."
npm install -g pnpm || true

# --- Python deps for Odoo ---
echo "[postCreate] Installing Python dependencies..."

# Install from requirements.txt if it exists
if [ -f "requirements.txt" ]; then
  echo "  Found requirements.txt at repo root"
  pip install -r requirements.txt || true
fi

# Install additional dev dependencies
pip install \
  black \
  isort \
  flake8 \
  pre-commit \
  pytest \
  psycopg2-binary \
  || true

# --- Node.js tooling for monorepo / control-room frontends ---
if [ -f "package.json" ]; then
  echo "[postCreate] Installing Node dependencies at repo root..."
  pnpm install || npm install || true
fi

# --- PostgreSQL database bootstrap ---
echo "[postCreate] Configuring PostgreSQL..."

export PGHOST="${PGHOST:-localhost}"
export PGUSER="${POSTGRES_USER:-odoo}"
export PGPASSWORD="${POSTGRES_PASSWORD:-odoo}"
export PGPORT="${POSTGRES_PORT:-5432}"

# Wait for PostgreSQL to be ready
echo "  Waiting for PostgreSQL..."
for i in $(seq 1 30); do
  if pg_isready -h localhost -U "$PGUSER" -p "$PGPORT" 2>/dev/null; then
    echo "  PostgreSQL is ready!"
    break
  fi
  echo "  Waiting... ($i/30)"
  sleep 1
done

# Create databases if not exists
for db in odoo_dev odoo_core odoo_marketing odoo_accounting; do
  psql -tc "SELECT 1 FROM pg_database WHERE datname = '$db';" | grep -q 1 || \
    psql -c "CREATE DATABASE $db ENCODING 'UTF8' TEMPLATE template0;" || true
  echo "  Database '$db': OK"
done

echo "[postCreate] Current databases:"
psql -lqt 2>/dev/null || true

# --- Pre-commit hooks ---
if [ -f ".pre-commit-config.yaml" ]; then
  echo "[postCreate] Installing pre-commit hooks..."
  pre-commit install || true
fi

# --- Claude Code CLI placeholder ---
echo ""
echo "[postCreate] NOTE: Claude Code CLI installation placeholder"
echo "  To install Claude Code CLI, run:"
echo "    npm install -g @anthropic-ai/claude-code"
echo ""

# --- Print summary ---
echo ""
echo "========================================"
echo "[postCreate] Setup Complete!"
echo "========================================"
echo ""
echo "Available dev commands:"
echo "  make dev           - Start Odoo Core dev server"
echo "  make dev-minimal   - Start minimal stack (Postgres + Odoo)"
echo "  make dev-full      - Start full stack"
echo "  make dev-frontend  - Start Control Room frontend"
echo "  make dev-backend   - Start Control Room API"
echo "  make dev-status    - Show running services"
echo "  make dev-health    - Run health checks"
echo ""
echo "Forwarded ports:"
echo "  8069 - Odoo CE Core"
echo "  8070 - Odoo Marketing"
echo "  8071 - Odoo Accounting"
echo "  3000 - Control Room Dashboard"
echo "  5678 - n8n Workflows"
echo "  8766 - MCP Coordinator"
echo "  8789 - Control Room API"
echo ""
