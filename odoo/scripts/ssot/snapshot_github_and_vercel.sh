#!/usr/bin/env bash
#
# snapshot_github_and_vercel.sh
#
# Single idempotent pipeline that snapshots three layers:
#   1. Org — metadata, teams, members, repos, branch protection
#   2. Repo — workflows, workflow runs, deployments, releases, tags
#   3. Runtime — Vercel projects, deployments, aliases
#
# Usage:
#   ./scripts/ssot/snapshot_github_and_vercel.sh              # full snapshot
#   ./scripts/ssot/snapshot_github_and_vercel.sh --org-only    # GitHub org layer only
#   ./scripts/ssot/snapshot_github_and_vercel.sh --repo-only   # GitHub repo layer only
#   ./scripts/ssot/snapshot_github_and_vercel.sh --vercel-only # Vercel layer only
#   ./scripts/ssot/snapshot_github_and_vercel.sh --repo odoo   # single repo
#
# Required env vars:
#   GITHUB_TOKEN or gh auth   — GitHub API access
#   VERCEL_TOKEN              — Vercel REST API (optional, skips Vercel if missing)
#
# Output:
#   ssot/github/org.snapshot.json
#   ssot/github/repos.snapshot.json
#   ssot/github/repo-details/<repo>.json
#   ssot/github/repo-details/<repo>.workflows.json
#   ssot/github/repo-details/<repo>.workflow-runs.json
#   ssot/github/repo-details/<repo>.deployments.json
#   ssot/vercel/projects.snapshot.json
#   ssot/vercel/deployments.snapshot.json
#   ssot/vercel/aliases.snapshot.json
#   ssot/evidence/snapshot-manifest.json
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}"

# ─── Config ───────────────────────────────────────────────────────────
GH_ORG="${GH_ORG:-Insightpulseai}"
VERCEL_TEAM_ID="${VERCEL_TEAM_ID:-}"
MAX_WORKFLOW_RUNS="${MAX_WORKFLOW_RUNS:-50}"
SNAPSHOT_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# ─── Output dirs ──────────────────────────────────────────────────────
GITHUB_DIR="ssot/github"
REPO_DETAIL_DIR="${GITHUB_DIR}/repo-details"
VERCEL_DIR="ssot/vercel"
EVIDENCE_DIR="ssot/evidence"
mkdir -p "${REPO_DETAIL_DIR}" "${VERCEL_DIR}" "${EVIDENCE_DIR}"

# ─── Parse args ───────────────────────────────────────────────────────
DO_ORG=true
DO_REPO=true
DO_VERCEL=true
SINGLE_REPO=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --org-only)   DO_REPO=false; DO_VERCEL=false ;;
    --repo-only)  DO_ORG=false; DO_VERCEL=false ;;
    --vercel-only) DO_ORG=false; DO_REPO=false ;;
    --repo)       SINGLE_REPO="$2"; shift ;;
    *)            echo "Unknown arg: $1"; exit 1 ;;
  esac
  shift
done

# ─── Helpers ──────────────────────────────────────────────────────────
log() { echo "$(date +%H:%M:%S) | $*"; }

gh_api() {
  local endpoint="$1"
  local output="$2"
  local paginate="${3:-false}"

  if [[ "${paginate}" == "true" ]]; then
    gh api --paginate "${endpoint}" > "${output}" 2>/dev/null || {
      echo "[]" > "${output}"
      log "  WARN: ${endpoint} returned error, wrote empty array"
    }
  else
    gh api "${endpoint}" > "${output}" 2>/dev/null || {
      echo "{}" > "${output}"
      log "  WARN: ${endpoint} returned error, wrote empty object"
    }
  fi
}

vercel_api() {
  local endpoint="$1"
  local output="$2"
  local url="https://api.vercel.com${endpoint}"

  if [[ -n "${VERCEL_TEAM_ID}" ]]; then
    if [[ "${url}" == *"?"* ]]; then
      url="${url}&teamId=${VERCEL_TEAM_ID}"
    else
      url="${url}?teamId=${VERCEL_TEAM_ID}"
    fi
  fi

  curl -sS -H "Authorization: Bearer ${VERCEL_TOKEN}" "${url}" > "${output}" 2>/dev/null || {
    echo "{}" > "${output}"
    log "  WARN: Vercel ${endpoint} returned error"
  }
}

