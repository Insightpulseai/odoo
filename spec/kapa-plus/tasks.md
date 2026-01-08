# Tasks — Kapa-Plus

## Backlog (ordered)

### 1) Data Layer
- [x] Create `spec/kapa-plus/{constitution,prd,plan,tasks}.md`
- [ ] Implement chunk store schema (source, version, hash, ACL, provenance)
- [ ] Add RLS policies for tenant isolation

### 2) Connectors
- [ ] GitHub Files connector (path allowlist, markdown parsing, code blocks)
- [ ] OpenAPI connector (endpoints → searchable docs)
- [ ] Web crawler connector (sitemap + HTML extraction)
- [ ] PDF/Docs connector (optional)

### 3) Retrieval & Ranking
- [ ] Hybrid retrieval + reranker interface
- [ ] Per-source boosts and freshness weighting
- [ ] Filters (tenant/source/path/tags/recency)

### 4) Answering
- [ ] Strict citation renderer + evidence panel
- [ ] Confidence scoring + escalation hooks
- [ ] Streaming responses

### 5) Feedback Loop
- [ ] Feedback pipeline + doc-gap detector rules
- [ ] Auto-create GitHub issue/PR suggestions
- [ ] Unresolved query clustering

### 6) Channels
- [ ] Docs widget SDK (React) + embed snippet
- [ ] Public API (auth, query, streams, analytics events)
- [ ] MCP registry + proxy + policy engine
- [ ] Slack bot surface

### 7) Actions (Agentic)
- [ ] Action policies: read, propose, execute
- [ ] Approval workflow (propose → approve → execute)
- [ ] Audit logging for all tool calls

### 8) Admin & Analytics
- [ ] Analytics dashboard + deflection metrics
- [ ] RBAC implementation
- [ ] Audit log viewer

### 9) Quality & Testing
- [ ] Eval harness (golden set, regression, CI gate)
- [ ] Load tests (latency p95 targets)
- [ ] Security review (RLS, PII, secrets)

### 10) Documentation
- [ ] Integration guides for each connector
- [ ] Deployment documentation
- [ ] API reference (OpenAPI)
