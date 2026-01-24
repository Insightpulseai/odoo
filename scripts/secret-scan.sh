#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "=== Secret Scan ==="

# Files that may contain public-safe client keys or otherwise acceptable patterns
ALLOWLIST_PATHS=(
  "config/config_keys.json"
  "scripts/secret-scan.sh"
  "*.md"
  # Supabase anon keys are public/safe for client-side
  "clients/flutter_receipt_ocr/lib/receipt_ocr/config.dart"
  "ops-control/utils/supabase/info.tsx"
)

is_allowlisted_file() {
  local f="$1"
  for p in "${ALLOWLIST_PATHS[@]}"; do
    # shellcheck disable=SC2053
    [[ "$f" == *"$p"* ]] && return 0
  done
  return 1
}

fail_with_matches() {
  local title="$1"
  shift
  local matches=("$@")
  echo -e "${RED}FOUND${NC}"
  printf '%s\n' "${matches[@]}"
  echo -e "${RED}FAIL:${NC} ${title}"
  exit 1
}

# Helper: rg list of files, then filter out allowlist globs
rg_files_filtered() {
  local pattern="$1"
  local files
  mapfile -t files < <(
    rg -l --no-ignore-vcs -g '!node_modules' -g '!.git' -g '!*.lock' -g '!.env.local' \
      "$pattern" "$REPO_ROOT" 2>/dev/null || true
  )

  local kept=()
  for f in "${files[@]}"; do
    if is_allowlisted_file "$f"; then
      continue
    fi
    kept+=("$f")
  done

  printf '%s\n' "${kept[@]}"
}

# Pattern 1: JWT-like tokens (eyJ...) — keep broad detection, exclude known public anon-key files + anon identifiers
echo -n "Checking for JWT tokens... "
mapfile -t jwt_files < <(
  rg_files_filtered 'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}'
)

# If any hits remain, double-check that they are not explicitly marked as anon/public identifiers in-code
if ((${#jwt_files[@]} > 0)); then
  # Re-scan content and check each match individually
  mapfile -t jwt_suspects < <(
    for file in "${jwt_files[@]}"; do
      # Skip markdown and example files
      [[ "$file" == *.md ]] && continue
      [[ "$file" == *.example ]] && continue
      [[ "$file" == *config_keys.json ]] && continue

      # Get JWT matches from this file with 2 lines of context before
      rg -n -B 2 -A 0 'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}' "$file" 2>/dev/null | {
        in_anon_block=false
        while IFS= read -r line; do
          # Check if this block contains anon key identifiers
          if [[ "$line" =~ (SUPABASE_ANON_KEY|anon[_-]?[Kk]ey|public[Aa]non[Kk]ey|supabaseAnonKey) ]]; then
            in_anon_block=true
          fi

          # If we hit a JWT line
          if [[ "$line" =~ eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,} ]]; then
            # Only output if we're not in an anon block
            if [[ "$in_anon_block" == "false" ]]; then
              echo "$line"
            fi
            # Reset for next match
            in_anon_block=false
          fi
        done
      }
    done
  )
  if ((${#jwt_suspects[@]} > 0)); then
    fail_with_matches "JWT-like token(s) detected (review/rotate if real secrets)" "${jwt_suspects[@]}"
  fi
fi
echo -e "${GREEN}OK${NC}"

# Pattern 1b: Service role key references (higher risk)
echo -n "Checking for Supabase service_role key usage... "
mapfile -t sr_hits < <(
  rg -n --no-ignore-vcs -g '!node_modules' -g '!.git' -g '!*.lock' -g '!.env.local' \
    '(SUPABASE_SERVICE_ROLE_KEY|service[_-]?role)' "$REPO_ROOT" 2>/dev/null \
    | grep -v -E '(\.example|\.md|config_keys\.json)' \
    || true
)
echo -e "${GREEN}OK${NC}"

# Pattern 2: AWS keys
echo -n "Checking for AWS keys... "
if rg -n --no-ignore-vcs -g '!node_modules' -g '!.git' -g '!*.lock' -g '!.env.local' \
  'AKIA[0-9A-Z]{16}' "$REPO_ROOT" 2>/dev/null | grep -v -E '(\.example|\.md|config_keys\.json)'; then
  echo -e "${RED}FOUND${NC}"
  exit 1
else
  echo -e "${GREEN}OK${NC}"
fi

# Pattern 3: Private keys
echo -n "Checking for private keys... "
if rg -n --no-ignore-vcs -g '!node_modules' -g '!.git' -g '!*.lock' -g '!.env.local' \
  'BEGIN (RSA|EC|OPENSSH|DSA) PRIVATE KEY' "$REPO_ROOT" 2>/dev/null \
  | grep -v -E '(\.example|\.md|config_keys\.json)' \
  | grep -v -E '^[^:]+:\d+:--' \
  | grep -v -E '(#|//|/\*).*BEGIN.*PRIVATE KEY'; then
  echo -e "${RED}FOUND${NC}"
  exit 1
else
  echo -e "${GREEN}OK${NC}"
fi

# Pattern 4: DigitalOcean tokens
echo -n "Checking for DO tokens... "
if rg -n --no-ignore-vcs -g '!node_modules' -g '!.git' -g '!*.lock' -g '!.env.local' \
  'dop_v1_[A-Za-z0-9]+' "$REPO_ROOT" 2>/dev/null | grep -v -E '(\.example|\.md|config_keys\.json)'; then
  echo -e "${RED}FOUND${NC}"
  exit 1
else
  echo -e "${GREEN}OK${NC}"
fi

# Pattern 5: "hardcoded API key-ish" heuristics (keep conservative)
echo -n "Checking for hardcoded API keys... "
if rg -n --no-ignore-vcs -g '!node_modules' -g '!.git' -g '!*.lock' -g '!.env.local' \
  -g '!*.woff' -g '!*.woff2' -g '!*.ttf' -g '!*.otf' -g '!*.po' -g '!*.pot' \
  -g '!*.sql' -g '!**/tests/**' -g '!**/test_*.py' \
  '(api[_-]?key|secret|token)\s*(=|:)\s*["\x27][A-Za-z0-9_\-]{24,}["\x27]' "$REPO_ROOT" 2>/dev/null \
  | grep -v -E '(\.example|\.md|config_keys\.json)' \
  | grep -v -E '\$\{?[A-Z_]+\}?' \
  | grep -v -E '(x{5,}|-{5,}|\.\.\.|\*\*\*|secret_your_|your_|_here|_placeholder)' \
  | grep -v 'app_store_connect_api_key'; then
  echo -e "${RED}FOUND${NC}"
  exit 1
else
  echo -e "${GREEN}OK${NC}"
fi

echo "=== No secrets detected ==="
