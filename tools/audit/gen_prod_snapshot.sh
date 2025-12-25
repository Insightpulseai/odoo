#!/usr/bin/env bash
# =============================================================================
# MASTER PRODUCTION SNAPSHOT GENERATOR
# =============================================================================
# Generates complete production parity snapshot including:
# - Repo tree and git state
# - Odoo runtime sitemap (menus, models, modules)
# - HTTP sitemap (if reachable)
#
# Usage:
#   ./tools/audit/gen_prod_snapshot.sh
#
# Environment Variables:
#   COMPOSE_FILE          - Docker compose file (default: deploy/docker-compose.prod.yml)
#   COMPOSE_OVERRIDE      - Compose override (default: deploy/docker-compose.workos-deploy.yml)
#   DB_SERVICE            - Database service name (default: db)
#   DB_NAME               - Database name (default: odoo)
#   DB_USER               - Database user (default: odoo)
#   ODOO_SERVICE          - Odoo service name (default: odoo)
#   BASE_URL              - Public URL (default: https://erp.insightpulseai.net)
#   SKIP_HTTP_CRAWL       - Set to 1 to skip HTTP crawling
#
# Outputs:
#   docs/repo/GIT_STATE.prod.txt
#   docs/repo/REPO_TREE.prod.md
#   docs/repo/REPO_SNAPSHOT.prod.json
#   docs/runtime/ODOO_MENU_SITEMAP.prod.json
#   docs/runtime/ODOO_MODEL_SNAPSHOT.prod.json
#   docs/runtime/MODULE_STATES.prod.csv
#   docs/runtime/ADDONS_PATH.prod.txt
#   docs/runtime/CONTAINER_PATH_CHECK.prod.txt
#   docs/runtime/HTTP_SITEMAP.prod.json
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Configuration
export COMPOSE_FILE="${COMPOSE_FILE:-deploy/docker-compose.prod.yml}"
export COMPOSE_OVERRIDE="${COMPOSE_OVERRIDE:-deploy/docker-compose.workos-deploy.yml}"
export DB_SERVICE="${DB_SERVICE:-db}"
export DB_NAME="${DB_NAME:-odoo}"
export DB_USER="${DB_USER:-odoo}"
export ODOO_SERVICE="${ODOO_SERVICE:-odoo}"
export BASE_URL="${BASE_URL:-https://erp.insightpulseai.net}"
SKIP_HTTP_CRAWL="${SKIP_HTTP_CRAWL:-0}"

echo "=============================================="
echo "  PRODUCTION PARITY SNAPSHOT GENERATOR"
echo "=============================================="
echo ""
echo "Repo:     $REPO_ROOT"
echo "Compose:  $COMPOSE_FILE"
echo "Database: $DB_NAME"
echo "URL:      $BASE_URL"
echo ""

cd "$REPO_ROOT"

# Ensure output directories exist
mkdir -p docs/repo docs/runtime

# =============================================================================
# STEP 1: REPO TREE SNAPSHOT
# =============================================================================
echo "=============================================="
echo "STEP 1: Generating Repo Tree Snapshot"
echo "=============================================="

chmod +x "$SCRIPT_DIR/gen_repo_tree_prod.sh"
"$SCRIPT_DIR/gen_repo_tree_prod.sh"

echo ""

# =============================================================================
# STEP 2: ODOO RUNTIME SITEMAP
# =============================================================================
echo "=============================================="
echo "STEP 2: Generating Odoo Runtime Sitemap"
echo "=============================================="

# Check if Docker is available and services are running
if command -v docker &>/dev/null; then
    if docker compose -f "$COMPOSE_FILE" ps 2>/dev/null | grep -q "$DB_SERVICE"; then
        chmod +x "$SCRIPT_DIR/gen_runtime_sitemap.sh"
        "$SCRIPT_DIR/gen_runtime_sitemap.sh" "$COMPOSE_FILE" "$DB_SERVICE" "$DB_NAME" "$DB_USER"
    else
        echo "⚠ Database service not running - skipping runtime sitemap"
        echo "  Start services with: docker compose -f $COMPOSE_FILE up -d"

        # Create placeholder files
        echo '{"error": "database not accessible", "generated_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > docs/runtime/ODOO_MENU_SITEMAP.prod.json
        echo '{"error": "database not accessible", "generated_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > docs/runtime/ODOO_MODEL_SNAPSHOT.prod.json
        echo "# Database not accessible at generation time" > docs/runtime/MODULE_STATES.prod.csv
    fi
