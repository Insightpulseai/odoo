# AI Bridge — Constitution

## Non-Negotiable Rules

1. **No Odoo IAP dependency.** All AI provider calls must route through the IPAI control plane, never via `odoo.com/iap`. Enforce: `grep -r "iap" addons/ipai/ipai_ai_widget/` must return 0 matches.
2. **OCA/ai is the in-Odoo substrate.** The `ipai_ai_widget` addon depends on `ai_oca_bridge` (once ported to 19.0). Until ported, it depends on `mail` only.
3. **IPAI bridge is the provider plane.** All actual LLM calls are made by the IPAI provider bridge (e.g., `POST /api/ai/gemini`), never from Odoo directly to an LLM API.
4. **Deterministic failure before outbound call.** If the bridge URL is not configured, the controller returns `503 BRIDGE_URL_NOT_CONFIGURED` without making any HTTP call.
5. **No API keys in Odoo.** The bridge URL is stored in `ir.config_parameter` (not a secret). API keys live in the provider bridge's environment (Vercel env vars / GitHub Actions Secrets), registered in `ssot/secrets/registry.yaml`.
6. **Response shape is contractual.** Controllers must return `{ provider, text, model, trace_id }` or `{ error: string, status: int }`. No arbitrary shapes.
7. **Bridge must be registered.** Every IPAI bridge referenced by `ipai_ai_widget` must have an entry in `ssot/bridges/catalog.yaml` and a contract doc in `docs/contracts/`.
