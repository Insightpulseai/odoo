#!/usr/bin/env bash
# Export architecture diagrams to SVG and PNG formats
#
# Usage:
#   ./scripts/export_architecture_diagrams.sh           # Export all diagrams
#   ./scripts/export_architecture_diagrams.sh --check   # Check for drift (CI mode)
#   ./scripts/export_architecture_diagrams.sh --single FILE.drawio  # Export single file
#
# Requirements:
#   - Docker (uses rlespinasse/drawio-export image)
#   - OR: drawio CLI installed locally
#
# Output:
#   docs/architecture/exports/*.svg
#   docs/architecture/exports/*.png

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_DIR="$REPO_ROOT/docs/architecture"
EXPORT_DIR="$REPO_ROOT/docs/architecture/exports"
DRAWIO_IMAGE="rlespinasse/drawio-export:latest"
PNG_SCALE=2  # Export at 2x resolution

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

usage() {
    cat <<EOF
Export architecture diagrams to SVG and PNG

Usage: $0 [OPTIONS]

Options:
    --check         Check for export drift (CI mode)
    --single FILE   Export a single .drawio file
    --local         Use local drawio-desktop instead of Docker
    --help          Show this help

Examples:
    $0                                    # Export all diagrams
    $0 --check                            # Verify exports are up to date
    $0 --single ipai_idp_architecture.drawio
EOF
    exit 0
}

# Parse arguments
CHECK_MODE=false
SINGLE_FILE=""
USE_LOCAL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --check)
            CHECK_MODE=true
            shift
            ;;
        --single)
            SINGLE_FILE="$2"
            shift 2
            ;;
        --local)
            USE_LOCAL=true
            shift
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Ensure export directory exists
mkdir -p "$EXPORT_DIR"

# Find .drawio files
find_diagrams() {
    if [[ -n "$SINGLE_FILE" ]]; then
        if [[ -f "$SOURCE_DIR/$SINGLE_FILE" ]]; then
            echo "$SOURCE_DIR/$SINGLE_FILE"
        else
            echo -e "${RED}File not found: $SINGLE_FILE${NC}" >&2
            exit 1
        fi
    else
        find "$SOURCE_DIR" -maxdepth 1 -name "*.drawio" -type f
    fi
}

# Export using Docker
export_with_docker() {
    local input_file="$1"
    local basename
    basename=$(basename "$input_file" .drawio)

    echo "  Exporting: $basename"

    # Export to SVG
    docker run --rm \
        -v "$SOURCE_DIR:/data" \
        "$DRAWIO_IMAGE" \
        --format svg \
        --output "/data/exports/${basename}.svg" \
        "/data/$(basename "$input_file")" 2>/dev/null || {
        echo -e "${YELLOW}    SVG export failed, trying alternate method${NC}"
        return 1
    }

    # Export to PNG
    docker run --rm \
        -v "$SOURCE_DIR:/data" \
        "$DRAWIO_IMAGE" \
        --format png \
        --scale "$PNG_SCALE" \
        --output "/data/exports/${basename}.png" \
        "/data/$(basename "$input_file")" 2>/dev/null || {
        echo -e "${YELLOW}    PNG export failed${NC}"
        return 1
    }

    echo -e "${GREEN}    Exported: ${basename}.svg, ${basename}.png${NC}"
}

# Export using local drawio CLI
export_with_local() {
    local input_file="$1"
    local basename
    basename=$(basename "$input_file" .drawio)

    echo "  Exporting: $basename"

    if ! command -v drawio &> /dev/null; then
        echo -e "${RED}drawio CLI not found. Install drawio-desktop or use Docker mode.${NC}"
        return 1
    fi

    # Export to SVG
    drawio --export --format svg \
        --output "$EXPORT_DIR/${basename}.svg" \
        "$input_file" 2>/dev/null

    # Export to PNG
    drawio --export --format png \
        --scale "$PNG_SCALE" \
        --output "$EXPORT_DIR/${basename}.png" \
        "$input_file" 2>/dev/null

    echo -e "${GREEN}    Exported: ${basename}.svg, ${basename}.png${NC}"
}

# Main export function
export_diagrams() {
    local diagrams
    diagrams=$(find_diagrams)

    if [[ -z "$diagrams" ]]; then
        echo -e "${YELLOW}No .drawio files found in $SOURCE_DIR${NC}"
        exit 0
    fi

    echo "Exporting architecture diagrams..."
    echo "Source: $SOURCE_DIR"
    echo "Output: $EXPORT_DIR"
    echo ""

    local count=0
    local failed=0

    while IFS= read -r diagram; do
        if [[ "$USE_LOCAL" == "true" ]]; then
            export_with_local "$diagram" || ((failed++))
        else
            export_with_docker "$diagram" || {
                echo -e "${YELLOW}  Falling back to local export${NC}"
                export_with_local "$diagram" || ((failed++))
            }
        fi
        ((count++))
    done <<< "$diagrams"

    echo ""
    echo -e "${GREEN}Exported $count diagram(s)${NC}"

    if [[ $failed -gt 0 ]]; then
        echo -e "${YELLOW}$failed export(s) failed${NC}"
        return 1
    fi
}

# Check for drift (CI mode)
check_drift() {
    echo "Checking for export drift..."

    # First, export all diagrams
    export_diagrams

    # Then check git diff
    cd "$REPO_ROOT"

    if git diff --exit-code "$EXPORT_DIR" > /dev/null 2>&1; then
        echo -e "${GREEN}No drift detected. Exports are up to date.${NC}"
        exit 0
    else
        echo -e "${RED}Drift detected! Exported files differ from committed versions.${NC}"
        echo ""
        echo "Changed files:"
        git diff --name-only "$EXPORT_DIR"
        echo ""
        echo "Run './scripts/export_architecture_diagrams.sh' locally and commit the updated exports."
        exit 1
    fi
}

# Generate manifest of diagrams and their hashes
generate_manifest() {
    local manifest="$EXPORT_DIR/MANIFEST.json"

    echo "{"
    echo "  \"generated_at\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\","
    echo "  \"diagrams\": ["

    local first=true
    for svg in "$EXPORT_DIR"/*.svg; do
        if [[ -f "$svg" ]]; then
            local name
            name=$(basename "$svg" .svg)
            local svg_hash
            svg_hash=$(sha256sum "$svg" | cut -d' ' -f1)
            local png_hash=""
            if [[ -f "$EXPORT_DIR/${name}.png" ]]; then
                png_hash=$(sha256sum "$EXPORT_DIR/${name}.png" | cut -d' ' -f1)
            fi

            if [[ "$first" == "true" ]]; then
                first=false
            else
                echo ","
            fi

            echo -n "    {\"name\": \"$name\", \"svg_sha256\": \"$svg_hash\", \"png_sha256\": \"$png_hash\"}"
        fi
    done

    echo ""
    echo "  ]"
    echo "}"
}

# Main
if [[ "$CHECK_MODE" == "true" ]]; then
    check_drift
else
    export_diagrams

    # Generate manifest
    generate_manifest > "$EXPORT_DIR/MANIFEST.json"
    echo "Generated: $EXPORT_DIR/MANIFEST.json"
fi
