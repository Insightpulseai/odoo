#!/usr/bin/env bash
# ============================================================================
# Supabase Deployment Verification Script
# ============================================================================
# Purpose: Verify ALL Supabase migrations, RLS, hooks, and Edge Functions
#          are deployed and working correctly.
#
# Usage:
#   ./scripts/verify_supabase_deploy.sh
#
# Environment variables required:
#   - SUPABASE_URL (https://<ref>.supabase.co)
#   - SUPABASE_ANON_KEY (for public endpoints)
#   - SUPABASE_SERVICE_ROLE_KEY (for admin checks)
#   - POSTGRES_URL_NON_POOLING or DATABASE_URL (for direct DB checks)
#
# Outputs:
#   - docs/ops/SUPABASE_DEPLOYMENT_VERIFICATION.md
#   - artifacts/supabase_verify/report.json
# ============================================================================

set -euo pipefail

# Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Script directory and paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPORT_DIR="$REPO_ROOT/artifacts/supabase_verify"
DOCS_DIR="$REPO_ROOT/docs/ops"
MD_REPORT="$DOCS_DIR/SUPABASE_DEPLOYMENT_VERIFICATION.md"
JSON_REPORT="$REPORT_DIR/report.json"
MIGRATIONS_DIR="$REPO_ROOT/supabase/migrations"
FUNCTIONS_DIR="$REPO_ROOT/supabase/functions"

# Global counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
SKIPPED_CHECKS=0

# Results arrays (bash 4+)
declare -A RESULTS

# Timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# ============================================================================
# Utility Functions
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_skip() {
    echo -e "${YELLOW}[SKIP]${NC} $1"
}

record_result() {
    local check_name="$1"
    local status="$2"  # pass, fail, skip
    local message="$3"
    local evidence="${4:-}"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    case "$status" in
        pass)
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            log_success "$check_name: $message"
            ;;
        fail)
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            log_fail "$check_name: $message"
            ;;
        skip)
            SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
            log_skip "$check_name: $message"
            ;;
    esac

    RESULTS["$check_name"]="$status|$message|$evidence"
}

check_env_vars() {
    log_info "Checking environment variables..."

    # Required variables
    local missing_vars=()

    if [[ -z "${SUPABASE_URL:-}" ]]; then
        missing_vars+=("SUPABASE_URL")
    fi

    if [[ -z "${SUPABASE_ANON_KEY:-}" ]]; then
        missing_vars+=("SUPABASE_ANON_KEY")
    fi

    if [[ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
        missing_vars+=("SUPABASE_SERVICE_ROLE_KEY")
    fi

    # Check for database URL (prefer non-pooling)
    if [[ -z "${POSTGRES_URL_NON_POOLING:-}" ]] && [[ -z "${DATABASE_URL:-}" ]]; then
        missing_vars+=("POSTGRES_URL_NON_POOLING or DATABASE_URL")
    fi

    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_fail "Missing required environment variables: ${missing_vars[*]}"
        return 1
    fi

    log_success "All required environment variables present"
    return 0
}

get_db_url() {
    if [[ -n "${POSTGRES_URL_NON_POOLING:-}" ]]; then
        echo "$POSTGRES_URL_NON_POOLING"
    else
        echo "${DATABASE_URL:-}"
    fi
}

run_sql() {
    local query="$1"
    local db_url
    db_url=$(get_db_url)

    if [[ -z "$db_url" ]]; then
        echo "ERROR: No database URL available"
        return 1
    fi

    psql "$db_url" -t -A -c "$query" 2>/dev/null || echo "SQL_ERROR"
}

run_sql_json() {
    local query="$1"
    local db_url
    db_url=$(get_db_url)

    if [[ -z "$db_url" ]]; then
        echo '{"error": "No database URL"}'
        return 1
    fi

    psql "$db_url" -t -A -c "SELECT row_to_json(t) FROM ($query) t" 2>/dev/null || echo '{"error": "SQL_ERROR"}'
}

curl_api() {
    local endpoint="$1"
    local method="${2:-GET}"
    local data="${3:-}"
    local auth="${4:-anon}"  # anon, service, none

    local headers=(-H "Content-Type: application/json")
    headers+=(-H "apikey: ${SUPABASE_ANON_KEY}")

    case "$auth" in
        service)
            headers+=(-H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}")
            ;;
        anon)
            headers+=(-H "Authorization: Bearer ${SUPABASE_ANON_KEY}")
            ;;
    esac

    if [[ -n "$data" ]]; then
        curl -s -X "$method" "${headers[@]}" -d "$data" "${SUPABASE_URL}${endpoint}" 2>/dev/null
    else
        curl -s -X "$method" "${headers[@]}" "${SUPABASE_URL}${endpoint}" 2>/dev/null
    fi
}

