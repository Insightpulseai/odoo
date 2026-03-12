# Tasks — Odoo Copilot on Azure Foundry

## Epic 1 — SSOT AI Manifests

- [x] Create `ssot/ai/agents.yaml` with physical + logical agent definitions
- [x] Create `ssot/ai/models.yaml` with gpt-4.1 deployment target
- [x] Create `ssot/ai/topics.yaml` with interaction topic taxonomy
- [x] Create `ssot/ai/tools.yaml` with bounded tool definitions
- [x] Create `ssot/ai/policies.yaml` with safety/posture policies
- [x] Create `ssot/ai/sources.yaml` with knowledge source definitions
- [x] Create `ssot/ai/prompts.yaml` with prompt template references

**GATE: All manifests exist, IDs resolve across files**

---

## Epic 2 — Foundry Instructions

- [x] Create `ssot/ai/foundry_instructions.md` with production instruction text
- [x] Cover all four logical modes (Ask, Authoring, Livechat, Transaction)
- [x] Declare grounded behavior, citation requirements, failure modes

**GATE: Instruction artifact is repo-tracked and complete**

---

## Epic 3 — Odoo Addon

- [x] Create `addons/ipai/ipai_odoo_copilot/__manifest__.py`
- [x] Create settings model (`res.config.settings` extension)
- [x] Create Foundry service model (thin bounded layer)
- [x] Create settings view XML
- [x] Create server action XML
- [x] Create security access rules
- [x] Optional: healthcheck cron

**GATE: Addon installs, settings render, actions exist**

---

## Epic 4 — Validation

- [x] Create SSOT integrity test (`tests/ssot/test_ai_manifests.py`)
- [x] Verify IDs resolve across YAML manifests
- [x] Verify no orphaned references

**GATE: Validation passes**

---

## Epic 5 — Acceptance

- [ ] Spec bundle aligned
- [ ] SSOT AI manifests coherent
- [ ] Odoo addon installable
- [ ] Memory defaults to off
- [ ] Read-only/draft-only posture explicit
- [ ] No repo-root scaffolding drift
- [ ] Foundry evaluations defined (deferred to integration phase)
