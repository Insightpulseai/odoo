#!/bin/bash
# =============================================================================
# CI Smoke Test for Odoo CE Custom Image
# =============================================================================
# Runs --stop-after-init boot test to verify image can start successfully
# with a fresh PostgreSQL database.
#
# Usage:
#   ./scripts/ci_smoke_test.sh <image>
#   ./scripts/ci_smoke_test.sh ghcr.io/jgtolentino/odoo-ce:18.0-abc1234
#
# Exit Codes:
#   0 - Smoke test passed
#   1 - Smoke test failed
#
# Environment Variables:
#   POSTGRES_IMAGE   - PostgreSQL image to use (default: postgres:16-alpine)
#   NETWORK_NAME     - Docker network name (default: ipai-smoke-<random>)
#   TIMEOUT          - Timeout in seconds for Odoo init (default: 300)
#   KEEP_CONTAINERS  - Set to "1" to keep containers after test for debugging
#   MODULES_CHECK    - Comma-separated list of modules to verify (optional)
#
# =============================================================================

set -euo pipefail

# Configuration
IMG="${1:?ERROR: Image reference required. Usage: $0 <image>}"
POSTGRES_IMAGE="${POSTGRES_IMAGE:-postgres:16-alpine}"
NETWORK_NAME="${NETWORK_NAME:-ipai-smoke-$$}"
TIMEOUT="${TIMEOUT:-300}"
KEEP_CONTAINERS="${KEEP_CONTAINERS:-0}"

