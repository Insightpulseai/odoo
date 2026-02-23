#!/usr/bin/env bash
# Setup Figma access token in macOS Keychain
# One-time setup for local development

set -euo pipefail

echo "=== Figma Token Setup ==="
echo ""
echo "This script will store your Figma personal access token in macOS Keychain."
echo ""
echo "To create a token:"
echo "  1. Go to https://www.figma.com/settings"
echo "  2. Scroll to 'Personal Access Tokens'"
echo "  3. Click 'Create new token'"
echo "  4. Copy the token (starts with 'figd_')"
echo ""

# Prompt for token
read -r -p "Enter your Figma access token: " FIGMA_TOKEN

if [[ -z "${FIGMA_TOKEN}" ]]; then
  echo "ERROR: Token cannot be empty"
  exit 1
fi

# Store in Keychain
echo ""
echo "Storing token in macOS Keychain..."

# Delete existing if present
security delete-generic-password -s ipai_figma -a FIGMA_ACCESS_TOKEN 2>/dev/null || true

# Add new token
security add-generic-password \
  -s ipai_figma \
  -a FIGMA_ACCESS_TOKEN \
  -w "${FIGMA_TOKEN}" \
  -U

echo ""
echo "✅ Token stored successfully!"
echo ""
echo "Keychain entry:"
echo "  Service: ipai_figma"
echo "  Account: FIGMA_ACCESS_TOKEN"
echo ""
echo "To load this token in your shell:"
echo "  source scripts/figma/load_figma_env.sh"
echo ""
