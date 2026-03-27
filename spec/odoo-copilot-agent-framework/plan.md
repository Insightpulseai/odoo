# Plan — Odoo Copilot Agent Framework

## Build Phases

### Phase 1: Router + Agent Split (2 weeks)

**Goal**: Split current five-mode agent into three logical agents with deterministic routing.

**Files changed**:
- `addons/ipai/ipai_odoo_copilot/models/foundry_service.py` — add router logic, agent mode selection
- `addons/ipai/ipai_odoo_copilot/models/copilot_router.py` — new: deterministic router class
- `addons/ipai/ipai_odoo_copilot/data/agent_modes.xml` — agent mode definitions (Advisory, Ops, Actions)
- `ssot/governance/ai-consolidation-foundry.yaml` — update capability_modes to three-agent model

**Dependencies**: None (builds on existing ipai_odoo_copilot)

**Verification**:
- Router classifies 100 test requests with ≥ 95% accuracy
- Each agent mode receives correct instruction set
- Write tools only available in Actions agent mode
- `--stop-after-init` passes

### Phase 2: Evaluation Framework (1 week)

**Goal**: Foundry evaluation runs per agent with minimum thresholds.

**Files changed**:
- `scripts/foundry/run_evaluations.py` — new: evaluation runner for all three agents
- `ssot/ai/evaluation_thresholds.yaml` — new: threshold definitions per agent
- `pipelines/foundry-eval-gate.yml` — new: Azure DevOps Pipelines CI gate on eval scores

**Dependencies**: Phase 1

**Verification**:
- Advisory: groundedness ≥ 0.8, relevance ≥ 0.85
- Ops: groundedness ≥ 0.85, data accuracy ≥ 0.95
- Actions: action correctness ≥ 0.95, safety = 1.0
- CI gate fails if thresholds not met

### Phase 3: Capability Packs — Marketing Strategy (1 week)

**Goal**: Attach Marketing Strategy pack to Advisory agent. Zero external credentials required.

**Files changed**:
- `addons/ipai/ipai_odoo_copilot/models/capability_packs.py` — new: pack registry + loader
- `addons/ipai/ipai_odoo_copilot/data/pack_marketing_strategy.xml` — prompt segments + tool config
- `ssot/ai/capability_packs.yaml` — new: pack definitions SSOT

**Dependencies**: Phase 1

**Verification**:
- Advisory agent answers marketing-related queries with brand guidelines context
- Pack loads without errors when module installed
- No credential requirements

### Phase 4: Capability Packs — Databricks + fal (2 weeks)

**Goal**: Attach Databricks Intelligence to Advisory+Ops, fal Creative to Actions.

**Files changed**:
- `addons/ipai/ipai_odoo_copilot/models/capability_packs.py` — extend with Databricks + fal packs
- `addons/ipai/ipai_odoo_copilot/data/pack_databricks.xml` — Databricks tool definitions
- `addons/ipai/ipai_odoo_copilot/data/pack_fal_creative.xml` — fal tool definitions
- MCP server registrations for Databricks SQL and fal endpoints

**Dependencies**: Phase 3 (pack registry exists)

**Verification**:
- Databricks pack disabled gracefully when `DATABRICKS_HOST` absent
- fal pack falls back to Foundry `image_generation` when `FAL_KEY` absent
- Both packs produce telemetry in App Insights
- Foundry eval scores maintained after pack addition

### Phase 4B: Capability Packs — BIR Compliance + Document Intake (2 weeks)

**Goal**: Attach BIR Compliance Pack (Tax Pulse) and Document Intake Pack to all agents.

**Files changed**:
- `addons/ipai/ipai_odoo_copilot/data/pack_bir_compliance.xml` — BIR tool definitions per agent
- `addons/ipai/ipai_ai_copilot/data/copilot_tools_bir.xml` — 8 BIR copilot tools
- `infra/ssot/agents/tax_pulse_tool_contracts.yaml` — typed tool contracts (COMPLETE)
- `infra/ssot/agents/agent_capability_matrix.yaml` — BIR pack registered (COMPLETE)
- `eval/datasets/bir_*.yaml` — evaluation datasets (COMPLETE)
- `eval/training/bir_sft_*.jsonl` — SFT training assets (COMPLETE)

