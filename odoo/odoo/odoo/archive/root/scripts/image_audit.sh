#!/bin/bash
# =============================================================================
# Image Audit Script - SBOM, Vulnerability Scan, and Image Diff
# =============================================================================
# Generates audit artifacts for Docker images:
#   - SBOM (Software Bill of Materials) via syft
#   - Vulnerability report via grype
#   - Image diff vs base image via container-diff
#   - Layer history comparison
#
# Usage:
#   ./scripts/image_audit.sh <custom-image> [base-image]
#   ./scripts/image_audit.sh ghcr.io/jgtolentino/odoo-ce:18.0-abc1234
#   ./scripts/image_audit.sh ghcr.io/jgtolentino/odoo-ce:18.0 odoo:18.0
#
# Output:
#   image_audit/
#   ├── sbom.base.json          # SBOM of base image
#   ├── sbom.custom.json        # SBOM of custom image
#   ├── vulns.base.json         # Vulnerabilities in base image
#   ├── vulns.custom.json       # Vulnerabilities in custom image
#   ├── vulns.summary.txt       # Human-readable vulnerability summary
#   ├── image_diff.json         # File/package differences
#   ├── history.base.txt        # Layer history of base image
#   ├── history.custom.txt      # Layer history of custom image
#   ├── history.diff            # Unified diff of histories
#   └── audit_summary.md        # Summary report
#
# Requirements:
#   - syft (https://github.com/anchore/syft)
#   - grype (https://github.com/anchore/grype)
#   - container-diff (https://github.com/GoogleContainerTools/container-diff)
#   - docker
#
# =============================================================================

set -euo pipefail

# Configuration
CUSTOM_IMAGE="${1:?ERROR: Custom image required. Usage: $0 <custom-image> [base-image]}"
BASE_IMAGE="${2:-odoo:18.0}"
OUTPUT_DIR="${OUTPUT_DIR:-image_audit}"
ARCHIVE_NAME="${ARCHIVE_NAME:-image_audit.tgz}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check for required tools
check_deps() {
    local missing=()

    if ! command -v syft &> /dev/null; then
        missing+=("syft")
    fi
    if ! command -v grype &> /dev/null; then
        missing+=("grype")
    fi
    if ! command -v container-diff &> /dev/null; then
        missing+=("container-diff")
    fi
    if ! command -v docker &> /dev/null; then
        missing+=("docker")
    fi

    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing[*]}"
        echo ""
        echo "Install instructions:"
        echo "  syft:           curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin"
        echo "  grype:          curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin"
        echo "  container-diff: curl -LO https://storage.googleapis.com/container-diff/latest/container-diff-linux-amd64 && chmod +x container-diff-linux-amd64 && mv container-diff-linux-amd64 /usr/local/bin/container-diff"
        exit 1
    fi

    log_success "All required tools available"
}

# Pull images if needed
pull_images() {
    log_info "Ensuring images are available..."

    if ! docker image inspect "$BASE_IMAGE" &>/dev/null; then
        log_info "Pulling base image: $BASE_IMAGE"
        docker pull "$BASE_IMAGE"
    fi

    if ! docker image inspect "$CUSTOM_IMAGE" &>/dev/null; then
        log_info "Pulling custom image: $CUSTOM_IMAGE"
        docker pull "$CUSTOM_IMAGE"
    fi

    log_success "Images available"
}

# Generate SBOM
generate_sbom() {
    log_info "Generating SBOM for base image..."
    syft "$BASE_IMAGE" -o json > "$OUTPUT_DIR/sbom.base.json" 2>/dev/null
    log_success "Base SBOM: $OUTPUT_DIR/sbom.base.json"

    log_info "Generating SBOM for custom image..."
    syft "$CUSTOM_IMAGE" -o json > "$OUTPUT_DIR/sbom.custom.json" 2>/dev/null
    log_success "Custom SBOM: $OUTPUT_DIR/sbom.custom.json"
}

# Run vulnerability scan
scan_vulnerabilities() {
    log_info "Scanning base image for vulnerabilities..."
    grype "$BASE_IMAGE" -o json > "$OUTPUT_DIR/vulns.base.json" 2>/dev/null
    log_success "Base vulns: $OUTPUT_DIR/vulns.base.json"

    log_info "Scanning custom image for vulnerabilities..."
    grype "$CUSTOM_IMAGE" -o json > "$OUTPUT_DIR/vulns.custom.json" 2>/dev/null
    log_success "Custom vulns: $OUTPUT_DIR/vulns.custom.json"

    # Generate human-readable summary
    log_info "Generating vulnerability summary..."
    {
        echo "Vulnerability Summary"
        echo "====================="
        echo ""
        echo "Base Image: $BASE_IMAGE"
        echo "Custom Image: $CUSTOM_IMAGE"
        echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo ""
        echo "Base Image Vulnerabilities:"
        echo "---------------------------"
        if command -v jq &>/dev/null; then
            jq -r '.matches | group_by(.vulnerability.severity) | map({severity: .[0].vulnerability.severity, count: length}) | sort_by(.severity) | .[] | "  \(.severity): \(.count)"' "$OUTPUT_DIR/vulns.base.json" 2>/dev/null || echo "  (unable to parse)"
        else
            echo "  (jq not available for parsing)"
        fi
        echo ""
        echo "Custom Image Vulnerabilities:"
        echo "-----------------------------"
        if command -v jq &>/dev/null; then
            jq -r '.matches | group_by(.vulnerability.severity) | map({severity: .[0].vulnerability.severity, count: length}) | sort_by(.severity) | .[] | "  \(.severity): \(.count)"' "$OUTPUT_DIR/vulns.custom.json" 2>/dev/null || echo "  (unable to parse)"
        else
            echo "  (jq not available for parsing)"
        fi
    } > "$OUTPUT_DIR/vulns.summary.txt"
    log_success "Vulnerability summary: $OUTPUT_DIR/vulns.summary.txt"
}

