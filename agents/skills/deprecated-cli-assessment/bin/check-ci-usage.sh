#!/usr/bin/env bash
# deprecated-cli-assessment: Check if deprecated tools appear in CI pipelines
# Usage: check-ci-usage.sh [--tool <name>]
set -euo pipefail

TOOL="${2:-odo}"
SEARCH_PATHS=(
  ".github/workflows/"
  "scripts/"
  "docker/"
  "Makefile"
)

echo "Checking for deprecated tool '${TOOL}' in CI/build files"
FOUND=0

for path in "${SEARCH_PATHS[@]}"; do
  if [ -e "${path}" ]; then
    MATCHES=$(grep -rl "${TOOL}" "${path}" 2>/dev/null || true)
    if [ -n "${MATCHES}" ]; then
      echo "FOUND in: ${MATCHES}"
      FOUND=$((FOUND + 1))
    fi
  fi
done

if [ "${FOUND}" -eq 0 ]; then
  echo "CLEAN: No references to '${TOOL}' found in CI/build files"
  exit 0
else
  echo "WARNING: ${FOUND} file(s) reference deprecated tool '${TOOL}'"
  exit 1
fi
