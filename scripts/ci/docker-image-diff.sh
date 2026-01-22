#!/bin/bash
# =============================================================================
# Docker Image Diff Script
# =============================================================================
# Compares two Docker images at multiple levels:
#   - Layer history
#   - Filesystem (addons, config, python packages)
#   - Runtime (pip packages, odoo version, env vars)
#
# Usage:
#   ./scripts/ci/docker-image-diff.sh <live_image> <target_image> [output_dir]
#
# Examples:
#   ./scripts/ci/docker-image-diff.sh \
#     ghcr.io/jgtolentino/odoo-ce:prod \
#     ghcr.io/jgtolentino/odoo-ce:edge-standard \
#     /tmp/image-diff-output
#
# Exit codes:
#   0 - Success (diff completed)
#   1 - Error (missing args, docker failure)
# =============================================================================
set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================
IMAGE_LIVE="${1:-}"
IMAGE_TARGET="${2:-}"
OUTPUT_DIR="${3:-/tmp/docker-image-diff}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# =============================================================================
# Helper Functions
# =============================================================================
log_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

cleanup() {
  log_info "Cleaning up temporary containers..."
  docker rm -f diff_live_container diff_target_container 2>/dev/null || true
  rm -f "$OUTPUT_DIR/live.tar" "$OUTPUT_DIR/target.tar" 2>/dev/null || true
}

trap cleanup EXIT

# =============================================================================
# Validation
# =============================================================================
if [ -z "$IMAGE_LIVE" ] || [ -z "$IMAGE_TARGET" ]; then
  log_error "Usage: $0 <live_image> <target_image> [output_dir]"
  exit 1
fi

if ! command -v docker &> /dev/null; then
  log_error "Docker is not installed or not in PATH"
  exit 1
fi

# =============================================================================
# Setup
# =============================================================================
log_info "=== Docker Image Diff ==="
log_info "Live image:   $IMAGE_LIVE"
log_info "Target image: $IMAGE_TARGET"
log_info "Output dir:   $OUTPUT_DIR"
log_info "Timestamp:    $TIMESTAMP"
echo ""

mkdir -p "$OUTPUT_DIR"/{history,filesystem,runtime,summary}

# =============================================================================
# Step 1: Pull Images
# =============================================================================
log_info ">>> Step 1: Pulling images..."

docker pull "$IMAGE_LIVE" || {
  log_error "Failed to pull live image: $IMAGE_LIVE"
  exit 1
}

docker pull "$IMAGE_TARGET" || {
  log_error "Failed to pull target image: $IMAGE_TARGET"
  exit 1
}

echo ""

# =============================================================================
# Step 2: Image Metadata
# =============================================================================
log_info ">>> Step 2: Extracting image metadata..."

# Image IDs and digests
docker inspect --format='{{.Id}}' "$IMAGE_LIVE" > "$OUTPUT_DIR/summary/live.id.txt"
docker inspect --format='{{.Id}}' "$IMAGE_TARGET" > "$OUTPUT_DIR/summary/target.id.txt"

docker inspect --format='{{json .RepoDigests}}' "$IMAGE_LIVE" > "$OUTPUT_DIR/summary/live.digest.json"
docker inspect --format='{{json .RepoDigests}}' "$IMAGE_TARGET" > "$OUTPUT_DIR/summary/target.digest.json"

# Full inspect
docker inspect "$IMAGE_LIVE" > "$OUTPUT_DIR/summary/live.inspect.json"
docker inspect "$IMAGE_TARGET" > "$OUTPUT_DIR/summary/target.inspect.json"

# Size comparison
LIVE_SIZE=$(docker inspect --format='{{.Size}}' "$IMAGE_LIVE")
TARGET_SIZE=$(docker inspect --format='{{.Size}}' "$IMAGE_TARGET")
LIVE_SIZE_MB=$((LIVE_SIZE / 1024 / 1024))
TARGET_SIZE_MB=$((TARGET_SIZE / 1024 / 1024))
SIZE_DIFF_MB=$((TARGET_SIZE_MB - LIVE_SIZE_MB))

cat > "$OUTPUT_DIR/summary/size.txt" << EOF
Live Image Size:   ${LIVE_SIZE_MB} MB
Target Image Size: ${TARGET_SIZE_MB} MB
Difference:        ${SIZE_DIFF_MB} MB
EOF

log_info "Live size: ${LIVE_SIZE_MB}MB, Target size: ${TARGET_SIZE_MB}MB (diff: ${SIZE_DIFF_MB}MB)"
echo ""

# =============================================================================
# Step 3: Layer History Diff
# =============================================================================
log_info ">>> Step 3: Comparing layer history..."

