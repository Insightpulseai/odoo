#!/usr/bin/env bash
# ============================================================================
# Odoo Environment Neutralization — Odoo.sh Parity
# ============================================================================
# Disables dangerous side effects in non-prod Odoo environments.
# Supports staging clone and post-import workflows.
#
# Usage:
#   ./neutralize_environment.sh --mode=staging  --database=odoo_staging
#   ./neutralize_environment.sh --mode=post-import --database=imported_db
#   ./neutralize_environment.sh --mode=staging --dry-run
#
# Env vars: DB_HOST, DB_USER, DB_PASSWORD, DB_PORT (default 5432)
# ============================================================================
set -euo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
MODE=""
DATABASE=""
DRY_RUN=false
DB_HOST="${DB_HOST:-localhost}"
DB_USER="${DB_USER:-odoo}"
DB_PORT="${DB_PORT:-5432}"
PGPASSWORD="${DB_PASSWORD:-}"
export PGPASSWORD
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
for arg in "$@"; do
  case "$arg" in
    --mode=*)      MODE="${arg#*=}" ;;
    --database=*)  DATABASE="${arg#*=}" ;;
    --host=*)      DB_HOST="${arg#*=}" ;;
    --port=*)      DB_PORT="${arg#*=}" ;;
    --config=*)    ;; # reserved for future odoo.conf path
    --dry-run)     DRY_RUN=true ;;
    *)             echo "ERROR: Unknown argument: $arg"; exit 1 ;;
  esac
done

# ---------------------------------------------------------------------------
# Validate inputs
# ---------------------------------------------------------------------------
if [[ -z "$MODE" ]]; then
  echo "ERROR: --mode required (staging or post-import)"
  exit 1
fi

if [[ "$MODE" != "staging" && "$MODE" != "post-import" ]]; then
  echo "ERROR: --mode must be 'staging' or 'post-import', got: $MODE"
  exit 1
fi

if [[ -z "$DATABASE" ]]; then
  if [[ "$MODE" == "staging" ]]; then
    DATABASE="odoo_staging"
  else
    echo "ERROR: --database required for post-import mode"
    exit 1
  fi
fi

# Production guard
if [[ "$DATABASE" == "odoo" ]]; then
  echo "ERROR: Refusing to neutralize production database 'odoo'"
  exit 1
fi

if [[ -z "$PGPASSWORD" ]]; then
  echo "ERROR: DB_PASSWORD env var required"
  exit 1
fi

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }
log_json() {
  local step="$1" status="$2" detail="$3"
  echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"mode\":\"$MODE\",\"database\":\"$DATABASE\",\"step\":\"$step\",\"status\":\"$status\",\"detail\":\"$detail\"}"
}

log "============================================"
log " Environment Neutralization"
log " Mode:     $MODE"
log " Database: $DATABASE"
log " Host:     $DB_HOST:$DB_PORT"
log " Dry-run:  $DRY_RUN"
log " Time:     $TIMESTAMP"
log "============================================"

# ---------------------------------------------------------------------------
# Psql helper
# ---------------------------------------------------------------------------
run_sql() {
  local sql="$1"
  local desc="${2:-}"

  if [[ "$DRY_RUN" == "true" ]]; then
    log "[DRY-RUN] Would execute: $desc"
    log "[DRY-RUN] SQL: $sql"
    return 0
  fi

  log "Executing: $desc"
  psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DATABASE" \
    -c "$sql" --quiet 2>&1
}

run_sql_file() {
  local file="$1"
  local desc="${2:-}"

  if [[ "$DRY_RUN" == "true" ]]; then
    log "[DRY-RUN] Would execute SQL file: $file ($desc)"
    return 0
  fi

  log "Executing SQL file: $file ($desc)"
  psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DATABASE" \
    -f "$file" 2>&1 | grep -E 'UPDATE|DELETE|INSERT|NOTICE|ERROR' || true
}

# ---------------------------------------------------------------------------
# Pre-flight: verify DB exists and is accessible
# ---------------------------------------------------------------------------
log ""
log ">>> Pre-flight: verifying database access..."
if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DATABASE" -c "SELECT 1;" --quiet 2>/dev/null; then
  log "ERROR: Cannot connect to database $DATABASE"
  log_json "preflight" "FAIL" "database_unreachable"
  exit 1
fi
log_json "preflight" "PASS" "database_accessible"

# ---------------------------------------------------------------------------
# Pre-flight: verify Odoo schema exists
# ---------------------------------------------------------------------------
HAS_ODOO_TABLES=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DATABASE" \
  -t -c "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'ir_cron');" 2>/dev/null | tr -d ' ')

if [[ "$HAS_ODOO_TABLES" != "t" ]]; then
  log "ERROR: Database $DATABASE does not contain Odoo tables (ir_cron missing)"
  log "This database may not be initialized. Neutralization requires a populated Odoo database."
  log_json "preflight_schema" "FAIL" "no_odoo_tables"
  exit 1
fi
log_json "preflight_schema" "PASS" "odoo_tables_present"

