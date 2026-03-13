# Tasks — ipai-odoo-copilot-azure

## Phase 1: Configuration Surface + Live Agent Verification (v1)

### Addon structure
- [x] Create `addons/ipai/ipai_odoo_copilot/__manifest__.py`
- [x] Create `models/res_config_settings.py` with Foundry fields
- [x] Create `models/foundry_service.py` (AbstractModel)
- [x] Create `views/res_config_settings_views.xml`
- [x] Create `data/ir_config_parameter.xml` (defaults)
- [x] Create `data/ir_actions_server.xml`
- [x] Create `data/ir_cron.xml` (nightly healthcheck)
- [x] Create `security/ir.model.access.csv`

### Health probe (test_connection)
- [x] Auth-mode detection: managed identity (IMDS) → env-key → none
- [x] IMDS resource scope: `cognitiveservices.azure.com` (correct for AI services)
- [x] Non-mutating API endpoint reachability probe (stdlib urllib)
- [x] Status-aware failure reporting (401/403/404/5xx/network)
- [x] Knowledge/search binding state reported separately
- [x] Structured logging (auth mode, target, status, no secrets)
- [x] Separate portal URL vs API endpoint fields

### Agent resolution (ensure_agent)
- [x] List agents via `GET /openai/assistants` (Azure AI Agent Service API)
- [x] Search response for configured agent name
- [x] Report found (with agent id + model) or not-found (with available agents)
- [x] Read-only — never creates/updates/deletes agents
- [x] HTTP status classification reused from health probe
- [x] UI button relabeled "Verify Agent" (accurate)

### Spec & SSOT
- [x] Create spec kit (constitution, prd, plan, tasks)
- [x] Create SSOT AI manifests (agents, models, topics, tools, policies, sources, prompts)
- [x] Create Foundry instruction artifact
- [x] Add SSOT integrity validator

### Validation
- [x] Python compile check passes
- [x] SSOT cross-reference validation passes
- [x] XML parse validation passes
- [ ] Install smoke test on Odoo 19 (requires devcontainer)
- [ ] Live agent resolution test (requires Azure access + API endpoint)
- [ ] Foundry evaluation runs (requires Azure access)

## Phase 2: Knowledge Grounding (future)

- [ ] Provision Azure AI Search index (srch-ipai-dev)
- [ ] Wire search connection to Foundry agent
- [ ] Add citation rendering
- [ ] Run grounding evaluations

## Phase 3: Bounded Tools (future)

- [ ] Define tool schemas
- [ ] Implement Odoo tool endpoints
- [ ] Add approval workflow
- [ ] Wire read-only toggle

## Phase 4: Production Hardening (future)

- [ ] Managed identity as primary auth (ACA role assignment to AI services)
- [ ] Audit logging
- [ ] queue_job integration
- [ ] Evaluation dashboard
