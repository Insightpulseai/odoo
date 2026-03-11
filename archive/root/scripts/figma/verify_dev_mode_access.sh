#!/usr/bin/env bash
# =============================================================================
# Figma Dev Mode Access Verification Script
# =============================================================================
# Verifies that the current Figma Personal Access Token has the required
# permissions for Dev Mode features including Code Connect and Variables API.
#
# Usage:
#   ./scripts/figma/verify_dev_mode_access.sh
#
# Prerequisites:
#   - FIGMA_ACCESS_TOKEN environment variable set
#   - jq installed for JSON parsing
#
# Exit codes:
#   0 - All checks passed
#   1 - Token validation failed
#   2 - Missing dependencies
#   3 - Partial access (some features unavailable)
# =============================================================================
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Output directory for results
EVIDENCE_DIR="${1:-artifacts/figma}"
mkdir -p "$EVIDENCE_DIR"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Figma Dev Mode Access Verification${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Track overall status
STATUS="pass"
WARNINGS=()

# =============================================================================
# Dependency check
# =============================================================================
echo -e "${BLUE}[1/5] Checking dependencies...${NC}"

if ! command -v jq &> /dev/null; then
    echo -e "${RED}  ✗ jq is required but not installed${NC}"
    echo "    Install with: apt-get install jq / brew install jq"
    exit 2
fi
echo -e "${GREEN}  ✓ jq installed${NC}"

if ! command -v curl &> /dev/null; then
    echo -e "${RED}  ✗ curl is required but not installed${NC}"
    exit 2
fi
echo -e "${GREEN}  ✓ curl installed${NC}"

# =============================================================================
# Token validation
# =============================================================================
echo ""
echo -e "${BLUE}[2/5] Validating FIGMA_ACCESS_TOKEN...${NC}"

if [[ -z "${FIGMA_ACCESS_TOKEN:-}" ]]; then
    echo -e "${RED}  ✗ FIGMA_ACCESS_TOKEN is not set${NC}"
    echo ""
    echo "  To set up Figma access:"
    echo "    1. Go to https://www.figma.com/developers/api#access-tokens"
    echo "    2. Create a Personal Access Token with scopes:"
    echo "       - File content (Read)"
    echo "       - Code Connect (Write)"
    echo "    3. Export it: export FIGMA_ACCESS_TOKEN=figd_xxx"
    exit 1
fi

# Token format check
if [[ ! "$FIGMA_ACCESS_TOKEN" =~ ^figd_ ]]; then
    echo -e "${YELLOW}  ⚠ Token doesn't start with 'figd_' - may be legacy format${NC}"
    WARNINGS+=("Token format may be outdated")
else
    echo -e "${GREEN}  ✓ Token format valid (figd_* format)${NC}"
fi

# =============================================================================
# API connectivity test
# =============================================================================
echo ""
echo -e "${BLUE}[3/5] Testing Figma API connectivity...${NC}"

# Get user info to validate token
USER_RESPONSE=$(curl -sS -w "\n%{http_code}" \
    -H "Authorization: Bearer ${FIGMA_ACCESS_TOKEN}" \
    "https://api.figma.com/v1/me" 2>&1) || true

HTTP_CODE=$(echo "$USER_RESPONSE" | tail -n1)
BODY=$(echo "$USER_RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" == "200" ]]; then
    USER_EMAIL=$(echo "$BODY" | jq -r '.email // "unknown"')
    USER_HANDLE=$(echo "$BODY" | jq -r '.handle // "unknown"')
    echo -e "${GREEN}  ✓ API connection successful${NC}"
    echo -e "    User: ${USER_HANDLE} (${USER_EMAIL})"

    # Save user info to evidence
    echo "$BODY" | jq '.' > "${EVIDENCE_DIR}/user_info.json"
elif [[ "$HTTP_CODE" == "403" ]]; then
    echo -e "${RED}  ✗ Token is invalid or expired (HTTP 403)${NC}"
    echo -e "    Response: $(echo "$BODY" | jq -r '.err // .message // "Unknown error"')"
    exit 1
