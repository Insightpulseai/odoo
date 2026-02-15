#!/usr/bin/env bash
set -euo pipefail

echo "[post-create] InsightPulseAI Odoo DevContainer Setup"

# ===== Tool Bootstrap (New from Spec Kit pattern) =====

# 1) Ensure corepack (pnpm) available
if command -v corepack >/dev/null 2>&1; then
  echo "[post-create] enabling corepack for pnpm..."
  corepack enable >/dev/null 2>&1 || true
  corepack prepare pnpm@latest --activate >/dev/null 2>&1 || true
fi

# 2) Install uv (fast Python tool manager) if missing
if ! command -v uv >/dev/null 2>&1; then
  echo "[post-create] installing uv..."
  curl -fsSL https://astral.sh/uv/install.sh | sh
  # shellcheck disable=SC1091
  source "$HOME/.cargo/env" 2>/dev/null || true
fi

# 3) Install specify-cli (Spec Kit) as a tool if missing
if ! command -v specify >/dev/null 2>&1; then
  echo "[post-create] installing specify-cli..."
  uv tool install specify-cli --from "git+https://github.com/github/spec-kit.git" || true
fi

# ===== Existing Database Setup Logic (Preserved) =====

# Python version check
python_version=$(python3 --version | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python $required_version or higher is required (found $python_version)"
    exit 1
fi

echo "✅ Python version: $python_version"

# PostgreSQL connectivity check with retry
echo "🔍 Waiting for PostgreSQL to be ready..."
max_retries=30
retry_count=0

# Start Docker Compose services first
echo "[post-create] Starting Docker Compose services..."
cd /workspaces/odoo
docker compose up -d || true

# Wait for db service to be ready
while ! docker compose -f /workspaces/odoo/docker-compose.yml exec -T db pg_isready -U odoo >/dev/null 2>&1; do
    retry_count=$((retry_count + 1))
    if [ $retry_count -ge $max_retries ]; then
        echo "❌ PostgreSQL is not available after $max_retries attempts"
        exit 1
    fi
    echo "   Waiting for PostgreSQL... (attempt $retry_count/$max_retries)"
    sleep 2
done

echo "✅ PostgreSQL is ready"

# Create databases (dev, stage, prod)
echo "📦 Creating databases..."
for db_name in odoo_dev odoo_stage odoo_prod; do
    if docker compose -f /workspaces/odoo/docker-compose.yml exec -T db psql -U odoo -lqt | cut -d \| -f 1 | grep -qw "$db_name"; then
        echo "   Database $db_name already exists"
    else
        docker compose -f /workspaces/odoo/docker-compose.yml exec -T db createdb -U odoo "$db_name" || true
        echo "   ✅ Created database: $db_name"
    fi
done

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install --quiet -r requirements.txt
    echo "   ✅ Dependencies installed"
fi

# Install dev tools
echo "🔧 Installing development tools..."
pip install --quiet black isort flake8 pre-commit pytest pytest-cov
echo "   ✅ Dev tools installed"

# Setup pre-commit hooks
if [ -f ".pre-commit-config.yaml" ]; then
    echo "🪝 Installing pre-commit hooks..."
    pre-commit install
    echo "   ✅ Pre-commit hooks installed"
fi

# Git safe directory
git config --global --add safe.directory /workspaces/odoo

# ===== Environment Info (Enhanced) =====

echo ""
echo "=== DevContainer Setup Complete ==="
echo "Python:  $(python --version 2>/dev/null || echo 'not found')"
echo "uv:      $(uv --version 2>/dev/null || echo 'not found')"
echo "Node:    $(node --version 2>/dev/null || echo 'not found')"
echo "pnpm:    $(pnpm --version 2>/dev/null || echo 'not found')"
echo "Docker:  $(docker --version 2>/dev/null || echo 'not found')"
echo "specify: $(specify --version 2>/dev/null || echo 'not found')"
echo ""
echo "📍 Odoo:      http://localhost:8069"
echo "📍 Database:  odoo_dev (default)"
echo ""
echo "🚀 Quick Start:"
echo "   docker compose up -d"
echo "   docker compose exec odoo odoo -d odoo_dev -u all"
echo ""
