# Org Documentation Platform Contract

> Version: 1.0
> Status: Active
> Owner: platform_team
> Updated: 2026-03-15
> Machine-readable architecture: `ssot/docs/doc_platform_architecture.yaml`
> Metadata schema: `ssot/docs/metadata_schema.yaml`
> Citation contract: `ssot/docs/citation_contract.yaml`
> Access policy: `ssot/docs/access_policy_contract.yaml`

---

## Purpose

This contract defines the architecture and operational contracts for the organization-wide documentation platform. It builds on and extends the existing `packages/odoo-docs-kb/` (chunker, embedder, indexer, eval) and `apps/odoo-docs-kb/` (FastAPI RAG service) components to support all documentation sources across the organization.

---

## 1. Source Adapters / Loaders

The platform ingests documentation from three source types:

### 1.1 Repo Docs Loader

Loads documentation from the git repository. Extends `packages/odoo-docs-kb/loader.py`.

| Field | Value |
|-------|-------|
| Source type | `repo` |
| Input | Git working tree paths |
| Formats | Markdown (.md), reStructuredText (.rst), YAML (.yaml/.yml) |
| Trigger | Git push to main (incremental), weekly full refresh |
| Paths indexed | See `ssot/docs/source_inventory.yaml` (P0 and P1 sources) |
| Exclusions | `node_modules/`, `.git/`, `archive/`, `infra/vendor/`, `docs/evidence/`, `.env*` |

### 1.2 Web Docs Loader

Loads external documentation from web sources. Extends `packages/odoo-docs-kb/web_loader.py`.

| Field | Value |
|-------|-------|
| Source type | `web` |
| Input | URLs defined in `agents/knowledge/*/source.yaml` |
| Formats | HTML, RST (converted to normalized markdown) |
| Trigger | Weekly refresh via CI |
| Sources | Odoo 18 docs, Azure platform docs, Databricks docs |

### 1.3 Spec Bundle Loader

Loads spec bundles as structured document groups.

| Field | Value |
|-------|-------|
| Source type | `spec` |
| Input | `spec/*/` directories |
| Structure | constitution.md + prd.md + plan.md + tasks.md per bundle |
| Metadata | Bundle name derived from directory, inter-doc references preserved |

---

## 2. Normalization Pipeline

All source content is normalized before chunking.

| Input Format | Normalizer | Output |
|-------------|------------|--------|
| RST (.rst) | `rst-normalizer` | Normalized plain text with heading hierarchy |
| Markdown (.md) | `markdown-normalizer` | Normalized plain text with heading hierarchy |
| HTML | `html-normalizer` | Extracted text, headings preserved |
| YAML (.yaml/.yml) | `yaml-normalizer` | Key-value pairs with path context |

Normalization rules:
- Strip images, figures, raw directives
- Preserve heading hierarchy for breadcrumb generation
- Convert code blocks to plain text with language annotation
- Strip front-matter (YAML headers) into metadata fields
- Normalize whitespace

---

## 3. Chunking Pipeline

Reuses `packages/odoo-docs-kb/chunker.py` (RST) and `packages/odoo-docs-kb/md_chunker.py` (Markdown).

### Chunking strategy

- **Split on**: h1, h2, h3 headings
- **Max chunk size**: 1500 characters (configurable)
- **Min chunk size**: 100 characters
- **Overlap**: 0 (heading-aware splitting avoids overlap need)
- **Context**: Each chunk carries its heading chain (breadcrumb)
- **IDs**: Deterministic: `{doc_id}:{heading_chain}:{ordinal}:{content_hash_8}`

### Chunk metadata

Every chunk carries metadata per `ssot/docs/metadata_schema.yaml`:
- `chunk_id` (deterministic)
- `doc_id` (parent document)
- `heading_chain` (breadcrumb path)
- `ordinal` (position within heading section)
- `char_count`
- `source` (repo | web | external)
- `path` (original file path)

---

## 4. Metadata Schema

Canonical schema defined in `ssot/docs/metadata_schema.yaml`.

Two levels:
1. **Document metadata**: Identifies a document within the corpus
2. **Chunk metadata**: Identifies a chunk within a document

Document ID formula: `{source}:{branch}:{path}:{content_hash}`
Chunk ID formula: `{doc_id}:{heading_chain}:{ordinal}:{content_hash_8}`

---

## 5. Indexing / Search Backend

### Azure AI Search

| Field | Value |
|-------|-------|
| Service | Azure AI Search |
| Identity | DefaultAzureCredential (managed identity) |
| Embedding model | Azure OpenAI `text-embedding-ada-002` |
| Vector dimensions | 1536 |
| Scoring profile | Hybrid (BM25 + vector cosine similarity) |
| Semantic ranker | Enabled |

### Indexes

| Index | Description | Status |
|-------|-------------|--------|
| `org-docs` | Unified org documentation (repo docs, specs, contracts, runbooks) | Planned |
| `odoo18-docs` | Odoo 18 CE documentation | Operational |
| `azure-platform-docs` | Azure platform documentation | Scaffolded |
| `databricks-docs` | Databricks documentation | Scaffolded |

Index schema follows Azure AI Search field definitions. Vector field `content_vector` stores embeddings. Filterable fields: `source`, `doc_type`, `sensitivity`, `freshness`.

---

