# Tasks — Pulser Assistant: Experience Layer

## Phase 1 — UI Contracts

- [ ] Define PulserChatSurface contract (streaming protocol, message format, error handling)
- [ ] Define PulserWorkbench contract (formation display, capability enablement, system status)
- [ ] Define PulserGroundingConsole contract (source list, pipeline status, refresh triggers)
- [ ] Define PulserEvaluationViewer contract (eval results, trace drill-down, quality metrics)
- [ ] Define PulserApprovalSurface contract (checkpoint context, approve/reject/modify, audit trail)
- [ ] Define PulserAdminShell contract (interactive agent testing, trace inspection, not production)

## Phase 2 — Production Chat

- [ ] Implement production Ask Pulser chat widget with Foundry Agent Service backend
- [ ] Implement streaming message display (SSE/WebSocket)
- [ ] Implement Entra ID authentication for chat
- [ ] Integrate with existing ipai-landing site (insightpulseai.com)
- [ ] Add production telemetry (usage metrics, error rates)

## Phase 3 — Operator Surfaces

- [ ] Implement operator workbench (formation management, capability enablement)
- [ ] Implement grounding management console (source registration, pipeline status, manual refresh)
- [ ] Implement evaluation viewer (eval results display, trace drill-down)
- [ ] Wire all operator surfaces to platform registry APIs

## Phase 4 — Preview and HITL

- [ ] Implement preview chat surface with visual distinction (PREVIEW banner)
- [ ] Implement environment switching (preview ↔ production) for operators
- [ ] Implement HITL approval surface for workflow checkpoints
- [ ] Wire approval surface to agent platform checkpoint API

## Phase 5 — Internal Tooling

- [ ] Build admin/debug shell (DevUI-like interactive agent testing)
- [ ] Separate admin shell from production routing (internal-only access)
- [ ] Add trace inspection UI in admin shell
- [ ] Add quick-test capability for individual agent/workflow templates

## Verification Gates

- [ ] Production chat operational on insightpulseai.com
- [ ] Preview chat visually distinct from production
- [ ] Operator workbench displaying formation status
- [ ] Grounding console showing source/pipeline health
- [ ] At least one HITL approval flow operational
- [ ] Admin shell available (not publicly routed)
- [ ] All surfaces authenticated via Entra ID

### Phase W5 — Tax Guru Web Surfaces

- [ ] W5.1 — Implement PulserTaxDecisionCard component (treatment summary, confidence score, evidence refs, escalate/approve/open actions)
- [ ] W5.2 — Implement PulserTaxExceptionQueueView (exception list, severity filter, bulk assign/escalate/resolve)
- [ ] W5.3 — Implement PulserTaxEvidenceView (rule sources, documents, explanation, timestamps, audit export)
- [ ] W5.4 — Add tax preview/admin shell for testing determination requests against preview rules
- [ ] W5.5 — Add capability-type-aware response rendering to chat surface (informational=evidence, navigational=targets, transactional=confirmation)
