#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"

TARGET_FILE="${ROOT_DIR}/spec.md"
TMP_TREE="$(mktemp)"

cd "${ROOT_DIR}"

# Check if tree command is available, otherwise use fallback
if command -v tree &> /dev/null; then
    # Generate the actual tree (depth 2, adjust as needed)
    # Exclude common build/cache directories and git-ignored paths
    # Use LC_ALL=C for consistent sorting across macOS and Linux
    # Use -a to show dotfiles but exclude specific ignored directories
    LC_ALL=C tree -a -L 2 \
      --dirsfirst \
      --noreport \
      -I 'node_modules|.git|__pycache__|*.pyc|.DS_Store|venv|env|packages' \
      . > "${TMP_TREE}"
else
    echo "Warning: 'tree' command not found, using fallback method"
    # Fallback: use find to generate tree-like output
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
            print "|-- " $NF
          } else if (depth == 2) {
            print "|   |-- " $NF
          }
        }
      ' > "${TMP_TREE}"
fi

# Escape backticks for safe insertion
ESCAPED_TREE=$(sed 's/`/\\`/g' "${TMP_TREE}")

# Replace the section between markers in TARGET_FILE
perl -0pi -e "s/<!-- REPO_TREE_START -->.*?<!-- REPO_TREE_END -->/<!-- REPO_TREE_START -->\n\`\`\`text\n${ESCAPED_TREE}\n\`\`\`\n<!-- REPO_TREE_END -->/s" "${TARGET_FILE}"

rm -f "${TMP_TREE}"

echo "✅ Updated repo tree in ${TARGET_FILE}"
