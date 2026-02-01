#!/usr/bin/env bash
###############################################################################
# GitHub Issues Bootstrap Script
# Creates labels, milestone, and tracking issues for Ops Control Room v1
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REPO="jgtolentino/odoo-ce"
MILESTONE_TITLE="Ops Control Room v1"
MILESTONE_DESCRIPTION="Core infrastructure for Ops Control Room: Spec Kit enforcement, Supabase ops schema, Edge Functions, worker framework, UI Runboard, DNS consolidation, Knowledge Graph ingestion"
MILESTONE_DUE_DATE="2026-02-01"

# Check for GitHub CLI
if ! command -v gh &> /dev/null; then
    echo -e "${RED}ERROR: GitHub CLI (gh) not found${NC}"
    echo "Install with: brew install gh"
    exit 1
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo -e "${RED}ERROR: Not authenticated with GitHub${NC}"
    echo "Run: gh auth login"
    exit 1
fi

echo "================================================================================"
echo "GitHub Issues Bootstrap for ${REPO}"
echo "================================================================================"
echo ""

###############################################################################
# 1. Create Labels
###############################################################################
echo "1. Creating labels..."

declare -A LABELS=(
    ["ops"]="Ops Control Room operations"
    ["spec-kit"]="Spec Kit enforcement and validation"
    ["supabase"]="Supabase database and Edge Functions"
    ["workers"]="Worker framework and execution"
    ["ui"]="User interface components"
    ["dns"]="DNS configuration and management"
    ["infra"]="Infrastructure and deployment"
    ["kg"]="Knowledge Graph ingestion and queries"
)

for label in "${!LABELS[@]}"; do
    description="${LABELS[$label]}"

    if gh label list --repo "$REPO" | grep -q "^$label"; then
        echo "  ✓ Label exists: $label"
    else
        gh label create "$label" \
            --repo "$REPO" \
            --description "$description" \
            --color "$(printf '%06x' $((RANDOM % 16777215)))" \
            && echo -e "  ${GREEN}✓ Created label: $label${NC}" \
            || echo -e "  ${RED}✗ Failed to create label: $label${NC}"
    fi
done

echo ""

###############################################################################
# 2. Create Milestone
###############################################################################
echo "2. Creating milestone..."

# Check if milestone exists
if gh api "repos/$REPO/milestones" --jq ".[] | select(.title==\"$MILESTONE_TITLE\") | .number" | grep -q .; then
    MILESTONE_NUMBER=$(gh api "repos/$REPO/milestones" --jq ".[] | select(.title==\"$MILESTONE_TITLE\") | .number")
    echo "  ✓ Milestone exists: $MILESTONE_TITLE (#$MILESTONE_NUMBER)"
else
    MILESTONE_NUMBER=$(gh api \
        --method POST \
        -H "Accept: application/vnd.github+json" \
        "/repos/$REPO/milestones" \
        -f title="$MILESTONE_TITLE" \
        -f description="$MILESTONE_DESCRIPTION" \
        -f due_on="$MILESTONE_DUE_DATE" \
        --jq '.number')

    echo -e "  ${GREEN}✓ Created milestone: $MILESTONE_TITLE (#$MILESTONE_NUMBER)${NC}"
fi

echo ""

###############################################################################
# 3. Create Issues
###############################################################################
echo "3. Creating issues..."

# Issue 1: Spec Kit Enforcement
ISSUE_1_TITLE="Spec Kit: CI enforcement + validation script"
ISSUE_1_BODY='**Goal**: Enforce Spec Kit structure in CI (constitution.md, prd.md, plan.md, tasks.md)

**Tasks**:
- [x] Create validation script: `scripts/validate_spec_kit.py`
- [x] Create CI workflow: `.github/workflows/spec-kit-enforce.yml`
- [x] Add undocumented specs check: `scripts/check_undocumented_specs.py`
- [x] Generate spec report: `scripts/generate_spec_report.py`
- [ ] Run validation on all existing spec bundles
- [ ] Document spec kit requirements in docs/

**Acceptance**:
- CI fails on missing/incomplete spec bundles
- Validation report shows all spec bundles status
- Zero undocumented spec bundles'