**Dependencies**: Phase 3 (pack registry exists), Wave 2-3 from `spec/tax-pulse-sub-agent/`

**Verification**:
- Advisory answers BIR questions with grounded citations (groundedness ≥ 0.8)
- Ops inspects filing readiness without triggering writes
- Actions compute/validate/export requires approval gate
- Safety = 1.0 (no unauthorized tax operations)
- Pack works without external credentials

### Phase 5: Multi-Agent Workflows (2 weeks)

**Goal**: Implement ERP workflows using Microsoft Agent Framework patterns.

**Workflows**:
1. **Expense Approval** (human-in-the-loop): Ops agent classifies → Actions agent drafts → human approves → Actions agent posts
2. **Month-End Close** (sequential): Ops agent reconciles GL → AP → AR → Tax
3. **Sales Inquiry** (group chat): Advisory agent handles CRM → Inventory → Pricing handoffs

**Files changed**:
- `addons/ipai/ipai_odoo_copilot/workflows/expense_approval.py` — Agent Framework workflow
- `addons/ipai/ipai_odoo_copilot/workflows/month_end_close.py` — sequential pipeline
- `addons/ipai/ipai_odoo_copilot/workflows/sales_inquiry.py` — group chat pattern

**Dependencies**: Phase 2 (evaluations), Phase 4 (all packs), `azure-ai-agentserver-agentframework`

**Verification**:
- Expense workflow completes end-to-end with OTel trace
- Month-end sequential pipeline handles 3+ agents without deadlock
- Human-in-the-loop gates block progression until approval received
- All workflows visible in VS Code Foundry extension visualizer

## Integration Surface Plan

| Consumer | Ingress Path | Phase |
|----------|-------------|-------|
| `ipai_odoo_copilot` (bridge) | Foundry Project Client + OpenAI-compatible client | 1 |
| Foundry evaluation runner | OpenAI-compatible client | 2 |
| n8n automation workflows | Direct REST (with APIM or service auth) | 4 |
| All production clients | APIM AI gateway (required) | 5 |
| Builders/operators (dev only) | Foundry Playgrounds (non-production) | 1+ |

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Agent Framework SDK is pre-release | Phase 5 is last; SDK may stabilize. Fallback: implement workflows as sequential Foundry Responses API calls |
| Databricks/fal credentials unavailable | Packs degrade gracefully; core agents unaffected |
| Router misclassification | Router is deterministic (no LLM); misroutes are bugs, not hallucinations — fix with rules |
| Evaluation threshold too strict | Start with proposed thresholds; adjust based on first eval run data |
| Foundry Memory (preview) instability | Memory is enhancement, not dependency; agents work without it |

## Ingress matrix

| Ingress path | Use it for | Backing endpoint / client | Who should use it | Governance layer |
|---|---|---|---|---|
| Foundry Project Client | project config, connections, tracing, Foundry-native ops | `AIProjectClient` on `https://<resource>.services.ai.azure.com/api/projects/<project>` | internal control-plane services | Foundry RBAC + project scope |
| OpenAI-compatible client from project | agents, evaluations, responses, model calls in project context | `project.get_openai_client(...)` / `/openai` route | advisory, ops, actions runtime calls | Foundry project scope + model deployment policy |
| Direct REST | adapters, n8n/webhooks, lightweight bridges | `/openai/v1` or compatible route | automation bridges, service adapters | APIM or service auth in front |
| API Management AI gateway | enterprise front door for models, agents, tools, MCP/A2A APIs | APIM AI gateway | all production ingress | auth, quotas, throttling, routing, observability |
| Foundry Playgrounds | rapid prototyping and validation | model / agents playground | builders and operators only | non-production sandbox |

## Ingress ownership by component

| Component | Primary ingress | Secondary ingress | Notes |
|---|---|---|---|
| Advisory | APIM → Foundry/OpenAI-compatible client | Playground during prototyping | main enterprise chat/API surface |
| Ops | internal APIM route → Agent Framework runtime | project client for setup/tracing | internal-only |
| Actions | internal APIM route → Agent Framework runtime | none | approval-gated only |
| Router | internal service ingress only | none | not user-facing |

