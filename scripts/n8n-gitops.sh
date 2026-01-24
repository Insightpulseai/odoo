#!/usr/bin/env bash
# GitOps management for n8n workflows
# Export/import workflows to/from the repository
#
# Usage:
#   ./scripts/n8n-gitops.sh export           # Export all workflows to n8n/workflows/
#   ./scripts/n8n-gitops.sh import           # Import all workflows from n8n/workflows/
#   ./scripts/n8n-gitops.sh import <file>    # Import specific workflow
#   ./scripts/n8n-gitops.sh diff             # Show diff between live and repo
#   ./scripts/n8n-gitops.sh activate <id>    # Activate a workflow by ID

set -euo pipefail

# Configuration
N8N_URL="${N8N_URL:-http://localhost:5678}"
N8N_API_KEY="${N8N_API_KEY:-}"
WORKFLOW_DIR="n8n/workflows"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[n8n-gitops]${NC} $*"; }
warn() { echo -e "${YELLOW}[n8n-gitops] WARN:${NC} $*"; }
error() { echo -e "${RED}[n8n-gitops] ERROR:${NC} $*" >&2; }

# Check prerequisites
check_prereqs() {
  if [[ -z "$N8N_API_KEY" ]]; then
    error "N8N_API_KEY not set. Export it or create via n8n Settings → API."
    exit 1
  fi

  if ! command -v jq &>/dev/null; then
    error "jq is required. Install with: apt install jq"
    exit 1
  fi
}

# API helper
n8n_api() {
  local method="$1"
  local endpoint="$2"
  local data="${3:-}"

  local args=(-s -X "$method" -H "X-N8N-API-KEY: $N8N_API_KEY" -H "Content-Type: application/json")

  if [[ -n "$data" ]]; then
    args+=(-d "$data")
  fi

  curl "${args[@]}" "${N8N_URL}/api/v1${endpoint}"
}

