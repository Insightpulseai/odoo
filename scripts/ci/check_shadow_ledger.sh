#!/usr/bin/env bash
set -euo pipefail

# Shadow-ledger detector:
# blocks introducing authoritative accounting/ERP "ledger primitives" under Supabase schemas/migrations/functions.
# Default mode: fail only on NEW findings compared to baseline file.

BASELINE="config/ci/shadow_ledger_baseline.txt"

TARGETS=(
  "supabase/migrations"
  "supabase/functions"
  "supabase/sql"
)

# Heuristic keywords – intentionally conservative
PATTERN='(create table|alter table|create view|create materialized view|create function).*(invoice|account_move|journal|payment|reconciliation|tax|vat|withholding|general_ledger|trial_balance|coa|chart_of_accounts|stock_move|picking|purchase_order|sale_order)'

tmp="$(mktemp)"
touch "$tmp"

for t in "${TARGETS[@]}"; do
  [ -d "$t" ] || continue
  # grep only tracked files
  git ls-files "$t" 2>/dev/null | while IFS= read -r f; do
    # skip empty or non-text
    [ -f "$f" ] || continue
    if grep -Ein "$PATTERN" "$f" >/dev/null 2>&1; then
      echo "$f" >> "$tmp"
    fi
  done
done

sort -u "$tmp" -o "$tmp"

if [ ! -f "$BASELINE" ]; then
  echo "INFO: baseline missing ($BASELINE). Creating baseline from current findings."
  mkdir -p "$(dirname "$BASELINE")"
  cp "$tmp" "$BASELINE"
  echo "OK: baseline created. Re-run CI; new violations will fail."
  exit 0
fi

new="$(comm -13 <(sort -u "$BASELINE") <(cat "$tmp") || true)"

if [ -n "$new" ]; then
  echo "FAIL: NEW potential shadow-ledger files detected (Supabase side):"
  echo "$new"
  echo
  echo "Policy: Odoo is SOR for ledger/postings; Supabase SSOT must not introduce authoritative ledger primitives."
  echo "If this is a false positive, add justification + baseline update in $BASELINE."
  exit 1
fi

echo "✅ OK: no new shadow-ledger risks introduced"