## Evaluation model

### System evaluations
- Task Completion
- Task Adherence
- Intent Resolution
- Relevance / Groundedness where applicable

### Process evaluations
- Tool Selection
- Tool Call Success
- Tool Output Utilization
- Tool Input Accuracy
- Task Navigation Efficiency for workflow paths with ground truth

### Safety evaluations
- advisory: content risk + jailbreak screening + sampled human review
- ops: leakage/refusal + internal red-team scenarios
- actions: policy tests, approval-path tests, human review before production enablement
- router: approval compliance and routing correctness

## Safety caveat

Foundry safety evaluations are helpful but not sufficient alone; they are not comprehensive, can produce false positives/negatives, and should be combined with human review and domain-specific policy tests before production release.

## Not In Scope

- Teams/BizChat publishing (future, depends on M365 Agents SDK maturity)
- GitHub Copilot SDK integration (Technical Preview, evaluate only)
- Declarative YAML workflows (start with pro-code, convert later)

Note: APIM gateway is **in scope** (required production front door, Phase 5).

---

## AFC Parity — Cross-Cutting Artifacts

The following artifacts were created as part of the AFC parity merge and are referenced by both the copilot framework and Tax Pulse capability pack.

### New Canonical Files

| File | Purpose | Referenced By |
|---|---|---|
| `agents/contracts/ui/confirm_action_card.json` | Adaptive Card JSON for write confirmation | Actions agent, Tax Pulse, all write operations |
| `agents/contracts/ui/adaptive_cards_index.yaml` | Index of all Adaptive Cards across surfaces | Teams integration, Odoo widget, agent responses |
| `agents/contracts/openapi/ipai_odoo_bridge.openapi.yaml` | Narrow OpenAPI spec for agent-to-Odoo bridge | All agents via APIM, Tax Pulse tools |
| `infra/ssot/tax/compliance_check_catalog.yaml` | Machine-readable compliance check registry (12 checks) | Tax Pulse agent, `ipai_bir_tax_compliance` |
| `infra/ssot/agents/tax_pulse_tool_contracts.yaml` | Tool contracts + agent metadata (updated) | Tax Pulse capability pack, bridge API |

### Capability Class Integration

Every agent response must be classified into one of four capability classes:
- **Informational**: explain, summarize (Advisory)
- **Navigational**: locate, deep-link (Advisory, Ops)
- **Transactional**: create, update, trigger (Actions, confirmation required)
- **Compliance Intelligence**: cross-check, flag, surface findings (Ops read, Actions write)

This classification drives routing, card selection, and audit trail behavior.

### Confirmation Flow (All Write Operations)

```
User request → Router → Actions agent → ConfirmActionCard → User confirms → Bridge API → Odoo write → Chatter audit note
                                          ↓ (cancel)
                                     No action taken
```

The `ConfirmActionCard` is mandatory for all write operations regardless of surface (Teams, Odoo Widget, or programmatic API with human-in-the-loop).

## Phase A4 — Skill Framework

- define canonical skill manifest schema
- define context-pack schema
- define output contract schema
- define router selection rules
- define policy wrapper for permission/config/approval checks
- define audit and observability contract for all skills

## Phase B9 — Skill Builder Kits

- create starter templates for informational skills
- create starter templates for artifact-generation skills
- create starter templates for record-producing skills
- create starter templates for governed execution skills
- create a conformance checklist so new skills cannot bypass the framework

## n8n orchestration boundary

n8n is the asynchronous connector and automation layer, not the primary assistant runtime and not the source of tax/compliance truth.

Use n8n for:
- delayed or scheduled automations
- external notifications
- connector-heavy fan-out/fan-in flows
- document/package delivery
- webhook-triggered side effects
- human approval relay plumbing where Teams/email/chat integrations are needed

Do not use n8n for:
- canonical workflow state
- tax-rule truth
- compliance decision authority
- primary conversational routing
- durable accounting/business object ownership