# Export all workflows
cmd_export() {
  log "Exporting workflows from ${N8N_URL}..."

  local response
  response=$(n8n_api GET "/workflows")

  local count
  count=$(echo "$response" | jq '.data | length')
  log "Found $count workflows"

  echo "$response" | jq -c '.data[]' | while read -r workflow; do
    local id name safename
    id=$(echo "$workflow" | jq -r '.id')
    name=$(echo "$workflow" | jq -r '.name')
    safename=$(echo "$name" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g')

    # Fetch full workflow (with nodes)
    local full_workflow
    full_workflow=$(n8n_api GET "/workflows/$id")

    # Determine output directory based on tags
    local outdir="$WORKFLOW_DIR"
    local tags
    tags=$(echo "$full_workflow" | jq -r '.tags[]?.name // empty' 2>/dev/null || true)
    if echo "$tags" | grep -q "control-plane"; then
      outdir="$WORKFLOW_DIR/control-plane"
    elif echo "$tags" | grep -q "integration"; then
      outdir="$WORKFLOW_DIR/integration"
    fi

    mkdir -p "$outdir"
    local outfile="$outdir/${safename}.json"

    # Clean up workflow for storage (remove runtime fields)
    echo "$full_workflow" | jq 'del(.id, .createdAt, .updatedAt, .active) | .versionId = "1"' > "$outfile"

    log "  → $outfile"
  done

  log "Export complete"
}

# Import all workflows
cmd_import() {
  local target="${1:-}"

  if [[ -n "$target" ]]; then
    # Import single workflow
    import_workflow "$target"
  else
    # Import all workflows
    log "Importing workflows from ${WORKFLOW_DIR}..."

    find "$WORKFLOW_DIR" -name "*.json" -type f | while read -r file; do
      import_workflow "$file"
    done

    log "Import complete"
  fi
}

import_workflow() {
  local file="$1"

  if [[ ! -f "$file" ]]; then
    error "File not found: $file"
    return 1
  fi

  local name
  name=$(jq -r '.name' "$file")
  log "Importing: $name"

  # Check if workflow exists (by name)
  local existing
  existing=$(n8n_api GET "/workflows" | jq -r --arg name "$name" '.data[] | select(.name == $name) | .id')

  if [[ -n "$existing" ]]; then
    # Update existing
    log "  Updating existing workflow (id=$existing)"
    local updated
    updated=$(jq --arg id "$existing" '. + {id: $id}' "$file")
    n8n_api PUT "/workflows/$existing" "$updated" > /dev/null
  else
    # Create new
    log "  Creating new workflow"
    n8n_api POST "/workflows" "$(cat "$file")" > /dev/null
  fi

  log "  ✓ Imported"
}

# Show diff between live and repo
cmd_diff() {
  log "Comparing live workflows with repository..."

  local response
  response=$(n8n_api GET "/workflows")

  echo "$response" | jq -c '.data[]' | while read -r workflow; do
    local id name safename
    id=$(echo "$workflow" | jq -r '.id')
    name=$(echo "$workflow" | jq -r '.name')
    safename=$(echo "$name" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g')

    # Find matching file
    local file
    file=$(find "$WORKFLOW_DIR" -name "${safename}.json" 2>/dev/null | head -1)

    if [[ -z "$file" ]]; then
      echo -e "${YELLOW}[NOT IN REPO]${NC} $name (live id=$id)"
      continue
    fi

    # Compare (ignoring runtime fields)
    local live_normalized repo_normalized
    live_normalized=$(n8n_api GET "/workflows/$id" | jq -S 'del(.id, .createdAt, .updatedAt, .active, .versionId)')
    repo_normalized=$(jq -S 'del(.versionId)' "$file")

    if [[ "$live_normalized" == "$repo_normalized" ]]; then
      echo -e "${GREEN}[SYNCED]${NC} $name"
    else
      echo -e "${RED}[DIFFERS]${NC} $name"
      # Show brief diff
      diff -u <(echo "$repo_normalized" | jq '.nodes | length') <(echo "$live_normalized" | jq '.nodes | length') || true
    fi
  done

  # Check for files not in live
  find "$WORKFLOW_DIR" -name "*.json" -type f | while read -r file; do
    local name
    name=$(jq -r '.name' "$file")
    local exists
    exists=$(echo "$response" | jq -r --arg name "$name" '.data[] | select(.name == $name) | .id')
    if [[ -z "$exists" ]]; then
      echo -e "${BLUE}[NOT LIVE]${NC} $name (file: $file)"
    fi
  done
}

# Activate workflow
cmd_activate() {
  local id="$1"

  if [[ -z "$id" ]]; then
    error "Usage: $0 activate <workflow-id>"
    exit 1
  fi

  log "Activating workflow $id..."
  n8n_api PATCH "/workflows/$id" '{"active": true}' > /dev/null
  log "✓ Activated"
}

# Main
main() {
  local cmd="${1:-help}"
  shift || true

  case "$cmd" in
    export)
      check_prereqs
      cmd_export
      ;;
    import)
      check_prereqs
      cmd_import "$@"
      ;;
    diff)
      check_prereqs
      cmd_diff
      ;;
    activate)
      check_prereqs
      cmd_activate "$@"
      ;;
    help|--help|-h)
      cat <<EOF
n8n GitOps - Manage n8n workflows via Git

Usage: $0 <command> [args]

Commands:
  export           Export all live workflows to n8n/workflows/
  import [file]    Import workflows (all or specific file)
  diff             Compare live vs repo workflows
  activate <id>    Activate a workflow by ID

Environment:
  N8N_URL         n8n instance URL (default: http://localhost:5678)
  N8N_API_KEY     API key from n8n Settings → API (required)

Examples:
  $0 export
  $0 import n8n/workflows/control-plane/deploy-trigger.json
  $0 diff
  $0 activate abc123
EOF
      ;;
    *)
      error "Unknown command: $cmd"
      main help
      exit 1
      ;;
  esac
}

main "$@"
