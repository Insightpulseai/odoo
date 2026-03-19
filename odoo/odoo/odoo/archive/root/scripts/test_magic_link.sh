#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Magic Link Test Script
# ============================================================================
# Purpose: Test magic link authentication flow end-to-end
#
# Prerequisites:
# 1. Redirect URL configured in Supabase Dashboard
# 2. Local server running at http://localhost:3000
#
# Usage: ./scripts/test_magic_link.sh <email>
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Load credentials
if [ -f "$HOME/.zshrc" ]; then
  source "$HOME/.zshrc" 2>/dev/null || true
fi

if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_ANON_KEY:-}" ]; then
  echo -e "${YELLOW}Missing SUPABASE_URL or SUPABASE_ANON_KEY${NC}"
  echo "Set in ~/.zshrc or export manually"
  exit 1
fi

# Get email from argument or use default
EMAIL="${1:-jgtolentino.rn@gmail.com}"

echo ""
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  Magic Link Authentication Test${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Step 1: Request magic link
echo -e "${BLUE}[1/4] Requesting magic link for: $EMAIL${NC}"

RESPONSE=$(curl -s -X POST \
  "$SUPABASE_URL/auth/v1/magiclink" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"options\": {
      \"redirectTo\": \"http://localhost:3000/auth/callback\"
    }
  }")

if echo "$RESPONSE" | grep -q "error"; then
  echo -e "${YELLOW}Warning: Magic link request might have failed${NC}"
  echo "$RESPONSE" | jq '.'
else
  echo -e "${GREEN}✓ Magic link sent to $EMAIL${NC}"
fi

echo ""

# Step 2: Instructions for user
echo -e "${BLUE}[2/4] Next Steps:${NC}"
echo ""
echo "1. Check your email inbox for magic link"
echo "2. Make sure local server is running:"
echo -e "   ${YELLOW}python3 -m http.server 3000${NC}"
echo ""
echo "3. Click the magic link in your email"
echo ""
echo "4. You should see a redirect to: http://localhost:3000/auth/callback"
echo ""

# Step 3: Verify redirect URL is configured
echo -e "${BLUE}[3/4] Checking Supabase Auth configuration...${NC}"

# Check if redirect URL is in config
SITE_URL=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "
  SELECT value FROM auth.config WHERE name = 'site_url';
" 2>/dev/null | xargs || echo "unknown")

echo -e "Site URL: ${YELLOW}$SITE_URL${NC}"
echo ""

# Step 4: Create simple test page
echo -e "${BLUE}[4/4] Creating auth callback test page...${NC}"

cat > /tmp/auth-callback.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <title>Magic Link Test - Auth Callback</title>
  <style>
    body {
      font-family: system-ui, -apple-system, sans-serif;
      max-width: 800px;
      margin: 50px auto;
      padding: 20px;
      background: #f5f5f5;
    }
    h1 { color: #333; }
    pre {
      background: #fff;
      padding: 20px;
      border-radius: 8px;
      overflow-x: auto;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success { color: #22c55e; }
    .error { color: #ef4444; }
    .loading { color: #3b82f6; }
  </style>
</head>
<body>
  <h1>Magic Link Authentication Test</h1>
  <pre id="output" class="loading">Loading session...</pre>

  <script type="module">
    import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

    const supabase = createClient(
      'https://spdtwktxdalcfigzeqrz.supabase.co',
      'YOUR_ANON_KEY_HERE'  // Replace with actual anon key
    )

    const output = document.getElementById('output')

    try {
      // Get session from URL (magic link adds tokens to URL)
      const { data: { session }, error } = await supabase.auth.getSession()

      if (error) {
        output.className = 'error'
        output.textContent = '❌ AUTH ERROR\n\n' + JSON.stringify(error, null, 2)
      } else if (session) {
        output.className = 'success'
        output.textContent = '✅ AUTHENTICATION SUCCESSFUL!\n\n' +
          'Email: ' + session.user.email + '\n' +
          'User ID: ' + session.user.id + '\n\n' +
          'JWT CLAIMS (from custom hook):\n' +
          '  tenant_id: ' + (session.user.user_metadata.tenant_id || 'MISSING!') + '\n' +
          '  role: ' + (session.user.user_metadata.role || 'MISSING!') + '\n' +
          '  tenant_slug: ' + (session.user.user_metadata.tenant_slug || 'MISSING!') + '\n' +
          '  display_name: ' + (session.user.user_metadata.display_name || 'MISSING!') + '\n\n' +
          'Full User Metadata:\n' + JSON.stringify(session.user.user_metadata, null, 2) + '\n\n' +
          'Access Token (first 50 chars):\n' + session.access_token.substring(0, 50) + '...'
      } else {
        output.className = 'error'
        output.textContent = '⚠️  NO SESSION FOUND\n\n' +
          'This could mean:\n' +
          '- Magic link not clicked yet\n' +
          '- Redirect URL not configured correctly\n' +
          '- Custom access token hook failed\n\n' +
          'Check Supabase Dashboard → Authentication → Logs'
      }
    } catch (err) {
      output.className = 'error'
      output.textContent = '❌ UNEXPECTED ERROR\n\n' + err.message + '\n\n' + err.stack
    }
  </script>
</body>
</html>
EOF

# Replace placeholder with actual anon key
sed -i '' "s/YOUR_ANON_KEY_HERE/$SUPABASE_ANON_KEY/" /tmp/auth-callback.html

echo -e "${GREEN}✓ Test page created: /tmp/auth-callback.html${NC}"
echo ""

# Instructions to run test
echo -e "${YELLOW}TO TEST:${NC}"
echo ""
echo "1. Start local server:"
echo -e "   ${BLUE}cd /tmp && python3 -m http.server 3000${NC}"
echo ""
echo "2. Click magic link in your email"
echo ""
echo "3. Browser will redirect to:"
echo -e "   ${BLUE}http://localhost:3000/auth-callback.html${NC}"
echo ""
echo "4. You should see:"
echo -e "   ${GREEN}✅ AUTHENTICATION SUCCESSFUL!${NC}"
echo -e "   With tenant_id: ${GREEN}00000000-0000-0000-0000-000000000001${NC}"
echo -e "   With role: ${GREEN}owner${NC}"
echo ""
echo -e "${YELLOW}TROUBLESHOOTING:${NC}"
echo "If you see errors, check:"
echo "• Supabase Dashboard → Authentication → URL Configuration"
echo "• Make sure http://localhost:3000/* is in Redirect URLs"
echo "• Check Supabase Dashboard → Authentication → Logs for errors"
echo ""
