#!/usr/bin/env bash
set -euo pipefail

REPO="${REPO:-jgtolentino/odoo-ce}"
BRANCH="${BRANCH:-main}"
MACHINE="${MACHINE:-standardLinux32gb}"

echo "Launching GitHub Codespace..."
echo "  Repo   : $REPO"
echo "  Branch : $BRANCH"
echo "  Machine: $MACHINE"
echo

gh codespace create \
  --repo "$REPO" \
  --branch "$BRANCH" \
  --machine "$MACHINE"