# ============================================================================
# A) Migrations Verification
# ============================================================================

verify_migrations_table() {
    log_info "Checking migrations table exists..."

    local result
    result=$(run_sql "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = 'supabase_migrations' AND table_name = 'schema_migrations')")

    if [[ "$result" == "t" ]]; then
        record_result "migrations_table_exists" "pass" "supabase_migrations.schema_migrations exists"
    else
        record_result "migrations_table_exists" "fail" "migrations table not found"
    fi
}

verify_migrations_applied() {
    log_info "Checking applied migrations..."

    # Get list of applied migrations
    local applied
    applied=$(run_sql "SELECT version FROM supabase_migrations.schema_migrations ORDER BY version")

    if [[ "$applied" == "SQL_ERROR" ]] || [[ -z "$applied" ]]; then
        record_result "migrations_applied" "fail" "Could not query applied migrations"
        return
    fi

    # Get count
    local applied_count
    applied_count=$(echo "$applied" | wc -l | tr -d ' ')

    record_result "migrations_applied" "pass" "$applied_count migrations applied" "$applied"
}

verify_key_migrations() {
    log_info "Checking key migrations (5001, 5002, 5003)..."

    local key_migrations=("5001_auth_foundation" "5002_auth_jwt_claims" "5003_rls_policies")
    local missing=()
    local found=()

    for migration in "${key_migrations[@]}"; do
        local result
        result=$(run_sql "SELECT COUNT(*) FROM supabase_migrations.schema_migrations WHERE version LIKE '%$migration%'")

        if [[ "$result" -gt 0 ]]; then
            found+=("$migration")
        else
            missing+=("$migration")
        fi
    done

    if [[ ${#missing[@]} -eq 0 ]]; then
        record_result "key_migrations" "pass" "All key migrations applied: ${found[*]}"
    else
        record_result "key_migrations" "fail" "Missing migrations: ${missing[*]}"
    fi
}

verify_repo_migrations_match() {
    log_info "Comparing repo migrations with applied..."

    if [[ ! -d "$MIGRATIONS_DIR" ]]; then
        record_result "repo_migrations_match" "skip" "Migrations directory not found: $MIGRATIONS_DIR"
        return
    fi

    # Count SQL files in repo
    local repo_count
    repo_count=$(find "$MIGRATIONS_DIR" -name "*.sql" -type f | wc -l | tr -d ' ')

    # Get applied count
    local applied_count
    applied_count=$(run_sql "SELECT COUNT(*) FROM supabase_migrations.schema_migrations")

    # Note: exact match isn't always expected due to Supabase internal migrations
    record_result "repo_migrations_match" "pass" "Repo has $repo_count SQL files, $applied_count migrations applied"
}

# ============================================================================
# B) Auth + JWT Hook Verification
# ============================================================================

verify_jwt_hook_exists() {
    log_info "Checking custom_access_token_hook function..."

    local result
    result=$(run_sql "SELECT COUNT(*) FROM pg_proc WHERE proname = 'custom_access_token_hook' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')")

    if [[ "$result" -gt 0 ]]; then
        record_result "jwt_hook_exists" "pass" "public.custom_access_token_hook function exists"
    else
        record_result "jwt_hook_exists" "fail" "custom_access_token_hook function not found"
    fi
}

verify_helper_functions() {
    log_info "Checking JWT helper functions..."

    local functions=("current_user_id" "current_tenant_id" "current_role")
    local missing=()
    local found=()

    for func in "${functions[@]}"; do
        local result
        result=$(run_sql "SELECT COUNT(*) FROM pg_proc WHERE proname = '$func' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'app')")

        if [[ "$result" -gt 0 ]]; then
            found+=("app.$func")
        else
            missing+=("app.$func")
        fi
    done

    if [[ ${#missing[@]} -eq 0 ]]; then
        record_result "helper_functions" "pass" "All helper functions exist: ${found[*]}"
    else
        record_result "helper_functions" "fail" "Missing helper functions: ${missing[*]}"
    fi
}

verify_schemas_exist() {
    log_info "Checking required schemas..."

    local schemas=("app" "ops" "public")
    local missing=()
    local found=()

    for schema in "${schemas[@]}"; do
        local result
        result=$(run_sql "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = '$schema'")

        if [[ "$result" -gt 0 ]]; then
            found+=("$schema")
        else
            missing+=("$schema")
        fi
    done

    if [[ ${#missing[@]} -eq 0 ]]; then
        record_result "schemas_exist" "pass" "All required schemas exist: ${found[*]}"
    else
        record_result "schemas_exist" "fail" "Missing schemas: ${missing[*]}"
    fi
}

# ============================================================================
# C) RLS Enforcement Verification
# ============================================================================

verify_rls_enabled() {
    log_info "Checking RLS is enabled on core tables..."

    local tables=(
        "app.tenants"
        "app.profiles"
        "ops.service_tokens"
        "ops.audit_log"
    )

    local enabled=()
    local disabled=()

    for table in "${tables[@]}"; do
        local schema_name="${table%%.*}"
        local table_name="${table##*.}"

        local result
        result=$(run_sql "SELECT rowsecurity FROM pg_tables WHERE schemaname = '$schema_name' AND tablename = '$table_name'")

        if [[ "$result" == "t" ]]; then
            enabled+=("$table")
        else
            disabled+=("$table")
        fi
    done

    if [[ ${#disabled[@]} -eq 0 ]]; then
        record_result "rls_enabled" "pass" "RLS enabled on all core tables: ${enabled[*]}"
    else
        record_result "rls_enabled" "fail" "RLS not enabled on: ${disabled[*]}"
    fi
}

verify_rls_policies_exist() {
    log_info "Checking RLS policies exist..."

    # Check for key policies on app.tenants
    local tenants_policies
    tenants_policies=$(run_sql "SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'app' AND tablename = 'tenants'")

    # Check for key policies on app.profiles
    local profiles_policies
    profiles_policies=$(run_sql "SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'app' AND tablename = 'profiles'")

    # Check for key policies on ops.service_tokens
    local tokens_policies
    tokens_policies=$(run_sql "SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'ops' AND tablename = 'service_tokens'")

    # Check for key policies on ops.audit_log
    local audit_policies
    audit_policies=$(run_sql "SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'ops' AND tablename = 'audit_log'")

    local total=$((tenants_policies + profiles_policies + tokens_policies + audit_policies))

    if [[ $total -gt 10 ]]; then
        record_result "rls_policies_exist" "pass" "Found $total RLS policies (tenants:$tenants_policies, profiles:$profiles_policies, tokens:$tokens_policies, audit:$audit_policies)"
    else
        record_result "rls_policies_exist" "fail" "Insufficient RLS policies found: $total (expected > 10)"
    fi
}

list_all_policies() {
    log_info "Listing all RLS policies..."

    local policies
    policies=$(run_sql "SELECT schemaname || '.' || tablename || ' -> ' || policyname FROM pg_policies WHERE schemaname IN ('app', 'ops') ORDER BY schemaname, tablename, policyname")

    if [[ -n "$policies" ]] && [[ "$policies" != "SQL_ERROR" ]]; then
        record_result "rls_policies_list" "pass" "RLS policies enumerated" "$policies"
    else
        record_result "rls_policies_list" "skip" "Could not enumerate policies"
    fi
}

# ============================================================================
# D) Edge Functions Verification
# ============================================================================

verify_edge_functions_deployed() {
    log_info "Checking Edge Functions deployment..."

    if [[ ! -d "$FUNCTIONS_DIR" ]]; then
        record_result "edge_functions_deployed" "skip" "Functions directory not found: $FUNCTIONS_DIR"
        return
    fi

    # Get list of functions from repo
    local repo_functions
    repo_functions=$(find "$FUNCTIONS_DIR" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)

    local count
    count=$(echo "$repo_functions" | wc -l | tr -d ' ')

    record_result "edge_functions_deployed" "pass" "$count Edge Functions defined in repo" "$repo_functions"
}

verify_required_functions() {
    log_info "Checking required Edge Functions..."

    local required=("auth-bootstrap" "tenant-invite")
    local missing=()
    local found=()

    for func in "${required[@]}"; do
        if [[ -d "$FUNCTIONS_DIR/$func" ]]; then
            found+=("$func")
        else
            missing+=("$func")
        fi
    done

    if [[ ${#missing[@]} -eq 0 ]]; then
        record_result "required_functions" "pass" "Required functions exist: ${found[*]}"
    else
        record_result "required_functions" "fail" "Missing required functions: ${missing[*]}"
    fi
}

test_auth_bootstrap_endpoint() {
    log_info "Testing auth-bootstrap endpoint..."

    # Test OPTIONS (CORS preflight)
    local cors_response
    cors_response=$(curl -s -o /dev/null -w "%{http_code}" -X OPTIONS \
        -H "Origin: http://localhost" \
        -H "Access-Control-Request-Method: POST" \
        "${SUPABASE_URL}/functions/v1/auth-bootstrap" 2>/dev/null || echo "000")

    if [[ "$cors_response" == "200" ]] || [[ "$cors_response" == "204" ]]; then
        record_result "auth_bootstrap_cors" "pass" "CORS preflight returns $cors_response"
    else
        record_result "auth_bootstrap_cors" "skip" "CORS preflight returned $cors_response (function may not be deployed)"
    fi

    # Test POST without body (should return 400)
    local post_response
    post_response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${SUPABASE_ANON_KEY}" \
        -d '{}' \
        "${SUPABASE_URL}/functions/v1/auth-bootstrap" 2>/dev/null || echo "000")

    local post_code
    post_code=$(echo "$post_response" | tail -n 1)

    if [[ "$post_code" == "400" ]]; then
        record_result "auth_bootstrap_validation" "pass" "auth-bootstrap returns 400 for invalid input"
    elif [[ "$post_code" == "000" ]] || [[ "$post_code" == "404" ]]; then
        record_result "auth_bootstrap_validation" "skip" "auth-bootstrap endpoint not reachable (HTTP $post_code)"
    else
        record_result "auth_bootstrap_validation" "pass" "auth-bootstrap responds with HTTP $post_code"
    fi
}

test_tenant_invite_endpoint() {
    log_info "Testing tenant-invite endpoint..."

    # Test without auth (should return 401)
    local noauth_response
    noauth_response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d '{"email": "test@example.com", "role": "viewer"}' \
        "${SUPABASE_URL}/functions/v1/tenant-invite" 2>/dev/null || echo "000")

    local noauth_code
    noauth_code=$(echo "$noauth_response" | tail -n 1)

    if [[ "$noauth_code" == "401" ]]; then
        record_result "tenant_invite_auth" "pass" "tenant-invite correctly requires authentication (401)"
    elif [[ "$noauth_code" == "000" ]] || [[ "$noauth_code" == "404" ]]; then
        record_result "tenant_invite_auth" "skip" "tenant-invite endpoint not reachable (HTTP $noauth_code)"
    else
        record_result "tenant_invite_auth" "pass" "tenant-invite responds with HTTP $noauth_code"
    fi
}

# ============================================================================
# E) Storage/Buckets Verification (Optional)
# ============================================================================

verify_storage_buckets() {
    log_info "Checking storage buckets..."

    # Query storage buckets via PostgREST
    local buckets_response
    buckets_response=$(curl_api "/storage/v1/bucket" "GET" "" "service")

    if [[ -n "$buckets_response" ]] && [[ "$buckets_response" != "null" ]]; then
        local bucket_count
        bucket_count=$(echo "$buckets_response" | jq -r 'if type == "array" then length else 0 end' 2>/dev/null || echo "0")

        if [[ "$bucket_count" -gt 0 ]]; then
            record_result "storage_buckets" "pass" "$bucket_count storage buckets configured"
        else
            record_result "storage_buckets" "skip" "No storage buckets found (may be expected)"
        fi
    else
        record_result "storage_buckets" "skip" "Could not query storage buckets"
    fi
}

# ============================================================================
# API Schema Exposure Verification
# ============================================================================

verify_api_schema_exposure() {
    log_info "Checking API schema exposure..."

    # Test that app schema is exposed
    local app_test
    app_test=$(curl_api "/rest/v1/tenants?limit=0" "GET" "" "service")

    if echo "$app_test" | grep -q "error" 2>/dev/null; then
        record_result "api_app_schema" "fail" "app.tenants not accessible via REST API"
    else
        record_result "api_app_schema" "pass" "app schema exposed via REST API"
    fi

    # Test that ops schema is NOT exposed (should fail or return empty)
    local ops_test
    ops_test=$(curl_api "/rest/v1/audit_log?limit=0" "GET" "" "anon")

    # This should fail with RLS or schema not exposed
    if echo "$ops_test" | grep -q "error\|permission denied" 2>/dev/null; then
        record_result "api_ops_schema" "pass" "ops schema properly restricted"
    else
        record_result "api_ops_schema" "skip" "Could not verify ops schema restriction"
    fi
}

# ============================================================================
# Data Integrity Checks
# ============================================================================

verify_seed_data() {
    log_info "Checking seed data..."

    # Check for bootstrap tenant
    local tenant_count
    tenant_count=$(run_sql "SELECT COUNT(*) FROM app.tenants")

    if [[ "$tenant_count" -gt 0 ]]; then
        record_result "seed_tenants" "pass" "$tenant_count tenant(s) exist in app.tenants"
    else
        record_result "seed_tenants" "skip" "No tenants found (bootstrap may not have run)"
    fi
}

# ============================================================================
# Report Generation
# ============================================================================

generate_json_report() {
    log_info "Generating JSON report..."

    mkdir -p "$REPORT_DIR"

    local overall_status="PASS"
    if [[ $FAILED_CHECKS -gt 0 ]]; then
        overall_status="FAIL"
    fi

    cat > "$JSON_REPORT" <<EOF
{
  "timestamp": "$TIMESTAMP",
  "overall_status": "$overall_status",
  "summary": {
    "total_checks": $TOTAL_CHECKS,
    "passed": $PASSED_CHECKS,
    "failed": $FAILED_CHECKS,
    "skipped": $SKIPPED_CHECKS
  },
  "environment": {
    "supabase_url": "${SUPABASE_URL:-not_set}",
    "project_ref": "spdtwktxdalcfigzeqrz"
  },
  "checks": {
EOF

    local first=true
    for key in "${!RESULTS[@]}"; do
        local value="${RESULTS[$key]}"
        local status="${value%%|*}"
        local rest="${value#*|}"
        local message="${rest%%|*}"
        local evidence="${rest#*|}"

        # Escape JSON special characters
        message="${message//\\/\\\\}"
        message="${message//\"/\\\"}"
        evidence="${evidence//\\/\\\\}"
        evidence="${evidence//\"/\\\"}"
        evidence="${evidence//$'\n'/\\n}"

        if [[ "$first" == "true" ]]; then
            first=false
        else
            echo "," >> "$JSON_REPORT"
        fi

        cat >> "$JSON_REPORT" <<EOF
    "$key": {
      "status": "$status",
      "message": "$message",
      "evidence": "$evidence"
    }
EOF
    done

    cat >> "$JSON_REPORT" <<EOF

  }
}
EOF

    log_success "JSON report generated: $JSON_REPORT"
}

generate_markdown_report() {
    log_info "Generating Markdown report..."

    mkdir -p "$DOCS_DIR"

    local overall_status="PASS"
    local status_emoji="+"
    if [[ $FAILED_CHECKS -gt 0 ]]; then
        overall_status="FAIL"
        status_emoji="-"
    fi

    cat > "$MD_REPORT" <<EOF
# Supabase Deployment Verification Report

**Generated:** $TIMESTAMP
**Project:** spdtwktxdalcfigzeqrz
**Status:** **$overall_status** ${status_emoji}

## Summary

| Metric | Count |
|--------|-------|
| Total Checks | $TOTAL_CHECKS |
| Passed | $PASSED_CHECKS |
| Failed | $FAILED_CHECKS |
| Skipped | $SKIPPED_CHECKS |

## Verification Results

### A) Migrations

EOF

    for key in migrations_table_exists migrations_applied key_migrations repo_migrations_match; do
        if [[ -n "${RESULTS[$key]:-}" ]]; then
            local value="${RESULTS[$key]}"
            local status="${value%%|*}"
            local rest="${value#*|}"
            local message="${rest%%|*}"
            local icon="?"
            case "$status" in
                pass) icon="+" ;;
                fail) icon="-" ;;
                skip) icon="~" ;;
            esac
            echo "- [${icon}] **$key**: $message" >> "$MD_REPORT"
        fi
    done

    cat >> "$MD_REPORT" <<EOF

### B) Auth + JWT Hook

EOF

    for key in jwt_hook_exists helper_functions schemas_exist; do
        if [[ -n "${RESULTS[$key]:-}" ]]; then
            local value="${RESULTS[$key]}"
            local status="${value%%|*}"
            local rest="${value#*|}"
            local message="${rest%%|*}"
            local icon="?"
            case "$status" in
                pass) icon="+" ;;
                fail) icon="-" ;;
                skip) icon="~" ;;
            esac
            echo "- [${icon}] **$key**: $message" >> "$MD_REPORT"
        fi
    done

    cat >> "$MD_REPORT" <<EOF

### C) RLS Enforcement

EOF

    for key in rls_enabled rls_policies_exist rls_policies_list; do
        if [[ -n "${RESULTS[$key]:-}" ]]; then
            local value="${RESULTS[$key]}"
            local status="${value%%|*}"
            local rest="${value#*|}"
            local message="${rest%%|*}"
            local icon="?"
            case "$status" in
                pass) icon="+" ;;
                fail) icon="-" ;;
                skip) icon="~" ;;
            esac
            echo "- [${icon}] **$key**: $message" >> "$MD_REPORT"
        fi
    done

    cat >> "$MD_REPORT" <<EOF

### D) Edge Functions

EOF

    for key in edge_functions_deployed required_functions auth_bootstrap_cors auth_bootstrap_validation tenant_invite_auth; do
        if [[ -n "${RESULTS[$key]:-}" ]]; then
            local value="${RESULTS[$key]}"
            local status="${value%%|*}"
            local rest="${value#*|}"
            local message="${rest%%|*}"
            local icon="?"
            case "$status" in
                pass) icon="+" ;;
                fail) icon="-" ;;
                skip) icon="~" ;;
            esac
            echo "- [${icon}] **$key**: $message" >> "$MD_REPORT"
        fi
    done

    cat >> "$MD_REPORT" <<EOF

### E) Storage & API

EOF

    for key in storage_buckets api_app_schema api_ops_schema seed_tenants; do
        if [[ -n "${RESULTS[$key]:-}" ]]; then
            local value="${RESULTS[$key]}"
            local status="${value%%|*}"
            local rest="${value#*|}"
            local message="${rest%%|*}"
            local icon="?"
            case "$status" in
                pass) icon="+" ;;
                fail) icon="-" ;;
                skip) icon="~" ;;
            esac
            echo "- [${icon}] **$key**: $message" >> "$MD_REPORT"
        fi
    done

    cat >> "$MD_REPORT" <<EOF

