#!/usr/bin/env bash
# =============================================================================
# Repository Surfaces Inventory — SSOT Audit
# =============================================================================
# Counts and lists all workspace, devcontainer, and docker-compose files
#
# Usage:
#   ./scripts/ci/inventory_repo_surfaces.sh
#
# Outputs:
#   - /tmp/ipai_workspaces.txt
#   - /tmp/ipai_devcontainers.txt
#   - /tmp/ipai_compose.txt
# =============================================================================

set -euo pipefail

prune=( -path './.git' -prune -o -path './node_modules' -prune -o -path './.venv' -prune -o )

count_list () {
  local label="$1"; shift
  local outfile="$1"; shift
  echo "== ${label} =="
  find . "${prune[@]}" -type f \( "$@" \) -print | sort | tee "$outfile"
  echo "COUNT: $(wc -l <"$outfile" | tr -d ' ')"
  echo
}

count_list "VS Code workspaces" /tmp/ipai_workspaces.txt -name '*.code-workspace' -o -name '*.code-workspace.json'
count_list "Dev Containers"      /tmp/ipai_devcontainers.txt -name 'devcontainer.json'
count_list "Docker Compose"      /tmp/ipai_compose.txt -name 'docker-compose*.yml' -o -name 'docker-compose*.yaml'

echo "== Active vs Archived Split =="
for f in /tmp/ipai_workspaces.txt /tmp/ipai_devcontainers.txt /tmp/ipai_compose.txt; do
  echo
  echo "File: $f"
  echo "-- Active (not in archive/) --"
  active_count=$(grep -cvE '(^|/)archive(/|$)' "$f" || echo "0")
  grep -vE '(^|/)archive(/|$)' "$f" || true
  echo "Active count: $active_count"
  echo "-- Archived (in archive/) --"
  archived_count=$(grep -cE '(^|/)archive(/|$)' "$f" || echo "0")
  grep -E '(^|/)archive(/|$)' "$f" || true
  echo "Archived count: $archived_count"
done
