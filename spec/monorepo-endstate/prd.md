# Monorepo End-State — Product Requirements

**Version**: 1.0.0
**Status**: Active
**Owner**: Platform Engineering

---

## Context

The InsightPulse AI monorepo has grown organically. This PRD defines the requirements
for reaching the target end-state: a fully governed, SSOT-anchored monorepo that supports
Odoo 19 CE + OCA feature parity and zero-touch deployment.

---

## Objectives

### O1: EE Feature Mapping

**Problem**: It is currently unclear which Odoo Enterprise Edition features are needed,
which have OCA equivalents, and which require custom IPAI bridges.

**Requirement**: A machine-readable matrix (`ssot/parity/ee_to_oca_matrix.yaml`) that:
- Lists all EE features relevant to InsightPulse AI workflows
- Maps each to: OCA equivalent module | IPAI bridge | "gap: no alternative"
- Is kept current via quarterly review
- Is referenced by CI parity gate

**Success criteria**:
- Matrix contains >=10 entries (initial population)
- CI gate (`ee-parity-gate.yml`) references the matrix
- No `odoo.enterprise` imports in `addons/ipai/` merge to main

### O2: IPAI Bridge Registry

**Problem**: IPAI integration bridges (Zoho Mail, OCR, AI tools, etc.) are not formally
cataloged, making it hard to audit dependencies and maintain contracts.

**Requirement**: A bridge catalog (`ssot/bridges/catalog.yaml`) that:
- Lists every active IPAI bridge with: name, replaces (EE feature), status, contract doc path
- Each bridge has a corresponding `docs/contracts/<NAME>_CONTRACT.md`
- Status transitions: `planned` -> `active` -> `deprecated`

**Success criteria**:
- All currently active bridges listed
- All active bridges have contract docs
- New bridges can't go active without contract (enforced by constitution rule #3)

### O3: CI Parity Gate

**Problem**: There is no automated check preventing EE module dependencies from creeping
into `addons/ipai/` modules.

**Requirement**: A CI workflow (`.github/workflows/ee-parity-gate.yml`) that:
- Scans `addons/ipai/**/*.py` for `odoo.enterprise` imports
- Scans `addons/ipai/**/__manifest__.py` for enterprise module dependencies
- Exits non-zero if any are found
- Runs on all PRs targeting `main`

**Success criteria**:
- Workflow exists and passes on current codebase
- At least one failing test case documented

### O4: Documentation Completeness

**Problem**: Several reference documents are missing, making it hard for engineers
(human and AI) to understand the expected end-state.

**Requirement**: The following documents must exist and be kept current:
- `docs/architecture/MONOREPO_END_STATE_OKR.md` -- OKR anchor
- `docs/architecture/AI_PROVIDER_BRIDGE.md` -- AI provider contracts
- `docs/runbooks/SECRETS_SSOT.md` -- Secret management workflow
- `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` -- Go-live procedure

### O5: AI Provider Bridge as Platform Contract

**Problem**: Odoo 19 "Ask AI" (html editor AI action) is an EE/IAP feature. Each AI surface
(editor, chatter, automations, ops-console) currently re-implements AI access independently,
creating ungoverned provider coupling.

**Requirement**: The IPAI AI Provider Bridge is the single platform contract for all AI generation:

- **O5.1**: Odoo AI (Ask AI / html editor assistant) MUST call the IPAI AI Provider Bridge
  by default. Calls are proxied through `ipai_ai_widget` Odoo addon (no Odoo IAP dependency).
  OCA-local Ollama generation (`ai_oca_native_generate_ollama`) MAY be enabled as a fallback
  for offline/local-only tenants by setting `ssot/ai/odoo_ai.yaml` mode to `ollama`.
- **O5.2**: All AI generation calls MUST return `{ provider, text, model, trace_id }`.
  Telemetry with those fields MUST be emitted to ops event log (trace_id enables cost
  attribution and audit). No fire-and-forget AI calls.

**Success criteria**:
- `ssot/bridges/catalog.yaml` has `ipai_ai_tools_bridge` status=active with consumers:
  `[odoo, ops-console, workers]` and `fallback: oca_ollama`
- `ssot/parity/ee_to_oca_matrix.yaml` records "Ask AI editor assistant" as
  `gap_type: ipai_bridge` (not `oca_available`) pointing to `ipai_ai_widget`
- `ipai_ai_widget` addon routes via `ir.config_parameter ipai_ai_widget.bridge_url` —
  no hardcoded LLM endpoint inside Odoo source
- Missing `GEMINI_API_KEY` on bridge side returns `503 AI_KEY_NOT_CONFIGURED`
  (enforced by contract, tested in `docs/contracts/AI_WIDGET_CONTRACT.md`)

---

## Non-Requirements (Out of Scope)

- This PRD does not require migrating to Odoo Enterprise Edition
- This PRD does not require changing the self-hosted deployment model
- This PRD does not require replacing currently-active OCA modules
- This PRD does not define specific Odoo module feature requirements (see individual spec bundles)

---

## Constraints

1. CE-only: No Enterprise Edition licenses
2. OCA-first: OCA modules preferred over custom `ipai_*` modules
3. Self-hosted: DigitalOcean droplet (not Odoo.sh, not SaaS)
4. Domain: `*.insightpulseai.com` only
5. Cost: Minimize infrastructure costs -- no paid SaaS where free/self-hosted alternative exists
