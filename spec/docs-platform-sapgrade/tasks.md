# Tasks: SAP-Grade Documentation Platform

## Phase 1: Schema Foundation

### 1.1 Create docs.taxonomy_nodes and doc_taxonomy tables
- [ ] Create migration file `20251220_001_docs_taxonomy.sql`
- [ ] Define `docs.taxonomy_nodes` with LTREE path support
- [ ] Define `docs.doc_metadata` with product/version/deprecation fields
- [ ] Define `docs.doc_taxonomy` junction table
- [ ] Define `docs.related_docs` graph table
- [ ] Add GIN indexes for LTREE and array columns
- [ ] Add trigger to maintain taxonomy_nodes.depth
- [ ] Test migration with rollback

### 1.2 Create docs.glossary table
- [ ] Add `docs.glossary` table with term/product_context PK
- [ ] Add unique constraint on (term, product_context)
- [ ] Add foreign key to rag.documents for authoritative source
- [ ] Create index for prefix search on term

### 1.3 Create docs.learning_journeys tables
- [ ] Create migration file `20251220_003_docs_journeys.sql`
- [ ] Define `docs.learning_journeys` with slug/title/description
- [ ] Define `docs.learning_journey_steps` with ordering
- [ ] Add self-referential FK for prerequisite steps
- [ ] Add CHECK constraint for valid step ordering

### 1.4 Extend rag.document_versions
- [ ] Create migration file `20251220_002_docs_versioning.sql`
- [ ] Add `release_channel` enum column
- [ ] Add `is_breaking` boolean column
- [ ] Add `is_deprecated` boolean column
- [ ] Add `successor_id` self-referential FK
- [ ] Backfill existing rows with defaults

### 1.5 Create audit tables
- [ ] Define `docs.taxonomy_audit` for change tracking
- [ ] Add trigger on taxonomy_nodes for INSERT/UPDATE/DELETE
- [ ] Include old_value, new_value, changed_by, changed_at

### 1.6 Seed initial taxonomy structure
- [ ] Create seed file `seed_taxonomy.sql`
- [ ] Define root nodes: odoo-ce, oca, platform, integrations
- [ ] Define L2 nodes for major product areas
- [ ] Define L3 nodes for specific topics
- [ ] Insert with LTREE path computation

## Phase 2: API Layer

### 2.1 Implement browse endpoint
- [ ] Create `backend/app/api/v1/docs/browse.py`
- [ ] Implement recursive CTE for tree traversal
- [ ] Add document count aggregation
- [ ] Support optional root node parameter
- [ ] Support depth limit parameter
- [ ] Add response caching (5 min TTL)
- [ ] Write unit tests

### 2.2 Implement faceted search endpoint
- [ ] Create `backend/app/api/v1/docs/search.py`
- [ ] Parse filter syntax from query params
- [ ] Build hybrid BM25 + vector query
- [ ] Compute facet counts with GROUP BY
- [ ] Return hits with highlighted snippets
- [ ] Add pagination support
- [ ] Write unit tests

### 2.3 Implement journey endpoint
- [ ] Create `backend/app/api/v1/docs/journey.py`
- [ ] Fetch journey by slug with steps
- [ ] Join with document titles/summaries
- [ ] Compute user progress (if auth present)
- [ ] Mark step status: completed/current/locked
- [ ] Write unit tests

### 2.4 Implement glossary endpoint
- [ ] Create `backend/app/api/v1/docs/glossary.py`
- [ ] Implement prefix search on term
- [ ] Filter by product context
- [ ] Return definitions with doc links
- [ ] Add caching for common terms
- [ ] Write unit tests

### 2.5 Update API router
- [ ] Register new endpoints in docs router
- [ ] Add OpenAPI documentation
- [ ] Add request/response models (Pydantic)

## Phase 3: Pipeline Enhancement

### 3.1 Create taxonomy assignment pipeline
- [ ] Create n8n workflow `docs_gold_taxonomy_assign`
- [ ] Add node: Fetch unassigned documents
- [ ] Add node: Extract topic signals (keywords, headers)
- [ ] Add node: Match against taxonomy descriptions
- [ ] Add node: Write primary taxonomy assignment
- [ ] Add node: Write secondary taxonomy assignments
- [ ] Add error handling and retry logic
- [ ] Test with sample documents

