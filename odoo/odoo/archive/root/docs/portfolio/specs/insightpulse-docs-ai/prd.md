# PRD – InsightPulse Docs AI – Technical Knowledge Assistant

## 1. Overview

### 1.1 Product Summary

InsightPulse Docs AI is a **model-agnostic AI assistant** that answers technical questions about InsightPulse products using existing documentation and support knowledge.

It provides:

- A unified "Ask AI" experience across:
  - Documentation sites.
  - In-product UI.
  - Support portals and internal chat.
- A RAG engine optimized for **technical content and product usage**.
- Analytics to identify documentation gaps and product friction.

All orchestrated via the **Pulser SDK** as a first-class agent.

---

## 2. Problem Statement

### 2.1 Current Pain

- Product and API docs are extensive but hard to navigate under time pressure.
- Support teams handle repetitive Level-1 questions:
  - "How do I…?"
  - "Which endpoint do I use for…?"
  - "Why is this error happening?"
- PMs and technical writers lack clear telemetry on:
  - Which parts of the product are confusing.
  - Where documentation is missing or unclear.

### 2.2 Why Now

- RAG and LLMs are mature enough to power reliable technical assistants.
- InsightPulse already has multiple products, docs, and internal notes spread across:
  - Websites, GitHub, wikis, ticketing tools.
- A unified AI assistant reduces support load and creates a defensible product capability.

---

## 3. Goals and Non-Goals

### 3.1 Goals

1. Provide **high-accuracy answers** to technical product questions using existing content.
2. Deploy a **single RAG brain** across:
   - Docs widget.
   - In-product UI.
   - Support deflection.
   - Internal assistant.
3. Provide **analytics** to:
   - Identify documentation gaps.
   - Track question volume, deflection, and CSAT.
4. Ensure **enterprise-grade security**:
   - Tenant isolation.
   - RBAC + SSO.
   - PII masking.

5. Integrate with **Pulser SDK**:
   - Docs AI is a named agent with YAML-defined skills and routing.
   - Existing Pulser workflows can call Docs AI as a service.

### 3.2 Non-Goals

- General-purpose conversational AI or web search.
- Full replacement for ticketing or CRM.
- Autonomously changing product configuration or infrastructure.

---

## 4. Target Users

1. **External Users / Customers (Dev & Power Users)**
   - Need quick answers while integrating or using InsightPulse products.

2. **Support & Customer Success**
   - Want to reduce repetitive tickets.
   - Need strong answers and clean handoff when escalation is required.

3. **Product Managers & Technical Writers**
   - Need insights into product friction.
   - Use analytics to prioritize content updates.

4. **Internal Engineering & Ops**
   - Use internal assistant for querying runbooks, ADRs, error codes, and troubleshooting docs.

---

## 5. Use Cases

### 5.1 External Docs Widget

- User on docs page clicks "Ask AI".
- Asks: "How do I authenticate with the Insights API in Python?"
- AI responds with:
  - A concise explanation.
  - Code snippet.
  - Source citations (docs URLs).
- User copies code snippet and integrates.

### 5.2 In-Product Helper

- User on settings page sees "Ask AI about this page".
- Context (route + feature) sent to Docs AI.
- Asks: "What happens if I change the data retention period?"
- AI responds referencing relevant docs and warnings.

### 5.3 Support Ticket Deflector

- User opens "Contact Support" page.
- Before the form, they see "Ask AI".
- Ask: "Why is my webhook returning 401?"
- AI suggests:
  - Potential misconfigurations.
  - Links to troubleshooting docs.
- If unresolved, user continues to submit ticket; AI conversation is attached.

### 5.4 Internal Assistant

- Support engineer in Slack types:
  - `/docsai summarize recent integration issues with Webhooks`
- AI returns:
  - Aggregated FAQ-style answers based on docs + recent question themes.

---

## 6. Functional Requirements

### 6.1 Data Connectors

**FR-1**: Support connectors for:

- Public:
  - Website / docs (sitemap-driven + URL allowlist).
  - GitHub repositories.
  - Markdown/Docusaurus-like docs.
- Internal:
  - Notion.
  - Confluence.
  - Google Drive (Docs, Sheets, PDFs).
  - Zendesk or equivalent help center.

**FR-2**: Ingestion Pipeline

- Scheduled syncs (configurable per connector).
- Delta detection via hashing or last-modified timestamps.
- Error handling and retry with alerting.

**FR-3**: Content Normalization

- Convert HTML/Markdown/PDF to a unified document format:
  - `id`, `title`, `url`, `body`, `headings`, `tags`, `source`, `tenant_id`, `access_level`.

### 6.2 RAG Engine

**FR-4**: Chunking

- Heading-aware chunking (sections).
- Preserve code blocks and lists.
- Configurable max tokens per chunk.

**FR-5**: Retrieval

- Hybrid search:
  - Dense vector retrieval (pgvector).
  - Sparse keyword retrieval (BM25 or full-text search).
- Ranking scores to select top-k chunks.

**FR-6**: Answer Generation

- Use LLM (model-agnostic) to generate answers from retrieved chunks.
- Always include:
  - Citations list.
  - Short title or doc reference.
- Provide a confidence score per answer.

**FR-7**: Escalation

