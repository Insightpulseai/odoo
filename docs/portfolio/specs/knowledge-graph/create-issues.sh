#!/usr/bin/env bash
# Knowledge Graph - GitHub Issue Creation Script
# Run this script after configuring gh CLI: gh auth login
#
# Usage:
#   ./create-issues.sh                    # Create all issues
#   ./create-issues.sh --dry-run          # Preview commands only
#   ./create-issues.sh --repo ORG/REPO    # Specify target repo

set -euo pipefail

# Configuration
DEFAULT_REPO="${KG_REPO:-}"
DRY_RUN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --repo)
            DEFAULT_REPO="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if gh is available
if ! command -v gh &> /dev/null; then
    echo "Error: gh CLI not found. Install from https://cli.github.com/"
    exit 1
fi

# Check auth
if ! gh auth status &> /dev/null; then
    echo "Error: gh CLI not authenticated. Run: gh auth login"
    exit 1
fi

# Set repo if specified
if [[ -n "$DEFAULT_REPO" ]]; then
    gh repo set-default "$DEFAULT_REPO"
fi

create_issue() {
    local title="$1"
    local body="$2"
    local labels="${3:-}"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "Would create issue: $title"
        echo "---"
        echo "$body"
        echo "---"
        echo ""
    else
        if [[ -n "$labels" ]]; then
            gh issue create --title "$title" --body "$body" --label "$labels"
        else
            gh issue create --title "$title" --body "$body"
        fi
    fi
}

echo "Creating Knowledge Graph issues..."
echo ""

# Issue 1: Schema
create_issue \
    "KG MVP: Create kg_nodes/kg_edges/kg_docs schema + indexes" \
    "$(cat <<'EOF'
## Summary
Create the core Knowledge Graph schema in Supabase.

## Details
- Apply migration `db/migrations/20260109_KG.sql`
- Tables: `kg.nodes`, `kg.edges`, `kg.docs`, `kg.mentions`
- Indexes: B-tree on keys, GIN on tsv, IVFFlat on embeddings
- Functions: `kg.search_docs`, `kg.search_docs_vector`, `kg.get_neighbors`, `kg.upsert_node`, `kg.upsert_edge`

## Acceptance Criteria
- [ ] Migration applied to Supabase project
- [ ] RLS policies configured (authenticated read, service_role write)
- [ ] Smoke test: insert node/edge/doc works
- [ ] FTS query works
- [ ] Vector search works (with mock embedding)

## Related
- Spec: `spec/knowledge-graph/`
- Migration: `db/migrations/20260109_KG.sql`
EOF
)"

# Issue 2: GitHub webhook
create_issue \
    "KG Ingest: GitHub webhook -> Edge Function upsert nodes/edges/docs" \
    "$(cat <<'EOF'
## Summary
Create Edge Function to receive GitHub webhooks and populate the knowledge graph.

## Details
- Create Edge Function `ingest-github-event`
- Handle events: `push`, `pull_request.*`, `issues.*`, `workflow_run.*`, `check_suite.*`
- Create nodes: Repo, Branch, PR, Issue, Workflow, Run
- Create edges: IMPLEMENTS (PR → Issue), OWNS (Org → Repo)
- Store event summaries as `kg.docs`

## Entity Mapping
| GitHub Entity | Node Type | Key Pattern |
|---------------|-----------|-------------|
| Repository | Repo | `repo:<owner>/<name>` |
| Pull Request | PR | `pr:<owner>/<repo>#<num>` |
| Issue | Issue | `issue:<owner>/<repo>#<num>` |
| Workflow Run | Run | `run:<owner>/<repo>:<run_id>` |

## Acceptance Criteria
- [ ] Webhook receiver deployed
- [ ] Signature verification implemented
- [ ] Nodes created for PR/Issue/Workflow events
- [ ] Edges created for PR → Issue links
- [ ] Event payloads stored as docs
EOF
)"

# Issue 3: GitHub backfill
create_issue \
    "KG Ingest: nightly GitHub GraphQL backfill (repos, issues, PRs, actions)" \
    "$(cat <<'EOF'
## Summary
Create scheduled function to backfill GitHub data and reconcile missed webhooks.

## Details
- Create scheduled function `backfill-github`
- Use GitHub GraphQL API for efficient bulk fetching
- Fetch: repositories, issues, pull requests, workflows, workflow runs
- Upsert nodes/edges idempotently
- Schedule: daily at 02:00 UTC

## Acceptance Criteria
- [ ] GraphQL queries implemented for all entity types
- [ ] Pagination handled for large result sets
- [ ] Rate limiting respected (with backoff)
- [ ] Scheduled in Supabase cron
- [ ] Can reconstruct graph from scratch if needed
EOF
)"

# Issue 4: DigitalOcean sync
create_issue \
    "KG Ingest: DigitalOcean sync (droplets/domains/apps/certs)" \
    "$(cat <<'EOF'
## Summary
Create function to sync DigitalOcean infrastructure into the knowledge graph.

## Details
- Create Edge Function `sync-do-inventory`
- Sync: Droplets → Host nodes, Domains → Domain nodes, DNS Records → DNSRecord nodes
- Create edges: CONFIGURES (DNSRecord → Host/Service)
- Schedule: every 6 hours

