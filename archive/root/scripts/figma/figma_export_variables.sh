#!/usr/bin/env bash
# =============================================================================
# Figma Variables Export Script
# =============================================================================
# Exports design variables (tokens) from Figma using the Variables REST API.
# Note: This API is only available to full members of Enterprise orgs.
#
# Usage:
#   ./scripts/figma/figma_export_variables.sh [output_dir]
#
# Environment variables required:
#   FIGMA_ACCESS_TOKEN - Personal Access Token with File content (Read) scope
#   FIGMA_FILE_KEY     - The file key from Figma URL
#
# Output:
#   - variables.local.json   - All local variables
#   - variables.published.json - Published library variables (if accessible)
#   - tokens.json            - Transformed design tokens format
#
# Exit codes:
#   0 - Success
#   1 - Missing environment variables
#   2 - API error (likely plan limitation)
#   3 - Partial success (some exports failed)
# =============================================================================
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
OUT_DIR="${1:-artifacts/figma}"
mkdir -p "$OUT_DIR"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Figma Variables Export${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# =============================================================================
# Validate environment
# =============================================================================
if [[ -z "${FIGMA_ACCESS_TOKEN:-}" ]]; then
    echo -e "${RED}Error: FIGMA_ACCESS_TOKEN is not set${NC}"
    echo ""
    echo "To create a Personal Access Token:"
    echo "  1. Go to https://www.figma.com/developers/api#access-tokens"
    echo "  2. Create token with 'File content (Read)' scope"
    echo "  3. Export: export FIGMA_ACCESS_TOKEN=figd_xxx"
    exit 1
fi

if [[ -z "${FIGMA_FILE_KEY:-}" ]]; then
    echo -e "${RED}Error: FIGMA_FILE_KEY is not set${NC}"
    echo ""
    echo "The file key is in the Figma URL:"
    echo "  https://www.figma.com/file/<FILE_KEY>/..."
    echo ""
    echo "Export: export FIGMA_FILE_KEY=xxxxx"
    exit 1
fi

echo -e "File Key: ${FIGMA_FILE_KEY}"
echo -e "Output:   ${OUT_DIR}/"
echo ""

# =============================================================================
# Export local variables
# =============================================================================
echo -e "${BLUE}[1/3] Exporting local variables...${NC}"

LOCAL_VARS_RESPONSE=$(curl -sS -w "\n%{http_code}" \
    -H "Authorization: Bearer ${FIGMA_ACCESS_TOKEN}" \
    "https://api.figma.com/v1/files/${FIGMA_FILE_KEY}/variables/local" 2>&1) || true

HTTP_CODE=$(echo "$LOCAL_VARS_RESPONSE" | tail -n1)
BODY=$(echo "$LOCAL_VARS_RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" == "200" ]]; then
    echo "$BODY" | jq '.' > "${OUT_DIR}/variables.local.json"
    VAR_COUNT=$(echo "$BODY" | jq '.meta.variables | length // 0')
    COLLECTION_COUNT=$(echo "$BODY" | jq '.meta.variableCollections | length // 0')
    echo -e "${GREEN}  ✓ Exported ${VAR_COUNT} variables in ${COLLECTION_COUNT} collections${NC}"
    echo -e "    Wrote: ${OUT_DIR}/variables.local.json"
elif [[ "$HTTP_CODE" == "403" ]]; then
    ERROR_MSG=$(echo "$BODY" | jq -r '.err // .message // "Unknown error"')
    echo -e "${YELLOW}  ⚠ Variables API not available${NC}"
    echo -e "    Error: ${ERROR_MSG}"
    echo -e ""
    echo -e "    The Variables REST API is limited to full members of Enterprise orgs."
    echo -e "    Alternative approaches:"
    echo -e "    - Use the Figma plugin API (Variables Plugin)"
    echo -e "    - Export via Figma Tokens Studio plugin"
    echo -e "    - Use Code Connect for design-to-code mapping"
    echo ""
    # Create placeholder file
    echo '{"error": "Variables API requires Enterprise plan", "fallback": "Use Code Connect or Figma Tokens Studio"}' > "${OUT_DIR}/variables.local.json"
else
    echo -e "${RED}  ✗ API request failed (HTTP ${HTTP_CODE})${NC}"
    echo -e "    Response: ${BODY}"
    exit 2
fi

# =============================================================================
# Export published library variables (if accessible)
# =============================================================================
echo ""
echo -e "${BLUE}[2/3] Exporting published library variables...${NC}"

