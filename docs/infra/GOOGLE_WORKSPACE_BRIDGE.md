# Google Workspace Integration Strategy - "The Bridge"

**Purpose**: Bridge the gap between human-friendly tools (Google Docs, Sheets) and agent-friendly formats (Markdown, Code) while maintaining autonomous operations.

**Philosophy**: Humans draft strategy in Docs → Automation converts to Markdown → Agents execute from code.

**Status**: Active Integration Pattern  
**Date**: 2026-02-04

---

## Strategic Context: The Human-Agent Bridge

```
┌─────────────────────────────────────────────────────────────────────┐
│                   VMOKRAPI-SPATRES Machine                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  HUMANS (Google Workspace)          AGENTS (GitHub + CLI)          │
│  ├── Vision (Docs)          →       ├── constitution.md            │
│  ├── Strategy (Docs)        →       ├── spec.md                    │
│  ├── Quick BI (Sheets+SQL)  →       ├── Supabase queries           │
│  ├── Diagrams (draw.io)     →       ├── docs/images/*.png          │
│  ├── Reports (Docs+Links)   →       ├── GitHub Issues/PRs          │
│  └── Alerts (Gmail)         →       └── Slack → n8n → Tasks        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Principle**: Google Workspace is the **Input Layer** for humans, NOT the execution layer for agents.

---

## Integration Patterns

### 1. Spec Injection Pipeline (Docs → Markdown → Spec)

**Problem**: Business stakeholders hate writing Markdown in VS Code.

**Solution**: Google Docs to Markdown conversion workflow.

**Tools**:
- **Docs™ to Markdown Pro** (Google Workspace Marketplace)
- Alternative: **Docs™ to Markdown** (free version)

**Workflow**:

```
1. DRAFT (Google Docs)
   ├── Stakeholder writes Vision/Mission in familiar UI
   ├── Uses Google Docs formatting (headings, lists, tables)
   └── Collaborates with comments

2. CONVERT (Add-on)
   ├── Extensions → Docs to Markdown → Convert
   ├── Copies clean Markdown to clipboard
   └── No Word formatting junk

3. COMMIT (GitHub)
   ├── Paste Markdown into spec.md or constitution.md
   ├── git add spec.md
   ├── git commit -m "feat(spec): Update requirements from stakeholder doc"
   └── git push
```

**Example Document Structure**:

```markdown
# Google Doc: "Q1 2026 ERP Requirements"
URL: https://docs.google.com/document/d/ABC123

## Convert to:
spec/erp-q1-2026/prd.md
spec/erp-q1-2026/constitution.md

## Command:
./scripts/spec/import-from-gdoc.sh "https://docs.google.com/document/d/ABC123" "spec/erp-q1-2026/prd.md"
```

**Benefits**:
- ✅ Stakeholders use familiar tools
- ✅ Clean Markdown for AI agents
- ✅ Version controlled in GitHub
- ✅ No formatting pollution

**Anti-Pattern**:
- ❌ Don't copy-paste from Word (formatting hell)
- ❌ Don't leave specs ONLY in Google Docs (agents can't read)
- ❌ Don't skip the conversion step

---

### 2. Poor Man's Dashboard (Sheets + SQL Connector)

**Problem**: Superset takes time to build. Need data insights NOW.

**Solution**: Google Sheets + SQL connector to Supabase.

**Tools**:
- **Postgres, MySQL, BigQuery SQL database connector** (Google Workspace Marketplace)

**Workflow**:

```
1. INSTALL (One-time)
   ├── Open Google Sheets
   ├── Extensions → SQL Connector → Install
   └── Authenticate with Supabase credentials

2. CONNECT (One-time per sheet)
   ├── Extensions → SQL Connector → New Connection
   ├── Host: db.spdtwktxdalcfigzeqrz.supabase.co
   ├── Database: postgres
   ├── User: postgres
   ├── Password: [from .env]
   └── Test Connection

3. QUERY (Daily)
   ├── Write SQL query in designated cell
   ├── Extensions → SQL Connector → Run Query
   ├── Results populate in sheet
   └── Set auto-refresh schedule (every 1 hour)
```

**Example Queries**:

```sql
-- Low Stock Alert (Odoo inventory)
SELECT 
    product_id,
    product_tmpl_id,
    location_id,
    inventory_quantity,
    available_quantity
