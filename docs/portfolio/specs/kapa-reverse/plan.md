# Plan — Kapa-Reverse

## Assumptions
- Supabase is the primary backend (Postgres + pgvector).
- Frontend can be Next.js (widget + admin) and deployed on Vercel/DO.
- LLM provider is configurable; start with OpenAI or Claude, add local later.
- Multi-tenant from day 1 (tenant_id everywhere + RLS).

## Architecture (High Level)
1. **Indexer Service**
   - Fetch sources, chunk, embed, store
2. **Retrieval Service**
   - Hybrid search + rerank
3. **Answer Service**
   - Prompting + streaming + citations + confidence gating
4. **Channel Surfaces**
   - Widget, API, MCP, Slack
5. **Ops/Tracing**
   - runs + events + replay tooling

## Milestones

### M1 — Core RAG (Week 1)
- Supabase schema + RLS
- Doc crawler + GitHub ingest
- Chunking + embeddings + hybrid retrieval
- `/ask` and `/search` endpoints
- Minimal widget embed

### M2 — Quality + Ops (Week 2)
- Citation enforcement + strict mode
- Confidence gating (`is_uncertain`) + escalation hook
- Structured tracing + replay
- Feedback loop + unresolved clustering v1

### M3 — MCP + Proxy (Week 3)
- Hosted MCP server (tools: search, ask)
- Proxy MCP example server for "single install"
- Pulser SDK instructions + agent registration
- Tenant-scoped auth tokens for IDE agents

### M4 — Admin Console + White-label (Week 4)
- Admin UI for sources + reindex + analytics
- Theme config + per-tenant branding
- Domain/embedding snippet generator
- Rate limits + abuse controls

## Risks
- Retrieval quality without reranker may be noisy → ship reranker early.
- Multi-tenant RLS mistakes → add policy tests + CI checks.
- Doc drift → enforce reindex schedules + webhook support.

## Concrete Next Steps
- Create repo scaffold with Spec Kit bundle + Supabase migrations + services layout.
- Implement M1 schema + ingest + ask/search endpoints.
- Add widget embed and a demo tenant wired to one repo + one docs site.
