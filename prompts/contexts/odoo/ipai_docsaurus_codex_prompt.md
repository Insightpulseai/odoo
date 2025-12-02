# Codex Prompt: Docusaurus-Style IPAI Docs (Odoo 18 CE)

Use this prompt when asking Codex to build a Docusaurus-like documentation layer on top of ipai_workspace (and optional ipai_confluence_core) inside the InsightPulse Odoo 18 CE + OCA monorepo. It adds versioned docs projects, sidebars, Markdown/MDX export, and an n8n/GitHub-driven static-site pipeline.

---

## Prompt (copy/paste into Codex)

You are Codex working inside the InsightPulse Odoo 18 CE + OCA monorepo with Supabase, n8n, Scout/GenieView, and self-hosted Claude via MCP. You already have ipai_workspace / ipai_workspace_db / ipai_workspace_enterprise / ipai_workspace_ai / ipai_workspace_n8n (and optionally ipai_confluence_core). Add a Docusaurus-like docs engine with projects, versions, sections, doc pages, sidebar export, Markdown/MDX conversion, and Git/n8n integration. Do not ask questions; make reasonable assumptions and implement end-to-end.

### Module: ipai_docsaurus
Depends on ipai_workspace and preferably ipai_confluence_core.

**Doc models**
- `ipai.docs.project`: name, code (unique), description, default_version_id, repo_url, docs_folder (default "docs"), sidebars_file (default "sidebars.js"/"sidebars.ts"), n8n_export_webhook_url, n8n_export_token.
- `ipai.docs.version`: project_id, name, slug, is_current, is_released, branch, build_target.
- `ipai.docs.section`: project_id, optional version_id, name, sidebar_id, order.
- `ipai.docs.page`: workspace_page_id (unique), project_id, version_id, section_id, slug, sidebar_label, sidebar_position, is_index, route_path (computed), include_in_search, markdown_snapshot, last_exported_at, last_exported_by_id.

Views/menus: IPAI / Docsaurus / Projects, Versions, Sections, Pages. Smart button on ipai.workspace.page to create/view doc mapping.

### Markdown/MDX conversion
- Helper `workspace_page_to_markdown(page)` (pure Python) mapping block types: heading → #/##/###, text → paragraphs (with basic bold/italic/links if present), todo → - [ ] / - [x], callout → blockquote or MDX `<Callout>`, divider → `---`, embed → link/MDX embed, db_view → note (`> [Database view omitted in docs]`), ai → last_response as Markdown.
- Button "Generate Markdown" on ipai.docs.page stores markdown_snapshot + timestamps.

### Sidebar & export
- `build_sidebar_structure(project_id, version_id)` returns internal dict matching Docusaurus sidebars grouped by section + sidebar_position.
- Controller `/ipai/docsaurus/export/<int:project_id>/<int:version_id>` returns JSON with project/version metadata, docs array (slug/path/markdown), sidebars structure, and optional search_index.
- Export JSON drives an external CLI or n8n flow to write .md files and sidebars.js/ts into a Docusaurus repo.

### Git/n8n integration
- Server action "Trigger Docs Export" on ipai.docs.project posts export JSON to n8n_export_webhook_url with token. n8n flow clones/pushes Docusaurus repo, writes markdown + sidebars, triggers build (Vercel/Netlify/GH Pages).
- CI test: demo project/version export, ensuring markdown conversion and sidebar JSON are well-formed.

### Product docs linkage
- Create projects for Finance PPM, Scout/GenieView, SariCoach, etc.; map workspace pages to ipai.docs.page per version. Smart buttons from business models to open internal doc page and show external route pattern.
- Support Supabase/MDX references (e.g., `<ChartPreview id="..."/>`) via markdown conversion/notes.

### Search & index
- Internal search view over ipai.docs.page (filter by project/version/slug/labels via workspace page labels).
- Helper `build_search_index(project_id, version_id)` producing route/title/headings/content_snippet list; include in export JSON for Algolia-like ingestion.

### Quality & constraints
- OCA style, semantic versions in manifests, no core patches, split security (ir.model.access.csv + groups/rules XML).
- Env vars/settings for external endpoints; no hard-coded secrets. Exports are additive/idempotent; no business data mutation.
- Add ipai_docsaurus to Docker/K8s addons path and CI matrix. Provide minimal docs describing model graph and export flow.
