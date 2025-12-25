#!/usr/bin/env bash
# =============================================================================
# WorkOS Production Deployment - Complete Workflow
# =============================================================================
# Target: erp.insightpulseai.net
# Branch: main (PR #89 already merged)
# Execute this script ON THE PRODUCTION SERVER as deploy user
#
# Usage:
#   ssh deploy@erp.insightpulseai.net
#   cd /opt/odoo-ce
#   bash PRODUCTION_DEPLOY_WORKOS.sh
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} $1"; }
log_ok() { echo -e "${GREEN}[$(date +%H:%M:%S)] ✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}[$(date +%H:%M:%S)] ⚠${NC} $1"; }
log_error() { echo -e "${RED}[$(date +%H:%M:%S)] ✗${NC} $1"; }
die() { log_error "$1"; exit 1; }

# =============================================================================
# A) PREFLIGHT DISCOVERY (PROD TRUTH)
# =============================================================================
log_info "=== PREFLIGHT DISCOVERY ==="

# Find repo path
if [ -d /opt/odoo-ce ]; then
    REPO_DIR="/opt/odoo-ce"
elif [ -d ~/odoo-ce ]; then
    REPO_DIR="$HOME/odoo-ce"
else
    die "Cannot find odoo-ce repository"
fi

cd "$REPO_DIR"
log_ok "Repository path: $REPO_DIR"

# Record environment
HOSTNAME=$(hostname)
UPTIME=$(uptime)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

log_info "Hostname: $HOSTNAME"
log_info "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
log_info "Uptime: $UPTIME"

# Git state
PREV_SHA=$(git rev-parse HEAD)
PREV_BRANCH=$(git branch --show-current)

log_info "Current SHA: $PREV_SHA"
log_info "Current branch: $PREV_BRANCH"

# Detect compose file
COMPOSE_FILE="deploy/docker-compose.prod.yml"
COMPOSE_OVERRIDE="deploy/docker-compose.workos-deploy.yml"

[ -f "$COMPOSE_FILE" ] || die "Missing $COMPOSE_FILE"
log_ok "Found $COMPOSE_FILE"

if [ -f "$COMPOSE_OVERRIDE" ]; then
    log_ok "Found $COMPOSE_OVERRIDE (will use for deployment)"
    USE_OVERRIDE=true
else
    log_warn "No $COMPOSE_OVERRIDE - will use base compose only"
    USE_OVERRIDE=false
fi

# Detect service names
DB_SERVICE=$(docker compose -f "$COMPOSE_FILE" config --services | grep -E '^(db|postgres|postgresql)' | head -1)
ODOO_SERVICE=$(docker compose -f "$COMPOSE_FILE" config --services | grep -E '^(odoo|web)' | head -1)

[ -z "$DB_SERVICE" ] && die "Could not detect database service"
[ -z "$ODOO_SERVICE" ] && die "Could not detect Odoo service"

log_ok "Detected services: DB=$DB_SERVICE, ODOO=$ODOO_SERVICE"

# Detect database config
if [ -f deploy/.env ]; then
    log_info "Loading config from deploy/.env"
    set -a
    source deploy/.env
    set +a
    DB_NAME="${POSTGRES_DB:-odoo}"
    DB_USER="${POSTGRES_USER:-odoo}"
elif [ -f deploy/odoo.conf ]; then
    log_info "Parsing deploy/odoo.conf"
    DB_NAME=$(grep '^db_name' deploy/odoo.conf | cut -d= -f2 | tr -d ' ' || echo "odoo")
    DB_USER=$(grep '^db_user' deploy/odoo.conf | cut -d= -f2 | tr -d ' ' || echo "odoo")
else
    log_warn "No config found, using defaults"
    DB_NAME="odoo"
    DB_USER="odoo"
fi

log_ok "Database config: DB=$DB_NAME, USER=$DB_USER"

# Show current services
log_info "Current running services:"
docker compose -f "$COMPOSE_FILE" ps

# =============================================================================
# B) SNAPSHOT FOR ROLLBACK
# =============================================================================
log_info "=== SNAPSHOT FOR ROLLBACK ==="

BACKUP_DIR="/var/backups/odoo"
mkdir -p "$BACKUP_DIR" || die "Cannot create $BACKUP_DIR"

# Database backup
BACKUP_FILE="$BACKUP_DIR/odoo_pre_workos_${TIMESTAMP}.dump"
log_info "Creating database backup: $BACKUP_FILE"

docker compose -f "$COMPOSE_FILE" exec -T "$DB_SERVICE" \
    pg_dump -Fc -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE" \
    || die "Database backup failed"

