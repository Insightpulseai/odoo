#!/usr/bin/env bash
set -euo pipefail

MODULE="${BRAND_TARGET_MODULE:-ipai_website_shell}"
STRICT="${BRAND_STRICT:-true}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MOD_DIR="${ROOT}/addons/${MODULE}"
IMG_DIR="${MOD_DIR}/static/src/img"

required=(
  "${IMG_DIR}/logo.png"
  "${IMG_DIR}/favicon.ico"
)

optional=(
  "${IMG_DIR}/logo-white.png"
)

fail=0

echo "[brand] validating module assets in: ${IMG_DIR}"

if [ ! -d "$MOD_DIR" ]; then
  echo "[brand] ERROR: module not found: $MOD_DIR" >&2
  exit 2
fi

for f in "${required[@]}"; do
  if [ ! -s "$f" ]; then
    echo "[brand] MISSING: $f" >&2
    fail=1
  else
    echo "[brand] OK: $f ($(wc -c < "$f") bytes)"
  fi
done

for f in "${optional[@]}"; do
  if [ -s "$f" ]; then
    echo "[brand] OK (optional): $f ($(wc -c < "$f") bytes)"
  else
    echo "[brand] WARN (optional missing): $f"
  fi
done

# Template drift checks: ensure templates prefer module static assets (product-as-code)
# - Look for logo_url/website.logo_url usage in website shell templates
# - Ensure /static/src/img/logo.png is referenced somewhere if header/footer uses it
echo "[brand] scanning templates for asset reference patterns"
if command -v rg >/dev/null 2>&1; then
  rg -n "logo_url|website\.logo|/web/image" "$MOD_DIR/views" && {
    echo "[brand] WARN: found DB-backed logo references in ${MOD_DIR}/views (consider using module static assets)."
  } || true

  rg -n "/${MODULE}/static/src/img/logo\.png|/static/src/img/logo\.png" "$MOD_DIR/views" >/dev/null 2>&1 || {
    echo "[brand] WARN: no explicit static logo reference found in ${MOD_DIR}/views."
  }
else
  echo "[brand] NOTE: ripgrep (rg) not available; skipping template scan"
fi

if [ "$fail" -eq 1 ] && [ "$STRICT" = "true" ]; then
  echo "[brand] FAIL: required brand assets missing"
  exit 1
fi

echo "[brand] PASS"
