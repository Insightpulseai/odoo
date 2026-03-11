#!/bin/bash
# Take screenshot of production Odoo login page

set -e

PRODUCTION_URL="https://erp.insightpulseai.com/web/login"
SCREENSHOT_DIR="/Users/tbwa/odoo-ce/docs/screenshots"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SCREENSHOT_FILE="$SCREENSHOT_DIR/login_${TIMESTAMP}.png"

echo "==========================================="
echo "Production Screenshot Capture"
echo "==========================================="
echo ""

# Create screenshots directory if it doesn't exist
mkdir -p "$SCREENSHOT_DIR"

echo "📸 Taking screenshot of: $PRODUCTION_URL"
echo ""

# Check if we have screenshot capability
if command -v screencapture &> /dev/null; then
    echo "Using macOS screencapture..."
    echo "Please:"
    echo "1. Open $PRODUCTION_URL in your browser"
    echo "2. Press Enter when ready to capture"
    read -p "Press Enter to continue..."

    echo "Taking screenshot in 3 seconds..."
    sleep 3
    screencapture -i "$SCREENSHOT_FILE"
    echo "✅ Screenshot saved to: $SCREENSHOT_FILE"

elif command -v playwright &> /dev/null; then
    echo "Using Playwright for screenshot..."
    npx playwright screenshot "$PRODUCTION_URL" "$SCREENSHOT_FILE" --full-page
    echo "✅ Screenshot saved to: $SCREENSHOT_FILE"

else
    echo "⚠️  No screenshot tool available"
    echo ""
    echo "Manual verification steps:"
    echo "1. Open: $PRODUCTION_URL"
    echo "2. Take a screenshot manually"
    echo "3. Save to: $SCREENSHOT_DIR/"
    echo ""
    echo "What to verify:"
    echo "✅ Header shows only TBWA logo and user menu"
    echo "✅ No navigation menu items visible"
    echo "✅ Login button is black with white text"
    echo "✅ Login button is clickable"
    echo "✅ TBWA footer is visible at bottom"
fi

echo ""
echo "==========================================="
echo "Verification Checklist"
echo "==========================================="
echo ""
echo "✅ Header cleanup:"
echo "   - Only TBWA logo visible on left"
echo "   - Only user menu visible on right"
echo "   - No menu items (Platform, Overview, Channels, etc.)"
echo "   - No breadcrumbs"
echo "   - No search bar"
echo ""
echo "✅ Login button:"
echo "   - Black background (#000000)"
echo "   - White text"
echo "   - Proper hover effect"
echo "   - Clickable"
echo ""
echo "✅ Footer:"
echo "   - TBWA branding visible"
echo "   - Social media links present"
echo ""
