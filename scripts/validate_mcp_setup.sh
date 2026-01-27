#!/usr/bin/env bash
set -euo pipefail

echo "🔍 Validating MCP setup..."

# 1. Check registry syntax
echo "✓ Checking registry syntax..."
python3 -c "import yaml; yaml.safe_load(open('mcp/registry/servers.yaml'))" || exit 1

# 2. Check secrets schema
echo "✓ Checking secrets schema..."
python3 -m json.tool secrets/schema.json >/dev/null || exit 1

# 3. Check policies
echo "✓ Checking policies..."
python3 -c "import yaml; yaml.safe_load(open('mcp/policies/safety.yaml'))" || exit 1

# 4. Validate generated adapters
echo "✓ Validating adapters..."
for f in adapters/*/*.json; do
  python3 -m json.tool "$f" >/dev/null || exit 1
done

# 5. Check capabilities inventory
echo "✓ Checking capabilities..."
if [ -f capabilities/current.json ]; then
  python3 -m json.tool capabilities/current.json >/dev/null || exit 1
fi

echo "✅ All MCP validations passed"
