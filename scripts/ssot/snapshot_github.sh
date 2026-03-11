#!/usr/bin/env bash
#
# snapshot_github.sh
#
# Single idempotent pipeline that snapshots two layers:
#   1. Org — metadata, teams, members, repos, branch protection
#   2. Repo — workflows, workflow runs, deployments, releases, tags
#
# Usage:
#   ./scripts/ssot/snapshot_github.sh              # full snapshot
#   ./scripts/ssot/snapshot_github.sh --org-only    # GitHub org layer only
#   ./scripts/ssot/snapshot_github.sh --repo-only   # GitHub repo layer only
#   ./scripts/ssot/snapshot_github.sh --repo odoo   # single repo
#
# Required env vars:
#   GITHUB_TOKEN or gh auth   — GitHub API access
#
# Output:
#   ssot/github/org.snapshot.json
#   ssot/github/repos.snapshot.json
#   ssot/github/repo-details/<repo>.json
#   ssot/github/repo-details/<repo>.workflows.json
#   ssot/github/repo-details/<repo>.workflow-runs.json
#   ssot/github/repo-details/<repo>.deployments.json
#   ssot/evidence/snapshot-manifest.json
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}"

# ─── Config ───────────────────────────────────────────────────────────
GH_ORG="${GH_ORG:-Insightpulseai}"
MAX_WORKFLOW_RUNS="${MAX_WORKFLOW_RUNS:-50}"
SNAPSHOT_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# ─── Output dirs ──────────────────────────────────────────────────────
GITHUB_DIR="ssot/github"
REPO_DETAIL_DIR="${GITHUB_DIR}/repo-details"
EVIDENCE_DIR="ssot/evidence"
mkdir -p "${REPO_DETAIL_DIR}" "${EVIDENCE_DIR}"

# ─── Parse args ───────────────────────────────────────────────────────
DO_ORG=true
DO_REPO=true
SINGLE_REPO=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --org-only)   DO_REPO=false ;;
    --repo-only)  DO_ORG=false ;;
    --github-only) ;; # Legacy arg for compatibility
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

  python3 "${SCRIPT_DIR}/build_snapshot_manifest.py" \
    --timestamp "${SNAPSHOT_TS}" \
    --org "${GH_ORG}" \
    --repo-count "${repo_count}" \
    --workflow-count "${workflow_count}" \
    --vercel-projects "0" \
    --vercel-deployments "0" \
    --output "${EVIDENCE_DIR}/snapshot-manifest.json"

  log "Manifest written to ${EVIDENCE_DIR}/snapshot-manifest.json"
}

# ─── Main ─────────────────────────────────────────────────────────────
main() {
  log "=== SSOT Inventory Snapshot (GitHub Only) ==="
  log "Org: ${GH_ORG} | Timestamp: ${SNAPSHOT_TS}"
  log ""

  # Verify gh is authenticated
  if ! gh auth status &>/dev/null; then
    echo "ERROR: gh is not authenticated. Run 'gh auth login' first."
    exit 1
  fi

  [[ "${DO_ORG}" == "true" ]] && snapshot_org
  [[ "${DO_REPO}" == "true" ]] && snapshot_all_repos

  build_manifest

  log ""
  log "=== Snapshot complete ==="
  log "Output:"
  log "  GitHub: ${GITHUB_DIR}/"
  log "  Manifest: ${EVIDENCE_DIR}/snapshot-manifest.json"
}

main "$@"
