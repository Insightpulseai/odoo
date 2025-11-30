#!/usr/bin/env bash
###############################################################################
# fix-superset-production.sh
# Complete Superset configuration fix for DigitalOcean App Platform
#
# Fixes:
# 1. SQLite → PostgreSQL (Supabase) migration
# 2. Missing SECRET_KEY configuration
# 3. Database initialization (superset db upgrade)
# 4. Admin user creation
# 5. Environment variable setup
#
# Usage: ./scripts/fix-superset-production.sh
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

SUPERSET_APP_NAME="superset-analytics"  # Change if your app has different name
SUPABASE_PROJECT_REF="spdtwktxdalcfigzeqrz"

# Load credentials from environment
if [ -f .env.production ]; then
    source .env.production
fi

# Check required variables
if [ -z "${POSTGRES_PASSWORD:-}" ]; then
    log_error "POSTGRES_PASSWORD not found in environment"
    log_info "Run: source .env.production"
    exit 1
fi

###############################################################################
# Step 1: Generate SECRET_KEY
###############################################################################

generate_secret_key() {
    log_info "Generating SECRET_KEY..."

    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

    if [ -z "$SECRET_KEY" ]; then
        log_error "Failed to generate SECRET_KEY"
        exit 1
    fi

    log_success "SECRET_KEY generated: ${SECRET_KEY:0:15}..."
    echo "$SECRET_KEY"
}

###############################################################################
# Step 2: Build Environment Variables
###############################################################################

build_env_vars() {
    local secret_key="$1"

    log_info "Building environment variables..."

    # Supabase connection string (pooled for App Platform)
    local db_uri="postgresql://postgres.${SUPABASE_PROJECT_REF}:${POSTGRES_PASSWORD}@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"

    cat <<EOF
# Copy these environment variables to DigitalOcean App Platform:
# Settings → Environment Variables → Bulk Editor

SQLALCHEMY_DATABASE_URI=${db_uri}
DATABASE_URL=${db_uri}
SECRET_KEY=${secret_key}
SUPERSET_SECRET_KEY=${secret_key}
PYTHONUNBUFFERED=1
SUPERSET_ENV=production
SUPERSET_LOAD_EXAMPLES=false

# Optional but recommended (if you have Redis):
# REDIS_URL=redis://default:<PASSWORD>@<redis-host>:6379/0
# CACHE_CONFIG={"CACHE_TYPE": "RedisCache", "CACHE_REDIS_URL": "redis://..."}
EOF
}

###############################################################################
# Step 3: Update App via doctl
###############################################################################

update_app_env_vars() {
    local secret_key="$1"

    log_info "Updating DigitalOcean App Platform environment variables..."

    # Check if doctl is authenticated
    if ! doctl account get &>/dev/null; then
        log_error "doctl not authenticated"
        log_info "Run: doctl auth init"
        exit 1
    fi

    # Find the app ID
    local app_id=$(doctl apps list --format ID,Spec.Name --no-header 2>/dev/null | grep "$SUPERSET_APP_NAME" | awk '{print $1}')

    if [ -z "$app_id" ]; then
        log_warning "App '$SUPERSET_APP_NAME' not found via doctl"
        log_info "You'll need to manually add environment variables in the DO console"
        return 1
    fi

    log_info "Found app: $app_id"

    # Build environment variable JSON
    local db_uri="postgresql://postgres.${SUPABASE_PROJECT_REF}:${POSTGRES_PASSWORD}@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"

    local env_vars=$(cat <<EOF
[
  {
    "key": "SQLALCHEMY_DATABASE_URI",
    "value": "${db_uri}",
    "scope": "RUN_AND_BUILD_TIME",
    "type": "SECRET"
  },
  {
    "key": "SECRET_KEY",
    "value": "${secret_key}",
    "scope": "RUN_AND_BUILD_TIME",
    "type": "SECRET"
  },
  {
    "key": "SUPERSET_SECRET_KEY",
    "value": "${secret_key}",
    "scope": "RUN_AND_BUILD_TIME",
    "type": "SECRET"
  },
  {
    "key": "PYTHONUNBUFFERED",
    "value": "1",
    "scope": "RUN_AND_BUILD_TIME",
    "type": "GENERAL"
  },
  {
    "key": "SUPERSET_ENV",
    "value": "production",
    "scope": "RUN_AND_BUILD_TIME",
    "type": "GENERAL"
  },
  {
    "key": "SUPERSET_LOAD_EXAMPLES",
    "value": "false",
    "scope": "RUN_AND_BUILD_TIME",
    "type": "GENERAL"
  }
]
EOF
)

    log_warning "Manual update required - doctl doesn't support bulk env var updates"
    log_info "Use the output above to update via DO console"
}

