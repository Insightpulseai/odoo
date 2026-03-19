#!/usr/bin/env bash
set -euo pipefail
: "${SUPABASE_PROJECT_REF:?Set SUPABASE_PROJECT_REF}"
OUT_DIR="${OUT_DIR:-out/schema}"
mkdir -p "${OUT_DIR}"

supabase link --project-ref "${SUPABASE_PROJECT_REF}" >/dev/null
supabase db dump --schema-only > "${OUT_DIR}/supabase.remote.schema.sql"

if [[ -f "supabase/schema.sql" ]]; then
  cp supabase/schema.sql "${OUT_DIR}/supabase.repo.schema.sql"
else
  echo "-- TODO: create supabase/schema.sql (blessed snapshot or render from migrations)" > "${OUT_DIR}/supabase.repo.schema.sql"
fi

diff -u "${OUT_DIR}/supabase.repo.schema.sql" "${OUT_DIR}/supabase.remote.schema.sql"
