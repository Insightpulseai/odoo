#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT_DIR"

echo "==> Applying Supabase Email Events Pack migrations"
supabase db reset --env-file .env.supabase || true
supabase db push --env-file .env.supabase

echo "==> Deploying email-events Edge Function"
cd supabase/functions/email-events
supabase functions deploy email-events --project-ref "${SUPABASE_PROJECT_REF:-}" --env-file ../../.env.supabase

echo "==> Email Events Pack applied."
