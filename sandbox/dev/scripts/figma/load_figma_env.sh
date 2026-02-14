#!/usr/bin/env bash
# Load Figma environment variables from macOS Keychain
# Usage: source scripts/figma/load_figma_env.sh

# Fetch token from Keychain
FIGMA_ACCESS_TOKEN="$(security find-generic-password -s ipai_figma -a FIGMA_ACCESS_TOKEN -w 2>/dev/null || true)"

if [[ -z "${FIGMA_ACCESS_TOKEN}" ]]; then
  echo "ERROR: FIGMA_ACCESS_TOKEN not found in macOS Keychain" >&2
  echo "Run: ./scripts/figma/setup_figma_token.sh" >&2
  return 1
fi

export FIGMA_ACCESS_TOKEN

# Set file key (from user's screenshot: Modern Brand Design Studio)
export FIGMA_FILE_KEY="${FIGMA_FILE_KEY:-7XCC5p6r9yDrMGCE9eI3LC}"

echo "✅ Figma environment loaded from Keychain"
echo "   FIGMA_FILE_KEY: ${FIGMA_FILE_KEY}"
