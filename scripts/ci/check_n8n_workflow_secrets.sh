#!/usr/bin/env bash
set -euo pipefail

# n8n Workflow Secret Hygiene Checker
# Purpose: Detect hardcoded secrets in n8n workflow JSON exports
# Usage: ./check_n8n_workflow_secrets.sh [ci|pre-commit]

MODE="${1:-ci}"  # ci (exit 1 on violations) | pre-commit (advisory warnings)
WORKFLOW_DIR="automations/n8n/workflows"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Status markers
CHECK_PASS="✅"
CHECK_FAIL="❌"
CHECK_WARN="⚠️"

# Graceful skip if directory doesn't exist
if [[ ! -d "${WORKFLOW_DIR}" ]]; then
  echo -e "${CHECK_WARN} n8n workflow directory not found - skipping secret check"
  echo "  Directory: ${WORKFLOW_DIR}"
  exit 0
fi

# Check if ripgrep is available
if ! command -v rg &> /dev/null; then
  echo -e "${CHECK_FAIL} ripgrep not found - required for pattern matching"
  echo "  Install: sudo apt-get install ripgrep (Ubuntu) or brew install ripgrep (macOS)"
  exit 2
fi

# Secret patterns to detect (high-confidence only)
# Excludes: $env.VARIABLE references (legitimate n8n pattern)
declare -a PATTERNS=(
  # API keys and tokens
  '"api_key"\s*:\s*"(?!\$env\.)([^"]{10,})"'
  '"apiKey"\s*:\s*"(?!\$env\.)([^"]{10,})"'
  '"access_token"\s*:\s*"(?!\$env\.)([^"]{10,})"'
  '"accessToken"\s*:\s*"(?!\$env\.)([^"]{10,})"'
  '"client_secret"\s*:\s*"(?!\$env\.)([^"]{10,})"'
  '"clientSecret"\s*:\s*"(?!\$env\.)([^"]{10,})"'

  # Bearer tokens (JWT pattern)
  '"Authorization"\s*:\s*"Bearer\s+eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"'
  '"authorization"\s*:\s*"Bearer\s+eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"'

  # Supabase specific tokens
  'sbp_[A-Za-z0-9]{40,}'  # Personal access tokens
  '"service_role"\s*:\s*"eyJ[A-Za-z0-9_-]{100,}"'  # Service role keys (very long JWTs)

  # Generic passwords and secrets (8+ chars, not env refs)
  '"password"\s*:\s*"(?!\$env\.)([^"]{8,})"'
  '"secret"\s*:\s*"(?!\$env\.)([A-Za-z0-9]{20,})"'
)

# Track violations
VIOLATIONS=0
VIOLATION_FILES=()

# Scan each workflow file
echo "Scanning n8n workflows for hardcoded secrets..."
echo "Directory: ${WORKFLOW_DIR}"
echo ""

for pattern in "${PATTERNS[@]}"; do
  # Use ripgrep with JSON-aware line context
  matches=$(rg --json --pcre2 "${pattern}" "${WORKFLOW_DIR}" 2>/dev/null || true)

  if [[ -n "${matches}" ]]; then
    # Process JSON output line by line
    while IFS= read -r line; do
      type=$(echo "${line}" | jq -r '.type // empty')

      if [[ "${type}" == "match" ]]; then
        file=$(echo "${line}" | jq -r '.data.path.text')
        line_num=$(echo "${line}" | jq -r '.data.line_number')
        line_text=$(echo "${line}" | jq -r '.data.lines.text')

        # Track unique violation files
        if [[ ! " ${VIOLATION_FILES[@]} " =~ " ${file} " ]]; then
          VIOLATION_FILES+=("${file}")
        fi

        VIOLATIONS=$((VIOLATIONS + 1))

        # Print violation details
        echo -e "${CHECK_FAIL} ${RED}Hardcoded secret detected${NC}"
        echo "  File: ${file}:${line_num}"
        echo "  Pattern: ${pattern}"
        echo "  Context: ${line_text}"
        echo ""
      fi
    done <<< "${matches}"
  fi
done

# Summary and exit
echo "----------------------------------------"
if [[ ${VIOLATIONS} -eq 0 ]]; then
  echo -e "${CHECK_PASS} ${GREEN}No hardcoded secrets detected${NC}"
  echo "  Scanned: ${WORKFLOW_DIR}/*.json"
  exit 0
else
  echo -e "${CHECK_FAIL} ${RED}Found ${VIOLATIONS} hardcoded secret(s) in ${#VIOLATION_FILES[@]} file(s)${NC}"
  echo ""
  echo "Remediation Steps:"
  echo "  1. Replace hardcoded secrets with n8n credential IDs or environment variables"
  echo "  2. Use \$env.VARIABLE_NAME for environment variable references"
  echo "  3. Use n8n credentials system for API keys and tokens"
  echo "  4. Never commit actual secret values to git"
  echo ""
  echo "Example Fix:"
  echo "  BAD:  \"api_key\": \"hardcoded_secret_value\""
  echo "  GOOD: \"api_key\": \"\$env.API_KEY\""
  echo "  GOOD: Use n8n credential node with credential ID"
  echo ""

  if [[ "${MODE}" == "pre-commit" ]]; then
    echo -e "${CHECK_WARN} ${YELLOW}Pre-commit advisory: Please fix before committing${NC}"
    exit 0  # Advisory only
  else
    echo "CI Mode: Blocking merge until secrets are removed"
    exit 1
  fi
fi
