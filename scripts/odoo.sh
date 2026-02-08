#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$ROOT/odoo-bin"

first="$(head -n 1 "$BIN" 2>/dev/null || true)"
if [[ "$first" == "#!"*bash* ]] || [[ "$first" == "#!"*"/env bash"* ]]; then
  exec "$BIN" "$@"
fi

# python entrypoint fallback
PY="${PYTHON:-python}"
command -v "$PY" >/dev/null 2>&1 || PY=python3
exec "$PY" "$BIN" "$@"
