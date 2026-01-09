# Execution Board - GitHub Projects Setup

**Organization**: `Insightpulseai-net`
**Repository**: `jgtolentino/odoo-ce`
**Milestone**: `Ops Control Room v1`

---

## Overview

The **Execution Board** is an org-level GitHub Project (ProjectV2) that tracks all infrastructure, rationalization, and ops work across the InsightPulse AI stack.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Execution Board (Org Project)                 │
├─────────────────────────────────────────────────────────────────┤
│  Custom Fields:                                                  │
│  - Area: Infra, DNS, Odoo, Supabase, Agents, KG, UI, CI/CD      │
│  - Priority: P0, P1, P2                                          │
│  - Target: fin-workspace, prod, staging                          │
│                                                                   │
│  Views:                                                          │
│  - Table (all issues with custom fields)                         │
│  - Board by Status (Todo, In Progress, Done)                    │
│  - By Area (group by Area field)                                │
│  - By Priority (group by Priority field)                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  GitHub Issues (jgtolentino/odoo-ce)             │
├─────────────────────────────────────────────────────────────────┤
│  Milestone: Ops Control Room v1                                 │
│                                                                   │
│  Labels:                                                         │
│  - ops:control-room, ops:workers                                │
│  - kg:ingestion, kg:schema                                      │
│  - spec-kit:validation, spec-kit:enforcement                    │
│  - supabase:migrations, supabase:rls                            │
│  - dns:routing, dns:ssl                                         │
│  - infra:nginx, infra:docker                                    │
│  - odoo:rationalization, odoo:baseline, odoo:oca-validation     │
│  - ui:runboard, ui:dashboard                                    │
│  - ci:automation                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Setup

### Prerequisites

- GitHub CLI installed: `brew install gh`
- Authenticated: `gh auth login`
- Access to `Insightpulseai-net` organization

### Single-Command Bootstrap

```bash
./scripts/bootstrap_execution_board.sh
```

This script will:

1. ✅ Create org-level Project: **Execution Board**
2. ✅ Add custom fields (Area, Priority, Target)
3. ✅ Create labels in `jgtolentino/odoo-ce`
4. ✅ Create milestone: **Ops Control Room v1**
5. ✅ Create 9 tracking issues
6. ✅ Add issues to project

**Duration**: ~2 minutes

---

## Project Structure

### Custom Fields

| Field | Type | Options | Purpose |
|-------|------|---------|---------|
| **Area** | Single-select | Infra, DNS, Odoo, Supabase, Agents, KG, UI, CI/CD | Categorize by domain |
| **Priority** | Single-select | P0, P1, P2 | Execution order |
| **Target** | Single-select | fin-workspace, prod, staging | Deployment target |
| **Owner** | Assignee | - | Responsible person |
| **Due** | Date | - | Deadline |

### Labels (Namespaced)

| Prefix | Labels | Purpose |
|--------|--------|---------|
| `ops:*` | control-room, workers | Ops Control Room operations |
| `kg:*` | ingestion, schema | Knowledge Graph |
| `spec-kit:*` | validation, enforcement | Spec Kit automation |
| `supabase:*` | migrations, rls | Supabase operations |
| `dns:*` | routing, ssl | DNS and SSL configuration |
| `infra:*` | nginx, docker | Infrastructure |
| `odoo:*` | rationalization, baseline, oca-validation | Odoo module work |
| `ui:*` | runboard, dashboard | UI components |
| `ci:*` | automation | CI/CD automation |

### Views

1. **Table** - All issues with custom fields (default)
2. **Board by Status** - Kanban: Todo → In Progress → Done
3. **By Area** - Grouped by Area field
4. **By Priority** - Grouped by Priority field

---

## Issues Breakdown

### Infrastructure (3 issues)

#### 1. DNS Consolidation
**Labels**: `dns:routing`, `dns:ssl`, `infra:nginx`
**Priority**: P0
**Target**: fin-workspace

**Summary**: Point all subdomains to 178.128.112.214 with nginx host-based routing