# ---------------------------------------------------------------------------
# Capture before-state
# ---------------------------------------------------------------------------
log ""
log ">>> Capturing before-state..."

safe_count() {
  psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DATABASE" \
    -t -c "$1" 2>/dev/null | tr -d ' ' || echo "0"
}

BEFORE_CRON_ACTIVE=$(safe_count "SELECT count(*) FROM ir_cron WHERE active = true;")
BEFORE_MAIL_ACTIVE=$(safe_count "SELECT count(*) FROM ir_mail_server WHERE active = true;")
BEFORE_PAYMENT_ENABLED=$(safe_count "SELECT count(*) FROM payment_provider WHERE state != 'disabled';")
BEFORE_MAIL_QUEUE=$(safe_count "SELECT count(*) FROM mail_mail WHERE state IN ('outgoing', 'exception');")

log "  Active crons:      $BEFORE_CRON_ACTIVE"
log "  Active mail svrs:  $BEFORE_MAIL_ACTIVE"
log "  Enabled payments:  $BEFORE_PAYMENT_ENABLED"
log "  Outgoing mail:     $BEFORE_MAIL_QUEUE"

# ---------------------------------------------------------------------------
# Step 1: Disable scheduled actions (ir.cron)
# ---------------------------------------------------------------------------
log ""
log ">>> Step 1: Disabling scheduled actions..."
run_sql "
UPDATE ir_cron SET active = false
WHERE id NOT IN (
    SELECT id FROM ir_cron
    WHERE cron_name IN (
        'base: GC unlinked attachments',
        'base: Auto-vacuum internal data',
        'base: Run autovacuum on registry',
        'mail: garbage collect notifications'
    )
);" "Disable non-essential crons (whitelist: GC, autovacuum, mail GC)"

# ---------------------------------------------------------------------------
# Step 2: Disable outbound mail servers
# ---------------------------------------------------------------------------
log ""
log ">>> Step 2: Disabling outbound mail servers..."
run_sql "UPDATE ir_mail_server SET active = false;" "Disable all ir_mail_server records"

# ---------------------------------------------------------------------------
# Step 3: Clear outgoing mail queue
# ---------------------------------------------------------------------------
log ""
log ">>> Step 3: Clearing outgoing mail queue..."
run_sql "DELETE FROM mail_mail WHERE state IN ('outgoing', 'exception');" "Purge queued outgoing mail"

# ---------------------------------------------------------------------------
# Step 4: Disable payment providers
# ---------------------------------------------------------------------------
log ""
log ">>> Step 4: Disabling payment providers..."
run_sql "UPDATE payment_provider SET state = 'disabled' WHERE state != 'disabled';" "Disable all payment providers"

# ---------------------------------------------------------------------------
# Step 5: Clear integration tokens
# ---------------------------------------------------------------------------
log ""
log ">>> Step 5: Clearing integration tokens..."
run_sql "DELETE FROM ir_config_parameter WHERE key LIKE '%google%token%';" "Clear Google tokens"
run_sql "DELETE FROM ir_config_parameter WHERE key LIKE '%microsoft%token%';" "Clear Microsoft tokens"
run_sql "DELETE FROM ir_config_parameter WHERE key LIKE '%calendar%token%';" "Clear calendar tokens"
run_sql "UPDATE ir_config_parameter SET value = '' WHERE key LIKE 'iap.%token%' OR key LIKE 'iap.%key%';" "Clear IAP tokens"

# ---------------------------------------------------------------------------
# Step 6: Disable social integrations
# ---------------------------------------------------------------------------
log ""
log ">>> Step 6: Disabling social integrations..."
run_sql "
UPDATE ir_config_parameter SET value = ''
WHERE key IN (
    'social.facebook_app_id',
    'social.linkedin_app_id',
    'social.twitter_api_key',
    'social.instagram_app_id',
    'push_notification.firebase_api_key'
);" "Blank social integration keys"

# ---------------------------------------------------------------------------
# Step 7: Set environment marker
# ---------------------------------------------------------------------------
log ""
log ">>> Step 7: Setting environment marker..."

ENV_LABEL="$MODE"
if [[ "$MODE" == "post-import" ]]; then
  ENV_LABEL="imported"
fi