elif [[ "$HTTP_CODE" == "401" ]]; then
    echo -e "${RED}  ✗ Token unauthorized (HTTP 401)${NC}"
    exit 1
else
    echo -e "${YELLOW}  ⚠ Unexpected response (HTTP ${HTTP_CODE})${NC}"
    echo -e "    Body: ${BODY}"
    WARNINGS+=("Unexpected API response code: ${HTTP_CODE}")
fi

# =============================================================================
# File access check (if FIGMA_FILE_KEY is set)
# =============================================================================
echo ""
echo -e "${BLUE}[4/5] Testing file access permissions...${NC}"

if [[ -z "${FIGMA_FILE_KEY:-}" ]]; then
    echo -e "${YELLOW}  ⚠ FIGMA_FILE_KEY not set - skipping file access test${NC}"
    echo "    Set FIGMA_FILE_KEY to test file-specific permissions"
    WARNINGS+=("File access not tested - FIGMA_FILE_KEY not set")
else
    FILE_RESPONSE=$(curl -sS -w "\n%{http_code}" \
        -H "Authorization: Bearer ${FIGMA_ACCESS_TOKEN}" \
        "https://api.figma.com/v1/files/${FIGMA_FILE_KEY}?depth=1" 2>&1) || true

    HTTP_CODE=$(echo "$FILE_RESPONSE" | tail -n1)
    BODY=$(echo "$FILE_RESPONSE" | sed '$d')

    if [[ "$HTTP_CODE" == "200" ]]; then
        FILE_NAME=$(echo "$BODY" | jq -r '.name // "unknown"')
        LAST_MODIFIED=$(echo "$BODY" | jq -r '.lastModified // "unknown"')
        echo -e "${GREEN}  ✓ File access confirmed${NC}"
        echo -e "    File: ${FILE_NAME}"
        echo -e "    Last modified: ${LAST_MODIFIED}"

        # Save file metadata to evidence
        echo "$BODY" | jq '{name, lastModified, version, role}' > "${EVIDENCE_DIR}/file_info.json"
    elif [[ "$HTTP_CODE" == "404" ]]; then
        echo -e "${RED}  ✗ File not found or no access (HTTP 404)${NC}"
        STATUS="fail"
    elif [[ "$HTTP_CODE" == "403" ]]; then
        echo -e "${RED}  ✗ No permission to access file (HTTP 403)${NC}"
        echo -e "    You need at least View access to the file"
        STATUS="fail"
    else
        echo -e "${YELLOW}  ⚠ Unexpected file response (HTTP ${HTTP_CODE})${NC}"
        WARNINGS+=("File access check returned: ${HTTP_CODE}")
    fi
fi

# =============================================================================
# Variables API check (Enterprise only)
# =============================================================================
echo ""
echo -e "${BLUE}[5/5] Testing Variables API access (Enterprise feature)...${NC}"

if [[ -z "${FIGMA_FILE_KEY:-}" ]]; then
    echo -e "${YELLOW}  ⚠ Skipped - FIGMA_FILE_KEY required${NC}"