# Container names
PG_CONTAINER="pg-smoke-$$"
ODOO_CONTAINER="odoo-smoke-$$"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[PASS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[FAIL]${NC} $1"; }

# Cleanup function
cleanup() {
    local exit_code=$?

    if [[ "$KEEP_CONTAINERS" == "1" && $exit_code -ne 0 ]]; then
        log_warn "KEEP_CONTAINERS=1: Containers preserved for debugging"
        log_info "  PostgreSQL: docker logs $PG_CONTAINER"
        log_info "  Odoo:       docker logs $ODOO_CONTAINER"
        log_info "  Cleanup:    docker rm -f $PG_CONTAINER $ODOO_CONTAINER; docker network rm $NETWORK_NAME"
        return $exit_code
    fi

    log_info "Cleaning up containers and network..."
    docker rm -f "$ODOO_CONTAINER" 2>/dev/null || true
    docker rm -f "$PG_CONTAINER" 2>/dev/null || true
    docker network rm "$NETWORK_NAME" 2>/dev/null || true

    return $exit_code
}

trap cleanup EXIT

# Start smoke test
echo ""
echo "============================================="
echo "  IPAI Odoo CE Smoke Test"
echo "============================================="
echo "  Image:    $IMG"
echo "  Postgres: $POSTGRES_IMAGE"
echo "  Timeout:  ${TIMEOUT}s"
echo "============================================="
echo ""

# Step 1: Create network
log_info "Creating Docker network: $NETWORK_NAME"
docker network create "$NETWORK_NAME" >/dev/null 2>&1 || true

# Step 2: Start PostgreSQL
log_info "Starting PostgreSQL container: $PG_CONTAINER"
docker run -d \
    --name "$PG_CONTAINER" \
    --network "$NETWORK_NAME" \
    -e POSTGRES_USER=odoo \
    -e POSTGRES_PASSWORD=odoo \
    -e POSTGRES_DB=postgres \
    "$POSTGRES_IMAGE" >/dev/null

# Wait for PostgreSQL to be ready
log_info "Waiting for PostgreSQL to be ready..."
for i in $(seq 1 30); do
    if docker exec "$PG_CONTAINER" pg_isready -U odoo -q 2>/dev/null; then
        log_success "PostgreSQL is ready"
        break
    fi
    if [[ $i -eq 30 ]]; then
        log_error "PostgreSQL failed to start within 30 seconds"
        docker logs "$PG_CONTAINER"
        exit 1
    fi
    sleep 1
done

# Step 3: Run Odoo with --stop-after-init
log_info "Running Odoo --stop-after-init (timeout: ${TIMEOUT}s)..."

# Build module init command if MODULES_CHECK is set
INIT_MODULES=""
if [[ -n "${MODULES_CHECK:-}" ]]; then
    INIT_MODULES="-i $MODULES_CHECK"
    log_info "Installing modules: $MODULES_CHECK"
fi

# Run Odoo with stop-after-init
START_TIME=$(date +%s)
set +e
docker run --rm \
    --name "$ODOO_CONTAINER" \
    --network "$NETWORK_NAME" \
    -e HOST="$PG_CONTAINER" \
    -e USER=odoo \
    -e PASSWORD=odoo \
    -e DB_NAME=odoo \
    "$IMG" \
    --stop-after-init \
    -d odoo \
    $INIT_MODULES \
    --log-level=info \
    2>&1 | tee /tmp/odoo-smoke-$$.log &

ODOO_PID=$!

# Wait for completion with timeout
ELAPSED=0
while kill -0 $ODOO_PID 2>/dev/null; do
    sleep 5
    ELAPSED=$((ELAPSED + 5))
    if [[ $ELAPSED -ge $TIMEOUT ]]; then
        log_error "Odoo init timed out after ${TIMEOUT}s"
        kill $ODOO_PID 2>/dev/null || true
        docker stop "$ODOO_CONTAINER" 2>/dev/null || true

        log_error "Last 50 lines of Odoo log:"
        tail -50 /tmp/odoo-smoke-$$.log

        exit 1
    fi
    echo -n "."
done
echo ""

wait $ODOO_PID
EXIT_CODE=$?
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
set -e

# Step 4: Check result
if [[ $EXIT_CODE -eq 0 ]]; then
    log_success "Odoo --stop-after-init completed successfully (${DURATION}s)"
else
    log_error "Odoo --stop-after-init failed with exit code: $EXIT_CODE"
    log_error "Last 100 lines of Odoo log:"
    tail -100 /tmp/odoo-smoke-$$.log

    # Check for common failure patterns
    if grep -q "module .* not found" /tmp/odoo-smoke-$$.log; then
        log_error "Detected: Missing module(s)"
    fi
    if grep -q "CRITICAL" /tmp/odoo-smoke-$$.log; then
        log_error "Detected: CRITICAL error in logs"
    fi
    if grep -q "OperationalError" /tmp/odoo-smoke-$$.log; then
        log_error "Detected: Database connection error"
    fi

    exit 1
fi

# Step 5: Verify database was created
log_info "Verifying database creation..."
if docker exec "$PG_CONTAINER" psql -U odoo -d odoo -c "SELECT 1" >/dev/null 2>&1; then
    log_success "Database 'odoo' created and accessible"
else
    log_error "Database 'odoo' not accessible"
    exit 1
fi

# Step 6: Check module installation (if specified)
if [[ -n "${MODULES_CHECK:-}" ]]; then
    log_info "Verifying module installation..."
    IFS=',' read -ra MODULES <<< "$MODULES_CHECK"
    for module in "${MODULES[@]}"; do
        module=$(echo "$module" | xargs)  # trim whitespace
        if docker exec "$PG_CONTAINER" psql -U odoo -d odoo -tAc \
            "SELECT state FROM ir_module_module WHERE name='$module'" | grep -q "installed"; then
            log_success "Module '$module' is installed"
        else
            log_error "Module '$module' not installed or not found"
            exit 1
        fi
    done
fi

# Cleanup temp file
rm -f /tmp/odoo-smoke-$$.log

# Final summary
echo ""
echo "============================================="
log_success "SMOKE TEST PASSED"
echo "============================================="
echo "  Image:    $IMG"
echo "  Duration: ${DURATION}s"
echo "  Status:   All checks passed"
echo "============================================="
echo ""

exit 0
