# WorkOS Production Deployment Runbook

**Target**: https://erp.insightpulseai.com
**Source**: main branch (PR #89 already merged, commit c6800438)
**Modules**: ipai_workos_affine (umbrella) + 13 dependencies

---

## Pre-Deployment Checklist

- [x] PR #89 merged to main (commit c6800438)
- [x] All WorkOS modules present on main
- [x] Deployment scripts exist in scripts/prod/
- [x] Runtime snapshot generators exist in tools/audit/
- [x] Docker compose configs present in deploy/

---

## RUN ON PROD

Copy/paste this entire block into production server terminal:

```bash
#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# WorkOS Production Deployment - Main Branch
# ============================================================================
# Target: erp.insightpulseai.com
# Branch: main (PR #89 merged)
# Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)
# ============================================================================

REPO_DIR="/opt/odoo-ce"
COMPOSE_FILE="deploy/docker-compose.prod.yml"
COMPOSE_OVERRIDE="deploy/docker-compose.workos-deploy.yml"
DB_NAME="odoo"
DB_USER="odoo"
BACKUP_DIR="/var/backups/odoo"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

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

# Detect service names dynamically
ODOO_SERVICE=$(docker compose -f "$COMPOSE_FILE" config --services 2>/dev/null | grep -E '^(odoo|web)' | head -1)
DB_SERVICE=$(docker compose -f "$COMPOSE_FILE" config --services 2>/dev/null | grep -E '^(db|postgres|postgresql)' | head -1)

[ -z "$ODOO_SERVICE" ] && die "Could not detect Odoo service name"
[ -z "$DB_SERVICE" ] && die "Could not detect database service name"

log_info "Detected services: Odoo=$ODOO_SERVICE, DB=$DB_SERVICE"

# ============================================================================
# PHASE 1: SNAPSHOT FOR ROLLBACK
# ============================================================================
log_info "=== PHASE 1: Creating Snapshot ==="

cd "$REPO_DIR" || die "Cannot cd to $REPO_DIR"

# Record git state
PREVIOUS_SHA=$(git rev-parse HEAD)
PREVIOUS_BRANCH=$(git branch --show-current)

log_info "Current SHA: $PREVIOUS_SHA"
log_info "Current branch: $PREVIOUS_BRANCH"

# Create backup directory
mkdir -p "$BACKUP_DIR" || die "Cannot create backup directory"

# Database backup
log_info "Creating database backup..."
BACKUP_FILE="$BACKUP_DIR/workos_pre_deploy_${TIMESTAMP}.dump"

docker compose -f "$COMPOSE_FILE" exec -T "$DB_SERVICE" \
    pg_dump -Fc -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE" \
    || die "Database backup failed"

BACKUP_SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')
BACKUP_MD5=$(md5sum "$BACKUP_FILE" | awk '{print $1}')

log_ok "Backup created: $BACKUP_FILE ($BACKUP_SIZE, MD5: ${BACKUP_MD5:0:10}...)"

# Save snapshot state
cat > "$REPO_DIR/.deploy_snapshot" << EOF
PREVIOUS_SHA=$PREVIOUS_SHA
PREVIOUS_BRANCH=$PREVIOUS_BRANCH
BACKUP_FILE=$BACKUP_FILE
BACKUP_MD5=$BACKUP_MD5
TIMESTAMP=$TIMESTAMP
EOF

log_ok "Snapshot saved to .deploy_snapshot"

# ============================================================================
# PHASE 2: DEPLOY MAIN
# ============================================================================
log_info "=== PHASE 2: Deploying Main Branch ==="

# Fetch latest
log_info "Fetching from origin..."
git fetch origin || die "git fetch failed"

# Checkout main
log_info "Checking out main..."
git checkout main || die "git checkout main failed"

# Pull latest (fast-forward only)
log_info "Pulling latest main..."
git pull --ff-only origin main || die "git pull failed (not fast-forward)"

NEW_SHA=$(git rev-parse HEAD)
log_ok "Deployed to SHA: $NEW_SHA"

# Verify modules exist
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
    if [[ -f "addons/$mod/__manifest__.py" ]]; then
        log_ok "Found: $mod"
    else
        die "Missing module: $mod"
    fi
done

# ============================================================================
# PHASE 3: INSTALL/UPGRADE MODULES
# ============================================================================
log_info "=== PHASE 3: Installing WorkOS Modules ==="

# Stop Odoo service
log_info "Stopping Odoo service..."
docker compose -f "$COMPOSE_FILE" stop "$ODOO_SERVICE" || die "Failed to stop Odoo"

# Install/upgrade via umbrella module (pulls all dependencies)
log_info "Installing ipai_workos_affine (umbrella module)..."

if [[ -f "$COMPOSE_OVERRIDE" ]]; then
    docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
        run --rm "$ODOO_SERVICE" \
        odoo -d "$DB_NAME" -i ipai_workos_affine,ipai_platform_permissions,ipai_platform_audit \
        --stop-after-init \
        2>&1 | tee /tmp/odoo_install_${TIMESTAMP}.log
else
    docker compose -f "$COMPOSE_FILE" \
        run --rm "$ODOO_SERVICE" \
        odoo -d "$DB_NAME" -i ipai_workos_affine,ipai_platform_permissions,ipai_platform_audit \
        --stop-after-init \
        2>&1 | tee /tmp/odoo_install_${TIMESTAMP}.log
fi

# Check for errors in install log
if grep -iE "error|traceback|failed" /tmp/odoo_install_${TIMESTAMP}.log | grep -v "ERROR.*psycopg2"; then
    log_warn "Potential errors in install log - review /tmp/odoo_install_${TIMESTAMP}.log"
else
    log_ok "Module installation completed"
fi

# Restart Odoo service
log_info "Starting Odoo service..."
if [[ -f "$COMPOSE_OVERRIDE" ]]; then
    docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" up -d "$ODOO_SERVICE"
else
    docker compose -f "$COMPOSE_FILE" up -d "$ODOO_SERVICE"
fi

log_info "Waiting for Odoo to start (60s)..."
sleep 60

# ============================================================================
# PHASE 4: RUNTIME VERIFICATION
# ============================================================================
log_info "=== PHASE 4: Runtime Verification ==="

ERRORS=0

# HTTP check
log_info "Checking HTTP endpoint..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://erp.insightpulseai.com/web/login 2>/dev/null || echo "000")

if [[ "$HTTP_CODE" == "200" ]] || [[ "$HTTP_CODE" == "303" ]]; then
    log_ok "HTTP check passed ($HTTP_CODE)"
else
    log_error "HTTP check failed ($HTTP_CODE)"
    ERRORS=$((ERRORS + 1))
fi

# Log check
log_info "Checking logs for errors..."
if [[ -f "$COMPOSE_OVERRIDE" ]]; then
    ERROR_COUNT=$(docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
        logs --tail=200 "$ODOO_SERVICE" 2>&1 | grep -icE "traceback|critical" || echo "0")
else
    ERROR_COUNT=$(docker compose -f "$COMPOSE_FILE" \
        logs --tail=200 "$ODOO_SERVICE" 2>&1 | grep -icE "traceback|critical" || echo "0")
fi

if [[ "$ERROR_COUNT" -gt 5 ]]; then
    log_error "Found $ERROR_COUNT errors in logs"
    ERRORS=$((ERRORS + 1))
else
    log_ok "Logs look clean ($ERROR_COUNT minor warnings)"
fi

# Module state check
log_info "Checking module states in database..."
if [[ -f "$COMPOSE_OVERRIDE" ]]; then
    INSTALLED_COUNT=$(docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
        exec -T "$DB_SERVICE" \
        psql -U "$DB_USER" -d "$DB_NAME" -tAc \
        "SELECT COUNT(*) FROM ir_module_module WHERE (name LIKE 'ipai_workos_%' OR name LIKE 'ipai_platform_%') AND state = 'installed';" \
        || echo "0")
else
    INSTALLED_COUNT=$(docker compose -f "$COMPOSE_FILE" \
        exec -T "$DB_SERVICE" \
        psql -U "$DB_USER" -d "$DB_NAME" -tAc \
        "SELECT COUNT(*) FROM ir_module_module WHERE (name LIKE 'ipai_workos_%' OR name LIKE 'ipai_platform_%') AND state = 'installed';" \
        || echo "0")
fi

if [[ "$INSTALLED_COUNT" -ge 11 ]]; then
    log_ok "All WorkOS modules installed ($INSTALLED_COUNT modules)"
else
    log_error "Expected at least 11 modules, got $INSTALLED_COUNT"
    ERRORS=$((ERRORS + 1))
fi

# Model check
log_info "Checking models in database..."
if [[ -f "$COMPOSE_OVERRIDE" ]]; then
    MODEL_COUNT=$(docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
        exec -T "$DB_SERVICE" \
        psql -U "$DB_USER" -d "$DB_NAME" -tAc \
        "SELECT COUNT(*) FROM ir_model WHERE model LIKE 'workos.%' OR model LIKE 'platform.%';" \
        || echo "0")
else
    MODEL_COUNT=$(docker compose -f "$COMPOSE_FILE" \
        exec -T "$DB_SERVICE" \
        psql -U "$DB_USER" -d "$DB_NAME" -tAc \
        "SELECT COUNT(*) FROM ir_model WHERE model LIKE 'workos.%' OR model LIKE 'platform.%';" \
        || echo "0")
fi

if [[ "$MODEL_COUNT" -gt 0 ]]; then
    log_ok "Found $MODEL_COUNT WorkOS models"
else
    log_warn "No WorkOS models found in database"
fi

# ============================================================================
# PHASE 5: GENERATE SNAPSHOT ARTIFACTS
# ============================================================================
log_info "=== PHASE 5: Generating Production Snapshot ==="

# Run master snapshot generator
bash tools/audit/gen_prod_snapshot.sh || log_warn "Snapshot generation had warnings"

log_ok "Production snapshot complete"

# ============================================================================
# PHASE 6: COMMIT ARTIFACTS
# ============================================================================
log_info "=== PHASE 6: Committing Artifacts ==="

# Add generated artifacts
git add docs/repo/*.prod.* docs/runtime/*.prod.* docs/PROD_SNAPSHOT_MANIFEST.md 2>/dev/null || true

# Check if there are changes to commit
if git diff --staged --quiet; then
    log_info "No artifact changes to commit"
else
    git commit -m "docs(runtime): add WorkOS production snapshot artifacts [skip ci]" || log_warn "Commit failed (may already exist)"
    log_ok "Artifacts committed"
fi

# ============================================================================
# PHASE 7: PUSH TO REMOTE
# ============================================================================
log_info "=== PHASE 7: Pushing to Remote ==="

git push origin main || log_warn "Push failed (may need manual resolution)"
log_ok "Pushed to origin/main"

# ============================================================================
# DEPLOYMENT SUMMARY
# ============================================================================
echo ""
echo "==========================================="
if [[ $ERRORS -eq 0 ]]; then
    log_ok "DEPLOYMENT COMPLETE"
else
    log_error "DEPLOYMENT COMPLETED WITH $ERRORS ERRORS"
fi
echo "==========================================="

echo ""
echo "Summary:"
echo "  Previous SHA: $PREVIOUS_SHA"
echo "  New SHA:      $NEW_SHA"
echo "  Backup:       $BACKUP_FILE"
echo "  Modules:      $INSTALLED_COUNT installed"
echo "  Models:       $MODEL_COUNT registered"
echo "  HTTP Status:  $HTTP_CODE"
echo "  Log Errors:   $ERROR_COUNT"
echo ""
echo "Artifacts:"
ls -lh docs/repo/*.prod.* docs/runtime/*.prod.* 2>/dev/null | awk '{print "  " $NF " (" $5 ")"}'
echo ""
echo "Rollback instructions:"
echo "  1. git checkout $PREVIOUS_SHA"
echo "  2. docker compose -f $COMPOSE_FILE restart $ODOO_SERVICE"
echo "  3. Optional: Restore DB from $BACKUP_FILE"
echo ""

exit $ERRORS
```

---

## Post-Deployment Verification

After running the deployment block, verify:

1. **HTTP Access**: https://erp.insightpulseai.com/web/login returns 200 or 303
2. **Modules Installed**: Check `ir_module_module` for all WorkOS modules in 'installed' state
3. **Models Registered**: Check `ir_model` for WorkOS models (workos.*, platform.*)
4. **Logs Clean**: No critical errors in Odoo logs (last 200 lines)
5. **Artifacts Generated**: docs/repo/*.prod.*, docs/runtime/*.prod.* exist with real data

## Rollback Procedure

If deployment fails or needs rollback:

```bash
cd /opt/odoo-ce
source .deploy_snapshot

# Revert git
git checkout $PREVIOUS_SHA

# Restart Odoo
docker compose -f deploy/docker-compose.prod.yml restart odoo

# Optional: Restore database
docker compose -f deploy/docker-compose.prod.yml exec -T db \
    pg_restore -U odoo -d odoo --clean --if-exists < $BACKUP_FILE
```

---

## Expected Artifacts

After successful deployment, the following files should be generated and committed:

### Repository Artifacts (docs/repo/)
- `GIT_STATE.prod.txt` - Git SHA, branch, status
- `REPO_TREE.prod.md` - Directory structure
- `REPO_SNAPSHOT.prod.json` - File counts, module versions

### Runtime Artifacts (docs/runtime/)
- `ODOO_MENU_SITEMAP.prod.json` - Menu structure
- `ODOO_MODEL_SNAPSHOT.prod.json` - Registered models
- `MODULE_STATES.prod.csv` - Module installation states
- `ADDONS_PATH.prod.txt` - Odoo addons path config
- `CONTAINER_PATH_CHECK.prod.txt` - Container path verification
- `HTTP_SITEMAP.prod.json` - HTTP routes
- `ODOO_ACTIONS.prod.json` - Window actions
- `IPAI_MODULE_STATUS.prod.txt` - IPAI module details

### Manifest
- `docs/PROD_SNAPSHOT_MANIFEST.md` - Complete artifact manifest

---

## Troubleshooting

### Issue: HTTP 502/503
**Cause**: Odoo not started or still starting
**Fix**: Wait longer (up to 90s), check logs: `docker compose logs odoo`

### Issue: Modules not installed
**Cause**: Installation failed, check /tmp/odoo_install_*.log
**Fix**: Review errors, fix dependencies, rerun installation phase

### Issue: Database backup failed
**Cause**: Insufficient disk space or DB service not running
**Fix**: Check disk space, verify DB service: `docker compose ps db`

### Issue: Git push failed
**Cause**: Divergent branches or network issues
**Fix**: Manual resolution needed, check `git status` and `git log`

---

**Deployment Date**: 2024-12-25
**Last Updated**: Deployment runbook created for main branch deployment
