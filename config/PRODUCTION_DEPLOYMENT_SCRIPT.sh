#!/bin/bash
#
# Mailgun Mailgate Production Deployment Script
# Purpose: Deploy ipai_enterprise_bridge mailgate controller to production
# Date: 2026-01-19
# Status: Ready for execution on production server
#

set -e  # Exit on error
set -u  # Exit on undefined variable

# ============================================================================
# CONFIGURATION
# ============================================================================

ODOO_DATABASE="${ODOO_DATABASE:-production}"
ODOO_USER="${ODOO_USER:-odoo}"
ODOO_SERVICE="${ODOO_SERVICE:-odoo}"
REPO_PATH="${REPO_PATH:-/opt/odoo-ce}"
LOG_DIR="${LOG_DIR:-/var/log/odoo}"
VALIDATION_LOG="${LOG_DIR}/mailgun_mailgate_validation_$(date +%Y%m%d_%H%M%S).txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    exit 1
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        error "Required command '$1' not found"
    fi
}

# ============================================================================
# PRE-DEPLOYMENT CHECKS
# ============================================================================

log "Starting Mailgun mailgate deployment..."

# Check required commands
check_command git
check_command docker
check_command psql
check_command curl

# Check if we're in the correct directory
if [ ! -d "$REPO_PATH/addons/ipai/ipai_enterprise_bridge" ]; then
    error "ipai_enterprise_bridge module not found at $REPO_PATH/addons/ipai/ipai_enterprise_bridge"
fi

log "Pre-deployment checks passed"

# ============================================================================
# STEP 1: UPDATE CODE FROM REPOSITORY
# ============================================================================

log "Step 1: Updating code from repository..."

cd "$REPO_PATH"

# Store current commit for rollback
CURRENT_COMMIT=$(git rev-parse HEAD)
log "Current commit: $CURRENT_COMMIT"

# Pull latest changes
if git pull origin main; then
    log "Code updated successfully"
    NEW_COMMIT=$(git rev-parse HEAD)
    log "New commit: $NEW_COMMIT"
else
    error "Failed to pull latest code"
fi

# ============================================================================
# STEP 2: VERIFY CONTROLLER FILES EXIST
# ============================================================================

log "Step 2: Verifying controller files..."

REQUIRED_FILES=(
    "addons/ipai/ipai_enterprise_bridge/controllers/__init__.py"
    "addons/ipai/ipai_enterprise_bridge/controllers/mailgun_mailgate.py"
    "addons/ipai/ipai_enterprise_bridge/__init__.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$REPO_PATH/$file" ]; then
        log "✓ Found: $file"
    else
        error "Missing required file: $file"
    fi
done

# Check that mailgun_mailgate.py contains the HTTP route
if grep -q "@http.route('/mailgate/mailgun'" "$REPO_PATH/addons/ipai/ipai_enterprise_bridge/controllers/mailgun_mailgate.py"; then
    log "✓ Mailgate HTTP route found in controller"
else
    error "Mailgate HTTP route not found in controller"
fi

log "Controller files verified"

# ============================================================================
# STEP 3: UPGRADE ODOO MODULE
# ============================================================================

log "Step 3: Upgrading ipai_enterprise_bridge module..."

# Determine if using Docker or direct install
if docker ps | grep -q odoo; then
    log "Detected Docker deployment"
    ODOO_CONTAINER=$(docker ps --filter "name=odoo" --format "{{.Names}}" | head -1)
    log "Using container: $ODOO_CONTAINER"

    docker exec "$ODOO_CONTAINER" odoo \
        -d "$ODOO_DATABASE" \
        -u ipai_enterprise_bridge \
        --stop-after-init \
        --log-level=info
else
    log "Detected direct Odoo installation"

    sudo -u "$ODOO_USER" odoo \
        -c /etc/odoo/odoo.conf \
        -d "$ODOO_DATABASE" \
        -u ipai_enterprise_bridge \
        --stop-after-init \
        --log-level=info
fi

if [ $? -eq 0 ]; then
    log "Module upgraded successfully"
else
    error "Module upgrade failed"
fi

# ============================================================================
# STEP 4: RESTART ODOO SERVICE
# ============================================================================

log "Step 4: Restarting Odoo service..."

if docker ps | grep -q odoo; then
    docker restart "$ODOO_CONTAINER"
    log "Odoo container restarted"

    # Wait for service to be ready
    sleep 10

    if docker ps | grep -q "$ODOO_CONTAINER"; then
        log "Odoo container is running"
    else
        error "Odoo container failed to start"
    fi
else
    sudo systemctl restart "$ODOO_SERVICE"
    log "Odoo service restarted"

    # Wait for service to be ready
    sleep 10

    if systemctl is-active --quiet "$ODOO_SERVICE"; then
        log "Odoo service is active"
    else
        error "Odoo service failed to start"
    fi
