#!/usr/bin/env bash
# =============================================================================
# test_mcp_jobs.sh - Test MCP Jobs Queue System
# =============================================================================
# Usage: ./scripts/test_mcp_jobs.sh [enqueue|status|events|reap|all]
# =============================================================================

set -euo pipefail

# Load environment
if [[ -f .env.local ]]; then
    source .env.local
elif [[ -f .env ]]; then
    source .env
fi

# Required environment variables
: "${SUPABASE_URL:?SUPABASE_URL is required}"
: "${SUPABASE_SERVICE_ROLE_KEY:?SUPABASE_SERVICE_ROLE_KEY is required}"

# Construct database URL for psql
POSTGRES_URL="${SUPABASE_URL/https:\/\//postgres://postgres:${SUPABASE_SERVICE_ROLE_KEY}@}"
POSTGRES_URL="${POSTGRES_URL}.supabase.co/postgres"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# =============================================================================
# Test Functions
# =============================================================================

test_enqueue_job() {
    print_header "Enqueuing Test Job"

    local JOB_ID
    JOB_ID=$(curl -s -X POST "${SUPABASE_URL}/rest/v1/rpc/enqueue_job" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Content-Type: application/json" \
        -H "Prefer: return=representation" \
        -d '{
            "p_source": "test",
            "p_job_type": "notify",
            "p_payload": {"message": "Test job from test_mcp_jobs.sh", "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"},
            "p_priority": 5
        }' | jq -r '.')

    if [[ "$JOB_ID" != "null" && -n "$JOB_ID" ]]; then
        print_success "Job enqueued: $JOB_ID"
        echo "$JOB_ID"
    else
        print_error "Failed to enqueue job"
        return 1
    fi
}

test_queue_status() {
    print_header "Queue Status"

    echo -e "${YELLOW}Jobs by Status:${NC}"
    curl -s -X GET "${SUPABASE_URL}/rest/v1/rpc/mcp_jobs_status" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Content-Type: application/json" 2>/dev/null | jq '.' || {

        # Fallback: direct table query
        curl -s -X GET "${SUPABASE_URL}/rest/v1/mcp_jobs.jobs?select=status&order=status" \
            -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
            -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" | jq 'group_by(.status) | map({status: .[0].status, count: length})'
    }

    echo -e "\n${YELLOW}Recent Jobs (last 10):${NC}"
    curl -s -X GET "${SUPABASE_URL}/rest/v1/mcp_jobs.jobs?select=id,source,job_type,status,created_at&order=created_at.desc&limit=10" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" | jq '.[] | {id: .id[0:8], source, job_type, status, created: .created_at[11:19]}'
}

test_job_events() {
    print_header "Recent Job Events"

    local JOB_ID="${1:-}"

    if [[ -n "$JOB_ID" ]]; then
        echo -e "${YELLOW}Events for job $JOB_ID:${NC}"
        curl -s -X GET "${SUPABASE_URL}/rest/v1/mcp_jobs.job_events?job_id=eq.${JOB_ID}&order=created_at.asc" \
            -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
            -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" | jq '.[] | {event_type, message, created: .created_at[11:19]}'
    else
        echo -e "${YELLOW}Last 20 events:${NC}"
        curl -s -X GET "${SUPABASE_URL}/rest/v1/mcp_jobs.job_events?select=job_id,event_type,message,created_at&order=created_at.desc&limit=20" \
            -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
            -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" | jq '.[] | {job: .job_id[0:8], event_type, message}'
    fi
}

