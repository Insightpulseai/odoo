#!/usr/bin/env bash
# scripts/dev/vscode_doctor.sh
# Verify VS Code CLI is on PATH before contributor workflow.
# Pattern mirrors scripts/dev/docker_doctor.sh (same exit codes, same message style).
#
# Usage:
#   bash scripts/dev/vscode_doctor.sh
#   CODE_CMD=code-insiders bash scripts/dev/vscode_doctor.sh
#
# Exit codes: 0 = OK, 1 = CLI not found or version check failed

set -euo pipefail

CODE_CMD="${CODE_CMD:-code}"

if ! command -v "$CODE_CMD" &>/dev/null; then
  echo "ERROR: '$CODE_CMD' not found on PATH." >&2
  echo "" >&2
  echo "  macOS:  Open VS Code → Cmd+Shift+P → 'Shell Command: Install code in PATH'" >&2
  echo "  Linux:  VS Code .deb/.rpm/Snap installs the code CLI automatically" >&2
  echo "  Alt:    Set CODE_CMD=code-insiders if you are using VS Code Insiders" >&2
  exit 1
fi

VERSION=$("$CODE_CMD" --version 2>/dev/null | head -1)
echo "OK: VS Code CLI reachable via '$CODE_CMD' — $VERSION"
