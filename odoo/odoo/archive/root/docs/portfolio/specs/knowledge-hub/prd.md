# PRD: Knowledge Hub

## Problem Statement

Current documentation tooling fails enterprise needs:

1. **Confluence** - No machine-readable knowledge graph, weak versioning
2. **Notion** - No RLS, poor enterprise governance
3. **NotebookLM** - Excellent synthesis but no wiki structure
4. **RAG pipelines** - Good retrieval but no human authoring layer

Teams need a platform that serves both:
- **Humans**: Browse, search, edit, version docs
- **Machines**: Chunk, embed, cite, retrieve knowledge

## Target Users

| Persona | Needs | Current Pain |
|---------|-------|--------------|
| Technical Writer | WYSIWYG + version control + publishing | Context switching between tools |
| Developer | API reference + code examples + citations | Scattered docs, no provenance |
| Support Engineer | Quick lookup + related topics + journeys | Manual knowledge assembly |
| AI Agent | Grounded answers with citations | No structured source linking |
| Compliance | Audit trail + version history | Untracked changes |

## Solution Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Knowledge Hub UI                              │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │  Wiki Tree    │  │   Notebook    │  │    Search     │       │
│  │  (Spaces/     │  │   Editor      │  │  (Hybrid      │       │
│  │   Pages)      │  │   (Blocks)    │  │   BM25+Vec)   │       │
│  └───────────────┘  └───────────────┘  └───────────────┘       │
└──────────────────────────────┬──────────────────────────────────┘
                               │ REST/GraphQL API
┌──────────────────────────────┴──────────────────────────────────┐
│                    Supabase Backend                              │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │  kb.* Schema  │  │  rag.* Schema │  │  Edge         │       │
│  │  (artifacts,  │  │  (chunks,     │  │  Functions    │       │
│  │   versions)   │  │   embeddings) │  │  (search)     │       │
│  └───────────────┘  └───────────────┘  └───────────────┘       │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────┴──────────────────────────────────┐
│                    Processing Pipeline                           │
│  Bronze (Crawl) → Silver (Normalize) → Gold (Chunk/Embed)       │
│  n8n orchestration + Spark compute + Delta storage              │
└─────────────────────────────────────────────────────────────────┘
```

### 1. Wiki Tree (Spaces → Pages)

Hierarchical documentation structure:

```
Spaces
├── Platform Docs
│   ├── Architecture
│   │   ├── Overview
│   │   └── Data Flow
│   └── API Reference
├── Odoo Modules
│   ├── Sales
│   └── Inventory
└── Runbooks
    ├── Deployment
    └── Incident Response
```

**Features:**
- Drag-and-drop reordering
- Permission inheritance (space → page)
- Version comparison (diff view)
- Publication workflow (draft → review → published)

### 2. Notebook Editor

NotebookLM-style block-based authoring:

```
┌────────────────────────────────────────────┐
│ Notebook: Q4 Architecture Review           │
├────────────────────────────────────────────┤
│ [source] SAP Integration Guide (attached)  │
│ [source] OCA hr-expense repo               │
│ [note] Key requirements from stakeholder   │
│ [query] SELECT * FROM capability_map       │
│ [summary] Based on sources, the gap is...  │
│ [decision] ADR-0042: Use Supabase RLS      │
│ [citation] Chunk: hr_expense_policy.md:42  │
├────────────────────────────────────────────┤
│ [Export as...] ▼ doc_page | spec_bundle    │
└────────────────────────────────────────────┘
```

**Features:**
- Block types: source, note, query, summary, decision, task, citation
- Auto-citation from RAG chunks
- Export to doc_page, spec_bundle, runbook
- Collaborative editing (optional)

### 3. Search (Hybrid BM25 + Vector)

Two-pronged retrieval:

```
Query: "expense policy approval workflow"
       ↓
┌──────────────────────────────────────────────┐
│ BM25 (tsvector)              Vector (pgvector)
│ rank by keyword match        rank by semantic
│         ↓                           ↓
│    results A                   results B
│         └──────────┬────────────┘
│                    ↓
│          Hybrid Fusion (RRF)
│          0.55 * cosine + 0.45 * bm25
│                    ↓
│          Top-K results + snippets
└──────────────────────────────────────────────┘
```

**Features:**
- Faceted filtering (space, type, version, author)
- Snippet highlighting
- Related topics (link graph)
- Query analytics for gap detection

### 4. Citations + Provenance

Every AI output traces to sources:

```
Generated Answer:
"Expense reports over $500 require manager approval
 per policy [1]. Three-way matching is mandatory
 for all PO-based invoices [2]."

Citations:
[1] expense_policy.md:L42-48 (chunk_id: abc123)
[2] procurement_sop.md:L15-22 (chunk_id: def456)
```

**Features:**
- Click-to-source navigation
- Citation confidence scores
- Provenance audit trail
- Orphan detection (uncited claims)

### 5. Learning Journeys

Guided paths through documentation:

```yaml
journey: "Odoo Developer Onboarding"
steps:
  - artifact: getting-started
    prereq: null
  - artifact: first-module-tutorial
    prereq: step[0]
  - artifact: orm-reference
    prereq: step[1]
  - artifact: views-and-forms
    prereq: step[2]
completion_badge: "odoo-dev-fundamentals"
```

**Features:**
- Ordered step progression
- Prerequisite enforcement
- Progress tracking
- Completion badges

### 6. Glossary

Canonical definitions with hover cards:

```
Term: ORM
Definition: Object-Relational Mapping layer that provides
            database abstraction in Odoo
Synonyms: Object-Relational Mapper, Model layer
See also: Model, Field, Recordset
Authoritative doc: /dev/orm-reference
```

**Features:**
- Auto-link terms in pages
- Hover card previews
- Synonym handling
- Cross-product disambiguation

## Technical Requirements

### Database Schema

See migrations for complete schema:
- `kb.spaces` - Workspace containers
- `kb.artifacts` - Canonical records
- `kb.versions` - Immutable snapshots
- `kb.blocks` - Notebook blocks
- `kb.citations` - Source linkage
- `rag.chunks` - Content segments
- `rag.embeddings` - Vectors

### API Endpoints

```yaml
/v1/kb/spaces:
  GET: List spaces (with permission filter)
  POST: Create space

/v1/kb/artifacts:
  GET: List artifacts (with facets)
  POST: Create artifact

/v1/kb/artifacts/{id}:
  GET: Get artifact with latest version
  PUT: Update (creates new version)

/v1/kb/artifacts/{id}/versions:
  GET: List versions
  GET /{version}: Get specific version

/v1/kb/notebooks/{id}/blocks:
  GET: List blocks
  POST: Add block
  PUT /{block_id}: Update block
  DELETE /{block_id}: Remove block

/v1/kb/notebooks/{id}/export:
  POST: Export to artifact type

/v1/search:
  POST: Hybrid search with facets

/v1/glossary:
  GET: Term lookup
```

### RLS Policies

All tables enforce:
```sql
tenant_id = (auth.jwt()->>'tenant_id')::uuid
```

Visibility rules:
- `public`: All authenticated users
- `workspace`: Members of artifact's workspace
- `private`: Owner only

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Search latency p95 | <500ms | Query analytics |
| Citation coverage | >95% AI outputs | kb.citations audit |
| Version adoption | 100% edits versioned | kb.versions count |
| Journey completion | >30% started | Progress tracking |
| Glossary hover rate | >20% page views | UI analytics |

## Out of Scope (v1)

- Real-time collaborative editing (v2)
- Translation/localization (v2)
- Offline sync (v2)
- Custom workflows (v2)
- External sharing (v2)