fi

# ============================================================================
# STEP 5: VALIDATE HTTP ENDPOINT
# ============================================================================

log "Step 5: Validating HTTP endpoint..."

# Test mailgate endpoint
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST https://erp.insightpulseai.net/mailgate/mailgun \
    -d "sender=deploy-test@example.com" \
    -d "recipient=test@mg.insightpulseai.net" \
    -d "subject=Deployment Validation Test" \
    -d "body-plain=Testing mailgate endpoint after deployment" || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    log "✓ Mailgate endpoint responding with HTTP 200"
else
    error "Mailgate endpoint returned HTTP $HTTP_CODE (expected 200)"
fi

# ============================================================================
# STEP 6: VERIFY DATABASE RECORD CREATION
# ============================================================================

log "Step 6: Verifying database record creation..."

# Wait for database write
sleep 2

# Query for the test message
if docker ps | grep -q postgres; then
    POSTGRES_CONTAINER=$(docker ps --filter "name=postgres" --format "{{.Names}}" | head -1)
    DB_RESULT=$(docker exec "$POSTGRES_CONTAINER" psql -U "$ODOO_USER" -d "$ODOO_DATABASE" -t -c \
        "SELECT COUNT(*) FROM mail_message WHERE subject = 'Deployment Validation Test' AND create_date >= NOW() - INTERVAL '1 minute';")
else
    DB_RESULT=$(sudo -u postgres psql -d "$ODOO_DATABASE" -t -c \
        "SELECT COUNT(*) FROM mail_message WHERE subject = 'Deployment Validation Test' AND create_date >= NOW() - INTERVAL '1 minute';")
fi

DB_COUNT=$(echo "$DB_RESULT" | tr -d ' ')

if [ "$DB_COUNT" -ge 1 ]; then
    log "✓ Database record created successfully (found $DB_COUNT records)"
else
    warn "Database record not found - mailgate may have failed silently"
fi

# ============================================================================
# STEP 7: CHECK ODOO LOGS
# ============================================================================

log "Step 7: Checking Odoo logs..."

# Check for successful inbound message log entry
if docker ps | grep -q odoo; then
    docker logs "$ODOO_CONTAINER" --tail 100 | grep "Mailgun inbound received" | tail -5
else
    tail -100 "$LOG_DIR/odoo-server.log" | grep "Mailgun inbound received" | tail -5
fi

# ============================================================================
# STEP 8: GENERATE VALIDATION REPORT
# ============================================================================

log "Step 8: Generating validation report..."

cat > "$VALIDATION_LOG" <<EOF
================================================================================
MAILGUN MAILGATE DEPLOYMENT VALIDATION REPORT
================================================================================

Deployment Date: $(date -Iseconds)
Repository Commit: $NEW_COMMIT
Previous Commit: $CURRENT_COMMIT
Database: $ODOO_DATABASE

================================================================================
DEPLOYMENT STEPS
================================================================================

1. Code Update: SUCCESS
   - Repository: $REPO_PATH
   - Branch: main
   - Commit: $NEW_COMMIT

2. Controller Verification: SUCCESS
   - controllers/__init__.py: EXISTS
   - controllers/mailgun_mailgate.py: EXISTS
   - HTTP route '/mailgate/mailgun': FOUND

3. Module Upgrade: SUCCESS
   - Module: ipai_enterprise_bridge
   - Database: $ODOO_DATABASE
   - Result: Module upgraded without errors

4. Service Restart: SUCCESS
   - Service: $ODOO_SERVICE
   - Status: ACTIVE

5. HTTP Endpoint Validation: $([ "$HTTP_CODE" = "200" ] && echo "SUCCESS" || echo "FAILED")
   - URL: https://erp.insightpulseai.net/mailgate/mailgun
   - Method: POST
   - Response Code: $HTTP_CODE
   - Expected: 200

6. Database Record Creation: $([ "$DB_COUNT" -ge 1 ] && echo "SUCCESS" || echo "WARNING")
   - Test Messages Found: $DB_COUNT
   - Query: mail_message WHERE subject = 'Deployment Validation Test'

================================================================================
RECENT MAIL MESSAGES (Last 5)
================================================================================

EOF

# Append recent messages
if docker ps | grep -q postgres; then
    docker exec "$POSTGRES_CONTAINER" psql -U "$ODOO_USER" -d "$ODOO_DATABASE" -c \
        "SELECT id, subject, email_from, email_to, create_date FROM mail_message ORDER BY create_date DESC LIMIT 5;" \
        >> "$VALIDATION_LOG"
else
    sudo -u postgres psql -d "$ODOO_DATABASE" -c \
        "SELECT id, subject, email_from, email_to, create_date FROM mail_message ORDER BY create_date DESC LIMIT 5;" \
        >> "$VALIDATION_LOG"
