# Constitution: SAP-Grade Documentation Platform

## Purpose

This feature transforms the RAG-enabled documentation system into a SAP-grade documentation platform with structured taxonomy, learning journeys, glossary integration, and faceted search—matching the discoverability and organization standards of enterprise documentation portals.

## Invariant Rules

### 1. Taxonomy Integrity
- Every document MUST be assigned to at least one taxonomy node
- Taxonomy nodes form a strict DAG (directed acyclic graph)—no circular references
- Root nodes represent product areas; leaves represent specific topics
- Orphan documents (no taxonomy) are flagged in `docs.doc_metadata.orphan_flag`

### 2. Version Lineage
- Documents follow semantic versioning with release channels: `edge`, `stable`, `lts`
- Breaking changes require `is_breaking = true` annotation
- Deprecated content requires `is_deprecated = true` with `successor_id` pointing to replacement
- Version lineage is immutable—new versions create new rows, never mutate history

### 3. Learning Journey Coherence
- Learning journeys are ordered sequences of documents
- Each step has prerequisites defined in `prerequisite_step_id`
- Journeys cannot reference deprecated documents without explicit override
- Journey completion tracking uses `runtime.user_journey_progress` (not in docs schema)

### 4. Related Documents Graph
- `docs.related_docs` defines weighted edges between documents
- Relationship types: `prerequisite`, `see_also`, `supersedes`, `example_of`, `contradicts`
- Bi-directional relationships require explicit reverse entries
- Contradiction relationships trigger editorial review queue

### 5. Glossary Authority
- Glossary terms are canonical—one definition per term per product context
- Terms link to authoritative document sections via `anchor_id`
- Acronym expansion is required for all glossary entries
- Cross-product term disambiguation uses `product_context` field

### 6. Search Quality Guarantees
- Faceted search must return results in <500ms for 95th percentile
- Full-text search uses hybrid retrieval (BM25 + vector similarity)
- Taxonomy facets are pre-computed, not runtime-calculated
- Zero-result queries log to `runtime.search_telemetry` for gap analysis

## Role Separation

| Role | Responsibilities | Prohibited Actions |
|------|------------------|--------------------|
| Content Author | Create/edit documents, assign taxonomy | Modify taxonomy structure, approve journeys |
| Taxonomy Editor | Manage taxonomy nodes, approve mappings | Delete documents, modify content |
| Journey Curator | Create learning paths, set prerequisites | Modify document content |
| Platform Admin | Schema changes, bulk operations | Direct content editing |

## Data Boundaries

- `docs.*` schema: Taxonomy, metadata, relationships, journeys (PostgreSQL)
- `rag.*` schema: Chunks, embeddings, search indices (PostgreSQL + pgvector)
- `gold.*` schema: Aggregated metrics, capability maps (analytics)
- `runtime.*` schema: User progress, telemetry, session state (ephemeral)

## Integration Contracts

### Ingest Pipeline
```
Bronze (raw HTML/MD) → Silver (normalized, chunked) → Gold (embedded, indexed)
```
- Bronze: Raw content with source metadata
- Silver: Cleaned markdown, chunked at semantic boundaries
- Gold: Vector embeddings + taxonomy assignments + glossary links

### API Surface
- `GET /v1/docs/browse` - Taxonomy tree navigation
- `GET /v1/docs/search` - Faceted hybrid search
- `GET /v1/docs/journey/{id}` - Learning journey with progress
- `GET /v1/docs/glossary` - Term lookup with context

## Failure Modes

| Condition | Behavior | Recovery |
|-----------|----------|----------|
| Taxonomy node deleted with children | Block deletion, require reassignment | Admin override with orphan flag |
| Document version conflict | Last-write-wins with conflict log | Editorial review queue |
| Embedding generation fails | Document searchable by BM25 only | Retry queue with backoff |
| Glossary term collision | Reject insert, require disambiguation | Manual resolution |

## Audit Requirements

- All taxonomy changes logged to `docs.taxonomy_audit`
- Document metadata changes tracked with `updated_at` + `updated_by`
- Journey modifications require approval workflow (via ticketing)
- Bulk operations require pre-approval and post-verification report