**Subdomains**:
- ✅ erp.insightpulseai.net → Odoo (8069)
- ✅ n8n.insightpulseai.net → n8n (5678)
- ✅ superset.insightpulseai.net → Superset (8088)
- 🟡 mcp.insightpulseai.net → MCP Coordinator (placeholder)
- 🟡 ocr.insightpulseai.net → OCR Service (placeholder)
- 🟡 auth.insightpulseai.net → Keycloak (placeholder)
- 🟡 chat.insightpulseai.net → Mattermost (placeholder)
- 🟡 affine.insightpulseai.net → Affine (placeholder)

**Files**: `deploy/nginx-complete.conf`, `docs/email/Mailgun_DNS.md`

#### 2. Supabase Schemas
**Labels**: `supabase:migrations`, `supabase:rls`, `kg:schema`, `ops:control-room`
**Priority**: P0
**Target**: prod

**Summary**: Create kg.* (Knowledge Graph) and ops.* (Ops Control Room) schemas

**kg schema**:
- `kg.nodes` (id, kind, name, ref, props)
- `kg.edges` (src, rel, dst, props)
- `kg.sources` (hash, fetched_at, url, content)
- Graph functions: get_node_neighbors, get_path, get_subgraph, search_nodes

**ops schema**:
- `ops.sessions`, `ops.run_templates`, `ops.runs`, `ops.run_events`, `ops.artifacts`
- Functions: claim_run (SKIP LOCKED), heartbeat_run, start_run, complete_run, fail_run, cancel_run

**Files**: `db/migrations/20260108_kg_schema.sql`, `db/migrations/20260108_ops_schema.sql`

#### 3. Knowledge Graph Ingestion
**Labels**: `kg:ingestion`, `kg:schema`, `ci:automation`
**Priority**: P1
**Target**: prod

**Summary**: Ingestion pipeline for repos/specs/issues → kg.*

**Sources**:
1. Local filesystem (spec/, addons/, apps/, workflows/, scripts/)
2. GitHub GraphQL API (issues, PRs, repos)
3. Supabase metadata (schemas, functions, policies)

**Output**:
- `docs/INDEX.md` (318 entries)
- `docs/knowledge/graph_seed.json` (318 nodes, 317 edges)
- `kg.nodes` table (deterministic IDs)
- `kg.edges` table (relationships)

**Files**: `scripts/generate_repo_index.py`, `scripts/ingest_knowledge_graph.py`

---

### Ops Control Room (2 issues)

#### 4. Worker Reference Implementation
**Labels**: `ops:workers`, `ops:control-room`
**Priority**: P1
**Target**: fin-workspace

**Summary**: Long-running worker with SKIP LOCKED claim loop

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

**Files**: `apps/pulser-runner/src/worker.ts`, `apps/pulser-runner/src/executor.ts`

#### 5. Ops UI Runboard
**Labels**: `ui:runboard`, `ui:dashboard`, `ops:control-room`
**Priority**: P1
**Target**: prod

**Summary**: Realtime dashboard for runs/events/artifacts

**Features**:
- Lane view (pending, processing, completed, failed)
- Real-time updates via Supabase Realtime (<2s)
- Cancel run action
- Artifact download links
- Event timeline per run
- Worker health status

**Files**: `apps/control-room/src/app/runboard/page.tsx`, `apps/control-room/src/components/RunLane.tsx`

---

### Spec Kit (1 issue)

#### 6. Spec Kit Validation CI
**Labels**: `spec-kit:validation`, `spec-kit:enforcement`, `ci:automation`
**Priority**: P1
**Target**: prod

**Summary**: Comprehensive Spec Kit validation in CI

**Validation checks**:
1. Required files exist (constitution.md, prd.md, plan.md, tasks.md)
2. Minimum content per file (≥10 non-heading lines)
3. constitution.md has "Non-Negotiable Rules" section
4. tasks.md has proper status markers
5. No undocumented spec bundles

**Files**: `.github/workflows/spec-kit-enforce.yml`, `scripts/validate_spec_kit.py`, `scripts/check_undocumented_specs.py`, `scripts/generate_spec_report.py`

---

### Odoo Rationalization (3 issues)

