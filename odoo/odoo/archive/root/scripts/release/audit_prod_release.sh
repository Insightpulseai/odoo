#!/usr/bin/env bash
# audit_prod_release.sh — Audit a production release for code inclusion and activation prerequisites
#
# Usage:
#   ./scripts/release/audit_prod_release.sh <prod-tag> [previous-prod-tag]
#
# Examples:
#   ./scripts/release/audit_prod_release.sh prod-20260302-0241
#   ./scripts/release/audit_prod_release.sh prod-20260302-0241 prod-20260302-0211

set -euo pipefail

PROD_TAG="${1:?Usage: $0 <prod-tag> [previous-prod-tag]}"
PREV_TAG="${2:-}"

# --- Resolve tag SHAs ---
PROD_SHA=$(git rev-parse "$PROD_TAG" 2>/dev/null) || {
    echo "ERROR: Tag '$PROD_TAG' not found. Run: git fetch origin --tags"
    exit 1
}
PROD_SHA_SHORT="${PROD_SHA:0:9}"

if [[ -z "$PREV_TAG" ]]; then
    # Auto-detect previous prod tag
    PREV_TAG=$(git tag -l 'prod-*' --sort=-creatordate | grep -A1 "^${PROD_TAG}$" | tail -1)
    if [[ "$PREV_TAG" == "$PROD_TAG" ]] || [[ -z "$PREV_TAG" ]]; then
        echo "WARNING: Could not auto-detect previous prod tag. Showing last 20 commits before $PROD_TAG."
        PREV_TAG=""
    fi
fi

if [[ -n "$PREV_TAG" ]]; then
    PREV_SHA=$(git rev-parse "$PREV_TAG" 2>/dev/null) || {
        echo "ERROR: Tag '$PREV_TAG' not found."
        exit 1
    }
    PREV_SHA_SHORT="${PREV_SHA:0:9}"
    RANGE="${PREV_TAG}..${PROD_TAG}"
else
    PREV_SHA="N/A"
    PREV_SHA_SHORT="N/A"
    RANGE=""
fi

# --- Output directory ---
TIMESTAMP=$(date -u +%Y%m%d-%H%M)
EVIDENCE_DIR="docs/evidence/${TIMESTAMP}/release-audit"
mkdir -p "$EVIDENCE_DIR"
REPORT="${EVIDENCE_DIR}/audit_${PROD_TAG}.md"

# --- Header ---
{
    echo "# Production Release Audit: ${PROD_TAG}"
    echo ""
    echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo ""
    echo "## Release Under Review"
    echo ""
    echo "| Field | Value |"
    echo "|-------|-------|"
    echo "| Release tag | \`${PROD_TAG}\` |"
    echo "| Commit SHA | \`${PROD_SHA}\` |"
    echo "| Previous prod tag | \`${PREV_TAG:-none}\` |"
    echo "| Previous SHA | \`${PREV_SHA}\` |"
    echo ""
} > "$REPORT"

# --- Commits in range ---
{
    echo "## Commits in Range"
    echo ""
    if [[ -n "$RANGE" ]]; then
        echo "Range: \`${RANGE}\`"
        echo ""
        echo '```'
        git log --oneline "$RANGE" 2>/dev/null || echo "(no commits in range)"
        echo '```'
    else
        echo "No previous tag — showing last 20 commits:"
        echo ""
        echo '```'
        git log --oneline -20 "$PROD_TAG"
        echo '```'
    fi
    echo ""
} >> "$REPORT"

# --- Merged PRs ---
{
    echo "## Merged PRs"
    echo ""
    if [[ -n "$RANGE" ]]; then
        PR_LIST=$(git log --oneline "$RANGE" --grep='(#' 2>/dev/null || true)
        if [[ -n "$PR_LIST" ]]; then
            echo "| Commit | Description |"
            echo "|--------|-------------|"
            while IFS= read -r line; do
                sha=$(echo "$line" | awk '{print $1}')
                msg=$(echo "$line" | cut -d' ' -f2-)
                echo "| \`${sha}\` | ${msg} |"
            done <<< "$PR_LIST"
        else
            echo "No PRs found in range."
        fi
    else
        echo "N/A — no range specified."
    fi
    echo ""
} >> "$REPORT"

# --- Files changed ---
{
    echo "## Files Changed"
    echo ""
    if [[ -n "$RANGE" ]]; then
        echo '```'
        git diff --stat "$RANGE" 2>/dev/null | tail -20
        echo '```'
    else
        echo '```'
        git show --stat "$PROD_TAG" --format="" | tail -20
        echo '```'
    fi
    echo ""
} >> "$REPORT"

# --- Odoo modules touched ---
{
    echo "## Odoo Modules Touched"
    echo ""
    if [[ -n "$RANGE" ]]; then
        MODULES=$(git diff --name-only "$RANGE" 2>/dev/null | grep -oP 'addons/ipai/\K[^/]+' | sort -u || true)
    else
        MODULES=$(git show --name-only "$PROD_TAG" --format="" | grep -oP 'addons/ipai/\K[^/]+' | sort -u || true)
    fi
    if [[ -n "$MODULES" ]]; then
        echo "| Module | Has Migration | Has Manifest |"
        echo "|--------|:------------:|:------------:|"
        while IFS= read -r mod; do
            has_migration="no"
            has_manifest="no"
            [[ -d "addons/ipai/${mod}/migrations" ]] && has_migration="yes"
            [[ -f "addons/ipai/${mod}/__manifest__.py" ]] && has_manifest="yes"
            echo "| \`${mod}\` | ${has_migration} | ${has_manifest} |"
        done <<< "$MODULES"
    else
        echo "No ipai modules touched in this range."
    fi
    echo ""
} >> "$REPORT"