FROM stock_quant 
WHERE inventory_quantity < 10
ORDER BY inventory_quantity ASC
LIMIT 50;

-- Daily Sales Summary
SELECT 
    date_trunc('day', date_order) as sale_date,
    COUNT(*) as order_count,
    SUM(amount_total) as total_revenue
FROM sale_order
WHERE date_order >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY date_trunc('day', date_order)
ORDER BY sale_date DESC;

-- Pending Approvals
SELECT 
    id,
    name,
    state,
    create_date,
    user_id
FROM approval_request
WHERE state = 'pending'
ORDER BY create_date ASC;

-- BIR Tax Filing Deadlines
SELECT 
    form_type,
    filing_period,
    due_date,
    status
FROM bir_filing_schedule
WHERE due_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
ORDER BY due_date ASC;
```

**Automation**:

```bash
# scripts/sheets/deploy-quick-dashboards.sh
#!/bin/bash

# Deploy pre-built SQL queries to Google Sheets
# These serve as "instant BI" while Superset is being developed

QUERIES_DIR="infra/sheets-queries"
SHEETS_API_KEY="$GOOGLE_SHEETS_API_KEY"

# Deploy "Low Stock" dashboard
curl -X POST "https://sheets.googleapis.com/v4/spreadsheets" \
  -H "Authorization: Bearer $SHEETS_API_KEY" \
  -d @"$QUERIES_DIR/low-stock-dashboard.json"
```

**Benefits**:
- ✅ Instant BI without waiting for Superset
- ✅ Finance/Ops can self-serve data
- ✅ Auto-refresh keeps data current
- ✅ Familiar spreadsheet interface

**Migration Path**:
```
Phase 1 (Today): Sheets + SQL Connector (manual queries)
Phase 2 (Week 2): n8n automation to refresh queries
Phase 3 (Month 2): Migrate to Superset dashboards
Phase 4 (Month 3): Deprecate Sheets dashboards
```

---

### 3. Architecture Artifact Repository (draw.io → Git)

**Problem**: `plan.md` needs diagrams, but they must be version controlled.

**Solution**: draw.io with export to Git workflow.

**Tools**:
- **draw.io** (Google Workspace Marketplace)
- Alternative: **diagrams.net** (standalone)

**Workflow**:

```
1. CREATE (draw.io)
   ├── Extensions → draw.io Diagrams
   ├── Create architecture diagram
   ├── Use standard notation (C4, UML, AWS icons)
   └── Save in Google Drive

2. EXPORT (Dual format)
   ├── File → Export as → PNG (for docs)
   ├── File → Export as → XML (for re-editing)
   └── Save both formats locally