- When confidence below threshold:
  - Ask clarifying question **or**
  - Suggest escalation and log as unresolved.

### 6.3 Deployment Surfaces

**FR-8**: Docs Widget

- Embeddable JS snippet:
  - Loads React-based chat widget.
  - Sends context (current URL, path, meta tags) along with user query.
- Customizable branding (colors, logo, position).

**FR-9**: In-Product Assistant

- Similar widget but integrated into product UI.
- Accepts additional context (feature flags, org plan, etc.).

**FR-10**: Support Deflector

- Widget variant optimized for help center and ticket pages.
- Explicit "Did this solve your issue?" capture.

**FR-11**: Internal Assistant

- Slack/Discord bot:
  - Command-based (`/docsai <question>`).
  - Can fetch internal-only sources where allowed by RBAC.

**FR-12**: Public API + SDK

- `POST /v1/ask` endpoint:
  - Input: `question`, `tenant_id`, `user_id`, `surface`, optional `source_filter`.
  - Output: `answer`, `citations`, `confidence`, `metadata`.
- TypeScript SDK for web apps.

### 6.4 Analytics & Insights

**FR-13**: Logging

- Log every interaction:
  - `tenant_id`, `user_id` (if available), `surface`, `question`, `answer_id`, `confidence`, `citations`, `timestamp`, `feedback`.

**FR-14**: Dashboard

- Metrics:
  - Total questions by surface and time.
  - Deflection rate.
  - Top queries.
  - Queries with low confidence or no good answer.
- Gap view:
  - List of questions with poor coverage.
  - Suggest docs and owners to update.

### 6.5 Pulser Integration

**FR-15**: Pulser Agent Definition

- Define **DocsAIAgent** in Pulser YAML:
  - Skills for:
    - `answer_question_from_docs`.
    - `analyze_question_log`.
    - `suggest_doc_changes`.
  - Model routing configuration.

**FR-16**: Pulser SDK Usage

- Edge Functions and backend services must use **Pulser SDK** to:
  - Invoke Docs AI.
  - Log agent-level telemetry.
  - Orchestrate multi-step flows (e.g., RAG → evaluation → analytics).

---

## 7. Non-Functional Requirements

**NFR-1**: Latency
- p95 < 3 seconds for standard queries on docs and product pages.

**NFR-2**: Availability
- Target 99.9% uptime for core `ask` API.

**NFR-3**: Multi-Tenancy
- Tenant isolation for:
  - Data (documents, embeddings).
  - Config (connectors, model settings).
  - Analytics (no cross-tenant visibility).

**NFR-4**: Security

- RBAC:
  - `Viewer` (analytics read-only).
  - `Admin` (manage connectors, settings).
  - `SuperAdmin` (internal).
- SSO: OAuth (Google, Microsoft) plus optional SAML.
- PII masking on ingestion where possible.

**NFR-5**: Observability

- Structured logs for:
  - Retrieval performance.
  - Model latencies.
- Metrics exposed to monitoring (e.g., Prometheus-compatible).

---

## 8. Dependencies

- Supabase project (Auth, Postgres, pgvector, Storage).
- LLM providers (OpenAI, Anthropic, others via configuration).
- Pulser SDK and Pulser agent registry.
- Frontend framework (Next.js/React + Tailwind).

---

## 9. Release Phases

### Phase 1 – RAG Core + Docs Widget (MVP)

- Website/docs connector.
- RAG engine with vector + keyword retrieval.
- Docs widget.
- Basic analytics.

### Phase 2 – Multi-Surface + Internal Assistant

- In-product widget.
- Support deflector.
- Slack/Discord internal assistant.
- Expanded connectors (Notion, Confluence, Drive, Zendesk).

### Phase 3 – Enterprise & Deep Analytics

- RBAC + SSO.
- PII masking and security hardening.
- Advanced analytics (themes, product-area segmentation).
- Evaluation harness and regression test suite.

---

## 10. KPIs / Success Metrics

- ≥ 60% of Level-1 questions answered by AI without ticket creation (Phase 2).
- ≥ 80% CSAT for AI answers (thumbs and optional comments).
- ≥ 30% reduction in average time-to-answer for supported topics.
- ≥ 10 actionable documentation gaps identified and fixed per quarter.
- Stable performance under 100k+ questions/month per tenant.

---

## 11. Risks and Mitigations

- **Risk**: Hallucinations on incomplete content.
  **Mitigation**: Conservative confidence thresholds, clear disclaimers, escalation paths, gap logging.

- **Risk**: LLM provider outages or changes.
  **Mitigation**: Model-agnostic routing, multi-provider fallback.

- **Risk**: Connector rate limits or changes in external APIs.
  **Mitigation**: Per-connector rate-limiting and monitoring; configurable sync strategies.

- **Risk**: Overload of analytics noise.
  **Mitigation**: Theme clustering and prioritization based on frequency and impact.

---

## 12. Open Questions (to be resolved before GA)

1. Exact multi-tenant pattern within Supabase (separate DBs vs shared DB with RLS + tenant_id).
2. Minimum connector set required for initial internal dogfooding.
3. Default model provider stack for InsightPulse internal usage vs external tenants.
4. How to version and roll out changes to chunking and retrieval without confusing analytics.