create_issue_if_not_exists "$ISSUE_1_TITLE" "$ISSUE_1_BODY" "spec-kit"

# Issue 2: Supabase Ops Schema
ISSUE_2_TITLE="Supabase: ops schema + RLS + exposure"
ISSUE_2_BODY='**Goal**: Create ops schema with sessions, runs, templates, events, artifacts

**Tasks**:
- [x] Create migration: `db/migrations/20260108_ops_schema.sql`
- [x] Define tables: ops.sessions, ops.run_templates, ops.runs, ops.run_events, ops.artifacts
- [x] Implement functions: claim_run(), heartbeat_run(), start_run(), complete_run(), fail_run(), cancel_run()
- [ ] Apply migration to Supabase project
- [ ] Create RLS policies for multi-tenant access
- [ ] Test run lifecycle (pending → processing → completed/failed)

**Acceptance**:
- Schema deployed to Supabase
- RLS policies enforce tenant isolation
- Functions work correctly with SKIP LOCKED for atomic claiming'

create_issue_if_not_exists "$ISSUE_2_TITLE" "$ISSUE_2_BODY" "supabase,ops"

# Issue 3: Edge Function ops-executor API
ISSUE_3_TITLE="Edge Function: ops-executor API (POST /run)"
ISSUE_3_BODY='**Goal**: HTTP API to enqueue runs with template_id + params

**Tasks**:
- [ ] Create Edge Function: `supabase/functions/ops-executor/index.ts`
- [ ] Implement POST /run endpoint with authentication
- [ ] Validate template_id exists and is enabled
- [ ] Call route_and_enqueue() RPC function
- [ ] Return run_id and status
- [ ] Add error handling and rate limiting
- [ ] Deploy to Supabase

**Acceptance**:
- API accepts authenticated requests
- Valid requests create runs in ops.runs table
- Invalid template_id returns 400 error
- Rate limiting prevents abuse'

create_issue_if_not_exists "$ISSUE_3_TITLE" "$ISSUE_3_BODY" "supabase,ops"

# Issue 4: Worker Reference Implementation
ISSUE_4_TITLE="Worker: reference implementation (Node.js/Deno)"
ISSUE_4_BODY='**Goal**: Long-running worker that claims and executes runs

**Tasks**:
- [ ] Create worker implementation: `packages/worker/src/index.ts`
- [ ] Implement claim loop with claim_run() RPC
- [ ] Execute step_dsl with timeout enforcement
- [ ] Send heartbeats during execution
- [ ] Call start_run(), complete_run(), fail_run() RPCs
- [ ] Add graceful shutdown handling
- [ ] Document deployment (DigitalOcean Droplet, pm2)

**Acceptance**:
- Worker claims pending runs atomically
- Executes steps correctly with timeout
- Updates run status and heartbeat
- Handles failures gracefully with retries'

create_issue_if_not_exists "$ISSUE_4_TITLE" "$ISSUE_4_BODY" "workers,ops"

# Issue 5: UI Runboard with Realtime
ISSUE_5_TITLE="UI: Runboard dashboard + realtime updates"
ISSUE_5_BODY='**Goal**: Dashboard showing active/completed runs with realtime updates

**Tasks**:
- [ ] Create Runboard component: `apps/control-room/src/app/runboard/page.tsx`
- [ ] Query ops.runs with Supabase client
- [ ] Display run status with color coding (pending=gray, processing=blue, completed=green, failed=red)
- [ ] Subscribe to realtime updates on ops.runs table
- [ ] Add run detail view with events and artifacts
- [ ] Add filters (status, template_id, date range)
- [ ] Deploy to Vercel

**Acceptance**:
- Dashboard shows all runs with current status
- Realtime updates appear without refresh
- Run details show full execution history
- Filters work correctly'

create_issue_if_not_exists "$ISSUE_5_TITLE" "$ISSUE_5_BODY" "ui,ops"

# Issue 6: DNS Consolidation
ISSUE_6_TITLE="DNS: consolidate all subdomains to 178.128.112.214"
ISSUE_6_BODY='**Goal**: All *.insightpulseai.com subdomains point to single droplet

