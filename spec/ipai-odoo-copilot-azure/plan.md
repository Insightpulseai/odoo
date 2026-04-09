# Implementation Plan: Odoo Copilot

## Stage 3 — Azure Foundry Wiring (Completed 2026-03-23)

Execution order (strict sequence):

1. **Model contract** — Deploy `gpt-4.1` to `oai-ipai-dev` (10 TPM Standard) ✅
2. **Retrieval index** — Create `odoo-docs-kb` in `srch-ipai-dev` (26 chunks, HNSW 1536d cosine) ✅
3. **RBAC** — Assign Search Index Data Reader + Cognitive Services OpenAI User to project + endpoint identities ✅
4. **Foundry connections** — Create CognitiveSearch + AzureOpenAI connections in `proj-ipai-claude` ✅
5. **Foundry endpoint** — Verify `ipai-copilot-endpoint` live (scoring URI operational) ✅
6. **Gateway wired** — `ipai-copilot-gateway` env vars → `gpt-4.1` via `ipai-copilot-resource` ✅
7. **Smoke test** — Grounded retrieval returns ranked results (score 7.33) ✅

### Stage 3 remaining (Marketplace Readiness)

- Teams/M365 app package
- Formal evaluation pack with pass/fail thresholds
- Privacy/data handling documentation
- Partner Center submission assets
- SLO baseline
- Full Odoo docs corpus expansion (26 → 7000+)

## Phase B2 — Compliance Core
- implement rule/check registry
- implement scenario model and lifecycle states
- implement run execution and monitoring
- implement finding model and review inbox

## Phase C2 — Remediation and Triage
- implement remediation task templates
- implement manual and automatic task generation
- implement confidence / impact / urgency scoring
- implement suppress / close / escalate states

## Phase D2 — Audit and Governance
- implement evidence pack generation
- implement auditor-scoped exports
- implement retention, anonymization, and archive controls
- implement access logging for sensitive reviews

## Phase A3 — Administrative Plane Foundations
- implement system landscape registry
- implement bootstrap readiness checks
- implement close/control role model and authorization groups
- implement adapter/connection registry

## Phase C3 — Operational Reliability
- implement connector health monitoring
- implement sync/job status tracking
- implement degraded-mode behavior and alerts
- implement business-log visibility and retry workflows

## Phase D3 — Lifecycle Governance
- implement archive/restore workflows
- implement auditor export flows
- implement retention/anonymization/purge controls
- implement offboarding checklist and guarded destructive actions

## Phase B1 — Data Preparation Foundation

- Define governed Power Query connection patterns
- Define reusable transformation/dataflow patterns for finance and ERP reporting
- Standardize connector auth, gateway, and privacy-level handling
- Map Odoo Copilot skills to shaped datasets rather than raw source coupling

## Phase C1 — Analytics Mirroring Foundation

- Define which sources should be mirrored vs queried directly
- Stand up Fabric Mirroring patterns for analytics replication
- Define mirrored-database monitoring, failure handling, and latency review
- Expose mirrored analytics only through governed Odoo Copilot/reporting surfaces

## Model Baseline

- **Primary model:** `gpt-5.2`
- **Escalation model:** `gpt-5.4`

`gpt-5.2` is the default internal beta Copilot model due to better throughput/cost balance for always-on product use. `gpt-5.4` is reserved for higher-stakes reasoning, policy-heavy responses, and code-sensitive operational surfaces.

**Note:** `gpt-4.1` is the current deployed model. Migration to GPT-5 tier as deployments become available.

## Go-Live Foundry Tool Selection

### First-wave enabled tools

- Foundry MCP Server (preview)
- GitHub
- Vercel
- Azure DevOps MCP Server (preview)
- Azure Managed Grafana
- Azure MCP Server (optional)

### Explicitly deferred

- Work IQ suite (Mail, Calendar, Teams, SharePoint, Word, OneDrive, Copilot)
- Microsoft 365 Admin Center
- Dataverse, Pipedream, ClickUp, Atlassian
- Broad remote MCP sprawl

First-wave tools are limited to code/repo/deploy/ops context. Broader Microsoft 365 action surfaces are out of scope for initial go-live.

## Foundry Implementation Sequence