test_reap_stuck_jobs() {
    print_header "Reaping Stuck Jobs"

    local RESULT
    RESULT=$(curl -s -X POST "${SUPABASE_URL}/rest/v1/rpc/reap_stuck_jobs" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Content-Type: application/json" \
        -d '{"p_default_timeout_minutes": 5}')

    local COUNT
    COUNT=$(echo "$RESULT" | jq 'length')

    if [[ "$COUNT" -gt 0 ]]; then
        print_info "Reaped $COUNT stuck jobs:"
        echo "$RESULT" | jq '.[] | {job_id: .job_id[0:8], action_taken, retry: "\(.retry_count)/\(.max_retries)"}'
    else
        print_success "No stuck jobs found"
    fi
}

test_run_executor_health() {
    print_header "Run Executor Health Check"

    local CRON_SECRET="${CRON_SECRET:-}"

    if [[ -z "$CRON_SECRET" ]]; then
        print_info "CRON_SECRET not set - using service role auth"
    fi

    local RESPONSE
    RESPONSE=$(curl -s -X GET "${SUPABASE_URL}/functions/v1/run-executor/health" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Content-Type: application/json" \
        ${CRON_SECRET:+-H "X-CRON-SECRET: $CRON_SECRET"})

    if echo "$RESPONSE" | jq -e '.ok == true' > /dev/null 2>&1; then
        print_success "Run executor is healthy"
        echo "$RESPONSE" | jq '.'
    else
        print_error "Run executor health check failed"
        echo "$RESPONSE"
        return 1
    fi
}

test_trigger_executor() {
    print_header "Triggering Run Executor"

    local CRON_SECRET="${CRON_SECRET:-}"

    local RESPONSE
    RESPONSE=$(curl -s -X POST "${SUPABASE_URL}/functions/v1/run-executor" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Content-Type: application/json" \
        ${CRON_SECRET:+-H "X-CRON-SECRET: $CRON_SECRET"} \
        -d '{"max_jobs": 5, "timeout_minutes": 5}')

    if echo "$RESPONSE" | jq -e '.ok == true' > /dev/null 2>&1; then
        print_success "Executor ran successfully"
        echo "$RESPONSE" | jq '.'
    else
        print_error "Executor failed"
        echo "$RESPONSE"
        return 1
    fi
}

test_dlq_status() {
    print_header "Dead Letter Queue Status"

    local DLQ
    DLQ=$(curl -s -X GET "${SUPABASE_URL}/rest/v1/mcp_jobs.dead_letter_queue?order=failed_at.desc&limit=10" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}")

    local COUNT
    COUNT=$(echo "$DLQ" | jq 'length')

    if [[ "$COUNT" -gt 0 ]]; then
        print_info "$COUNT jobs in DLQ:"
        echo "$DLQ" | jq '.[] | {job_id: .job_id[0:8], failure_reason, failed_at: .failed_at[0:19]}'
    else
        print_success "Dead letter queue is empty"
    fi
}

run_all_tests() {
    print_header "Running All MCP Jobs Tests"

    # 1. Check queue status
    test_queue_status

    # 2. Enqueue a test job
    local JOB_ID
    JOB_ID=$(test_enqueue_job) || true

    # 3. Check health
    test_run_executor_health || true

    # 4. Trigger executor to process the test job
    test_trigger_executor || true

    # 5. Check events for the test job
    if [[ -n "${JOB_ID:-}" ]]; then
        sleep 2
        test_job_events "$JOB_ID"
    fi

    # 6. Check for stuck jobs
    test_reap_stuck_jobs

    # 7. Check DLQ
    test_dlq_status

    print_header "All Tests Complete"
}

# =============================================================================
# Main
# =============================================================================

case "${1:-all}" in
    enqueue)
        test_enqueue_job
        ;;
    status)
        test_queue_status
        ;;
    events)
        test_job_events "${2:-}"
        ;;
    reap)
        test_reap_stuck_jobs
        ;;
    health)
        test_run_executor_health
        ;;
    trigger)
        test_trigger_executor
        ;;
    dlq)
        test_dlq_status
        ;;
    all)
        run_all_tests
        ;;
    *)
        echo "Usage: $0 [enqueue|status|events [job_id]|reap|health|trigger|dlq|all]"
        exit 1
        ;;
esac
