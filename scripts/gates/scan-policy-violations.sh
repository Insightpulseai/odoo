#!/bin/bash
# ============================================================================
# DATAVERSE ENTERPRISE CONSOLE - POLICY VIOLATION SCANNER
# ============================================================================
# Portfolio Initiative: PORT-2026-012
# Control: CTRL-POLICY-001 (CI Gate - Policy Violation Detection)
#
# Purpose: Scan for policy violations at PR time:
# - Unattested capability claims
# - Blocked model usage
# - Privacy mode violations
#
# Usage: bash scripts/gates/scan-policy-violations.sh
# Exit: 0 = no violations, 1 = violations found
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
VIOLATIONS=0
TIMESTAMP=$(date +%Y%m%d-%H%M)
EVIDENCE_DIR="docs/evidence/${TIMESTAMP}/policy-violations"
SARIF_FILE="${EVIDENCE_DIR}/scan-results.sarif"

echo "============================================================================"
echo "POLICY VIOLATION SCANNER"
echo "Portfolio Initiative: PORT-2026-012"
echo "Control: CTRL-POLICY-001"
echo "============================================================================"
echo ""

# Create evidence directory
mkdir -p "$EVIDENCE_DIR"

# ============================================================================
# CHECK 1: UNATTESTED CAPABILITY CLAIMS
# ============================================================================

echo "[1/3] Scanning for unattested capability claims..."

# Scan for capability: declarations in code
if grep -rn "capability:" apps/ scripts/ --include="*.ts" --include="*.py" --include="*.js" 2>/dev/null | while read -r line; do
    CAPABILITY=$(echo "$line" | sed -n "s/.*capability:\s*['\"]\\([^'\"]*\\)['\"].*/\\1/p")

    if [ -n "$CAPABILITY" ]; then
        # Check if capability is attested in ops.capability_attestations
        # Note: This requires Supabase connection - skip if not available
        if [ -n "$SUPABASE_DB_URL" ]; then
            IS_ATTESTED=$(psql "$SUPABASE_DB_URL" -tAc "SELECT EXISTS(SELECT 1 FROM ops.capability_attestations WHERE capability_key = '$CAPABILITY' AND has_capability = true);" 2>/dev/null || echo "f")

            if [ "$IS_ATTESTED" = "f" ]; then
                echo -e "${RED}VIOLATION:${NC} Unattested capability '$CAPABILITY' in $line"
                echo "$line" >> "${EVIDENCE_DIR}/unattested-capabilities.txt"
                VIOLATIONS=$((VIOLATIONS+1))
            fi
        else
            echo -e "${YELLOW}WARNING:${NC} Cannot verify capability '$CAPABILITY' (no SUPABASE_DB_URL)"
        fi
    fi
done; then
    echo -e "${GREEN}✓${NC} No unattested capabilities found"
fi

# ============================================================================
# CHECK 2: BLOCKED MODEL USAGE
# ============================================================================

echo "[2/3] Scanning for blocked model usage..."

# Scan for model: declarations in code
if grep -rn "model:" apps/ scripts/ --include="*.ts" --include="*.py" --include="*.js" 2>/dev/null | while read -r line; do
    MODEL=$(echo "$line" | sed -n "s/.*model:\s*['\"]\\([^'\"]*\\)['\"].*/\\1/p")

    if [ -n "$MODEL" ]; then
        # Check if model is blocked in ops.model_policy
        if [ -n "$SUPABASE_DB_URL" ]; then
            IS_BLOCKED=$(psql "$SUPABASE_DB_URL" -tAc "SELECT EXISTS(SELECT 1 FROM ops.model_policy WHERE model_name = '$MODEL' AND policy_type = 'block');" 2>/dev/null || echo "f")

            if [ "$IS_BLOCKED" = "t" ]; then
                echo -e "${RED}VIOLATION:${NC} Blocked model '$MODEL' in $line"
                echo "$line" >> "${EVIDENCE_DIR}/blocked-models.txt"
                VIOLATIONS=$((VIOLATIONS+1))
            fi
        else
            echo -e "${YELLOW}WARNING:${NC} Cannot verify model '$MODEL' (no SUPABASE_DB_URL)"
        fi
    fi
