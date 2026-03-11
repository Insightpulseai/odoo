#!/usr/bin/env bash
set -euo pipefail

# E2E Test Suite for OdooOps Sh Integration
# Tests full workflow lifecycle with ops.runs table

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/_common.sh"

# Test configuration
TEST_PROJECT_ID="test-project-$(date +%s)"
TEST_ENV_ID="dev"
TEST_GIT_REF="main"
TEST_COMMIT_SHA="abc123def456789012345678901234567890abcd"
PASSED=0
FAILED=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_test() {
  echo -e "${YELLOW}[TEST]${NC} $1"
}

log_pass() {
  echo -e "${GREEN}[PASS]${NC} $1"
  ((PASSED++))
}

log_fail() {
  echo -e "${RED}[FAIL]${NC} $1"
  ((FAILED++))
}

cleanup() {
  log_test "Cleaning up test data..."

  # Delete test project and all related runs
  curl -fsS -X DELETE \
    "${SUPABASE_URL}/rest/v1/ops.projects?project_id=eq.${TEST_PROJECT_ID}" \
    -H "apikey: ${SUPABASE_ANON_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" >/dev/null 2>&1 || true

  echo "Cleanup complete"
}

trap cleanup EXIT

# ============================================================================
# Test 1: Create Test Project
# ============================================================================
log_test "Test 1: Create test project in ops.projects"

project_payload=$(cat <<JSON
{
  "project_id": "${TEST_PROJECT_ID}",
  "name": "Test Project",
  "repo_slug": "test-org/test-repo",
  "odoo_version": "19.0",
  "metadata": {"test": true}
}
JSON
)

resp=$(curl -fsS -X POST \
  "${SUPABASE_URL}/rest/v1/ops.projects" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "${project_payload}")

created_project=$(echo "$resp" | python -c "import json,sys; d=json.load(sys.stdin); print(d[0]['project_id'] if isinstance(d, list) else d.get('project_id',''))")

if [[ "$created_project" == "$TEST_PROJECT_ID" ]]; then
  log_pass "Project created successfully"
else
  log_fail "Failed to create project: $resp"
  exit 1
fi

# ============================================================================
# Test 2: Create Test Environment
# ============================================================================
log_test "Test 2: Create test environment in ops.environments"

env_payload=$(cat <<JSON
{
  "env_id": "${TEST_ENV_ID}",
  "project_id": "${TEST_PROJECT_ID}",
  "env_type": "dev",
  "branch_pattern": "main",
  "db_name": "test_db",
  "config": {"test": true}
}
JSON
)

resp=$(curl -fsS -X POST \
  "${SUPABASE_URL}/rest/v1/ops.environments" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "${env_payload}")

created_env=$(echo "$resp" | python -c "import json,sys; d=json.load(sys.stdin); print(d[0]['env_id'] if isinstance(d, list) else d.get('env_id',''))")

if [[ "$created_env" == "$TEST_ENV_ID" ]]; then
  log_pass "Environment created successfully"
else
  log_fail "Failed to create environment: $resp"
  exit 1
fi

# ============================================================================
# Test 3: Create Queued Run (env_create.sh)
# ============================================================================
log_test "Test 3: Create queued run using env_create.sh"

run_id=$(bash "${SCRIPT_DIR}/env_create.sh" \
  "$TEST_PROJECT_ID" \
  "build" \
  "$TEST_GIT_REF" \
  "$TEST_COMMIT_SHA" \
  "$TEST_ENV_ID" 2>&1)

if [[ "$run_id" =~ ^run- ]]; then
  log_pass "Run created with ID: $run_id"
else
  log_fail "Failed to create run: $run_id"
  exit 1
fi

# ============================================================================
# Test 4: Verify Run is Queued
# ============================================================================
log_test "Test 4: Verify run status is 'queued'"

resp=$(curl -fsS -G \
  "${SUPABASE_URL}/rest/v1/ops.runs" \
  --data-urlencode "run_id=eq.${run_id}" \
  --data-urlencode "select=status" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}")

status=$(echo "$resp" | python -c "import json,sys; d=json.load(sys.stdin); print(d[0]['status'] if isinstance(d, list) and len(d) > 0 else '')")

if [[ "$status" == "queued" ]]; then
  log_pass "Run status is 'queued'"
