# Plan — Odoo Copilot on Azure Foundry

## 1. Strategy

Implement the smallest coherent brownfield patch:

1. Create SSOT AI manifests modeling one physical Foundry agent with logical modes
2. Create Foundry instructions artifact
3. Create thin Odoo addon for configuration/policy/audit
4. Add minimal validation for SSOT integrity and addon smoke tests
5. No repo-root scaffolding

---

## 2. Deliverables

### SSOT AI Manifests
- `ssot/ai/agents.yaml` — physical + logical agent definitions
- `ssot/ai/models.yaml` — gpt-4.1 deployment target
- `ssot/ai/topics.yaml` — interaction topic taxonomy
- `ssot/ai/tools.yaml` — bounded tool definitions (v1 minimal)
- `ssot/ai/policies.yaml` — safety/posture policies
- `ssot/ai/sources.yaml` — knowledge source definitions
- `ssot/ai/prompts.yaml` — prompt template references

### Foundry Instructions
- `ssot/ai/foundry_instructions.md` — production instruction text

### Odoo Addon
- `addons/ipai/ipai_odoo_copilot/` — thin configuration addon

### Validation
- `tests/ssot/test_ai_manifests.py` — cross-manifest integrity checks

---

## 3. Architecture decisions

### One physical agent
All logical behavior (Ask, Authoring, Livechat, Transaction) is routed
through a single Foundry agent via instructions and topic selection.
No separate Foundry deployments per mode.

### Odoo as control plane
Foundry runtime config is considered authoritative only when it matches
Odoo-managed policy. Odoo settings are the source of truth for:
- enabled/disabled state
- memory toggle
- read-only/draft-only posture
- model selection
- knowledge source configuration

### Stub pattern for Azure SDK
v1 does not require the Azure Foundry SDK in the Odoo runtime.
Sync actions (connection test, agent ensure) validate config shape
and log intent. Full SDK integration is a future slice.

---

## 4. Validation phases

### Phase 1 — Static
- SSOT manifests pass cross-reference validation
- Odoo addon imports without error
- XML/action references resolve

### Phase 2 — Functional
- Settings UI renders
- Config persists to ir.config_parameter
- Actions execute without error

### Phase 3 — Integration (future)
- Foundry agent responds to grounded queries
- Evaluations pass acceptance thresholds

---

## 5. Open points

- Exact Azure Foundry project endpoint URL pattern (assumed standard)
- Managed identity availability in current ACA deployment
- Azure Search index name for knowledge grounding
- Evaluation threshold criteria

These are marked as assumptions in code/docs rather than invented facts.