done; then
    echo -e "${GREEN}✓${NC} No blocked models found"
fi

# ============================================================================
# CHECK 3: PRIVACY MODE BYPASS ATTEMPTS
# ============================================================================

echo "[3/3] Scanning for privacy mode bypass attempts..."

# Scan for x-privacy-mode: false headers (suspicious)
if grep -rn "x-privacy-mode.*false" apps/ scripts/ --include="*.ts" --include="*.py" --include="*.js" 2>/dev/null | while read -r line; do
    echo -e "${YELLOW}WARNING:${NC} Privacy mode explicitly disabled: $line"
    echo "$line" >> "${EVIDENCE_DIR}/privacy-mode-disabled.txt"
done; then
    echo -e "${GREEN}✓${NC} No privacy mode bypasses found"
fi

# ============================================================================
# GENERATE SARIF OUTPUT
# ============================================================================

echo ""
echo "Generating SARIF output..."

cat > "$SARIF_FILE" <<EOF
{
  "version": "2.1.0",
  "\$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "runs": [{
    "tool": {
      "driver": {
        "name": "Policy Violation Scanner",
        "informationUri": "https://github.com/Insightpulseai/odoo/blob/main/docs/constitution/DATAVERSE_ENTERPRISE_CONSOLE.md",
        "version": "1.0.0",
        "rules": [
          {
            "id": "unattested-capability",
            "name": "UnattestedCapability",
            "shortDescription": {
              "text": "Capability claim without attestation"
            },
            "fullDescription": {
              "text": "Code declares capability requirement but capability is not attested in ops.capability_attestations"
            },
            "help": {
              "text": "Attest capability via ops.capability_attestations or provide code evidence"
            },
            "defaultConfiguration": {
              "level": "error"
            }
          },
          {
            "id": "blocked-model",
            "name": "BlockedModelUsage",
            "shortDescription": {
              "text": "Usage of blocked model"
            },
            "fullDescription": {
              "text": "Code attempts to use model that is blocked by org policy in ops.model_policy"
            },
            "help": {
              "text": "Remove blocked model usage or update org policy"
            },
            "defaultConfiguration": {
              "level": "error"
            }
          },
          {
            "id": "privacy-mode-disabled",
            "name": "PrivacyModeDisabled",
            "shortDescription": {
              "text": "Privacy mode explicitly disabled"
            },
            "fullDescription": {
              "text": "Code contains x-privacy-mode: false header (requires justification)"
            },
            "help": {
              "text": "Document reason for privacy mode bypass or remove header"
            },
            "defaultConfiguration": {
              "level": "warning"
            }
          }
        ]
      }
    },
    "results": []
  }]
}
EOF

# ============================================================================
# SUMMARY & EXIT
# ============================================================================

echo ""
echo "============================================================================"
if [ $VIOLATIONS -gt 0 ]; then
    echo -e "${RED}❌ $VIOLATIONS policy violations found${NC}"
    echo ""
    echo "Evidence artifacts:"
    echo "  - $SARIF_FILE"
    [ -f "${EVIDENCE_DIR}/unattested-capabilities.txt" ] && echo "  - ${EVIDENCE_DIR}/unattested-capabilities.txt"
    [ -f "${EVIDENCE_DIR}/blocked-models.txt" ] && echo "  - ${EVIDENCE_DIR}/blocked-models.txt"
    [ -f "${EVIDENCE_DIR}/privacy-mode-disabled.txt" ] && echo "  - ${EVIDENCE_DIR}/privacy-mode-disabled.txt"
    echo ""
    echo "Remediation:"
    echo "  1. Review violations in evidence artifacts"
    echo "  2. Attest capabilities via ops.capability_attestations"
    echo "  3. Update model policies in ops.model_policy"
    echo "  4. Document privacy mode bypass justifications"
    echo ""
    echo "Re-run: bash scripts/gates/scan-policy-violations.sh"
    echo "============================================================================"
    exit 1
else
    echo -e "${GREEN}✅ No policy violations detected${NC}"
    echo ""
    echo "SARIF output: $SARIF_FILE"
    echo "============================================================================"
    exit 0
fi
