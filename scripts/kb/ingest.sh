#!/usr/bin/env bash
# Knowledge Base Ingestion Pipeline
#
# Usage:
#   ./scripts/kb/ingest.sh discover              # List discoverable docs
#   ./scripts/kb/ingest.sh ingest --dry-run      # Chunk without indexing
#   ./scripts/kb/ingest.sh ingest --full          # Full re-ingestion
#   ./scripts/kb/ingest.sh manifest               # Show index manifest
#   ./scripts/kb/ingest.sh eval                   # Run retrieval eval
#
# Required env vars for live indexing:
#   AZURE_SEARCH_ENDPOINT    (e.g. https://srch-ipai-dev.search.windows.net)
#   AZURE_SEARCH_API_KEY     (admin key from Azure portal)
#   AZURE_OPENAI_ENDPOINT    (e.g. https://oai-ipai-dev.openai.azure.com)
#   AZURE_OPENAI_API_KEY     (API key)
#
# Dry-run mode does NOT require Azure credentials.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
KB_PKG="${REPO_ROOT}/packages/odoo-docs-kb"

# Add package parent to PYTHONPATH so relative imports work
# We symlink-trick: run via python -c with sys.path injection
exec python3 -c "
import sys, os
sys.path.insert(0, '${KB_PKG}')
os.chdir('${REPO_ROOT}')

# Re-create the package context for relative imports
import importlib, types
pkg = types.ModuleType('odoo_docs_kb')
pkg.__path__ = ['${KB_PKG}']
pkg.__package__ = 'odoo_docs_kb'
sys.modules['odoo_docs_kb'] = pkg

# Now import and run
sys.argv = ['kb-ingest'] + sys.argv[1:]
from odoo_docs_kb.cli import main
main()
" "$@"
