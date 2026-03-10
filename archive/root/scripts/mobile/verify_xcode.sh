#!/usr/bin/env bash
# verify_xcode.sh — Detect Xcode 16.x and select it via xcode-select.
#
# Used by:
#   - .github/workflows/odoo-mobile-ios-swift-tests.yml (ios-simulator job)
#   - Local development (run manually before xcodebuild)
#
# Exit codes:
#   0  Xcode 16.x found and selected
#   1  No Xcode 16.x found — prints install instructions
#
# Canonical version: Xcode 16.4 (MANUAL_REQUIRED: xcodes install "16.4")
# Fallback: any Xcode_16.x in /Applications (CI runners may have 16.2/16.3)

set -euo pipefail

CANONICAL_VERSION="16.4"
CANONICAL_PATH="/Applications/Xcode_${CANONICAL_VERSION}.app"

if [ -d "${CANONICAL_PATH}" ]; then
    echo "✅ Xcode ${CANONICAL_VERSION} found at ${CANONICAL_PATH}"
    sudo xcode-select -s "${CANONICAL_PATH}/Contents/Developer"
else
    # Fall back to the latest Xcode 16.x available
    XCODE=$(ls /Applications/ 2>/dev/null | grep -E "^Xcode_16\." | sort -V | tail -1 || true)
    if [ -n "${XCODE}" ]; then
        echo "⚠️  Xcode ${CANONICAL_VERSION} not found; using /Applications/${XCODE}"
        sudo xcode-select -s "/Applications/${XCODE}/Contents/Developer"
    else
        echo "❌ No Xcode 16.x found in /Applications/"
        echo ""
        echo "   Install Xcode 16.4 (Apple ID required):"
        echo "     xcodes install \"${CANONICAL_VERSION}\""
        echo ""
        echo "   Or download from: https://developer.apple.com/download/"
        echo ""
        echo "   The ios-simulator CI job requires Xcode 16.x."
        echo "   The macos-swift-clt job runs without Xcode (CLT only)."
        exit 1
    fi
fi

xcodebuild -version
