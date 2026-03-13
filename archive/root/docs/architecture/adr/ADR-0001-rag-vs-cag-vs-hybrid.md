# ADR-0001: RAG vs CAG vs Hybrid Knowledge Access Pattern (Supabase-First)

## Status

Proposed

## Date

2026-02-24

## Owners

- Platform Architecture
- AI/Agent Systems
- Data Platform (Supabase SSOT)

## Context

We need a standard pattern for giving LLM-powered features access to external knowledge across InsightPulseAI systems (Odoo bridges, Supabase control plane, dashboards, agent workflows, support/ops tooling).

Current and planned use cases include:

- Product/domain documentation QA
- Internal operational runbooks
- Structured analytics interpretation
- Ticket/task/event summaries
- Cross-document synthesis
- Agent execution guidance with citations/evidence

### Existing Repository Capabilities (Confirmed)

This repository already has automated codebase/KB indexing and verification in CI, including:

- GitHub Actions gates for KB/index integrity verification
- Python verification scripts for index validation
- Auto-generated AI-assistant-oriented index artifacts (e.g., agent/codelens catalogs)
- Artifact sweep/validation during build/deploy to prevent index drift

This materially lowers the implementation cost of the RAG/Hybrid path because corpus/index freshness and drift detection are already enforced by repository automation.

We are evaluating three patterns:

1. **RAG (Retrieval-Augmented Generation)**
   - Retrieve relevant chunks from an external corpus (typically vector search / keyword search / hybrid search), then inject into the prompt.

2. **CAG (Cache-Augmented Generation)**
   - Load a large stable corpus directly into long context and rely on provider prompt/KV caching to reduce repeated prefill cost.

3. **Hybrid (CAG + RAG)**
   - Preload/cache a stable “core corpus” and retrieve dynamic/recent/large-tail data at query time.

### Definitions (Normative)

To avoid ambiguity, this repository uses:

- **CAG** = **Cache-Augmented Generation** (long-context prompting + provider prompt/KV caching), not any other overloaded meaning.

## Decision Drivers

- **Accuracy** under real-world corpus growth
- **Operational simplicity** for MVP and iteration speed
- **Cost efficiency** under repeated queries
- **Freshness** for fast-changing data
- **Traceability / citations** for evidence-backed outputs
- **Multi-tenant isolation** and access control
- **Supabase-first alignment** (Postgres, pgvector, RLS, Edge Functions, Storage, Realtime)

## Options Considered

### Option A — RAG-first

Use retrieval as the primary knowledge access mechanism for most queries.

### Option B — CAG-first

Use long-context + prompt caching as the primary mechanism, avoiding vector infrastructure initially.

### Option C — Hybrid (Chosen)

Use **CAG for stable core knowledge** and **RAG for dynamic / large / recent data**.

## Decision

We will adopt a **Hybrid knowledge access architecture**:

- **CAG** for:
  - Stable policies
  - Canonical architecture docs
  - Product definitions / glossary
  - Schema semantics / field dictionaries
  - Standard operating procedures
  - Agent capability manifests (relatively stable)
- **RAG** for:
  - Recent events/logs
  - Tickets/tasks/messages
  - Large document collections
  - Customer/project-specific documents
  - Time-sensitive operational data
  - High-churn records

### Why this decision

This pattern balances:

- **MVP simplicity** (CAG for core corpus)
- **Scalability** (RAG for large and dynamic tail)
- **Accuracy** (better synthesis from stable context + lower retrieval miss risk for core rules)
- **Freshness** (dynamic retrieval on changing data)
- **Cost control** (cache reuse for repeated core context)
- **Operational leverage** (reuses existing CI-automated KB/index generation + verification instead of introducing a separate indexing process)

## Architectural Implications

### 1) Supabase-First Implementation Baseline (Required)

#### Core services

- **Supabase Postgres** as metadata/control-plane SSOT
- **pgvector** for embeddings and semantic retrieval (RAG path)
- **Supabase Storage** for source documents / artifacts
- **Edge Functions** for:
  - ingest
  - chunk/embed/index
  - retrieval orchestration
  - prompt assembly
  - cache-key/version management
- **RLS** for tenant/user-level access boundaries
- **Realtime** for cache invalidation signals / ingestion completion events (optional but preferred)
- **Cron / scheduled jobs** for re-indexing and cache refreshes (if available in project setup)

#### Non-goals (for now)

- Provider-agnostic abstraction for every LLM vendor feature on day 1
- Full semantic graph retrieval replacement (can be layered later)
- “No retrieval ever” architecture

### 2) CAG Corpus Management (Required)

Even with CAG, we must manage:

- document selection
- context packing/order
- token budgeting
- versioning
- cache invalidation/refresh
- corpus change detection

**CAG is not “no infra”; it is different infra.**

### 3) RAG Retrieval Strategy (Preferred)

Use **hybrid retrieval** where feasible:

- vector similarity (semantic)
- lexical/keyword filters (metadata, exact terms)
- recency filters (for operational contexts)
- tenant/project scoping via RLS + metadata

### 4) Citations / Evidence Policy

All user-visible answers in operational/analytical contexts should support:

- source identifiers
- chunk/document references
- timestamps/versions where applicable

