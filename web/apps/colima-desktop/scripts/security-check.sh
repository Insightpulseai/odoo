#!/usr/bin/env bash
set -euo pipefail

echo "🔒 Colima Desktop - Security Verification Script"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() {
  echo -e "${GREEN}✅ PASS${NC}: $1"
}

fail() {
  echo -e "${RED}❌ FAIL${NC}: $1"
}

warn() {
  echo -e "${YELLOW}⚠️  WARN${NC}: $1"
}

# Check 1: No eval() usage
echo "1. Checking for eval() usage..."
if ! grep -r "eval(" apps/colima-desktop-ui/src/ >/dev/null 2>&1; then
  pass "No eval() found in renderer code"
else
  fail "eval() found - dynamic code execution risk"
  exit 1
fi

# Check 2: No Function() constructor
echo "2. Checking for Function() constructor..."
if ! grep -r "Function(" apps/colima-desktop-ui/src/ >/dev/null 2>&1; then
  pass "No Function() constructor found"
else
  fail "Function() constructor found - code injection risk"
  exit 1
fi

# Check 3: No direct ipcRenderer in renderer
echo "3. Checking for direct ipcRenderer usage in renderer..."
if ! grep -r "ipcRenderer" apps/colima-desktop-ui/src/renderer/ >/dev/null 2>&1; then
  pass "No direct ipcRenderer access in renderer"
else
  fail "Direct ipcRenderer usage found - should use contextBridge"
  exit 1
fi

# Check 4: contextIsolation enabled
echo "4. Checking contextIsolation setting..."
if grep -q "contextIsolation: true" apps/colima-desktop-ui/src/main/index.ts; then
  pass "contextIsolation enabled"
else
  fail "contextIsolation not enabled"
  exit 1
fi

# Check 5: nodeIntegration disabled
echo "5. Checking nodeIntegration setting..."
if grep -q "nodeIntegration: false" apps/colima-desktop-ui/src/main/index.ts; then
  pass "nodeIntegration disabled"
else
  fail "nodeIntegration not disabled"
  exit 1
fi

# Check 6: sandbox enabled
echo "6. Checking sandbox setting..."
if grep -q "sandbox: true" apps/colima-desktop-ui/src/main/index.ts; then
  pass "Sandbox enabled"
else
  fail "Sandbox not enabled"
  exit 1
fi

# Check 7: CSP headers present
echo "7. Checking Content-Security-Policy..."
if grep -q "Content-Security-Policy" apps/colima-desktop-ui/src/renderer/index.html; then
  pass "CSP headers defined in index.html"
else
  warn "CSP headers not found in index.html"
fi

# Check 8: localhost-only daemon
echo "8. Checking daemon URL hardcoded to localhost..."
if grep -q "const BASE_URL = 'http://localhost:35100'" apps/colima-desktop-ui/src/main/ipc-handlers.ts; then
  pass "Daemon URL hardcoded to localhost"
else
  fail "Daemon URL not hardcoded to localhost - network exposure risk"
  exit 1
fi

# Check 9: contextBridge usage
echo "9. Checking contextBridge usage in preload..."
if grep -q "contextBridge.exposeInMainWorld" apps/colima-desktop-ui/src/main/preload.ts; then
  pass "contextBridge used in preload script"
else
  fail "contextBridge not used - IPC not properly isolated"
  exit 1
fi

# Check 10: Minimal IPC surface
echo "10. Checking IPC method count..."
IPC_COUNT=$(grep -c "ipcRenderer.invoke" apps/colima-desktop-ui/src/main/preload.ts || echo "0")
if [ "$IPC_COUNT" -le 10 ]; then
  pass "IPC surface area is minimal ($IPC_COUNT methods)"
else
  warn "IPC surface area is large ($IPC_COUNT methods) - review for necessity"
fi

# Check 11: Dependency audit (informational)
echo "11. Running dependency audit..."
cd apps/colima-desktop-ui
AUDIT_OUTPUT=$(pnpm audit 2>&1 || true)
if echo "$AUDIT_OUTPUT" | grep -q "0 vulnerabilities"; then
  pass "No vulnerabilities in dependencies"
elif echo "$AUDIT_OUTPUT" | grep -q "critical\|high"; then
  fail "HIGH or CRITICAL vulnerabilities found - run 'pnpm audit' for details"
  echo "$AUDIT_OUTPUT" | grep -A 5 "critical\|high"
else
  warn "Low/moderate vulnerabilities found - review with 'pnpm audit'"
fi
cd ../..

echo ""
echo "=================================================="
echo -e "${GREEN}🎉 Security checks completed!${NC}"
echo ""
echo "See apps/colima-desktop-ui/SECURITY.md for full audit report"