#### 7. Odoo Baseline Installation
**Labels**: `odoo:baseline`, `odoo:rationalization`
**Priority**: P0
**Target**: prod

**Summary**: Install Odoo CE + OCA Must-Have before custom modules

**CE baseline**:
- base, web, mail, account, accountant, sale_management, purchase, stock, crm, project, hr_timesheet

**OCA Must-Have**:
- account_financial_report, account_lock_date_update, account_fiscal_year
- base_tier_validation, mass_editing, report_xlsx

**OCA Should-Have**:
- sale_order_type, purchase_order_type, auditlog, web_responsive

**Files**: `scripts/install_baseline.sh`

#### 8. OCA Validation Engine
**Labels**: `odoo:oca-validation`, `odoo:rationalization`, `supabase:migrations`
**Priority**: P0
**Target**: prod

**Summary**: Feature signature matching for detecting redundant ipai_* modules

**Database schema**:
- `oca.module_index` (OCA module catalog with keywords)
- `oca.custom_module_signatures` (ipai_* feature signatures)
- `oca.validation_results` (match confidence + recommendations)
- `oca.module_footprints` (UI elements vs business logic)

**Validation logic**:
1. Extract feature signatures (models, views, menus, keywords)
2. Compute Jaccard similarity vs OCA index
3. Identify UI-only modules (zero models/fields/security)
4. Generate KEEP/REDUCE/RETIRE recommendations

**Decision rule**:
- **RETIRE**: UI-only + OCA match ≥0.7
- **REDUCE**: UI-only + OCA match ≥0.4
- **KEEP**: Unique models/fields/security

**Files**: `db/migrations/20260108_oca_validation.sql`, `scripts/generate_module_signatures.py`

#### 9. Rationalization Workflow
**Labels**: `odoo:rationalization`, `odoo:baseline`, `odoo:oca-validation`
**Priority**: P1
**Target**: prod

**Summary**: Execute complete rationalization workflow

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

**Files**: `scripts/execute_rationalization.sh`, `docs/rationalization/README.md`, `docs/rationalization/EXECUTION_CHECKLIST.md`

---

## Usage Workflows

### Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/jgtolentino/odoo-ce.git
cd odoo-ce

# 2. Run bootstrap script
./scripts/bootstrap_execution_board.sh

# 3. Open project in browser
# (URL will be displayed at end of script)

# 4. Configure views
# - Table: Add filters (Status, Area, Priority)
# - Board: Create lanes (Todo, In Progress, Done)
# - By Area: Group by Area field
# - By Priority: Group by Priority field
```

### Working with Issues

```bash
# List all issues in milestone
gh issue list --repo jgtolentino/odoo-ce --milestone "Ops Control Room v1"

# Filter by label
gh issue list --repo jgtolentino/odoo-ce --label "odoo:rationalization"

# View specific issue
gh issue view 123 --repo jgtolentino/odoo-ce

# Update issue
gh issue edit 123 --repo jgtolentino/odoo-ce --add-label "P0" --add-assignee "@me"

# Close issue
gh issue close 123 --repo jgtolentino/odoo-ce --comment "Completed and verified"
```

### Project Management

```bash
# Add new issue to project
gh api graphql -f query='
mutation($project:ID!,$content:ID!){
  addProjectV2ItemById(input:{projectId:$project, contentId:$content}){
    item{ id }
  }
}' -F project="PROJECT_ID" -F content="ISSUE_ID"

# Update custom field value
# (Use GitHub web UI - GraphQL mutation is complex)

# Bulk operations
# Use GitHub Projects bulk edit feature
```

---

## Verification

### Check Project Setup

```bash
# 1. Verify project exists
gh api graphql -f query='
query($login:String!,$title:String!){
  organization(login:$login){
    projectsV2(first:50, query:$title){
      nodes{ id title url }
    }
  }
}' -F login="Insightpulseai-net" -F title="Execution Board"

# 2. Verify issues exist
gh issue list --repo jgtolentino/odoo-ce --milestone "Ops Control Room v1" | wc -l
# Should return: 9

