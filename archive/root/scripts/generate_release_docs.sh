#!/bin/bash
# =============================================================================
# generate_release_docs.sh - Generate release documentation pack
# =============================================================================
# Usage: ./scripts/generate_release_docs.sh <release_tag>
# Example: ./scripts/generate_release_docs.sh prod-20260109-1642
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get release tag from argument or environment
RELEASE_TAG="${1:-${RELEASE_TAG:-}}"
if [[ -z "$RELEASE_TAG" ]]; then
    echo -e "${RED}Error: Release tag required${NC}"
    echo "Usage: $0 <release_tag>"
    exit 1
fi

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RELEASES_DIR="$REPO_ROOT/docs/releases"
RELEASE_DIR="$RELEASES_DIR/$RELEASE_TAG"
PROOFS_DIR="$RELEASE_DIR/DEPLOYMENT_PROOFS"

echo -e "${GREEN}Generating release documentation for: $RELEASE_TAG${NC}"

# Create directories
mkdir -p "$RELEASE_DIR" "$PROOFS_DIR"

# Get commit SHA for the tag (or HEAD if tag doesn't exist)
if git rev-parse "$RELEASE_TAG^{commit}" >/dev/null 2>&1; then
    COMMIT_SHA=$(git rev-parse "$RELEASE_TAG^{commit}")
else
    echo -e "${YELLOW}Tag $RELEASE_TAG not found, using HEAD${NC}"
    COMMIT_SHA=$(git rev-parse HEAD)
fi
SHORT_SHA="${COMMIT_SHA:0:7}"

# Get previous release tag for comparison
PREV_TAG=$(git tag -l 'prod-*' --sort=-version:refname | grep -v "$RELEASE_TAG" | head -1 || echo "")

# Get commits between tags
if [[ -n "$PREV_TAG" ]]; then
    COMMITS=$(git log --oneline "$PREV_TAG..$COMMIT_SHA" 2>/dev/null || git log --oneline -20)
    COMMITS_JSON=$(git log --format='{"sha":"%H","short":"%h","subject":"%s","author":"%an","date":"%aI"}' "$PREV_TAG..$COMMIT_SHA" 2>/dev/null | jq -s '.' || echo "[]")
else
    COMMITS=$(git log --oneline -20)
    COMMITS_JSON=$(git log --format='{"sha":"%H","short":"%h","subject":"%s","author":"%an","date":"%aI"}' -20 | jq -s '.' || echo "[]")
fi

# Get changed files
if [[ -n "$PREV_TAG" ]]; then
    CHANGED_PATHS=$(git diff --name-only "$PREV_TAG..$COMMIT_SHA" 2>/dev/null || echo "")
else
    CHANGED_PATHS=$(git diff --name-only HEAD~20 2>/dev/null || echo "")
fi

# Extract changed modules
ODOO_MODULES=$(echo "$CHANGED_PATHS" | grep -E '^addons/' | cut -d'/' -f2-3 | sort -u | head -20 || echo "")
SUPABASE_FUNCTIONS=$(echo "$CHANGED_PATHS" | grep -E '^supabase/functions/' | cut -d'/' -f3 | sort -u || echo "")
WORKFLOWS=$(echo "$CHANGED_PATHS" | grep -E '^\.github/workflows/' | xargs -I{} basename {} .yml 2>/dev/null | sort -u || echo "")

# Get current date
RELEASE_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
RELEASE_DATE_HUMAN=$(date -u +"%B %d, %Y at %H:%M UTC")

# =============================================================================
# Generate WHAT_SHIPPED.md
# =============================================================================
cat > "$RELEASE_DIR/WHAT_SHIPPED.md" << EOF
# What Shipped: $RELEASE_TAG