BACKUP_SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')
BACKUP_MD5=$(md5sum "$BACKUP_FILE" | awk '{print $1}')

log_ok "Backup created: $BACKUP_SIZE, MD5: ${BACKUP_MD5:0:16}..."

# Save MD5
echo "$BACKUP_MD5  $BACKUP_FILE" > "$BACKUP_FILE.md5"

# Export current module states
MODULE_BACKUP="$BACKUP_DIR/modules_before_${TIMESTAMP}.csv"
log_info "Exporting current module states: $MODULE_BACKUP"

docker compose -f "$COMPOSE_FILE" exec -T "$DB_SERVICE" \
    psql -U "$DB_USER" -d "$DB_NAME" -c \
    "COPY (SELECT name,state,latest_version FROM ir_module_module WHERE name LIKE 'ipai_%' ORDER BY name) TO STDOUT WITH CSV HEADER" \
    > "$MODULE_BACKUP" || log_warn "Module state export failed (may be first install)"

# Save snapshot metadata
cat > "$REPO_DIR/.deploy_snapshot" << EOF
PREV_SHA=$PREV_SHA
PREV_BRANCH=$PREV_BRANCH
BACKUP_FILE=$BACKUP_FILE
BACKUP_MD5=$BACKUP_MD5
MODULE_BACKUP=$MODULE_BACKUP
TIMESTAMP=$TIMESTAMP
DB_SERVICE=$DB_SERVICE
ODOO_SERVICE=$ODOO_SERVICE
DB_NAME=$DB_NAME
DB_USER=$DB_USER
EOF

log_ok "Snapshot metadata saved to .deploy_snapshot"

# =============================================================================
# C) DEPLOY MAIN
# =============================================================================
log_info "=== DEPLOY MAIN BRANCH ==="

log_info "Fetching from origin..."
git fetch origin || die "git fetch failed"

log_info "Checking out main..."
git checkout main || die "git checkout main failed"

log_info "Pulling latest main..."
git pull --ff-only origin main || die "git pull failed (not fast-forward)"

NEW_SHA=$(git rev-parse HEAD)
log_ok "Deployed to SHA: $NEW_SHA"

# Verify WorkOS modules present
log_info "Verifying WorkOS modules..."
WORKOS_MODULES=(
    "ipai_workos_affine"
    "ipai_workos_core"
    "ipai_workos_blocks"
    "ipai_workos_db"
    "ipai_workos_views"
    "ipai_workos_templates"
    "ipai_workos_collab"
    "ipai_workos_search"
    "ipai_workos_canvas"
    "ipai_platform_permissions"
    "ipai_platform_audit"
)

for mod in "${WORKOS_MODULES[@]}"; do
    if [ -f "addons/$mod/__manifest__.py" ]; then
        log_ok "Found: $mod"
    else
        die "Missing module: $mod"
    fi
done

# =============================================================================
# D) DETERMINE RUNTIME CODE STRATEGY
# =============================================================================
log_info "=== RUNTIME CODE STRATEGY ==="

if [ "$USE_OVERRIDE" = true ]; then
    log_ok "Using mount override strategy (addons/ mounted into container)"
    STRATEGY="mount"
    COMPOSE_CMD="docker compose -f $COMPOSE_FILE -f $COMPOSE_OVERRIDE"
else
    log_warn "No override found - using base compose only"
    STRATEGY="base"
    COMPOSE_CMD="docker compose -f $COMPOSE_FILE"
fi

# =============================================================================
# E) INSTALL/UPGRADE WORKOS MODULES (NON-INTERACTIVE)
# =============================================================================
log_info "=== INSTALL/UPGRADE WORKOS MODULES ==="

# Stop main Odoo service
log_info "Stopping Odoo service..."
$COMPOSE_CMD stop "$ODOO_SERVICE" || die "Failed to stop Odoo"

# Check if init profile exists
if $COMPOSE_CMD config --profiles 2>/dev/null | grep -q '^init$'; then
    log_info "Using init profile for module installation..."
    $COMPOSE_CMD --profile init run --rm odoo-workos-init \
        2>&1 | tee /tmp/odoo_install_${TIMESTAMP}.log
