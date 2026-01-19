#!/usr/bin/env bash
# deploy-mailgun-mailgate.sh
# Deploys Mailgun Mailgate controller to Odoo production
# Part of ipai_enterprise_bridge module

set -euo pipefail

# Configuration
DEPLOY_BRANCH="${DEPLOY_BRANCH:-claude/deploy-odoo-enterprise-bridge-RbvGm}"
ODOO_DATABASE="${ODOO_DATABASE:-odoo_core}"
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo-core}"
PRODUCTION_URL="${PRODUCTION_URL:-https://erp.insightpulseai.net}"
LOG_FILE="/var/log/mailgun_mailgate_deployment_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo "[$(date -Iseconds)] $*" | tee -a "$LOG_FILE"
}

error() {
    log "ERROR: $*"
    exit 1
}

# Phase 1: Pull latest code
log "Phase 1: Updating codebase"
git fetch origin "$DEPLOY_BRANCH" || error "Failed to fetch branch"
git checkout "$DEPLOY_BRANCH" || error "Failed to checkout branch"
git pull origin "$DEPLOY_BRANCH" || error "Failed to pull branch"
log "Code updated successfully"

# Phase 2: Verify module files exist
log "Phase 2: Verifying module files"
MODULE_PATH="addons/ipai/ipai_enterprise_bridge"
CONTROLLER_FILE="$MODULE_PATH/controllers/mailgun_mailgate.py"

if [[ ! -f "$CONTROLLER_FILE" ]]; then
    error "Controller file not found: $CONTROLLER_FILE"
fi
log "Module files verified"

# Phase 3: Upgrade Odoo module
log "Phase 3: Upgrading ipai_enterprise_bridge module"
if command -v docker &> /dev/null && docker ps --format '{{.Names}}' | grep -q "$ODOO_CONTAINER"; then
    # Docker deployment
    docker compose exec -T "$ODOO_CONTAINER" odoo -d "$ODOO_DATABASE" -u ipai_enterprise_bridge --stop-after-init \
        || error "Module upgrade failed"
    log "Module upgraded (Docker)"

    # Restart container
    log "Phase 4: Restarting Odoo container"
    docker compose restart "$ODOO_CONTAINER" || error "Failed to restart container"
    log "Container restarted"
else
    # Systemd deployment
    odoo -d "$ODOO_DATABASE" -u ipai_enterprise_bridge --stop-after-init \
        || error "Module upgrade failed"
    log "Module upgraded (systemd)"

    # Restart service
    log "Phase 4: Restarting Odoo service"
    systemctl restart odoo.service || error "Failed to restart service"
    log "Service restarted"
fi

# Wait for service to come up
log "Waiting for service startup..."
sleep 10

# Phase 5: Validate endpoint
log "Phase 5: Validating /mailgate/mailgun endpoint"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PRODUCTION_URL/mailgate/mailgun" 2>/dev/null || echo "000")

if [[ "$HTTP_STATUS" == "200" ]]; then
    log "Health check passed: HTTP $HTTP_STATUS"
else
    log "WARNING: Health check returned HTTP $HTTP_STATUS (may need nginx config)"
fi

# Phase 6: Test webhook
log "Phase 6: Testing webhook with sample payload"
TEST_RESPONSE=$(curl -s -X POST "$PRODUCTION_URL/mailgate/mailgun" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data "sender=deploy-test@mg.insightpulseai.net" \
    --data "recipient=test@insightpulseai.net" \
    --data "subject=Deployment Validation $(date -Iseconds)" \
    --data "body-plain=Automated deployment test message" \
    2>/dev/null || echo '{"status": "error", "message": "curl failed"}')

log "Webhook test response: $TEST_RESPONSE"

# Generate validation report
log "Phase 7: Generating validation report"
cat > "$LOG_FILE.validation.json" <<EOF
{
  "deploy_status": "completed",
  "branch": "$DEPLOY_BRANCH",
  "timestamp": "$(date -Iseconds)",
  "http_check": "$HTTP_STATUS",
  "webhook_test": $TEST_RESPONSE,
  "validation_report_path": "$LOG_FILE"
}
EOF

log "Deployment completed"
log "Validation report: $LOG_FILE.validation.json"

# Output final summary
cat <<EOF

=== DEPLOYMENT SUMMARY ===
Branch: $DEPLOY_BRANCH
Database: $ODOO_DATABASE
Endpoint: $PRODUCTION_URL/mailgate/mailgun
HTTP Status: $HTTP_STATUS
Log: $LOG_FILE
Validation: $LOG_FILE.validation.json

Next steps:
1. Verify mail.message records in database
2. Configure Mailgun route if not already done
3. Test with real inbound email
EOF
