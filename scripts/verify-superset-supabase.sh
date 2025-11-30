#!/usr/bin/env bash
###############################################################################
# verify-superset-supabase.sh
# Verify Superset connection to Supabase PostgreSQL
#
# Checks:
# 1. Superset is accessible
# 2. Supabase PostgreSQL connection works
# 3. Superset metadata tables exist
# 4. Data source configuration (if applicable)
#
# Usage: ./scripts/verify-superset-supabase.sh
###############################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ ${NC}$1"; }
log_success() { echo -e "${GREEN}✅ ${NC}$1"; }
log_warning() { echo -e "${YELLOW}⚠️  ${NC}$1"; }
log_error() { echo -e "${RED}❌ ${NC}$1"; }

###############################################################################
# Configuration
###############################################################################

SUPERSET_URL="https://superset.insightpulseai.net"
SUPABASE_HOST="aws-1-us-east-1.pooler.supabase.com"
SUPABASE_PORT="6543"
SUPABASE_USER="postgres.spdtwktxdalcfigzeqrz"
SUPABASE_DB="postgres"

# Load password from CLAUDE.md (canonical source)
SUPABASE_PASSWORD="SHWYXDMFAwXI1drT"

###############################################################################
# Check 1: Superset Accessibility
###############################################################################

check_superset_accessible() {
    log_info "=== Check 1: Superset Accessibility ==="

    if curl -sf "${SUPERSET_URL}/login/" -o /dev/null; then
        log_success "Superset is accessible: ${SUPERSET_URL}"
    else
        log_error "Superset is not responding"
        exit 1
    fi
}

###############################################################################
# Check 2: Supabase PostgreSQL Connection
###############################################################################

check_supabase_connection() {
    log_info "=== Check 2: Supabase PostgreSQL Connection ==="

    log_info "Testing connection to ${SUPABASE_HOST}:${SUPABASE_PORT}..."

    if ! command -v psql &> /dev/null; then
        log_warning "psql not installed, skipping database connectivity test"
        log_info "Install with: brew install postgresql"
        return 0
    fi

    local connection_string="postgresql://${SUPABASE_USER}@${SUPABASE_HOST}:${SUPABASE_PORT}/${SUPABASE_DB}?sslmode=require"

    if PGPASSWORD="${SUPABASE_PASSWORD}" psql "$connection_string" -c "SELECT current_database(), version();" &> /dev/null; then
        log_success "Supabase connection successful"

        # Get database info
        local db_info=$(PGPASSWORD="${SUPABASE_PASSWORD}" psql "$connection_string" -t -c "SELECT current_database(), version();" 2>/dev/null | head -1)
        log_info "Database: $db_info"
    else
        log_error "Supabase connection failed"
        log_info "Connection string (sanitized): postgresql://${SUPABASE_USER}@${SUPABASE_HOST}:${SUPABASE_PORT}/${SUPABASE_DB}"
        exit 1
    fi
}

###############################################################################
# Check 3: Superset Metadata Tables
###############################################################################

check_superset_metadata() {
    log_info "=== Check 3: Superset Metadata Tables ==="

    if ! command -v psql &> /dev/null; then
        log_warning "psql not installed, skipping metadata check"
        return 0
    fi

    local connection_string="postgresql://${SUPABASE_USER}@${SUPABASE_HOST}:${SUPABASE_PORT}/${SUPABASE_DB}?sslmode=require"

    log_info "Checking for Superset tables..."

    # Check if logs table exists (the one that was failing)
    if PGPASSWORD="${SUPABASE_PASSWORD}" psql "$connection_string" -c "SELECT COUNT(*) FROM logs LIMIT 1;" &> /dev/null; then
        log_success "Superset 'logs' table exists"
    else
        log_warning "Superset 'logs' table not found - database may need initialization"
        log_info "Run in Superset console: superset db upgrade"
    fi

    # Check for other common Superset tables
    local tables=("dbs" "tables" "slices" "dashboards")
    local found=0

    for table in "${tables[@]}"; do
        if PGPASSWORD="${SUPABASE_PASSWORD}" psql "$connection_string" -c "SELECT COUNT(*) FROM $table LIMIT 1;" &> /dev/null 2>&1; then
            ((found++))
        fi
    done

    if [ $found -gt 0 ]; then
        log_success "Found $found Superset metadata tables"
    else
        log_warning "No Superset metadata tables found"
    fi
}

