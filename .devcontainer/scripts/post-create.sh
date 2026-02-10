#!/bin/bash
set -e

echo "🔧 Odoo 19 Development - Post-Create Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verify Python version
python_version=$(python3 --version | grep -oP '3\.\d+')
if [[ "$python_version" < "3.11" ]]; then
    echo "⚠️  Warning: Python $python_version detected, Odoo 19 requires 3.11+"
    exit 1
fi
echo "✅ Python $python_version"

# Wait for PostgreSQL
echo "🔍 Checking PostgreSQL connectivity..."
max_attempts=30
attempt=0
until pg_isready -h postgres -U odoo -d postgres || [ $attempt -eq $max_attempts ]; do
    attempt=$((attempt + 1))
    echo "   Waiting for PostgreSQL... (attempt $attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ PostgreSQL connection failed after $max_attempts attempts"
    exit 1
fi
echo "✅ PostgreSQL is ready"

# Install Python dependencies
if [ -f requirements.txt ]; then
    echo "📦 Installing Python dependencies..."
    pip install --user -r requirements.txt
fi

# Install pre-commit hooks
if [ -f .pre-commit-config.yaml ]; then
    echo "🔒 Installing pre-commit hooks..."
    pip install --user pre-commit
    pre-commit install
fi

# Git safe directory
echo "🔧 Configuring Git safe directory..."
git config --global --add safe.directory /workspace

echo "✅ Post-create setup complete"
