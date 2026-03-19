#!/usr/bin/env bash
# Example: List workspace root and export a notebook
set -euo pipefail

echo "=== List workspace root ==="
databricks workspace ls / --output json

echo "=== Export a notebook ==="
# databricks workspace export /Users/user@example.com/my_notebook ./my_notebook.py
# Uncomment and adjust paths for actual use

echo "=== List secret scopes ==="
databricks secrets list-scopes --output json

echo "=== List files in a volume ==="
# databricks fs ls dbfs:/mnt/data/ --output json
# Uncomment and adjust for actual use
