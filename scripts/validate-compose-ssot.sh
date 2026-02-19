#!/usr/bin/env bash
set -euo pipefail

echo "🔍 Validating Docker Compose SSOT compliance..."

ALLOWLIST=".github/compose-allowlist.txt"

# 1. Check for unauthorized compose files
find . -type f \( -name "docker-compose*.yml" -o -name "compose.yaml" \) \
  -not -path "*/archive/*" -not -path "*/.git/*" -not -path "*/node_modules/*" \
  | while read -r file; do

  file_clean="${file#./}"  # Remove leading ./

  if ! grep -Fxq "$file_clean" "$ALLOWLIST"; then
    echo "❌ FAIL: Unauthorized compose file: $file_clean"
    echo "  Add to $ALLOWLIST or delete"
    exit 1
  fi
done

# 2. Check delegators use include:
while read -r file; do
  # Skip comment lines and empty lines
  [[ "$file" =~ ^#.*$ || -z "$file" ]] && continue

  # Skip "Authorized Independent Stacks"
  if [[ "$file" == infra/* || "$file" == sandbox/* ]]; then
    continue
  fi

  # Skip canonical SSOT
  if [[ "$file" == "docker-compose.yml" ]]; then
    continue
  fi

  # Delegators MUST have include:
  if [[ -f "$file" ]]; then
    if ! grep -q "^include:" "$file"; then
      echo "❌ FAIL: Delegator $file missing 'include:' directive"
      exit 1
    fi
  fi
done < "$ALLOWLIST"

# 3. Check delegators don't redefine core services
DELEGATORS=(
  "docker-compose.dev.yml"
  ".devcontainer/docker-compose.devcontainer.yml"
  "ipai-platform/compose.yaml"
)

for file in "${DELEGATORS[@]}"; do
  if [[ -f "$file" ]]; then
    if grep -qE "^\s+(db|redis|odoo):" "$file"; then
      echo "❌ FAIL: Delegator $file redefines core services (db/redis/odoo)"
      exit 1
    fi
  fi
done

# 4. Validate DB name is odoo_dev
find . -type f \( -name "docker-compose*.yml" -o -name "compose.yaml" \) \
  -not -path "*/archive/*" -not -path "*/.git/*" \
  | while read -r file; do

  if grep -q "POSTGRES_DB:" "$file"; then
    if ! grep -qE "POSTGRES_DB.*odoo_dev" "$file"; then
      echo "❌ FAIL: $file uses wrong DB name (must be odoo_dev)"
      grep "POSTGRES_DB" "$file"
      exit 1
    fi
  fi
done

# 5. Validate Odoo version is 19 (in active files)
ACTIVE_FILES=(
  "docker-compose.yml"
  "docker-compose.dev.yml"
)

for file in "${ACTIVE_FILES[@]}"; do
  if [[ -f "$file" ]]; then
    if grep -q "image: odoo:" "$file"; then
      if ! grep -qE "image: odoo:19(\.|$| )" "$file"; then
        echo "❌ FAIL: $file uses wrong Odoo version (must be 19)"
        grep "image: odoo:" "$file"
        exit 1
      fi
    fi
  fi
done

echo "✅ PASS: All compose files comply with SSOT standards"
