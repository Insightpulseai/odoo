#!/usr/bin/env bash
# update-formula.sh — Recalculate SHA256s and update Homebrew formula after a release
#
# Usage: ./scripts/update-formula.sh <version>
# Example: ./scripts/update-formula.sh 0.2.0
#
# Prerequisites:
#   - GitHub release published with signed DMGs as assets
#   - curl + shasum available (standard on macOS)
#   - GITHUB_TOKEN env var set (for private repos)

set -euo pipefail

VERSION="${1:?Usage: $0 <version>}"
FORMULA="Formula/colima-desktop.rb"
REPO="Insightpulseai/odoo"
BASE_URL="https://github.com/${REPO}/releases/download/v${VERSION}"

DMG_X64="Colima-Desktop-${VERSION}.dmg"
DMG_ARM64="Colima-Desktop-${VERSION}-arm64.dmg"
TMP_DIR="$(mktemp -d)"

echo "Downloading DMGs for v${VERSION}..."

# Download both DMGs
curl -fsSL \
  -H "${GITHUB_TOKEN:+Authorization: Bearer $GITHUB_TOKEN}" \
  "${BASE_URL}/${DMG_X64}" -o "${TMP_DIR}/${DMG_X64}"

curl -fsSL \
  -H "${GITHUB_TOKEN:+Authorization: Bearer $GITHUB_TOKEN}" \
  "${BASE_URL}/${DMG_ARM64}" -o "${TMP_DIR}/${DMG_ARM64}"

# Calculate SHA256
SHA_X64="$(shasum -a 256 "${TMP_DIR}/${DMG_X64}" | awk '{print $1}')"
SHA_ARM64="$(shasum -a 256 "${TMP_DIR}/${DMG_ARM64}" | awk '{print $1}')"

echo "x64 SHA256:   ${SHA_X64}"
echo "arm64 SHA256: ${SHA_ARM64}"

# Update formula: version, URLs, SHA256s
sed -i '' \
  -e "s|version \"[^\"]*\"|version \"${VERSION}\"|" \
  -e "s|/download/v[^/]*/Colima-Desktop-[^.]*\.dmg|/download/v${VERSION}/Colima-Desktop-${VERSION}.dmg|" \
  -e "s|/download/v[^/]*/Colima-Desktop-[^-]*-arm64\.dmg|/download/v${VERSION}/Colima-Desktop-${VERSION}-arm64.dmg|" \
  -e "s|sha256 \"PLACEHOLDER_x64_SHA256\"|sha256 \"${SHA_X64}\"|" \
  -e "s|sha256 \"PLACEHOLDER_arm64_SHA256\"|sha256 \"${SHA_ARM64}\"|" \
  -e "s|sha256 \"[a-f0-9]\{64\}\" # x64|sha256 \"${SHA_X64}\" # x64|" \
  -e "s|sha256 \"[a-f0-9]\{64\}\" # arm64|sha256 \"${SHA_ARM64}\" # arm64|" \
  "${FORMULA}"

# Verify update applied
if grep -q "PLACEHOLDER" "${FORMULA}"; then
  echo "ERROR: Formula still contains PLACEHOLDER values — update failed" >&2
  exit 1
fi

echo ""
echo "Formula updated: ${FORMULA}"
echo "Version: ${VERSION}"
echo "Next step: commit + push to homebrew tap"
echo ""
echo "  git add ${FORMULA}"
echo "  git commit -m \"chore: bump colima-desktop formula to v${VERSION}\""
echo "  git push"

# Cleanup
rm -rf "${TMP_DIR}"
