# Implementation Plan: SAP-Grade Documentation Platform

## Phase 1: Schema Foundation

### 1.1 Create docs.* Schema Tables

**Files to create:**
- `supabase/migrations/20251220_001_docs_taxonomy.sql`
- `supabase/migrations/20251220_002_docs_versioning.sql`
- `supabase/migrations/20251220_003_docs_journeys.sql`

**Tables:**
```
docs.taxonomy_nodes     - Hierarchical topic tree with LTREE paths
docs.doc_metadata       - Product, version, deprecation flags
docs.doc_taxonomy       - Document-to-taxonomy mapping (M:N)
docs.related_docs       - Weighted relationship graph
docs.learning_journeys  - Journey definitions
docs.learning_journey_steps - Ordered steps with prerequisites
docs.glossary           - Term definitions with product context
docs.taxonomy_audit     - Change log for taxonomy modifications
```

**Indexes:**
- GIN index on `taxonomy_nodes.path` for LTREE queries
- GIN index on `doc_metadata.glossary_terms` for term search
- Composite index on `doc_taxonomy(taxonomy_id, doc_id)` for browse queries
- Partial index on `doc_metadata.is_deprecated = false` for current docs

### 1.2 Add Version Lineage to rag.document_versions

**Alterations:**
```sql
ALTER TABLE rag.document_versions ADD COLUMN release_channel TEXT DEFAULT 'stable';
ALTER TABLE rag.document_versions ADD COLUMN is_breaking BOOLEAN DEFAULT false;
ALTER TABLE rag.document_versions ADD COLUMN is_deprecated BOOLEAN DEFAULT false;
ALTER TABLE rag.document_versions ADD COLUMN successor_id UUID REFERENCES rag.document_versions(id);
```

### 1.3 Seed Initial Taxonomy

**Root nodes:**
- `odoo-ce` - Core Odoo CE documentation
- `oca` - OCA addon documentation
- `platform` - Platform/infrastructure docs
- `integrations` - Third-party integrations

**Sample hierarchy:**
```
odoo-ce
├── modules
│   ├── sale
│   ├── purchase
│   ├── inventory
│   ├── accounting
│   └── hr
├── development
│   ├── orm
│   ├── views
│   ├── actions
│   └── security
└── deployment
    ├── docker
    ├── kubernetes
    └── configuration
```

## Phase 2: API Layer

### 2.1 Browse Endpoint

**File:** `backend/app/api/v1/docs/browse.py`

**Logic:**
1. Accept optional `root` taxonomy UUID
2. Query taxonomy_nodes with recursive CTE or LTREE
3. Aggregate document counts per node
4. Return tree structure with counts

**Query pattern:**
```sql
WITH RECURSIVE tree AS (
  SELECT id, parent_id, slug, title, depth, 0 as level
  FROM docs.taxonomy_nodes
  WHERE parent_id IS NULL OR parent_id = :root
  UNION ALL
  SELECT n.id, n.parent_id, n.slug, n.title, n.depth, t.level + 1
  FROM docs.taxonomy_nodes n
  JOIN tree t ON n.parent_id = t.id
  WHERE t.level < :max_depth
)
SELECT t.*, COUNT(dt.doc_id) as doc_count
FROM tree t
LEFT JOIN docs.doc_taxonomy dt ON dt.taxonomy_id = t.id
GROUP BY t.id, t.parent_id, t.slug, t.title, t.depth, t.level;
```

### 2.2 Faceted Search Endpoint

**File:** `backend/app/api/v1/docs/search.py`

**Logic:**
1. Accept query + filter object
2. Build hybrid search (BM25 + vector)
3. Apply facet filters as WHERE clauses
4. Compute facet counts with GROUP BY
5. Return hits + facet aggregations

**Facet computation:**
```sql
-- Pre-filter hits
WITH filtered_hits AS (
  SELECT d.id, d.title, ts_rank(d.fts, query) as bm25_score
  FROM rag.documents d
  WHERE d.fts @@ plainto_tsquery(:query)
    AND d.id IN (SELECT doc_id FROM docs.doc_taxonomy WHERE taxonomy_id = ANY(:taxonomy_filter))
    AND (SELECT product FROM docs.doc_metadata WHERE doc_id = d.id) = ANY(:product_filter)
)
-- Compute facets
SELECT
  'product' as facet,
  dm.product as value,
  COUNT(*) as count
FROM filtered_hits fh
JOIN docs.doc_metadata dm ON dm.doc_id = fh.id
GROUP BY dm.product
UNION ALL
SELECT
  'taxonomy' as facet,
  tn.slug as value,
  COUNT(*) as count
FROM filtered_hits fh
JOIN docs.doc_taxonomy dt ON dt.doc_id = fh.id
JOIN docs.taxonomy_nodes tn ON tn.id = dt.taxonomy_id
GROUP BY tn.slug;
```