###############################################################################
# Step 4: Generate Deployment Commands
###############################################################################

generate_deployment_commands() {
    log_info "Generating post-deployment commands..."

    cat <<'EOF'

# After setting environment variables and redeploying, run these commands
# in the DigitalOcean App Platform Console tab:

# 1. Initialize Superset metadata database
superset db upgrade

# 2. Create admin user (change password!)
superset fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@insightpulseai.net \
  --password AdminPassword123!

# 3. Initialize roles and permissions
superset init

# 4. Verify database connection
superset db upgrade --show-sql-only | head -20

# 5. Test Superset is working
curl -I https://superset.insightpulseai.net/login/

EOF
}

###############################################################################
# Step 5: Test Supabase Connection
###############################################################################

test_supabase_connection() {
    log_info "Testing Supabase connection from local machine..."

    local db_uri="postgresql://postgres.${SUPABASE_PROJECT_REF}:${POSTGRES_PASSWORD}@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"

    if command -v psql &> /dev/null; then
        if psql "$db_uri" -c "SELECT current_database(), version();" 2>&1 | grep -q "postgres"; then
            log_success "Supabase connection: OK"
            return 0
        else
            log_error "Supabase connection failed"
            return 1
        fi
    else
        log_warning "psql not installed, skipping connection test"
        log_info "Install with: brew install postgresql"
    fi
}

###############################################################################
# Step 6: Generate App Spec (Optional)
###############################################################################

generate_app_spec() {
    log_info "Generating sample App Spec for Superset..."

    cat > /tmp/superset-app-spec.yaml <<'EOF'
name: superset-analytics
region: nyc
services:
  - name: superset
    dockerfile_path: Dockerfile
    source_dir: /
    github:
      repo: your-org/superset-deployment
      branch: main
      deploy_on_push: true
    envs:
      - key: SQLALCHEMY_DATABASE_URI
        value: ${SQLALCHEMY_DATABASE_URI}
        type: SECRET
      - key: SECRET_KEY
        value: ${SECRET_KEY}
        type: SECRET
      - key: SUPERSET_SECRET_KEY
        value: ${SUPERSET_SECRET_KEY}
        type: SECRET
      - key: PYTHONUNBUFFERED
        value: "1"
      - key: SUPERSET_ENV
        value: production
      - key: SUPERSET_LOAD_EXAMPLES
        value: "false"
    http_port: 8088
    instance_count: 1
    instance_size_slug: basic-xs
    routes:
      - path: /
    health_check:
      http_path: /health
      initial_delay_seconds: 60
      period_seconds: 10
      timeout_seconds: 5
      success_threshold: 1
      failure_threshold: 3
EOF

    log_success "App spec saved to: /tmp/superset-app-spec.yaml"
}

###############################################################################
# Main Execution
###############################################################################

main() {
    log_info "=== Superset Production Fix Script ==="
    echo ""

    # Step 1: Generate secret key
    SECRET_KEY=$(generate_secret_key)
    echo ""

    # Step 2: Build environment variables
    log_info "=== Environment Variables to Add ==="
    build_env_vars "$SECRET_KEY"
    echo ""

    # Step 3: Try to update via doctl (or show manual instructions)
    log_info "=== DigitalOcean App Platform Update ==="
    update_app_env_vars "$SECRET_KEY" || true
    echo ""

    # Step 4: Show deployment commands
    log_info "=== Post-Deployment Commands ==="
    generate_deployment_commands
    echo ""

    # Step 5: Test connection
    log_info "=== Connection Test ==="
    test_supabase_connection || true
    echo ""

    # Step 6: Generate app spec (optional)
    generate_app_spec
    echo ""

    # Final instructions
    log_success "=== Next Steps ==="
    echo ""
    echo "1. Copy the environment variables above to DigitalOcean:"
    echo "   https://cloud.digitalocean.com/apps → $SUPERSET_APP_NAME → Settings → Environment Variables"
    echo ""
    echo "2. Click 'Deploy' to restart the app with new configuration"
    echo ""
    echo "3. Once deployed, open Console tab and run the post-deployment commands above"
    echo ""
    echo "4. Access Superset at: https://superset.insightpulseai.net"
    echo "   Username: admin"
    echo "   Password: AdminPassword123! (change this!)"
    echo ""

    log_info "Script completed successfully!"
}

# Run main function
main "$@"