else
    VARS_RESPONSE=$(curl -sS -w "\n%{http_code}" \
        -H "Authorization: Bearer ${FIGMA_ACCESS_TOKEN}" \
        "https://api.figma.com/v1/files/${FIGMA_FILE_KEY}/variables/local" 2>&1) || true

    HTTP_CODE=$(echo "$VARS_RESPONSE" | tail -n1)
    BODY=$(echo "$VARS_RESPONSE" | sed '$d')

    if [[ "$HTTP_CODE" == "200" ]]; then
        VAR_COUNT=$(echo "$BODY" | jq '.meta.variables | length // 0')
        COLLECTION_COUNT=$(echo "$BODY" | jq '.meta.variableCollections | length // 0')
        echo -e "${GREEN}  ✓ Variables API accessible (Enterprise plan confirmed)${NC}"
        echo -e "    Variables: ${VAR_COUNT}"
        echo -e "    Collections: ${COLLECTION_COUNT}"

        # Save variables metadata
        echo "$BODY" > "${EVIDENCE_DIR}/variables.local.json"
    elif [[ "$HTTP_CODE" == "403" ]]; then
        ERROR_MSG=$(echo "$BODY" | jq -r '.err // .message // "Unknown"')
        echo -e "${YELLOW}  ⚠ Variables API not available (likely not Enterprise plan)${NC}"
        echo -e "    Message: ${ERROR_MSG}"
        echo -e "    Note: Variables REST API requires Enterprise org membership"
        WARNINGS+=("Variables API unavailable - use Code Connect fallback")
    else
        echo -e "${YELLOW}  ⚠ Variables API returned HTTP ${HTTP_CODE}${NC}"
        WARNINGS+=("Variables API check failed: ${HTTP_CODE}")
    fi
fi

# =============================================================================
# Dev Mode seat requirements info
# =============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Dev Mode Access Requirements${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  Dev Mode requires one of the following seat types:"
echo ""
echo "  ┌─────────────────────────────────────────────────────────────────┐"
echo "  │  Seat Type  │  Dev Mode  │  Variables API  │  Code Connect    │"
echo "  ├─────────────────────────────────────────────────────────────────┤"
echo "  │  Full       │     ✓      │    Enterprise   │        ✓         │"
echo "  │  Dev        │     ✓      │    Enterprise   │        ✓         │"
echo "  │  Collab     │     ✗      │        ✗        │        ✗         │"
echo "  │  View-only  │     ✗      │        ✗        │        ✗         │"
echo "  └─────────────────────────────────────────────────────────────────┘"
echo ""
echo "  Toggle Dev Mode in Figma: Shift + D"
echo ""

# =============================================================================
# Generate verification report
# =============================================================================
REPORT_FILE="${EVIDENCE_DIR}/dev_mode_access_report.json"

cat > "$REPORT_FILE" << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "status": "${STATUS}",
  "checks": {
    "dependencies": "pass",
    "token_format": "$(if [[ "$FIGMA_ACCESS_TOKEN" =~ ^figd_ ]]; then echo "pass"; else echo "warn"; fi)",
    "api_connectivity": "$(if [[ "$HTTP_CODE" == "200" ]]; then echo "pass"; else echo "fail"; fi)",
    "file_access": "$(if [[ -z "${FIGMA_FILE_KEY:-}" ]]; then echo "skipped"; elif [[ -f "${EVIDENCE_DIR}/file_info.json" ]]; then echo "pass"; else echo "fail"; fi)",
    "variables_api": "$(if [[ -f "${EVIDENCE_DIR}/variables.local.json" ]]; then echo "pass"; else echo "unavailable"; fi)"
  },
  "warnings": $(printf '%s\n' "${WARNINGS[@]:-}" | jq -R . | jq -s .),
  "evidence_files": [
    "user_info.json",
    "file_info.json",
    "variables.local.json"
  ],
  "recommendations": [
    "Ensure you have a Dev or Full seat for Dev Mode access",
    "Variables REST API requires Enterprise org membership",
    "Use Code Connect CLI for design-to-code mapping"
  ]
}
EOF

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Verification Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [[ "$STATUS" == "pass" ]]; then
    if [[ ${#WARNINGS[@]} -gt 0 ]]; then
        echo -e "${YELLOW}  Status: PASSED with warnings${NC}"
        for w in "${WARNINGS[@]}"; do
            echo -e "    ⚠ ${w}"
        done
        exit 3
    else
        echo -e "${GREEN}  Status: PASSED${NC}"
        echo -e "  All Figma Dev Mode access checks passed."
        exit 0
    fi
else
    echo -e "${RED}  Status: FAILED${NC}"
    echo -e "  One or more critical checks failed."
    exit 1
fi
