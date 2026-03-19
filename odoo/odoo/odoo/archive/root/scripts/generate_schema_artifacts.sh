#!/bin/bash
# =============================================================================
# Generate Schema Artifacts
# Runs all schema generation tools and outputs to docs/data_model/
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Generate Schema Artifacts ==="
echo "Output directory: docs/data_model/"

# Default env vars if not set
export OUT_DIR="${OUT_DIR:-docs/data_model}"
export SCHEMA_JSON="${SCHEMA_JSON:-docs/data_model/schema.json}"
export OUT_DRAWIO="${OUT_DRAWIO:-docs/data_model/erd.drawio}"
export OUT_PY="${OUT_PY:-docs/data_model/orm_models.py}"

# Default anchors for ERD (key business models + analytic spine)
export ANCHORS="${ANCHORS:-res.partner,res.users,res.company,crm.lead,sale.order,purchase.order,stock.picking,account.move,project.task,account.analytic.account,account.analytic.line,hr.expense,hr.expense.sheet}"

cd "$ROOT_DIR"

# Step 1: Export schema from Odoo database
echo ""
echo "Step 1: Exporting schema from database..."
if python3 tools/odoo_schema/export_schema.py; then
    echo "  ✓ schema.json"
    echo "  ✓ schema.yaml"
    echo "  ✓ erd.mmd"
    echo "  ✓ EXTENSION_POINTS.md"
else
    echo "  ✗ Failed to export schema (check DB connection)"
    exit 1
fi

# Step 2: Generate Draw.io ERD
echo ""
echo "Step 2: Generating Draw.io ERD..."
if python3 tools/odoo_schema/schema_to_drawio.py; then
    echo "  ✓ erd.drawio"
else
    echo "  ✗ Failed to generate Draw.io ERD"
    exit 1
fi

# Step 3: Generate Pydantic stubs
echo ""
echo "Step 3: Generating Pydantic ORM stubs..."
if python3 tools/odoo_schema/schema_to_pydantic.py; then
    echo "  ✓ orm_models.py"
else
    echo "  ✗ Failed to generate Pydantic stubs"
    exit 1
fi

echo ""
echo "=== Schema Artifacts Generated ==="
echo ""
echo "Files created:"
ls -lh docs/data_model/
echo ""
echo "To view ERD:"
echo "  - Open docs/data_model/erd.drawio in diagrams.net"
echo "  - Or render erd.mmd in any Mermaid viewer"