# --- Migrations added ---
{
    echo "## Migrations Added"
    echo ""
    if [[ -n "$RANGE" ]]; then
        MIGRATIONS=$(git diff --name-only "$RANGE" 2>/dev/null | grep -i 'migrat' || true)
    else
        MIGRATIONS=$(git show --name-only "$PROD_TAG" --format="" | grep -i 'migrat' || true)
    fi
    if [[ -n "$MIGRATIONS" ]]; then
        echo '```'
        echo "$MIGRATIONS"
        echo '```'
        echo ""
        echo "**Action required**: Verify these migrations were applied in production."
    else
        echo "No migration files in this range."
    fi
    echo ""
} >> "$REPORT"

# --- Environment dependencies ---
{
    echo "## Environment Dependencies Flagged"
    echo ""
    if [[ -n "$RANGE" ]]; then
        ENV_REFS=$(git diff "$RANGE" 2>/dev/null | grep -oP '(os\.getenv|os\.environ|process\.env\.|SUPABASE_|OPENAI_|ANTHROPIC_|MAILGUN_|VERCEL_|GITHUB_TOKEN|FIGMA_)[A-Z_]*' | sort -u || true)
    else
        ENV_REFS=$(git show "$PROD_TAG" 2>/dev/null | grep -oP '(os\.getenv|os\.environ|process\.env\.|SUPABASE_|OPENAI_|ANTHROPIC_|MAILGUN_|VERCEL_|GITHUB_TOKEN|FIGMA_)[A-Z_]*' | sort -u || true)
    fi
    if [[ -n "$ENV_REFS" ]]; then
        echo "Environment variables referenced in changed code:"
        echo ""
        echo '```'
        echo "$ENV_REFS"
        echo '```'
        echo ""
        echo "**Action required**: Verify these env vars are set in production."
    else
        echo "No new environment variable references detected."
    fi
    echo ""
} >> "$REPORT"

# --- Workflow changes ---
{
    echo "## CI/CD Workflow Changes"
    echo ""
    if [[ -n "$RANGE" ]]; then
        WF_CHANGES=$(git diff --name-only "$RANGE" 2>/dev/null | grep '.github/workflows/' || true)
    else
        WF_CHANGES=$(git show --name-only "$PROD_TAG" --format="" | grep '.github/workflows/' || true)
    fi
    if [[ -n "$WF_CHANGES" ]]; then
        echo '```'
        echo "$WF_CHANGES"
        echo '```'
    else
        echo "No workflow changes."
    fi
    echo ""
} >> "$REPORT"

# --- Recent PRs NOT in this release ---
{
    echo "## PRs Merged After This Release"
    echo ""
    AFTER_COMMITS=$(git log --oneline "${PROD_TAG}..HEAD" --grep='(#' 2>/dev/null | head -20 || true)
    if [[ -n "$AFTER_COMMITS" ]]; then
        echo "These PRs merged after \`${PROD_TAG}\` and are **not** in this release:"
        echo ""
        echo "| Commit | Description |"
        echo "|--------|-------------|"
        while IFS= read -r line; do
            sha=$(echo "$line" | awk '{print $1}')
            msg=$(echo "$line" | cut -d' ' -f2-)
            echo "| \`${sha}\` | ${msg} |"
        done <<< "$AFTER_COMMITS"
    else
        echo "No additional PRs merged after this release (tag is at HEAD or no PR merges found)."
    fi
    echo ""
} >> "$REPORT"

# --- Summary ---
{
    echo "## Summary"
    echo ""
    if [[ -n "$RANGE" ]]; then
        COMMIT_COUNT=$(git rev-list --count "$RANGE" 2>/dev/null || echo 0)
        echo "- **Commits in range**: ${COMMIT_COUNT}"
    fi
    echo "- **Prod tag**: \`${PROD_TAG}\` → \`${PROD_SHA_SHORT}\`"
    [[ -n "$PREV_TAG" ]] && echo "- **Previous tag**: \`${PREV_TAG}\` → \`${PREV_SHA_SHORT}\`"
    echo "- **Report**: \`${REPORT}\`"
    echo ""
    echo "## Verdict"
    echo ""
    echo "- [ ] All included PRs verified as intended"
    echo "- [ ] Migrations applied in production"
    echo "- [ ] Environment variables confirmed in production"
    echo "- [ ] Module installs confirmed in production"
    echo "- [ ] Health checks passed post-deployment"
} >> "$REPORT"

echo ""
echo "=== Release Audit Report ==="
echo "Tag:      ${PROD_TAG}"
echo "SHA:      ${PROD_SHA}"
echo "Previous: ${PREV_TAG:-none}"
echo "Report:   ${REPORT}"
echo ""
cat "$REPORT"
