#!/bin/bash
# Deploy EE Parity Tracking Schema to Supabase
# Usage: ./deploy_parity_schema.sh

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=============================================================="
echo "      EE Parity Schema Deployment"
echo "=============================================================="

# Check required environment variables
check_env() {
    local var_name=$1
    if [ -z "${!var_name:-}" ]; then
        echo -e "${RED}ERROR: $var_name is not set${NC}"
        echo "Set it with: export $var_name=your_value"
        return 1
    fi
    echo -e "${GREEN}[OK]${NC} $var_name is set"
    return 0
}

echo ""
echo "Checking required environment variables..."

MISSING=0
check_env "SUPABASE_DB_PASSWORD" || MISSING=1
check_env "SUPABASE_PROJECT_REF" || MISSING=1

if [ $MISSING -eq 1 ]; then
    echo ""
    echo "Required environment variables:"
    echo "  SUPABASE_DB_PASSWORD - Database password from Supabase dashboard"
    echo "  SUPABASE_PROJECT_REF - Project reference (default: spdtwktxdalcfigzeqrz)"
    echo ""
    echo "Example:"
    echo "  export SUPABASE_DB_PASSWORD='your_password'"
    echo "  export SUPABASE_PROJECT_REF='spdtwktxdalcfigzeqrz'"
    echo "  ./deploy_parity_schema.sh"
    exit 1
fi

# Build connection string
PROJECT_REF="${SUPABASE_PROJECT_REF:-spdtwktxdalcfigzeqrz}"
DB_HOST="db.${PROJECT_REF}.supabase.co"
DB_USER="postgres"
DB_NAME="postgres"
DB_PORT="5432"

echo ""
echo "Connecting to: $DB_HOST"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATION_FILE="${SCRIPT_DIR}/../supabase/migrations/20260126_000001_ee_parity_tracking.sql"

if [ ! -f "$MIGRATION_FILE" ]; then
    echo -e "${RED}ERROR: Migration file not found: $MIGRATION_FILE${NC}"
    exit 1
fi

echo "Deploying: $(basename $MIGRATION_FILE)"
echo ""

# Deploy schema
PGPASSWORD="$SUPABASE_DB_PASSWORD" psql \
    -h "$DB_HOST" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -p "$DB_PORT" \
    -f "$MIGRATION_FILE" \
    --echo-errors \
    2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=============================================================="
    echo "      Schema deployment successful!"
    echo "==============================================================${NC}"
    echo ""
    echo "Deployed views:"
    echo "  - v_latest_parity_results"
    echo "  - v_parity_scorecard"
    echo "  - v_overall_parity"
    echo "  - v_parity_trend"
    echo "  - v_parity_gaps"
    echo ""
    echo "Next steps:"
    echo "  1. Open Superset and add datasets for the views above"
    echo "  2. Run parity tests: ./tools/parity/run_ee_parity.sh -f json"
    echo "  3. Insert results: See tools/parity/superset_parity_dashboard.sql"
else
    echo ""
    echo -e "${RED}Schema deployment failed. Check errors above.${NC}"
    exit 1
fi