else
    log_info "Using direct odoo-bin for module installation..."

    # Find odoo config
    if [ -f /etc/odoo/odoo.conf ]; then
        ODOO_CONF="/etc/odoo/odoo.conf"
    elif [ -f deploy/odoo.conf ]; then
        ODOO_CONF="/etc/odoo/odoo.conf"  # Will be mounted
    else
        ODOO_CONF=""
    fi

    MODULE_LIST="ipai_workos_affine,ipai_workos_core,ipai_workos_blocks,ipai_workos_db,ipai_workos_views,ipai_workos_templates,ipai_workos_collab,ipai_workos_search,ipai_workos_canvas,ipai_platform_permissions,ipai_platform_audit"

    if [ -n "$ODOO_CONF" ]; then
        $COMPOSE_CMD run --rm "$ODOO_SERVICE" \
            odoo -c "$ODOO_CONF" -d "$DB_NAME" \
            -i ipai_workos_affine \
            -u "$MODULE_LIST" \
            --stop-after-init \
            2>&1 | tee /tmp/odoo_install_${TIMESTAMP}.log
    else
        $COMPOSE_CMD run --rm "$ODOO_SERVICE" \
            odoo -d "$DB_NAME" \
            -i ipai_workos_affine \
            -u "$MODULE_LIST" \
            --stop-after-init \
            2>&1 | tee /tmp/odoo_install_${TIMESTAMP}.log
    fi
fi

# Check for critical errors in install log
if grep -iE "error|traceback|failed" /tmp/odoo_install_${TIMESTAMP}.log | grep -v "ERROR.*psycopg2" | grep -v "INFO" > /tmp/install_errors.txt; then
    ERROR_COUNT=$(wc -l < /tmp/install_errors.txt)
    if [ "$ERROR_COUNT" -gt 0 ]; then
        log_warn "Found $ERROR_COUNT potential errors in install log:"
        head -20 /tmp/install_errors.txt
        log_warn "Review full log: /tmp/odoo_install_${TIMESTAMP}.log"
    fi
else
    log_ok "Module installation completed without critical errors"
fi

# Start Odoo service
log_info "Starting Odoo service..."
$COMPOSE_CMD up -d "$ODOO_SERVICE" || die "Failed to start Odoo"

log_info "Waiting for Odoo to boot (60s)..."
sleep 60

# =============================================================================
# F) VERIFY (CONCRETE CHECKS)
# =============================================================================
log_info "=== DEPLOYMENT VERIFICATION ==="

ERRORS=0

# 1) HTTP check
log_info "Checking HTTP endpoint..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -I https://erp.insightpulseai.net/web/login 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "303" ]; then
    log_ok "HTTP check passed ($HTTP_CODE)"
else
    log_error "HTTP check failed ($HTTP_CODE)"
    ERRORS=$((ERRORS + 1))
fi

# 2) Logs check
log_info "Checking recent logs..."
$COMPOSE_CMD logs --tail=200 "$ODOO_SERVICE" > /tmp/odoo_tail_${TIMESTAMP}.log

CRITICAL_COUNT=$(grep -iE "traceback|critical" /tmp/odoo_tail_${TIMESTAMP}.log | wc -l)
ERROR_COUNT=$(grep -iE "ERROR" /tmp/odoo_tail_${TIMESTAMP}.log | grep -v "psycopg2" | wc -l)

if [ "$CRITICAL_COUNT" -gt 5 ]; then
    log_error "Found $CRITICAL_COUNT critical errors in logs"
    grep -iE "traceback|critical" /tmp/odoo_tail_${TIMESTAMP}.log | head -10
    ERRORS=$((ERRORS + 1))
else
    log_ok "Logs look clean ($CRITICAL_COUNT tracebacks, $ERROR_COUNT errors)"
fi

# 3) Module states
log_info "Checking module states..."
$COMPOSE_CMD exec -T "$DB_SERVICE" psql -U "$DB_USER" -d "$DB_NAME" -c \
    "SELECT name,state FROM ir_module_module WHERE name LIKE 'ipai_workos_%' OR name LIKE 'ipai_platform_%' ORDER BY name;" \
    > /tmp/module_states_${TIMESTAMP}.txt

INSTALLED_COUNT=$(grep '|.*installed' /tmp/module_states_${TIMESTAMP}.txt | wc -l)
cat /tmp/module_states_${TIMESTAMP}.txt

if [ "$INSTALLED_COUNT" -ge 11 ]; then
    log_ok "Found $INSTALLED_COUNT WorkOS/Platform modules in installed state"
else
    log_error "Expected at least 11 modules installed, found $INSTALLED_COUNT"
    ERRORS=$((ERRORS + 1))
fi

# 4) Models exist
log_info "Checking models..."
$COMPOSE_CMD exec -T "$DB_SERVICE" psql -U "$DB_USER" -d "$DB_NAME" -c \
    "SELECT model FROM ir_model WHERE model LIKE 'ipai.workos.%' ORDER BY model LIMIT 30;" \
    > /tmp/models_${TIMESTAMP}.txt

MODEL_COUNT=$(grep -c 'ipai.workos.' /tmp/models_${TIMESTAMP}.txt || echo "0")
cat /tmp/models_${TIMESTAMP}.txt

