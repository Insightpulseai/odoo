#!/usr/bin/env bash
# Example: Create a secret scope and store a secret
set -euo pipefail

SCOPE="ipai-secrets"

echo "=== Create secret scope ==="
databricks secrets create-scope --scope "${SCOPE}" 2>/dev/null || echo "Scope already exists"

echo "=== Store a secret (from stdin) ==="
# echo "my-secret-value" | databricks secrets put-secret --scope "${SCOPE}" --key "api-key"
# Uncomment for actual use — never hardcode secret values

echo "=== List secrets in scope (metadata only) ==="
databricks secrets list --scope "${SCOPE}" --output json
