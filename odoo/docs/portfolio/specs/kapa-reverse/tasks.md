# Tasks — Kapa-Reverse

## 0) Repo + Spec Kit
- [x] Create `spec/kapa-reverse/{constitution,prd,plan,tasks}.md`
- [ ] Add CI gate: fail if Spec Kit bundle missing or malformed

## 1) Supabase (Schema + RLS)
- [ ] Create tables: tenants, sources, documents, chunks, queries, answers, citations, feedback, runs, run_events
- [ ] Add pgvector + indexes
- [ ] Implement RLS policies + policy tests

## 2) Indexer
- [ ] Docs crawler (sitemap + HTML→MD extraction)
- [ ] GitHub ingest (repo paths + markdown parsing; store commit hash)
- [ ] Chunker (heading-aware) + metadata enrich
- [ ] Embeddings job + backfill runner
- [ ] Reindex scheduler + drift detection

## 3) Retrieval
- [ ] Vector search RPC
- [ ] Keyword search (tsvector) + merged ranking
- [ ] Optional reranker adapter
- [ ] Filters (tenant/source/path/tags/recency)

## 4) Answer Service
- [ ] Provider adapter interface (OpenAI/Claude/local stub)
- [ ] Prompt policy for citations + "I don't know"
- [ ] Structured response payload with confidence + is_uncertain
- [ ] Streaming responses

## 5) Channels
- [ ] Web widget (embed + citations UI + feedback)
- [ ] REST API (ask/search/feedback)
- [ ] MCP server (search/ask tools)
- [ ] Proxy MCP example (FastMCP)

## 6) Admin Console
- [ ] Tenant + sources management
- [ ] Index status + errors
- [ ] Analytics dashboard
- [ ] Feedback triage + unresolved clustering

## 7) Observability + QA
- [ ] Trace logging for retrieval + generation
- [ ] Replay endpoint
- [ ] Offline eval harness (golden Q/A set, citation checks)
- [ ] Load tests (latency p95 targets)

## 8) Pulser SDK Requirement
- [ ] Add docs: Pulser SDK install + registering MCP + API tools
- [ ] Add example agent configs for Codex/Claude/Gemini parity

## 9) Release
- [ ] Demo tenant configured (one repo + one docs site)
- [ ] One-command deploy docs (Supabase + web)
- [ ] Versioned migrations + changelog