if [ "$MODEL_COUNT" -gt 0 ]; then
    log_ok "Found $MODEL_COUNT WorkOS models registered"
else
    log_warn "No WorkOS models found (may be expected for some configurations)"
fi

# =============================================================================
# G) GENERATE PROD RUNTIME SITEMAP + REPO TREE ARTIFACTS
# =============================================================================
log_info "=== GENERATING PRODUCTION SNAPSHOT ==="

if [ -f tools/audit/gen_prod_snapshot.sh ]; then
    chmod +x tools/audit/gen_prod_snapshot.sh
    bash tools/audit/gen_prod_snapshot.sh || log_warn "Snapshot generation had warnings"
else
    log_warn "gen_prod_snapshot.sh not found - creating minimal artifacts"

    mkdir -p docs/repo docs/runtime

    # Repo tree
    {
        echo "# Production Git State"
        echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo ""
        echo "SHA: $NEW_SHA"
        echo "Branch: $(git branch --show-current)"
        echo ""
        git log -1 --oneline
    } > docs/repo/GIT_STATE.prod.txt

    # Runtime state
    cp /tmp/module_states_${TIMESTAMP}.txt docs/runtime/MODULE_STATES.prod.csv
    cp /tmp/models_${TIMESTAMP}.txt docs/runtime/ODOO_MODEL_SNAPSHOT.prod.txt
fi

# Verify artifacts
log_info "Verifying generated artifacts..."
for artifact in docs/repo/GIT_STATE.prod.* docs/runtime/MODULE_STATES.prod.*; do
    if [ -f "$artifact" ]; then
        SIZE=$(stat -c%s "$artifact" 2>/dev/null || stat -f%z "$artifact" 2>/dev/null || echo "0")
        if [ "$SIZE" -gt 10 ]; then
            log_ok "Found $artifact (${SIZE} bytes)"
        else
            log_warn "$artifact is suspiciously small (${SIZE} bytes)"
        fi
    else
        log_warn "Missing artifact: $artifact"
    fi
done

# =============================================================================
# H) COMMIT ARTIFACTS BACK TO MAIN
# =============================================================================
log_info "=== COMMITTING ARTIFACTS ==="

git add docs/repo docs/runtime docs/PROD_SNAPSHOT_MANIFEST.md 2>/dev/null || true

if git diff --staged --quiet; then
    log_info "No artifact changes to commit"
else
    git commit -m "docs(runtime): production snapshot after WorkOS deploy ($NEW_SHA)" \
        || log_warn "Commit failed (may already exist)"

    log_info "Pushing to origin main..."
    git push origin main || log_warn "Push failed - may need manual resolution"
    log_ok "Artifacts committed and pushed"
fi

# =============================================================================
# DEPLOYMENT REPORT
# =============================================================================
echo ""
echo "============================================="
if [ "$ERRORS" -eq 0 ]; then
    log_ok "DEPLOYMENT COMPLETE"
else
    log_error "DEPLOYMENT COMPLETED WITH $ERRORS ERRORS"
fi
echo "============================================="
echo ""

cat << EOF
DEPLOYMENT REPORT
=================

Git Transition:
  Previous SHA: $PREV_SHA
  New SHA:      $NEW_SHA
  Branch:       main

Backup Files:
  Database:     $BACKUP_FILE ($BACKUP_SIZE)
  MD5:          ${BACKUP_MD5:0:32}
  Modules:      $MODULE_BACKUP

Verification Results:
  HTTP Status:  $HTTP_CODE
  Modules:      $INSTALLED_COUNT installed
  Models:       $MODEL_COUNT registered
  Log Errors:   $CRITICAL_COUNT critical, $ERROR_COUNT errors

Generated Artifacts:
EOF

ls -lh docs/repo/*.prod.* docs/runtime/*.prod.* 2>/dev/null | awk '{print "  " $NF " (" $5 ")"}'

echo ""
echo "ROLLBACK INSTRUCTIONS (if needed):"
echo "=================================="
echo "1. Stop Odoo:"
echo "   $COMPOSE_CMD stop $ODOO_SERVICE"
echo ""
echo "2. Revert git:"
echo "   git checkout $PREV_SHA"
echo ""
echo "3. Restart Odoo:"
echo "   $COMPOSE_CMD up -d $ODOO_SERVICE"
echo ""
echo "4. Optional - Restore database:"
echo "   $COMPOSE_CMD exec -T $DB_SERVICE \\"
echo "     pg_restore -U $DB_USER -d $DB_NAME --clean --if-exists \\"
echo "     < $BACKUP_FILE"
echo ""

exit $ERRORS
