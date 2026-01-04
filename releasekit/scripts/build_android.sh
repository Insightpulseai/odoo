#!/usr/bin/env bash
# Build Android release (AAB)
# For Flutter apps

set -euo pipefail

APP_DIR="${APP_DIR:-apps/flutter_app}"

echo "=== Building Android Release ==="
echo ""

cd "$APP_DIR"

# Clean and get dependencies
echo "Getting dependencies..."
flutter pub get

# Build release AAB
echo "Building release AAB..."
flutter build appbundle --release

AAB_PATH="$PWD/build/app/outputs/bundle/release/app-release.aab"

if [[ ! -f "$AAB_PATH" ]]; then
    echo "FAIL: AAB not found at $AAB_PATH"
    exit 1
fi

# Save path for fastlane
echo "$AAB_PATH" > "$PWD/.aab_path"

echo ""
echo "PASS: Built $AAB_PATH"
echo ""
echo "Size: $(du -h "$AAB_PATH" | cut -f1)"
