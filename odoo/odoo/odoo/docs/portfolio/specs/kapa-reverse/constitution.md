# Kapa-Reverse Constitution

## 1) Purpose
Build a production-grade, self-hostable, white-label "Ask AI for your product" system that:
- Ingests your docs + repos + tickets + chats
- Answers with grounded citations
- Supports web widget + in-app + MCP + Slack
- Operates Supabase-first (Postgres + pgvector) with strict RLS

## 2) Product Principles
1. **Grounded by default**: every answer must include citations to indexed sources; no-citation responses are flagged.
2. **White-label first**: no vendor branding in client-facing surfaces; configurable theme + domain + legal text.
3. **Composable channels**: the same core retrieval/answer service powers Widget / API / MCP / Slack.
4. **Fast feedback loop**: thumbs up/down, "missing answer" capture, and auto-suggested source gaps.
5. **Observability is a feature**: full trace logs (retrieval, rerank, generation) and replayable runs.
6. **Tenant isolation**: org/project separation via RLS + schema boundaries; no cross-tenant leakage.
7. **Deterministic interfaces**: stable contracts (OpenAPI + MCP schema); versioned migrations.
8. **Fail safely**: when uncertain → ask clarifying question OR offer escalation (ticket/hand-off) instead of hallucinating.
9. **Upgrade-friendly**: migration-first, feature flags, backward-compatible APIs, CI gates for drift.
10. **Bring-your-own-model**: support OpenAI/Claude/local; swap via provider adapter.

## 3) Non-Negotiables
- RLS enforced on every read path.
- Source provenance stored for every chunk + answer span.
- "No citations" cannot be returned unless explicitly toggled per tenant.
- PII redaction hooks supported at ingestion and retrieval time.
- All secrets live in env/secret stores; never in repo.

## 4) Supported Surfaces (MVP+)
- Web widget (embed)
- REST API (answers, search, feedback)
- MCP server (retrieval tool + "ask" tool)
- Slack bot (optional MVP+)

## 5) Definition of Done
- A tenant can onboard 1–3 sources (Docs + GitHub) in <15 minutes.
- Typical answer latency p95 < 2.5s for retrieval + generation (with caching).
- Citation coverage: >95% answers with at least 1 valid citation.
- "Uncertain" gating triggers escalation on low-confidence queries.
