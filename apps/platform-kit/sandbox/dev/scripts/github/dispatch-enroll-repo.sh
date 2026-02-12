#!/usr/bin/env bash
# =============================================================================
# dispatch-enroll-repo.sh - Trigger Repo Enrollment Workflow
# =============================================================================
# Called by the pulser-hub webhook handler (n8n) when a new repository is
# created or needs enrollment in the governance framework.
#
# USAGE:
#   ./scripts/github/dispatch-enroll-repo.sh <repo_full_name>
#
# EXAMPLE:
#   ./scripts/github/dispatch-enroll-repo.sh Insightpulseai-net/new-repo
#
# REQUIRED ENVIRONMENT:
#   GITHUB_TOKEN - GitHub App installation token or PAT with workflow scope
#
# OPTIONAL ENVIRONMENT:
#   GITHUB_ORG        - Organization (default: Insightpulseai-net)
#   GOVERNANCE_REPO   - Repo containing governance workflows (default: odoo-kit)
#   WORKFLOW_FILE     - Workflow filename (default: governance-enroll-repo.yml)
# =============================================================================

set -euo pipefail

# Configuration
GITHUB_ORG="${GITHUB_ORG:-Insightpulseai-net}"
GOVERNANCE_REPO="${GOVERNANCE_REPO:-odoo-kit}"
WORKFLOW_FILE="${WORKFLOW_FILE:-governance-enroll-repo.yml}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------

if [[ -z "${1:-}" ]]; then
    log_error "Missing required argument: repo_full_name"
    echo "Usage: $0 <repo_full_name>"
    echo "Example: $0 Insightpulseai-net/new-repo"
    exit 1
fi

REPO_FULL_NAME="$1"

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
    log_error "GITHUB_TOKEN environment variable is required"
    exit 1
fi

# Validate repo name format
if [[ ! "${REPO_FULL_NAME}" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
    log_error "Invalid repo_full_name format: ${REPO_FULL_NAME}"
    echo "Expected format: owner/repo (e.g., Insightpulseai-net/odoo-ce)"
    exit 1
fi

# -----------------------------------------------------------------------------
# Check if workflow exists
# -----------------------------------------------------------------------------

log_info "Checking workflow availability..."

WORKFLOW_CHECK=$(curl -sS -w "%{http_code}" -o /tmp/workflow_check.json \
    -H "Authorization: Bearer ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/${GITHUB_ORG}/${GOVERNANCE_REPO}/actions/workflows/${WORKFLOW_FILE}")

if [[ "${WORKFLOW_CHECK}" != "200" ]]; then
    log_error "Workflow not found: ${WORKFLOW_FILE}"
    log_error "HTTP status: ${WORKFLOW_CHECK}"
    cat /tmp/workflow_check.json
    exit 1
fi

WORKFLOW_ID=$(jq -r '.id' /tmp/workflow_check.json)
log_info "Found workflow ID: ${WORKFLOW_ID}"

# -----------------------------------------------------------------------------
# Dispatch workflow
# -----------------------------------------------------------------------------

log_info "Dispatching enrollment workflow for: ${REPO_FULL_NAME}"

DISPATCH_PAYLOAD=$(cat <<EOF
{
  "ref": "main",
  "inputs": {
    "repo_full_name": "${REPO_FULL_NAME}",
    "apply_governance": "true",
    "sync_inventory": "true"
  }
}
EOF
)

DISPATCH_RESPONSE=$(curl -sS -w "\n%{http_code}" \
    -X POST \
    -H "Authorization: Bearer ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    -H "Content-Type: application/json" \
    "https://api.github.com/repos/${GITHUB_ORG}/${GOVERNANCE_REPO}/actions/workflows/${WORKFLOW_FILE}/dispatches" \
    -d "${DISPATCH_PAYLOAD}")

HTTP_CODE=$(echo "${DISPATCH_RESPONSE}" | tail -1)
RESPONSE_BODY=$(echo "${DISPATCH_RESPONSE}" | sed '$d')

if [[ "${HTTP_CODE}" == "204" ]]; then
    log_info "✅ Workflow dispatched successfully"
    log_info "Repository: ${REPO_FULL_NAME}"
    log_info "Workflow: ${WORKFLOW_FILE}"

    # Output JSON for n8n/automation consumption
    echo ""
    echo "{"
    echo "  \"status\": \"dispatched\","
    echo "  \"repo_full_name\": \"${REPO_FULL_NAME}\","
    echo "  \"workflow\": \"${WORKFLOW_FILE}\","
    echo "  \"workflow_id\": ${WORKFLOW_ID},"
    echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\""
    echo "}"
else
    log_error "Failed to dispatch workflow"
    log_error "HTTP status: ${HTTP_CODE}"

    if [[ -n "${RESPONSE_BODY}" ]]; then
        echo "${RESPONSE_BODY}" | jq . 2>/dev/null || echo "${RESPONSE_BODY}"
    fi

    exit 1
fi

# -----------------------------------------------------------------------------
# Optional: Wait for workflow to start (for synchronous use cases)
# -----------------------------------------------------------------------------

if [[ "${WAIT_FOR_START:-false}" == "true" ]]; then
    log_info "Waiting for workflow run to start..."
    sleep 3

    # Get most recent workflow run
    RUNS_RESPONSE=$(curl -sS \
        -H "Authorization: Bearer ${GITHUB_TOKEN}" \
        -H "Accept: application/vnd.github+json" \
        "https://api.github.com/repos/${GITHUB_ORG}/${GOVERNANCE_REPO}/actions/workflows/${WORKFLOW_ID}/runs?per_page=1")

    RUN_ID=$(echo "${RUNS_RESPONSE}" | jq -r '.workflow_runs[0].id // empty')
    RUN_URL=$(echo "${RUNS_RESPONSE}" | jq -r '.workflow_runs[0].html_url // empty')

    if [[ -n "${RUN_ID}" ]]; then
        log_info "Workflow run started: ${RUN_URL}"
        echo ""
        echo "{"
        echo "  \"status\": \"started\","
        echo "  \"run_id\": ${RUN_ID},"
        echo "  \"run_url\": \"${RUN_URL}\""
        echo "}"
    fi
fi
