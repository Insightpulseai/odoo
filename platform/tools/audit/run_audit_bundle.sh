#!/usr/bin/env bash
# Generate complete audit bundle
# This script generates all audit artifacts for CI and documentation
set -euo pipefail

AUDIT_DIR="${1:-audit}"
mkdir -p "$AUDIT_DIR"
mkdir -p docs

echo "=== Generating Audit Bundle ==="
echo ""

# 1) Generate runtime snapshot (text)
echo "[1/5] Generating runtime snapshot..."
bash tools/audit/snapshot.sh "$AUDIT_DIR"

# 2) Generate snapshot JSON (for audit dir)
echo "[2/5] Generating snapshot JSON..."
bash tools/audit/gen_snapshot_json.sh "$AUDIT_DIR/snapshot.json"

# 3) Generate snapshot JSON (for docs)
echo "[3/5] Generating docs/REPO_SNAPSHOT.json..."
bash tools/audit/gen_snapshot_json.sh docs/REPO_SNAPSHOT.json

# 4) Generate repo tree (for docs)
echo "[4/5] Generating docs/REPO_TREE.generated.md..."
bash tools/audit/gen_repo_tree.sh . docs/REPO_TREE.generated.md

# 5) Verify expected paths
echo "[5/5] Verifying expected paths..."
bash tools/audit/verify_expected_paths.sh

echo ""
echo "=== Audit Bundle Complete ==="
echo ""
echo "Generated artifacts:"
echo "  - $AUDIT_DIR/snapshot.txt"
echo "  - $AUDIT_DIR/snapshot.json"
echo "  - docs/REPO_SNAPSHOT.json"
echo "  - docs/REPO_TREE.generated.md"
echo ""
ls -la "$AUDIT_DIR/"
