# PRD — Kapa-Plus (Improved Knowledge Support AI)

## 1. Overview
Kapa-Plus is a "Support + Docs + In-product" AI assistant platform that turns technical knowledge into verified answers and safe actions.

## 2. Goals
- Deflect support with **high-precision, cited answers**.
- Provide **in-product agentic workflows** (read-only by default; write-actions gated).
- Surface **documentation gaps** and auto-open PRs/issues.
- Offer **MCP servers** per workspace for IDE/agent consumption.

## 3. Non-goals
- Not a general chat app.
- Not a generic vector DB product.
- Not an LLM training platform.

## 4. Personas
- DevRel / Docs lead (wants deflection + doc gap reports)
- Support lead (wants lower tickets + safe escalation)
- Product engineer (wants embed + API + actions)
- Security/IT (wants RBAC, audit, data controls)

## 5. Core UX surfaces
1. Docs widget (web)
2. In-product panel (SDK)
3. Slack/Discord bot
4. Ticketing sidebar (Zendesk/Intercom)
5. API + MCP server

## 6. Key features

### 6.1 Sources & Ingestion
- GitHub files/issues/discussions/PRs; OpenAPI; web crawl; PDF/Docs; Slack exports.
- Versioned indexing: `source_id@version` with hash-based chunk IDs.
- Re-ingest scheduling + webhooks.

### 6.2 Retrieval & Ranking
- Hybrid retrieval (BM25 + embeddings).
- Reranker stage (configurable).
- Per-source boosts and freshness weighting.
- "Show evidence" panel with chunk provenance.

### 6.3 Answering
- Strict citation mode (default).
- Confidence scoring + "ask a human" escalation when below threshold.
- Streaming responses + inline quoted snippets (short, compliant).

### 6.4 Actions (Agentic)
- MCP tool registry with org-level allowlists.
- Action policies: `read`, `propose`, `execute`.
- "Propose" mode generates a plan + diff/command preview; execution requires approval.

### 6.5 Feedback & Doc Gap Loop
- User feedback buttons: helpful / not helpful + reason.
- Auto-create GitHub issue/PR suggestion when:
  - no sources found,
  - conflicting sources,
  - repeated unanswered questions.

### 6.6 Analytics
- Deflection rate, top questions, broken intents, source coverage, time-to-answer.
- Per-surface reporting (docs vs slack vs in-app).
- Regression evals on golden Q/A sets.

## 7. Admin & Security
- RBAC: org admin, content admin, agent admin, analyst.
- Data controls: per-source access, PII redaction, retention windows.
- Full audit logs: ingestion runs, retrieval traces, tool calls, approvals.

## 8. Integrations
- GitHub, GitBook, ReadMe, Docusaurus, Zendesk, Intercom, Slack, Discord.
- Webhooks + OpenAPI + MCP.

## 9. Success metrics
- ≥ 30% ticket deflection in 60 days
- ≥ 70% "helpful" rating on answered questions
- < 5% answers without citations (in strict mode)
- < 1% unsafe action attempts passing policy gates
