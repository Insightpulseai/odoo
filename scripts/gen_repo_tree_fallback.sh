#!/usr/bin/env bash
# Fallback tree generator when 'tree' command is not available
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
TARGET_FILE="${ROOT_DIR}/spec.md"
TMP_TREE="$(mktemp)"

cd "${ROOT_DIR}"

# Generate tree-like structure using find
# Depth 2, exclude common build/cache directories
find . -maxdepth 2 \
  -not -path '*/\.*' \
  -not -path '*/node_modules*' \
  -not -path '*/__pycache__*' \
  -not -path '*/venv*' \
  -not -path '*/env*' \
  -not -path '*/packages*' \
  -not -name '*.pyc' \
  -not -name '.DS_Store' \
  | LC_ALL=C sort \
  | sed 's|^\./||' \
  | awk '
    BEGIN { FS = "/" }
    {
      depth = NF - 1
      if (depth == 0) {
        if ($0 == "") print "."
        else print $0
      } else if (depth == 1) {
        print "├── " $NF
      } else if (depth == 2) {
        print "│   ├── " $NF
      }
    }
  ' > "${TMP_TREE}"

# Escape backticks for safe insertion
ESCAPED_TREE=$(sed 's/`/\\`/g' "${TMP_TREE}")

# Replace the section between markers in TARGET_FILE
perl -0pi -e "s/<!-- REPO_TREE_START -->.*?<!-- REPO_TREE_END -->/<!-- REPO_TREE_START -->\n\`\`\`text\n${ESCAPED_TREE}\n\`\`\`\n<!-- REPO_TREE_END -->/s" "${TARGET_FILE}"

rm -f "${TMP_TREE}"

echo "✅ Updated repo tree in ${TARGET_FILE} (using fallback)"
