# Odoo Copilot on Azure — Tasks

## T0 — Contracts and Boundaries

- [ ] T0.1 Define capability taxonomy: transactional / navigational / informational
- [ ] T0.2 Define canonical entity map across Odoo / Supabase / Databricks / Plane (ref: `docs/architecture/CANONICAL_ENTITY_MAP.yaml`)
- [ ] T0.3 Define tool approval and allowlist policy
- [ ] T0.4 Define grounding scope and citation rules
- [ ] T0.5 Define identity model: Agent Framework managed identity → Odoo user mapping
- [ ] T0.6 Define audit logging contract: what, where, retention

## T1 — Odoo Tool Layer

- [ ] T1.1 Create `ipai_copilot_gateway` module scaffold
- [ ] T1.2 Create record lookup tools (partner, invoice, expense, project)
- [ ] T1.3 Create approval/action tools (approve, reject, delegate)
- [ ] T1.4 Create deep-link tools (generate Odoo web client URLs)
- [ ] T1.5 Create expense/finance-specific tools (create expense, close worklist)
- [ ] T1.6 Create `ipai_copilot_finance` module with finance tool endpoints
- [ ] T1.7 Create `ipai_copilot_compliance` module with BIR/tax tool endpoints
- [ ] T1.8 Add role-aware authorization parity checks (Agent Framework identity → Odoo permissions)
- [ ] T1.9 Add tool contract tests (request/response schema validation)

## T2 — Shared Contracts

- [ ] T2.1 Create `packages/shared-agent-contracts/` scaffold
- [ ] T2.2 Add typed request/response schemas for all tools
- [ ] T2.3 Add structured output contracts (typed agent responses)
- [ ] T2.4 Add error taxonomy (categories, retry semantics, user-facing messages)
- [ ] T2.5 Add tool versioning strategy

## T3 — Agent Runtime

- [ ] T3.1 Scaffold `agents/odoo-copilot/` with Agent Framework
- [ ] T3.2 Create `packages/tool-odoo/` MCP server
- [ ] T3.3 Create `packages/tool-supabase/` MCP server
- [ ] T3.4 Create `packages/tool-databricks/` MCP server **(optional — defer if Databricks not provisioned)**
- [ ] T3.5 Create `packages/tool-plane/` MCP server
- [ ] T3.6 Add session/state handling (multi-turn conversations)
- [ ] T3.7 Add workflows for multi-step tasks (approval chains, expense lifecycle)
- [ ] T3.8 Add context providers / RAG for document grounding
- [ ] T3.9 Add OpenTelemetry instrumentation (traces, metrics, spans)
- [ ] T3.10 Add citation engine (source tracking for informational answers)

## T4 — Agent Framework Integration

- [ ] T4.1 Configure Agent Framework runtime on Container Apps
- [ ] T4.2 Register all MCP endpoints in Agent Framework tool registry
- [ ] T4.3 Deploy agent via Agent Framework runtime
- [ ] T4.4 Configure auth/permissions (managed identity, RBAC)
- [ ] T4.5 Add evaluation suite (tool contract tests, grounding quality tests)
- [ ] T4.6 Add deployment rollout gates (CI/CD with approval)

## T5 — Channel Surfaces

- [ ] T5.1 Add web shell (`apps/copilot-web/`) on Container Apps (if required)
- [ ] T5.2 Prepare Microsoft 365 Copilot publication path
- [ ] T5.3 Prepare Teams usage path (bot/messaging integration)
- [ ] T5.4 Add API Management facade for external API access (if required)
- [ ] T5.5 Add `ipai_copilot_workspace_bridge` module for activity/notification dispatch

## T6 — Governance

- [ ] T6.1 CI checks for tool contract schema validation
- [ ] T6.2 Prompt/grounding policy tests (ensure no SoR violations)
- [ ] T6.3 Security review (penetration testing, permission audit)
- [ ] T6.4 Telemetry redaction rules (sensitive data exclusion)
- [ ] T6.5 Runtime evidence pack (deploy-time proof collection)
- [ ] T6.6 Production deployment checklist and go-live gates

---

## Dependencies

```
T0 (contracts) ──► T1 (Odoo tools)
                    T2 (shared contracts)
                    │
T1 + T2 ──────────► T3 (agent runtime)
                    │
T3 ───────────────► T4 (Agent Framework integration)
                    │
T4 ───────────────► T5 (channels)
                    │
T3 + T4 + T5 ────► T6 (governance)
```

## Estimation

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| T0 | Spec only (complete) | None |
| T1 | Medium | T0 |
| T2 | Small | T0 |
| T3 | Large | T1, T2 |
| T4 | Medium | T3 |
| T5 | Medium | T4 |
| T6 | Medium | T3, T4, T5 |
