# Delivery Plan – InsightPulse Docs AI

## 1. Approach

We will deliver InsightPulse Docs AI in **three phases**, each shippable and independently valuable:

1. **Phase 1 – Core RAG & Docs Widget (MVP)**
2. **Phase 2 – Multi-Surface Deployment & Connectors**
3. **Phase 3 – Enterprise-Grade Security & Deep Analytics**

All work is driven by this plan and tracked via `tasks.md`. Docs AI is a **Pulser-managed agent** from day one.

---

## 2. Phase 1 – Core RAG & Docs Widget (MVP)

**Objective**
Ship a working AI assistant on InsightPulse product docs, backed by an internal RAG engine.

### 2.1 Deliverables

- Supabase schema for:
  - Documents, chunks, embeddings, questions, answers.
- Ingestion pipeline:
  - Website/docs + GitHub connectors.
- RAG engine:
  - Chunking, retrieval, answer composition.
- `POST /v1/ask` API (single-tenant initially).
- Docs "Ask AI" widget (JS snippet).
- Basic analytics:
  - Question log.
  - Answer success/failure markers.
- Pulser agent definition:
  - `DocsAIEngineer` agent registered via Pulser SDK.

### 2.2 Workstreams

1. **Data & Schema**
   - Define `documents`, `document_chunks`, `embeddings`, `questions`, `answers` tables.
   - Apply Supabase migrations (SQL).

2. **Connectors (MVP)**
   - Website/docs crawler (sitemap-based).
   - GitHub connector (targeted repo + path).

3. **RAG Engine**
   - Chunking pipeline.
   - Embedding + retrieval layers.
   - Answer composer with citations.

4. **API & SDK**
   - Node/TS API server or Edge Function(s).
   - `POST /v1/ask` endpoint.
   - Minimal TS SDK for internal use.

5. **Docs Widget**
   - React widget.
   - JS snippet integration for docs site.
   - Basic UI states (loading, answer, error).

6. **Pulser Integration**
   - Pulser SDK installed and configured.
   - Docs AI agent defined in YAML, with skills:
     - `answer_question_from_docs`.
   - Internal routing from Pulser workflows to `/v1/ask`.

7. **Internal Dogfooding**
   - Deploy to internal docs first.
   - Collect early feedback and misfires.

---

## 3. Phase 2 – Multi-Surface & Connectors

**Objective**
Expand from a single docs widget to multiple surfaces and knowledge sources.

### 3.1 Deliverables

- Additional connectors:
  - Notion.
  - Confluence.
  - Google Drive.
  - Zendesk or equivalent.
- In-product assistant variant.
- Support-ticket deflector variant.
- Internal assistant (Slack/Discord bot).
- Enhanced analytics:
  - Surface-based metrics.
  - Low-confidence cases surfaced.

### 3.2 Workstreams

1. **Connectors**
   - Notion, Confluence, GDrive, Zendesk ingestion.
   - Per-connector sync schedule and error handling.

2. **In-Product & Deflector Widgets**
   - Modify core widget for:
     - In-product context (route, feature).
     - Support deflector flow (pre-ticket form).

3. **Internal Assistant**
   - Slack bot:
     - `/docsai` command.
   - Optional Discord bot.

4. **RAG Improvements**
   - Source weighting and filters (internal vs external).
   - Confidence threshold tuning.

5. **Analytics**
   - Per-surface breakdown (docs, product, support, internal).
   - Deflection metrics for support surfaces.

6. **Pulser Enhancements**
   - Add skills for:
     - `analyze_question_log`.
     - `suggest_doc_changes`.
   - Expose agent to other Pulser workflows.

---

## 4. Phase 3 – Enterprise & Deep Analytics

**Objective**
Harden the platform for multi-tenant, security-conscious deployments and deepen analytics.

### 4.1 Deliverables

- RBAC + SSO integration.
- PII masking in ingestion.
- Tenant isolation (RLS or per-DB).
- Advanced analytics dashboard:
  - Topics, gaps, product areas.
- Evaluation test harness and regression testing.

### 4.2 Workstreams

1. **Security & Tenancy**
   - RBAC roles.
   - SSO integration (OAuth, optional SAML).
   - Finalized tenancy model (RLS or separate DBs).

2. **Data Protection**
   - PII detection and masking on ingestion.
   - Configurable redaction policies.

3. **Analytics**
   - Topic clustering and themes.
   - Gap reports per product/module.
   - Export capabilities.

4. **Evaluation Framework**
   - Seed test question set.
   - Automated evaluation pipeline:
     - Retrieval quality.
     - Answer quality metrics.

5. **Pulser & Observability**
   - Pulser-level instrumentation for Docs AI.
   - Expose metrics for monitoring (e.g., latency, error rate).

---

## 5. Milestones

- **M1 – RAG Core Online**
  - API + schema + basic retrieval running against seeded docs.

- **M2 – Docs Widget Live (Internal)**
  - Docs widget embedded on internal docs, used by InsightPulse team.

- **M3 – Multi-Surface Beta**
  - In-product and support widgets enabled.
  - Slack internal assistant available.

- **M4 – Enterprise Ready**
  - RBAC, SSO, PII masking, and tenant isolation complete.

- **M5 – Analytics & Evaluation**
  - Analytics dashboard and evaluation pipeline operational.

---

## 6. Stack Summary

- **Backend**
  - Supabase (Postgres + pgvector + Storage).
  - Supabase Edge Functions / Node backend for API.
  - Pulser SDK for agent orchestration.

- **Frontend**
  - Next.js/React + Tailwind for dashboard.
  - Widget code packaged as embed script.

- **Models**
  - Primary providers: OpenAI, Anthropic, others via env configuration.
  - Routing logic in a single abstraction layer.

---

## 7. Assumptions

- Existing InsightPulse docs are accessible and crawlable.
- Supabase + Pulser infrastructure is already available or will be provisioned in parallel.
- LLM provider access (keys, quotas) is available for development and initial production.

---

## 8. Exit Criteria per Phase

**Phase 1 Exit Criteria**

- Docs widget live on at least one InsightPulse product docs site.
- ≥ 200 internal questions answered.
- RAG retrieval running via Supabase and pgvector.

**Phase 2 Exit Criteria**

- At least two additional surfaces live (e.g., in-product + Slack).
- Connectors syncing from at least two internal sources (e.g., Notion + Confluence).
- Deflection metrics visible in dashboard.

**Phase 3 Exit Criteria**

- SSO configured for at least one identity provider.
- Tenant isolation verified via tests.
- Analytics dashboard with actionable gap reports.
- Evaluation harness running on every major engine change.
