# Tasks — agent-platform

## Phase 0 — Repo establishment

- [ ] Create canonical `agent-platform` repo entry in repo topology / governance SSOT
- [ ] Create `spec/agent-platform/{constitution,prd,plan,tasks}.md`
- [ ] Add repo description aligned to runtime/orchestration ownership
- [ ] Update org/repo topology docs to split `agents` and `agent-platform`
- [ ] Remove runtime/orchestration wording from `agents` repo descriptions and cross-repo maps

## Phase 1 — Runtime contracts

- [ ] Define run contract
- [ ] Define task contract
- [ ] Define tool invocation contract
- [ ] Define policy decision contract
- [ ] Define event/webhook contract
- [ ] Define status/state transition rules
- [ ] Add contract tests for all runtime payloads

## Phase 2 — Task ledger and state

- [ ] Implement durable task ledger
- [ ] Implement run lifecycle persistence
- [ ] Implement retry / cancel / timeout handling
- [ ] Implement replay-safe duplicate handling
- [ ] Implement operator inspection surfaces for run/task state

## Phase 3 — Orchestration engine

- [ ] Implement sequential orchestration
- [ ] Implement maker-checker orchestration
- [ ] Implement concurrent orchestration
- [ ] Implement handoff orchestration
- [ ] Implement magentic orchestration
- [ ] Add explicit workflow-to-pattern declarations
- [ ] Add pattern selection validation so critical workflows cannot rely on implicit prompt behavior

### Phase 4 — Delivery Surfaces & Connectors
- [ ] Define Microsoft 365 Copilot / Copilot Studio channel contract
- [ ] Define ERP-backed finance action contract (Odoo-native writes)
- [ ] Define finance Q&A runtime contract (grounding + escalation)
- [ ] Define balance sheet reconciliation runtime workflow (stateful matching)
- [ ] Define multi-source ingestion contract (CSV/JSON/PDF/XLSX)
- [ ] Define agent-to-agent handoff contracts (Matching -> Detection -> Correction)
- [ ] Map M365 "Day in the Life" flows to Odoo model interfaces
- [ ] Implement Odoo Finance metadata mapping layer
- [ ] Define escalation/logging/reporting contract for finance agents
- [ ] Implement M365 Agents SDK adapter logic

### Phase 4.5 — SAP Adapter
- [ ] Define SAP OData adapter contract (read/write business objects)
- [ ] Implement SAP Cloud SDK Azure Functions quickstart adapter
- [ ] Define SAP event/webhook integration contract
- [ ] Add adapter conformance test against SAP sandbox or mock

## Phase 5 — MCP and tool execution

- [ ] Implement MCP server registration contract
- [ ] Implement MCP tool call execution path
- [ ] Implement tool invocation logging/evidence
- [ ] Implement tool failure and retry handling
- [ ] Add at least one shared MCP tool integration test

## Phase 6 — Runtime adapters

- [ ] Implement primary runtime/provider adapter interface
- [ ] Implement Azure-oriented runtime adapter
- [ ] Implement fallback/secondary adapter contract
- [ ] Ensure workflow logic is adapter-based and not provider-hardcoded
- [ ] Add adapter conformance tests

## Phase 6 — Cross-repo integration

- [ ] Wire consumption of skills/judges from `agents`
- [ ] Wire control-plane dependencies from `platform`
- [ ] Wire event/webhook integration with `automations`
- [ ] Define Odoo runtime integration contract
- [ ] Define web/control-room integration contract

## Phase 7 — Security and policy

- [ ] Enforce Entra-backed identity on Azure-hosted runtime surfaces
- [ ] Enforce Key Vault-backed secret retrieval for production credentials
- [ ] Add runtime policy gate hooks
- [ ] Add judge invocation hooks
- [ ] Add failure evidence and decision evidence capture

## Phase 8 — Observability and evidence

- [ ] Emit structured run/task logs
- [ ] Emit tool invocation traces
- [ ] Emit policy/judge decision artifacts
- [ ] Add run evidence bundle output
- [ ] Add operator-facing troubleshooting guide

## Phase 9 — Repo and doc normalization

- [ ] Add `CLAUDE.md` with thin runtime-focused repo contract
- [ ] Add architecture doc for runtime boundaries
- [ ] Add validation guard so runtime ownership cannot drift back into `agents`
- [ ] Add go-live checklist for runtime readiness

## Verification gates

- [ ] `agents` no longer claims runtime/orchestration ownership
- [ ] `agent-platform` is present in canonical repo inventory
- [ ] sequential and maker-checker flows are operational first
- [ ] MCP integration is operational
- [ ] run/task state is durable
- [ ] evidence is produced for runtime executions
- [ ] repo boundaries with `platform`, `automations`, `agents`, and `odoo` are documented and enforced
