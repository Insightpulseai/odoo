#!/usr/bin/env bash
# =============================================================================
# scripts/repo_health.sh — Repo structure and hygiene gate
# Referenced by CLAUDE.md as mandatory pre-commit check
# =============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ERRORS=0

echo "=== Repo Health Check ==="
echo "Repo: ${REPO_ROOT}"
echo ""

# 1. Critical directory structure
echo "--- Directory Structure ---"
for dir in addons/ipai .devcontainer scripts docs spec ssot; do
  if [ -d "${REPO_ROOT}/${dir}" ]; then
    echo "  PASS  ${dir}/"
  else
    echo "  FAIL  ${dir}/ missing"
    ERRORS=$((ERRORS + 1))
  fi
done

# 2. Required root files
echo ""
echo "--- Required Files ---"
for f in CLAUDE.md .gitignore; do
  if [ -f "${REPO_ROOT}/${f}" ]; then
    echo "  PASS  ${f}"
  else
    echo "  FAIL  ${f} missing"
    ERRORS=$((ERRORS + 1))
  fi
done

# 3. No secrets in staged files
echo ""
echo "--- Secrets Check (staged files) ---"
STAGED=$(git -C "${REPO_ROOT}" diff --cached --name-only 2>/dev/null || true)
if [ -n "${STAGED}" ]; then
  # Check for common secret patterns in staged diffs
  SECRET_HITS=$(git -C "${REPO_ROOT}" diff --cached -U0 2>/dev/null | \
    grep -iE '(password|secret|token|api_key|private_key)\s*[:=]\s*["\x27][^"\x27]{8,}' | \
    grep -v '\.example' | grep -v '#.*password' | grep -v 'placeholder' || true)
  if [ -n "${SECRET_HITS}" ]; then
    echo "  FAIL  Potential secrets in staged changes:"
    echo "${SECRET_HITS}" | head -5
    ERRORS=$((ERRORS + 1))
  else
    echo "  PASS  No secrets detected in staged changes"
  fi
else
  echo "  SKIP  No staged files"
fi

# 4. No deprecated system references in new/modified files
echo ""
echo "--- Deprecated System Check (staged files) ---"
if [ -n "${STAGED}" ]; then
  DEPRECATED_HITS=$(echo "${STAGED}" | while read -r file; do
    if [ -f "${REPO_ROOT}/${file}" ]; then
      grep -lnE '(supabase|insightpulseai\.net|mailgun|mg\.insightpulseai|digitalocean)' \
        "${REPO_ROOT}/${file}" 2>/dev/null || true
    fi
  done | grep -v 'CLAUDE.md' | grep -v 'deprecated' | grep -v 'MEMORY' | grep -v 'docs/wiki' || true)
  if [ -n "${DEPRECATED_HITS}" ]; then
    echo "  WARN  Deprecated references found (review manually):"
    echo "${DEPRECATED_HITS}" | head -5
  else
    echo "  PASS  No deprecated system references"
  fi
else
  echo "  SKIP  No staged files"
fi

# 5. IPAI module completeness (spot check staged modules)
echo ""
echo "--- Module Completeness (staged ipai_* modules) ---"
MODULE_DIRS=$(echo "${STAGED}" | grep '^addons/ipai/' | cut -d'/' -f3 | sort -u 2>/dev/null || true)
if [ -n "${MODULE_DIRS}" ]; then
  for mod in ${MODULE_DIRS}; do
    MOD_PATH="${REPO_ROOT}/addons/ipai/${mod}"
    if [ -d "${MOD_PATH}" ]; then
      MISSING=""
      [ ! -f "${MOD_PATH}/__manifest__.py" ] && MISSING="${MISSING} __manifest__.py"
      [ ! -f "${MOD_PATH}/README.md" ] && MISSING="${MISSING} README.md"
      if [ -n "${MISSING}" ]; then
        echo "  WARN  ${mod}: missing${MISSING}"
      else
        echo "  PASS  ${mod}"
      fi
    fi
  done
else
  echo "  SKIP  No ipai modules in staged files"
fi

# Summary
echo ""
echo "==========================="
if [ ${ERRORS} -gt 0 ]; then
  echo "FAIL: ${ERRORS} error(s) found"
  exit 1
else
  echo "PASS: Repo health OK"
  exit 0
fi
