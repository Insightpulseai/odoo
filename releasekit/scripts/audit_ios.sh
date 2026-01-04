#!/usr/bin/env bash
# iOS Store Readiness Audit
# Checks App Store requirements before submission

set -euo pipefail

IOS_DIR="${IOS_DIR:-apps/flutter_app/ios}"
PBXPROJ="${PBXPROJ:-$IOS_DIR/Runner.xcodeproj/project.pbxproj}"
INFO_PLIST="${INFO_PLIST:-$IOS_DIR/Runner/Info.plist}"

echo "=== iOS Store Readiness Audit ==="
echo ""

# Check project file exists
if [[ ! -f "$PBXPROJ" ]]; then
    echo "FAIL: Xcode project not found at $PBXPROJ"
    exit 1
fi

echo "Checking: $PBXPROJ"
echo ""

# Check bundle identifier
if grep -q "PRODUCT_BUNDLE_IDENTIFIER" "$PBXPROJ"; then
    BUNDLE_ID=$(grep "PRODUCT_BUNDLE_IDENTIFIER" "$PBXPROJ" | head -1 | sed 's/.*= *"\{0,1\}\([^";]*\).*/\1/')
    echo "Bundle ID: $BUNDLE_ID"
else
    echo "FAIL: No PRODUCT_BUNDLE_IDENTIFIER found"
    exit 1
fi

echo ""
echo "Checking Info.plist..."

if [[ -f "$INFO_PLIST" ]]; then
    echo "  ✓ Info.plist exists"

    # Check for common usage descriptions
    USAGE_KEYS=(
        "NSCameraUsageDescription:Camera"
        "NSMicrophoneUsageDescription:Microphone"
        "NSPhotoLibraryUsageDescription:Photo Library"
        "NSLocationWhenInUseUsageDescription:Location"
    )

    for key_desc in "${USAGE_KEYS[@]}"; do
        key="${key_desc%%:*}"
        desc="${key_desc#*:}"
        if grep -q "$key" "$INFO_PLIST"; then
            echo "  ✓ $desc usage description present"
        else
            echo "  - $desc usage description not found (add if needed)"
        fi
    done
else
    echo "  ✗ Info.plist not found at $INFO_PLIST"
fi

echo ""
echo "App Store Review Guidelines Checklist:"
echo "  □ Privacy policy URL configured"
echo "  □ App icons for all required sizes"
echo "  □ Screenshots for required device sizes"
echo "  □ Test account credentials (if login required)"
echo "  □ No placeholder content"
echo "  □ App provides real value (not a thin wrapper)"
echo ""

echo "=== Audit Complete ==="
