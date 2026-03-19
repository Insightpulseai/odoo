#!/usr/bin/env bash
# Generate canonical repo tree documentation
set -euo pipefail

ROOT="${1:-.}"
OUT_MD="${2:-docs/REPO_TREE.generated.md}"

mkdir -p "$(dirname "$OUT_MD")"

# Prefer `tree` if present; fallback to find.
if command -v tree >/dev/null 2>&1; then
  TREE_CMD="tree -a -I '.git|.venv|node_modules|__pycache__|.pytest_cache|dist|build' -L 4"
  echo "# Repo Tree (generated)" > "$OUT_MD"
  echo "" >> "$OUT_MD"
  echo "Generated at: $(date -Iseconds)" >> "$OUT_MD"
  echo "Commit: $(git rev-parse HEAD 2>/dev/null || echo 'N/A')" >> "$OUT_MD"
  echo "" >> "$OUT_MD"
  echo '```' >> "$OUT_MD"
  (cd "$ROOT" && $TREE_CMD) >> "$OUT_MD"
  echo '```' >> "$OUT_MD"
else
  echo "# Repo Tree (generated)" > "$OUT_MD"
  echo "" >> "$OUT_MD"
  echo "Generated at: $(date -Iseconds)" >> "$OUT_MD"
  echo "" >> "$OUT_MD"
  echo '```' >> "$OUT_MD"
  (cd "$ROOT" && find . -maxdepth 4 \
    -not -path '*/.git/*' \
    -not -path '*/node_modules/*' \
    -not -path '*/__pycache__/*' \
    -not -path '*/.pytest_cache/*' \
    -type d | sort) >> "$OUT_MD"
  echo '```' >> "$OUT_MD"
fi
echo "Wrote $OUT_MD"