else
    echo "⚠ Docker not available - skipping runtime sitemap"
    echo '{"error": "docker not available", "generated_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > docs/runtime/ODOO_MENU_SITEMAP.prod.json
    echo '{"error": "docker not available", "generated_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > docs/runtime/ODOO_MODEL_SNAPSHOT.prod.json
fi

echo ""

# =============================================================================
# STEP 3: HTTP SITEMAP
# =============================================================================
echo "=============================================="
echo "STEP 3: Generating HTTP Sitemap"
echo "=============================================="

if [[ "$SKIP_HTTP_CRAWL" == "1" ]]; then
    echo "⚠ HTTP crawl skipped (SKIP_HTTP_CRAWL=1)"
    echo '{"skipped": true, "generated_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > docs/runtime/HTTP_SITEMAP.prod.json
else
    # Test if URL is reachable
    if curl -sf -o /dev/null --connect-timeout 5 "$BASE_URL/web/login" 2>/dev/null; then
        echo "URL reachable, starting crawl..."
        python3 "$SCRIPT_DIR/http_crawler.py" "$BASE_URL" "docs/runtime/HTTP_SITEMAP.prod.json"
    else
        echo "⚠ URL not reachable: $BASE_URL"
        echo "  Creating placeholder sitemap"

        # At least test a few endpoints if possible
        cat > docs/runtime/HTTP_SITEMAP.prod.json << EOF
{
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "base_url": "$BASE_URL",
  "error": "host not reachable from this environment",
  "manual_checks_required": [
    "curl -I $BASE_URL/web",
    "curl -I $BASE_URL/web/login"
  ]
}
EOF
    fi
fi

echo ""

# =============================================================================
# SUMMARY
# =============================================================================
echo "=============================================="
echo "  SNAPSHOT GENERATION COMPLETE"
echo "=============================================="
echo ""
echo "Artifacts generated:"
echo ""
echo "docs/repo/"
ls -la docs/repo/*.prod.* 2>/dev/null | awk '{print "  " $NF " (" $5 " bytes)"}'
echo ""
echo "docs/runtime/"
ls -la docs/runtime/*.prod.* 2>/dev/null | awk '{print "  " $NF " (" $5 " bytes)"}'
echo ""

# Generate manifest
cat > docs/PROD_SNAPSHOT_MANIFEST.md << EOF
# Production Snapshot Manifest

Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Host: $(hostname)
Repo: $REPO_ROOT

## Repo Artifacts

| File | Description |
|------|-------------|
| docs/repo/GIT_STATE.prod.txt | Git SHA, branch, status |
| docs/repo/REPO_TREE.prod.md | Directory structure |
| docs/repo/REPO_SNAPSHOT.prod.json | File counts, module versions |

## Runtime Artifacts

| File | Description |
|------|-------------|
| docs/runtime/ODOO_MENU_SITEMAP.prod.json | Odoo UI menus and actions |
| docs/runtime/ODOO_MODEL_SNAPSHOT.prod.json | Installed models |
| docs/runtime/MODULE_STATES.prod.csv | Module installation states |
| docs/runtime/ADDONS_PATH.prod.txt | Odoo addons path config |
| docs/runtime/CONTAINER_PATH_CHECK.prod.txt | Container path verification |
| docs/runtime/HTTP_SITEMAP.prod.json | Public HTTP endpoints |
| docs/runtime/ODOO_ACTIONS.prod.json | Window actions |
| docs/runtime/IPAI_MODULE_STATUS.prod.txt | IPAI module details |

## Regeneration

\`\`\`bash
# On production server:
cd /opt/odoo-ce
./tools/audit/gen_prod_snapshot.sh

# Environment variables:
export COMPOSE_FILE=deploy/docker-compose.prod.yml
export DB_NAME=odoo
export BASE_URL=https://erp.insightpulseai.net
\`\`\`
EOF

echo "Manifest: docs/PROD_SNAPSHOT_MANIFEST.md"
echo ""
echo "To commit:"
echo "  git add docs/repo docs/runtime docs/PROD_SNAPSHOT_MANIFEST.md"
echo "  git commit -m 'docs(runtime): add production sitemap + repo snapshot artifacts'"
echo ""