**Release Date:** $RELEASE_DATE_HUMAN
**Commit SHA:** \`$COMMIT_SHA\`
**Short SHA:** \`$SHORT_SHA\`
**Previous Release:** ${PREV_TAG:-"(initial release)"}

---

## Summary

This release includes updates to the InsightPulse AI Odoo CE platform.

---

## Commits Included

\`\`\`
$COMMITS
\`\`\`

---

## Modules Changed

### Odoo Addons
$(echo "$ODOO_MODULES" | sed 's/^/- /' | head -30)

### Supabase Edge Functions
$(if [[ -n "$SUPABASE_FUNCTIONS" ]]; then echo "$SUPABASE_FUNCTIONS" | sed 's/^/- /'; else echo "- (none)"; fi)

### GitHub Workflows
$(if [[ -n "$WORKFLOWS" ]]; then echo "$WORKFLOWS" | sed 's/^/- /'; else echo "- (none)"; fi)

---

## Breaking Changes

- None identified

---

## Feature Flags / Config Changes

- None

---

## Known Issues / TODO Carryover

- See GitHub Issues for current backlog

---

## Rollback Instructions

\`\`\`bash
# Rollback to previous release
git checkout ${PREV_TAG:-"main"}
docker compose down && docker compose up -d
\`\`\`

---

## Related Links

- [GO_LIVE_MANIFEST.md](./GO_LIVE_MANIFEST.md)
- [DEPLOYMENT_PROOFS/](./DEPLOYMENT_PROOFS/)
- [GitHub Release](https://github.com/jgtolentino/odoo-ce/releases/tag/$RELEASE_TAG)
EOF

echo -e "${GREEN}Created: WHAT_SHIPPED.md${NC}"

# =============================================================================
# Generate WHAT_SHIPPED.json
# =============================================================================
cat > "$RELEASE_DIR/WHAT_SHIPPED.json" << EOF
{
  "release_tag": "$RELEASE_TAG",
  "commit_sha": "$COMMIT_SHA",
  "short_sha": "$SHORT_SHA",
  "previous_tag": "${PREV_TAG:-null}",
  "release_date": "$RELEASE_DATE",
  "commits": $COMMITS_JSON,
  "changed_paths": $(echo "$CHANGED_PATHS" | jq -R -s 'split("\n") | map(select(length > 0))'),
  "odoo_modules": $(echo "$ODOO_MODULES" | jq -R -s 'split("\n") | map(select(length > 0))'),
  "supabase_functions": $(echo "$SUPABASE_FUNCTIONS" | jq -R -s 'split("\n") | map(select(length > 0))'),
  "workflows": $(echo "$WORKFLOWS" | jq -R -s 'split("\n") | map(select(length > 0))'),
  "breaking_changes": [],
  "feature_flags": [],
  "known_issues": []
}
EOF

echo -e "${GREEN}Created: WHAT_SHIPPED.json${NC}"

# =============================================================================
# Generate GO_LIVE_MANIFEST.md
# =============================================================================
cat > "$RELEASE_DIR/GO_LIVE_MANIFEST.md" << EOF
# Go-Live Manifest: $RELEASE_TAG

**Generated:** $RELEASE_DATE_HUMAN

---

## Environment Identifiers

| Component | Value |
|-----------|-------|
| **Release Tag** | \`$RELEASE_TAG\` |
| **Commit SHA** | \`$COMMIT_SHA\` |
| **Production URL** | https://erp.insightpulseai.com |
| **Database** | \`odoo_core\` |
| **Docker Image** | \`ghcr.io/jgtolentino/odoo-ce:$RELEASE_TAG\` |

---

## Deployed Artifacts

### Docker Image
- **Registry:** ghcr.io/jgtolentino/odoo-ce
- **Tag:** \`$RELEASE_TAG\`
- **Digest:** See \`DEPLOYMENT_PROOFS/docker_image_digest.txt\`

### Odoo Modules (Install/Upgrade List)
$(echo "$ODOO_MODULES" | sed 's/^/- /' | head -20)

### Supabase Migrations
- See \`DEPLOYMENT_PROOFS/supabase_migration_status.txt\`

### Edge Functions
$(if [[ -n "$SUPABASE_FUNCTIONS" ]]; then echo "$SUPABASE_FUNCTIONS" | sed 's/^/- /'; else echo "- (none deployed)"; fi)

---

## Health Checks

| Check | Expected | Proof File |
|-------|----------|------------|
| Odoo Web | HTTP 200 | \`curl_health_headers.txt\` |
| Odoo Init | Exit 0 | \`odoo_stop_after_init.log\` |
| Database | Connected | \`odoo_stop_after_init.log\` |

---

## Verification Commands

\`\`\`bash
# Check Odoo health
curl -sI https://erp.insightpulseai.com/web/health | head -5

# Check Docker image
docker inspect ghcr.io/jgtolentino/odoo-ce:$RELEASE_TAG --format='{{.Id}}'

# Check module state
docker exec odoo-erp-prod odoo shell -d odoo_core -c "print(env['ir.module.module'].search([('state','=','installed')]).mapped('name'))"
\`\`\`

---

## Rollback Procedure

\`\`\`bash
# 1. Stop current deployment
docker compose down

# 2. Pull previous image
docker pull ghcr.io/jgtolentino/odoo-ce:${PREV_TAG:-"latest"}

# 3. Update docker-compose.yml to use previous tag
# 4. Restart
docker compose up -d

# 5. Verify
curl -sI https://erp.insightpulseai.com/web | head -3
\`\`\`
EOF

echo -e "${GREEN}Created: GO_LIVE_MANIFEST.md${NC}"

# =============================================================================
# Create placeholder proof files
# =============================================================================
echo "# Docker Image Digest for $RELEASE_TAG
# Run: docker inspect ghcr.io/jgtolentino/odoo-ce:$RELEASE_TAG --format='{{.Id}}'
# Paste digest below:
DIGEST_PENDING" > "$PROOFS_DIR/docker_image_digest.txt"

echo "# Odoo stop-after-init log for $RELEASE_TAG
# Run: docker exec odoo-erp-prod odoo -d odoo_core --stop-after-init 2>&1 | tail -50
# Paste output below:
LOG_PENDING" > "$PROOFS_DIR/odoo_stop_after_init.log"

echo "# Health check headers for $RELEASE_TAG
# Run: curl -sI https://erp.insightpulseai.com/web | head -10
# Paste output below:
HEADERS_PENDING" > "$PROOFS_DIR/curl_health_headers.txt"

echo "# Supabase migration status for $RELEASE_TAG
# Run: supabase db migrations list
# Paste output below:
STATUS_PENDING" > "$PROOFS_DIR/supabase_migration_status.txt"

echo "{}" > "$PROOFS_DIR/workflow_run.json"

echo -e "${GREEN}Created: DEPLOYMENT_PROOFS/ placeholder files${NC}"

# =============================================================================
# Update LATEST symlinks
# =============================================================================
cat > "$RELEASES_DIR/LATEST.md" << EOF
# Latest Release: $RELEASE_TAG

This document redirects to the latest release documentation.

**Current Release:** [$RELEASE_TAG](./$RELEASE_TAG/WHAT_SHIPPED.md)

---

## Quick Links

- [What Shipped](./$RELEASE_TAG/WHAT_SHIPPED.md)
- [Go-Live Manifest](./$RELEASE_TAG/GO_LIVE_MANIFEST.md)
- [Deployment Proofs](./$RELEASE_TAG/DEPLOYMENT_PROOFS/)

---

## All Releases

$(git tag -l 'prod-*' --sort=-version:refname | head -10 | sed 's/^/- /')
EOF

# Create LATEST.json as symlink content
cat > "$RELEASES_DIR/LATEST.json" << EOF
{
  "latest_release": "$RELEASE_TAG",
  "release_dir": "./$RELEASE_TAG",
  "what_shipped": "./$RELEASE_TAG/WHAT_SHIPPED.json",
  "go_live_manifest": "./$RELEASE_TAG/GO_LIVE_MANIFEST.md",
  "all_releases": $(git tag -l 'prod-*' --sort=-version:refname | head -10 | jq -R -s 'split("\n") | map(select(length > 0))')
}
EOF

echo -e "${GREEN}Created: LATEST.md and LATEST.json${NC}"

# =============================================================================
# Summary
# =============================================================================
echo ""
echo -e "${GREEN}=== Release Documentation Generated ===${NC}"
echo "Release: $RELEASE_TAG"
echo "Location: $RELEASE_DIR"
echo ""
echo "Files created:"
ls -la "$RELEASE_DIR"
echo ""
echo "Proofs directory:"
ls -la "$PROOFS_DIR"
echo ""
echo -e "${YELLOW}NOTE: Update DEPLOYMENT_PROOFS/ files with actual deployment data${NC}"