else
  log_fail "Expected 'queued', got '$status'"
fi

# ============================================================================
# Test 5: Simulate Worker Claiming Run
# ============================================================================
log_test "Test 5: Simulate worker claiming run"

claim_payload='{"status":"claimed","claimed_by":"test-worker-001"}'

resp=$(curl -fsS -X PATCH \
  "${SUPABASE_URL}/rest/v1/ops.runs?run_id=eq.${run_id}" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "${claim_payload}")

claimed_status=$(echo "$resp" | python -c "import json,sys; d=json.load(sys.stdin); print(d[0]['status'] if isinstance(d, list) and len(d) > 0 else '')")

if [[ "$claimed_status" == "claimed" ]]; then
  log_pass "Run claimed by worker"
else
  log_fail "Failed to claim run: $resp"
fi

# ============================================================================
# Test 6: Add Log Events
# ============================================================================
log_test "Test 6: Add log events to ops.run_events"

for level in "info" "debug" "warn"; do
  log_payload=$(cat <<JSON
{
  "run_id": "${run_id}",
  "level": "${level}",
  "message": "Test ${level} message",
  "payload": {"step": "test", "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
}
JSON
)

  curl -fsS -X POST \
    "${SUPABASE_URL}/rest/v1/ops.run_events" \
    -H "apikey: ${SUPABASE_ANON_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" \
    -d "${log_payload}" >/dev/null
done

# Verify logs were created
resp=$(curl -fsS -G \
  "${SUPABASE_URL}/rest/v1/ops.run_events" \
  --data-urlencode "run_id=eq.${run_id}" \
  --data-urlencode "select=count" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Prefer: count=exact")

log_count=$(echo "$resp" | grep -o 'content-range: [0-9]*-[0-9]*/\([0-9]*\)' | grep -o '[0-9]*$' || echo "0")

if [[ "$log_count" -ge 3 ]]; then
  log_pass "Log events created ($log_count total)"
else
  log_fail "Expected 3+ log events, found $log_count"
fi

# ============================================================================
# Test 7: Mark Run as Running
# ============================================================================
log_test "Test 7: Mark run as running"

running_payload='{"status":"running","started_at":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"}'

curl -fsS -X PATCH \
  "${SUPABASE_URL}/rest/v1/ops.runs?run_id=eq.${run_id}" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -d "${running_payload}" >/dev/null

resp=$(curl -fsS -G \
  "${SUPABASE_URL}/rest/v1/ops.runs" \
  --data-urlencode "run_id=eq.${run_id}" \
  --data-urlencode "select=status" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}")

status=$(echo "$resp" | python -c "import json,sys; d=json.load(sys.stdin); print(d[0]['status'] if isinstance(d, list) and len(d) > 0 else '')")

if [[ "$status" == "running" ]]; then
  log_pass "Run marked as running"
else
  log_fail "Expected 'running', got '$status'"
fi

# ============================================================================
# Test 8: Add Artifact
# ============================================================================
log_test "Test 8: Add artifact to ops.artifacts"

artifact_payload=$(cat <<JSON
{
  "run_id": "${run_id}",
  "artifact_type": "image",
  "storage_path": "ghcr.io/test/image:latest",
  "digest": "sha256:1234567890abcdef",
  "size_bytes": 123456789,
  "metadata": {"test": true}
}
JSON
)

resp=$(curl -fsS -X POST \
  "${SUPABASE_URL}/rest/v1/ops.artifacts" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "${artifact_payload}")

artifact_id=$(echo "$resp" | python -c "import json,sys; d=json.load(sys.stdin); print(d[0].get('artifact_id','') if isinstance(d, list) else d.get('artifact_id',''))")

if [[ -n "$artifact_id" ]]; then
  log_pass "Artifact created: $artifact_id"
else
  log_fail "Failed to create artifact: $resp"
fi

# ============================================================================
# Test 9: Mark Run as Success
# ============================================================================
log_test "Test 9: Mark run as success"

success_payload='{"status":"success","finished_at":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"}'

curl -fsS -X PATCH \
  "${SUPABASE_URL}/rest/v1/ops.runs?run_id=eq.${run_id}" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -d "${success_payload}" >/dev/null

resp=$(curl -fsS -G \
  "${SUPABASE_URL}/rest/v1/ops.runs" \
  --data-urlencode "run_id=eq.${run_id}" \
  --data-urlencode "select=status" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}")

status=$(echo "$resp" | python -c "import json,sys; d=json.load(sys.stdin); print(d[0]['status'] if isinstance(d, list) and len(d) > 0 else '')")

if [[ "$status" == "success" ]]; then
  log_pass "Run marked as success"
else
  log_fail "Expected 'success', got '$status'"
fi

# ============================================================================
# Test 10: Wait Ready (Should Return Immediately)
# ============================================================================
log_test "Test 10: Test env_wait_ready.sh with completed run"

# This should return immediately since run is already successful
timeout 10 bash "${SCRIPT_DIR}/env_wait_ready.sh" "$run_id" 30 1 >/dev/null 2>&1
wait_exit_code=$?

if [[ $wait_exit_code -eq 0 ]]; then
  log_pass "env_wait_ready.sh returned successfully"
else
  log_fail "env_wait_ready.sh failed with exit code $wait_exit_code"
fi

# ============================================================================
# Test 11: Test Cancellation (env_destroy.sh)
# ============================================================================
log_test "Test 11: Create another run and cancel it"

run_id_2=$(bash "${SCRIPT_DIR}/env_create.sh" \
  "$TEST_PROJECT_ID" \
  "test" \
  "feature/test" \
  "def456abc123" \
  "$TEST_ENV_ID" 2>&1)

if [[ ! "$run_id_2" =~ ^run- ]]; then
  log_fail "Failed to create second run: $run_id_2"
else
  # Cancel it
  result=$(bash "${SCRIPT_DIR}/env_destroy.sh" "$run_id_2" 2>&1)

  if [[ "$result" =~ ^cancelled: ]]; then
    log_pass "Run cancelled successfully: $run_id_2"

    # Verify status is cancelled
    resp=$(curl -fsS -G \
      "${SUPABASE_URL}/rest/v1/ops.runs" \
      --data-urlencode "run_id=eq.${run_id_2}" \
      --data-urlencode "select=status" \
      -H "apikey: ${SUPABASE_ANON_KEY}" \
      -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}")

    status=$(echo "$resp" | python -c "import json,sys; d=json.load(sys.stdin); print(d[0]['status'] if isinstance(d, list) and len(d) > 0 else '')")

    if [[ "$status" == "cancelled" ]]; then
      log_pass "Run status confirmed as cancelled"
    else
      log_fail "Expected 'cancelled', got '$status'"
    fi
  else
    log_fail "Failed to cancel run: $result"
  fi
fi

# ============================================================================
# Test 12: Test Retry Logic (Failed Run)
# ============================================================================
log_test "Test 12: Create run, mark as failed, verify wait_ready detects it"

run_id_3=$(bash "${SCRIPT_DIR}/env_create.sh" \
  "$TEST_PROJECT_ID" \
  "build" \
  "bugfix/critical" \
  "789abc123def" \
  "$TEST_ENV_ID" 2>&1)

if [[ ! "$run_id_3" =~ ^run- ]]; then
  log_fail "Failed to create third run: $run_id_3"
else
  # Mark as failed
  failed_payload='{"status":"failed","finished_at":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"}'

  curl -fsS -X PATCH \
    "${SUPABASE_URL}/rest/v1/ops.runs?run_id=eq.${run_id_3}" \
    -H "apikey: ${SUPABASE_ANON_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" \
    -d "${failed_payload}" >/dev/null

  # env_wait_ready should exit with error for failed run
  timeout 10 bash "${SCRIPT_DIR}/env_wait_ready.sh" "$run_id_3" 30 1 >/dev/null 2>&1
  wait_exit_code=$?

  if [[ $wait_exit_code -ne 0 ]]; then
    log_pass "env_wait_ready.sh correctly detected failed run"
  else
    log_fail "env_wait_ready.sh should have failed for failed run"
  fi
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "=========================================="
echo "E2E Test Suite Summary"
echo "=========================================="
echo -e "${GREEN}PASSED:${NC} $PASSED"
echo -e "${RED}FAILED:${NC} $FAILED"
echo "=========================================="

if [[ $FAILED -eq 0 ]]; then
  echo -e "${GREEN}All tests passed!${NC}"
  exit 0
else
  echo -e "${RED}Some tests failed!${NC}"
  exit 1
fi
