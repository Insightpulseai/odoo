#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$REPO_ROOT/scripts"

echo "=== Config/Secrets Inventory ==="
echo ""

# ─────────────────────────────────────────────────────────────
# 1) Scan repository for environment variable references
# ─────────────────────────────────────────────────────────────
echo "[1/4] Scanning repository for env var references..."

ENV_VARS_FILE="$OUT_DIR/env_vars_found.txt"
> "$ENV_VARS_FILE"

# Find all env var patterns (process.env.VAR_NAME)
rg --no-heading --no-ignore-vcs -g '!node_modules' -g '!.git' -g '!*.lock' \
  -o 'process\.env\.([A-Z_][A-Z0-9_]*)' -r '$1' "$REPO_ROOT" 2>/dev/null | \
  cut -d: -f2 >> "$ENV_VARS_FILE" || true

# Find Vite env vars (import.meta.env.VAR_NAME)
rg --no-heading --no-ignore-vcs -g '!node_modules' -g '!.git' -g '!*.lock' \
  -o 'import\.meta\.env\.([A-Z_][A-Z0-9_]*)' -r '$1' "$REPO_ROOT" 2>/dev/null | \
  cut -d: -f2 >> "$ENV_VARS_FILE" || true

# Find Python getenv calls (os.getenv("VAR_NAME"))
rg --no-heading --no-ignore-vcs -g '!node_modules' -g '!.git' -g '!*.lock' \
  -o 'getenv\(["\x27]([A-Z_][A-Z0-9_]*)["\x27]\)' -r '$1' "$REPO_ROOT" 2>/dev/null | \
  cut -d: -f2 >> "$ENV_VARS_FILE" || true

# Find dollar sign env vars in shell/config files ($VAR_NAME or ${VAR_NAME})
rg --no-heading --no-ignore-vcs -g '*.sh' -g '*.yml' -g '*.yaml' -g '.env*' -g 'docker-compose*' \
  -o '\$\{?([A-Z_][A-Z0-9_]*)\}?' -r '$1' "$REPO_ROOT" 2>/dev/null | \
  cut -d: -f2 >> "$ENV_VARS_FILE" || true

# Deduplicate
sort -u -o "$ENV_VARS_FILE" "$ENV_VARS_FILE"

ENV_COUNT=$(wc -l < "$ENV_VARS_FILE" | tr -d ' ')
echo "   Found $ENV_COUNT unique env var references"

# ─────────────────────────────────────────────────────────────
# 2) Enumerate config files
# ─────────────────────────────────────────────────────────────
echo "[2/4] Enumerating config files..."

CONFIG_FILES_LIST="$OUT_DIR/config_files_found.txt"
> "$CONFIG_FILES_LIST"

find "$REPO_ROOT" -type f \( \
  -name ".env*" -o \
  -name "*.config.js" -o \
  -name "*.config.ts" -o \
  -name "docker-compose*.yml" \
  \) \
  ! -path "*/node_modules/*" \
  ! -path "*/.git/*" \
  ! -path "*/dist/*" \
  >> "$CONFIG_FILES_LIST" || true

CONFIG_COUNT=$(wc -l < "$CONFIG_FILES_LIST" | tr -d ' ')
echo "   Found $CONFIG_COUNT config files"

# ─────────────────────────────────────────────────────────────
# 3) Generate simple inventory report
# ─────────────────────────────────────────────────────────────
echo "[3/4] Generating inventory report..."

INVENTORY_FILE="$OUT_DIR/CONFIG_INVENTORY.txt"

cat > "$INVENTORY_FILE" << EOF
Configuration & Secrets Inventory
Generated: $(date +%Y-%m-%d)
Repository: odoo-ce

====================================================
ENVIRONMENT VARIABLES ($ENV_COUNT found)
====================================================

EOF

cat "$ENV_VARS_FILE" >> "$INVENTORY_FILE"

cat >> "$INVENTORY_FILE" << EOF

====================================================
CONFIGURATION FILES ($CONFIG_COUNT found)
====================================================

EOF

while IFS= read -r file; do
  [[ -z "$file" ]] && continue
  relpath="${file#$REPO_ROOT/}"
  echo "$relpath" >> "$INVENTORY_FILE"
done < "$CONFIG_FILES_LIST"

cat >> "$INVENTORY_FILE" << EOF

====================================================
SECURITY GUARDRAILS
====================================================

- Secret scanning: scripts/secret-scan.sh
- Pre-commit hooks: .pre-commit-config.yaml
- CI workflow: .github/workflows/secret-scan.yml

Run secret scan:
  bash scripts/secret-scan.sh

EOF

echo "   Created: $INVENTORY_FILE"

# ─────────────────────────────────────────────────────────────
# 4) Create .env.example template
# ─────────────────────────────────────────────────────────────
echo "[4/4] Creating .env.example template..."

ENV_EXAMPLE="$OUT_DIR/.env.example"

cat > "$ENV_EXAMPLE" << EOF
# Environment Variables Template
# Generated: $(date +%Y-%m-%d)
# DO NOT commit .env with real values!

EOF

while IFS= read -r var; do
  [[ -z "$var" ]] && continue
  echo "${var}=" >> "$ENV_EXAMPLE"
done < "$ENV_VARS_FILE"

echo "   Created: $ENV_EXAMPLE"

# ─────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────
echo ""
echo "=== Inventory Complete ==="
echo ""
echo "Generated artifacts (scripts/ directory):"
echo "  ✓ CONFIG_INVENTORY.txt ($ENV_COUNT env vars, $CONFIG_COUNT files)"
echo "  ✓ .env.example (template with all keys)"
echo "  ✓ env_vars_found.txt (raw list)"
echo "  ✓ config_files_found.txt (raw list)"
echo ""
