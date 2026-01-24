#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo "[postCreate] Setting up IPAI Odoo CE 18 Dev"
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
  superclaude \
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

# --- Claude Code CLI ---
echo ""
echo "[postCreate] Installing Claude Code CLI..."
npm install -g @anthropic-ai/claude-code 2>/dev/null || {
  echo "  Claude Code CLI not available via npm, skipping..."
}

# --- SuperClaude Framework ---
echo "[postCreate] Installing SuperClaude commands..."
superclaude install 2>/dev/null || {
  echo "  SuperClaude commands installation skipped"
}

# --- Supabase CLI Link ---
echo "[postCreate] Linking Supabase project..."
if [ -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
  echo "  Service role key found, linking project..."
  supabase link --project-ref "${SUPABASE_PROJECT_REF:-spdtwktxdalcfigzeqrz}" 2>/dev/null || true
else
  echo "  No service role key, skipping Supabase link"
  echo "  Set SUPABASE_SERVICE_ROLE_KEY in Codespaces secrets to enable"
fi

# --- Load environment from .env.local if exists ---
if [ -f ".env.local" ]; then
  echo "[postCreate] Loading .env.local..."
  set -a
  source .env.local
  set +a
fi

# --- Print summary ---
echo ""
echo "========================================"
echo "[postCreate] Setup Complete!"
echo "========================================"
echo ""
echo "🚀 IPAI Odoo CE 18 Development Environment"
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
echo "SuperClaude commands (if installed):"
echo "  /sc:research       - Deep web research"
echo "  /sc:implement      - Code implementation"
echo "  /sc:test           - Testing workflows"
echo "  /sc:pm             - Project management"
echo ""
echo "Supabase commands:"
echo "  supabase db push   - Push migrations"
echo "  supabase functions deploy - Deploy edge functions"
echo "  supabase status    - Check project status"
echo ""
echo "Verification:"
echo "  ./scripts/verify_supabase_full.sh  - Full Supabase audit"
echo "  ./scripts/repo_health.sh           - Repo health check"
echo ""
echo "Forwarded ports:"
echo "  8069  - Odoo CE Core"
echo "  8070  - Odoo Marketing"
echo "  8071  - Odoo Accounting"
echo "  3000  - Control Room Dashboard"
echo "  5678  - n8n Workflows"
echo "  8766  - MCP Coordinator"
echo "  8789  - Control Room API"
echo "  54321 - Supabase API"
echo "  54322 - Supabase Studio"
echo ""
echo "📚 Read CLAUDE.md for full documentation"
echo ""
