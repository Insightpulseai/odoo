# PRD — Kapa-Reverse (Improved Knowledge Support AI)

## Summary
Kapa-Reverse is a white-label, Supabase-first knowledge support AI platform that outperforms typical "docs chat" by combining:
- Multi-source ingestion + dedup + canonicalization
- Hybrid search (BM25 + vector) + reranking
- Strict grounding with citations + confidence gating
- Multi-channel delivery: widget, API, MCP, Slack
- Full observability + feedback-driven continuous improvement

## Problem
Teams ship fast across docs, code, and support channels. Users ask questions in product and expect precise, current answers. Traditional RAG bots:
- hallucinate without citations,
- drift with outdated docs,
- can't isolate tenants cleanly,
- lack operational tooling (replay, QA, gap analysis),
- and don't expose a clean MCP surface for IDE/agent tooling.

## Target Users
1. **End users**: customers searching docs from website/app.
2. **Support & CS**: need faster, consistent answers with citations + escalation.
3. **Engineers**: want MCP retrieval tool for IDE agents (Claude/Codex/Gemini).
4. **Admins**: need onboarding, access controls, and analytics.

## Goals (MVP)
- Grounded Q&A on a tenant's sources with reliable citations.
- Embed widget + API.
- Hosted MCP endpoint + optional proxy MCP for unified tool install.
- Admin console for sources, indexing status, and feedback triage.

## Non-Goals (MVP)
- Full ticketing system replacement (only escalation hooks).
- Full multi-lingual rewriting workflows (basic multi-language retrieval ok).
- Enterprise SSO breadth (support basic SSO later; MVP can use Supabase Auth + magic link).

## Key Differentiators vs typical Kapa-like setups
1. **Confidence gating + escalation**: deterministic `is_uncertain` plus "ask clarifying" fallback before hallucinating.
2. **Doc freshness guarantees**: "staleness scoring" and scheduled reindex with drift alerts.
3. **Source gap analytics**: automatically clusters "unanswered" queries and recommends missing docs/pages.
4. **Trace replay**: every answer run is replayable with pinned retrieval snapshot.
5. **White-label**: per-tenant theming + domain + legal/ToS injection.

## Functional Requirements

### A) Ingestion & Indexing
- Sources:
  - GitHub repos (markdown, mdx, docs folders, READMEs, issues/PR discussions optional)
  - Static docs site (crawl + sitemap)
  - GitBook (optional connector)
  - Slack/Zendesk later (hooks prepared)
- Pipeline steps:
  1. Fetch → normalize → split into chunks
  2. Extract metadata (url, title, headings, repo path, commit hash, timestamps)
  3. Compute embeddings + optional BM25 indexing
  4. Store chunks in Supabase Postgres + pgvector
  5. Maintain "document lineage" (source version → chunk ids)
- Reindex:
  - Scheduled (cron) and event-driven (GitHub webhook)
  - Drift detection: compare source hash/commit to index version

### B) Retrieval
- Hybrid search:
  - Vector similarity (pgvector)
  - Keyword/BM25 (Postgres tsvector or external optional)
  - Merge + rerank (cross-encoder or lightweight reranker)
- Filters:
  - tenant_id, source_id, doc_type, path prefix, tags, recency window
- Output:
  - top_k chunks with spans and canonical URLs

### C) Answering
- LLM adapter interface:
  - OpenAI, Anthropic, local (Ollama/vLLM) pluggable
- Prompt policy:
  - Must cite sources for claims
  - Must say "I don't know" if retrieval insufficient
  - Must produce structured payload:
    - `answer_markdown`
    - `citations[]` (url, title, chunk_id, offsets)
    - `confidence` (0–1)
    - `is_uncertain` boolean
    - `followups[]`
- Optional modes:
  - "Search only" (no generation)
  - "Strict mode" (refuse if no citations)

### D) Channels
1. **Web Widget**
   - Small launcher + chat panel
   - Streaming responses
   - Citation cards + "copy answer"
   - Feedback (thumbs up/down + reason)
2. **REST API**
   - `POST /ask`
   - `POST /search`
   - `POST /feedback`
3. **MCP Server**
   - Tools:
     - `kapa_reverse.search(query, filters) -> chunks`
     - `kapa_reverse.ask(query, mode) -> answer + citations`
   - Tenant auth via token + RLS-backed claims
4. **Slack Bot (MVP+)**
   - `/ask` command, thread replies, citations

### E) Admin Console
- Tenants, users, roles
- Sources: connect, crawl status, last indexed version, errors
- Analytics:
  - top queries
  - unresolved queries
  - citation coverage
  - latency
- Feedback triage:
  - label clusters
  - mark "resolved by doc"
  - link to KB tasks

## UX / UI
- Use OpenAI Apps SDK UI patterns for chat ergonomics and accessibility.
- Optionally wrap with Fluent UI tokens for enterprise consistency.
- White-label theme config:
  - colors, logo, typography, corner radius, spacing
- Widget embed snippet with per-tenant key.

## Data Model (Supabase)
Schemas:
- `auth` (Supabase)
- `public` or `kb` (core data)
- `ops` (runs, events, traces)

Core tables (high-level):
- `tenants`
- `sources`
- `documents`
- `chunks` (content, metadata, embedding vector)
- `queries` (raw query logs, anonymized)
- `answers` (final response payload)
- `answer_citations` (join to chunks)
- `feedback` (vote + label)
- `runs` / `run_events` (traceability)

RLS:
- All tables keyed by `tenant_id`
- Policies ensure tenant isolation for all read/write paths

## Integrations
- GitHub App / PAT for repo sync (webhook + scheduled backfill)
- Sitemap crawler for docs
- Optional: GitBook integration
- Optional: Zendesk/Intercom (escalation endpoint only)

## Observability
- Store structured traces per run:
  - retrieval candidates + scores
  - rerank results
  - prompt version
  - model + latency + token usage
- Dashboard metrics:
  - p50/p95 latency
  - citation rate
  - unresolved rate
  - "uncertain" trigger rate

## Security & Compliance
- Tenant isolation via RLS
- Secrets only in env (Supabase secrets / host secrets)
- PII redaction hook for ingestion + query logs
- Audit logs for admin actions

## Rollout Plan (MVP)
- Phase 1: GitHub + docs crawler + widget + API + minimal admin
- Phase 2: MCP server + proxy MCP + trace replay + gap analytics
- Phase 3: Slack + webhook-driven indexing + enterprise auth options

## Success Metrics
- Citation coverage > 95%
- "Unresolved" rate < 8% after 30 days of feedback loop
- p95 end-to-end response < 2.5s (cached < 1.2s)
- Support deflection rate improvement measurable per tenant

## Requirement: Pulser SDK
Include Pulser SDK installation + agent registration docs so Codex/Claude/Gemini can invoke MCP and API consistently from your orchestration environment.