docker history --no-trunc "$IMAGE_LIVE" > "$OUTPUT_DIR/history/live.history.txt"
docker history --no-trunc "$IMAGE_TARGET" > "$OUTPUT_DIR/history/target.history.txt"

diff -u "$OUTPUT_DIR/history/live.history.txt" "$OUTPUT_DIR/history/target.history.txt" \
  > "$OUTPUT_DIR/history/history.diff" 2>&1 || true

LAYER_COUNT_LIVE=$(docker history -q "$IMAGE_LIVE" | wc -l)
LAYER_COUNT_TARGET=$(docker history -q "$IMAGE_TARGET" | wc -l)

log_info "Live layers: $LAYER_COUNT_LIVE, Target layers: $LAYER_COUNT_TARGET"
echo ""

# =============================================================================
# Step 4: Runtime Diff (pip, odoo, env)
# =============================================================================
log_info ">>> Step 4: Comparing runtime environment..."

# Pip packages
docker run --rm "$IMAGE_LIVE" pip list --format=freeze 2>/dev/null | sort > "$OUTPUT_DIR/runtime/live.pip.txt" || true
docker run --rm "$IMAGE_TARGET" pip list --format=freeze 2>/dev/null | sort > "$OUTPUT_DIR/runtime/target.pip.txt" || true

diff -u "$OUTPUT_DIR/runtime/live.pip.txt" "$OUTPUT_DIR/runtime/target.pip.txt" \
  > "$OUTPUT_DIR/runtime/pip.diff" 2>&1 || true

# Count pip changes
PIP_ADDED=$(diff "$OUTPUT_DIR/runtime/live.pip.txt" "$OUTPUT_DIR/runtime/target.pip.txt" | grep '^>' | wc -l || echo "0")
PIP_REMOVED=$(diff "$OUTPUT_DIR/runtime/live.pip.txt" "$OUTPUT_DIR/runtime/target.pip.txt" | grep '^<' | wc -l || echo "0")

log_info "Pip packages: +$PIP_ADDED added, -$PIP_REMOVED removed"

# Odoo version
docker run --rm "$IMAGE_LIVE" odoo --version 2>/dev/null > "$OUTPUT_DIR/runtime/live.odoo-version.txt" || echo "Unknown" > "$OUTPUT_DIR/runtime/live.odoo-version.txt"
docker run --rm "$IMAGE_TARGET" odoo --version 2>/dev/null > "$OUTPUT_DIR/runtime/target.odoo-version.txt" || echo "Unknown" > "$OUTPUT_DIR/runtime/target.odoo-version.txt"

diff -u "$OUTPUT_DIR/runtime/live.odoo-version.txt" "$OUTPUT_DIR/runtime/target.odoo-version.txt" \
  > "$OUTPUT_DIR/runtime/odoo-version.diff" 2>&1 || true

# Environment variables
docker run --rm "$IMAGE_LIVE" env 2>/dev/null | sort > "$OUTPUT_DIR/runtime/live.env.txt" || true
docker run --rm "$IMAGE_TARGET" env 2>/dev/null | sort > "$OUTPUT_DIR/runtime/target.env.txt" || true

diff -u "$OUTPUT_DIR/runtime/live.env.txt" "$OUTPUT_DIR/runtime/target.env.txt" \
  > "$OUTPUT_DIR/runtime/env.diff" 2>&1 || true

echo ""

# =============================================================================
# Step 5: Filesystem Diff (targeted paths)
# =============================================================================
log_info ">>> Step 5: Comparing filesystem (targeted paths)..."

# Create containers
docker create --name diff_live_container "$IMAGE_LIVE" >/dev/null
docker create --name diff_target_container "$IMAGE_TARGET" >/dev/null

# Export specific directories instead of full filesystem (faster)
mkdir -p "$OUTPUT_DIR/filesystem/live" "$OUTPUT_DIR/filesystem/target"

# Copy key directories
DIFF_PATHS=(
  "/mnt/extra-addons"
  "/etc/odoo"
  "/usr/lib/python3/dist-packages/odoo"
)

for path in "${DIFF_PATHS[@]}"; do
  path_safe=$(echo "$path" | tr '/' '_')

  # Extract from live
  docker cp "diff_live_container:$path" "$OUTPUT_DIR/filesystem/live/$path_safe" 2>/dev/null || {
    log_warn "Path not found in live: $path"
    mkdir -p "$OUTPUT_DIR/filesystem/live/$path_safe"
  }

  # Extract from target
  docker cp "diff_target_container:$path" "$OUTPUT_DIR/filesystem/target/$path_safe" 2>/dev/null || {
    log_warn "Path not found in target: $path"
    mkdir -p "$OUTPUT_DIR/filesystem/target/$path_safe"
  }
