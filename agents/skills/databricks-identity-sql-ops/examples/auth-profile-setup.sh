#!/usr/bin/env bash
# Example: Authentication profile setup and verification
set -euo pipefail

echo "=== List configured profiles ==="
databricks auth profiles 2>/dev/null || echo "No profiles configured"

echo "=== Check current auth environment ==="
databricks auth env 2>/dev/null || echo "Auth environment not configured"

echo "=== Verify token validity ==="
# databricks auth token --host https://<workspace>.azuredatabricks.net
# Uncomment with actual workspace URL