# Generate image diff
generate_diff() {
    log_info "Generating image diff (this may take a while)..."

    # Use container-diff for file and package differences
    container-diff diff \
        "daemon://$BASE_IMAGE" \
        "daemon://$CUSTOM_IMAGE" \
        --type=file \
        --type=apt \
        --type=pip \
        -j > "$OUTPUT_DIR/image_diff.json" 2>/dev/null || {
            log_warn "container-diff failed, generating basic diff..."
            echo '{"error": "container-diff failed", "base": "'"$BASE_IMAGE"'", "custom": "'"$CUSTOM_IMAGE"'"}' > "$OUTPUT_DIR/image_diff.json"
        }

    log_success "Image diff: $OUTPUT_DIR/image_diff.json"
}

# Generate layer history
generate_history() {
    log_info "Capturing layer history..."

    docker history --no-trunc "$BASE_IMAGE" > "$OUTPUT_DIR/history.base.txt" 2>/dev/null
    docker history --no-trunc "$CUSTOM_IMAGE" > "$OUTPUT_DIR/history.custom.txt" 2>/dev/null

    # Generate unified diff
    diff -u "$OUTPUT_DIR/history.base.txt" "$OUTPUT_DIR/history.custom.txt" > "$OUTPUT_DIR/history.diff" 2>/dev/null || true

    log_success "History files generated"
}

# Generate summary report
generate_summary() {
    log_info "Generating audit summary..."

    local base_size custom_size size_diff
    base_size=$(docker image inspect "$BASE_IMAGE" --format='{{.Size}}' 2>/dev/null || echo "0")
    custom_size=$(docker image inspect "$CUSTOM_IMAGE" --format='{{.Size}}' 2>/dev/null || echo "0")
    size_diff=$((custom_size - base_size))

    # Convert to human-readable
    base_size_mb=$((base_size / 1024 / 1024))
    custom_size_mb=$((custom_size / 1024 / 1024))
    size_diff_mb=$((size_diff / 1024 / 1024))

    cat > "$OUTPUT_DIR/audit_summary.md" << EOF
# Image Audit Summary

**Generated:** $(date -u +%Y-%m-%dT%H:%M:%SZ)

## Images

| Property | Base Image | Custom Image |
|----------|------------|--------------|
| Reference | \`$BASE_IMAGE\` | \`$CUSTOM_IMAGE\` |
| Size | ${base_size_mb} MB | ${custom_size_mb} MB |
| Size Delta | - | +${size_diff_mb} MB |

## Artifacts Generated

| Artifact | Description |
|----------|-------------|
| sbom.base.json | Software Bill of Materials for base image |
| sbom.custom.json | Software Bill of Materials for custom image |
| vulns.base.json | Vulnerability scan of base image |
| vulns.custom.json | Vulnerability scan of custom image |
| vulns.summary.txt | Human-readable vulnerability summary |
| image_diff.json | File/package differences between images |
| history.base.txt | Layer history of base image |
| history.custom.txt | Layer history of custom image |
| history.diff | Unified diff of layer histories |

## Vulnerability Summary

$(cat "$OUTPUT_DIR/vulns.summary.txt" | sed 's/^/> /')

## File Structure Changes

The \`image_diff.json\` contains detailed file and package changes.
Key changes are typically in:

- \`/mnt/odoo/addons/ipai\` - IPAI custom modules
- \`/mnt/odoo/addons/oca\` - OCA modules
- \`/etc/odoo/odoo.conf\` - Configuration
- \`/entrypoint.d/\` - Entrypoint hooks

## Notes

- SBOM generated with [syft](https://github.com/anchore/syft)
- Vulnerabilities scanned with [grype](https://github.com/anchore/grype)
- Image diff generated with [container-diff](https://github.com/GoogleContainerTools/container-diff)

---
*This report is auto-generated by \`scripts/image_audit.sh\`*
EOF

    log_success "Audit summary: $OUTPUT_DIR/audit_summary.md"
}

# Create archive
create_archive() {
    log_info "Creating archive: $ARCHIVE_NAME"
    tar -czf "$ARCHIVE_NAME" -C "$(dirname "$OUTPUT_DIR")" "$(basename "$OUTPUT_DIR")"
    log_success "Archive created: $ARCHIVE_NAME ($(du -h "$ARCHIVE_NAME" | cut -f1))"
}

# Main execution
main() {
    echo ""
    echo "============================================="
    echo "  IPAI Odoo CE Image Audit"
    echo "============================================="
    echo "  Base Image:   $BASE_IMAGE"
    echo "  Custom Image: $CUSTOM_IMAGE"
    echo "  Output:       $OUTPUT_DIR/"
    echo "============================================="
    echo ""

    check_deps

    # Prepare output directory
    rm -rf "$OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"

    pull_images
    generate_sbom
    scan_vulnerabilities
    generate_diff
    generate_history
    generate_summary
    create_archive

    echo ""
    echo "============================================="
    log_success "AUDIT COMPLETE"
    echo "============================================="
    echo "  Output Directory: $OUTPUT_DIR/"
    echo "  Archive:          $ARCHIVE_NAME"
    echo ""
    echo "  View summary:     cat $OUTPUT_DIR/audit_summary.md"
    echo "  View vulns:       cat $OUTPUT_DIR/vulns.summary.txt"
    echo "============================================="
    echo ""
}

main "$@"
