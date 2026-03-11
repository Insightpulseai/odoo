# AI Copilot Constitution — ipai_ai_copilot

Version: 1.0.0 | Status: Active | Last updated: 2026-02-27

## Non-Negotiable Rules

**Rule 1: All write actions require explicit user confirmation dialog before execution.**
The copilot sidebar MUST display a confirmation dialog showing exactly what action will be taken
before any create, update, delete, or state-change operation is executed. No auto-execution of
write operations under any circumstances. Tools with `requires_confirmation=True` are gated by
the frontend confirmation component.

**Rule 2: AI always operates within res.users context — record rules and access rights always enforced.**
Every tool call is dispatched through `request.env` which carries the authenticated user's context.
Record-level security (ir.rule), field-level access (ir.model.access), and group membership
are always respected. The copilot cannot escalate privileges beyond the user's own permissions.

**Rule 3: Tool registry is the ONLY mechanism for AI to affect Odoo data.**
The AI copilot may only affect Odoo data through registered tools in `ipai.copilot.tool`.
No raw ORM calls, no direct SQL, no ir.rule bypass. Any new capability must be registered
as a tool with an appropriate `category` and `requires_confirmation` flag before it can be used.

**Rule 4: No direct LLM calls from Odoo — all AI routes through IPAI bridge.**
The Odoo controller (`/ipai/copilot/chat`) MUST forward all AI requests to the IPAI bridge URL
configured at `ir.config_parameter:ipai_ai_copilot.bridge_url`. No Python code in this addon
may call any LLM API directly (OpenAI, Google, Anthropic, Ollama, etc.). The bridge is the
sole AI inference endpoint.

**Rule 5: Embeddings live in Supabase pgvector, never in Odoo's own PostgreSQL.**
Any vector similarity search, RAG retrieval, or embedding storage MUST use Supabase pgvector
via the configured Supabase Edge Function. No pgvector extension may be added to Odoo's PostgreSQL.
Odoo PostgreSQL is for transactional ERP data only.

**Rule 6: All AI responses include trace_id for audit (O5.2 contract).**
Every response from the IPAI bridge MUST include a `trace_id` (UUID). The Odoo controller
records this trace_id in the session history and includes it in all responses to the frontend.
Trace IDs enable correlation between user actions and AI model calls for compliance and debugging.

**Rule 7: Session history is per-user, max 50 turns, stored in ipai.copilot.session.**
Conversation history is stored per authenticated user in `ipai.copilot.session.history_json`.
Sessions are bounded to 50 turns (100 messages: 50 user + 50 assistant) to prevent unbounded growth.
Sessions are associated with `res.users` and cannot be shared across users.

**Rule 8: Provider configured via ssot/ai/odoo_ai.yaml — default: gemini.**
The AI provider is determined by the IPAI bridge, not by Odoo configuration. Odoo only
knows the bridge URL. Provider selection, model routing (Flash vs Pro), and fallback logic
are managed in the platform layer. Default provider is Gemini (Google) as specified in the SSOT.

**Rule 9: Tool declarations are server-side only — never sent to client before AI evaluation.**
The list of available tools and their JSON Schema declarations MUST NOT be sent to the browser
until after the AI has evaluated the user's message. The frontend receives only the human-readable
tool results preview (for confirmation display), not the raw Gemini function declarations.
This prevents client-side tool manipulation.

**Rule 10: n8n automation tools are allowlisted in ssot/bridges/catalog.yaml before use.**
The `trigger_workflow` tool may only trigger n8n workflows that are explicitly registered in
`ssot/bridges/catalog.yaml` with a corresponding `ipai_ai_copilot.n8n_webhook.<workflow_id>`
ir.config_parameter. Any workflow_id not in the allowlist MUST return an error, not attempt
execution. New workflows require a SSOT update and code review before use.

---

## Extension Decision Policy (CE vs OCA vs addon vs Bridge)

Before building or extending any capability, follow this decision tree in order:

### A. Can Odoo CE configuration satisfy the requirement?
- Use `ir.config_parameter`, system settings, or built-in module options.
- **If yes** → Configure. No code needed. Document in `ssot/odoo/settings_catalog.yaml`.

### B. Does an OCA module exist for this capability?
- Search `OCA/*` repos and the OCA app store.
- **If yes and mature (19.0 port available)** → Adopt the OCA module. Pin version in `.gitmodules` or `requirements.txt`. Do not fork or vendor — use `_inherit` overrides if customization is needed.
- **If yes but no 19.0 port** → Mark `[NEEDS PORT]`. File an OCA issue or initiate a port. Use a temporary `ipai_*` shim if blocking, but plan to migrate when port lands.

### C. Is a custom Odoo addon the right approach?
- Only if A and B are exhausted.
- **Naming**: `ipai_<domain>_<feature>` (e.g. `ipai_ai_copilot`).
- **Must**: follow OCA quality standards (pre-commit, manifest, README, tests).
- **Must not**: duplicate functionality available in OCA.

### D. Does the capability require an external service?
- AI/ML inference, OCR, vector search, or any non-Odoo runtime.
- **If yes** → Bridge-first architecture. The Odoo addon (`ipai_*`) is a thin connector; heavy logic runs in the external service (Rule 4: all AI routes through IPAI bridge).
- **Bridge contract**: `contracts/tools/TOOL_SPEC_TEMPLATE.md` (preview → approval → commit; audit envelope; idempotency key).

### E. Tie-breakers
- **EE parity feature** → Prefer OCA path (even partial) over custom addon. Document gap in `ssot/parity/`.
- **AI/ML capability** → Always Bridge (Rule 4: no direct LLM calls from Odoo).
- **OCA/ai surface** → Thin adapter only; no forking OCA modules (Rule 3: tool registry is the ONLY mechanism).
- **Cross-domain integration** → Requires a contract doc per `ssot-platform.md` Rule 9.

### Required artifacts per path

| Path | Required artifact |
|------|-------------------|
| A (Config) | Settings entry in `ssot/odoo/settings_catalog.yaml` |
| B (OCA) | `.gitmodules` pin or `requirements.txt` entry |
| C (Custom addon) | `addons/ipai/ipai_<domain>_<feature>/` with manifest + tests |
| D (Bridge) | Tool spec in `contracts/tools/` + bridge entry in `ssot/bridges/catalog.yaml` |
| E (Parity) | Row in `ssot/parity/ee_to_oca_proof_matrix.yaml` |