# ─── Layer 1: Org Snapshot ────────────────────────────────────────────
snapshot_org() {
  log "Layer 1: Org snapshot (${GH_ORG})"

  log "  org metadata..."
  gh_api "/orgs/${GH_ORG}" "${GITHUB_DIR}/org.snapshot.json"

  log "  org repos..."
  gh_api "/orgs/${GH_ORG}/repos?type=all&per_page=100&sort=updated" \
    "${GITHUB_DIR}/repos.snapshot.json" true

  log "  org teams..."
  gh_api "/orgs/${GH_ORG}/teams?per_page=100" \
    "${GITHUB_DIR}/teams.snapshot.json" true

  log "  org members..."
  gh_api "/orgs/${GH_ORG}/members?per_page=100" \
    "${GITHUB_DIR}/members.snapshot.json" true

  local repo_count
  repo_count=$(jq 'if type == "array" then length else 0 end' "${GITHUB_DIR}/repos.snapshot.json" 2>/dev/null || echo 0)
  log "  Found ${repo_count} repos"
}

# ─── Layer 2: Repo Snapshot ───────────────────────────────────────────
snapshot_repo() {
  local repo="$1"
  log "  repo: ${repo}"

  # repo metadata
  gh_api "/repos/${GH_ORG}/${repo}" \
    "${REPO_DETAIL_DIR}/${repo}.json"

  # branch protection (default branch)
  local default_branch
  default_branch=$(jq -r '.default_branch // "main"' "${REPO_DETAIL_DIR}/${repo}.json" 2>/dev/null || echo "main")
  gh_api "/repos/${GH_ORG}/${repo}/branches/${default_branch}/protection" \
    "${REPO_DETAIL_DIR}/${repo}.branch-protection.json"

  # workflows
  gh_api "/repos/${GH_ORG}/${repo}/actions/workflows?per_page=100" \
    "${REPO_DETAIL_DIR}/${repo}.workflows.json" true

  # recent workflow runs (capped)
  gh_api "/repos/${GH_ORG}/${repo}/actions/runs?per_page=${MAX_WORKFLOW_RUNS}" \
    "${REPO_DETAIL_DIR}/${repo}.workflow-runs.json"

  # deployments
  gh_api "/repos/${GH_ORG}/${repo}/deployments?per_page=100" \
    "${REPO_DETAIL_DIR}/${repo}.deployments.json" true

  # environments
  gh_api "/repos/${GH_ORG}/${repo}/environments" \
    "${REPO_DETAIL_DIR}/${repo}.environments.json"

  # releases (last 10)
  gh_api "/repos/${GH_ORG}/${repo}/releases?per_page=10" \
    "${REPO_DETAIL_DIR}/${repo}.releases.json"

  # tags (last 20)
  gh_api "/repos/${GH_ORG}/${repo}/tags?per_page=20" \
    "${REPO_DETAIL_DIR}/${repo}.tags.json"
}

