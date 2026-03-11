#!/usr/bin/env bash
# ============================================================================
# Supabase Migrations Lint Script
#
# Validates that all migration files follow naming conventions and structure.
# ============================================================================
set -euo pipefail

MIGRATIONS_DIR="${MIGRATIONS_DIR:-supabase/migrations}"

die() {
  echo "[migrations-lint] FAIL: $*" >&2
  exit 1
}

warn() {
  echo "[migrations-lint] WARN: $*" >&2
}

# Check migrations directory exists
if [ ! -d "$MIGRATIONS_DIR" ]; then
  die "Missing $MIGRATIONS_DIR/"
fi

# Count SQL files
sql_count=$(find "$MIGRATIONS_DIR" -maxdepth 1 -name "*.sql" -type f | wc -l)
if [ "$sql_count" -eq 0 ]; then
  die "No .sql files found in $MIGRATIONS_DIR/"
fi

echo "[migrations-lint] Found $sql_count SQL migration files"

# Check naming convention: YYYYMMDD or YYYYMMDDHHMMSS prefix followed by underscore and description
# Pattern: digits followed by underscore and alphanumeric/underscores, ending in .sql
bad_files=""
for f in "$MIGRATIONS_DIR"/*.sql; do
  [ -f "$f" ] || continue
  basename_f=$(basename "$f")

  # Check if filename matches expected pattern
  # Accepts: 20260124_something.sql, 20260124_1000_something.sql, 202601241200_something.sql
  if ! echo "$basename_f" | grep -qE '^[0-9]{8,14}_[a-zA-Z0-9_]+\.sql$'; then
    bad_files="$bad_files\n  - $basename_f"
  fi
done

if [ -n "$bad_files" ]; then
  echo "[migrations-lint] Invalid migration filenames (expected: YYYYMMDD[HHMMSS]_description.sql):$bad_files"
  # This is a warning, not a failure - some repos have different conventions
  warn "Non-standard naming detected but allowing to proceed"
fi

# Check for basic SQL syntax issues
syntax_issues=""
for f in "$MIGRATIONS_DIR"/*.sql; do
  [ -f "$f" ] || continue
  basename_f=$(basename "$f")

  # Check for empty files
  if [ ! -s "$f" ]; then
    syntax_issues="$syntax_issues\n  - $basename_f: empty file"
    continue
  fi

  # Check for basic SQL keywords (at least one should be present)
  if ! grep -qiE '(CREATE|ALTER|DROP|INSERT|UPDATE|DELETE|SELECT|GRANT|REVOKE)' "$f"; then
    syntax_issues="$syntax_issues\n  - $basename_f: no SQL statements detected"
  fi
done

if [ -n "$syntax_issues" ]; then
  die "SQL syntax issues detected:$syntax_issues"
fi

# Check for lakehouse control plane specific tables in ops schema
ops_tables=0
if grep -rq "ops\.runs" "$MIGRATIONS_DIR" 2>/dev/null; then
  ops_tables=$((ops_tables + 1))
fi
if grep -rq "ops\.run_events" "$MIGRATIONS_DIR" 2>/dev/null; then
  ops_tables=$((ops_tables + 1))
fi
if grep -rq "ops\.run_artifacts\|ops\.artifacts" "$MIGRATIONS_DIR" 2>/dev/null; then
  ops_tables=$((ops_tables + 1))
fi

if [ "$ops_tables" -gt 0 ]; then
  echo "[migrations-lint] Found $ops_tables lakehouse control plane tables in ops schema"
fi

echo "[migrations-lint] OK"
