# AI Bridge — Implementation Plan

## Phase 1: Addon scaffold + controller (T-2, T-3, T-4)

Create `addons/ipai/ipai_ai_widget/` with:
- `__manifest__.py` (depends: `['mail']`, no IAP, no enterprise)
- Controller: `POST /ipai/ai/ask` → reads `ipai_ai_widget.bridge_url` from ir.config_parameter → proxies to IPAI bridge → returns standardized response
- OWL 2 component: button in chatter + dialog (prompt input + response display + insert button)
- Settings view: bridge URL field under Settings

## Phase 2: SSOT wiring (T-5, T-6)

- Add `ipai_ai_widget` to `ssot/bridges/catalog.yaml`
- Create `docs/contracts/AI_WIDGET_CONTRACT.md`

## Phase 3: OCA/ai porting (T-1, future)

- Port `ai_oca_bridge` and `ai_oca_bridge_chatter` from 18.0 to 19.0
- Add `ai_oca_bridge` to `ipai_ai_widget` depends list
- Replace direct HTTP proxy in controller with OCA bridge call pattern

## Phase 4: CI gate (T-7)

- Add to `ssot-gates.yml` or a new workflow: `grep -r "iap" addons/ipai/ipai_ai_widget/` exits 1 if any IAP reference found
