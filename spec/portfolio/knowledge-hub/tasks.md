# Tasks: Knowledge Hub

## Phase 1: Foundation

### 1.1 Database Schema

- [ ] Create migration `20251220_004_kb_core.sql`
  - [ ] Create `kb` schema
  - [ ] Create `kb.spaces` table with RLS
  - [ ] Create `kb.artifacts` table with type enum
  - [ ] Create `kb.versions` table (immutable)
  - [ ] Add GIN index on `artifacts.tags`
  - [ ] Add tsvector column + index on `versions`
  - [ ] Add RLS policies for tenant isolation
  - [ ] Test migration rollback

- [ ] Create migration `20251220_005_kb_blocks.sql`
  - [ ] Create `kb.blocks` table with block_type enum
  - [ ] Create `kb.citations` table
  - [ ] Add foreign keys to rag.chunks
  - [ ] Add ordering index on blocks
  - [ ] Add RLS policies
  - [ ] Test citation integrity

- [ ] Create migration `20251220_006_kb_discovery.sql`
  - [ ] Create `kb.glossary_terms` table
  - [ ] Create `kb.journeys` table
  - [ ] Create `kb.journey_steps` table
  - [ ] Create `rag.search_logs` table
  - [ ] Add indexes for lookup
  - [ ] Add RLS policies
  - [ ] Seed sample glossary terms

### 1.2 Edge Functions

- [ ] Create `kb-artifacts-crud` function
  - [ ] GET /artifacts - list with filters
  - [ ] POST /artifacts - create new
  - [ ] GET /artifacts/:id - get with latest version
  - [ ] PUT /artifacts/:id - update (new version)
  - [ ] DELETE /artifacts/:id - soft delete
  - [ ] Add tenant validation
  - [ ] Add permission checks
  - [ ] Write unit tests

- [ ] Create `kb-search-hybrid` function
  - [ ] Parse search query
  - [ ] Execute BM25 query
  - [ ] Execute vector query
  - [ ] Merge with RRF
  - [ ] Apply facet filters
  - [ ] Return results + facet counts
  - [ ] Log to search_logs
  - [ ] Write unit tests

- [ ] Create `kb-notebook-export` function
  - [ ] Validate notebook blocks
  - [ ] Render to target format
  - [ ] Create artifact + version
  - [ ] Write citations
  - [ ] Git commit (for spec_bundle)
  - [ ] Return new artifact
  - [ ] Write unit tests

- [ ] Create `kb-citations-resolve` function
  - [ ] Accept chunk_id list
  - [ ] Fetch chunk content
  - [ ] Return with metadata
  - [ ] Add caching

### 1.3 Pipeline Integration

- [ ] Create n8n workflow `kb_bronze_ingest`
  - [ ] Git webhook trigger
  - [ ] Fetch changed files
  - [ ] Write to bronze.raw_pages
  - [ ] Trigger silver pipeline

- [ ] Create n8n workflow `kb_silver_normalize`
  - [ ] Read bronze rows
  - [ ] Convert HTML/MD to clean markdown
  - [ ] Extract metadata (title, version, etc.)
  - [ ] Write to silver.normalized_docs

- [ ] Create n8n workflow `kb_gold_chunk_embed`
  - [ ] Read silver rows
  - [ ] Chunk with semantic boundaries
  - [ ] Generate embeddings
  - [ ] Write to gold.chunks + gold.embeddings

- [ ] Create n8n workflow `kb_gold_link_graph`
  - [ ] Extract explicit links
  - [ ] Compute embedding similarity
  - [ ] Write to kb.related_docs

- [ ] Update mirror script for kb tables
  - [ ] Mirror kb.artifacts to search index
  - [ ] Mirror kb.versions for versioned search

## Phase 2: Wiki Experience

### 2.1 Space Management

- [ ] Create space list view component
- [ ] Create space tree navigation component
- [ ] Create space settings modal
- [ ] Implement space CRUD API calls
- [ ] Add permission inheritance logic
- [ ] Write integration tests

### 2.2 Page Viewer

- [ ] Create markdown renderer component
  - [ ] Syntax highlighting
  - [ ] Image handling
  - [ ] Link resolution
  - [ ] Code block copy button

- [ ] Create version history panel
  - [ ] Version list with dates
  - [ ] Diff viewer
  - [ ] Restore button

- [ ] Create related topics sidebar
  - [ ] Fetch from link graph
  - [ ] Display with relevance

- [ ] Create citation hover cards
  - [ ] Detect citation markers
  - [ ] Show source preview
  - [ ] Link to source

- [ ] Create breadcrumb navigation
  - [ ] Space > Parent > Current
  - [ ] Clickable links

### 2.3 Page Editor

