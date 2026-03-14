# Copilot Target-State — PRD

## Problem

The current system has 1 Foundry prompt agent as a seed. Without a governed architecture, growth leads to agent sprawl, copilot-as-workflow-engine anti-patterns, and ungoverned transactional actions.

## Solution

One assistant product backed by a governed multi-role runtime with APIM ingress, Agent Framework orchestration, and domain capability packs.

## Success Criteria

1. Users interact with **one assistant**
2. Chat answers are grounded and safe
3. Complex work routes to correct backend role
4. Writes are isolated and approval-gated
5. APIM fronts production traffic
6. Traces and evals exist for every role
7. Vendor/domain growth happens through packs, not new agents

## Rollout Phases

### Phase 1 — Lock the front door
- Keep `ipai-odoo-copilot-azure` as user-facing
- Attach guardrails, eval datasets, tracing
- Agent remains read-only by default

### Phase 2 — Backend split
- Router workflow (deterministic classification, approval pause/resume)
- Ops runtime (read-only diagnostics, tool/knowledge inspection)
- Actions runtime (smallest approved write scope, evidence + rollback)

### Phase 3 — Capability packs
- BIR Compliance Pack (priority — current tax/compliance goals)
- Document Intake & Extraction Pack (BIR attachments, invoices, receipts)
- Databricks Intelligence Pack
- fal Creative Production Pack
- Marketing Strategy & Insight Pack

### Phase 4 — Production ingress
- APIM AI Gateway in front
- Project client + OpenAI-compatible client
- Internal services private

### Phase 5 — Enterprise workflow rigor
- Simulation mode
- Approval checkpoints via Odoo-native Activities
- Task templates/worklists via project.task
- Export/package review flow
- Channel-aware fallback to richer web surfaces

## Azure Stack Mapping

| Component | Azure Service |
|---|---|
| Front-door agent | Foundry / AI Agent Service |
| Router/Ops/Actions | Agent Framework |
| Knowledge grounding | Azure AI Search / Foundry IQ |
| Document ingestion | Azure AI Document Intelligence |
| Runtime | Azure Container Apps |
| Production ingress | APIM AI Gateway |
| Observability | Foundry Tracing + App Insights |

## Template Reuse Strategy

| Template | Use as |
|---|---|
| Get started with AI agents | Primary starter skeleton |
| RAG chat with Azure AI Search | Knowledge-grounding benchmark |
| Deploy AI app in production | Runtime hardening benchmark |
| Home Banking Assistant / multi-agent | Approval-safe transactional benchmark |
| Multi-modal Content Processing | Document ingestion benchmark |

## Do Not

- Create separate top-level agents per domain/vendor
- Rely on playground configs as production SSOT
- Fine-tune before knowledge/tools/evals work
- Allow direct transactional actions from Advisory surface