Hybrid architecture must preserve evidence provenance in both paths:

- **CAG path:** cite document/section/version included in cached corpus
- **RAG path:** cite retrieved chunks/records

### 5) Repository Indexes as First-Class Retrieval Inputs (Required for code-aware use cases)

For codebase-aware assistant features, retrieval should preferentially reuse repository-generated index artifacts (already validated in CI) before introducing duplicate indexing pipelines.

Examples of eligible inputs:

- KB/document search indexes
- code symbol/tag catalogs
- AI-assistant-specific generated indexes
- boundary inventories / SSOT manifests

Implications:

- Retrieval quality improves via deterministic, repo-native artifacts
- CI can gate index freshness and schema compatibility
- We avoid “shadow indexes” that drift from the build system

## Decision Rules (Routing Policy)

### Route to CAG when ALL are true

- Corpus is relatively stable
- Corpus fits within practical long-context budget
- Queries require broad synthesis across many docs
- Cache reuse expected across many requests
- Freshness tolerance is moderate (minutes/hours/daily refresh)

### Route to RAG when ANY are true

- Corpus is large or unbounded
- Data changes frequently
- Queries are narrow/lookup-style
- Tenant-specific data isolation is strict
- Freshness requirements are high
- Cost of re-caching large prompts is too high

### Route to Hybrid by default

If a feature is expected to grow or enter production, use Hybrid unless there is a strong reason not to.

## Supabase Data Model (Conceptual)

### Core tables (control plane)

- `ops.kb_corpora`
  - corpus metadata, tenant scope, strategy (`cag`, `rag`, `hybrid`)
- `ops.kb_documents`
  - source docs, versions, hashes, storage paths
- `ops.kb_chunks`
  - chunk text, embeddings, metadata (RAG path)
- `ops.kb_indexes`
  - index metadata / embedding model / dimensions
- `ops.kb_cache_manifests`
  - packed CAG corpus manifests (ordered doc/version list, token estimates)
- `ops.kb_cache_versions`
  - cache keys, provider cache IDs (if exposed), TTL/status
- `ops.kb_query_logs`
  - routing decision, latency, tokens, cache hit/miss, citations
- `ops.kb_refresh_jobs`
  - ingestion/re-embed/repack tasks and status

> Exact schema names may be adapted to existing `ops.*` conventions, but the separation of concerns above is required.

## Risks and Mitigations

### Risk 1: Retrieval misses in RAG

- **Mitigation:** hybrid retrieval, retrieval evals, chunking QA, fallback to broader retrieval, query rewriting.

### Risk 2: Prompt cache invalidation churn in CAG

- **Mitigation:** stable core corpus boundaries, manifest versioning, partial corpus partitioning, refresh windows.

### Risk 3: Cost spikes from long-context prefill

- **Mitigation:** cache warm-up for hot corpora, smaller manifests by domain, route narrow queries to RAG.

### Risk 4: Stale answers from cached context

- **Mitigation:** TTL + content hash invalidation + freshness-aware router + recency overlay via RAG.

### Risk 5: Tenant data leakage

- **Mitigation:** enforce RLS and tenant-scoped corpus manifests; never cross-tenant cache manifests.

## Consequences

### Positive

- Better synthesis for stable docs
- Better scalability for dynamic data
- Faster time to value for MVP features
- Stronger path to production-grade observability and optimization

### Negative

- More moving parts than pure CAG
- More routing/telemetry work than pure RAG
- Requires operational discipline for cache/version management

## Implementation Plan (Phased)

### Phase 1 — Hybrid Foundation (MVP)

- Establish `ops.*` control-plane tables
- Implement doc ingest + hashing + versioning
- Implement RAG pipeline (chunk/embed/index/search)
- Implement CAG manifest builder for one stable corpus
- Implement router with explicit rules (`cag` / `rag` / `hybrid`)
- Add query logging + citation payloads

### Phase 2 — Production Hardening

- Retrieval quality eval set + regression checks
- Cache hit/miss telemetry + cost dashboards
- Freshness-aware routing and invalidation policies
- Tenant/project scoping enforcement tests
- Failure-mode fallbacks (cache miss → RAG; retrieval fail → constrained CAG core)

### Phase 3 — Optimization

- Domain-specific corpus partitioning
- Query classifier for routing
- Adaptive context packing
- Optional graph/context overlays (knowledge graph / semantic relations)

## Rejected Alternatives

### Pure RAG everywhere

Rejected because it underperforms on broad cross-document synthesis and creates unnecessary retrieval dependency for stable corpora.

### Pure CAG everywhere

Rejected because it does not scale well for high-churn, large, or tenant-diverse corpora and creates expensive cache rebuild/invalidation behavior.

## Success Criteria

- ≥ 90% of target queries route successfully without manual intervention
- Citation payloads available for operational answers
- Cache hit rate improves repeated-query latency for stable corpora
- No cross-tenant citation/source leakage in validation tests
- Measurable cost reduction vs naive long-context-only prompting on mixed workloads

## Review Trigger

Revisit this ADR if any of the following occur:

- LLM provider context limits/caching economics materially change
- Corpus sizes or update rates exceed current thresholds
- New compliance requirements mandate different evidence/provenance handling
- A new retrieval/caching primitive materially simplifies the design
