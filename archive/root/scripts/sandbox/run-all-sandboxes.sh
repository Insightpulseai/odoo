#!/usr/bin/env bash
set -euo pipefail

echo "=== Sandbox Options ==="
echo "1) Local CI gates only"
echo "2) Local Docker sandbox (dev)"
echo "3) GitHub Codespaces"
echo "4) DigitalOcean CE19 build/test"
echo

read -rp "Select option [1-4]: " choice

ROOT_DIR="$(git rev-parse --show-toplevel)"
case "$choice" in
  1)
    exec "$ROOT_DIR/scripts/ci/run-all-gates.sh"
    ;;
  2)
    exec "$ROOT_DIR/scripts/sandbox/start-local-sandbox.sh"
    ;;
  3)
    exec "$ROOT_DIR/scripts/sandbox/start-codespace.sh"
    ;;
  4)
    exec "$ROOT_DIR/scripts/sandbox/start-do-sandbox.sh"
    ;;
  *)
    echo "Invalid choice"
    exit 1
    ;;
esac
