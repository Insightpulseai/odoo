#!/bin/bash
# =============================================================================
# Odoo 18 CE Project Import Sequence
# Imports data in correct dependency order
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
TEMPLATES_DIR="${PROJECT_ROOT}/data/import_templates"

# Configuration
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo-core}"
DB_NAME="${DB_NAME:-odoo_core}"

echo "=============================================="
echo "Odoo 18 CE Project Import Sequence"
echo "=============================================="
echo "Container: $ODOO_CONTAINER"
echo "Database:  $DB_NAME"
echo "Templates: $TEMPLATES_DIR"
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
    local mode=${4:-create}  # create or update

    echo ""
    echo "[$step] Importing $model from $csv_file (mode: $mode)..."

    if [[ ! -f "$TEMPLATES_DIR/$csv_file" ]]; then
        echo "  SKIP: File not found: $csv_file"
        return 0
    fi

    # Copy file to container
    docker cp "$TEMPLATES_DIR/$csv_file" "${ODOO_CONTAINER}:/tmp/${csv_file}"

    # Run import via Odoo shell
    docker exec -i "$ODOO_CONTAINER" odoo shell -d "$DB_NAME" --no-http <<PYTHON
import csv

csv_path = "/tmp/${csv_file}"
model_name = "${model}"
mode = "${mode}"

print(f"Importing {model_name} from {csv_path} (mode: {mode})")

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
PYTHON

    echo "  Done."
}

# =============================================================================
# IMPORT SEQUENCE (ordered by dependencies)
# =============================================================================

echo ""
echo "=============================================="
echo "STEP 1: CREATE PASSES (new records)"
echo "=============================================="

import_csv "1.1" "project.task.type" "01_project.task.type.csv" "create"
import_csv "1.2" "project.project" "02_project.project.csv" "create"
import_csv "1.3" "project.milestone" "03_project.milestone.csv" "create"
import_csv "1.4" "project.task" "04_project.task.csv" "create"

echo ""
echo "=============================================="
echo "STEP 2: UPDATE PASSES (dependencies/recurrence)"
echo "=============================================="

import_csv "2.1" "project.task" "05_project.task.dependencies.csv" "update"
import_csv "2.2" "project.task" "06_project.task.recurrence.csv" "update"

echo ""
echo "=============================================="
echo "STEP 3: ACTIVITIES (via script)"
echo "=============================================="

# Copy activity CSV and import script
docker cp "$TEMPLATES_DIR/07_mail.activity.csv" "${ODOO_CONTAINER}:/tmp/"
docker cp "$SCRIPT_DIR/import_activities.py" "${ODOO_CONTAINER}:/tmp/"

docker exec -i "$ODOO_CONTAINER" bash -c "
export ACTIVITY_CSV='/tmp/07_mail.activity.csv'
cd /tmp && odoo shell -d $DB_NAME --no-http < /tmp/import_activities.py
"

echo ""
echo "=============================================="
echo "IMPORT SEQUENCE COMPLETE"
echo "=============================================="
echo ""
echo "Next: Run verification script to confirm import"
echo "  ./scripts/import/verify_import.sh"
