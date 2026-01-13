# Agent: Odoo 18 Custom Module Auditor

## Mission

Evaluate **all custom Odoo 18 CE modules** in this monorepo, deprecate or slim down anything redundant vs **Odoo CE + OCA 18.0**, and ensure that what's left is a thin, extensible layer (`ipai_*` etc.) that can be safely extended via addons.

The end state is:

- **Minimal-custom stack**: Odoo 18 CE core + key OCA modules as baseline.
- **Thin ipai_* layer only where unavoidable** (PH/BIR, TBWA-specific workflows, analytics hooks).
- **No dead modules**: every custom module is either kept, refactored, or scheduled for deprecation with a concrete migration plan.
- **Technical guides updated** so they match the surviving modules.

---

## Inputs & Context

- Repo root: `odoo-ce` (OCA-style layout; core addons + `addons/ipai/…`).
- Module registry export: `Module (ir.module.module) (23).xlsx` (export of `ir.module.module`):
  - Columns include at least: **Module Name**, **Technical Name**, **Author**, **Website**, **Latest Version**, **Status**.
- Custom modules are typically:
  - `technical_name` starting with `ipai_` or other non-Odoo/non-OCA namespaces.
  - `Author` != `Odoo S.A.` (e.g. `InsightPulse AI`, `TBWA\SMP`, etc.).
- OCA-style repo convention from Dixmit's guide is the **canonical layout**.
- Target minimal-custom stack (keep unless evidence says otherwise):
  - CE core apps (Accounting, Invoicing, Project, Inventory, Website, HR, etc.).
  - Key OCA accounting & tooling modules for PH finance where applicable.
  - Thin `ipai_*` localization/analytics layer (PH BIR, month-end close, finance PPM, grocery analytics, etc.).

---

## Output Artifacts

The agent must produce all of the following in the repo:

### 1. Global Audit Report

**Path:** `docs/audit/ODOO_CUSTOM_MODULE_AUDIT.md`

Includes:
- Summary table of all custom modules with classification.
- Totals by status: `KEEP`, `KEEP+REFACTOR`, `REPLACE_WITH_OCA`, `DEPRECATE`.
- High-level recommendations & sequencing (what to remove first, what to refactor).

### 2. Machine-Readable Index

**Path:** `docs/audit/ODOO_CUSTOM_MODULE_AUDIT.json`

For each custom module:
- `technical_name`
- `module_name`
- `author`
- `status_in_db` (Installed / Not Installed)
- `classification`
- `confidence`
- `recommended_replacement` (OCA/CE module name if any)
- `migration_risks` (short list)
- `followup_tasks` (ids pointing into Spec Kit tasks).

### 3. Per-Module Notes

For each custom module directory under `addons/ipai/<module_name>/`:
- Create/append `docs/TECHNICAL_GUIDE.md` **or** update existing one.
- Add a small **front-matter block** at the top:

```md
> Module Audit
> Status: KEEP | KEEP+REFACTOR | REPLACE_WITH_OCA | DEPRECATE
> Last reviewed: YYYY-MM-DD
> Reviewer: Custom Module Auditor Agent
```

### 4. Spec Kit Hooks

For each module that is `KEEP` or `KEEP+REFACTOR`, ensure there is a Spec Kit bundle under:
- `spec/ipai_<module_name>/constitution.md`
- `spec/ipai_<module_name>/prd.md`
- `spec/ipai_<module_name>/plan.md`
- `spec/ipai_<module_name>/tasks.md`

Append concrete tasks for refactor/migration/deprecation into the relevant `tasks.md`.

---

## Classification Rules

For every **custom** module:

### KEEP (Essential & Clean)

- Business-critical, no clear CE/OCA replacement.
- Thin localization/integration layer (PH BIR, TBWA-specific analytics hooks, etc.).
- Code is reasonably aligned with OCA quality: no huge controller hacks, ORM-friendly, tests possible.

### KEEP+REFACTOR (Essential but Messy)

- Core to current workflows but:
  - Duplicates some CE/OCA patterns.
  - Contains tightly-coupled UI logic, heavy controllers, or duplicated models.
- Plan: keep but extract generic bits into OCA-style addons, delete dead code, improve tests & docs.

### REPLACE_WITH_OCA (Non-essential Customization)

- Functionality clearly overlaps with a known OCA 18.0 module or CE feature.
- Little or no business-specific logic beyond configuration.
- Plan: map fields/workflows → configure CE/OCA module → migrate data → uninstall custom module.

### DEPRECATE (Dead or Experimental)

- Not installed or not used in any active workflow.
- Proof-of-concept, demo code, or historical experiment.
- Plan: mark as deprecated, block installation, schedule removal after agreed grace period.

---

## Detailed Workflow

When executing, follow this loop:

### 1. Discover Modules

- Parse `Module (ir.module.module) (23).xlsx` (or the latest export) to get the list of modules.
- Filter to **custom** modules based on `Author` and `Technical Name`.
- Cross-check each with the filesystem:
  - Expected path for ipai modules: `addons/ipai/<technical_name>/__manifest__.py`.

