#!/usr/bin/env bash
# Build iOS release
# For Flutter apps (signing handled by fastlane)

set -euo pipefail

APP_DIR="${APP_DIR:-apps/flutter_app}"

echo "=== Building iOS Release ==="
echo ""

cd "$APP_DIR"

# Clean and get dependencies
echo "Getting dependencies..."
flutter pub get

# Build iOS release (no codesign - fastlane handles it)
echo "Building iOS release..."
flutter build ios --release --no-codesign

echo ""
echo "PASS: Built iOS app (unsigned)"
echo ""
echo "Next: Use 'fastlane ios beta' to sign and upload to TestFlight"
