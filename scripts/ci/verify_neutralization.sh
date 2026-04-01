#!/usr/bin/env bash
# ============================================================================
# Verify Neutralization — CI Check
# ============================================================================
# Validates that a database has been properly neutralized.
# Returns exit code 0 if all checks pass, 1 if any fail.
#
# Usage: DB_HOST=... DB_USER=... DB_PASSWORD=... ./verify_neutralization.sh <database>
# ============================================================================
set -euo pipefail

DATABASE="${1:?ERROR: Database name required as first argument}"
DB_HOST="${DB_HOST:?ERROR: DB_HOST required}"
DB_USER="${DB_USER:?ERROR: DB_USER required}"
DB_PORT="${DB_PORT:-5432}"
PGPASSWORD="${DB_PASSWORD:?ERROR: DB_PASSWORD required}"
export PGPASSWORD

FAILURES=0

check() {
  local name="$1" sql="$2" expected="$3"
  local actual
  actual=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DATABASE" \
    -t -c "$sql" 2>/dev/null | tr -d ' ')

  if [[ "$actual" == "$expected" ]]; then
    echo "PASS: $name (got: $actual)"
  else
    echo "FAIL: $name (expected: $expected, got: $actual)"
    FAILURES=$((FAILURES + 1))
  fi
}

echo "Verifying neutralization of database: $DATABASE"
echo "---"

# 1. No active mail servers
check "No active mail servers" \
  "SELECT count(*) FROM ir_mail_server WHERE active = true;" \
  "0"

# 2. No enabled payment providers
check "No enabled payment providers" \
  "SELECT count(*) FROM payment_provider WHERE state != 'disabled';" \
  "0"

# 3. No outgoing mail in queue
check "No outgoing mail queued" \
  "SELECT count(*) FROM mail_mail WHERE state IN ('outgoing', 'exception');" \
  "0"

# 4. Environment marker set
check "Environment marker is not 'production'" \
  "SELECT CASE WHEN value IN ('staging', 'imported') THEN 'safe' ELSE 'unsafe' END FROM ir_config_parameter WHERE key = 'ipai.environment';" \
  "safe"

# 5. Most crons disabled (allow up to 4 whitelisted)
ACTIVE_CRONS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DATABASE" \
  -t -c "SELECT count(*) FROM ir_cron WHERE active = true;" 2>/dev/null | tr -d ' ')
if [[ "$ACTIVE_CRONS" -le 4 ]]; then
  echo "PASS: Cron jobs controlled ($ACTIVE_CRONS active, max 4 whitelisted)"
else
  echo "FAIL: Too many active crons ($ACTIVE_CRONS, max 4)"
  FAILURES=$((FAILURES + 1))
fi

echo "---"
if [[ "$FAILURES" -gt 0 ]]; then
  echo "RESULT: FAIL ($FAILURES checks failed)"
  exit 1
else
  echo "RESULT: PASS (all neutralization checks passed)"
  exit 0
fi
