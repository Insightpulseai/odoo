# AI Bridge — Tasks

## Backlog

- [ ] **T-1** [FUTURE] Port `OCA/ai` 18.0 → 19.0 (ai_oca_bridge, ai_oca_bridge_chatter). Spec: this file. Branch: `feat/oca-ai-port`.
- [x] **T-2** Create `addons/ipai/ipai_ai_widget/__manifest__.py` (depends: mail, no IAP)
- [x] **T-3** Create controller `controllers/ai_proxy.py` with `POST /ipai/ai/ask`
- [x] **T-4** Create OWL 2 component + XML template (button in chatter, dialog, insert)
- [x] **T-5** Add `ipai_ai_widget` to `ssot/bridges/catalog.yaml`
- [x] **T-6** Create `docs/contracts/AI_WIDGET_CONTRACT.md`
- [x] **T-7** Add no-IAP CI lint gate to `.github/workflows/ssot-gates.yml`
