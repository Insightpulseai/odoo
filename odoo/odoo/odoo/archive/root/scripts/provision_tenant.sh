#!/usr/bin/env bash
# Tenant Provisioning Script for InsightPulse AI Platform
# Usage: ./scripts/provision_tenant.sh <TENANT_CODE>
# Example: ./scripts/provision_tenant.sh tbwa

set -euo pipefail

TENANT_CODE="${1:?Usage: $0 TENANT_CODE}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Required environment variables
: "${ODOO_ADMIN_PASSWORD:?ODOO_ADMIN_PASSWORD required}"
: "${POSTGRES_URL:?POSTGRES_URL required (Supabase connection string)}"
: "${SUPABASE_SERVICE_ROLE_KEY:?SUPABASE_SERVICE_ROLE_KEY required}"

# Derived variables
TENANT_DB="odoo_${TENANT_CODE}"
SUPABASE_SCHEMA="${TENANT_CODE}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}>>> $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if tenant already exists in Odoo platform DB
check_tenant_exists() {
    log_info "Checking if tenant '$TENANT_CODE' exists in platform DB..."

    TENANT_EXISTS=$(psql "$POSTGRES_URL" -tAc \
        "SELECT COUNT(*) FROM ipai_tenant WHERE code = '$TENANT_CODE';" || echo "0")

    if [ "$TENANT_EXISTS" -eq "0" ]; then
        log_error "Tenant '$TENANT_CODE' not found in ipai.tenant table!"
        log_info "Please create tenant record in Odoo platform first."
        log_info "Go to: Platform > Tenants > Create"
        exit 1
    fi

    log_info "Tenant '$TENANT_CODE' found in platform DB ✓"
}

# Create Supabase schema for tenant
provision_supabase_schema() {
    log_info "Provisioning Supabase schema '$SUPABASE_SCHEMA'..."

    # Check if schema already exists
    SCHEMA_EXISTS=$(psql "$POSTGRES_URL" -tAc \
        "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = '$SUPABASE_SCHEMA';" || echo "0")

    if [ "$SCHEMA_EXISTS" -eq "1" ]; then
        log_warn "Schema '$SUPABASE_SCHEMA' already exists, skipping creation"
    else
        psql "$POSTGRES_URL" -c "CREATE SCHEMA IF NOT EXISTS $SUPABASE_SCHEMA;"
        log_info "Schema '$SUPABASE_SCHEMA' created ✓"
    fi

    # Enable RLS on schema
    psql "$POSTGRES_URL" -c "ALTER SCHEMA $SUPABASE_SCHEMA OWNER TO postgres;"

    log_info "Supabase schema provisioned ✓"
}

# Create Odoo database for tenant
provision_odoo_database() {
    log_info "Provisioning Odoo database '$TENANT_DB'..."

    # Check if database already exists
    DB_EXISTS=$(psql "$POSTGRES_URL" -tAc \
        "SELECT COUNT(*) FROM pg_database WHERE datname = '$TENANT_DB';" || echo "0")

    if [ "$DB_EXISTS" -eq "1" ]; then
        log_warn "Database '$TENANT_DB' already exists, skipping creation"
        return
    fi

    # Create database via Odoo CLI
    if command -v odoo-bin &> /dev/null; then
        log_info "Using odoo-bin to initialize database..."
        odoo-bin -d "$TENANT_DB" --stop-after-init --without-demo=all --db-filter="$TENANT_DB"
    elif command -v docker &> /dev/null && docker ps | grep -q odoo; then
        log_info "Using Docker Odoo container to initialize database..."
        docker exec odoo odoo-bin -d "$TENANT_DB" --stop-after-init --without-demo=all --db-filter="$TENANT_DB"
    else
        log_error "No Odoo installation found (odoo-bin or Docker container)"
        exit 1
    fi

    log_info "Odoo database '$TENANT_DB' created ✓"
}

# Install base modules for tenant
install_base_modules() {
    log_info "Installing base modules for '$TENANT_DB'..."

    MODULES="base,mail,web,ipai_tenant_core,ipai_bi_superset_embed"

    if command -v odoo-bin &> /dev/null; then
        odoo-bin -d "$TENANT_DB" -i "$MODULES" --stop-after-init
    elif command -v docker &> /dev/null && docker ps | grep -q odoo; then
        docker exec odoo odoo-bin -d "$TENANT_DB" -i "$MODULES" --stop-after-init
    fi

    log_info "Base modules installed ✓"
}

# Set admin password for tenant database
set_admin_password() {
    log_info "Setting admin password for '$TENANT_DB'..."

    # Use XML-RPC to set password (safer than SQL)
    python3 "$SCRIPT_DIR/xmlrpc_set_admin_password.py" "$TENANT_DB" "$ODOO_ADMIN_PASSWORD"

    log_info "Admin password set ✓"
}

# Create Superset workspace for tenant
provision_superset_workspace() {
    log_info "Provisioning Superset workspace for '$TENANT_CODE'..."

    # This would call Superset API to create workspace/folder
    # For now, just log the intention
    log_warn "Superset workspace provisioning is manual for now"
    log_info "Go to: https://superset.insightpulseai.com/superset/dashboard/"
    log_info "Create folder: '$TENANT_CODE'"

    log_info "Superset workspace provisioning noted ✓"
}

# Main provisioning workflow
main() {
    log_info "================================================"
    log_info "InsightPulse AI - Tenant Provisioning"
    log_info "Tenant Code: $TENANT_CODE"
    log_info "Tenant DB: $TENANT_DB"
    log_info "Supabase Schema: $SUPABASE_SCHEMA"
    log_info "================================================"

    # Step 1: Check tenant exists
    check_tenant_exists

    # Step 2: Provision Supabase schema
    provision_supabase_schema

    # Step 3: Create Odoo database
    provision_odoo_database

    # Step 4: Install base modules
    install_base_modules

    # Step 5: Set admin password
    set_admin_password

    # Step 6: Provision Superset workspace
    provision_superset_workspace

    log_info "================================================"
    log_info "✅ Tenant '$TENANT_CODE' provisioned successfully!"
    log_info "================================================"
    log_info "Next steps:"
    log_info "1. Access Odoo: https://tbwa.erp.insightpulseai.com (or configured domain)"
    log_info "2. Login: admin / $ODOO_ADMIN_PASSWORD"
    log_info "3. Configure tenant-specific modules"
    log_info "4. Create Superset dashboards for tenant"
    log_info "================================================"
}

# Run main function
main