fi

cat >> "$VALIDATION_LOG" <<EOF

================================================================================
ROLLBACK INSTRUCTIONS (If Needed)
================================================================================

To rollback this deployment:

1. Revert to previous commit:
   cd $REPO_PATH
   git reset --hard $CURRENT_COMMIT

2. Downgrade module:
   docker exec $ODOO_CONTAINER odoo -d $ODOO_DATABASE -u ipai_enterprise_bridge --stop-after-init
   # OR
   sudo -u $ODOO_USER odoo -c /etc/odoo/odoo.conf -d $ODOO_DATABASE -u ipai_enterprise_bridge --stop-after-init

3. Restart service:
   docker restart $ODOO_CONTAINER
   # OR
   sudo systemctl restart $ODOO_SERVICE

================================================================================
NEXT STEPS
================================================================================

1. Send test messages via Mailgun API to verify end-to-end integration:
   - deploy@insightpulseai.net
   - support@insightpulseai.net
   - invoices@insightpulseai.net
   - test-archive@mg.insightpulseai.net

2. Check Mailgun events API for delivery status:
   curl -s --user "api:\$MAILGUN_API_KEY" \\
     "https://api.mailgun.net/v3/mg.insightpulseai.net/events?limit=10"

3. Monitor Odoo logs for inbound message processing:
   docker logs -f $ODOO_CONTAINER | grep "Mailgun inbound"
   # OR
   tail -f $LOG_DIR/odoo-server.log | grep "Mailgun inbound"

4. Verify mail.message records in database for each test route

================================================================================
VALIDATION COMPLETE
================================================================================

Report saved to: $VALIDATION_LOG
Overall Status: $([ "$HTTP_CODE" = "200" ] && [ "$DB_COUNT" -ge 1 ] && echo "SUCCESS ✓" || echo "REVIEW REQUIRED ⚠")

EOF

log "Validation report generated: $VALIDATION_LOG"

# ============================================================================
# FINAL OUTPUT
# ============================================================================

# Generate JSON summary
cat > "${VALIDATION_LOG%.txt}.json" <<EOF
{
  "deployment_date": "$(date -Iseconds)",
  "deploy_status": "$([ "$HTTP_CODE" = "200" ] && [ "$DB_COUNT" -ge 1 ] && echo "SUCCESS" || echo "PARTIAL")",
  "repository": {
    "path": "$REPO_PATH",
    "previous_commit": "$CURRENT_COMMIT",
    "current_commit": "$NEW_COMMIT"
  },
  "module": {
    "name": "ipai_enterprise_bridge",
    "database": "$ODOO_DATABASE",
    "upgrade_status": "SUCCESS"
  },
  "http_check": {
    "url": "https://erp.insightpulseai.net/mailgate/mailgun",
    "status_code": $HTTP_CODE,
    "expected": 200,
    "result": "$([ "$HTTP_CODE" = "200" ] && echo "PASS" || echo "FAIL")"
  },
  "message_ingest": {
    "test_messages_found": $DB_COUNT,
    "result": "$([ "$DB_COUNT" -ge 1 ] && echo "PASS" || echo "WARNING")"
  },
  "db_log_excerpt": "See mail_message table - last 5 records in validation report",
  "validation_report_path": "$VALIDATION_LOG",
  "validation_json_path": "${VALIDATION_LOG%.txt}.json"
}
EOF

log "JSON summary generated: ${VALIDATION_LOG%.txt}.json"

# Display summary
echo ""
echo "================================================================================"
echo "DEPLOYMENT SUMMARY"
echo "================================================================================"
echo ""
echo "Deploy Status:        $([ "$HTTP_CODE" = "200" ] && [ "$DB_COUNT" -ge 1 ] && echo -e "${GREEN}SUCCESS ✓${NC}" || echo -e "${YELLOW}REVIEW REQUIRED ⚠${NC}")"
echo "HTTP Endpoint:        $([ "$HTTP_CODE" = "200" ] && echo -e "${GREEN}PASS${NC}" || echo -e "${RED}FAIL${NC}") (HTTP $HTTP_CODE)"
echo "Database Ingestion:   $([ "$DB_COUNT" -ge 1 ] && echo -e "${GREEN}PASS${NC}" || echo -e "${YELLOW}WARNING${NC}") ($DB_COUNT records)"
echo "Validation Report:    $VALIDATION_LOG"
echo "JSON Summary:         ${VALIDATION_LOG%.txt}.json"
echo ""
echo "================================================================================"

if [ "$HTTP_CODE" = "200" ] && [ "$DB_COUNT" -ge 1 ]; then
    log "✓ Deployment completed successfully!"
    exit 0
else
    warn "Deployment completed but validation has warnings - review logs"
    exit 1
fi
