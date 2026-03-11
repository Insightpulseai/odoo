#!/usr/bin/env bash
# Expense OCR Ingestion Script
#
# Processes a receipt text file through OCR extraction and creates
# an ipai.expense.ocr.run record in Odoo.
#
# Usage:
#   scripts/expense_ocr_ingest.sh <expense_id> <attachment_id> <text_path>
#
# Environment:
#   ODOO_BIN  - Path to odoo binary (default: odoo)
#   ODOO_DB   - Database name (required)
#   ODOO_CONF - Path to odoo.conf (required)
#
# Example:
#   ODOO_DB=odoo_core ODOO_CONF=/etc/odoo/odoo.conf \
#     scripts/expense_ocr_ingest.sh 42 123 /tmp/receipt.txt

set -euo pipefail

# Defaults
: "${ODOO_BIN:=odoo}"

# Required env vars
: "${ODOO_DB:?Set ODOO_DB environment variable}"
: "${ODOO_CONF:?Set ODOO_CONF environment variable}"

# Arguments
EXPENSE_ID="${1:?Usage: scripts/expense_ocr_ingest.sh <expense_id> <attachment_id> <text_path>}"
ATTACHMENT_ID="${2:?Usage: scripts/expense_ocr_ingest.sh <expense_id> <attachment_id> <text_path>}"
TEXT_PATH="${3:?Usage: scripts/expense_ocr_ingest.sh <expense_id> <attachment_id> <text_path>}"

# Validate input file
if [[ ! -f "$TEXT_PATH" ]]; then
    echo "ERROR: Text file not found: $TEXT_PATH" >&2
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Run OCR extraction
TMP_JSON="$(mktemp)"
trap 'rm -f "$TMP_JSON"' EXIT

echo "Running OCR extraction..."
python3 "$REPO_ROOT/addons/ipai/ipai_expense_ocr/scripts/ocr_extract.py" \
    --in "$TEXT_PATH" \
    --out "$TMP_JSON"

echo "OCR output: $TMP_JSON"
cat "$TMP_JSON"

# Create OCR run in Odoo
echo ""
echo "Creating OCR run record in Odoo..."

$ODOO_BIN shell -d "$ODOO_DB" -c "$ODOO_CONF" --no-http <<PYTHON
import json

# Load OCR result
data = json.load(open("$TMP_JSON", "r", encoding="utf-8"))

# Validate references
expense = env["hr.expense"].browse(int("$EXPENSE_ID"))
att = env["ir.attachment"].browse(int("$ATTACHMENT_ID"))

if not expense.exists():
    print("ERROR: Expense not found:", "$EXPENSE_ID")
    exit(1)
if not att.exists():
    print("ERROR: Attachment not found:", "$ATTACHMENT_ID")
    exit(1)

# Create OCR run record
run = env["ipai.expense.ocr.run"].create({
    "expense_id": expense.id,
    "attachment_id": att.id,
    "status": "ok",
    "confidence": float(data.get("confidence") or 0.0),
    "merchant": data.get("merchant"),
    "receipt_date": data.get("receipt_date"),
    "total": float(data.get("total") or 0.0),
    "raw_json": data,
})

# Optionally update expense with extracted data
if data.get("merchant") and not expense.name:
    expense.name = data["merchant"]
if data.get("total") and not expense.unit_amount:
    expense.unit_amount = data["total"]

env.cr.commit()

print("SUCCESS: OCR run created with ID:", run.id)
print("  Merchant:", run.merchant)
print("  Total:", run.total)
print("  Date:", run.receipt_date)
print("  Confidence:", f"{run.confidence:.0%}")
PYTHON

echo ""
echo "Done."
