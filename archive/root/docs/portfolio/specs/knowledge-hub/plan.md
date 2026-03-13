# Implementation Plan: Knowledge Hub

## Phase 1: Foundation (Schema + Core API)

### 1.1 Database Schema

**Migration files:**
- `20251220_004_kb_core.sql` - Spaces, artifacts, versions
- `20251220_005_kb_blocks.sql` - Notebook blocks, citations
- `20251220_006_kb_discovery.sql` - Glossary, journeys, search logs

**Tables:**
```
kb.spaces
kb.artifacts
kb.versions
kb.blocks
kb.citations
kb.glossary_terms
kb.journeys
kb.journey_steps
rag.search_logs
```

**Indexes:**
- GIN on `kb.artifacts.tags` for tag filtering
- GIN on `kb.versions.content_tsvector` for full-text
- HNSW on `rag.embeddings.v` for vector search
- Composite on `(tenant_id, space_id, status)` for listings

**RLS Policies:**
- All tables: `tenant_id = auth.jwt()->>'tenant_id'`
- Visibility-based access for `kb.artifacts`
- Inherited permissions for `kb.versions`, `kb.blocks`

### 1.2 Edge Functions

**Functions to create:**
- `kb-artifacts-crud` - CRUD operations with versioning
- `kb-search-hybrid` - Combined BM25 + vector search
- `kb-notebook-export` - Export notebook to artifact
- `kb-citations-resolve` - Resolve citation chunks

**Each function:**
- Validates tenant context
- Enforces RLS
- Returns standardized response format

### 1.3 Ingestion Pipeline Integration

**n8n workflows:**
- `kb_bronze_ingest` - Raw content capture
- `kb_silver_normalize` - Markdown + metadata extraction
- `kb_gold_chunk_embed` - Chunking + embedding
- `kb_gold_link_graph` - Related docs computation

**Integration points:**
- Git webhook → spec bundle ingestion
- Odoo attachment sync → source ingestion
- Web crawler → doc_page creation

## Phase 2: Wiki Experience

### 2.1 Space Management UI

**Components:**
- Space tree navigation (sidebar)
- Space settings modal (permissions, visibility)
- Space create/edit forms

**API endpoints:**
```
GET    /v1/kb/spaces
POST   /v1/kb/spaces
GET    /v1/kb/spaces/{id}
PUT    /v1/kb/spaces/{id}
DELETE /v1/kb/spaces/{id}
GET    /v1/kb/spaces/{id}/artifacts
```

### 2.2 Page Viewer

**Components:**
- Markdown renderer with syntax highlighting
- Version history panel
- Related topics sidebar
- Citation hover cards
- Breadcrumb navigation

**Features:**
- Version diff view
- Print/export to PDF
- Copy link to section
- Edit button (opens editor)

### 2.3 Page Editor

**Components:**
- Rich text editor (ProseMirror or TipTap)
- Markdown source toggle
- Image/file upload
- Link insertion with autocomplete
- Version save with message

**Features:**
- Auto-save drafts
- Conflict detection
- Preview mode
- Publish workflow (draft → review → published)

## Phase 3: Notebook Experience

### 3.1 Notebook Editor

**Block components:**
- `SourceBlock` - File/URL attachment
- `NoteBlock` - Rich text editor
- `QueryBlock` - SQL editor + result table
- `SummaryBlock` - AI-generated with citations
- `DecisionBlock` - ADR template
- `TaskBlock` - Spec-kit task format
- `CitationBlock` - Chunk reference card

**Interactions:**
- Drag-drop reordering
- Block type conversion
- Block duplication
- Block deletion with confirmation

### 3.2 Source Attachment

**File upload:**
- Drag-drop zone
- Progress indicator
- Thumbnail preview
- Metadata extraction

**URL attachment:**
- URL input with validation
- Automatic title/description fetch
- Screenshot preview (optional)

**Odoo reference:**
- Attachment picker modal
- Knowledge article selector
- Record reference input

### 3.3 Export Workflow

**Export modal:**
- Target type selector (doc_page, spec_bundle, runbook)
- Title/slug input
- Space selector
- Citation review panel
- Preview before export

**Export process:**
1. Validate all blocks
2. Render to target format
3. Create kb.artifacts + kb.versions
4. Write kb.citations for all chunks
5. Optionally commit to Git (spec_bundle)

## Phase 4: Search + Discovery

### 4.1 Hybrid Search

**Search function:**
```sql
CREATE FUNCTION kb.hybrid_search(
  query TEXT,
  filters JSONB,
  limit_val INT DEFAULT 20
) RETURNS TABLE(...)
```

**Ranking:**
- BM25 score from tsvector
- Cosine similarity from pgvector
- Reciprocal Rank Fusion: `1/(k + rank_bm25) + 1/(k + rank_vec)`

### 4.2 Faceted Search UI

**Facet panels:**
- Space filter (tree)
- Type filter (checkboxes)
- Status filter (published, draft, deprecated)
- Version filter (current, all)
- Date range filter

**Results display:**
- Title + snippet with highlights
- Type badge
- Space breadcrumb
- Last updated
- Relevance score (optional)

### 4.3 Related Topics

**Computation:**
- Link graph edges (explicit links in content)
- Embedding similarity (top-k nearest chunks)
- Co-citation (chunks cited together)

**Display:**
- Sidebar panel on page view
- Weighted by relationship type

### 4.4 Glossary Integration

**Term detection:**
- Scan rendered content for glossary terms
- Wrap matches with hover trigger
- Exclude code blocks and URLs

**Hover card:**
- Term + definition
- Synonyms
- "See also" links
- "Go to authoritative doc" button

## Phase 5: Journeys + Progress

### 5.1 Journey Builder

**Components:**
- Journey metadata form (title, description, badge)
- Step list editor (drag-drop)
- Artifact picker for each step
- Prerequisite configuration

### 5.2 Journey Viewer

**Components:**
- Progress bar
- Step list with status (locked, available, complete)
- Current step highlight
- Estimated time remaining
- Completion certificate (on finish)

### 5.3 Progress Tracking

**Storage:**
- `runtime.user_journey_progress` table
- Track: started_at, completed_at per step
- Compute: overall completion percentage

## Dependency Graph

```
Phase 1.1 (Schema) ──┬──> Phase 1.2 (Edge Functions)
                     ├──> Phase 1.3 (Pipeline)
                     ├──> Phase 2.* (Wiki)
                     └──> Phase 3.* (Notebook)

Phase 1.2 (Edge Functions) ──> Phase 4.1 (Search)

Phase 2.* (Wiki) ──> Phase 4.2 (Faceted Search)
                 ──> Phase 4.3 (Related Topics)

Phase 3.* (Notebook) ──> Phase 3.3 (Export)

Phase 4.4 (Glossary) ──> Phase 5.* (Journeys)
```

## Rollout Strategy

### Stage 1: Internal Alpha
- Schema + API deployed
- Basic wiki viewer (read-only)
- Search with manual indexing

### Stage 2: Internal Beta
- Page editor enabled
- Notebook editor enabled
- Automatic ingestion pipeline

### Stage 3: GA
- Export workflow
- Journeys + progress
- Full glossary integration
- Performance optimization

## Technical Stack

| Layer | Technology |
|-------|------------|
| Database | Supabase PostgreSQL + pgvector |
| Backend | Supabase Edge Functions (Deno) |
| Pipeline | n8n + Spark + Delta Lake |
| Storage | MinIO (S3-compatible) |
| Frontend | React + TipTap/ProseMirror |
| Search | PostgreSQL FTS + pgvector |
