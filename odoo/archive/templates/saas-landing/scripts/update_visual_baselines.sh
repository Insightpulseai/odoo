#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> pnpm install"
pnpm install --frozen-lockfile

echo "==> install playwright browsers"
pnpm playwright install --with-deps

echo "==> update snapshots for visual spec"
pnpm playwright test dashboard-visual.spec.ts --update-snapshots
