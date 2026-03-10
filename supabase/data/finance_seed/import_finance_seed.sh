#!/bin/bash
# =============================================================================
# Finance Seed Data Import Script
# Imports Month-End Close and BIR Tax Filing projects with tasks
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuration - override with environment variables
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo-core}"
DB_NAME="${DB_NAME:-odoo_core}"
ODOO_URL="${ODOO_URL:-http://localhost:8069}"

echo "=============================================="
echo "Finance Seed Data Import"
echo "=============================================="
echo "Container: $ODOO_CONTAINER"
echo "Database:  $DB_NAME"
echo "Directory: $SCRIPT_DIR"
echo ""

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${ODOO_CONTAINER}$"; then
    echo "ERROR: Container '$ODOO_CONTAINER' is not running."
    echo "Start the stack with: docker compose up -d"
    exit 1
fi

# Function to import a CSV file
import_csv() {
    local step=$1
    local model=$2
    local csv_file=$3

    echo ""
    echo "[$step] Importing $model from $csv_file..."

    if [[ ! -f "$SCRIPT_DIR/$csv_file" ]]; then
        echo "  SKIP: File not found: $csv_file"
        return 0
    fi

    # Copy file to container
    docker cp "$SCRIPT_DIR/$csv_file" "${ODOO_CONTAINER}:/tmp/${csv_file}"

    # Run import via Odoo shell
    docker exec -i "$ODOO_CONTAINER" odoo shell -d "$DB_NAME" --no-http <<PYTHON
import csv

csv_path = "/tmp/${csv_file}"
model_name = "${model}"

print(f"Importing {model_name} from {csv_path}")

Model = env[model_name].sudo()

with open(csv_path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Found {len(rows)} rows")

# Use load() for proper import with external IDs
fields = list(rows[0].keys()) if rows else []
data = [[row.get(f, '') for f in fields] for row in rows]

result = Model.load(fields, data)

if result.get('messages'):
    for msg in result['messages']:
        print(f"  {msg.get('type', 'info')}: {msg.get('message', '')}")

ids = result.get('ids', [])
print(f"Imported {len(ids)} records")

env.cr.commit()
PYTHON

    echo "  Done."
}

# =============================================================================
# IMPORT SEQUENCE
# =============================================================================

echo ""
echo "=============================================="
echo "STEP 1: Import Tags"
echo "=============================================="
import_csv "1.1" "project.tags" "01_project.tags.csv"

echo ""
echo "=============================================="
echo "STEP 2: Import Projects"
echo "=============================================="
import_csv "2.1" "project.project" "02_project.project.csv"

echo ""
echo "=============================================="
echo "STEP 3: Import Month-End Close Tasks"
echo "=============================================="
import_csv "3.1" "project.task" "03_project.task.month_end.csv"

echo ""
echo "=============================================="
echo "STEP 4: Import BIR Tax Filing Tasks"
echo "=============================================="
import_csv "4.1" "project.task" "04_project.task.bir_tax.csv"

echo ""
echo "=============================================="
echo "IMPORT COMPLETE"
echo "=============================================="
echo ""
echo "Summary:"
echo "  - Tags: 36 (4 phase + 26 category + 6 BIR form)"
echo "  - Projects: 2 (Month-End Close, BIR Tax Filing)"
echo "  - Month-End Close Tasks: 36"
echo "  - BIR Tax Filing Tasks: 33"
echo ""
echo "Next steps (optional):"
echo "  1. Run update script to assign users:"
echo "     python3 $SCRIPT_DIR/update_tasks_after_import.py \\"
echo "       --url $ODOO_URL --db $DB_NAME --user admin --password YOUR_PASSWORD"
echo ""
echo "  2. Or manually assign users via Odoo UI:"
echo "     Project -> Tasks -> List View -> Select All -> Action -> Edit"
echo ""
