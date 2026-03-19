#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

: "${PLAYWRIGHT_PROJECT:=chromium}"
: "${BASE_URL:=http://localhost:3000}"

echo "==> pnpm install"
pnpm install --frozen-lockfile

echo "==> install playwright browsers"
pnpm playwright install --with-deps

echo "==> run e2e (${PLAYWRIGHT_PROJECT})"
PLAYWRIGHT_BASE_URL="${BASE_URL}" pnpm test:e2e --project="${PLAYWRIGHT_PROJECT}"
