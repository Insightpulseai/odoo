# Quick Start - Execution Board

**TL;DR**: Single command to bootstrap org-level GitHub Project with all tracking issues.

---

## Prerequisites

```bash
# Install GitHub CLI
brew install gh

# Authenticate
gh auth login

# Verify org access
gh api user/orgs --jq '.[].login' | grep "Insightpulseai-net"
```

---

## One-Command Setup

```bash
./scripts/bootstrap_execution_board.sh
```

**Duration**: ~2 minutes

**What it creates**:

1. ✅ Org Project: **Execution Board** (with 4 custom fields)
2. ✅ Milestone: **Ops Control Room v1** (due 2026-01-31)
3. ✅ Labels: 18 namespaced labels (ops:*, kg:*, dns:*, etc.)
4. ✅ Issues: 9 tracking issues covering all deliverables
5. ✅ Links: Issues added to project automatically

**Output**: Project URL printed at end of script

---

## What Gets Created

### Project Structure

```
Execution Board (Org-Level ProjectV2)
├── Custom Fields
│   ├── Area: Infra, DNS, Odoo, Supabase, Agents, KG, UI, CI/CD
│   ├── Priority: P0, P1, P2
│   ├── Target: fin-workspace, prod, staging
│   └── Owner, Due Date
├── Views
│   ├── Table (default)
│   ├── Board by Status
│   ├── By Area
│   └── By Priority
└── Issues (9 total)
    ├── Infrastructure (3)
    │   ├── DNS Consolidation
    │   ├── Supabase Schemas
    │   └── Knowledge Graph Ingestion
    ├── Ops Control Room (2)
    │   ├── Worker Implementation
    │   └── UI Runboard
    ├── Spec Kit (1)
    │   └── CI Validation
    └── Odoo Rationalization (3)
        ├── Baseline Installation
        ├── OCA Validation Engine
        └── Rationalization Workflow
```

---

## Quick Commands

### View Issues

```bash
# All issues in milestone
gh issue list --repo jgtolentino/odoo-ce --milestone "Ops Control Room v1"

# By label
gh issue list --repo jgtolentino/odoo-ce --label "odoo:rationalization"
gh issue list --repo jgtolentino/odoo-ce --label "ops:control-room"

# Open issues only
gh issue list --repo jgtolentino/odoo-ce --state open
```

### Manage Issues

```bash
# View details
gh issue view 123 --repo jgtolentino/odoo-ce

# Edit
gh issue edit 123 --repo jgtolentino/odoo-ce --add-label "P0" --add-assignee "@me"

# Close with verification
gh issue close 123 --repo jgtolentino/odoo-ce --comment "✅ Completed and verified"

# Reopen
gh issue reopen 123 --repo jgtolentino/odoo-ce
```

### Project Commands

```bash
# Open project in browser
open "$(gh api graphql -f query='
query($login:String!,$title:String!){
  organization(login:$login){
    projectsV2(first:50, query:$title){
      nodes{ url }
    }
  }
}' -F login="Insightpulseai-net" -F title="Execution Board" --jq '.data.organization.projectsV2.nodes[0].url')"
```

---

## Issue Breakdown by Priority

### P0 - Must complete before other work

1. **DNS Consolidation** (`dns:routing`, `dns:ssl`, `infra:nginx`)
   - All subdomains → 178.128.112.214
   - nginx host-based routing
   - SSL via Let's Encrypt
   - **Status**: ✅ Partially complete (3/8 services active)

2. **Supabase Schemas** (`supabase:migrations`, `kg:schema`, `ops:control-room`)
   - kg.* (Knowledge Graph)
   - ops.* (Ops Control Room)
   - **Status**: ✅ Complete (migrations written)

3. **Odoo Baseline** (`odoo:baseline`, `odoo:rationalization`)
   - CE + OCA Must-Have installation
   - **Status**: ✅ Complete (script ready)

4. **OCA Validation Engine** (`odoo:oca-validation`, `supabase:migrations`)
   - Feature signature matching
   - Jaccard similarity
   - **Status**: ✅ Complete (schema + scripts ready)

### P1 - Execute after P0 complete

5. **Knowledge Graph Ingestion** (`kg:ingestion`, `ci:automation`)
   - Repo scan → kg.nodes/edges
   - docs/INDEX.md generation
   - **Status**: ✅ Complete (scripts ready)

6. **Worker Implementation** (`ops:workers`, `ops:control-room`)
   - SKIP LOCKED claim loop
   - Heartbeat + recovery
   - **Status**: 🟡 In progress

