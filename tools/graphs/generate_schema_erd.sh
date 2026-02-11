#!/usr/bin/env bash
set -euo pipefail

# Generate Schema ERD with HTML Viewer
# Wraps existing generate_erd_graphviz.py script

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

OUTPUT_DIR="out/graphs/schema"
TEMPLATES_DIR="tools/graphs/templates"
SCRIPT="scripts/generate_erd_graphviz.py"

# Parse arguments
FILTER=""
NO_OPEN=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --filter)
      FILTER="$2"
      shift 2
      ;;
    --no-open)
      NO_OPEN=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--filter PREFIX] [--no-open]"
      exit 1
      ;;
  esac
done

# Check dependencies
if ! command -v dot &>/dev/null; then
  echo "ERROR: Graphviz 'dot' command not found"
  echo "Install with: brew install graphviz"
  exit 1
fi

if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 not found"
  exit 1
fi

if [[ ! -f "$SCRIPT" ]]; then
  echo "ERROR: ERD generator script not found: $SCRIPT"
  exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "==> Generating Schema ERD..."

# Run existing ERD generator (outputs to its own directory structure)
if [[ -n "$FILTER" ]]; then
  echo "    Filter: $FILTER"
  python3 "$SCRIPT" --format svg --output-dir "$OUTPUT_DIR" --filter "$FILTER"
  # Find the generated SVG file (e.g., ODOO_ERD_ipai.svg)
  SVG_FILE=$(find "$OUTPUT_DIR" -name "ODOO_ERD_*.svg" -type f | head -1)
  if [[ -z "$SVG_FILE" ]]; then
    echo "ERROR: No SVG file found after generation"
    exit 1
  fi
  SVG_FILE=$(basename "$SVG_FILE")
else
  echo "    Generating full schema (all tables) - this may take a while..."
  echo "    TIP: Use --filter ipai_ for faster results"
  python3 "$SCRIPT" --format svg --output-dir "$OUTPUT_DIR"
  # Find the generated SVG file
  SVG_FILE=$(find "$OUTPUT_DIR" -name "ODOO_ERD*.svg" -type f | head -1)
  if [[ -z "$SVG_FILE" ]]; then
    echo "ERROR: No SVG file found after generation"
    exit 1
  fi
  SVG_FILE=$(basename "$SVG_FILE")
fi

echo "    Generated: $SVG_FILE"

echo "==> Generating HTML viewer..."

# Generate HTML viewer
HTML_TEMPLATE="$TEMPLATES_DIR/erd_viewer.html"
HTML_OUTPUT="$OUTPUT_DIR/index.html"

if [[ ! -f "$HTML_TEMPLATE" ]]; then
  echo "ERROR: HTML template not found: $HTML_TEMPLATE"
  exit 1
fi

# Replace SVG file reference in template
sed "s|__SVG_FILE__|$SVG_FILE|g" "$HTML_TEMPLATE" > "$HTML_OUTPUT"

echo ""
echo "✅ Schema ERD generated successfully!"
echo ""
echo "Output files:"
echo "  - SVG: $OUTPUT_DIR/$SVG_FILE"
echo "  - HTML: $OUTPUT_DIR/index.html"
echo ""
echo "Open in browser:"
echo "  file://$REPO_ROOT/$OUTPUT_DIR/index.html"
echo ""

# Try to open in browser automatically (macOS)
if [[ "$NO_OPEN" != true ]] && command -v open &>/dev/null; then
  echo "Opening in browser..."
  open "$OUTPUT_DIR/index.html"
fi
