# AI Bridge — Tasks

> **Spec**: `spec/ai-bridge/`
> **Status**: Active
> **Last updated**: 2026-02-17

---

## Completed

- [x] **T-2** Create `addons/ipai/ipai_ai_widget/__manifest__.py` (depends: mail, no IAP)
- [x] **T-3** Create controller `controllers/ai_proxy.py` with `POST /ipai/ai/ask`
- [x] **T-4** Create OWL 2 component + XML template (button in chatter, dialog, insert)
- [x] **T-5** Add `ipai_ai_widget` to `ssot/bridges/catalog.yaml`
- [x] **T-6** Create `docs/contracts/AI_WIDGET_CONTRACT.md`
- [x] **T-7** Add no-IAP CI lint gate to `.github/workflows/ssot-gates.yml`

## Backlog

- [ ] **T-1** [FUTURE] Port `OCA/ai` 18.0 to 19.0 (ai_oca_bridge, ai_oca_bridge_chatter). Spec: this file. Branch: `feat/oca-ai-port`.
- [ ] **T-8** [FUTURE] Add multi-provider switching (beyond Gemini) once OCA/ai port lands.
- [ ] **T-9** [FUTURE] Add streaming response support to the OWL dialog component.