done

# Generate filesystem diffs
for path in "${DIFF_PATHS[@]}"; do
  path_safe=$(echo "$path" | tr '/' '_')

  diff -ruN \
    "$OUTPUT_DIR/filesystem/live/$path_safe" \
    "$OUTPUT_DIR/filesystem/target/$path_safe" \
    > "$OUTPUT_DIR/filesystem/${path_safe}.diff" 2>&1 || true

  # Count changes
  CHANGES=$(grep -c '^[+-]' "$OUTPUT_DIR/filesystem/${path_safe}.diff" 2>/dev/null || echo "0")
  log_info "  $path: $CHANGES lines changed"
done

# Odoo config diff specifically
if [ -f "$OUTPUT_DIR/filesystem/live/_etc_odoo/odoo.conf" ] && [ -f "$OUTPUT_DIR/filesystem/target/_etc_odoo/odoo.conf" ]; then
  diff -u \
    "$OUTPUT_DIR/filesystem/live/_etc_odoo/odoo.conf" \
    "$OUTPUT_DIR/filesystem/target/_etc_odoo/odoo.conf" \
    > "$OUTPUT_DIR/filesystem/odoo.conf.diff" 2>&1 || true
fi

echo ""

# =============================================================================
# Step 6: Generate Summary Report
# =============================================================================
log_info ">>> Step 6: Generating summary report..."

cat > "$OUTPUT_DIR/summary/DIFF_REPORT.md" << EOF
# Docker Image Diff Report

**Generated:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")

## Images Compared

| Property | Live | Target |
|----------|------|--------|
| Image | \`$IMAGE_LIVE\` | \`$IMAGE_TARGET\` |
| Size | ${LIVE_SIZE_MB} MB | ${TARGET_SIZE_MB} MB |
| Layers | $LAYER_COUNT_LIVE | $LAYER_COUNT_TARGET |

**Size Difference:** ${SIZE_DIFF_MB} MB

## Summary

### Pip Packages
- **Added:** $PIP_ADDED packages
- **Removed:** $PIP_REMOVED packages

### Layer Changes
\`\`\`
$(head -30 "$OUTPUT_DIR/history/history.diff" 2>/dev/null || echo "No layer changes")
\`\`\`

### Pip Package Changes
\`\`\`
$(head -50 "$OUTPUT_DIR/runtime/pip.diff" 2>/dev/null || echo "No pip changes")
\`\`\`

### Odoo Version
- **Live:** $(cat "$OUTPUT_DIR/runtime/live.odoo-version.txt")
- **Target:** $(cat "$OUTPUT_DIR/runtime/target.odoo-version.txt")

### Config Changes
\`\`\`
$(head -30 "$OUTPUT_DIR/filesystem/odoo.conf.diff" 2>/dev/null || echo "No config changes")
\`\`\`

## Files Generated

- \`history/\` - Layer history comparison
- \`runtime/\` - Pip, Odoo version, env diffs
- \`filesystem/\` - Targeted path diffs
- \`summary/\` - This report and metadata

## Verification Commands

\`\`\`bash
# Smoke test target image
docker run --rm $IMAGE_TARGET odoo --version

# DB connection test (replace env vars)
docker run --rm \\
  -e DB_HOST="\$DB_HOST" \\
  -e DB_PORT="\$DB_PORT" \\
  -e DB_USER="\$DB_USER" \\
  -e DB_PASSWORD="\$DB_PASSWORD" \\
  $IMAGE_TARGET \\
  odoo -d \$ODOO_DB --log-level=info --stop-after-init
\`\`\`
EOF

# Generate JSON summary for machine consumption
cat > "$OUTPUT_DIR/summary/diff_summary.json" << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "live_image": "$IMAGE_LIVE",
  "target_image": "$IMAGE_TARGET",
  "live_size_mb": $LIVE_SIZE_MB,
  "target_size_mb": $TARGET_SIZE_MB,
  "size_diff_mb": $SIZE_DIFF_MB,
  "live_layers": $LAYER_COUNT_LIVE,
  "target_layers": $LAYER_COUNT_TARGET,
  "pip_added": $PIP_ADDED,
  "pip_removed": $PIP_REMOVED
}
EOF

echo ""
log_info "=== Diff Complete ==="
log_info "Report: $OUTPUT_DIR/summary/DIFF_REPORT.md"
log_info "JSON:   $OUTPUT_DIR/summary/diff_summary.json"
echo ""

# Output summary to stdout
cat "$OUTPUT_DIR/summary/DIFF_REPORT.md"
