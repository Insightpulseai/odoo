#!/usr/bin/env bash
# Generate complete audit bundle
set -euo pipefail

AUDIT_DIR="${1:-audit}"
mkdir -p "$AUDIT_DIR"

echo "=== Generating Audit Bundle ==="

# Generate snapshot
bash tools/audit/snapshot.sh "$AUDIT_DIR"

# Generate snapshot JSON
bash tools/audit/gen_snapshot_json.sh "$AUDIT_DIR/snapshot.json"

# Generate repo tree
bash tools/audit/gen_repo_tree.sh . "$AUDIT_DIR/repo_tree.md"

# Verify expected paths
bash tools/audit/verify_expected_paths.sh

echo ""
echo "=== Audit bundle generated under ./$AUDIT_DIR/ ==="
ls -la "$AUDIT_DIR/"