run_sql "
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES ('ipai.environment', '$ENV_LABEL', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET value = '$ENV_LABEL', write_date = NOW();" "Set ipai.environment=$ENV_LABEL"

run_sql "
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES ('ribbon.name', '${ENV_LABEL^^}', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET value = '${ENV_LABEL^^}', write_date = NOW();" "Set ribbon.name=${ENV_LABEL^^}"

# ---------------------------------------------------------------------------
# Step 8: Disable robots.txt
# ---------------------------------------------------------------------------
log ""
log ">>> Step 8: Disabling robots.txt..."
run_sql "
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES ('website.robots_txt_disabled', 'true', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET value = 'true', write_date = NOW();" "Disable robots.txt"

# ---------------------------------------------------------------------------
# Step 9 (staging only): Mask PII
# ---------------------------------------------------------------------------
if [[ "$MODE" == "staging" ]]; then
  log ""
  log ">>> Step 9: Masking PII (staging mode)..."
  run_sql "UPDATE res_partner SET email = 'staging+' || id || '@insightpulseai.com' WHERE email IS NOT NULL AND email != '';" "Mask partner emails"
  run_sql "UPDATE res_partner SET phone = '+63900' || LPAD(id::text, 7, '0') WHERE phone IS NOT NULL AND phone != '';" "Mask partner phones"
  run_sql "UPDATE res_partner SET mobile = NULL WHERE mobile IS NOT NULL;" "Clear partner mobiles"
  run_sql "UPDATE res_partner SET street = 'Staging Address ' || id, street2 = NULL WHERE street IS NOT NULL;" "Mask partner addresses"
  run_sql "UPDATE res_users SET password = 'staging_changeme' WHERE id > 2;" "Reset non-admin passwords"
fi

if [[ "$MODE" == "post-import" ]]; then
  log ""
  log ">>> Step 9: Resetting passwords (post-import mode)..."
  run_sql "UPDATE res_users SET password = 'import_changeme' WHERE id > 2;" "Reset non-admin passwords for imported DB"
fi

# ---------------------------------------------------------------------------
# Capture after-state
# ---------------------------------------------------------------------------
log ""
log ">>> Capturing after-state..."

AFTER_CRON_ACTIVE=$(safe_count "SELECT count(*) FROM ir_cron WHERE active = true;")
AFTER_MAIL_ACTIVE=$(safe_count "SELECT count(*) FROM ir_mail_server WHERE active = true;")
AFTER_PAYMENT_ENABLED=$(safe_count "SELECT count(*) FROM payment_provider WHERE state != 'disabled';")
AFTER_MAIL_QUEUE=$(safe_count "SELECT count(*) FROM mail_mail WHERE state IN ('outgoing', 'exception');")

log "  Active crons:      $BEFORE_CRON_ACTIVE → $AFTER_CRON_ACTIVE"
log "  Active mail svrs:  $BEFORE_MAIL_ACTIVE → $AFTER_MAIL_ACTIVE"
log "  Enabled payments:  $BEFORE_PAYMENT_ENABLED → $AFTER_PAYMENT_ENABLED"
log "  Outgoing mail:     $BEFORE_MAIL_QUEUE → $AFTER_MAIL_QUEUE"

# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------
log ""
log ">>> Verification..."
FAILURES=0

if [[ "$AFTER_MAIL_ACTIVE" != "0" ]]; then
  log "FAIL: Mail servers still active ($AFTER_MAIL_ACTIVE)"
  log_json "verify_mail" "FAIL" "active_count=$AFTER_MAIL_ACTIVE"
  FAILURES=$((FAILURES + 1))
else
  log "PASS: All mail servers disabled"
  log_json "verify_mail" "PASS" "all_disabled"
fi

if [[ "$AFTER_PAYMENT_ENABLED" != "0" ]]; then
  log "FAIL: Payment providers still enabled ($AFTER_PAYMENT_ENABLED)"
  log_json "verify_payment" "FAIL" "enabled_count=$AFTER_PAYMENT_ENABLED"
  FAILURES=$((FAILURES + 1))
else
  log "PASS: All payment providers disabled"
  log_json "verify_payment" "PASS" "all_disabled"
fi

if [[ "$AFTER_MAIL_QUEUE" != "0" ]]; then
  log "FAIL: Outgoing mail still queued ($AFTER_MAIL_QUEUE)"
  log_json "verify_queue" "FAIL" "queued=$AFTER_MAIL_QUEUE"
  FAILURES=$((FAILURES + 1))
else
  log "PASS: Mail queue cleared"
  log_json "verify_queue" "PASS" "queue_empty"
fi

# Verify environment marker
ENV_VALUE=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DATABASE" \
  -t -c "SELECT value FROM ir_config_parameter WHERE key = 'ipai.environment';" 2>/dev/null | tr -d ' ')
if [[ "$ENV_VALUE" == "$ENV_LABEL" ]]; then
  log "PASS: Environment marker set to '$ENV_LABEL'"
  log_json "verify_env" "PASS" "marker=$ENV_LABEL"
else
  log "FAIL: Environment marker is '$ENV_VALUE', expected '$ENV_LABEL'"
  log_json "verify_env" "FAIL" "marker=$ENV_VALUE"
  FAILURES=$((FAILURES + 1))
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
log ""
log "============================================"
log " NEUTRALIZATION COMPLETE"
log " Mode:     $MODE"
log " Database: $DATABASE"
log " Crons:    $BEFORE_CRON_ACTIVE → $AFTER_CRON_ACTIVE active"
log " Mail:     All servers disabled, queue cleared"
log " Payments: All providers disabled"
log " Tokens:   Google/Microsoft/IAP/social cleared"
log " Marker:   ipai.environment=$ENV_LABEL"
log " Failures: $FAILURES"
log "============================================"

if [[ "$FAILURES" -gt 0 ]]; then
  log "ERROR: $FAILURES verification failures — neutralization incomplete"
  exit 1
fi

exit 0