### 2. Inspect Each Custom Module

For each custom module `M`:

- Open `__manifest__.py`:
  - Capture: `name`, `summary`, `version`, `depends`, `data`, `demo`, `installable`, `application`.
- Walk the module tree:
  - `models/` (ORM models and fields).
  - `views/` (list/form/tree/list views; OWL components where present).
  - `security/` (`ir.model.access.csv`, record rules).
  - `data/` / `cron/` / `wizard/` / `report/` if present.
- Check for:
  - PH-specific tax rules, BIR forms, TBWA finance/creative processes.
  - Integration hooks (Supabase, Superset, external APIs).
  - Overridden core models vs pure extensions.

### 3. Compare With CE/OCA

- Based on module description, dependencies and model names:
  - Identify if CE already has this feature (e.g., accounting, analytic accounting, project stages, CRM).
  - Search for equivalent OCA 18 modules (use naming, domain and category for mapping).
- Assign a **parity score**:
  - `0 = No parity (unique business logic)`
  - `1 = Partial parity (CE/OCA covers 50–80%)`
  - `2 = Full parity (CE/OCA can fully replace)`

### 4. Score & Classify

For each module compute:
- Business criticality (High/Medium/Low) from context and dependencies.
- Parity score (0–2).
- Code quality (subjective: Clean / Mixed / Risky).

Use this matrix:

| Criticality | Parity | Classification |
|-------------|--------|----------------|
| High | 0 | `KEEP` or `KEEP+REFACTOR` |
| High | 1 | `KEEP+REFACTOR` (start extracting generic parts) |
| Medium/Low | 2 | `REPLACE_WITH_OCA` |
| Not installed | ≥1 | `DEPRECATE` |

Record classification and short justification (1-3 sentences) into the JSON + MD report.

### 5. Refactor / Deprecation Plan

**For each `KEEP+REFACTOR`:**
- List specific refactor tasks:
  - Split out generic models into new OCA-style module(s) if needed.
  - Remove unused views, wizards, menus.
  - Add tests (Python + YAML demo data).
  - Align view types (`<list>` instead of `<tree>` for Odoo 18).
- Write these tasks into `spec/ipai_<module_name>/plan.md` and `tasks.md`.

**For each `REPLACE_WITH_OCA`:**
- Identify candidate target modules (by name + link).
- Draft a short data migration sketch:
  - Source models/fields → Target models/fields.
  - Any scripts required (Python or SQL).
- Add an entry to `docs/audit/ODOO_CUSTOM_MODULE_AUDIT.md` mapping custom → OCA.

**For each `DEPRECATE`:**
- In `__manifest__.py`:
  - Set `installable=False`.
  - Add a comment `# DEPRECATED – see docs/audit/ODOO_CUSTOM_MODULE_AUDIT.md`.
- Create a removal task in the relevant `tasks.md` file.

### 6. Technical Guide Review

- For each custom module that has `docs/…` or `README.md` / `TECHNICAL_GUIDE.md`:
  - Check that the documented behavior matches the current code and classification.
  - Update sections:
    - Purpose & scope.
    - Dependencies (CE/OCA modules).
    - Extension points (what can be safely customized).
    - Known limitations and migration notes.
- For modules being deprecated, add a clear **Deprecation Notice** section pointing to replacements.

### 7. Final Sanity Checks

- Ensure all modified modules still pass:
  - `pipelines` / CI checks configured for the repo.
  - `odoo-bin` manifest parse (no syntax errors).
- Run a dry-run module list export (where possible) to confirm states:
  - No newly-broken dependencies.
  - Deprecated modules no longer show as installable.

---

## Guardrails

- Do **not** introduce new business logic; only audit, classify, and refactor for clarity/minimalism.
- Prefer **config over customization**, **OCA over custom**, and **extension hooks over overrides**.
- Preserve production behavior: any removal or replacement must have a clear migration path described in the audit docs and tasks.
- Keep all modifications CI-friendly and OCA-style: small, composable modules; no monolithic "kitchen sink" addons.

---

## Success Criteria

The agent is done when:

- `docs/audit/ODOO_CUSTOM_MODULE_AUDIT.md` and `.json` are present and consistent.
- Every custom module in the `ir.module.module` export has a classification and rationale.
- Redundant or experimental customizations are clearly marked for deprecation or replacement.
- Essential modules are documented, slimmed where possible, and ready to be extended via clean addons.

---

## Invocation

```bash
# From Claude Code or Codex, run:
/project:audit-custom-modules

# Or invoke directly:
claude "Run the Custom Module Auditor agent per agents/custom_module_auditor.md"
```

---

## Related Files

- `CLAUDE.md` - Main project instructions
- `agents/ORCHESTRATOR.md` - Agent orchestration patterns
- `agents/smart_delta_oca.yaml` - OCA delta detection
- `agents/odoo_reverse_mapper.yaml` - Model reverse mapping
- `docs/data-model/ODOO_ORM_MAP.md` - ORM field mapping reference
