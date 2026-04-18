#!/bin/bash
# scripts/m365/build_app_package.sh
# Validates and packages the Pulser M365 Shell for sideloading.

PACKAGE_DIR="agents/pulser-surface/appPackage"
OUTPUT="pulser_m365_v1.zip"

echo "📍 Validating M365 App Package: $PACKAGE_DIR"

# Check for required files
FILES=("manifest.json" "declarativeAgent.json" "declarativeAgent_r2r.json" "ai-plugin.json" "color.png" "outline.png")

for file in "${FILES[@]}"; do
    if [ ! -f "$PACKAGE_DIR/$file" ]; then
        echo "❌ Missing: $PACKAGE_DIR/$file"
        MISSING=1
    else
        echo "✅ Found: $file"
    fi
done

if [ "$MISSING" == "1" ]; then
    echo "⚠️  Package incomplete. Please ensure icons are present before zipping."
    exit 1
fi

# Zip the package
echo "📦 Creating archive: $OUTPUT"
cd "$PACKAGE_DIR" && zip -r "../../..$OUTPUT" .
echo "✅ Done! Sideload $OUTPUT to Microsoft Teams or Outlook."