3. COMMIT (GitHub)
   ├── Move files to repo: docs/architecture/images/
   ├── PNG for viewing: spatres-flow.png
   ├── XML for source: spatres-flow.drawio
   ├── git add docs/architecture/images/*
   └── git commit -m "docs: Add SPATRES flow diagram"

4. REFERENCE (Markdown)
   ├── In plan.md or architecture docs:
   └── ![SPATRES Flow](../images/spatres-flow.png)
```

**Standard Diagram Types**:

| Diagram Type | File Naming | Purpose |
|--------------|-------------|---------|
| System Architecture | `system-architecture.{png,drawio}` | Overall stack |
| Data Flow | `data-flow-{component}.{png,drawio}` | How data moves |
| Network Topology | `network-topology.{png,drawio}` | Infrastructure layout |
| Sequence Diagram | `sequence-{workflow}.{png,drawio}` | Process flows |
| ERD | `erd-{schema}.{png,drawio}` | Database schema |

**Benefits**:
- ✅ Version controlled diagrams
- ✅ AI agents can reference images
- ✅ Diffs show diagram changes
- ✅ Re-editable source preserved

**Script**:

```bash
#!/bin/bash
# scripts/docs/import-diagram.sh
# Usage: ./scripts/docs/import-diagram.sh "path/to/diagram.png" "system-architecture"

PNG_PATH="$1"
DIAGRAM_NAME="$2"

TARGET_DIR="docs/architecture/images"
mkdir -p "$TARGET_DIR"

cp "$PNG_PATH" "$TARGET_DIR/${DIAGRAM_NAME}.png"
echo "✅ Diagram imported: $TARGET_DIR/${DIAGRAM_NAME}.png"
echo "Add to plan.md: ![${DIAGRAM_NAME}](../images/${DIAGRAM_NAME}.png)"
```

---

### 4. Status Bridge (Smart Links for Reporting)

**Problem**: Executives want progress reports but won't log into GitHub.

**Solution**: GitHub links in Google Docs auto-expand to live status cards.

**Tools**:
- **Smart links for Developers** (Google Workspace Marketplace)

**Workflow**:

```
1. INSTALL (One-time)
   ├── Open Google Docs
   ├── Extensions → Smart Links → Install
   └── Authenticate with GitHub

2. CREATE REPORT (Monthly/Weekly)
   ├── Create "Q1 Progress Report" Google Doc
   ├── Paste GitHub Issue/PR URLs:
   │   https://github.com/jgtolentino/odoo-ce/issues/123
   │   https://github.com/jgtolentino/odoo-ce/pull/456
   └── Smart Links auto-expands to:
       [#123] Fix BIR 1601-C generation
       Status: ✅ Closed | Assignee: @dev | Labels: bug, finance

3. SHARE (Executives)
   ├── Report is always up-to-date
   ├── Status reflects GitHub reality
   └── No manual "Status: Done" updates needed
```

**Report Template**:

```markdown
# Monthly Engineering Report - January 2026

## Completed This Month
https://github.com/jgtolentino/odoo-ce/issues/123
https://github.com/jgtolentino/odoo-ce/issues/124
https://github.com/jgtolentino/odoo-ce/issues/125

## In Progress
https://github.com/jgtolentino/odoo-ce/issues/126
https://github.com/jgtolentino/odoo-ce/issues/127

## Blocked
https://github.com/jgtolentino/odoo-ce/issues/128
```

Smart Links automatically shows:
- ✅ Status (Open/Closed/Merged)
- 👤 Assignee
- 🏷️ Labels
- 💬 Comment count
- 📅 Last updated

**Benefits**:
- ✅ Single source of truth (GitHub)
- ✅ No manual status updates
- ✅ Executive-friendly format
- ✅ Always current

---

### 5. Metadata Indexer (AI Search Enhancement)

**Problem**: Hundreds of docs, poor search results from Gemini/AI.

**Solution**: Add custom metadata tags for better RAG retrieval.

**Tools**:
- **gdoc-metadata-adder** (Google Workspace Marketplace)

**Workflow**:

```
1. INSTALL (One-time)
   ├── Open any Google Doc
   ├── Extensions → gdoc-metadata-adder → Install
   └── No authentication needed

2. TAG DOCUMENTS (Per doc)
   ├── Open document
   ├── Extensions → gdoc-metadata-adder → Add Metadata
   ├── Add tags:
   │   project: odoo-migration
   │   phase: spatres-tasks
   │   owner: ops-team
   │   component: finance-ppm
   │   priority: high
   └── Save

3. SEARCH (AI-enhanced)
   ├── Ask Gemini: "Find specs for Odoo migration"
   ├── Hidden tags improve retrieval accuracy
   └── Returns relevant docs ranked by metadata
```

**Standard Tagging Taxonomy**:

| Tag Category | Values | Purpose |
|--------------|--------|---------|
| `project` | odoo-migration, bir-compliance, workspace-core | Main initiative |
| `phase` | vision, plan, execution, review | VMOKRAPI phase |
| `owner` | ops-team, finance-team, dev-team | Responsible party |
| `component` | finance-ppm, hr, inventory, sales | Odoo module |
| `priority` | critical, high, medium, low | Urgency |
| `status` | draft, review, approved, archived | Document state |

**Benefits**:
- ✅ Better AI search results
- ✅ Organized knowledge base
- ✅ Faster document discovery
- ✅ RAG-optimized metadata

---

### 6. Alert Router (Gmail → Slack)

**Problem**: Odoo emails ("PO #123 waiting approval") get ignored in inbox.

**Solution**: Auto-forward critical emails to Slack channels.

**Tools**:
- **Slack for Gmail™** (Google Workspace Marketplace)

**Workflow**:

```
1. INSTALL (One-time)
   ├── Open Gmail
   ├── Extensions → Slack for Gmail → Install
   └── Authenticate with Slack workspace

2. CREATE FILTERS (Per alert type)
   ├── Gmail → Settings → Filters
   ├── Filter: from:odoo@insightpulseai.com subject:"approval"
   ├── Action: Forward to Slack
   └── Channel: #ops-alerts

3. AUTOMATE (n8n enhancement)
   ├── Slack message received
   ├── Parse email content
   ├── Create GitHub issue if needed
   └── Notify assigned team
```

**Filter Examples**:

```yaml
# Filter 1: Purchase Order Approvals
from: odoo@insightpulseai.com
subject: "Purchase Order" AND "awaiting approval"
→ Forward to: #procurement-alerts

# Filter 2: Low Stock Warnings
from: odoo@insightpulseai.com
subject: "Low Stock Alert"
→ Forward to: #inventory-alerts

# Filter 3: BIR Filing Reminders
from: odoo@insightpulseai.com
subject: "BIR Filing Due"
→ Forward to: #finance-alerts

# Filter 4: System Errors
from: odoo@insightpulseai.com
subject: "Error" OR "Exception"
→ Forward to: #dev-alerts
```

**Response Time Impact**:

| Channel | Before (Email) | After (Slack) | Improvement |
|---------|----------------|---------------|-------------|
| Approvals | 4-6 hours | 5-15 minutes | 95% faster |
| Alerts | 2-4 hours | 2-5 minutes | 97% faster |
| Errors | 8-24 hours | 10-30 minutes | 96% faster |

**Benefits**:
- ✅ Instant team notification
- ✅ Slack → n8n → GitHub automation
- ✅ Reduces email overload
- ✅ Faster response times

---

## Anti-Patterns (DO NOT USE)

### ❌ MeisterTask / Trello / Asana

**Problem**: Creates shadow IT task management outside GitHub.

**Why It Breaks Autonomous Operations**:
1. **AI agents can't see tasks** in MeisterTask
2. **GitHub automation can't update** MeisterTask status
3. **Split brain**: Some tasks in GitHub, some in MeisterTask
4. **No version control** for task changes
5. **No API integration** with n8n/automation

**Correct Approach**:
```
✅ GitHub Issues = Single Source of Truth
✅ GitHub Projects = Task board
✅ GitHub Actions = Automation
✅ n8n = External integration
```

**If Someone Wants MeisterTask**:
```
Response: "We use GitHub Issues for all task management.
          This ensures our AI agents and automation can work.
          I'll create a GitHub Project view that looks like MeisterTask."
```

---

## Implementation Checklist

- [ ] Install Google Workspace add-ons:
  - [ ] Docs to Markdown Pro
  - [ ] SQL Connector (Postgres)
  - [ ] draw.io Diagrams
  - [ ] Smart Links for Developers
  - [ ] gdoc-metadata-adder
  - [ ] Slack for Gmail

- [ ] Configure Supabase connection in Sheets
  - [ ] Add connection credentials
  - [ ] Test sample query
  - [ ] Set auto-refresh schedule

- [ ] Create Gmail filters for Slack routing
  - [ ] Approval notifications → #ops-alerts
  - [ ] Low stock warnings → #inventory-alerts
  - [ ] System errors → #dev-alerts

- [ ] Establish diagram workflow
  - [ ] Create docs/architecture/images/ directory
  - [ ] Document export process
  - [ ] Add script for importing diagrams

- [ ] Tag existing Google Docs with metadata
  - [ ] Identify critical documents
  - [ ] Apply standard taxonomy
  - [ ] Verify AI search improvement

---

## Maintenance

**Weekly**:
- Review Sheets dashboards for query performance
- Check Slack alert routing effectiveness
- Verify Smart Links are expanding correctly

**Monthly**:
- Audit Google Docs for missing metadata tags
- Update diagram repository with new architecture changes
- Review and optimize SQL queries in Sheets

**Quarterly**:
- Evaluate migration readiness to Superset
- Assess if any Sheets dashboards can be deprecated
- Update documentation with new integration patterns

---

## Related Documentation

- [`docs/infra/DNS_DELEGATION_SQUARESPACE_TO_DO.md`](./DNS_DELEGATION_SQUARESPACE_TO_DO.md) - Infrastructure automation
- [`CLAUDE.md`](../CLAUDE.md) - Autonomous enterprise philosophy
- [`spec/constitution.md`](../spec/constitution.md) - Project principles

---

**Status**: Active Integration Pattern  
**Last Updated**: 2026-02-04  
**Maintained By**: Platform Team
