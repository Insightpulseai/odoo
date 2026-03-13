#!/usr/bin/env bash
# =============================================================================
# check_org_repos.sh — Validate GitHub org repos against SSOT manifests
# Reads: ssot/github/org-repos.yaml, ssot/github/repo-standards.yaml
# Requires: gh (authenticated), yq
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ---------------------------------------------------------------------------
# Prerequisites
# ---------------------------------------------------------------------------
for cmd in gh yq; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "FAIL: $cmd is required but not found" >&2; exit 1
    fi
done

if ! gh auth status &>/dev/null 2>&1; then
    echo "FAIL: gh is not authenticated. Run: gh auth login" >&2; exit 1
fi

MANIFEST="$REPO_ROOT/ssot/github/org-repos.yaml"
STANDARDS="$REPO_ROOT/ssot/github/repo-standards.yaml"

for f in "$MANIFEST" "$STANDARDS"; do
    if [[ ! -f "$f" ]]; then
        echo "FAIL: $f not found" >&2; exit 1
    fi
done

ORG=$(yq -r '.org.github_org' "$MANIFEST")
GOV_VERSION=$(yq -r '.org.governance_version' "$MANIFEST")

echo "== InsightPulseAI Org Repo Check (governance v${GOV_VERSION}) =="
echo "   Org: ${ORG}"
echo ""

# ---------------------------------------------------------------------------
# Fetch live repo data from GitHub (single API call)
# ---------------------------------------------------------------------------
LIVE_REPOS=$(gh repo list "$ORG" --json name,visibility,isArchived --limit 100)

fail=0
warn=0
pass=0

# ---------------------------------------------------------------------------
# Read baseline required files
# ---------------------------------------------------------------------------
mapfile -t BASELINE_FILES < <(yq -r '.repo_standards.baseline.required_files[]' "$STANDARDS")

# ---------------------------------------------------------------------------
# Check each canonical repo
# ---------------------------------------------------------------------------
REPO_COUNT=$(yq -r '.repos | length' "$MANIFEST")

for i in $(seq 0 $((REPO_COUNT - 1))); do
    REPO_NAME=$(yq -r ".repos[$i].name" "$MANIFEST")
    EXPECTED_VIS=$(yq -r ".repos[$i].visibility" "$MANIFEST" | tr '[:lower:]' '[:upper:]')
    EXPECTED_LIFECYCLE=$(yq -r ".repos[$i].lifecycle" "$MANIFEST")
    REPO_TYPE=$(yq -r ".repos[$i].type" "$MANIFEST")

    echo "-- ${REPO_NAME} (type: ${REPO_TYPE}, expected: ${EXPECTED_VIS}) --"

    # Check repo exists on GitHub
    ACTUAL_VIS=$(echo "$LIVE_REPOS" | yq -r ".[] | select(.name == \"${REPO_NAME}\") | .visibility")
    IS_ARCHIVED=$(echo "$LIVE_REPOS" | yq -r ".[] | select(.name == \"${REPO_NAME}\") | .isArchived")

    if [[ -z "$ACTUAL_VIS" || "$ACTUAL_VIS" == "null" ]]; then
        echo "  FAIL: repo not found on GitHub" >&2
        fail=$((fail + 1))
        echo ""
        continue
    fi

    # Visibility check
    if [[ "$ACTUAL_VIS" != "$EXPECTED_VIS" ]]; then
        echo "  FAIL: visibility mismatch (expected: ${EXPECTED_VIS}, actual: ${ACTUAL_VIS})" >&2
        fail=$((fail + 1))
    else
        echo "  OK: visibility ${ACTUAL_VIS}"
        pass=$((pass + 1))
    fi

    # Archived status check
    if [[ "$EXPECTED_LIFECYCLE" == "active" && "$IS_ARCHIVED" == "true" ]]; then
        echo "  FAIL: repo is archived but manifest says active" >&2
        fail=$((fail + 1))
    fi

    # Required files: merge baseline + per-repo + type-specific
    mapfile -t REPO_REQUIRED < <(yq -r ".repos[$i].required_files[]" "$MANIFEST" 2>/dev/null)
    mapfile -t TYPE_EXTRA < <(yq -r ".repo_standards.types.\"${REPO_TYPE}\".extra_required_files[] // empty" "$STANDARDS" 2>/dev/null || true)

    # Combine and deduplicate
    ALL_REQUIRED=()
    declare -A SEEN_FILES=()
    for f in "${BASELINE_FILES[@]}" "${REPO_REQUIRED[@]}" "${TYPE_EXTRA[@]}"; do
        if [[ -n "$f" && "$f" != "null" && -z "${SEEN_FILES[$f]:-}" ]]; then
            ALL_REQUIRED+=("$f")
            SEEN_FILES[$f]=1
        fi
    done
    unset SEEN_FILES

    for req_file in "${ALL_REQUIRED[@]}"; do
        if gh api "repos/${ORG}/${REPO_NAME}/contents/${req_file}" --silent >/dev/null 2>&1; then
            echo "  OK: ${req_file}"
            pass=$((pass + 1))
        else
            echo "  WARN: ${req_file} missing" >&2
            warn=$((warn + 1))
        fi
    done

    # Directory layout spot-checks
    mapfile -t EXPECTED_DIRS < <(yq -r ".repos[$i].directory_layout[]" "$MANIFEST" 2>/dev/null)
    for dir in "${EXPECTED_DIRS[@]}"; do
        if [[ -z "$dir" || "$dir" == "null" ]]; then continue; fi
        dir_clean="${dir%/}"
        if gh api "repos/${ORG}/${REPO_NAME}/contents/${dir_clean}" --silent >/dev/null 2>&1; then
            echo "  OK: ${dir_clean}/"
            pass=$((pass + 1))
        else
            echo "  WARN: ${dir_clean}/ not found" >&2
            warn=$((warn + 1))
        fi
    done

    echo ""
done

# ---------------------------------------------------------------------------
# Check archived repos are actually archived
# ---------------------------------------------------------------------------
echo "== Archived Repos =="
ARCHIVED_COUNT=$(yq -r '.archived | length' "$MANIFEST")

for i in $(seq 0 $((ARCHIVED_COUNT - 1))); do
    REPO_NAME=$(yq -r ".archived[$i].name" "$MANIFEST")
    REASON=$(yq -r ".archived[$i].reason" "$MANIFEST")

    IS_ARCHIVED=$(echo "$LIVE_REPOS" | yq -r ".[] | select(.name == \"${REPO_NAME}\") | .isArchived")

    if [[ "$IS_ARCHIVED" == "true" ]]; then
        echo "  OK: ${REPO_NAME} (archived — ${REASON})"
        pass=$((pass + 1))
    elif [[ -z "$IS_ARCHIVED" || "$IS_ARCHIVED" == "null" ]]; then
        echo "  WARN: ${REPO_NAME} not found on GitHub"
        warn=$((warn + 1))
    else
        echo "  FAIL: ${REPO_NAME} should be archived but is active" >&2
        fail=$((fail + 1))
    fi
done

echo ""

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo "== Summary =="
echo "  Pass: ${pass}"
echo "  Warn: ${warn}"
echo "  Fail: ${fail}"
echo ""

if [[ $fail -gt 0 ]]; then
    echo "check_org_repos: FAIL — ${fail} check(s) failed" >&2
    exit 1
fi

if [[ $warn -gt 0 ]]; then
    echo "check_org_repos: PASS with ${warn} warning(s)"
    exit 0
fi

echo "check_org_repos: PASS — all checks green"
