#!/usr/bin/env bash
# Example: controlled write operation via safe wrapper
set -euo pipefail

# 1. Execute the write
TOOL_NAME=mycli ./bin/tool-safe update --target "$TARGET" --output json

# 2. Verify the result
TOOL_NAME=mycli ./bin/tool-safe show --target "$TARGET" --output json | jq '.status'
