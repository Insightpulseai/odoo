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
- `.github/workflows/foundry-eval-gate.yml` — new: CI gate on eval scores

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

| Consumer | Integration Mode | Phase |
|----------|-----------------|-------|
| `ipai_odoo_copilot` (bridge) | SDK Direct | 1 |
| Foundry evaluation runner | SDK Direct | 2 |
| n8n automation workflows | REST Direct | 4 |
| Third-party API consumers | APIM Gateway | 5 |

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Agent Framework SDK is pre-release | Phase 5 is last; SDK may stabilize. Fallback: implement workflows as sequential Foundry Responses API calls |
| Databricks/fal credentials unavailable | Packs degrade gracefully; core agents unaffected |
| Router misclassification | Router is deterministic (no LLM); misroutes are bugs, not hallucinations — fix with rules |
| Evaluation threshold too strict | Start with proposed thresholds; adjust based on first eval run data |
| Foundry Memory (preview) instability | Memory is enhancement, not dependency; agents work without it |

## Not In Scope

- Teams/BizChat publishing (future, depends on M365 Agents SDK maturity)
- GitHub Copilot SDK integration (Technical Preview, evaluate only)
- APIM gateway setup (Phase 5 stretch goal, not blocking)
- Declarative YAML workflows (start with pro-code, convert later)
