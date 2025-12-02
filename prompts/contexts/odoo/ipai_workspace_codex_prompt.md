# Codex Prompt: IPAI Notion-Style Workspace (Odoo 18 CE)

Use this prompt when asking Codex to implement or extend the IPAI Notion-style workspace inside the InsightPulse Odoo 18 CE + OCA monorepo. It is written to align with ongoing deployment initiatives (Supabase, n8n, Scout/GenieView, AI gateway) and to keep the ipai* naming scheme consistent.

---

## Prompt (copy/paste into Codex)

You are Codex working inside the InsightPulse Odoo 18 CE + OCA monorepo. Implement and wire the ipai_* workspace modules to behave like a Notion-style system that integrates with the current deployment stack (Supabase + pgvector, n8n automations, Scout/GenieView analytics, AI gateway via MCP/Claude). Do not ask questions; make reasonable assumptions and deliver end-to-end code.

### Base conventions
- Module prefix: ipai_*
- Model prefix: ipai.* (e.g., ipai.workspace, ipai.workspace.page)
- OCA style, semantic versioning in manifests, no core patches.
- Keep external endpoints/env vars configurable (no credentials in code).

### Modules to deliver
1) **ipai_workspace**: workspaces, pages, blocks (block types: text, heading, todo, callout, divider, embed, file, db_view, ai); JSON payload per block; menus + backend views; access rules based on owner/members/company and is_private.
2) **ipai_workspace_db**: databases/properties/rows/views (EAV JSON); block_type `db_view` renders a basic table; menus + views; optional backing_model for hybrid Odoo relations.
3) **ipai_workspace_enterprise**: link key business objects (project.project, hr.employee, account.move, hr.expense or sheet) with ipai_workspace_page_id, notebook tab embedding the page, helper ensure_ipai_workspace_page().
4) **ipai_workspace_ai**: block_type `ai` with prompt_template, input_refs, last_response, last_run_at; controller /ipai/ai/workspace/ask that queries Supabase pgvector + forwards to AI gateway; env-driven endpoints; button/action to drop AI response into a page.
5) **ipai_workspace_n8n**: res.config.settings for n8n_base_url + webhook_token; outbound POST on create/write/unlink of pages/blocks/db rows to {base}/webhook/ipai-workspace; inbound controller /ipai/workspace/n8n/hook for authorized updates.

### Deployment linkage
- **Supabase**: use env vars IPAI_SUPABASE_URL, IPAI_SUPABASE_SERVICE_KEY; helpers for pgvector similarity on pages + DB rows; fail gracefully if unset.
- **n8n**: default base https://n8n.insightpulseai.net/; emit events with model, id, changes, user_id, company_id; accept inbound payloads with shared secret.
- **Scout/GenieView**: allow database properties to store Scout identifiers (e.g., scout_brand_id); document how pages provide narrative over Supabase dashboards.
- **Finance PPM / HR**: auto-create workspace pages on project/employee creation; expose "Open IPAI Workspace" actions; keep financial data authoritative in existing models.

### Quality gates
- Add security/ir.model.access.csv per module; split groups/security XML if needed.
- Backend views with sensible defaults; basic QWeb/OWL placeholders are fine.
- Graceful defaults when external services are missing (log warnings, no crashes).
- Wire modules into Docker/compose/K8s manifests and CI test matrix; expose required env vars.

### Deliverables
- Module scaffolds under addons/ with manifests, models, views, security, controllers/helpers as needed.
- Minimal docs (IPAI_WORKSPACE.md) explaining the model graph, integrations, env vars, and example n8n flow triggers.
- Smoke tests or demo data creating a workspace, page, block, database, row, and verifying enterprise links.