snapshot_all_repos() {
  log "Layer 2: Repo snapshots"

  if [[ -n "${SINGLE_REPO}" ]]; then
    snapshot_repo "${SINGLE_REPO}"
    return
  fi

  local repos
  repos=$(jq -r '
    if type == "array" then .[].name
    elif type == "object" and has("name") then .name
    else empty end
  ' "${GITHUB_DIR}/repos.snapshot.json" 2>/dev/null || echo "")

  if [[ -z "${repos}" ]]; then
    log "  WARN: No repos found in repos.snapshot.json"
    return
  fi

  local count=0
  while IFS= read -r repo; do
    [[ -z "${repo}" ]] && continue
    snapshot_repo "${repo}"
    count=$((count + 1))
  done <<< "${repos}"

  log "  Snapshotted ${count} repos"
}

# ─── Layer 3: Vercel Snapshot ─────────────────────────────────────────
snapshot_vercel() {
  if [[ -z "${VERCEL_TOKEN:-}" ]]; then
    log "Layer 3: Vercel — SKIPPED (VERCEL_TOKEN not set)"
    echo '{"skipped": true, "reason": "VERCEL_TOKEN not set"}' > "${VERCEL_DIR}/projects.snapshot.json"
    echo '{"skipped": true, "reason": "VERCEL_TOKEN not set"}' > "${VERCEL_DIR}/deployments.snapshot.json"
    echo '{"skipped": true, "reason": "VERCEL_TOKEN not set"}' > "${VERCEL_DIR}/aliases.snapshot.json"
    return
  fi

  log "Layer 3: Vercel snapshot"

  log "  projects..."
  vercel_api "/v9/projects?limit=100" "${VERCEL_DIR}/projects.snapshot.json"

  log "  deployments (last 100)..."
  vercel_api "/v6/deployments?limit=100" "${VERCEL_DIR}/deployments.snapshot.json"

  # per-project aliases
  local project_ids
  project_ids=$(jq -r '.projects[]?.id // empty' "${VERCEL_DIR}/projects.snapshot.json" 2>/dev/null || echo "")

  if [[ -n "${project_ids}" ]]; then
    local all_aliases="[]"
    while IFS= read -r pid; do
      [[ -z "${pid}" ]] && continue
      local tmp
      tmp=$(mktemp)
      vercel_api "/v4/aliases?projectId=${pid}&limit=50" "${tmp}"
      local aliases_chunk
      aliases_chunk=$(jq '.aliases // []' "${tmp}" 2>/dev/null || echo "[]")
      all_aliases=$(echo "${all_aliases}" | jq --argjson chunk "${aliases_chunk}" '. + $chunk')
      rm -f "${tmp}"
    done <<< "${project_ids}"
    echo "${all_aliases}" | jq '.' > "${VERCEL_DIR}/aliases.snapshot.json"
  else
    echo "[]" > "${VERCEL_DIR}/aliases.snapshot.json"
  fi

  local proj_count
  proj_count=$(jq '.projects | length' "${VERCEL_DIR}/projects.snapshot.json" 2>/dev/null || echo 0)
  local deploy_count
  deploy_count=$(jq '.deployments | length' "${VERCEL_DIR}/deployments.snapshot.json" 2>/dev/null || echo 0)
  log "  Found ${proj_count} projects, ${deploy_count} deployments"
}

# ─── Build manifest ──────────────────────────────────────────────────
build_manifest() {
  log "Building snapshot manifest..."

  local repo_count
  repo_count=$(jq 'if type == "array" then length else 0 end' \
    "${GITHUB_DIR}/repos.snapshot.json" 2>/dev/null || echo 0)

  local workflow_count=0
  if [[ -d "${REPO_DETAIL_DIR}" ]]; then
    workflow_count=$(find "${REPO_DETAIL_DIR}" -name "*.workflows.json" -exec \
      jq '.workflows | length // 0' {} + 2>/dev/null | awk '{s+=$1} END {print s+0}')
  fi

  local vercel_proj_count
  vercel_proj_count=$(jq '.projects | length // 0' \
    "${VERCEL_DIR}/projects.snapshot.json" 2>/dev/null || echo 0)

  local vercel_deploy_count
  vercel_deploy_count=$(jq '.deployments | length // 0' \
    "${VERCEL_DIR}/deployments.snapshot.json" 2>/dev/null || echo 0)

  python3 "${SCRIPT_DIR}/build_snapshot_manifest.py" \
    --timestamp "${SNAPSHOT_TS}" \
    --org "${GH_ORG}" \
    --repo-count "${repo_count}" \
    --workflow-count "${workflow_count}" \
    --vercel-projects "${vercel_proj_count}" \
    --vercel-deployments "${vercel_deploy_count}" \
    --output "${EVIDENCE_DIR}/snapshot-manifest.json"

  log "Manifest written to ${EVIDENCE_DIR}/snapshot-manifest.json"
}

# ─── Main ─────────────────────────────────────────────────────────────
main() {
  log "=== SSOT Inventory Snapshot ==="
  log "Org: ${GH_ORG} | Timestamp: ${SNAPSHOT_TS}"
  log ""

  # Verify gh is authenticated
  if ! gh auth status &>/dev/null; then
    echo "ERROR: gh is not authenticated. Run 'gh auth login' first."
    exit 1
  fi

  [[ "${DO_ORG}" == "true" ]] && snapshot_org
  [[ "${DO_REPO}" == "true" ]] && snapshot_all_repos
  [[ "${DO_VERCEL}" == "true" ]] && snapshot_vercel

  build_manifest

  log ""
  log "=== Snapshot complete ==="
  log "Output:"
  log "  GitHub: ${GITHUB_DIR}/"
  log "  Vercel: ${VERCEL_DIR}/"
  log "  Manifest: ${EVIDENCE_DIR}/snapshot-manifest.json"
}

main "$@"
