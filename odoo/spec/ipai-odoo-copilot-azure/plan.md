# Plan — ipai-odoo-copilot-azure

## Phase 1: Configuration Surface + Live Agent Verification (v1 — current)

1. Create `addons/ipai/ipai_odoo_copilot/` Odoo addon
   - `res.config.settings` with Foundry connection fields
   - `ipai.foundry.service` AbstractModel for bounded operations
   - Settings view with test/sync/portal actions
   - Default config parameters for known Foundry coordinates
   - Nightly healthcheck cron
   - No hard OCA dependencies beyond `base`

2. Two distinct endpoints configured:
   - **Portal URL** (`foundry_endpoint`): for "Open Foundry Portal" button
   - **API Endpoint** (`foundry_api_endpoint`): for health probe and agent resolution
     (e.g. `https://data-intel-ph-resource.services.ai.azure.com`)

3. `test_connection()` is a **real non-mutating health probe**
   - Validates: enabled → config shape → auth availability → API endpoint reachability
   - Auth precedence: managed identity (IMDS with cognitiveservices scope) → env-key → clear failure
   - Reports HTTP status, auth mode, and knowledge/search binding state
   - Never mutates Foundry state — read-only GET only

4. `ensure_agent()` is a **real read-only agent resolution**
   - Runs `test_connection()` first
   - Lists agents via `GET /openai/assistants?api-version=...`
   - Searches for the configured agent name in the response
   - Reports: agent found (with id + model) or agent not found (with available agents list)
   - **Never creates, updates, or deletes agents**

5. Create spec kit, SSOT AI manifests, Foundry instruction artifact, SSOT validator

## Phase 2: Knowledge Grounding (future)

- Provision Azure AI Search index (`srch-ipai-dev`) with Odoo knowledge base content
- Wire search connection/index fields to actual retrieval
- Add citation rendering in Odoo UI
- Run Foundry evaluations for grounded response quality

## Phase 3: Bounded Tools (future)

- Define tool schemas for Transaction Agent mode
- Implement Odoo-side tool endpoints (bounded CRUD)
- Add approval workflow for draft → commit
- Wire read-only mode toggle to tool availability

## Phase 4: Production Hardening (future)

- Managed identity as primary auth (probe logic exists, needs ACA role assignment)
- Add Odoo-side audit logging for Foundry interactions
- Integrate with `queue_job` for async operations
- Add Foundry trace/evaluation dashboard in Odoo
