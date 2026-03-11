#!/usr/bin/env bash
# scripts/vercel/should-build-ops-console.sh
#
# Vercel "Ignored Build Step" script for apps/ops-console.
#
# Exit 0 → Vercel proceeds with the build.
# Exit 1 → Vercel skips the build.
#
# Problem: Vercel performs a shallow clone and does NOT always include
# origin/main in the local ref store.  Falling back to literal "origin/main"
# causes: "fatal: ambiguous argument 'origin/main': unknown revision"
#
# Strategy:
#  1) Prefer VERCEL_GIT_PREVIOUS_SHA  (always present on push events)
#  2) Try to resolve origin/main from the shallow clone as-is
#  3) Shallow-fetch origin main so the ref exists, then diff
#  4) If we can't determine a base at all, fail open (exit 0 = build)
#
set -euo pipefail

TARGET_PATH_REGEX='^apps/ops-console/'

BASE="${VERCEL_GIT_PREVIOUS_SHA:-}"
HEAD="${VERCEL_GIT_COMMIT_SHA:-HEAD}"

if [[ -n "${BASE}" ]]; then
  echo "[should-build] Using VERCEL_GIT_PREVIOUS_SHA=${BASE}"
else
  echo "[should-build] VERCEL_GIT_PREVIOUS_SHA not set — resolving origin/main"

  # Try if origin/main is already available (full clones, subsequent builds)
  if git rev-parse --verify origin/main >/dev/null 2>&1; then
    BASE="origin/main"
    echo "[should-build] origin/main resolved from local ref store"
  else
    # Shallow-fetch main; if this fails, fail open
    echo "[should-build] Shallow-fetching origin main..."
    if git fetch --depth=1 origin main >/dev/null 2>&1 && \
       git rev-parse --verify origin/main >/dev/null 2>&1; then
      BASE="origin/main"
      echo "[should-build] origin/main available after shallow fetch"
    else
      echo "[should-build] Cannot resolve base ref; failing open (build will proceed)"
      exit 0
    fi
  fi
fi

echo "[should-build] diff base=${BASE} head=${HEAD}"
if git diff --name-only "${BASE}" "${HEAD}" | grep -qE "${TARGET_PATH_REGEX}"; then
  echo "[should-build] ops-console changes detected → BUILD"
  exit 0
else
  echo "[should-build] No ops-console changes → SKIP BUILD"
  exit 1
fi
