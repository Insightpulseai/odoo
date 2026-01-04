#!/usr/bin/env bash
# Android Store Readiness Audit
# Checks Play Store requirements before submission

set -euo pipefail

APP_DIR="${APP_DIR:-apps/flutter_app}"
GRADLE_FILE="${GRADLE_FILE:-$APP_DIR/android/app/build.gradle}"
MIN_TARGET_SDK="${MIN_TARGET_SDK:-35}"

echo "=== Android Store Readiness Audit ==="
echo ""

# Check Gradle file exists
if [[ ! -f "$GRADLE_FILE" ]]; then
    echo "FAIL: Gradle file not found at $GRADLE_FILE"
    exit 1
fi

echo "Checking: $GRADLE_FILE"
echo ""

# Extract targetSdkVersion
TARGET_SDK=$(grep -E 'targetSdkVersion|targetSdk' "$GRADLE_FILE" | \
    tail -n 1 | \
    sed -E 's/.*(targetSdkVersion|targetSdk)[^0-9]*([0-9]+).*/\2/' || echo "")

if [[ -z "$TARGET_SDK" ]]; then
    echo "FAIL: Could not detect targetSdk in $GRADLE_FILE"
    exit 1
fi

echo "Target SDK: $TARGET_SDK (minimum required: $MIN_TARGET_SDK)"

# Play Store requirement: API 35 for new apps/updates (as of Aug 2025)
if (( TARGET_SDK < MIN_TARGET_SDK )); then
    echo "FAIL: targetSdk=$TARGET_SDK < $MIN_TARGET_SDK"
    echo ""
    echo "Google Play requires API $MIN_TARGET_SDK for new apps and updates."
    echo "Update android/app/build.gradle: targetSdkVersion $MIN_TARGET_SDK"
    exit 1
fi

echo "PASS: targetSdk=$TARGET_SDK meets Play Store requirements"
echo ""

# Check for required files
echo "Checking required files..."

CHECKS=(
    "$APP_DIR/android/app/src/main/AndroidManifest.xml:Android Manifest"
    "$APP_DIR/android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png:App Icon (xxxhdpi)"
)

for check in "${CHECKS[@]}"; do
    file="${check%%:*}"
    desc="${check#*:}"
    if [[ -f "$file" ]]; then
        echo "  ✓ $desc"
    else
        echo "  ✗ $desc - MISSING: $file"
    fi
done

echo ""
echo "=== Audit Complete ==="
