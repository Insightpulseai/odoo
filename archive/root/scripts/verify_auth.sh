#!/usr/bin/env bash
# verify_auth.sh — Verify auth module structure and installability
# Usage: ./scripts/verify_auth.sh
# Exit 0 = all checks pass, Exit 1 = at least one failure
set -euo pipefail

PASS=0
FAIL=0

check() {
  local name="$1"
  shift
  if "$@" > /dev/null 2>&1; then
    echo "  PASS  $name"
    PASS=$((PASS + 1))
  else
    echo "  FAIL  $name"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== Auth Module Verification ==="
echo ""

# File existence
check "Module manifest exists" test -f addons/ipai/ipai_auth_oidc/__manifest__.py
check "Module init exists"     test -f addons/ipai/ipai_auth_oidc/__init__.py
check "Provider data XML exists" test -f addons/ipai/ipai_auth_oidc/data/auth_provider_data.xml

# Python syntax
check "Manifest syntax valid" python3 -m py_compile addons/ipai/ipai_auth_oidc/__manifest__.py
check "Init syntax valid"     python3 -m py_compile addons/ipai/ipai_auth_oidc/__init__.py

# XML well-formedness
check "Provider XML well-formed" python3 -c "import xml.etree.ElementTree; xml.etree.ElementTree.parse('addons/ipai/ipai_auth_oidc/data/auth_provider_data.xml')"

# Manifest content checks
check "Depends on auth_totp" python3 -c "
m = eval(open('addons/ipai/ipai_auth_oidc/__manifest__.py').read())
assert 'auth_totp' in m['depends'], 'auth_totp not in depends'
"
check "Version starts with 19.0" python3 -c "
m = eval(open('addons/ipai/ipai_auth_oidc/__manifest__.py').read())
assert m['version'].startswith('19.0'), f'Version {m[\"version\"]} does not start with 19.0'
"
check "No hardcoded secrets" python3 -c "
import re
content = open('addons/ipai/ipai_auth_oidc/data/auth_provider_data.xml').read()
assert 'sk-' not in content and 'ghp_' not in content and 'gho_' not in content, 'Found hardcoded secret pattern'
"

echo ""
echo "=== Results: PASS=$PASS  FAIL=$FAIL ==="

if [ "$FAIL" -gt 0 ]; then
  echo "STATUS: FAIL"
  exit 1
fi

echo "STATUS: PASS"
exit 0
