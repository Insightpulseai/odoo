#!/usr/bin/env bash
# analyze-dependencies.sh — Cross-plane dependency scanner
#
# Scans Python and TypeScript/JavaScript import statements across the monorepo
# to identify cross-plane dependencies. Outputs a dependency matrix.
#
# Usage: ./scripts/repo-split/analyze-dependencies.sh [--json]
#
# Authority: docs/architecture/adr/ADR_REPO_SPLIT_STRATEGY.md
# SSOT: ssot/governance/org-repo-target-state.yaml

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUTPUT_JSON="${1:-}"

# ─── Plane-to-directory mapping ──────────────────────────────────────────────
# Each target repo maps to one or more top-level monorepo directories.
# Directories not listed here are unmapped (archive, legacy, orphan).

declare -A PLANE_DIRS
PLANE_DIRS=(
  [odoo]="addons config odoo"
  [platform]="platform apps packages"
  [agent-platform]="agent-platform"
  [agents]="agents"
  [data-intelligence]="data-intelligence databricks lakehouse"
  [web]="web web-site docs-site"
  [infra]="infra docker"
  [automations]="automations"
  [design]="design"
  [docs]="docs"
  [templates]="templates"
  [.github]=".github"
)

# Reverse map: directory -> plane
declare -A DIR_TO_PLANE
for plane in "${!PLANE_DIRS[@]}"; do
  for dir in ${PLANE_DIRS[$plane]}; do
    DIR_TO_PLANE[$dir]="$plane"
  done
done

# Also map scripts/, spec/, ssot/ by scanning their subdirectories
# These are cross-cutting and mapped by content analysis below.

echo "============================================================"
echo "Cross-Plane Dependency Analysis"
echo "Repo: $REPO_ROOT"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================================"
echo ""

# ─── Phase 1: Python imports ────────────────────────────────────────────────

echo "--- Phase 1: Python cross-plane imports ---"
echo ""

# Find Python files, extract imports, check if they reference other planes
declare -A PY_DEPS

for plane in "${!PLANE_DIRS[@]}"; do
  for dir in ${PLANE_DIRS[$plane]}; do
    target_dir="$REPO_ROOT/$dir"
    [ -d "$target_dir" ] || continue

    # Find all .py files in this plane
    while IFS= read -r pyfile; do
      [ -f "$pyfile" ] || continue

      # Extract import targets (from X import Y, import X)
      while IFS= read -r import_path; do
        # Check if the import references another plane's directory
        for other_plane in "${!PLANE_DIRS[@]}"; do
          [ "$other_plane" = "$plane" ] && continue
          for other_dir in ${PLANE_DIRS[$other_plane]}; do
            # Check if import path starts with the other directory name
            # or references it (e.g., "from agents.evals" when in platform/)
            if echo "$import_path" | grep -qiE "^(from\s+)?${other_dir}[./]|^import\s+${other_dir}[.]"; then
              key="${plane} -> ${other_plane}"
              PY_DEPS[$key]=$(( ${PY_DEPS[$key]:-0} + 1 ))
            fi
          done
        done
      done < <(grep -hE '^\s*(from\s+\S+\s+import|import\s+\S+)' "$pyfile" 2>/dev/null || true)
    done < <(find "$target_dir" -name '*.py' -not -path '*/__pycache__/*' -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null)
  done
done