### 3.2 Create glossary extraction pipeline
- [ ] Create n8n workflow `docs_gold_glossary_extract`
- [ ] Add node: Scan for definition patterns
- [ ] Add node: Extract term/definition pairs
- [ ] Add node: Detect acronyms
- [ ] Add node: Deduplicate against existing
- [ ] Add node: Insert new terms
- [ ] Add node: Flag conflicts for review
- [ ] Test with sample documents

### 3.3 Create related docs pipeline
- [ ] Create n8n workflow `docs_gold_related_build`
- [ ] Add node: Compute embedding similarity matrix
- [ ] Add node: Extract explicit links
- [ ] Add node: Detect version supersession
- [ ] Add node: Build weighted edges
- [ ] Add node: Write to related_docs table
- [ ] Test with sample document set

### 3.4 Update bronze ingest pipeline
- [ ] Add version detection from URL/metadata
- [ ] Add product detection from source
- [ ] Pass signals to silver pipeline

### 3.5 Update silver normalize pipeline
- [ ] Extract glossary candidate terms
- [ ] Preserve heading hierarchy for taxonomy hints
- [ ] Pass enriched metadata to gold pipeline

## Phase 4: Continue Integration

### 4.1 Update /docs slash command
- [ ] Parse facet filter syntax: `product:X type:Y`
- [ ] Pass filters to search API
- [ ] Display facet counts in response
- [ ] Add help text for filter syntax

### 4.2 Add /docs browse command
- [ ] Create new slash command handler
- [ ] Display taxonomy tree with doc counts
- [ ] Support navigation by node slug
- [ ] Add keyboard navigation hints

### 4.3 Add /docs journey command
- [ ] Create new slash command handler
- [ ] List available journeys
- [ ] Display journey steps with status
- [ ] Show estimated time remaining
- [ ] Link to current step document

### 4.4 Create taxonomy context provider
- [ ] Create `.continue/context/taxonomy.ts`
- [ ] Fetch taxonomy tree from API
- [ ] Format as markdown tree
- [ ] Cache for session duration

### 4.5 Create journey context provider
- [ ] Create `.continue/context/journey.ts`
- [ ] Fetch active journey from API
- [ ] Include current step context
- [ ] Include next step preview

## Phase 5: Observability

### 5.1 Create search telemetry table
- [ ] Add `runtime.search_telemetry` table
- [ ] Add columns: query, filters, result_count, click_position
- [ ] Add session_id for grouping
- [ ] Add retention policy (90 days)

### 5.2 Create journey progress table
- [ ] Add `runtime.user_journey_progress` table
- [ ] Add columns: user_id, journey_id, step_order, completed_at
- [ ] Add indexes for user lookup
- [ ] Add API endpoints for progress updates

### 5.3 Add zero-result analysis
- [ ] Create scheduled job for weekly aggregation
- [ ] Group zero-result queries by similarity
- [ ] Output content gap report
- [ ] Create ticketing integration for gaps

### 5.4 Add browse analytics
- [ ] Track taxonomy node visits
- [ ] Track drill-down patterns
- [ ] Compute popular paths

### 5.5 Create monitoring dashboard
- [ ] Define Prometheus metrics
- [ ] Create Grafana dashboard
- [ ] Add alerts for search latency
- [ ] Add alerts for pipeline failures

## Validation Checklist

### Schema
- [ ] All tables created successfully
- [ ] All indexes present and used
- [ ] RLS policies applied where needed
- [ ] Audit triggers functioning

### API
- [ ] All endpoints return valid responses
- [ ] Error handling covers edge cases
- [ ] Response times within SLA (<500ms p95)
- [ ] Pagination works correctly

### Pipelines
- [ ] All documents have taxonomy assignments
- [ ] Glossary extraction produces valid terms
- [ ] Related docs graph is connected
- [ ] No orphan documents remain

### Integration
- [ ] Continue commands work end-to-end
- [ ] Context providers return valid data
- [ ] Filters apply correctly
- [ ] Progress tracking updates

### Observability
- [ ] Telemetry events recorded
- [ ] Metrics exposed to Prometheus
- [ ] Dashboard shows meaningful data
- [ ] Alerts fire correctly
