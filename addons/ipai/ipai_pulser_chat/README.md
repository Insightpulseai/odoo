# Pulser Chat Shell

Thin Odoo-side shell for the Pulser assistant.

## Authority

- Product authority: `spec/pulser-odoo/prd.md`
- Release-scope authority: `ssot/release/go-live-scope-matrix.yaml`

## Ownership split

- `odoo` owns:
  - Owl systray entry
  - chat drawer UI
  - authenticated user/company/record context handoff
  - optional proxy to the external Pulser backend
- `platform` and `agent-platform` own:
  - model/provider routing
  - tool and MCP policy
  - orchestration
  - memory and eval control
- `data-intelligence` owns:
  - retrieval and governed semantic grounding

## Optional integrations

- Reuse `OCA/ai` only if a bridge abstraction is actually needed.
- Prefer a separate adapter layer for `ai_oca_bridge` instead of baking chatter-first assumptions into the global widget.
- Use Azure sample repos as backend pattern sources only; do not paste their frontend code into Odoo.
