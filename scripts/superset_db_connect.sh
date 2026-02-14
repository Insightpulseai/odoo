#!/usr/bin/env bash
set -euo pipefail

# Superset Database Connection Tester
# Tests connectivity to Odoo PostgreSQL and Supabase PostgreSQL

echo "🔍 Testing Superset Database Connections..."

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test PostgreSQL connection
test_connection() {
    local name="$1"
    local host="$2"
    local port="$3"
    local user="$4"
    local database="$5"
    local password="$6"

    echo ""
    echo "Testing: $name"
    echo "  Host: $host:$port"
    echo "  Database: $database"
    echo "  User: $user"

    if PGPASSWORD="$password" psql -h "$host" -p "$port" -U "$user" -d "$database" -c "SELECT version();" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ Connection successful${NC}"

        # Get version
        version=$(PGPASSWORD="$password" psql -h "$host" -p "$port" -U "$user" -d "$database" -t -c "SELECT version();" 2>/dev/null | head -1 | xargs)
        echo "  Version: ${version:0:50}..."

        return 0
    else
        echo -e "  ${RED}❌ Connection failed${NC}"
        return 1
    fi
}

# Function to generate Superset SQLAlchemy URI
generate_uri() {
    local name="$1"
    local user="$2"
    local password="$3"
    local host="$4"
    local port="$5"
    local database="$6"
    local ssl="${7:-}"

    local uri="postgresql://${user}:${password}@${host}:${port}/${database}"
    if [ -n "$ssl" ]; then
        uri="${uri}?sslmode=require"
    fi

    echo ""
    echo "📋 Superset Connection URI for: $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    # Mask password in output
    masked_uri=$(echo "$uri" | sed "s/:${password}@/:***@/")
    echo "$masked_uri"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Test 1: Odoo PostgreSQL (Local Dev)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 1: Odoo PostgreSQL (Local Development)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ODOO_HOST="${ODOO_DB_HOST:-localhost}"
ODOO_PORT="${ODOO_DB_PORT:-5432}"
ODOO_USER="${ODOO_DB_USER:-odoo}"
ODOO_DB="${ODOO_DB_NAME:-odoo_dev}"
ODOO_PASSWORD="${ODOO_DB_PASSWORD:-odoo}"

if test_connection "Odoo Dev" "$ODOO_HOST" "$ODOO_PORT" "$ODOO_USER" "$ODOO_DB" "$ODOO_PASSWORD"; then
    generate_uri "Odoo Development" "$ODOO_USER" "$ODOO_PASSWORD" "$ODOO_HOST" "$ODOO_PORT" "$ODOO_DB"
fi

# Test 2: Supabase PostgreSQL (Direct)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 2: Supabase PostgreSQL (Direct Connection)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

SUPABASE_HOST="${SUPABASE_DB_HOST:-aws-0-us-east-1.pooler.supabase.com}"
SUPABASE_PORT="${SUPABASE_DB_PORT:-5432}"
SUPABASE_USER="${SUPABASE_DB_USER:-postgres.spdtwktxdalcfigzeqrz}"
SUPABASE_DB="${SUPABASE_DB_NAME:-postgres}"
SUPABASE_PASSWORD="${SUPABASE_DB_PASSWORD:-}"

if [ -z "$SUPABASE_PASSWORD" ]; then
    echo -e "${YELLOW}⚠️  SUPABASE_DB_PASSWORD not set. Skipping Supabase test.${NC}"
    echo "   Set it in .env or export SUPABASE_DB_PASSWORD=your_password"
else
    if test_connection "Supabase Direct" "$SUPABASE_HOST" "$SUPABASE_PORT" "$SUPABASE_USER" "$SUPABASE_DB" "$SUPABASE_PASSWORD"; then
        generate_uri "Supabase (OPS)" "$SUPABASE_USER" "$SUPABASE_PASSWORD" "$SUPABASE_HOST" "$SUPABASE_PORT" "$SUPABASE_DB" "ssl"

        # Check for ops schema
        echo ""
        echo "Checking for 'ops' schema..."
        if PGPASSWORD="$SUPABASE_PASSWORD" psql -h "$SUPABASE_HOST" -p "$SUPABASE_PORT" -U "$SUPABASE_USER" -d "$SUPABASE_DB" -t -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'ops';" 2>/dev/null | grep -q ops; then
            echo -e "${GREEN}✅ 'ops' schema exists${NC}"
        else
            echo -e "${YELLOW}⚠️  'ops' schema not found${NC}"
        fi
    fi
fi

# Test 3: Supabase PostgreSQL (Pooler)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 3: Supabase PostgreSQL (Pooler - Recommended)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

SUPABASE_POOLER_PORT="6543"

if [ -n "$SUPABASE_PASSWORD" ]; then
    if test_connection "Supabase Pooler" "$SUPABASE_HOST" "$SUPABASE_POOLER_PORT" "$SUPABASE_USER" "$SUPABASE_DB" "$SUPABASE_PASSWORD"; then
        generate_uri "Supabase Pooler (Transactional)" "$SUPABASE_USER" "$SUPABASE_PASSWORD" "$SUPABASE_HOST" "$SUPABASE_POOLER_PORT" "$SUPABASE_DB" "ssl"
    fi
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Copy the connection URIs above into Superset"
echo "📖 Full documentation: docs/superset/DATABASE_CONNECTIONS.md"
echo ""
echo "Next steps:"
echo "  1. Open Superset: http://localhost:8088"
echo "  2. Go to: Data → Databases → + Database"
echo "  3. Paste the connection URI from above"
echo "  4. Click 'Test Connection' then 'Connect'"
echo ""
