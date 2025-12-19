# Constitution — IPAI Control Center

## Non-negotiables
1. **No Notion integration.** We do not sync/embed Notion or build connectors to Notion.
2. **Clone SaaS UX into Odoo CE 18 + OCA.** The "workspace" experience (docs/wiki/tasks/projects/dashboards) is implemented natively in Odoo CE using OCA modules plus IPAI custom modules.
3. **Layering rule:** Odoo CE → OCA gap-fill → IPAI custom (minimal overrides, inherit/extend only).
4. **Idempotent data + migrations:** all schema/data changes are deterministic and re-runnable.
5. **CI must stay green:** repo-structure, guardrails, parity tests must pass on every PR.
6. **No UI-only hacks:** avoid inline styles in XML; use assets (SCSS) + proper QWeb inheritance with unique xmlids.
7. **Operational first:** observability, audit trails, and automation hooks are first-class requirements.

## Definition of done
- Spec kit complete (this + PRD + Plan + Tasks).
- Modules install cleanly on a fresh DB (docker compose) without restart loops.
- Advisor dashboard + PPM basics render; scores compute; lifecycle works end-to-end.
- All CI checks pass; no merge conflicts in target branch.

## Scope boundaries
- We may integrate with **Supabase, n8n, Mattermost, Superset** (your stack).
- We do **not** build/maintain external SaaS dependencies for the core workflow (Notion excluded).

