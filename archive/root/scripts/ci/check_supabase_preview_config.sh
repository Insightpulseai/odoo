#!/usr/bin/env bash
# =============================================================================
# Supabase Preview Branches Configuration Checker
# =============================================================================
# Validates that the Supabase directory structure matches expected integration
# settings to prevent "ignored / no changes" false positives.
#
# Usage: ./scripts/ci/check_supabase_preview_config.sh
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SUPABASE_ROOT="${SUPABASE_ROOT:-supabase}"
EXPECTED_CONFIG="${SUPABASE_ROOT}/.supabase-preview-config.json"

echo "=== Supabase Preview Branches Configuration Check ==="
echo ""

# Check 1: Supabase root exists
if [[ -d "$SUPABASE_ROOT" ]]; then
    echo -e "${GREEN}✓${NC} Supabase root directory exists: $SUPABASE_ROOT/"
else
    echo -e "${RED}✗${NC} Supabase root directory NOT found: $SUPABASE_ROOT/"
    exit 1
fi

# Check 2: config.toml exists
if [[ -f "$SUPABASE_ROOT/config.toml" ]]; then
    echo -e "${GREEN}✓${NC} config.toml exists"
else
    echo -e "${RED}✗${NC} config.toml NOT found"
    exit 1
fi

# Check 3: migrations directory exists
if [[ -d "$SUPABASE_ROOT/migrations" ]]; then
    MIGRATION_COUNT=$(find "$SUPABASE_ROOT/migrations" -name "*.sql" 2>/dev/null | wc -l)
    echo -e "${GREEN}✓${NC} migrations/ directory exists ($MIGRATION_COUNT SQL files)"
else
    echo -e "${YELLOW}!${NC} migrations/ directory NOT found (may be intentional)"
fi

# Check 4: functions directory exists
if [[ -d "$SUPABASE_ROOT/functions" ]]; then
    FUNCTION_COUNT=$(find "$SUPABASE_ROOT/functions" -maxdepth 1 -type d 2>/dev/null | wc -l)
    FUNCTION_COUNT=$((FUNCTION_COUNT - 1)) # Subtract parent dir
    echo -e "${GREEN}✓${NC} functions/ directory exists ($FUNCTION_COUNT Edge Functions)"
else
    echo -e "${YELLOW}!${NC} functions/ directory NOT found (may be intentional)"
fi

# Check 5: NO nested supabase/supabase (common misconfiguration)
if [[ -d "$SUPABASE_ROOT/supabase" ]]; then
    echo -e "${RED}✗${NC} MISCONFIGURATION DETECTED: $SUPABASE_ROOT/supabase/ exists"
    echo ""
    echo "    The Supabase GitHub integration may be watching the wrong directory."
    echo "    Expected: supabase/"
    echo "    Found:    supabase/supabase/"
    echo ""
    echo "    Fix: Remove nested directory or update integration settings."
    exit 1
else
    echo -e "${GREEN}✓${NC} No nested supabase/supabase/ (correct structure)"
fi

# Check 6: Extract project_id from config.toml
PROJECT_ID=$(grep -E "^project_id" "$SUPABASE_ROOT/config.toml" 2>/dev/null | sed 's/.*= *"\([^"]*\)".*/\1/' || echo "")
if [[ -n "$PROJECT_ID" ]]; then
    echo -e "${GREEN}✓${NC} project_id: $PROJECT_ID"
else
    echo -e "${YELLOW}!${NC} project_id not found in config.toml"
fi

echo ""
echo "=== Configuration Summary ==="
echo ""
echo "Supabase Dashboard Integration Settings should be:"
echo "  Project ref:        $PROJECT_ID"
echo "  Watched directory:  supabase/"
echo ""
echo "Dashboard URL: https://supabase.com/dashboard/project/$PROJECT_ID/settings/integrations"
echo ""

# Check if there are supabase changes in current branch vs main
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "=== PR Change Detection ==="
    git fetch origin main --quiet 2>/dev/null || true
    if git diff --name-only origin/main...HEAD 2>/dev/null | grep -q "^supabase/"; then
        echo -e "${GREEN}✓${NC} This PR contains Supabase changes - preview should trigger"
        git diff --name-only origin/main...HEAD 2>/dev/null | grep "^supabase/" | head -10
    else
        echo -e "${YELLOW}!${NC} No Supabase changes in this PR - preview will be skipped (expected)"
    fi
fi

echo ""
echo -e "${GREEN}All checks passed.${NC}"
exit 0