# 3. Verify labels
gh label list --repo jgtolentino/odoo-ce | grep -E "ops:|kg:|spec-kit:|supabase:|dns:|infra:|odoo:|ui:|ci:" | wc -l
# Should return: 18
```

### Health Checks

```bash
# DNS resolution
for subdomain in erp n8n superset mcp ocr auth chat affine; do
  echo "$subdomain.insightpulseai.net:"
  dig +short $subdomain.insightpulseai.net
done

# Service accessibility
for subdomain in erp n8n superset; do
  echo "$subdomain.insightpulseai.net:"
  curl -I https://$subdomain.insightpulseai.net 2>&1 | head -1
done

# Supabase schema verification
psql "$POSTGRES_URL" -c "SELECT COUNT(*) FROM kg.nodes;"
psql "$POSTGRES_URL" -c "SELECT COUNT(*) FROM ops.runs;"

# Odoo health check
ssh root@178.128.112.214 "docker exec odoo-erp-prod odoo -d odoo --stop-after-init"
```

---

## Automation

### GitHub Actions Integration

All rationalization scripts can run in CI:

```yaml
# .github/workflows/rationalization-report.yml
name: Rationalization Report
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  generate-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate rationalization report
        run: |
          python scripts/generate_module_signatures.py
          python scripts/generate_repo_index.py
      - name: Commit reports
        run: |
          git add docs/rationalization/ docs/INDEX.md docs/knowledge/
          git commit -m "chore: update rationalization reports"
          git push
```

### Scheduled Ingestion

```yaml
# .github/workflows/kg-ingestion.yml
name: Knowledge Graph Ingestion
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run ingestion
        env:
          POSTGRES_URL: ${{ secrets.POSTGRES_URL }}
        run: python scripts/ingest_knowledge_graph.py
```

---

## Best Practices

### Issue Management

1. **Use labels consistently** - Follow namespace convention (prefix:suffix)
2. **Update status regularly** - Move cards across board lanes
3. **Close with comments** - Document completion and verification
4. **Link PRs to issues** - Use "Closes #123" in PR description
5. **Update custom fields** - Keep Area, Priority, Target accurate

### Project Hygiene

1. **Archive completed milestones** - After all issues closed
2. **Regular triage** - Weekly review of open issues
3. **Update priorities** - Based on business needs
4. **Remove stale issues** - Close if no longer relevant
5. **Maintain views** - Keep filters and groupings useful

### Collaboration

1. **Assign ownership** - Every issue has an owner
2. **Add due dates** - For time-sensitive work
3. **Use mentions** - Tag relevant people in comments
4. **Document decisions** - In issue comments
5. **Share progress** - Weekly project updates

---

## Troubleshooting

### Issue: Project not found

**Symptom**: GraphQL query returns empty nodes array

**Solution**:
```bash
# Check organization access
gh api user/orgs --jq '.[].login' | grep "Insightpulseai-net"

# If not found, request access from org admin
```

### Issue: Cannot create issues

**Symptom**: `gh issue create` fails with permission error

**Solution**:
```bash
# Check repository access
gh repo view jgtolentino/odoo-ce

# If not found, ensure you have write access
```

### Issue: Custom fields not showing

**Symptom**: Fields exist but not visible in UI

**Solution**:
1. Open project in browser
2. Go to Settings → Custom fields
3. Click "Show" on hidden fields
4. Refresh project view

### Issue: Labels not applying

**Symptom**: Labels exist but not attached to issues

**Solution**:
```bash
# Re-run label creation
for label in ops:control-room kg:ingestion spec-kit:validation; do
  gh label create "$label" -R jgtolentino/odoo-ce --force
done

# Manually apply to issues
gh issue edit 123 --add-label "ops:control-room"
```

---

## References

- **GitHub Projects Docs**: https://docs.github.com/en/issues/planning-and-tracking-with-projects
- **GraphQL API**: https://docs.github.com/en/graphql
- **GitHub CLI**: https://cli.github.com/manual/

---

**Last Updated**: 2026-01-08
**Maintainer**: Jake Tolentino
**Repository**: https://github.com/jgtolentino/odoo-ce
