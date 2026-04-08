# Tasks: Odoo Copilot

## Epic 0 — Stage 3 Azure Wiring (Completed 2026-03-23)

- [x] Deploy gpt-4.1 model contract to oai-ipai-dev
- [x] Deploy text-embedding-ada-002 for vector embeddings
- [x] Create odoo-docs-kb index (vector-enabled, HNSW cosine, 1536d)
- [x] Seed 26 Odoo doc chunks with embeddings
- [x] Assign RBAC: project identity → Search Reader + OpenAI User
- [x] Assign RBAC: endpoint identity → Search Reader + OpenAI User
- [x] Create Foundry connection: srch-ipai-dev-connection (CognitiveSearch)
- [x] Create Foundry connection: oai-ipai-dev-connection (AzureOpenAI)
- [x] Verify ipai-copilot-endpoint scoring URI operational
- [x] Wire ipai-copilot-gateway env vars to gpt-4.1
- [x] Pass retrieval smoke test (grounded results, score ≥ 3.0)
- [x] Update SSOT: foundry_stage3.yaml, models.yaml, diva_copilot.yaml
- [x] Update AI_RUNTIME_AUTHORITY.md with Stage 3 completions

## Epic 0.1 — Stage 3 Marketplace Readiness (Not Started)

- [ ] Create Teams/M365 app package manifest
- [ ] Create formal evaluation pack with pass/fail quality thresholds
- [ ] Create privacy/data handling documentation
- [ ] Prepare Partner Center submission assets
- [ ] Establish SLO baseline (latency, availability, error rate)
- [ ] Expand Odoo docs corpus: 26 → 7000+ chunks via full documentation crawl
- [ ] Wire Entra identity (app registration + OIDC flow)
- [ ] Enable write actions (flip config flag) — requires eval pack + SLO first

## Epic 1 — Copilot Core

- [ ] Unified gateway entrypoint
- [ ] Auth / role resolution (Entra → Odoo user mapping)
- [ ] Context assembly (user, company, permissions, recent activity)
- [ ] Skill registry (discovery, routing, version tracking)
- [ ] Run logging / artifact storage
- [ ] Approval / escalation hooks
- [ ] Channel adapters (Odoo UI, Teams, Telegram, email)

### Validation
- [x] Python compile check passes
- [x] SSOT cross-reference validation passes
- [x] XML parse validation passes
- [ ] Install smoke test on Odoo 18 (requires devcontainer)
- [ ] Live agent resolution test (requires Azure access + API endpoint)
- [ ] Foundry evaluation runs (requires Azure access)

## Epic 0.7 — Compliance Rule Library
- define check/rule object model
- define selection/filter/scope model
- define check outputs and finding schema
- define lifecycle and versioning rules

## Epic 0.8 — Scenario Runner
- define scenario object model
- support draft/active/disabled lifecycle
- support scheduled and ad hoc runs
- persist run logs, scope, timestamps, and artifacts

## Epic 0.9 — Findings Inbox
- build finding list/detail views
- support comments, attachments, evidence links
- support confidence/risk display
- support assign, suppress, close, and escalate actions

## Epic 1.0 — Remediation Templates
- define task template model
- map finding types to remediation playbooks
- support manual and automatic task creation
- support task completion/closure feedback into findings

## Epic 1.1 — Audit & Retention
- build evidence export pack generation
- support period/entity scoped auditor exports
- define archive and retention workflows
- add sensitive-read access logging

## Epic 1.2 — Bootstrap & Landscape
- define system landscape object model
- define entity/calendar/jurisdiction registration
- define scenario enablement workflow
- add readiness/preflight checks

## Epic 1.3 — Security & Access
- define close/control role families
- build role assignment flows
- add authorization-group model
- enforce permission boundaries across define/run/review/approve/archive actions

## Epic 1.4 — Connectivity Registry
- define connection/adaptor registry
- define sync/job status model
- define adapter contracts (read/write/auth/evidence/failure semantics)
- expose connected-system health to operators

## Epic 1.5 — Monitoring & Reliability
- build run monitor
- build connector-health and sync-failure views
- build degraded-mode state handling
- add retry/escalation logging

## Epic 1.6 — Lifecycle & Retention
- build archive/restore flows
- build auditor export center
- define retention/anonymization/purge workflows
- build offboarding checklist with guarded destructive controls
## Epic 0.5 — Data Prep Adapter

- [ ] Define approved Power Query connector patterns
- [ ] Define connection credential, gateway, and privacy handling contract
- [ ] Define reusable finance/ERP transformation templates
- [ ] Map shaped outputs into Odoo Copilot context packs and downstream analytics

## Epic 0.6 — Analytics Mirror Adapter

- [ ] Identify candidate mirrored sources (Odoo PG, Supabase, external)
- [ ] Define Fabric Mirroring source/target topology
- [ ] Define mirrored database monitoring and alerting contract
- [ ] Expose replication status, lag, and failures to admin/operator observability
- [ ] Connect mirrored outputs to analytics/reporting skills without bypassing Odoo authority

## Cross-Cutting

- [ ] SSOT agent contract YAML
- [ ] Mode-to-tool mapping documentation
- [ ] Publish gate schema and enforcement
- [ ] Evaluation freshness policy
- [ ] Adversarial eval suite (unsafe actions, missing evidence, prohibited mutations)
- [ ] Observability: traces, eval outcomes, failure paths

## Epic 2.0 — Sub-Agent Registry

- [ ] Sub-agent registration model (domain, capabilities, tools, policy)
- [ ] Routing logic (intent + model/view + domain → sub-agent)
- [ ] Sub-agent response rendering in Odoo UI
- [ ] Sub-agent lifecycle (enable, disable, version)

## Epic 2.1 — project_copilot Sub-Agent

- [ ] Project dashboard summarization entry point
- [ ] Milestone/risk context builder
- [ ] Profitability interpretation context builder
- [ ] Advisory-only response handling (no project mutation)
- [ ] Eval scaffold from OpenAI Academy product pack

## Epic 2.2 — taxpulse_ph Integration

- [ ] Wire `spec/tax-pulse-sub-agent/` into sub-agent registry
- [ ] Tax/compliance entry points in finance surfaces
- [ ] Advisory-only BIR guidance (Release 1)
- [ ] Eval scaffold from OpenAI Academy finserv pack + BIR test sets

## Epic 2.3 — finance_reconciliation Sub-Agent

- [ ] GL/intercompany context builder
- [ ] Variance-analysis context builder
- [ ] Collections context builder
- [ ] Escalation/routing metadata
- [ ] Eval scaffold from Microsoft Copilot Finance benchmarks
