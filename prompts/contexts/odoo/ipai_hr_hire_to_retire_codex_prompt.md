# Codex Prompt: IPAI Hire-to-Retire BPMN + DOLE/SLA Integration (Odoo 18 CE)

Use this prompt when asking Codex to ingest the Hire-to-Retire BPMN + DOLE/SLA draft and wire it into the IPAI workspace/docs stack (ipai_workspace, ipai_confluence_core, ipai_docsaurus) inside the InsightPulse Odoo 18 CE + OCA monorepo.

---

## Prompt (copy/paste into Codex)

You are Codex working inside the InsightPulse Odoo 18 CE + OCA monorepo. Integrate the Hire-to-Retire BPMN draft (Philippines) as structured data, workspace pages, and docs, reusing the ipai_* stack (ipai_workspace, ipai_confluence_core, ipai_docsaurus). Do not ask questions; make reasonable assumptions and ship end-to-end.

### Source of truth
- HTML reference: `docs/hr/hire_to_retire/Hire-to-Retire BPMN Process - DOLE Compliance & SLA Guide.html` contains the BPMN, swimlanes, and SLA notes.
- Statutory vs internal SLA: DOLE 30-day final pay rule; internal TBWA SLAs (7-day last pay, 5-day clearance) are more favorable and must be preserved.

### New module: ipai_hr_hire_to_retire
Depends on hr, ipai_workspace, ipai_docsaurus, and optionally ipai_confluence_core.

Models:
- `ipai.hr.process`: name (default “Hire-to-Retire (Philippines)”), code `hire_to_retire_ph`, description, is_active.
- `ipai.hr.process.stage`: process_id, name (Attract & Hire, Onboarding, Active Employment, Movement, Offboarding, Post-Exit), sequence, bpmn_ref.
- `ipai.hr.swimlane`: process_id, name (HR, People Manager, Finance/Payroll, IT/Assets, Employee, etc.), role_xml_id.
- `ipai.hr.process.step`: process_id, stage_id, swimlane_id, name, code, description, is_critical, has_sla.
- `ipai.hr.sla_rule`: process_id, step_id, name, rule_type (statutory/internal/practice), days_limit, description, legal_citation, reference_text, is_more_favorable_than_statutory.

Seed data:
- DOLE final pay ≤30 days (statutory) with citation/reference_text from the HTML.
- TBWA 7-day last pay and 5-day clearance (internal/practice) flagged as more favorable than statutory.

### Workspace integration (ipai_workspace)
- Create a master workspace page “Hire-to-Retire | DOLE Compliance & SLA Guide”.
- Create child pages per stage (Stage 1–6) with headings/bullets/callouts summarizing activities and SLAs.
- Extend pages with process_id/stage_id links to the HR models.
- Use callouts to distinguish statutory (DOLE) vs internal SLA content; apply labels like DOLE/statutory/internal where appropriate.

### Docs integration (ipai_docsaurus)
- Create `ipai.docs.project` code `hire-to-retire-hr-ph`, name “Hire-to-Retire HR Process (PH)”, description from HTML.
- Create version v1.0 (slug `current`, is_current=True).
- Map workspace pages to `ipai.docs.page` entries with sections (Overview, Stages, DOLE & SLA Rules), slugs (e.g., `stage-5-offboarding-final-pay`), sidebar labels/positions.
- On the HR process form, add an action “Generate Docsaurus Markdown” to run `workspace_page_to_markdown` for linked doc pages and (optionally) trigger export/webhook.

### BPMN assets
- Add fields on `ipai.hr.process`: `bpmn_drawio_attachment_id`, `bpmn_image_attachment_id`.
- Provide `tools/import_hire_to_retire_bpmn.py` to read the HTML, attach diagram assets, and link attachments to the process.
- Allow MD/MDX export to embed the BPMN image placeholder in the overview page.

### SLA visualization
- Tree/kanban views for `ipai.hr.sla_rule`, grouped by rule_type with badges for statutory vs internal.
- Smart buttons to open related workspace/doc pages; show DOLE reference_text and the 30-day rule prominently.

### Quality & tests
- Manifests with semantic versioning; security split (ir.model.access.csv + groups/rules XML); OCA style; no core patches.
- Demo/data XML for the base process, stages, swimlanes, SLA rules, workspace pages, and docs mappings.
- Tests (e.g., `test_process_and_sla_structure`) asserting process exists, stages ≥5, and SLA rules for 30-day/7-day/5-day entries with correct types/flags.
- CI: include module in install/test matrix; fail softly if optional modules are absent.

### Deployment & integrations
- Keep external endpoints/env vars configurable (no secrets). Wire to ipai_docsaurus export/n8n patterns for static docs if present.
- Keep behavior additive and idempotent; do not alter business data beyond this module’s scope.
