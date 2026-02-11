#!/bin/bash
set -e

echo "========================================"
echo "[postCreate] Odoo 19 Development Setup"
echo "========================================"

# Verify Python version
python_version=$(python3 --version | grep -oP '3\.\d+')
if [[ "$python_version" < "3.10" ]]; then
    echo "Python $python_version detected, Odoo 19 requires 3.10+"
    exit 1
fi
echo "Python $python_version"

# Wait for PostgreSQL
echo "Checking PostgreSQL connectivity..."
max_attempts=30
attempt=0
until pg_isready -h postgres -U odoo -d odoo || [ $attempt -eq $max_attempts ]; do
    attempt=$((attempt + 1))
    echo "  Waiting for PostgreSQL... ($attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "PostgreSQL connection failed after $max_attempts attempts"
    exit 1
fi
echo "PostgreSQL is ready"

# Create databases: odoo_dev, odoo_stage, odoo_prod
echo "Setting up databases..."
for db in odoo_dev odoo_stage odoo_prod; do
    psql -h postgres -U odoo -d odoo -tc \
        "SELECT 1 FROM pg_database WHERE datname = '$db';" \
        | grep -q 1 \
        || psql -h postgres -U odoo -d odoo -c \
        "CREATE DATABASE $db ENCODING 'UTF8' TEMPLATE template0;" \
        || true
    echo "  Database '$db': OK"
done
echo "Databases: odoo_dev (dev), odoo_stage (staging), odoo_prod (production)"

# Install Python dependencies
if [ -f /workspace/requirements.txt ]; then
    echo "Installing Python dependencies..."
    pip install --user -r /workspace/requirements.txt
fi

# Install dev tools
echo "Installing dev tools..."
pip install --user black isort flake8 pre-commit pytest psycopg2-binary || true

# Install pre-commit hooks
if [ -f /workspace/.pre-commit-config.yaml ]; then
    echo "Installing pre-commit hooks..."
    pre-commit install || true
fi

# Git safe directory
git config --global --add safe.directory /workspace

echo ""
echo "========================================"
echo "[postCreate] Setup Complete"
echo "========================================"
echo ""
echo "  python odoo-bin -d odoo_dev --addons-path=addons"
echo "  ./scripts/repo_health.sh"
echo ""