7. **UI Runboard** (`ui:runboard`, `ui:dashboard`)
   - Realtime updates
   - Event timeline
   - **Status**: 🟡 In progress

8. **Spec Kit CI** (`spec-kit:validation`, `ci:automation`)
   - CI enforcement
   - Validation reports
   - **Status**: ✅ Complete (workflows exist)

9. **Rationalization Workflow** (`odoo:rationalization`)
   - Complete 7-phase workflow
   - Priority-based backlog
   - **Status**: ✅ Complete (script ready)

---

## Execution Order (Recommended)

```
Phase 1: Infrastructure Foundation (P0)
├── 1. Apply Supabase schemas
├── 2. Deploy DNS consolidation
└── 3. Verify all services accessible

Phase 2: Odoo Rationalization (P0)
├── 4. Install Odoo baseline (CE + OCA)
├── 5. Apply OCA validation schema
├── 6. Generate feature signatures
├── 7. Run validation workflow
└── 8. Generate retire backlog

Phase 3: Ops Control Room (P1)
├── 9. Ingest Knowledge Graph
├── 10. Deploy worker
└── 11. Deploy UI Runboard

Phase 4: Continuous Integration (P1)
├── 12. Enable Spec Kit CI
├── 13. Schedule KG ingestion
└── 14. Schedule rationalization reports
```

---

## Verification Commands

### Infrastructure

```bash
# DNS resolution
for subdomain in erp n8n superset mcp ocr auth chat affine; do
  dig +short $subdomain.insightpulseai.net
done

# Service health
curl -I https://erp.insightpulseai.net
curl -I https://n8n.insightpulseai.net
curl -I https://superset.insightpulseai.net
```

### Supabase

```bash
# Check schemas
psql "$POSTGRES_URL" -c "\dn"
# Should show: kg, ops, public

# Check tables
psql "$POSTGRES_URL" -c "\dt kg.*"
psql "$POSTGRES_URL" -c "\dt ops.*"

# Check functions
psql "$POSTGRES_URL" -c "\df kg.*"
psql "$POSTGRES_URL" -c "\df ops.*"
```

### Odoo

```bash
# Check baseline installation
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo -c '\
    SELECT
      CASE
        WHEN author LIKE '\''%OCA%'\'' THEN '\''OCA'\''
        WHEN name LIKE '\''ipai_%'\'' THEN '\''Custom'\''
        ELSE '\''Core'\''
      END as category,
      COUNT(*) as count
    FROM ir_module_module
    WHERE state = '\''installed'\''
    GROUP BY category;\
  '\
\""

# Check validation schema
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo -c '\
    SELECT COUNT(*) FROM oca.module_index;\
  '\
\""
```

### Knowledge Graph

```bash
# Check ingestion
python scripts/generate_repo_index.py
ls -la docs/INDEX.md docs/knowledge/graph_seed.json

# Check database
psql "$POSTGRES_URL" -c "SELECT COUNT(*) FROM kg.nodes;"
psql "$POSTGRES_URL" -c "SELECT COUNT(*) FROM kg.edges;"
```

---

## Troubleshooting

### Issue: Script fails with permission error

**Solution**: Ensure you're authenticated and have org access

```bash
gh auth status
gh api user/orgs --jq '.[].login' | grep "Insightpulseai-net"
```

### Issue: Issues not appearing in project

**Solution**: Manually add issues to project

```bash
PROJECT_ID="..." # Get from script output
ISSUE_ID="..." # Get from gh issue view

gh api graphql -f query='
mutation($project:ID!,$content:ID!){
  addProjectV2ItemById(input:{projectId:$project, contentId:$content}){
    item{ id }
  }
}' -F project="$PROJECT_ID" -F content="$ISSUE_ID"
```

### Issue: Custom fields not visible

**Solution**: Show hidden fields in project settings

1. Open project in browser
2. Click Settings → Custom fields
3. Click "Show" on hidden fields
4. Refresh project

---

## Next Steps After Bootstrap

1. **Open project in browser** (URL from script output)
2. **Configure board views** (Todo, In Progress, Done lanes)
3. **Set priorities** (Update Priority field for each issue)
4. **Assign owners** (Add Owner field values)
5. **Execute Phase 1** (Infrastructure foundation)

---

**Documentation**: [docs/ops/EXECUTION_BOARD.md](./EXECUTION_BOARD.md)
**Scripts**: `scripts/bootstrap_execution_board.sh`
**Repository**: https://github.com/jgtolentino/odoo-ce