### 2.3 Learning Journey Endpoint

**File:** `backend/app/api/v1/docs/journey.py`

**Logic:**
1. Fetch journey by slug
2. Join steps with documents
3. Compute user progress from `runtime.user_journey_progress`
4. Mark completed/current/locked steps

### 2.4 Glossary Endpoint

**File:** `backend/app/api/v1/docs/glossary.py`

**Logic:**
1. Prefix search on term
2. Filter by product context
3. Return definitions with doc links

## Phase 3: Pipeline Enhancement

### 3.1 Taxonomy Assignment Pipeline

**n8n Workflow:** `docs_gold_taxonomy_assign`

**Steps:**
1. Receive Silver chunks with headings
2. Extract topic signals (keywords, headers, code patterns)
3. Match against taxonomy node descriptions
4. Assign primary + secondary taxonomy nodes
5. Write to `docs.doc_taxonomy`

### 3.2 Glossary Extraction Pipeline

**n8n Workflow:** `docs_gold_glossary_extract`

**Steps:**
1. Scan documents for definition patterns
2. Extract term + definition pairs
3. Detect acronyms and expansions
4. Deduplicate against existing glossary
5. Insert new terms, flag conflicts for review

### 3.3 Related Docs Graph Builder

**n8n Workflow:** `docs_gold_related_build`

**Steps:**
1. For each document, compute embedding similarity
2. Extract explicit links (href references)
3. Detect supersession (version comparison)
4. Build weighted edges
5. Write to `docs.related_docs`

## Phase 4: UI Integration (Continue)

### 4.1 Context Provider: Taxonomy

**File:** `.continue/context/taxonomy.ts`

Provides taxonomy tree for `/docs browse` command.

### 4.2 Context Provider: Journey

**File:** `.continue/context/journey.ts`

Provides learning journey context for `/docs journey` command.

### 4.3 Slash Command Updates

**Updates to existing:**
- `/docs <query>` - Add facet filter syntax: `/docs query product:odoo-ce type:guide`
- `/docs browse [node]` - Navigate taxonomy tree
- `/docs journey <slug>` - Show learning journey with progress

## Phase 5: Observability

### 5.1 Search Telemetry

**Table:** `runtime.search_telemetry`

```sql
CREATE TABLE runtime.search_telemetry (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  query TEXT NOT NULL,
  filters JSONB,
  result_count INTEGER,
  click_position INTEGER,
  session_id UUID,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### 5.2 Zero-Result Analysis

**Scheduled job:** Weekly aggregation of zero-result queries to identify content gaps.

### 5.3 Journey Progress Tracking

**Table:** `runtime.user_journey_progress`

```sql
CREATE TABLE runtime.user_journey_progress (
  user_id UUID,
  journey_id UUID REFERENCES docs.learning_journeys(id),
  step_order INTEGER,
  completed_at TIMESTAMPTZ,
  PRIMARY KEY (user_id, journey_id, step_order)
);
```

## Dependency Graph

```
Phase 1.1 (Schema) ──┬──> Phase 2.1 (Browse API)
                     ├──> Phase 2.2 (Search API)
                     └──> Phase 3.* (Pipelines)

Phase 1.2 (Versioning) ──> Phase 2.2 (Search facets)

Phase 1.3 (Seed Data) ──> Phase 3.1 (Taxonomy assign)

Phase 2.* (APIs) ──> Phase 4.* (Continue UI)

Phase 5.* (Observability) - Independent, can run in parallel
```

## Rollout Strategy

1. **Schema migration** - Deploy during low-traffic window
2. **Seed taxonomy** - Initial structure from existing doc categories
3. **Backfill pipeline** - Run taxonomy assignment on existing docs
4. **API endpoints** - Deploy behind feature flag
5. **Continue integration** - Enable new slash commands
6. **Monitoring** - Enable telemetry collection
7. **GA** - Remove feature flag after validation
