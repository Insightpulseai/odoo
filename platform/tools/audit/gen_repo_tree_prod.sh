#!/usr/bin/env bash
# =============================================================================
# GENERATE PRODUCTION REPO TREE SNAPSHOT
# =============================================================================
# Creates repo tree and git state artifacts for production deployment tracking.
#
# Usage:
#   ./tools/audit/gen_repo_tree_prod.sh [output_dir]
#
# Outputs:
#   docs/repo/GIT_STATE.prod.txt
#   docs/repo/REPO_TREE.prod.md
#   docs/repo/REPO_SNAPSHOT.prod.json
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUTPUT_DIR="${1:-$REPO_ROOT/docs/repo}"

mkdir -p "$OUTPUT_DIR"

echo "=== Generating Repo Tree Snapshot ==="
echo "Repo: $REPO_ROOT"
echo "Output: $OUTPUT_DIR"
echo ""

# =============================================================================
# GIT STATE
# =============================================================================
echo "Generating GIT_STATE.prod.txt..."

cat > "$OUTPUT_DIR/GIT_STATE.prod.txt" << EOF
# Git State Snapshot
# Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
# Host: $(hostname)
# Repo: $REPO_ROOT

SHA: $(git -C "$REPO_ROOT" rev-parse HEAD)
Branch: $(git -C "$REPO_ROOT" branch --show-current 2>/dev/null || echo "detached")
Short SHA: $(git -C "$REPO_ROOT" rev-parse --short HEAD)

# Remote
$(git -C "$REPO_ROOT" remote -v)

# Status (dirty check)
$(git -C "$REPO_ROOT" status --porcelain 2>/dev/null || echo "clean")

# Last 5 commits
$(git -C "$REPO_ROOT" log --oneline -5)

# Tags
$(git -C "$REPO_ROOT" tag --points-at HEAD 2>/dev/null || echo "no tags")
EOF

echo "  ✓ GIT_STATE.prod.txt"

# =============================================================================
# REPO TREE
# =============================================================================
echo "Generating REPO_TREE.prod.md..."

cat > "$OUTPUT_DIR/REPO_TREE.prod.md" << 'EOF'
# Production Repo Tree

EOF

echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$OUTPUT_DIR/REPO_TREE.prod.md"
echo "SHA: $(git -C "$REPO_ROOT" rev-parse --short HEAD)" >> "$OUTPUT_DIR/REPO_TREE.prod.md"
echo "" >> "$OUTPUT_DIR/REPO_TREE.prod.md"

# Generate tree for key directories
for dir in addons deploy tools catalog spec kb docs .github; do
    if [[ -d "$REPO_ROOT/$dir" ]]; then
        echo "## $dir/" >> "$OUTPUT_DIR/REPO_TREE.prod.md"
        echo '```' >> "$OUTPUT_DIR/REPO_TREE.prod.md"

        if command -v tree &>/dev/null; then
            tree -L 2 --dirsfirst --noreport "$REPO_ROOT/$dir" 2>/dev/null >> "$OUTPUT_DIR/REPO_TREE.prod.md" || \
            find "$REPO_ROOT/$dir" -maxdepth 2 -type d | head -50 >> "$OUTPUT_DIR/REPO_TREE.prod.md"
        else
            find "$REPO_ROOT/$dir" -maxdepth 2 | sort | head -100 >> "$OUTPUT_DIR/REPO_TREE.prod.md"
        fi

        echo '```' >> "$OUTPUT_DIR/REPO_TREE.prod.md"
        echo "" >> "$OUTPUT_DIR/REPO_TREE.prod.md"
    fi
done

# IPAI modules summary
echo "## IPAI Modules" >> "$OUTPUT_DIR/REPO_TREE.prod.md"
echo '```' >> "$OUTPUT_DIR/REPO_TREE.prod.md"
find "$REPO_ROOT/addons" -maxdepth 1 -type d -name "ipai_*" -exec basename {} \; | sort >> "$OUTPUT_DIR/REPO_TREE.prod.md"
echo '```' >> "$OUTPUT_DIR/REPO_TREE.prod.md"

echo "  ✓ REPO_TREE.prod.md"

# =============================================================================
# REPO SNAPSHOT JSON
# =============================================================================
echo "Generating REPO_SNAPSHOT.prod.json..."

# Count files by type
py_count=$(find "$REPO_ROOT/addons" -name "*.py" 2>/dev/null | wc -l)
xml_count=$(find "$REPO_ROOT/addons" -name "*.xml" 2>/dev/null | wc -l)
js_count=$(find "$REPO_ROOT/addons" -name "*.js" 2>/dev/null | wc -l)

# List IPAI modules with versions
ipai_modules_json="["
first=true
for manifest in "$REPO_ROOT"/addons/ipai_*/__manifest__.py; do
    if [[ -f "$manifest" ]]; then
        module_name=$(basename "$(dirname "$manifest")")
        version=$(grep -oP '(?<="version":\s*")[^"]+' "$manifest" 2>/dev/null || echo "unknown")
        if [[ "$first" == "true" ]]; then
            first=false
        else
            ipai_modules_json+=","
        fi
        ipai_modules_json+="{\"name\":\"$module_name\",\"version\":\"$version\"}"
    fi
done
ipai_modules_json+="]"

cat > "$OUTPUT_DIR/REPO_SNAPSHOT.prod.json" << EOF
{
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "hostname": "$(hostname)",
  "repo_path": "$REPO_ROOT",
  "git": {
    "sha": "$(git -C "$REPO_ROOT" rev-parse HEAD)",
    "short_sha": "$(git -C "$REPO_ROOT" rev-parse --short HEAD)",
    "branch": "$(git -C "$REPO_ROOT" branch --show-current 2>/dev/null || echo "detached")",
    "dirty_files": $(git -C "$REPO_ROOT" status --porcelain 2>/dev/null | wc -l)
  },
  "file_counts": {
    "python": $py_count,
    "xml": $xml_count,
    "javascript": $js_count
  },
  "ipai_modules": $ipai_modules_json
}
EOF

echo "  ✓ REPO_SNAPSHOT.prod.json"

echo ""
echo "=== Repo Tree Snapshot Complete ==="
echo "Artifacts in: $OUTPUT_DIR"
