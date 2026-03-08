#!/usr/bin/env bash
# audit_prod_release.sh — Audit a production release against its predecessor
#
# Usage:
#   ./scripts/release/audit_prod_release.sh <prod-tag> [previous-prod-tag]
#
# Examples:
#   ./scripts/release/audit_prod_release.sh prod-20260302-0241 prod-20260302-0211
#   ./scripts/release/audit_prod_release.sh prod-20260302-0241
#
# Output: Markdown report to stdout (pipe to file or tee as needed)

set -euo pipefail

PROD_TAG="${1:?Usage: $0 <prod-tag> [previous-prod-tag]}"
PREV_TAG="${2:-}"

# --- Resolve SHAs ---
PROD_SHA=$(git rev-parse "$PROD_TAG" 2>/dev/null) || {
    echo "ERROR: Tag '$PROD_TAG' not found" >&2
    exit 1
}

if [ -n "$PREV_TAG" ]; then
    PREV_SHA=$(git rev-parse "$PREV_TAG" 2>/dev/null) || {
        echo "ERROR: Tag '$PREV_TAG' not found" >&2
        exit 1
    }
else
    # Find the previous prod tag automatically
    PREV_TAG=$(git tag -l 'prod-*' --sort=-creatordate | grep -A1 "^${PROD_TAG}$" | tail -1)
    if [ "$PREV_TAG" = "$PROD_TAG" ] || [ -z "$PREV_TAG" ]; then
        echo "WARNING: No previous prod tag found. Showing all history up to $PROD_TAG." >&2
        PREV_SHA=""
    else
        PREV_SHA=$(git rev-parse "$PREV_TAG")
    fi
fi

# --- Header ---
cat <<EOF
# Production Release Audit

## Release under review

| Field | Value |
|-------|-------|
| **Prod tag** | \`$PROD_TAG\` |
| **Commit SHA** | \`$PROD_SHA\` |
| **Previous prod tag** | \`${PREV_TAG:-none}\` |
| **Previous SHA** | \`${PREV_SHA:-none}\` |
| **Audit date** | $(date -u +"%Y-%m-%dT%H:%M:%SZ") |

EOF

# --- Commit range ---
if [ -n "$PREV_SHA" ]; then
    RANGE="${PREV_TAG}..${PROD_TAG}"
else
    RANGE="$PROD_TAG"
fi

echo "## Commits in range \`$RANGE\`"
echo ""
echo '```'
if [ -n "$PREV_SHA" ]; then
    git log --oneline "$RANGE" 2>/dev/null || echo "(no commits in range)"
else
    git log --oneline -20 "$PROD_TAG" 2>/dev/null
fi
echo '```'
echo ""

# --- PR inclusion ---
echo "## Included PRs"
echo ""
echo "| Commit | PR | Title |"
echo "|--------|----|-------|"

if [ -n "$PREV_SHA" ]; then
    git log --oneline "$RANGE" 2>/dev/null | while IFS= read -r line; do
        sha=$(echo "$line" | cut -d' ' -f1)
        rest=$(echo "$line" | cut -d' ' -f2-)
        pr=$(echo "$rest" | grep -oE '#[0-9]+' | head -1 || echo "—")
        echo "| \`$sha\` | $pr | $rest |"
    done
else
    echo "| — | — | (no range comparison available) |"
fi
echo ""

# --- Files changed ---
echo "## Files changed"
echo ""
if [ -n "$PREV_SHA" ]; then
    CHANGED_FILES=$(git diff --name-only "$RANGE" 2>/dev/null || echo "")
    FILE_COUNT=$(echo "$CHANGED_FILES" | grep -c '.' || echo 0)
    echo "**$FILE_COUNT files changed** in this range."
    echo ""
    echo '```'
    echo "$CHANGED_FILES"
    echo '```'
else
    echo "(no range comparison available)"
fi
echo ""

# --- Odoo modules touched ---
echo "## Odoo modules touched"
echo ""
if [ -n "$PREV_SHA" ]; then
    ODOO_MODULES=$(git diff --name-only "$RANGE" 2>/dev/null \
        | grep -E '^addons/ipai/' \
        | cut -d'/' -f3 \
        | sort -u || echo "")
    if [ -n "$ODOO_MODULES" ]; then
        echo "| Module | Files changed |"
        echo "|--------|--------------|"
        echo "$ODOO_MODULES" | while IFS= read -r mod; do
            count=$(git diff --name-only "$RANGE" | grep -c "addons/ipai/$mod/" || echo 0)
            echo "| \`$mod\` | $count |"
        done
    else
        echo "No Odoo modules changed in this range."
    fi
else
    echo "(no range comparison available)"
fi
echo ""

# --- Migrations ---
echo "## Migrations"
echo ""
if [ -n "$PREV_SHA" ]; then
    MIGRATIONS=$(git diff --name-only "$RANGE" 2>/dev/null \
        | grep -iE 'migration|migrate' || echo "")
    if [ -n "$MIGRATIONS" ]; then
        echo "**Migration files detected:**"
        echo ""
        echo '```'
        echo "$MIGRATIONS"
        echo '```'
        echo ""
        echo "These may require post-deploy activation (module update / db migration)."
    else
        echo "No migration files detected in this range."
    fi
else
    echo "(no range comparison available)"
fi
echo ""

# --- Environment / secrets dependencies ---
echo "## Environment / secrets changes"
echo ""
if [ -n "$PREV_SHA" ]; then
    ENV_FILES=$(git diff --name-only "$RANGE" 2>/dev/null \
        | grep -iE '\.env|secrets|vault|credential' || echo "")
    if [ -n "$ENV_FILES" ]; then
        echo "**Environment/secrets files changed:**"
        echo ""
        echo '```'
        echo "$ENV_FILES"
        echo '```'
        echo ""
        echo "These may require runtime configuration updates."
    else
        echo "No environment/secrets files changed in this range."
    fi
else
    echo "(no range comparison available)"
fi
echo ""

# --- Workflow changes ---
echo "## CI/CD workflow changes"
echo ""
if [ -n "$PREV_SHA" ]; then
    WF_FILES=$(git diff --name-only "$RANGE" 2>/dev/null \
        | grep -E '^\.github/workflows/' || echo "")
    if [ -n "$WF_FILES" ]; then
        echo "| Workflow | Action |"
        echo "|----------|--------|"
        echo "$WF_FILES" | while IFS= read -r wf; do
            echo "| \`$wf\` | changed |"
        done
    else
        echo "No workflow files changed in this range."
    fi
else
    echo "(no range comparison available)"
fi
echo ""

# --- Runtime activation checklist ---
cat <<'EOF'
## Runtime activation checklist

### Odoo
- [ ] Required modules installed (`-u module_name --stop-after-init`)
- [ ] Migrations applied (if migration files detected above)
- [ ] Config present in `odoo.conf` or env vars

### Platform
- [ ] Environment variables / secrets present in runtime
- [ ] External integrations connected
- [ ] Health check passed (`curl -s erp.insightpulseai.com/web/health`)

### Workflows
- [ ] Changed CI/CD workflows active and passing
- [ ] n8n workflows deployed (if applicable)

## Verdict

| Dimension | Status |
|-----------|--------|
| Deployed in code | (verify) |
| Active in runtime | (verify) |
| Expected in production | (verify) |
EOF
