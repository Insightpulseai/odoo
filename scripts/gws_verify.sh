#!/bin/bash
# gws Connectivity Verification Script
# Powered by InsightPulseAI

# Load W9 Studio credentials if available
CREDENTIALS_FILE="/Users/tbwa/Downloads/client_secret_916601142061-kva9q6607moot9rfm00so8l7h7a4b341.apps.googleusercontent.com.json"
GWS_BIN="./bin/gws"

echo "🔍 Verifying gws CLI..."
if [[ ! -f "$GWS_BIN" ]]; then
    echo "❌ Error: gws binary not found at $GWS_BIN"
    exit 1
fi

VERSION=$($GWS_BIN --version)
echo "✅ Tool found: $VERSION"

if [[ -f "$CREDENTIALS_FILE" ]]; then
    echo "🔑 Found W9 Studio credentials. Attempting headless connectivity check..."
    export GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE="$CREDENTIALS_FILE"
    
    # Simple read-only check: List 1 drive file
    $GWS_BIN drive files list --params '{"pageSize": 1}' > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Connectivity successful: Can reach Google Drive API."
    else
        echo "⚠️ Connectivity check failed (Exit code $?). This may be expected if consent is required."
        echo "💡 To fix, run: ./bin/gws auth login --scopes drive,gmail,calendar"
    fi
else
    echo "ℹ️ W9 Studio credentials JSON not found in Downloads. Skipping connectivity check."
fi
