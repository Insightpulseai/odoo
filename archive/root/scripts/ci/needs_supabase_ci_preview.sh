#!/usr/bin/env bash
set -euo pipefail
git fetch origin main --quiet || true
if git diff --name-only origin/main...HEAD | grep -q '^supabase/'; then
  echo "true"
else
  echo "false"
fi
