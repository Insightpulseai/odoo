# PRD: SAP-Grade Documentation Platform

## Problem Statement

Current RAG documentation provides search and retrieval but lacks:
1. **Structured browsing** - No taxonomy tree for topic exploration
2. **Learning paths** - No guided journeys for skill building
3. **Glossary integration** - Terms not linked to authoritative definitions
4. **Version clarity** - No release channel or deprecation signals
5. **Faceted search** - No filtering by product, version, content type

Enterprise users expect SAP-style documentation portals with these capabilities.

## Target Users

| Persona | Needs | Current Pain |
|---------|-------|--------------|
| New Developer | Guided learning path from basics to advanced | Scattered docs, unclear order |
| Support Engineer | Quick lookup by product + version | Search returns all versions mixed |
| Integration Partner | API reference with examples | Examples not linked to specs |
| Auditor | Version history + deprecation trail | No lineage visibility |

## Solution Overview

### 1. Taxonomy Navigation (Browse Mode)

Hierarchical topic tree matching SAP Help Portal structure:

```
Products
├── Odoo CE
│   ├── Sales
│   │   ├── CRM
│   │   ├── Quotations
│   │   └── Orders
│   ├── Inventory
│   └── Accounting
├── OCA Addons
│   ├── hr-expense
│   ├── sale-workflow
│   └── ...
└── Platform
    ├── API Reference
    ├── Integration Guides
    └── Migration Paths
```

### 2. Learning Journeys

Curated paths with prerequisites and progress tracking:

```yaml
journey: "Odoo Developer Onboarding"
steps:
  - doc: getting-started/environment-setup
    prereq: null
  - doc: tutorials/first-module
    prereq: step[0]
  - doc: guides/orm-basics
    prereq: step[1]
  - doc: guides/views-forms
    prereq: step[2]
  - doc: advanced/custom-widgets
    prereq: step[3]
estimated_hours: 8
certification: "odoo-dev-fundamentals"
```

### 3. Glossary Integration

Terms linked to authoritative sources:

| Term | Definition | Authoritative Doc | Product Context |
|------|------------|-------------------|-----------------|
| ORM | Object-Relational Mapping layer | /dev/orm-reference | Odoo CE |
| RLS | Row-Level Security | /platform/security | Supabase |
| Medallion | Bronze/Silver/Gold data layers | /arch/data-layers | Platform |

### 4. Version Lineage

Release channel clarity:

```
Document: /api/sale-order
├── v18.0 (stable) ← current
├── v17.0 (lts) ← maintained
├── v16.0 (deprecated) → successor: v17.0
└── v19.0-edge (preview)
```

### 5. Faceted Search

Filter dimensions:
- **Product**: Odoo CE, OCA, Platform
- **Version**: 18.0, 17.0, 16.0
- **Type**: Guide, Reference, Tutorial, API
- **Status**: Current, Deprecated, Preview
- **Topic**: From taxonomy nodes

## Technical Requirements

### Schema Additions

```sql
-- Taxonomy tree (adjacency list)
CREATE TABLE docs.taxonomy_nodes (
  id UUID PRIMARY KEY,
  parent_id UUID REFERENCES docs.taxonomy_nodes(id),
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  depth INTEGER GENERATED ALWAYS AS (computed),
  path LTREE,
  sort_order INTEGER DEFAULT 0
);

-- Document metadata
CREATE TABLE docs.doc_metadata (
  doc_id UUID PRIMARY KEY REFERENCES rag.documents(id),
  product TEXT NOT NULL,
  content_type TEXT NOT NULL,
  release_channel TEXT DEFAULT 'stable',
  is_breaking BOOLEAN DEFAULT false,
  is_deprecated BOOLEAN DEFAULT false,
  successor_id UUID REFERENCES rag.documents(id),
  glossary_terms TEXT[],
  orphan_flag BOOLEAN DEFAULT false
);

-- Document-taxonomy mapping (many-to-many)
CREATE TABLE docs.doc_taxonomy (
  doc_id UUID REFERENCES rag.documents(id),
  taxonomy_id UUID REFERENCES docs.taxonomy_nodes(id),
  is_primary BOOLEAN DEFAULT false,
  PRIMARY KEY (doc_id, taxonomy_id)
);

-- Related documents graph
CREATE TABLE docs.related_docs (
  source_id UUID REFERENCES rag.documents(id),
  target_id UUID REFERENCES rag.documents(id),
  relationship TEXT NOT NULL,
  weight FLOAT DEFAULT 1.0,
  PRIMARY KEY (source_id, target_id, relationship)
);

-- Learning journeys
CREATE TABLE docs.learning_journeys (
  id UUID PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  estimated_hours FLOAT,
  certification_slug TEXT,
  product TEXT NOT NULL
);

CREATE TABLE docs.learning_journey_steps (
  journey_id UUID REFERENCES docs.learning_journeys(id),
  step_order INTEGER NOT NULL,
  doc_id UUID REFERENCES rag.documents(id),
  prereq_step_id UUID REFERENCES docs.learning_journey_steps(journey_id, step_order),
  notes TEXT,
  PRIMARY KEY (journey_id, step_order)
);

-- Glossary
CREATE TABLE docs.glossary (
  term TEXT NOT NULL,
  product_context TEXT NOT NULL,
  definition TEXT NOT NULL,
  acronym_expansion TEXT,
  doc_id UUID REFERENCES rag.documents(id),
  anchor_id TEXT,
  PRIMARY KEY (term, product_context)
);
```

### API Endpoints

```yaml
/v1/docs/browse:
  GET:
    params:
      - root: taxonomy node to start from (optional)
      - depth: how many levels to return (default: 2)
    returns:
      nodes: taxonomy tree with doc counts

/v1/docs/search:
  POST:
    body:
      query: string
      filters:
        product: string[]
        version: string[]
        type: string[]
        taxonomy: uuid[]
      limit: integer
      offset: integer
    returns:
      hits: documents with snippets
      facets: aggregated filter counts

/v1/docs/journey/{slug}:
  GET:
    returns:
      journey: metadata
      steps: ordered documents
      progress: user completion status

/v1/docs/glossary:
  GET:
    params:
      - term: search term
      - product: filter by product context
    returns:
      terms: matching glossary entries
```

### Pipeline Integration

```
Bronze (Crawl)     → Silver (Normalize)      → Gold (Enrich)
─────────────────────────────────────────────────────────────
Raw HTML/MD        → Markdown chunks         → Embeddings
Source metadata    → Cleaned headings        → Taxonomy assignments
                   → Code block extraction   → Glossary term links
                   → Version detection       → Related doc graph
```

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Browse to doc click-through | >40% | Analytics on taxonomy nav |
| Search with facets | >60% of queries | Filter usage telemetry |
| Journey completion rate | >25% | Step progress tracking |
| Glossary hover engagement | >10% of sessions | Term popup analytics |
| Deprecated doc views | <5% | Version telemetry |

## Out of Scope

- Real-time collaborative editing (use external CMS)
- Translation/localization (future phase)
- User-generated content (comments, ratings)
- Offline documentation sync