PUBLISHED_VARS_RESPONSE=$(curl -sS -w "\n%{http_code}" \
    -H "Authorization: Bearer ${FIGMA_ACCESS_TOKEN}" \
    "https://api.figma.com/v1/files/${FIGMA_FILE_KEY}/variables/published" 2>&1) || true

HTTP_CODE=$(echo "$PUBLISHED_VARS_RESPONSE" | tail -n1)
BODY=$(echo "$PUBLISHED_VARS_RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" == "200" ]]; then
    echo "$BODY" | jq '.' > "${OUT_DIR}/variables.published.json"
    VAR_COUNT=$(echo "$BODY" | jq '.meta.variables | length // 0')
    echo -e "${GREEN}  ✓ Exported ${VAR_COUNT} published variables${NC}"
    echo -e "    Wrote: ${OUT_DIR}/variables.published.json"
elif [[ "$HTTP_CODE" == "403" ]]; then
    echo -e "${YELLOW}  ⚠ Published variables not accessible (expected for non-Enterprise)${NC}"
    echo '{"error": "Published variables API requires Enterprise plan"}' > "${OUT_DIR}/variables.published.json"
else
    echo -e "${YELLOW}  ⚠ Could not fetch published variables (HTTP ${HTTP_CODE})${NC}"
fi

# =============================================================================
# Transform to design tokens format
# =============================================================================
echo ""
echo -e "${BLUE}[3/3] Transforming to design tokens format...${NC}"

# Check if we have valid local variables
if [[ -f "${OUT_DIR}/variables.local.json" ]] && \
   [[ $(jq -r '.meta.variables // empty' "${OUT_DIR}/variables.local.json" 2>/dev/null) != "" ]]; then

    # Transform Figma variables to W3C Design Tokens format
    jq '
    {
      "$schema": "https://tr.designtokens.org/format/",
      "figma": {
        "fileKey": env.FIGMA_FILE_KEY,
        "exportedAt": now | strftime("%Y-%m-%dT%H:%M:%SZ")
      },
      "collections": (
        .meta.variableCollections | to_entries | map({
          (.value.name): {
            "$type": "collection",
            "modes": .value.modes,
            "variableCount": (.value.variableIds | length)
          }
        }) | add
      ),
      "tokens": (
        .meta.variables | to_entries | map({
          (.value.name | gsub("/"; ".")): {
            "$type": (
              if .value.resolvedType == "COLOR" then "color"
              elif .value.resolvedType == "FLOAT" then "number"
              elif .value.resolvedType == "STRING" then "string"
              elif .value.resolvedType == "BOOLEAN" then "boolean"
              else .value.resolvedType | ascii_downcase
              end
            ),
            "$value": (
              .value.valuesByMode | to_entries | first | .value |
              if type == "object" and has("r") then
                "rgba(\(.r * 255 | floor), \(.g * 255 | floor), \(.b * 255 | floor), \(.a // 1))"
              else
                .
              end
            ),
            "$description": .value.description,
            "figmaId": .key
          }
        }) | add
      )
    }' "${OUT_DIR}/variables.local.json" > "${OUT_DIR}/tokens.json" 2>/dev/null || {
        echo -e "${YELLOW}  ⚠ Could not transform to tokens format (no valid variables)${NC}"
        echo '{"$schema": "https://tr.designtokens.org/format/", "tokens": {}, "note": "No variables available"}' > "${OUT_DIR}/tokens.json"
    }

    if [[ -s "${OUT_DIR}/tokens.json" ]]; then
        TOKEN_COUNT=$(jq '.tokens | length // 0' "${OUT_DIR}/tokens.json")
        echo -e "${GREEN}  ✓ Generated ${TOKEN_COUNT} design tokens${NC}"
        echo -e "    Wrote: ${OUT_DIR}/tokens.json"
    fi
else
    echo -e "${YELLOW}  ⚠ Skipped - no valid variables to transform${NC}"
    echo '{"$schema": "https://tr.designtokens.org/format/", "tokens": {}, "note": "Variables API not available on this plan"}' > "${OUT_DIR}/tokens.json"
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Export Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  Output directory: ${OUT_DIR}/"
echo ""
ls -la "${OUT_DIR}/"*.json 2>/dev/null | while read line; do
    echo "  ${line}"
done
echo ""
echo -e "${GREEN}Done.${NC}"
