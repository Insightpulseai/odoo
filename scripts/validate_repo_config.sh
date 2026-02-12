#!/usr/bin/env bash
# Repository configuration validation script
# Ensures SSOT compliance and environment configuration consistency
# Usage: ./scripts/validate_repo_config.sh

set -euo pipefail

ERRORS=0

echo "🔍 Validating Repository Configuration (SSOT Compliance)"
echo ""

# Check environment files exist
echo "📋 Checking environment files..."
for ENV in dev stage; do
  FILE="ops/compose/${ENV}.env"
  if [[ -f "$FILE" ]]; then
    echo "  ✅ $FILE exists"
  else
    echo "  ❌ $FILE is missing"
    ERRORS=$((ERRORS + 1))
  fi
done

if [[ -f "ops/compose/prod.env.example" ]]; then
  echo "  ✅ ops/compose/prod.env.example exists"
else
  echo "  ❌ ops/compose/prod.env.example is missing"
  ERRORS=$((ERRORS + 1))
fi

# Validate database naming convention
echo ""
echo "🗄️ Validating database naming (SSOT)..."
for ENV in dev stage; do
  FILE="ops/compose/${ENV}.env"
  if [[ -f "$FILE" ]]; then
    ODOO_DB=$(grep "^ODOO_DB=" "$FILE" | cut -d= -f2)
    POSTGRES_DB=$(grep "^POSTGRES_DB=" "$FILE" | cut -d= -f2)

    EXPECTED_DB="odoo_${ENV}"

    if [[ "$ODOO_DB" == "$EXPECTED_DB" ]] && [[ "$POSTGRES_DB" == "$EXPECTED_DB" ]]; then
      echo "  ✅ $ENV: database naming correct (odoo_${ENV})"
    else
      echo "  ❌ $ENV: database naming incorrect"
      echo "     Expected: $EXPECTED_DB"
      echo "     ODOO_DB: $ODOO_DB"
      echo "     POSTGRES_DB: $POSTGRES_DB"
      ERRORS=$((ERRORS + 1))
    fi
  fi
done

# Validate no hardcoded database names in docker-compose.yml
echo ""
echo "🐳 Checking docker-compose.yml for hardcoded database names..."
if grep -q "odoo_core\|odoo_db" docker-compose.yml 2>/dev/null; then
  echo "  ❌ Found hardcoded 'odoo_core' or 'odoo_db' in docker-compose.yml"
  echo "     Use environment variables instead: \${ODOO_DB:-odoo_dev}"
  ERRORS=$((ERRORS + 1))
else
  echo "  ✅ No hardcoded database names found"
fi

# Validate project name (SSOT)
echo ""
echo "📦 Validating compose project name..."
if grep -q "^COMPOSE_PROJECT_NAME=odoo$" ops/compose/project.env; then
  echo "  ✅ Project name is 'odoo' (SSOT compliant)"
else
  echo "  ❌ Project name is not 'odoo' or project.env is missing"
  ERRORS=$((ERRORS + 1))
fi

# Check for deprecated naming
echo ""
echo "🚫 Checking for deprecated naming conventions..."
DEPRECATED_PATTERNS=(
  "odoo-ce"
  "odoo-core"
  "odoo_core"
)

for PATTERN in "${DEPRECATED_PATTERNS[@]}"; do
  # Check docker-compose.yml and env files, excluding comment lines
  if grep -h "$PATTERN" docker-compose.yml ops/compose/*.env 2>/dev/null | grep -v "^#" | grep -q "$PATTERN"; then
    echo "  ⚠️  Found deprecated pattern: $PATTERN"
    echo "     Should use: odoo-app, odoo-db, odoo_dev, odoo_stage, odoo_prod"
    ERRORS=$((ERRORS + 1))
  fi
done

if [[ $ERRORS -eq 0 ]]; then
  echo "  ✅ No deprecated naming conventions found"
fi

# Validate environment scripts are executable
echo ""
echo "🔧 Checking environment scripts..."
for SCRIPT in up down smoke; do
  FILE="scripts/${SCRIPT}.sh"
  if [[ -x "$FILE" ]]; then
    echo "  ✅ $FILE is executable"
  else
    echo "  ❌ $FILE is not executable or missing"
    echo "     Run: chmod +x $FILE"
    ERRORS=$((ERRORS + 1))
  fi
done

# Final summary
echo ""
echo "=================================================="
if [[ $ERRORS -eq 0 ]]; then
  echo "✅ All configuration checks passed"
  echo "=================================================="
  exit 0
else
  echo "❌ Found $ERRORS configuration error(s)"
  echo "=================================================="
  exit 1
fi