###############################################################################
# Check 4: Superset Configuration
###############################################################################

check_superset_config() {
    log_info "=== Check 4: Superset Configuration ==="

    log_info "Expected environment variables in DigitalOcean App Platform:"
    echo ""
    echo "SQLALCHEMY_DATABASE_URI=postgresql://${SUPABASE_USER}:${SUPABASE_PASSWORD}@${SUPABASE_HOST}:${SUPABASE_PORT}/${SUPABASE_DB}?sslmode=require"
    echo "DATABASE_URL=postgresql://${SUPABASE_USER}:${SUPABASE_PASSWORD}@${SUPABASE_HOST}:${SUPABASE_PORT}/${SUPABASE_DB}?sslmode=require"
    echo "SECRET_KEY=wsRBfW7Sd_q9EdL3sHztC6bTQTVy0gY9fptjsPZmFkQ"
    echo "SUPERSET_SECRET_KEY=wsRBfW7Sd_q9EdL3sHztC6bTQTVy0gY9fptjsPZmFkQ"
    echo "PYTHONUNBUFFERED=1"
    echo "SUPERSET_ENV=production"
    echo "SUPERSET_LOAD_EXAMPLES=false"
    echo ""
    log_info "Verify these in: https://cloud.digitalocean.com/apps → superset-analytics → Settings → Environment Variables"
}

###############################################################################
# Check 5: Superset Health
###############################################################################

check_superset_health() {
    log_info "=== Check 5: Superset Health ==="

    # Try to access health endpoint (if exists)
    if curl -sf "${SUPERSET_URL}/health" &> /dev/null; then
        log_success "Superset health endpoint responding"
    else
        log_warning "Superset health endpoint not available (not critical)"
    fi

    # Check login page
    if curl -sf "${SUPERSET_URL}/login/" | grep -q "Superset"; then
        log_success "Superset login page is functional"
    else
        log_warning "Superset login page may have issues"
    fi
}

###############################################################################
# Summary and Next Steps
###############################################################################

print_summary() {
    echo ""
    log_info "========================================="
    log_info "Verification Summary"
    log_info "========================================="
    echo ""
    log_info "Next Steps:"
    echo ""
    echo "1. If metadata tables are missing:"
    echo "   - Go to DigitalOcean → superset-analytics → Console"
    echo "   - Run: superset db upgrade"
    echo "   - Run: superset init"
    echo ""
    echo "2. Create admin user (if not exists):"
    echo "   superset fab create-admin \\"
    echo "     --username admin \\"
    echo "     --firstname Admin \\"
    echo "     --lastname User \\"
    echo "     --email admin@insightpulseai.net \\"
    echo "     --password AdminPassword123!"
    echo ""
    echo "3. Add Supabase as data source in Superset:"
    echo "   - Login: ${SUPERSET_URL}/login/"
    echo "   - Go to: Settings → Database Connections → + Database"
    echo "   - Choose: PostgreSQL"
    echo "   - SQLAlchemy URI:"
    echo "     postgresql://${SUPABASE_USER}:${SUPABASE_PASSWORD}@${SUPABASE_HOST}:${SUPABASE_PORT}/${SUPABASE_DB}?sslmode=require"
    echo "   - Test Connection → Save"
    echo ""
    log_info "========================================="
}

###############################################################################
# Main Execution
###############################################################################

main() {
    log_info "========================================="
    log_info "Superset ↔ Supabase Connection Verification"
    log_info "========================================="
    echo ""

    check_superset_accessible
    check_supabase_connection
    check_superset_metadata
    check_superset_config
    check_superset_health
    print_summary

    log_success "Verification complete!"
}

# Run main function
main "$@"
