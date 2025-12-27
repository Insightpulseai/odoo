# InsightPulse Docs AI – Constitution

## 1. Purpose

InsightPulse Docs AI is a **production-grade AI assistant** that reliably answers technical questions about InsightPulse products using existing documentation, support content, and internal knowledge.

It is designed to:

- Reduce support load and time-to-answer for technical questions.
- Improve documentation quality via analytics and gap detection.
- Provide a consistent "Ask AI" experience across docs, product UI, and internal tools.

This constitution defines the **non-negotiable principles, boundaries, and priorities** for all future work on this product.

---

## 2. Product Principles

1. **Accuracy over Cleverness**
   - The assistant must prioritize **correct, source-grounded answers** with citations.
   - Hallucinations are treated as critical bugs, not acceptable tradeoffs.

2. **Docs as Source of Truth**
   - All answers are grounded in the **official knowledge base** (docs, runbooks, ADRs, tickets).
   - When the content is missing or ambiguous, the assistant:
     - Acknowledges limitations.
     - Proposes follow-up questions or human escalation.
     - Logs the gap for analytics.

3. **RAG First, LLM Second**
   - Retrieval is the primary engine; LLMs are applied as controlled generators.
   - Prompting, chunking, and scoring are tuned for **technical content**, not casual chat.

4. **Model Agnostic, Behavior Stable**
   - The product must remain agnostic to specific LLM providers.
   - Model swaps (OpenAI, Anthropic, etc.) must not materially change:
     - Contract of APIs.
     - UX of surfaces.
     - Security posture.

5. **Multi-Surface, Single Brain**
   - Docs widget, in-product assistant, support deflector, and internal chat are **different faces of the same brain**.
   - All surfaces share:
     - Common retrieval layer.
     - Common analytics and logging.
     - Common security and RBAC policies.

6. **Enterprise-Grade by Default**
   - Security, RBAC, and auditability are first-class concerns, not retrofits.
   - Tenants are fully isolated at data and index levels.

7. **Telemetry-Driven Improvement**
   - Product evolution is driven by:
     - Question logs.
     - Deflection metrics.
     - Gap analytics.
   - Every release must be measurable against defined KPIs.

8. **Pulser-First Orchestration**
   - All agentic workflows are orchestrated via **Pulser SDK** patterns.
   - Docs AI is a first-class Pulser agent with explicit skills and YAML-defined capabilities.

---

## 3. Scope and Boundaries

### 3.1 In Scope (Core)

- RAG-based answering for:
  - Product usage questions.
  - API and SDK questions.
  - Integration and configuration questions.
- Connectors for:
  - Public docs (website, Docusaurus/Markdown, GitHub).
  - Internal docs (Notion, Confluence, Google Drive).
  - Support systems (Zendesk/equivalent).
- Surfaces:
  - Docs "Ask AI" widget.
  - In-product assistant.
  - Support ticket deflector.
  - Internal assistant (Slack/Discord).
  - REST API + JS SDK.
- Analytics and gap detection:
  - Question logs.
  - Coverage and deflection.
  - Doc gaps and themes.

### 3.2 Out of Scope (for now)

- General web search and arbitrary browsing.
- Full ticketing/CRM replacement.
- Automatic large-scale doc rewriting without human review.
- Long-running workflows beyond Q&A (e.g., provisioning, billing ops).

---

## 4. Architecture Guardrails

1. **Data Platform**
   - Primary data backbone: **Supabase (Postgres + Storage + Auth)**.
   - Vector search: `pgvector` in Supabase.
   - Multi-tenant schema pattern (per-tenant or row-level tenancy) must be explicit.

2. **Backend**
   - Core API: TypeScript/Node (e.g., Fastify/NestJS) or equivalent, deployed with:
     - Supabase Edge Functions for latency-critical paths where appropriate.
   - RAG layer:
     - Retrieval: hybrid (BM25 + vector).
     - Chunking: heading-aware, code-block-aware for tech docs.
     - Evaluation harness for regression tests.

3. **Frontend**
   - Docs widget + dashboard: React + Tailwind (Next.js or similar).
   - Widgets must be embeddable via **single JS snippet**.

4. **LLM Orchestration**
   - Model routing is configured via:
     - Environment-level configuration (e.g., `MODEL_PROVIDER`, `MODEL_NAME`).
     - Pulser SDK for defining and managing agent skills.
   - No hard-coded vendor lock-in inside business logic.

5. **Security**
   - SSO (OAuth/SAML) and RBAC for dashboard and internal assistant.
   - Data masking for PII on ingestion where applicable.
   - Strict tenant isolation enforced at the DB and index levels.

---

## 5. Governance and Decision-Making

### 5.1 Product Authority

- **Product Owner** defines:
  - Roadmap, priority, scoping, and success metrics.
- **Tech Lead** defines:
  - Architecture, implementation details, and technical tradeoffs.

Where conflicts arise, Product Owner decides on **"what"** and **"why"**, Tech Lead decides on **"how"**.

### 5.2 Change Management

- All major changes (e.g., new connector, new surface, new LLM provider):
  - Must be reflected in the **PRD** and **plan**.
  - Must include migration or rollout strategy.
  - Must be tested against the regression question set.

---

## 6. Success Definition

InsightPulse Docs AI is considered successful when:

1. It consistently answers >70% of repetitive technical questions without human intervention.
2. It measurably reduces:
   - Level-1 ticket volume.
   - Time-to-answer for common questions.
3. It uncovers and helps close documentation gaps on a rolling basis.
4. It can be deployed for new InsightPulse products with minimal additional engineering effort (connectors + config only).

---

## 7. Glossary

- **RAG**: Retrieval-Augmented Generation.
- **Surface**: Any user-facing entry point to the assistant (widget, bot, etc.).
- **Deflection**: A support question answered by AI without creating a human ticket.
- **Tenant**: A logically isolated customer or product environment.
- **Pulser SDK**: The agent orchestration SDK used to define and execute Docs AI skills and workflows.