**Tasks**:
- [x] Update nginx config with host-based routing
- [x] Install SSL certificates with Let'\''s Encrypt
- [x] Configure erp.insightpulseai.com (Odoo)
- [x] Configure n8n.insightpulseai.com (n8n)
- [x] Configure superset.insightpulseai.com (Superset)
- [ ] Deploy and configure mcp.insightpulseai.com
- [ ] Deploy and configure ocr.insightpulseai.com
- [ ] Deploy and configure auth.insightpulseai.com
- [ ] Deploy and configure chat.insightpulseai.com (Mattermost)
- [ ] Deploy and configure affine.insightpulseai.com
- [ ] Document DNS configuration in docs/email/Mailgun_DNS.md

**Verification**:
```bash
for subdomain in erp n8n superset mcp ocr auth chat affine; do
  echo "$subdomain.insightpulseai.com:"
  dig +short $subdomain.insightpulseai.com
  curl -I https://$subdomain.insightpulseai.com 2>&1 | head -1
done
```

**Acceptance**:
- All subdomains resolve to 178.128.112.214
- Nginx routes based on Host header
- All services accessible via HTTPS
- SSL certificates auto-renew'

create_issue_if_not_exists "$ISSUE_6_TITLE" "$ISSUE_6_BODY" "dns,infra"

# Issue 7: Knowledge Graph Ingestion
ISSUE_7_TITLE="KG: ingestion pipeline for repos/specs/issues/workflows"
ISSUE_7_BODY='**Goal**: Populate kg schema from local repo scan + GitHub API

**Tasks**:
- [x] Create KG schema migration: `db/migrations/20260108_kg_schema.sql`
- [x] Create repo index generator: `scripts/generate_repo_index.py`
- [x] Generate graph seed: `docs/knowledge/graph_seed.json`
- [x] Create ingestion script: `scripts/ingest_knowledge_graph.py`
- [ ] Implement GitHub GraphQL ingestion (repos, issues, PRs, workflows)
- [ ] Add change detection via content hashing
- [ ] Schedule periodic ingestion (GitHub Action)
- [ ] Create query examples for common patterns

**Acceptance**:
- kg.nodes populated with repos, modules, specs, workflows
- kg.edges connect entities with relationships
- kg.sources track ingestion history
- Graph functions work (get_path, get_neighbors, search_nodes)'

create_issue_if_not_exists "$ISSUE_7_TITLE" "$ISSUE_7_BODY" "kg,infra"

# Issue 8: DNS and Mailgun Documentation
ISSUE_8_TITLE="Docs: DNS configuration and Mailgun setup"
ISSUE_8_BODY='**Goal**: Document DNS records and Mailgun email configuration

**Tasks**:
- [ ] Create docs/email/Mailgun_DNS.md
- [ ] Document all DNS A records (*.insightpulseai.com)
- [ ] Document Mailgun CNAME records (email.insightpulseai.com)
- [ ] Document Mailgun TXT records (SPF, DKIM, DMARC)
- [ ] Add verification steps (dig, nslookup, mail send test)
- [ ] Document nginx host-based routing
- [ ] Add troubleshooting section

**Acceptance**:
- Complete DNS record inventory
- Mailgun configuration documented
- Verification commands provided
- Troubleshooting guide included'

create_issue_if_not_exists "$ISSUE_8_TITLE" "$ISSUE_8_BODY" "dns,infra"

echo ""
echo "================================================================================"
echo "✓ Bootstrap complete"
echo "================================================================================"
echo ""
echo "View milestone: gh issue list --repo $REPO --milestone \"$MILESTONE_TITLE\""
echo ""

###############################################################################
# Helper Function
###############################################################################
function create_issue_if_not_exists() {
    local title="$1"
    local body="$2"
    local labels="$3"

    # Check if issue with same title exists
    if gh issue list --repo "$REPO" --search "in:title $title" --limit 1 | grep -q "$title"; then
        echo "  ✓ Issue exists: $title"
    else
        gh issue create \
            --repo "$REPO" \
            --title "$title" \
            --body "$body" \
            --label "$labels" \
            --milestone "$MILESTONE_NUMBER" \
            && echo -e "  ${GREEN}✓ Created issue: $title${NC}" \
            || echo -e "  ${RED}✗ Failed to create issue: $title${NC}"
    fi
}