- [ ] Set up TipTap/ProseMirror editor
- [ ] Add markdown source toggle
- [ ] Implement image upload
- [ ] Add link autocomplete
- [ ] Implement version save
- [ ] Add auto-save drafts
- [ ] Add conflict detection
- [ ] Add preview mode
- [ ] Implement publish workflow

## Phase 3: Notebook Experience

### 3.1 Notebook Editor

- [ ] Create notebook container component
- [ ] Create block wrapper component
- [ ] Implement drag-drop reordering

- [ ] Create SourceBlock component
  - [ ] File upload zone
  - [ ] URL input
  - [ ] Odoo picker
  - [ ] Thumbnail preview

- [ ] Create NoteBlock component
  - [ ] Rich text editor
  - [ ] Markdown toggle

- [ ] Create QueryBlock component
  - [ ] SQL editor
  - [ ] Execute button
  - [ ] Result table

- [ ] Create SummaryBlock component
  - [ ] Generate button
  - [ ] Citation display
  - [ ] Edit capability

- [ ] Create DecisionBlock component
  - [ ] ADR template fields
  - [ ] Status selector

- [ ] Create TaskBlock component
  - [ ] Task format input
  - [ ] Status checkbox

- [ ] Create CitationBlock component
  - [ ] Chunk selector
  - [ ] Quote display
  - [ ] Source link

### 3.2 Source Attachment

- [ ] Implement file upload to S3
- [ ] Add progress indicator
- [ ] Extract file metadata
- [ ] Generate thumbnails

- [ ] Implement URL attachment
  - [ ] URL validation
  - [ ] Title fetch
  - [ ] Preview generation

- [ ] Implement Odoo picker
  - [ ] Attachment list
  - [ ] Knowledge article list
  - [ ] Search within picker

### 3.3 Export Workflow

- [ ] Create export modal component
- [ ] Add target type selector
- [ ] Add title/slug input
- [ ] Add space selector
- [ ] Create citation review panel
- [ ] Add preview pane

- [ ] Implement doc_page export
  - [ ] Render blocks to markdown
  - [ ] Create artifact + version
  - [ ] Write citations

- [ ] Implement spec_bundle export
  - [ ] Generate 4 files
  - [ ] Git commit
  - [ ] Create artifact

- [ ] Implement runbook export
  - [ ] Apply template
  - [ ] Create artifact

## Phase 4: Search + Discovery

### 4.1 Hybrid Search

- [ ] Create hybrid_search SQL function
- [ ] Add BM25 scoring
- [ ] Add vector scoring
- [ ] Implement RRF fusion
- [ ] Add query logging
- [ ] Benchmark performance

### 4.2 Faceted Search UI

- [ ] Create search input component
- [ ] Create facet panel component
  - [ ] Space tree filter
  - [ ] Type checkboxes
  - [ ] Status filter
  - [ ] Date range

- [ ] Create results list component
  - [ ] Title + snippet
  - [ ] Type badge
  - [ ] Breadcrumb
  - [ ] Score indicator

- [ ] Add result pagination
- [ ] Add result sorting

### 4.3 Related Topics

- [ ] Create related topics component
- [ ] Fetch from link graph API
- [ ] Display with relationship type
- [ ] Add loading state

### 4.4 Glossary Integration

- [ ] Create glossary lookup API
- [ ] Create term detection utility
- [ ] Create hover card component
- [ ] Integrate with page viewer
- [ ] Add to notebook viewer

## Phase 5: Journeys + Progress

### 5.1 Journey Builder

- [ ] Create journey form component
- [ ] Create step list editor
- [ ] Add artifact picker
- [ ] Add prerequisite configuration
- [ ] Implement save/publish

### 5.2 Journey Viewer

- [ ] Create progress bar component
- [ ] Create step list component
- [ ] Show lock/available/complete states
- [ ] Highlight current step
- [ ] Show estimated time

### 5.3 Progress Tracking

- [ ] Create progress API endpoints
- [ ] Implement step completion
- [ ] Calculate overall progress
- [ ] Add completion certificate

## Validation Checklist

### Schema
- [ ] All tables have tenant_id
- [ ] All tables have RLS policies
- [ ] All indexes created
- [ ] Migration tested (up + down)

### API
- [ ] All endpoints documented
- [ ] All endpoints have auth
- [ ] Error handling complete
- [ ] Response times <500ms p95

### Pipeline
- [ ] Git ingestion working
- [ ] Odoo sync working
- [ ] Chunking deterministic
- [ ] Embeddings consistent

### UI
- [ ] Responsive design
- [ ] Keyboard navigation
- [ ] Loading states
- [ ] Error states
- [ ] Empty states

### Security
- [ ] No cross-tenant access
- [ ] Citation integrity
- [ ] Input sanitization
- [ ] Rate limiting
