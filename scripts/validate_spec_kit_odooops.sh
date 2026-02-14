#!/usr/bin/env bash
# Validates OdooOps Sh Spec Kit presence, structure, and completeness
set -euo pipefail

SLUG="odooops-sh"
BASE="spec/${SLUG}"

echo "=== Validating OdooOps Sh Spec Kit ==="

# Required spec kit files
REQUIRED_SPEC_FILES=(
  "${BASE}/constitution.md"
  "${BASE}/prd.md"
  "${BASE}/plan.md"
  "${BASE}/tasks.md"
)

# Check file existence and non-empty
for f in "${REQUIRED_SPEC_FILES[@]}"; do
  if [ ! -f "$f" ]; then
    echo "❌ Missing: $f"
    exit 1
  fi

  if [ ! -s "$f" ]; then
    echo "❌ Empty: $f"
    exit 1
  fi

  echo "✓ Found: $f"
done

# Basic structure checks (titles) - flexible matching
grep -q "^# " "${BASE}/constitution.md" || {
  echo "❌ constitution.md missing markdown title"
  exit 1
}

grep -q "^# " "${BASE}/prd.md" || {
  echo "❌ prd.md missing markdown title"
  exit 1
}

grep -q "^# " "${BASE}/plan.md" || {
  echo "❌ plan.md missing markdown title"
  exit 1
}

grep -q "^# " "${BASE}/tasks.md" || {
  echo "❌ tasks.md missing markdown title"
  exit 1
}

echo ""
echo "=== Checking Migration Files ==="

# Required migration files (Week 1-3)
REQUIRED_MIGRATIONS=(
  "supabase/migrations/20260213_000001_ops_rename_agent_tables.sql"
)

for f in "${REQUIRED_MIGRATIONS[@]}"; do
  if [ ! -f "$f" ]; then
    echo "❌ Missing migration: $f"
    exit 1
  fi

  echo "✓ Found migration: $f"
done

echo ""
echo "=== Checking Schema Documentation (Optional) ==="

# Optional schema documentation (Week 2)
OPTIONAL_SCHEMA_DOCS=(
  "${BASE}/schema.dbml"
  "${BASE}/erd.mmd"
)

SCHEMA_DOC_COUNT=0
for f in "${OPTIONAL_SCHEMA_DOCS[@]}"; do
  if [ -f "$f" ]; then
    echo "✓ Found: $f"
    SCHEMA_DOC_COUNT=$((SCHEMA_DOC_COUNT + 1))
  else
    echo "⏳ Planned (Week 2): $f"
  fi
done

echo ""
echo "=== Checking Prisma Schema (Optional) ==="

# Optional Prisma schema (Week 2)
if [ -f "prisma/schema.prisma" ]; then
  if grep -q "ops_" prisma/schema.prisma; then
    echo "✓ Prisma schema includes ops models"
  else
    echo "⏳ Prisma schema exists but ops models not yet defined (Week 2)"
  fi
else
  echo "⏳ Prisma schema not yet created (Week 2)"
fi

echo ""
echo "=== Validation Summary ==="
echo "✅ All required spec kit files present and valid"
echo "✅ All required migrations present"
echo "📊 Schema documentation: $SCHEMA_DOC_COUNT/2 files created (optional for Week 4)"
echo ""
echo "✅ SUCCESS: OdooOps Sh Spec Kit validation passed"
