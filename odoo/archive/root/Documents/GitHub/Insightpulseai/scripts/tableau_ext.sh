#!/usr/bin/env bash
set -euo pipefail

ROOT="templates/vendor/tableau-extensions-api"

cmd="${1:-}"
case "$cmd" in
  install)
    (cd "$ROOT" && npm install)
    ;;
  build)
    (cd "$ROOT" && npm run build)
    ;;
  start)
    (cd "$ROOT" && npm start)
    ;;
  dev)
    (cd "$ROOT" && npm run dev)
    ;;
  start-sandbox)
    (cd "$ROOT" && npm run start-sandbox)
    ;;
  *)
    cat <<'TXT'
Usage:
  ./scripts/tableau_ext.sh install|build|start|dev|start-sandbox

Notes:
- Commands map to the official tableau/extensions-api README scripts.
TXT
    exit 2
    ;;
esac