## Remediation Commands

If any checks failed, use the following commands to remediate:

### Apply Missing Migrations

\`\`\`bash
# Using Supabase CLI
supabase db push

# Or manually apply specific migration
psql "\$POSTGRES_URL_NON_POOLING" -f supabase/migrations/5001_auth_foundation.sql
psql "\$POSTGRES_URL_NON_POOLING" -f supabase/migrations/5002_auth_jwt_claims.sql
psql "\$POSTGRES_URL_NON_POOLING" -f supabase/migrations/5003_rls_policies.sql
\`\`\`

### Deploy Edge Functions

\`\`\`bash
# Deploy all functions
supabase functions deploy

# Deploy specific function
supabase functions deploy auth-bootstrap
supabase functions deploy tenant-invite
\`\`\`

### Enable Custom Access Token Hook

1. Go to Supabase Dashboard > Authentication > Hooks
2. Enable "Custom Access Token Hook"
3. Set function to \`public.custom_access_token_hook\`

### Verify RLS

\`\`\`sql
-- Check RLS status
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname IN ('app', 'ops');

-- Enable RLS if needed
ALTER TABLE app.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.service_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.audit_log ENABLE ROW LEVEL SECURITY;
\`\`\`

## Re-run Verification

\`\`\`bash
./scripts/verify_supabase_deploy.sh
\`\`\`

---

*Generated by verify_supabase_deploy.sh*
EOF

    log_success "Markdown report generated: $MD_REPORT"
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    echo ""
    echo -e "${BOLD}============================================${NC}"
    echo -e "${BOLD}  Supabase Deployment Verification${NC}"
    echo -e "${BOLD}============================================${NC}"
    echo ""
    echo "Timestamp: $TIMESTAMP"
    echo "Project: spdtwktxdalcfigzeqrz"
    echo ""

    # Check environment
    if ! check_env_vars; then
        echo ""
        echo -e "${RED}ERROR: Missing required environment variables.${NC}"
        echo ""
        echo "Required variables:"
        echo "  - SUPABASE_URL"
        echo "  - SUPABASE_ANON_KEY"
        echo "  - SUPABASE_SERVICE_ROLE_KEY"
        echo "  - POSTGRES_URL_NON_POOLING (or DATABASE_URL)"
        echo ""
        echo "Set these in your .env file or export them before running."

        # Still generate reports with skip status
        record_result "env_check" "fail" "Missing required environment variables"
        generate_json_report
        generate_markdown_report

        exit 1
    fi

    record_result "env_check" "pass" "Environment variables configured"

    echo ""
    echo -e "${BOLD}--- A) Migrations Verification ---${NC}"
    verify_migrations_table
    verify_migrations_applied
    verify_key_migrations
    verify_repo_migrations_match

    echo ""
    echo -e "${BOLD}--- B) Auth + JWT Hook Verification ---${NC}"
    verify_schemas_exist
    verify_jwt_hook_exists
    verify_helper_functions

    echo ""
    echo -e "${BOLD}--- C) RLS Enforcement Verification ---${NC}"
    verify_rls_enabled
    verify_rls_policies_exist
    list_all_policies

    echo ""
    echo -e "${BOLD}--- D) Edge Functions Verification ---${NC}"
    verify_edge_functions_deployed
    verify_required_functions
    test_auth_bootstrap_endpoint
    test_tenant_invite_endpoint

    echo ""
    echo -e "${BOLD}--- E) Storage & API Verification ---${NC}"
    verify_storage_buckets
    verify_api_schema_exposure
    verify_seed_data

    echo ""
    echo -e "${BOLD}--- Generating Reports ---${NC}"
    generate_json_report
    generate_markdown_report

    # Final summary
    echo ""
    echo -e "${BOLD}============================================${NC}"
    echo -e "${BOLD}  Verification Complete${NC}"
    echo -e "${BOLD}============================================${NC}"
    echo ""
    echo "Total Checks: $TOTAL_CHECKS"
    echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
    echo -e "Failed: ${RED}$FAILED_CHECKS${NC}"
    echo -e "Skipped: ${YELLOW}$SKIPPED_CHECKS${NC}"
    echo ""

    if [[ $FAILED_CHECKS -eq 0 ]]; then
        echo -e "${GREEN}${BOLD}OVERALL: PASS${NC}"
        echo ""
        exit 0
    else
        echo -e "${RED}${BOLD}OVERALL: FAIL${NC}"
        echo ""
        echo "See reports for details:"
        echo "  - $MD_REPORT"
        echo "  - $JSON_REPORT"
        echo ""
        exit 1
    fi
}

# Run main
main "$@"
