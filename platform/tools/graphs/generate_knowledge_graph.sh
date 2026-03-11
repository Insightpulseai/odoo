#!/usr/bin/env bash
set -euo pipefail

# Generate Knowledge Graph with HTML Viewer
# Wraps Python knowledge graph generator

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

OUTPUT_DIR="out/graphs/knowledge"
TEMPLATES_DIR="tools/graphs/templates"
GENERATOR="tools/graphs/generate_knowledge_graph.py"

# Parse arguments
NO_OPEN=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-open)
      NO_OPEN=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--no-open]"
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

if [[ ! -f "$GENERATOR" ]]; then
  echo "ERROR: Knowledge graph generator not found: $GENERATOR"
  exit 1
fi

# Run Python generator
python3 "$GENERATOR"

# Check if SVG was generated
if [[ ! -f "$OUTPUT_DIR/knowledge_graph.svg" ]]; then
  echo "ERROR: SVG generation failed"
  exit 1
fi

echo ""
echo "==> Generating HTML viewer..."

# Generate HTML viewer
HTML_TEMPLATE="$TEMPLATES_DIR/knowledge_viewer.html"
HTML_OUTPUT="$OUTPUT_DIR/index.html"

if [[ ! -f "$HTML_TEMPLATE" ]]; then
  echo "ERROR: HTML template not found: $HTML_TEMPLATE"
  exit 1
fi

# Replace SVG file reference in template
sed "s|__SVG_FILE__|knowledge_graph.svg|g" "$HTML_TEMPLATE" > "$HTML_OUTPUT"

echo ""
echo "✅ Knowledge graph viewer generated successfully!"
echo ""
echo "Output files:"
echo "  - DOT: $OUTPUT_DIR/knowledge_graph.dot"
echo "  - SVG: $OUTPUT_DIR/knowledge_graph.svg"
echo "  - PNG: $OUTPUT_DIR/knowledge_graph.png"
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