## Entity Mapping
| DO Resource | Node Type | Key Pattern |
|-------------|-----------|-------------|
| Droplet | Host | `droplet:<id>` |
| Domain | Domain | `domain:<name>` |
| DNS Record | DNSRecord | `dns:<domain>:<type>:<name>` |
| App | Service | `do-app:<id>` |

## Acceptance Criteria
- [ ] DO API token stored as secret
- [ ] All droplets synced as Host nodes
- [ ] All domains synced as Domain nodes
- [ ] DNS records create CONFIGURES edges
- [ ] Scheduled sync working
EOF
)"

# Issue 5: Odoo exporter
create_issue \
    "KG Ingest: Odoo exporter (installed modules, models, views, key system params)" \
    "$(cat <<'EOF'
## Summary
Create exporter to sync Odoo metadata into the knowledge graph.

## Details
- Export from `ir.module.module` (installed modules)
- Parse manifest files for dependencies
- Create OdooModule nodes
- Create DEPENDS_ON edges from manifest
- Optional: Export models/views in phase 2

## Entity Mapping
| Odoo Entity | Node Type | Key Pattern |
|-------------|-----------|-------------|
| Module | OdooModule | `odoo:module:<technical_name>` |
| Model | OdooModel | `odoo:model:<model_name>` |
| View | OdooView | `odoo:view:<xml_id>` |

## Acceptance Criteria
- [ ] All ipai_* modules exported
- [ ] Dependency graph accurate
- [ ] Module metadata (version, author, summary) stored
- [ ] Works with docker-compose Odoo instance
EOF
)"

# Issue 6: DNS mapping
create_issue \
    "KG Model: DNSRecord node type + CONFIGURES edges" \
    "$(cat <<'EOF'
## Summary
Model DNS records and connect them to target services/hosts.

## Details
- DNSRecord nodes with type, name, value, TTL
- CONFIGURES edges:
  - A/AAAA record → Host (by IP match)
  - CNAME → Service (by name match)
- Support subdomain hierarchy

## Acceptance Criteria
- [ ] DNSRecord schema defined
- [ ] A records link to droplets by IP
- [ ] CNAME records link to services
- [ ] DNS → Service mapping queryable
EOF
)"

# Issue 7: Chat ingestion
create_issue \
    "KG Docs: ingest ChatGPT/Claude thread + extract mentions" \
    "$(cat <<'EOF'
## Summary
Store AI chat threads as documents and extract entity mentions.

## Details
- Store conversation as `kg.docs` with source='chatgpt' or 'claude'
- Extract mentions of:
  - Repositories (repo:org/name)
  - Modules (ipai_*, oca_*)
  - Droplets (by name or IP)
  - Domains
- Create `kg.mentions` with confidence scores

## Acceptance Criteria
- [ ] Chat thread stored as doc
- [ ] Entity extraction working
- [ ] Mentions link to existing nodes
- [ ] Confidence scores assigned
EOF
)"

# Issue 8: Embeddings
create_issue \
    "KG Index: embed kg_docs + upsert vectors; enable hybrid search" \
    "$(cat <<'EOF'
## Summary
Create embedding pipeline for semantic search.

## Details
- Create Edge Function `embed-doc`
- Use OpenAI text-embedding-3-small (1536 dims)
- Batch processing for backlog
- Handle rate limiting

## Acceptance Criteria
- [ ] Embedding function deployed
- [ ] New docs automatically embedded
- [ ] Backlog processing working
- [ ] Vector search returns relevant results
- [ ] Cost tracking implemented
EOF
)"

# Issue 9: Query API
create_issue \
    "KG API: /kg_query hybrid search + neighborhood expansion" \
    "$(cat <<'EOF'
## Summary
Create RAG-ready query API combining FTS, vector search, and graph traversal.

## Details
- Create Edge Function `kg-query`
- Hybrid search: FTS + vector with RRF ranking
- Mention expansion: doc → related nodes
- Graph traversal: include neighboring nodes

## API Contract
```json
// Request
{
  "query": "What modules depend on ipai_workspace_core?",
  "embedding": [0.1, ...],
  "limit": 10
}

// Response
{
  "docs": [...],
  "nodes": [...],
  "edges": [...]
}
```

## Acceptance Criteria
- [ ] Endpoint deployed
- [ ] FTS + vector combined correctly
- [ ] Mentions expanded to nodes
- [ ] Graph neighbors included
- [ ] Response under 200ms p95
EOF
)"

# Issue 10: UI
create_issue \
    "KG UI: Graph explorer (node view, neighbors, doc evidence)" \
    "$(cat <<'EOF'
## Summary
Create minimal UI for exploring the knowledge graph.

## Details
- Add page to control-room app
- Search bar with hybrid search
- Node detail panel (type, key, data)
- Edge list (incoming/outgoing)
- Doc evidence panel

## Features
- [ ] Search bar
- [ ] Node view
- [ ] Edge list
- [ ] Doc evidence
- [ ] Basic graph visualization (optional)

## Acceptance Criteria
- [ ] Can search for any entity
- [ ] Can view node details
- [ ] Can see relationships
- [ ] Can see supporting documents
EOF
)"

echo ""
echo "Done! Created 10 issues for Knowledge Graph implementation."
