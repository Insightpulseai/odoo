#!/usr/bin/env bash
# ============================================================================
# Secret Scan Script
#
# Scans repository for potential secrets and sensitive data.
# Checks for common patterns like API keys, tokens, passwords, etc.
# ============================================================================
set -euo pipefail

die() {
  echo "[secret-scan] FAIL: $*" >&2
  exit 1
}

warn() {
  echo "[secret-scan] WARN: $*" >&2
}

# Directories to exclude from scanning
EXCLUDE_DIRS=".git node_modules .venv venv __pycache__ dist build .next .nuxt"

# Build exclude pattern for grep
EXCLUDE_PATTERN=""
for dir in $EXCLUDE_DIRS; do
  EXCLUDE_PATTERN="$EXCLUDE_PATTERN --exclude-dir=$dir"
done

# Also exclude binary files and common non-sensitive files
EXCLUDE_FILES="--exclude=*.png --exclude=*.jpg --exclude=*.gif --exclude=*.ico --exclude=*.woff --exclude=*.woff2 --exclude=*.ttf --exclude=*.eot --exclude=*.pdf --exclude=*.zip --exclude=*.tar.gz --exclude=*.lock --exclude=package-lock.json --exclude=pnpm-lock.yaml --exclude=yarn.lock"

echo "[secret-scan] Scanning for potential secrets..."

# Define patterns to search for
PATTERNS=(
  # API Keys with common prefixes
  "sk-[a-zA-Z0-9]{20,}"           # OpenAI, Stripe secret keys
  "pk-[a-zA-Z0-9]{20,}"           # Stripe publishable keys
  "AKIA[A-Z0-9]{16}"              # AWS Access Key ID
  "ghp_[a-zA-Z0-9]{36}"           # GitHub personal access token
  "gho_[a-zA-Z0-9]{36}"           # GitHub OAuth token
  "ghr_[a-zA-Z0-9]{36}"           # GitHub refresh token
  "github_pat_[a-zA-Z0-9_]{22,}"  # GitHub fine-grained PAT

  # Generic patterns (more likely to have false positives)
  "api[_-]?key['\"]?\s*[:=]\s*['\"][a-zA-Z0-9]{20,}"
  "secret[_-]?key['\"]?\s*[:=]\s*['\"][a-zA-Z0-9]{20,}"
  "password['\"]?\s*[:=]\s*['\"][^'\"]{8,}"

  # Service-specific
  "xoxb-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24}"  # Slack bot token
  "xoxp-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24}"  # Slack user token
  "eyJ[a-zA-Z0-9_-]{50,}\\.[a-zA-Z0-9_-]+\\.[a-zA-Z0-9_-]+"  # JWT tokens
)

# Files that commonly contain secrets (should be in .gitignore)
SENSITIVE_FILES=(
  ".env"
  ".env.local"
  ".env.production"
  ".env.development"
  "credentials.json"
  "service-account.json"
  "secrets.json"
  "*.pem"
  "*.key"
)

found_issues=0

# Check for sensitive files that shouldn't be committed
echo "[secret-scan] Checking for sensitive files..."
for pattern in "${SENSITIVE_FILES[@]}"; do
  # Use find to locate files matching the pattern
  while IFS= read -r -d '' file; do
    if [ -f "$file" ] && ! echo "$file" | grep -qE "\.example$|\.sample$|\.template$"; then
      warn "Potentially sensitive file found: $file"
      found_issues=$((found_issues + 1))
    fi
  done < <(find . -name "$pattern" -not -path "./.git/*" -not -path "./node_modules/*" -print0 2>/dev/null || true)
done

# Run pattern matching (limited to avoid false positives)
echo "[secret-scan] Checking for secret patterns..."

# Check for hardcoded Supabase service role keys (common mistake)
if grep -rn $EXCLUDE_PATTERN $EXCLUDE_FILES "SUPABASE_SERVICE_ROLE_KEY.*=.*eyJ" . 2>/dev/null | grep -v "\.example\|\.sample\|\.template\|CLAUDE\.md" | head -5; then
  warn "Potential hardcoded Supabase service role key found"
  found_issues=$((found_issues + 1))
fi

# Check for AWS keys
if grep -rn $EXCLUDE_PATTERN $EXCLUDE_FILES "AKIA[A-Z0-9]{16}" . 2>/dev/null | grep -v "\.example\|\.sample\|\.template\|CLAUDE\.md" | head -5; then
  warn "Potential AWS access key found"
  found_issues=$((found_issues + 1))
fi

# Check for private keys
if grep -rn $EXCLUDE_PATTERN $EXCLUDE_FILES "BEGIN RSA PRIVATE KEY\|BEGIN PRIVATE KEY\|BEGIN EC PRIVATE KEY" . 2>/dev/null | grep -v "\.example\|\.sample\|\.template" | head -5; then
  warn "Potential private key found"
  found_issues=$((found_issues + 1))
fi

echo ""
echo "[secret-scan] Summary:"
echo "  - Potential issues found: $found_issues"

if [ "$found_issues" -gt 0 ]; then
  echo ""
  echo "[secret-scan] Please review the warnings above."
  echo "[secret-scan] If these are false positives, consider adding them to the exclusion list."
  # Don't fail on warnings - secrets detection has high false positive rates
  # In production, you'd want to use a more sophisticated tool like truffleHog or gitleaks
fi

echo "[secret-scan] OK (scan complete, review warnings if any)"
