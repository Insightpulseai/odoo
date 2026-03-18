#!/bin/bash
#
# Fix broken ir.act_window action (missing tree view error)
#
# This script diagnoses and fixes the "View types not defined tree found in act_window"
# error by either removing 'tree' from view_mode or identifying the missing view.
#
# Usage:
#   ./scripts/odoo/fix_broken_action.sh ACTION_ID [--fix] [--container CONTAINER] [--db DATABASE]
#
# Examples:
#   ./scripts/odoo/fix_broken_action.sh 678              # Diagnose only
#   ./scripts/odoo/fix_broken_action.sh 678 --fix        # Diagnose and fix
#   ./scripts/odoo/fix_broken_action.sh 678 --fix --container odoo-erp-prod --db odoo
#

set -euo pipefail

# Defaults
ACTION_ID="${1:-}"
DO_FIX="false"
CONTAINER="${CONTAINER:-db}"
DATABASE="${DATABASE:-odoo}"
DB_USER="${DB_USER:-postgres}"

# Parse arguments
shift || true
while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            DO_FIX="true"
            shift
            ;;
        --container)
            CONTAINER="$2"
            shift 2
            ;;
        --db)
            DATABASE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ -z "$ACTION_ID" ]]; then
    echo "Usage: $0 ACTION_ID [--fix] [--container CONTAINER] [--db DATABASE]"
    echo ""
    echo "Examples:"
    echo "  $0 678              # Diagnose action 678"
    echo "  $0 678 --fix        # Diagnose and fix action 678"
    exit 1
fi

echo "=========================================="
echo "Odoo Action Diagnostic Tool"
echo "=========================================="
echo "Action ID:  $ACTION_ID"
echo "Container:  $CONTAINER"
echo "Database:   $DATABASE"
echo "Fix mode:   $DO_FIX"
echo ""

# Step 1: Get action details
echo "Step 1: Fetching action details..."
ACTION_INFO=$(docker exec -i "$CONTAINER" psql -U "$DB_USER" -d "$DATABASE" -t -A -F'|' -c "
SELECT id, name, res_model, view_mode, view_id
FROM ir_act_window
WHERE id = $ACTION_ID;
")

if [[ -z "$ACTION_INFO" ]]; then
    echo "ERROR: Action ID $ACTION_ID not found in database."
    exit 1
fi

IFS='|' read -r ID NAME RES_MODEL VIEW_MODE VIEW_ID <<< "$ACTION_INFO"

echo "  ID:         $ID"
echo "  Name:       $NAME"
echo "  Model:      $RES_MODEL"
echo "  View Mode:  $VIEW_MODE"
echo "  View ID:    ${VIEW_ID:-None}"
echo ""

# Step 2: Check if tree view exists for this model
echo "Step 2: Checking for tree views on model '$RES_MODEL'..."
TREE_VIEWS=$(docker exec -i "$CONTAINER" psql -U "$DB_USER" -d "$DATABASE" -t -c "
SELECT id, name, type
FROM ir_ui_view
WHERE model = '$RES_MODEL' AND type = 'tree'
ORDER BY id DESC
LIMIT 10;
")

if [[ -z "$TREE_VIEWS" || "$TREE_VIEWS" =~ ^[[:space:]]*$ ]]; then
    echo "  ⚠️  NO TREE VIEWS FOUND for model '$RES_MODEL'"
    NEEDS_FIX="true"
else
    echo "  ✓ Tree views found:"
    echo "$TREE_VIEWS" | sed 's/^/    /'
    NEEDS_FIX="false"
fi
echo ""

# Step 3: Check if 'tree' is in view_mode
HAS_TREE="false"
if [[ "$VIEW_MODE" == *"tree"* ]]; then
    HAS_TREE="true"
fi

echo "Step 3: Analysis"
echo "  View mode contains 'tree': $HAS_TREE"
echo "  Tree view exists: $(if [[ $NEEDS_FIX == 'true' ]]; then echo 'NO'; else echo 'YES'; fi)"
echo ""

# Step 4: Determine recommended fix
if [[ "$HAS_TREE" == "true" && "$NEEDS_FIX" == "true" ]]; then
    echo "DIAGNOSIS: Action $ACTION_ID references 'tree' view but no tree view exists for model '$RES_MODEL'."
    echo ""

    # Calculate new view_mode without 'tree'
    NEW_VIEW_MODE=$(echo "$VIEW_MODE" | sed 's/tree,//g; s/,tree//g; s/^tree$/form/')
    if [[ -z "$NEW_VIEW_MODE" ]]; then
        NEW_VIEW_MODE="form"
    fi

    echo "RECOMMENDED FIX:"
    echo "  Current view_mode: $VIEW_MODE"
    echo "  New view_mode:     $NEW_VIEW_MODE"
    echo ""

    if [[ "$DO_FIX" == "true" ]]; then
        echo "Applying fix..."

        # Backup first
        BACKUP_FILE="/tmp/ir_act_window_${ACTION_ID}_backup.csv"
        echo "  Backing up to $BACKUP_FILE..."
        docker exec -i "$CONTAINER" psql -U "$DB_USER" -d "$DATABASE" -c "\copy (SELECT * FROM ir_act_window WHERE id=$ACTION_ID) TO STDOUT WITH CSV HEADER" > "$BACKUP_FILE" 2>/dev/null || true

        # Apply fix
        echo "  Updating view_mode..."
        docker exec -i "$CONTAINER" psql -U "$DB_USER" -d "$DATABASE" -c "
UPDATE ir_act_window
SET view_mode = '$NEW_VIEW_MODE'
WHERE id = $ACTION_ID;
"
        echo "  ✓ Fix applied!"
        echo ""
        echo "Next steps:"
        echo "  1. Restart Odoo to clear cache:"
        echo "     docker restart odoo-erp-prod"
        echo ""
        echo "  2. Verify the action works in the UI"
        echo ""
        echo "  3. If you need to rollback:"
        echo "     docker exec -i $CONTAINER psql -U $DB_USER -d $DATABASE -c \\"
        echo "       \"UPDATE ir_act_window SET view_mode = '$VIEW_MODE' WHERE id = $ACTION_ID;\""
    else
        echo "To apply this fix, run:"
        echo "  $0 $ACTION_ID --fix"
        echo ""
        echo "Or manually:"
        echo "  docker exec -i $CONTAINER psql -U $DB_USER -d $DATABASE -c \\"
        echo "    \"UPDATE ir_act_window SET view_mode = '$NEW_VIEW_MODE' WHERE id = $ACTION_ID;\""
    fi
else
    echo "DIAGNOSIS: Action appears to be correctly configured."
    if [[ "$HAS_TREE" == "false" ]]; then
        echo "  - 'tree' is not in view_mode, so no tree view is needed."
    else
        echo "  - Tree view exists for model '$RES_MODEL'."
    fi
    echo ""
    echo "If you're still seeing errors, check:"
    echo "  1. The view_id might be pointing to a non-existent view"
    echo "  2. There might be XML syntax errors in the view definition"
    echo "  3. Required fields might be missing from the view"
fi

echo ""
echo "=========================================="
echo "Done"
echo "=========================================="