## 6. Citation Contract

Defined in `ssot/docs/citation_contract.yaml`.

Every answer from the RAG service must include:
- At least 1 citation with `chunk_id`, `doc_id`, `title`, `path`, `content_excerpt`, `score`
- A `confidence_band` (high | medium | low | none)
- An `ambiguity_flag` with reason if multiple conflicting sources found

---

## 7. Access Control Model

Defined in `ssot/docs/access_policy_contract.yaml`.

| Level | Description |
|-------|-------------|
| `public` | Indexed, searchable by all |
| `internal` | Indexed, searchable by authenticated users |
| `restricted` | Indexed, searchable by authorized roles only |

Default level: `internal`.

Special rules:
- `docs/evidence/**` -- skip indexing (derived, not source of truth)
- `.env*` -- never index
- `docs/security/**` -- restricted

---

## 8. Freshness / Refresh Model

### Incremental refresh (git-based)

- Trigger: Push to main branch
- Mechanism: `git diff --name-only HEAD~1` to identify changed files
- Action: Re-chunk and re-index only changed documents
- CI workflow: `.github/workflows/odoo-docs-kb-refresh.yml`

### Full refresh (weekly)

- Trigger: Scheduled CI (weekly, Sunday 02:00 UTC)
- Mechanism: Full crawl of all P0 and P1 sources
- Action: Rebuild all chunks, re-embed, re-index
- Web sources: Re-fetch from source.yaml URLs

### Staleness detection

- Documents not modified in >90 days: flag as `potentially_stale`
- Documents with deprecated markers: flag as `deprecated`
- Evidence bundles: never index (skip)

---

## 9. Evaluation Model

### Capability Evaluation

Reuses `agents/evals/odoo_copilot_target_capabilities.yaml` pattern.

| Eval Type | Tool | Metric |
|-----------|------|--------|
| Retrieval precision | `packages/odoo-docs-kb/eval.py` | Precision@5, Recall@5 |
| Answer quality | Foundry eval (Azure AI) | Groundedness, Coherence, Relevance |
| Citation accuracy | Custom validator | Citation hit rate |
| Latency | Service health probe | P50, P95, P99 response time |

### Retrieval Evaluation

Test queries defined per knowledge domain:
- `agents/knowledge/odoo18_docs/` -- existing eval queries
- `agents/knowledge/azure_platform/` -- existing eval queries
- `spec/odoo-copilot-benchmark/scenarios/` -- existing benchmark scenarios

---

## 10. Deployment / Runtime Model

### Compute

| Component | Runtime | Notes |
|-----------|---------|-------|
| Indexer | Azure Container Apps (job) | Runs on push and weekly schedule |
| RAG service | Azure Container Apps (app) | FastAPI, always-on |
| Search backend | Azure AI Search | Managed service |
| Embedder | Azure OpenAI | Managed service |

### Container

| Field | Value |
|-------|-------|
| Registry | Azure Container Registry (ACR) |
| Image | `org-docs-search-service:latest` |
| Base | `apps/odoo-docs-kb/Dockerfile` |
| Health probe | `GET /health` |
| Port | 8000 |

### Identity

All Azure service calls use `DefaultAzureCredential` (managed identity). No API keys in code.

---

## 11. Observability Model

### Logging

- Structured JSON logs to stdout (Azure Monitor picks up)
- Log fields: `timestamp`, `level`, `component`, `operation`, `duration_ms`, `doc_count`, `chunk_count`

### Metrics

| Metric | Type | Alert Threshold |
|--------|------|----------------|
| Index document count | Gauge | < 100 (expected ~800+) |
| Indexing duration | Timer | > 30 min |
| Search latency P95 | Timer | > 2s |
| Search error rate | Counter | > 5% |
| Embedding API errors | Counter | > 10/hour |

### Health Probes

| Endpoint | Expected | Interval |
|----------|----------|----------|
| `GET /health` | `{"status": "ok"}` | 30s |
| `GET /health/search` | Azure AI Search reachable | 60s |
| `GET /health/embedder` | Azure OpenAI reachable | 60s |

---

## Component Reuse Map

| Existing Component | Reuse in Org Platform |
|-------------------|----------------------|
| `packages/odoo-docs-kb/chunker.py` | RST chunking (Odoo docs) |
| `packages/odoo-docs-kb/md_chunker.py` | Markdown chunking (repo docs) |
| `packages/odoo-docs-kb/embed.py` | Azure OpenAI embedding |
| `packages/odoo-docs-kb/index.py` | Azure AI Search indexing |
| `packages/odoo-docs-kb/loader.py` | Document loading |
| `packages/odoo-docs-kb/web_loader.py` | Web document fetching |
| `packages/odoo-docs-kb/eval.py` | Retrieval evaluation |
| `apps/odoo-docs-kb/service.py` | FastAPI RAG service |
| `agents/knowledge/*/source.yaml` | Source definitions |
| `agents/knowledge/*/chunking.yaml` | Chunking configuration |
| `agents/knowledge/*/indexing.yaml` | Indexing configuration |
| `agents/evals/*.yaml` | Capability evaluation framework |
| `spec/odoo-copilot-benchmark/scenarios/` | Benchmark scenarios |

---

*Registered in `docs/contracts/PLATFORM_CONTRACTS_INDEX.md`.*
