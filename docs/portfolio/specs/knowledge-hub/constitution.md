# Constitution: Knowledge Hub

## Purpose

Knowledge Hub is a unified platform combining:
1. **Human-first docs/wiki** - Browseable, versioned, permissioned documentation
2. **Machine-first knowledge graph** - Chunked, embedded, cited, auditable RAG primitives

It bridges Confluence-style wiki authoring with NotebookLM-style artifact creation, producing both human-readable docs and machine-queryable knowledge.

## Invariant Rules

### 1. Single Source of Truth

| Layer | Authority | Storage |
|-------|-----------|---------|
| Governance | Supabase Postgres + RLS | `kb.*`, `rag.*` schemas |
| Content | Git + Object Storage + Odoo | Markdown, S3/MinIO, ir.attachment |
| Citations | Supabase | `kb.citations` → `rag.chunks` |

**Rule:** Every artifact has exactly one canonical source. No dual-master scenarios.

### 2. Tenant Isolation (Non-Negotiable)

- Every table has `tenant_id` column
- RLS policies enforce `tenant_id = auth.jwt()->>'tenant_id'`
- RAG tables (`rag.chunks`, `rag.embeddings`) inherit artifact permissions
- Cross-tenant queries are impossible at database level

### 3. Version Immutability

- `kb.versions` rows are append-only
- Edits create new versions, never mutate existing
- Each version has unique `content_hash`
- Versions are addressable: `{artifact_id}@{version}`

### 4. Citation Lineage

- Every AI-generated output MUST link to source chunks via `kb.citations`
- Citations include: chunk_id, quote, relevance_score
- Orphan outputs (no citations) are flagged and quarantined
- Citation graph is queryable for provenance audits

### 5. Artifact Type Discipline

Only these artifact types are allowed:

| Type | Description | Authoring Source |
|------|-------------|------------------|
| `doc_page` | Wiki page | Editor / Git |
| `spec_bundle` | 4-file spec kit | Git repo |
| `runbook` | Operations playbook | Editor / template |
| `notebook` | Block container | Notebook UI |
| `notebook_block` | Atomic content | Notebook UI |
| `dataset_contract` | Delta/Supabase schema | Git YAML |
| `api_spec` | OpenAPI/RPC contract | Git YAML |
| `evidence_pack` | Curated sources + queries | Notebook export |
| `agent_output` | Generated artifact | AI pipeline |
| `journey` | Learning path | Editor |
| `glossary_term` | Definition + synonyms | Editor |

### 6. Block Types (Notebook)

| Type | Purpose | Promotable To |
|------|---------|---------------|
| `source` | Attached doc/URL/Odoo ref | - |
| `note` | Free text content | doc_page |
| `query` | SQL + result pointer | evidence_pack |
| `summary` | Generated synthesis | doc_page |
| `decision` | ADR-style record | runbook |
| `task` | Spec-kit task candidate | spec_bundle |
| `citation` | Chunk references | - |
| `export` | Render target | any artifact |

## Data Boundaries

### kb.* Schema (Knowledge Base)

- `kb.spaces` - Workspace containers
- `kb.artifacts` - Canonical artifact records
- `kb.versions` - Immutable version snapshots
- `kb.blocks` - Notebook blocks
- `kb.citations` - Output → source mappings
- `kb.glossary_terms` - Definitions + synonyms
- `kb.journeys` - Learning paths
- `kb.journey_steps` - Path steps

### rag.* Schema (Retrieval)

- `rag.chunks` - Tokenized content segments
- `rag.embeddings` - Vector representations
- `rag.search_logs` - Query analytics

### Boundary Rules

- Write ops: kb.* only (rag.* populated by pipeline)
- Read ops: Both (API combines human + machine views)
- Citations: kb.citations → rag.chunks (immutable link)

## Integration Contracts

### Ingestion Sources

| Source | Artifact Type | Canonical Ref Pattern |
|--------|---------------|----------------------|
| Git spec/ | spec_bundle | `git://{repo}/{path}@{sha}` |
| Git docs/ | doc_page | `git://{repo}/{path}@{sha}` |
| Odoo attachment | source | `odoo://ir.attachment/{id}` |
| Odoo knowledge | doc_page | `odoo://knowledge.article/{id}` |
| Web crawl | doc_page | `https://{url}` |

### Export Targets

| From | To | Output |
|------|-----|--------|
| Notebook | doc_page | Markdown file + kb.artifacts row |
| Notebook | spec_bundle | 4 markdown files in spec/{slug}/ |
| Notebook | runbook | Templated operations doc |
| Notebook | evidence_pack | Curated sources + citations |

## Failure Modes

| Condition | Behavior | Recovery |
|-----------|----------|----------|
| Missing citations on agent_output | Block publish, flag for review | Manual source linking |
| Tenant mismatch in citation | Reject operation | - |
| Duplicate content_hash | Deduplicate, point to existing | - |
| Orphan chunks (no artifact) | Quarantine, scheduled cleanup | - |
| Embedding model change | Version in rag.embeddings.model | Re-embed with new model |

## Audit Requirements

- All artifact mutations logged with `created_by`, `created_at`
- Version history preserved indefinitely
- Citation graph immutable (append-only)
- Search queries logged to `rag.search_logs` for gap analysis
- Export operations tracked in `kb.export_log`