if [ ${#PY_DEPS[@]} -eq 0 ]; then
  echo "  No cross-plane Python imports detected."
else
  printf "  %-40s %s\n" "DEPENDENCY" "COUNT"
  printf "  %-40s %s\n" "----------------------------------------" "-----"
  for key in $(echo "${!PY_DEPS[@]}" | tr ' ' '\n' | sort); do
    printf "  %-40s %d\n" "$key" "${PY_DEPS[$key]}"
  done
fi
echo ""

# ─── Phase 2: TypeScript/JavaScript imports ──────────────────────────────────

echo "--- Phase 2: TypeScript/JavaScript cross-plane imports ---"
echo ""

declare -A TS_DEPS

for plane in "${!PLANE_DIRS[@]}"; do
  for dir in ${PLANE_DIRS[$plane]}; do
    target_dir="$REPO_ROOT/$dir"
    [ -d "$target_dir" ] || continue

    while IFS= read -r tsfile; do
      [ -f "$tsfile" ] || continue

      # Extract import/require paths
      while IFS= read -r import_path; do
        for other_plane in "${!PLANE_DIRS[@]}"; do
          [ "$other_plane" = "$plane" ] && continue
          for other_dir in ${PLANE_DIRS[$other_plane]}; do
            if echo "$import_path" | grep -qiE "@${other_dir}/|['\"]\.\./(\.\./)*(${other_dir})/|from\s+['\"]${other_dir}/"; then
              key="${plane} -> ${other_plane}"
              TS_DEPS[$key]=$(( ${TS_DEPS[$key]:-0} + 1 ))
            fi
          done
        done
      done < <(grep -hE '^\s*(import\s|from\s|require\()' "$tsfile" 2>/dev/null || true)
    done < <(find "$target_dir" \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' \) \
      -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/.next/*' -not -path '*/dist/*' 2>/dev/null)
  done
done

if [ ${#TS_DEPS[@]} -eq 0 ]; then
  echo "  No cross-plane TypeScript/JavaScript imports detected."
else
  printf "  %-40s %s\n" "DEPENDENCY" "COUNT"
  printf "  %-40s %s\n" "----------------------------------------" "-----"
  for key in $(echo "${!TS_DEPS[@]}" | tr ' ' '\n' | sort); do
    printf "  %-40s %d\n" "$key" "${TS_DEPS[$key]}"
  done
fi
echo ""

# ─── Phase 3: YAML/config cross-references ──────────────────────────────────

echo "--- Phase 3: Cross-plane path references in YAML/config ---"
echo ""

declare -A YAML_DEPS

for plane in "${!PLANE_DIRS[@]}"; do
  for dir in ${PLANE_DIRS[$plane]}; do
    target_dir="$REPO_ROOT/$dir"
    [ -d "$target_dir" ] || continue

    while IFS= read -r yamlfile; do
      [ -f "$yamlfile" ] || continue

      for other_plane in "${!PLANE_DIRS[@]}"; do
        [ "$other_plane" = "$plane" ] && continue
        for other_dir in ${PLANE_DIRS[$other_plane]}; do
          count=$(grep -cE "(^|\s|/|:)${other_dir}/" "$yamlfile" 2>/dev/null || echo 0)
          if [ "$count" -gt 0 ]; then
            key="${plane} -> ${other_plane}"
            YAML_DEPS[$key]=$(( ${YAML_DEPS[$key]:-0} + count ))
          fi
        done
      done
    done < <(find "$target_dir" \( -name '*.yaml' -o -name '*.yml' -o -name '*.json' \) \
      -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/package-lock.json' 2>/dev/null)
  done
done

if [ ${#YAML_DEPS[@]} -eq 0 ]; then
  echo "  No cross-plane YAML path references detected."
else
  printf "  %-40s %s\n" "DEPENDENCY" "COUNT"
  printf "  %-40s %s\n" "----------------------------------------" "-----"
  for key in $(echo "${!YAML_DEPS[@]}" | tr ' ' '\n' | sort); do
    printf "  %-40s %d\n" "$key" "${YAML_DEPS[$key]}"
  done
fi
echo ""

# ─── Phase 4: CI workflow path triggers ──────────────────────────────────────

echo "--- Phase 4: CI workflow path triggers (cross-plane coupling) ---"
echo ""

WORKFLOW_DIR="$REPO_ROOT/.github/workflows"
if [ -d "$WORKFLOW_DIR" ]; then
  declare -A WF_PLANES
  for wf in "$WORKFLOW_DIR"/*.yml; do
    [ -f "$wf" ] || continue
    wf_name=$(basename "$wf")
    planes_touched=""
    for other_plane in "${!PLANE_DIRS[@]}"; do
      for other_dir in ${PLANE_DIRS[$other_plane]}; do
        if grep -qE "paths:.*${other_dir}/|\"${other_dir}/|'${other_dir}/" "$wf" 2>/dev/null; then
          if ! echo "$planes_touched" | grep -q "$other_plane"; then
            planes_touched="$planes_touched $other_plane"
          fi
        fi
      done
    done
    plane_count=$(echo "$planes_touched" | wc -w)
    if [ "$plane_count" -gt 1 ]; then
      echo "  $wf_name touches:$planes_touched"
    fi
  done
else
  echo "  No .github/workflows/ directory found."
fi
echo ""

# ─── Phase 5: Shared directories (cross-cutting) ────────────────────────────

echo "--- Phase 5: Unmapped/shared directories (cross-cutting concerns) ---"
echo ""

for dir in scripts spec ssot eval foundry marketplace prompts skills supabase archive ops-platform; do
  if [ -d "$REPO_ROOT/$dir" ]; then
    file_count=$(find "$REPO_ROOT/$dir" -type f -not -path '*/.git/*' 2>/dev/null | wc -l)
    echo "  $dir/ — $file_count files (needs assignment to a target repo)"
  fi
done
echo ""

# ─── Phase 6: Nested git repos ──────────────────────────────────────────────

echo "--- Phase 6: Nested git repositories (already partially split) ---"
echo ""

while IFS= read -r gitdir; do
  parent="$(dirname "$gitdir")"
  rel="${parent#$REPO_ROOT/}"
  if [ "$rel" != "." ] && [ "$rel" != "" ]; then
    echo "  $rel/ — has own .git (nested repo)"
  fi
done < <(find "$REPO_ROOT" -maxdepth 2 -name '.git' -type d 2>/dev/null)
echo ""

# ─── Summary matrix ─────────────────────────────────────────────────────────

echo "============================================================"
echo "DEPENDENCY MATRIX SUMMARY"
echo "============================================================"
echo ""
echo "Arrows show direction of dependency (A -> B means A imports from B)."
echo "Count = total import/reference occurrences across Python + TS + YAML."
echo ""

declare -A TOTAL_DEPS

for key in "${!PY_DEPS[@]}"; do
  TOTAL_DEPS[$key]=$(( ${TOTAL_DEPS[$key]:-0} + ${PY_DEPS[$key]} ))
done
for key in "${!TS_DEPS[@]}"; do
  TOTAL_DEPS[$key]=$(( ${TOTAL_DEPS[$key]:-0} + ${TS_DEPS[$key]} ))
done
for key in "${!YAML_DEPS[@]}"; do
  TOTAL_DEPS[$key]=$(( ${TOTAL_DEPS[$key]:-0} + ${YAML_DEPS[$key]} ))
done

if [ ${#TOTAL_DEPS[@]} -eq 0 ]; then
  echo "  No cross-plane dependencies detected."
  echo "  This likely means planes are already well-isolated or imports use"
  echo "  relative paths within the same plane."
else
  printf "  %-40s %s\n" "DEPENDENCY" "TOTAL"
  printf "  %-40s %s\n" "----------------------------------------" "-----"
  for key in $(echo "${!TOTAL_DEPS[@]}" | tr ' ' '\n' | sort); do
    printf "  %-40s %d\n" "$key" "${TOTAL_DEPS[$key]}"
  done
fi
echo ""
echo "--- End of analysis ---"
