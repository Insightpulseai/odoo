#!/usr/bin/env bash
set -euo pipefail

MODULE="${BRAND_TARGET_MODULE:-ipai_website_shell}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MOD_DIR="${ROOT}/addons/${MODULE}"
IMG_DIR="${MOD_DIR}/static/src/img"

: "${BRAND_LOGO_SRC:?Set BRAND_LOGO_SRC to an absolute path}"
: "${BRAND_FAVICON_SRC:?Set BRAND_FAVICON_SRC to an absolute path}"

mkdir -p "$IMG_DIR"

copy_if_changed () {
  src="$1"
  dst="$2"
  if [ ! -f "$src" ]; then
    echo "[brand] ERROR: src missing: $src" >&2
    exit 2
  fi
  if [ -f "$dst" ] && cmp -s "$src" "$dst"; then
    echo "[brand] unchanged: $dst"
  else
    cp "$src" "$dst"
    echo "[brand] updated: $dst"
  fi
}

echo "[brand] syncing assets into ${IMG_DIR}"
copy_if_changed "$BRAND_LOGO_SRC" "${IMG_DIR}/logo.png"
copy_if_changed "$BRAND_FAVICON_SRC" "${IMG_DIR}/favicon.ico"

if [ -n "${BRAND_LOGO_WHITE_SRC:-}" ]; then
  copy_if_changed "$BRAND_LOGO_WHITE_SRC" "${IMG_DIR}/logo-white.png"
fi

echo "[brand] sync complete"
