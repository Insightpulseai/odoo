# Codex Prompt: Confluence-Style IPAI Workspace (Odoo 18 CE)

Use this prompt when asking Codex to add a Confluence-like layer on top of the existing ipai_* workspace stack (workspaces, pages, blocks, databases) inside the InsightPulse Odoo 18 CE + OCA monorepo. It extends the Notion-style workspace with spaces, labels, macros, approvals, history, and enterprise links.

---

## Prompt (copy/paste into Codex)

You are Codex working inside the InsightPulse Odoo 18 CE + OCA monorepo with Supabase, n8n, Scout/GenieView, and self-hosted Claude via MCP. You already have ipai_workspace / ipai_workspace_db / ipai_workspace_enterprise / ipai_workspace_ai / ipai_workspace_n8n. Add a Confluence-like layer with spaces, labels, history, comments, approvals, macros, and blueprints. Do not ask questions; make reasonable assumptions and implement end-to-end.

### Modules and models

1) **ipai_confluence_core** (depends on ipai_workspace)
   - `ipai.space`: name, key, description, icon, owner_id, admin_ids, member_ids, is_public, company_id.
   - Link pages to spaces: add `space_id` to `ipai.workspace.page`; constrain pages to a single space or allow global drafts.
   - Menus/views: IPAI / Spaces (tree/kanban), space form showing root pages; server-rendered page tree per space.

2) **Labels & search**
   - `ipai.page.label`: label list with unique names per company; add `label_ids` M2M on `ipai.workspace.page`.
   - Menu IPAI / Labels; show label chips on page form and allow filtering.
   - Controller `/ipai/confluence/search` to search by q, space, label, type across page names and (optionally) text/heading block content; return JSON and basic HTML.

3) **Version history & diff**
   - `ipai.workspace.page.version`: page_id, version_number (auto per page), title snapshot, content_snapshot (JSON of ordered blocks), comment, author_id, created_at.
   - On significant page save: serialize blocks, create version.
   - Actions: view versions, compare with current (basic text diff), restore (replace blocks, create new version). Add "History" tab on page form.

4) **Comments (page + inline)**
   - `ipai.workspace.page.comment`: page_id, parent_id (thread), author_id, body, created_at, updated_at, optional block_id (inline), optional anchor_path for text ranges.
   - UI: comment thread at page bottom; inline comment indicator on blocks with side-panel threads.

5) **Restrictions & approvals**
   - Extend page with `restriction_mode` (inherit_space/custom) and allowed_* user/group M2Ms for view/edit/comment. Record rules enforce access; comment creation respects allowed_comment sets.
   - `ipai.workspace.page.approval`: page_id, requested_by_id, approver_id, status (pending/approved/rejected), comment, requested_at, decided_at; page fields `requires_approval`, `approval_status`.
   - Buttons/wizards: request approval, approve/reject. Integrate with ipai_workspace_n8n emitter for events page.approval.requested/approved/rejected.

6) **Macros & blueprints**
   - Extend block_type with `macro`; payload includes macro_key + macro_params. Macro registry maps macro_key → resolver for context. Baseline macros: children, page_tree, decision_log (DB rows), task_list.
   - QWeb templates render macro contexts.
   - `ipai.workspace.blueprint`: name, key, description, optional space_id, content_schema (JSON page structure), category (meeting_note, decision, incident, policy, blank). "Create from blueprint" clones schema into new page. Seed initial blueprints.

7) **Enterprise linkage**
   - Space conventions: FIN, HR, OPS, CLIENT_* etc. Smart button "Open Space" on project.project, hr.employee, finance PPM entities. Config mapping to pick space/labels.
   - Method `get_or_create_confluence_page()` on key models to locate/create a page under the right space using a blueprint when ref_model/ref_res_id matches; expose smart button "Open IPAI Page".

### Deployment & quality
- Add ipai_confluence_core to addons path and Docker/K8s manifests; env vars via settings (no hard-coded secrets).
- Tests: create space, labeled pages, comments, versions; enforce restrictions; macro resolution.
- Docs: `docs/IPAI_CONFLUENCE_MODE.md` mapping Confluence concepts to IPAI models, setup for spaces/restrictions/blueprints for Finance PPM/HR/projects.
- Keep OCA style, semantic versions in manifests, security split (ir.model.access.csv + groups/rules XML), no core patches, graceful behavior when external services are absent.
