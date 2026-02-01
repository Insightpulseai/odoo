#!/usr/bin/env bash
###############################################################################
# Bootstrap Execution Board (Org-Level Project + Issues)
###############################################################################
# Purpose: Create org-level GitHub Project with issues from rationalization work
# Org: Insightpulseai-net
# Repo: jgtolentino/odoo-ce (existing)
###############################################################################

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ORG="Insightpulseai-net"
PROJECT_TITLE="Execution Board"
REPO="jgtolentino/odoo-ce"
MILESTONE="Ops Control Room v1"

echo "================================================================================"
echo "Bootstrap Execution Board"
echo "================================================================================"
echo ""
echo "Organization: $ORG"
echo "Target Repo: $REPO"
echo "Milestone: $MILESTONE"
echo ""

###############################################################################
# Step 1: Create Org-Level Project (ProjectV2)
###############################################################################
echo "================================================================================"
echo "Step 1: Create Org-Level Project"
echo "================================================================================"
echo ""

echo "Getting organization ID..."
ORG_ID=$(gh api graphql -f query='
query($login:String!){
  organization(login:$login){
    id
  }
}
' -F login="$ORG" --jq '.data.organization.id')

echo -e "${GREEN}✓ Organization ID: $ORG_ID${NC}"

echo ""
echo "Creating ProjectV2: $PROJECT_TITLE..."
PROJECT_ID=$(gh api graphql -f query='
mutation($orgId:ID!,$title:String!){
  createProjectV2(input:{ownerId:$orgId,title:$title}){
    projectV2{
      id
      number
      url
    }
  }
}
' -F orgId="$ORG_ID" -F title="$PROJECT_TITLE" --jq '.data.createProjectV2.projectV2.id' 2>/dev/null || \
gh api graphql -f query='
query($login:String!,$title:String!){
  organization(login:$login){
    projectsV2(first:50, query:$title){
      nodes{
        id
        title
      }
    }
  }
}' -F login="$ORG" -F title="$PROJECT_TITLE" --jq '.data.organization.projectsV2.nodes[0].id')

echo -e "${GREEN}✓ Project ID: $PROJECT_ID${NC}"

PROJECT_URL=$(gh api graphql -f query='
query($login:String!,$title:String!){
  organization(login:$login){
    projectsV2(first:50, query:$title){
      nodes{
        url
      }
    }
  }
}' -F login="$ORG" -F title="$PROJECT_TITLE" --jq '.data.organization.projectsV2.nodes[0].url')

echo -e "${BLUE}Project URL: $PROJECT_URL${NC}"

###############################################################################
# Step 2: Add Custom Fields to Project
###############################################################################
echo ""
echo "================================================================================"
echo "Step 2: Add Custom Fields"
echo "================================================================================"
echo ""

# Area field (single-select)
echo "Adding 'Area' field..."
gh api graphql -f query='
mutation($project:ID!,$name:String!,$dataType:ProjectV2CustomFieldType!,$options:[ProjectV2SingleSelectFieldOptionInput!]!){
  createProjectV2Field(input:{
    projectId:$project,
    dataType:$dataType,
    name:$name,
    singleSelectOptions:$options
  }){
    projectV2Field{
      ... on ProjectV2SingleSelectField{
        id
        name
      }
    }
  }
}
' -F project="$PROJECT_ID" \
  -F name="Area" \
  -F dataType="SINGLE_SELECT" \
  -f options='[
    {name:"Infra",color:"BLUE"},
    {name:"DNS",color:"GREEN"},
    {name:"Odoo",color:"PURPLE"},
    {name:"Supabase",color:"ORANGE"},
    {name:"Agents",color:"PINK"},
    {name:"KnowledgeGraph",color:"YELLOW"},
    {name:"UI",color:"RED"},
    {name:"CI/CD",color:"GRAY"}
  ]' >/dev/null 2>&1 || echo "  (Field may already exist)"

echo -e "${GREEN}✓ Area field added${NC}"

# Priority field (single-select)
echo "Adding 'Priority' field..."
gh api graphql -f query='
mutation($project:ID!,$name:String!,$dataType:ProjectV2CustomFieldType!,$options:[ProjectV2SingleSelectFieldOptionInput!]!){
  createProjectV2Field(input:{
    projectId:$project,
    dataType:$dataType,
    name:$name,
    singleSelectOptions:$options
  }){
    projectV2Field{
      ... on ProjectV2SingleSelectField{
        id
        name
      }
    }
  }
}
' -F project="$PROJECT_ID" \
  -F name="Priority" \
  -F dataType="SINGLE_SELECT" \
  -f options='[
    {name:"P0",color:"RED"},
    {name:"P1",color:"ORANGE"},
    {name:"P2",color:"YELLOW"}
  ]' >/dev/null 2>&1 || echo "  (Field may already exist)"

echo -e "${GREEN}✓ Priority field added${NC}"

# Target field (single-select)
echo "Adding 'Target' field..."
gh api graphql -f query='
mutation($project:ID!,$name:String!,$dataType:ProjectV2CustomFieldType!,$options:[ProjectV2SingleSelectFieldOptionInput!]!){
  createProjectV2Field(input:{
    projectId:$project,
    dataType:$dataType,
    name:$name,
    singleSelectOptions:$options
  }){
    projectV2Field{
      ... on ProjectV2SingleSelectField{
        id
        name
      }
    }
  }
}
' -F project="$PROJECT_ID" \
  -F name="Target" \
  -F dataType="SINGLE_SELECT" \
  -f options='[
    {name:"fin-workspace",color:"BLUE"},
    {name:"prod",color:"RED"},
    {name:"staging",color:"YELLOW"}
  ]' >/dev/null 2>&1 || echo "  (Field may already exist)"

echo -e "${GREEN}✓ Target field added${NC}"

###############################################################################
# Step 3: Create Labels in Repo
###############################################################################
echo ""
echo "================================================================================"
echo "Step 3: Create Labels in Repo"
echo "================================================================================"
echo ""

LABELS=(
  "ops:control-room"
  "ops:workers"
  "kg:ingestion"
  "kg:schema"
  "spec-kit:validation"
  "spec-kit:enforcement"
  "supabase:migrations"
  "supabase:rls"
  "dns:routing"
  "dns:ssl"
  "infra:nginx"
  "infra:docker"
  "odoo:rationalization"
  "odoo:baseline"
  "odoo:oca-validation"
  "ui:runboard"
  "ui:dashboard"
  "ci:automation"
)

for label in "${LABELS[@]}"; do
  echo "Creating label: $label"
  gh label create "$label" -R "$REPO" --color "0E8A16" --description "$label" 2>/dev/null || echo "  (Label already exists)"
done

echo -e "${GREEN}✓ Labels created${NC}"

###############################################################################
# Step 4: Create Milestone
###############################################################################
echo ""
echo "================================================================================"
echo "Step 4: Create Milestone"
echo "================================================================================"
echo ""

echo "Creating milestone: $MILESTONE"
gh api -X POST "repos/$REPO/milestones" \
  -f title="$MILESTONE" \
  -f description="Complete Ops Control Room + Knowledge Graph + Module Rationalization" \
  -f due_on="2026-01-31T00:00:00Z" \
  2>/dev/null || echo "  (Milestone already exists)"

echo -e "${GREEN}✓ Milestone created${NC}"

###############################################################################
# Step 5: Create Issues
###############################################################################
echo ""
echo "================================================================================"
echo "Step 5: Create Issues"
echo "================================================================================"
echo ""

mk_issue() {
  local title="$1"
  local body="$2"
  local labels="$3"

  echo "Creating issue: $title"
  gh issue create -R "$REPO" \
    --title "$title" \
    --body "$body" \
    --label "$labels" \
    --milestone "$MILESTONE" 2>/dev/null || echo "  (Issue may already exist)"
}

# Infrastructure Issues
mk_issue \
  "DNS consolidation to new droplet IP + reverse proxy routing" \
  "Point required subdomains to 178.128.112.214 and configure nginx host-based routing to containers.

**Subdomains**:
- erp.insightpulseai.com → Odoo (8069)
- n8n.insightpulseai.com → n8n (5678)
- superset.insightpulseai.com → Superset (8088)
- mcp.insightpulseai.com → MCP Coordinator (placeholder)
- ocr.insightpulseai.com → OCR Service (placeholder)
- auth.insightpulseai.com → Keycloak (placeholder)

**Acceptance**:
- [ ] All A records point to 178.128.112.214
- [ ] nginx host-based routing configured
- [ ] TLS works via Let's Encrypt
- [ ] All active services (erp, n8n, superset) accessible via HTTPS
- [ ] Placeholder services return 503 with service name

**Files**:
- \`deploy/nginx-complete.conf\`
- \`docs/email/Mailgun_DNS.md\`
" \
  "dns:routing,dns:ssl,infra:nginx"

mk_issue \
  "Supabase: create kg schema + ops schema migrations" \
  "Create Supabase migrations for kg.* (Knowledge Graph) and ops.* (Ops Control Room) tables with indexes and RLS policies.

**kg schema**:
- kg.nodes (id, kind, name, ref, props)
- kg.edges (src, rel, dst, props)
- kg.sources (hash, fetched_at, url, content)
- Graph functions: get_node_neighbors, get_path, get_subgraph, search_nodes

**ops schema**:
- ops.sessions (session_id, started_at, ended_at)
- ops.run_templates (id, name, timeout_seconds, enabled)
- ops.runs (id, template_id, worker_id, status, params, artifacts)
- ops.run_events (run_id, kind, payload, timestamp)
- ops.artifacts (run_id, key, storage_key, content_type)

**Acceptance**:
- [ ] Migrations applied successfully
- [ ] All tables have proper indexes
- [ ] RLS policies enforce security
- [ ] Graph functions return correct results
- [ ] SKIP LOCKED pattern works for work claiming

**Files**:
- \`db/migrations/20260108_kg_schema.sql\`
- \`db/migrations/20260108_ops_schema.sql\`
" \
  "supabase:migrations,supabase:rls,kg:schema,ops:control-room"

mk_issue \
  "Knowledge Graph ingestion (repos/specs/issues → kg.*)" \
  "Implement ingestion script that scans repos and loads kg nodes/edges + generates docs/INDEX.md deterministically.

**Nodes**:
- Repo, SpecBundle, Module, App, Workflow, Script, Service

**Edges**:
- HAS_SPEC, DEPLOYS, RUNS_ON, DEPENDS_ON, IMPLEMENTS, TESTS

**Ingestion sources**:
1. Local filesystem (spec/, addons/, apps/, workflows/, scripts/)
2. GitHub GraphQL API (issues, PRs, repos)
3. Supabase metadata (schemas, functions, policies)

**Acceptance**:
- [ ] Stable IDs (e.g., repo:owner/name, spec:slug, module:ipai.name)
- [ ] Re-run produces identical output unless inputs changed
- [ ] Change detection via content hashing
- [ ] docs/INDEX.md generated with 300+ entries
- [ ] docs/knowledge/graph_seed.json generated with nodes + edges
- [ ] Integration with GitHub GraphQL for issue tracking

**Files**:
- \`scripts/generate_repo_index.py\`
- \`scripts/ingest_knowledge_graph.py\`
- \`docs/INDEX.md\`
- \`docs/knowledge/graph_seed.json\`
" \
  "kg:ingestion,kg:schema,ci:automation"

mk_issue \
  "Ops executor worker (claim/heartbeat/events/artifacts)" \
  "Implement reference worker loop (SKIP LOCKED claim) + artifact uploads for Ops Control Room.

**Worker loop**:
1. Claim pending run (SKIP LOCKED prevents double-run)
2. Execute template with timeout
3. Heartbeat every 30s
4. Emit events (started, progress, completed, failed)
5. Upload artifacts to Supabase Storage
6. Mark run as completed/failed

**Recovery**:
- Dead worker detection (last_heartbeat > timeout)
- Auto-restart stale runs

**Acceptance**:
- [ ] No double-run (SKIP LOCKED works)
- [ ] Heartbeat updates every 30s
- [ ] Timeout kills long-running jobs
- [ ] Events stored in ops.run_events
- [ ] Artifacts uploaded to Supabase Storage
- [ ] Stale run recovery works

**Files**:
- \`apps/pulser-runner/src/worker.ts\`
- \`apps/pulser-runner/src/executor.ts\`
" \
  "ops:workers,ops:control-room"

mk_issue \
  "Ops UI Runboard (realtime lanes)" \
  "Implement runboard UI with realtime updates (<2s) for runs/events/artifacts.

**Features**:
- Lane view (pending, processing, completed, failed)
- Real-time updates via Supabase Realtime
- Cancel run action
- Artifact download links
- Event timeline per run
- Worker health status

**Acceptance**:
- [ ] Lane status updates in <2s
- [ ] Cancel run works
- [ ] Artifact download works
- [ ] Event timeline shows all events
- [ ] Worker health status accurate
- [ ] Mobile responsive

**Files**:
- \`apps/control-room/src/app/runboard/page.tsx\`
- \`apps/control-room/src/components/RunLane.tsx\`
" \
  "ui:runboard,ui:dashboard,ops:control-room"

# Spec Kit Issues
mk_issue \
  "Spec Kit validation CI enforcement" \
  "Implement comprehensive Spec Kit validation in CI with detailed reports.

**Validation checks**:
1. Required files exist (constitution.md, prd.md, plan.md, tasks.md)
2. Minimum content per file (≥10 non-heading lines)
3. constitution.md has \"Non-Negotiable Rules\" section
4. tasks.md has proper status markers
5. No undocumented spec bundles (all in spec/ have 4 files)

**Acceptance**:
- [ ] CI workflow fails on invalid spec bundles
- [ ] Validation report generated (spec_report.json)
- [ ] Undocumented specs detected
- [ ] Clear error messages for fixes

**Files**:
- \`.github/workflows/spec-kit-enforce.yml\`
- \`scripts/validate_spec_kit.py\`
- \`scripts/check_undocumented_specs.py\`
- \`scripts/generate_spec_report.py\`
" \
  "spec-kit:validation,spec-kit:enforcement,ci:automation"

# Odoo Rationalization Issues
mk_issue \
  "Odoo baseline installation (CE + OCA Must-Have)" \
  "Install clean Odoo CE baseline + OCA Must-Have modules before custom ipai_* modules.

**CE baseline**:
- base, web, mail, account, accountant, sale_management, purchase, stock, crm, project, hr_timesheet

**OCA Must-Have** (from PRD Appendix A):
- account_financial_report
- account_lock_date_update
- account_fiscal_year
- base_tier_validation
- mass_editing
- report_xlsx

**OCA Should-Have**:
- sale_order_type
- purchase_order_type
- auditlog
- web_responsive

**Acceptance**:
- [ ] All CE modules installed (state=installed)
- [ ] All OCA Must-Have modules installed
- [ ] OCA Should-Have modules installed (optional)
- [ ] Server boots cleanly
- [ ] No module conflicts
- [ ] Health checks pass

**Files**:
- \`scripts/install_baseline.sh\`
" \
  "odoo:baseline,odoo:rationalization"

mk_issue \
  "OCA validation engine implementation" \
  "Implement OCA validation engine for detecting redundant ipai_* modules using feature signature matching.

**Database schema**:
- oca.module_index (OCA module catalog with keywords)
- oca.custom_module_signatures (ipai_* feature signatures)
- oca.validation_results (match confidence + recommendations)
- oca.module_footprints (UI elements vs business logic)

**Validation logic**:
1. Extract feature signatures (models, views, menus, keywords)
2. Compute Jaccard similarity vs OCA index
3. Identify UI-only modules (zero models/fields/security)
4. Generate KEEP/REDUCE/RETIRE recommendations

**Decision rule**:
- **RETIRE**: UI-only + OCA match ≥0.7
- **REDUCE**: UI-only + OCA match ≥0.4
- **KEEP**: Unique models/fields/security

**Acceptance**:
- [ ] oca schema created with all tables
- [ ] Jaccard similarity function works
- [ ] Feature signatures generated for all ipai_* modules
- [ ] Validation results show match confidence
- [ ] Footprint analysis identifies UI-only modules

**Files**:
- \`db/migrations/20260108_oca_validation.sql\`
- \`scripts/generate_module_signatures.py\`
" \
  "odoo:oca-validation,odoo:rationalization,supabase:migrations"

mk_issue \
  "Odoo rationalization workflow execution" \
  "Execute complete rationalization workflow: baseline → signatures → validation → footprint → backlog.

**Workflow phases**:
1. Install baseline (CE + OCA)
2. Apply OCA validation schema
3. Generate feature signatures
4. Run OCA validation
5. Generate footprint analysis
6. Generate retire backlog
7. Generate final report

**Priority levels**:
- Priority 1: RETIRE (UI-only + high OCA match) - Safest
- Priority 2: REDUCE (UI-only + medium OCA match)
- Priority 3: REDUCE (UI-only, no OCA match)
- Priority 4: RETIRE (high OCA match, has models)
- Priority 5: REDUCE (medium OCA match, has models)
- Priority 6: KEEP (unique business logic)

**Acceptance**:
- [ ] All 7 phases complete
- [ ] Reports generated (validation_results.txt, footprint_analysis.txt, retire_backlog.txt)
- [ ] Final report generated (FINAL_RATIONALIZATION_REPORT.md)
- [ ] Prioritized backlog ready for execution
- [ ] Business approval obtained

**Files**:
- \`scripts/execute_rationalization.sh\`
- \`docs/rationalization/README.md\`
- \`docs/rationalization/EXECUTION_CHECKLIST.md\`
" \
  "odoo:rationalization,odoo:baseline,odoo:oca-validation"

echo -e "${GREEN}✓ Issues created${NC}"

###############################################################################
# Step 6: Add Issues to Project
###############################################################################
echo ""
echo "================================================================================"
echo "Step 6: Add Issues to Project"
echo "================================================================================"
echo ""

echo "Fetching recently created issues..."
ISSUE_IDS=$(gh issue list -R "$REPO" --limit 20 --state open --json id --jq '.[].id')

echo "Adding issues to project..."
for iid in $ISSUE_IDS; do
  gh api graphql -f query='
mutation($project:ID!,$content:ID!){
  addProjectV2ItemById(input:{projectId:$project, contentId:$content}){
    item{
      id
    }
  }
}' -F project="$PROJECT_ID" -F content="$iid" >/dev/null 2>&1 || echo "  (Issue already in project)"
done

echo -e "${GREEN}✓ Issues added to project${NC}"

###############################################################################
# Summary
###############################################################################
echo ""
echo "================================================================================"
echo "Bootstrap Complete"
echo "================================================================================"
echo ""
echo -e "${GREEN}✓ Organization: $ORG${NC}"
echo -e "${GREEN}✓ Project: $PROJECT_TITLE${NC}"
echo -e "${GREEN}✓ Project URL: $PROJECT_URL${NC}"
echo -e "${GREEN}✓ Repository: $REPO${NC}"
echo -e "${GREEN}✓ Milestone: $MILESTONE${NC}"
echo ""
echo "Next steps:"
echo "  1. Open project: $PROJECT_URL"
echo "  2. Configure views (Table, Board, By Area, By Priority)"
echo "  3. Set custom field values for each issue"
echo "  4. Review and prioritize issues"
echo ""
