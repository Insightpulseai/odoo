#!/usr/bin/env bash
set -euo pipefail

# Generate all graphs (Schema ERD + Knowledge Graph)

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

SCHEMA_SCRIPT="tools/graphs/generate_schema_erd.sh"
KNOWLEDGE_SCRIPT="tools/graphs/generate_knowledge_graph.sh"

echo "╔════════════════════════════════════════════╗"
echo "║  Odoo Repository Graph Generator           ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Generate Schema ERD
echo "1/2 - Generating Schema ERD..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [[ -f "$SCHEMA_SCRIPT" ]]; then
  bash "$SCHEMA_SCRIPT" --no-open || echo "Warning: Schema ERD generation failed"
else
  echo "ERROR: Schema ERD script not found: $SCHEMA_SCRIPT"
fi

echo ""

# Generate Knowledge Graph
echo "2/2 - Generating Knowledge Graph..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [[ -f "$KNOWLEDGE_SCRIPT" ]]; then
  bash "$KNOWLEDGE_SCRIPT" --no-open || echo "Warning: Knowledge graph generation failed"
else
  echo "ERROR: Knowledge graph script not found: $KNOWLEDGE_SCRIPT"
fi

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║  ✅ All graphs generated successfully!     ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Open viewers:"
echo "  Schema ERD:       file://$REPO_ROOT/out/graphs/schema/index.html"
echo "  Knowledge Graph:  file://$REPO_ROOT/out/graphs/knowledge/index.html"
echo ""

# Try to open both in browser (macOS)
if command -v open &>/dev/null; then
  echo "Opening in browser..."
  open "out/graphs/schema/index.html" 2>/dev/null || true
  open "out/graphs/knowledge/index.html" 2>/dev/null || true
fi
