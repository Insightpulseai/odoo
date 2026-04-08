#!/usr/bin/env bash
# scripts/build-gateway.sh
# Prepares the build context with agents/ assets, then builds via ACR.
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PLATFORM_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
AGENTS_ROOT=$(cd "$PLATFORM_ROOT/../agents" && pwd)

echo "Platform root: $PLATFORM_ROOT"
echo "Agents root:   $AGENTS_ROOT"

# Copy agents assets into build context (temporary)
echo "=== Copying agents assets into build context ==="
rm -rf "$PLATFORM_ROOT/_agents"
mkdir -p "$PLATFORM_ROOT/_agents/foundry"
cp -r "$AGENTS_ROOT/foundry/ipai-odoo-copilot-azure" "$PLATFORM_ROOT/_agents/foundry/"

# Build via ACR
echo "=== Building via ACR ==="
cd "$PLATFORM_ROOT"
az acr build \
  --registry ipaiodoodevacr \
  --resource-group rg-ipai-dev \
  --image ipai-copilot-gateway:0.1.0 \
  --image ipai-copilot-gateway:latest \
  --file Dockerfile.gateway \
  .

# Cleanup
echo "=== Cleaning up ==="
rm -rf "$PLATFORM_ROOT/_agents"

echo "=== Done ==="
