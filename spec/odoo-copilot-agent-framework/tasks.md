# Tasks — Odoo Copilot Agent Framework

## Phase 1: Router + Agent Split

- [ ] **1.1** Create `copilot_router.py` with deterministic routing rules (channel, model, role, intent)
- [ ] **1.2** Refactor `foundry_service.py` to accept agent mode parameter from router
- [ ] **1.3** Define three instruction sets (Advisory, Ops, Actions) in `agent_modes.xml`
- [ ] **1.4** Restrict write tools (`create_draft`, `create_record`, `update_record`, `execute_action`) to Actions mode only
- [ ] **1.5** Add model allowlist and field allowlist configuration for Actions agent
- [ ] **1.6** Update `ai-consolidation-foundry.yaml` from five modes to three agents
- [ ] **1.7** Write router unit tests: 100 test cases covering all routing rules
- [ ] **1.8** Verify `--stop-after-init` passes with refactored module
- [ ] **1.9** Update `docs/architecture/AI_CONSOLIDATION_FOUNDRY.md` with three-agent diagram

## Phase 2: Evaluation Framework

- [ ] **2.1** Create `scripts/foundry/run_evaluations.py` — runs Foundry evaluators per agent
- [ ] **2.2** Define `ssot/ai/evaluation_thresholds.yaml` with per-agent minimum scores
- [ ] **2.3** Create evaluation datasets: 50 test cases per agent (150 total)
- [ ] **2.4** Run baseline evaluations, capture scores in `docs/evidence/`
- [ ] **2.5** Create `.github/workflows/foundry-eval-gate.yml` CI gate
- [ ] **2.6** Verify Advisory groundedness ≥ 0.8 on baseline dataset
- [ ] **2.7** Verify Actions safety = 1.0 (no unauthorized writes in test suite)

## Phase 3: Marketing Strategy Pack

- [ ] **3.1** Create `capability_packs.py` — pack registry with load/unload lifecycle
- [ ] **3.2** Define pack schema in `ssot/ai/capability_packs.yaml`
- [ ] **3.3** Create `pack_marketing_strategy.xml` — prompt segments for brand/campaign context
- [ ] **3.4** Wire Marketing Strategy pack to Advisory agent instruction set
- [ ] **3.5** Write smoke tests: marketing queries return brand-aware responses
- [ ] **3.6** Verify no credential requirements (pack uses existing web_search + search_knowledge)

## Phase 4: Databricks + fal Packs

- [ ] **4.1** Create `pack_databricks.xml` — Databricks SQL, Unity Catalog, dashboard tools
- [ ] **4.2** Register Databricks MCP server endpoint in Foundry Tool Catalog
- [ ] **4.3** Implement graceful degradation: pack disabled when `DATABRICKS_HOST` absent
- [ ] **4.4** Create `pack_fal_creative.xml` — image/video generation, style transfer tools
- [ ] **4.5** Register fal MCP server endpoint in Foundry Tool Catalog
- [ ] **4.6** Implement fal fallback: use Foundry `image_generation` when `FAL_KEY` absent
- [ ] **4.7** Wire Databricks to Advisory + Ops agents
- [ ] **4.8** Wire fal to Actions agent
- [ ] **4.9** Verify telemetry: pack tool calls logged in App Insights
- [ ] **4.10** Re-run evaluations: confirm scores maintained after pack addition

## Phase 5: Multi-Agent Workflows

- [ ] **5.1** Install `azure-ai-agentserver-agentframework` in devcontainer
- [ ] **5.2** Create `expense_approval.py` — human-in-the-loop workflow (classify → draft → approve → post)
- [ ] **5.3** Create `month_end_close.py` — sequential pipeline (GL → AP → AR → Tax)
- [ ] **5.4** Create `sales_inquiry.py` — group chat with dynamic agent handoff
- [ ] **5.5** Add OTel observability: `setup_observability(vs_code_extension_port=4319)`
- [ ] **5.6** Test expense workflow end-to-end with human approval gate
- [ ] **5.7** Test month-end pipeline with 3+ sequential agents
- [ ] **5.8** Capture OTel traces in `docs/evidence/` for each workflow
- [ ] **5.9** (Stretch) Register APIM gateway `apim-ipai-dev` as enterprise front door
- [ ] **5.10** (Stretch) Convert expense YAML workflow to Agent Framework code via GitHub Copilot

## Cross-Cutting

- [ ] **X.1** Ensure all agent invocations produce App Insights telemetry (user, mode, tools, tokens, latency, safety)
- [ ] **X.2** Update `ipai_odoo_copilot` settings UI to expose agent mode selection
- [ ] **X.3** Add router diagnostics endpoint: `GET /copilot/router/test?input=...` returns predicted agent
- [ ] **X.4** Create `spec/odoo-copilot-agent-framework/` (this spec kit) — committed
- [ ] **X.5** Update SSOT YAML with three-agent model + capability packs + integration modes
