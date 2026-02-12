# Plan — Kapa-Plus

## Architecture
- **Ingestion service**: connectors → normalized docs → chunk store
- **Index service**: hybrid index + reranker
- **Answer service**: retrieval → cite → generate → stream
- **Action service**: MCP proxy + policy engine + approval workflow
- **Analytics service**: events + traces + dashboards

## Milestones

### 1. MVP (4 weeks)
- Docs widget + API
- GitHub files + OpenAPI ingestion
- Hybrid retrieval + citations
- Feedback capture

### 2. Agentic (4 weeks)
- MCP registry + propose/execute gating
- Slack bot + basic actions (create issue, draft PR)

### 3. Enterprise (4 weeks)
- RBAC, audit exports, retention controls
- Zendesk/Intercom sidebar
- Eval harness + regression gates in CI

## Risks
- Hallucinations → mitigated by strict citations + confidence gating
- Source drift → mitigated by versioned ingestion + freshness weighting
- Tool misuse → mitigated by allowlists + approval + audit trails