Staged template adoption for authenticated Odoo Copilot:

- **Stage 1:** `Get started with AI agents` — controlled actions, trusted-user scope, read-only advisory
- **Stage 2:** `Build your conversational agent` — deterministic workflows, human-controllable routing
- **Stage 3:** `Deploy your AI application in production` — security, observability, environment hardening

### Explicitly deferred (not first-wave go-live)

- `Multi-Agent Workflow Automation` — until eval pack, docs corpus, SLO baseline, and write gates are policy-safe
- `Create a multi-agent Release Manager Assistant` — until single-agent surfaces are stable
- `Agentic applications for unified data foundation` — until data intelligence lane is mature

## Foundry Project Baseline

Confirmed Foundry project baseline:
- project: `ipai-copilot`
- parent resource: `ipai-copilot-resource`
- resource group: `rg-data-intel-ph`
- region: `eastus2`
- project endpoint: `https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot`

## Connected Resources Strategy

The Foundry project uses attachable connections.
Do not assume Azure AI Search, Azure OpenAI, Cosmos DB, Storage, Application Insights, Bing grounding, or Fabric are already attached unless explicitly verified.

For MVP:
- attach only the minimum required connections
- keep preview connections (Fabric) off the critical path by default
- document every required project connection explicitly before implementation depends on it

## Runtime Rules

- Microsoft Foundry is the shared runtime for production use
- Foundry Local is dev/offline/prototyping only — not shared production
- Azure Document Intelligence is the default extraction layer for finance documents
- External SaaS/vendor capabilities are exposed only through adapters behind Odoo Copilot
- All skills share the unified gateway, context assembly, and logging infrastructure
- Power Query is the default Microsoft-native data shaping substrate for reusable prep flows
- Fabric Mirroring is the default Microsoft-native near-real-time analytics replication path where mirroring is justified
- Neither Power Query nor Fabric Mirroring changes the Odoo transactional authority model
- compliance findings, runs, and remediation tasks are first-class persisted objects
- scheduled and ad hoc scenario execution must use the same evidence and logging model
- all state-changing remediation actions must resolve back to Odoo records/workflows
- bootstrap readiness must be validated before production scenario execution
- admin-plane actions must be role-gated and audit-logged
- connector and degraded-mode state must be observable independently from scenario state
- archive/purge/offboarding actions require explicit governed workflows

## Evaluation Gates (per phase)

- Phase A: gateway health, auth flow, logging completeness
- Phase B: hallucination resistance, evidence requirements, escalation behavior per skill
- Phase C: accuracy on reconciliation/collections/tax test sets, fail-closed behavior
- Phase D: end-to-end close workflow coverage, audit trail completeness

## Foundry Integration References

When implementing runtime integration, reference these patterns:

| Reference | Purpose |
|-----------|---------|
| `microsoft-foundry/foundry-agent-webapp` | Entra + Agent web app pattern (TypeScript, auth flow, agent lifecycle) |
| `microsoft-foundry/mcp-foundry` | MCP Server integration pattern (Python, tool registration, Foundry runtime) |
| `microsoft-foundry/Foundry-Local-Lab` | Local dev/prototyping only — not shared production |
| `microsoft-foundry/foundry-samples` | Sample patterns for agent scenarios |
| Azure resource `data-intel-ph` in `rg-data-intel-ph` | Document Intelligence for finance document extraction |

## Sub-Agent Phasing

### Phase E1 — project_copilot Sub-Agent
- Define project context builder (dashboard, milestones, profitability)
- Implement read-only advisory responses for project Q&A
- Wire to Odoo Project model context (`project.project`, `project.task`)
- Evaluation: OpenAI Academy product pack scenarios

### Phase E2 — taxpulse_ph Integration
- Wire `spec/tax-pulse-sub-agent/` into the sub-agent registry
- Implement tax/compliance entry points in finance surfaces
- Advisory-only BIR guidance in Release 1
- Evaluation: OpenAI Academy finserv pack + BIR-specific test sets

### Phase E3 — finance_reconciliation Sub-Agent
- Define GL/intercompany context builder
- Implement variance-analysis and collections context builders
- Wire escalation/routing metadata
- Evaluation: Microsoft Copilot Finance benchmark scenarios
