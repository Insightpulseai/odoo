# Tasks – InsightPulse Docs AI

> Status values: `todo`, `in-progress`, `blocked`, `done`

## 1. Spec & Foundations

- [x] **T-001** – Create Spec Kit directory `spec/insightpulse-docs-ai/` in repo
  - Status: done
  - Output: `constitution.md`, `prd.md`, `plan.md`, `tasks.md` checked in.

- [ ] **T-002** – Register Docs AI as a Pulser agent in the central Pulser registry
  - Status: todo
  - Output: `pulser/agents/docs_ai.yaml` with skills and model routing.

- [ ] **T-003** – Confirm Supabase project and environment variables for Docs AI
  - Status: todo
  - Output: `.env` / secret mapping prepared for CI and runtime.

---

## 2. Data & Schema (Phase 1)

- [x] **T-010** – Design Supabase schema for documents and chunks
  - Status: done
  - Tables: `docs_ai_documents`, `docs_ai_document_chunks`.

- [x] **T-011** – Add `pgvector` extension and `embeddings` column on `document_chunks`
  - Status: done
  - Output: migration with `vector` column and index.

- [x] **T-012** – Create question/answer logging schema
  - Status: done
  - Tables: `docs_ai_questions`, `docs_ai_answers`.

- [x] **T-013** – Write initial SQL migrations for all Docs AI tables
  - Status: done
  - Output: `supabase/migrations/20251227_docs_ai_schema.sql`.

---

## 3. Connectors (Phase 1)

- [ ] **T-020** – Implement website/docs crawler (sitemap-based)
  - Status: todo
  - Features: URL allowlist, robots.txt respect, HTML → normalized doc.

- [ ] **T-021** – Implement GitHub docs connector
  - Status: todo
  - Features: repo path allowlist, Markdown parsing.

- [ ] **T-022** – Implement ingestion scheduler (cron/Edge Functions)
  - Status: todo
  - Features: periodic sync, simple retry policy.

- [ ] **T-023** – Seed initial InsightPulse docs content into Supabase
  - Status: todo
  - Output: baseline document set for QA.

---

## 4. RAG Engine

- [ ] **T-030** – Implement chunking strategy for technical docs
  - Status: todo
  - Inputs: heading-based splitting, code-block preservation.

- [ ] **T-031** – Implement embedding pipeline (batch + on-change)
  - Status: todo
  - Requirements: error logging and retry on failures.

- [ ] **T-032** – Implement hybrid retrieval (vector + keyword)
  - Status: todo
  - Output: retrieval function with configurable k and weights.

- [ ] **T-033** – Implement answer composer with citations
  - Status: todo
  - Behavior: citations always included, summarize in ≤ N tokens.

- [ ] **T-034** – Implement confidence scoring and low-confidence behavior
  - Status: todo
  - Behavior: ask for clarification or mark as unresolved.

---

## 5. API & SDK

- [x] **T-040** – Implement `POST /v1/ask` API (Edge Function or Node service)
  - Status: done
  - Input: `question`, `tenant_id`, optional filters.
  - Output: `answer`, `citations`, `confidence`.

- [ ] **T-041** – Implement healthcheck endpoint for Docs AI
  - Status: todo
  - Output: `/health` with DB + LLM sanity checks.

- [ ] **T-042** – Implement minimal TypeScript SDK for Docs AI
  - Status: todo
  - Methods: `ask()`, `withSurface()`, `withContext()`.

- [ ] **T-043** – Add Pulser SDK integration calls to `/v1/ask` backend
  - Status: todo
  - Behavior: all calls executed via Pulser agent where applicable.

---

## 6. Docs Widget (Phase 1)

- [x] **T-050** – Implement React-based docs widget
  - Status: done
  - Features: chat UI, loading state, error handling, answer rendering.

- [x] **T-051** – Implement embeddable JS snippet loader
  - Status: done
  - Behavior: single script tag injects widget into docs site.

- [ ] **T-052** – Add basic theming (colors, logo, position)
  - Status: todo
  - Inputs: config object or data attributes.

- [ ] **T-053** – Integrate widget into InsightPulse docs for internal dogfooding
  - Status: todo
  - Output: visible "Ask AI" entry point.

---

## 7. Multi-Surface Expansion (Phase 2)

- [ ] **T-060** – Implement in-product assistant variant of widget
  - Status: todo
  - Behavior: accepts route/feature context props.

- [ ] **T-061** – Implement support-ticket deflector widget
  - Status: todo
  - Behavior: "Did this solve your issue?" + escalate path.

- [ ] **T-062** – Implement Slack bot (`/docsai`)
  - Status: todo
  - Features: basic Q&A + link expansions.

- [ ] **T-063** – Optional: Implement Discord bot variant
  - Status: todo

---

## 8. Additional Connectors (Phase 2)

- [ ] **T-070** – Implement Notion connector
  - Status: todo
  - Behavior: sync selected spaces and pages.

- [ ] **T-071** – Implement Confluence connector
  - Status: todo
  - Behavior: space-based sync.

- [ ] **T-072** – Implement Google Drive connector (Docs, Sheets, PDFs)
  - Status: todo

- [ ] **T-073** – Implement Zendesk/help center connector
  - Status: todo
  - Behavior: ingest articles and categories.

---

## 9. Analytics & Dashboard

- [ ] **T-080** – Implement question/answer logging in Supabase
  - Status: todo
  - Data: surface, timestamps, confidence, feedback.

- [ ] **T-081** – Build analytics dashboard (Next.js)
  - Status: todo
  - Views: overview, per-surface, low-confidence, gaps.

- [ ] **T-082** – Implement gap detection view
  - Status: todo
  - Criteria: queries with low confidence or no good match.

---

## 10. Security & Enterprise Features (Phase 3)

- [ ] **T-090** – Implement RBAC roles (Viewer, Admin, SuperAdmin)
  - Status: todo

- [ ] **T-091** – Integrate SSO (Google/Microsoft OAuth, optional SAML)
  - Status: todo

- [ ] **T-092** – Implement tenant isolation with RLS or per-DB pattern
  - Status: todo

- [ ] **T-093** – Add PII masking to ingestion pipeline
  - Status: todo
  - Behavior: redact emails, phone numbers, IDs where configured.

---

## 11. Evaluation & QA

- [ ] **T-100** – Create initial evaluation question set (golden set)
  - Status: todo

- [ ] **T-101** – Implement automated evaluation pipeline
  - Status: todo
  - Metrics: retrieval quality, answer quality rating.

- [ ] **T-102** – Add regression tests for major engine changes
  - Status: todo

---

## 12. Observability & Operations

- [ ] **T-110** – Add structured logging for Docs AI services
  - Status: todo

- [ ] **T-111** – Expose metrics for monitoring (latency, error rates, volume)
  - Status: todo

- [ ] **T-112** – Document operational runbook for Docs AI incidents
  - Status: todo

---

## 13. Launch & Adoption

- [ ] **T-120** – Enable Docs AI on primary InsightPulse product docs
  - Status: todo

- [ ] **T-121** – Train internal teams on usage and feedback loops
  - Status: todo

- [ ] **T-122** – Define and track KPIs (deflection, CSAT, time-to-answer)
  - Status: todo
