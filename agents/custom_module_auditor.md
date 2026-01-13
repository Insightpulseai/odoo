# Agent: Odoo 18 Custom Module Auditor (Minimal 2-Module Policy)

## Mission

Enforce a **brutally minimal custom stack** for Odoo 18 CE + OCA:

**Only these custom IPAI modules are allowed to survive:**

- `ipai_bir_compliance` – PH tax localization (BIR forms, 2307, Alphalist, RELIEF).
- `ipai_finance_ppm` – PPM reporting & dashboards **beyond** what CE Project + OCA provide.

Everything else must be either:

- Replaced by **CE/OCA 18.0**; or
- Explicitly **deprecated** with a clear removal plan.

The auditor must review all custom modules, classify them, and update docs/specs accordingly.

---

## Canonical Minimal Stack

### 1. CE Core (KEEP, not audited as custom)

- `account`, `sale`, `purchase`, `stock`, `project`, `hr_expense`, `website` (if used)

### 2. OCA Modules (Preferred, not custom)

Use OCA instead of custom whenever possible:

- `account_financial_report`
- `mis_builder`
- `project_timeline`
- `project_budget`
- Other standard OCA 18.0 modules as needed (no IPAI clone of them).

### 3. Essential IPAI Modules (ONLY 2 ALLOWED)

| Module | Why Essential |
|--------|---------------|
| `ipai_bir_compliance` | PH tax localization: BIR forms, 2307, Alphalist, RELIEF, etc. |
| `ipai_finance_ppm` | Project portfolio metrics & dashboards not covered by CE/OCA. |

> The default assumption for any other IPAI/custom module is: **NOT ESSENTIAL**.

---

## Classification Rules (Hard Mode)

For **every custom module** (non-CE, non-OCA):

### Whitelist (Automatic KEEP)

1. If `technical_name` is exactly:
   - `ipai_bir_compliance` → `KEEP`
   - `ipai_finance_ppm` → `KEEP+REFACTOR` (ensure it is strictly PPM analytics, no generic project duplication)

### Everything Else

2. For **all other custom modules**:

   - If functionality is available via CE/OCA:
     - `REPLACE_WITH_OCA`
   - If it's styling, branding, dev studio, workspace shell, AI infra, TBWA-only UX, integrations that are not in active use:
     - `DEPRECATE`
   - If it's critical and no OCA equivalent exists, but not in the 2-module whitelist:
     - Temporary `KEEP+REFACTOR`, with a mandatory **migration-out plan** (merge into one of the 2 kept modules, or replaced by OCA within a defined window).

### Categories Treated as NON-ESSENTIAL by Default

| Category | Modules | Default Classification |
|----------|---------|------------------------|
| **Platform & Branding** | `ipai_dev_studio_base`, `ipai_workspace_core`, `ipai_ce_branding`, similar | `DEPRECATE` |
| **Orchestration / Approvals** | `ipai_close_orchestration`, `ipai_approvals` | `REPLACE_WITH_OCA` (use `account_cutoff_*`, `*_tier_validation`) |
| **AI Infrastructure** | Any `ipai_*` purely for AI, prompts, chat, agents | `DEPRECATE` |
| **Integrations** | Superset, Mattermost, n8n connectors | `DEPRECATE` (unless proven actively used) |
| **TBWA-specific** | TBWA branding/themes, agency-only workflows | `DEPRECATE` (not generic PH localization) |
| **SaaS / Multitenancy** | `ipai_saas_tenant`, `ipai_tenant_core` | `DEPRECATE` (unless multi-tenant SaaS is live) |

---

## Inputs & Context

- Repo root: `odoo-ce` (OCA-style).
- Module registry export: `Module (ir.module.module) (23).xlsx`.
- Custom modules are:
  - `technical_name` starting with `ipai_` or other non-Odoo/non-OCA prefixes.
  - `author` not `Odoo S.A.` or OCA.

---

## Outputs

### 1. Global Audit Report

**Path:** `docs/audit/ODOO_CUSTOM_MODULE_AUDIT.md`

- Table of all **custom** modules with:
  - `technical_name`
  - `status_in_db` (Installed / Not Installed)
  - `classification` (`KEEP`, `KEEP+REFACTOR`, `REPLACE_WITH_OCA`, `DEPRECATE`)
  - `justification` (1–3 lines)
- Summary:
  - How many custom modules → **2 kept** (target).
  - List of modules replaced by CE/OCA.
  - List of modules to deprecate and remove.

### 2. Machine-Readable Index

**Path:** `docs/audit/ODOO_CUSTOM_MODULE_AUDIT.json`

For each custom module:

```json
{
  "technical_name": "ipai_example",
  "module_name": "IPAI Example",
  "author": "InsightPulseAI",
  "status_in_db": "Installed",
  "classification": "DEPRECATE",
  "confidence": "high",
  "recommended_replacement": "OCA module_name or null",
  "followup_tasks": ["task-id-1", "task-id-2"]
}
```

### 3. Per-Module Audit Banner

For each custom module directory (`addons/ipai/<module>/`):

- Create or update `docs/TECHNICAL_GUIDE.md` (or `README.md`) with:

```md
> Module Audit
> Status: KEEP | KEEP+REFACTOR | REPLACE_WITH_OCA | DEPRECATE
> Last reviewed: YYYY-MM-DD
> Reviewer: Custom Module Auditor Agent
```

- For deprecated modules, add a **Deprecation Notice** section with:
  - Target removal version.
  - Replacement (if any).

### 4. Spec Kit Alignment

For `ipai_bir_compliance` and `ipai_finance_ppm` **only**:

- Ensure spec bundles exist:

```
spec/ipai_bir_compliance/constitution.md
spec/ipai_bir_compliance/prd.md
spec/ipai_bir_compliance/plan.md
spec/ipai_bir_compliance/tasks.md

spec/ipai_finance_ppm/constitution.md
spec/ipai_finance_ppm/prd.md
spec/ipai_finance_ppm/plan.md
spec/ipai_finance_ppm/tasks.md
```

- For any other custom module:
  - If `KEEP+REFACTOR` (temporary), add explicit tasks to merge/migrate into the 2 core modules or CE/OCA.
  - Otherwise, tasks for deprecation and removal.

---

## Workflow

### 1. Discover & Filter

- Parse `Module (ir.module.module) (23).xlsx`.
- Identify all non-Odoo / non-OCA modules.
- Mark `ipai_bir_compliance` and `ipai_finance_ppm` as hard "keep-candidates".

### 2. Inspect Each Custom Module

For each module:

- Parse `__manifest__.py`:
  - `name`, `summary`, `version`, `depends`, `installable`.
- Inspect `models/`, `views/`, `security/`, `data/`, `wizard/`, `report/`.
- Decide if covered by CE/OCA:
  - Project stages/milestones/dependencies → CE `project`.
  - Gantt → OCA `project_timeline`.
  - Budgets → OCA `project_budget`.
  - Reports → OCA `mis_builder`, `account_financial_report`, etc.

### 3. Classify (using Minimal Policy)

Apply the rules:

- `ipai_bir_compliance` → `KEEP`.
- `ipai_finance_ppm` → `KEEP+REFACTOR` (ensure it's strictly PPM dashboards, not generic project duplication).
- Anything else:
  - If CE/OCA covers it → `REPLACE_WITH_OCA`.
  - If branding/platform/AI/integration cruft → `DEPRECATE`.
  - Only in truly exceptional cases: `KEEP+REFACTOR` with migration-out plan.

### 4. Refactor / Replacement Plans

**For `KEEP+REFACTOR`:**

- List concrete refactor tasks:
  - Remove duplicated CE/OCA functionality.
  - Restrict scope to what CE/OCA cannot do (PH tax, PPM analytics).
  - Add/align tests and technical guide.

**For `REPLACE_WITH_OCA`:**

- Identify OCA/CE module(s) to use instead.
- Sketch data migration: source models/fields → target.

**For `DEPRECATE`:**

- In `__manifest__.py`:
  - `installable = False`
  - Add comment: `# DEPRECATED – see docs/audit/ODOO_CUSTOM_MODULE_AUDIT.md`
- Add removal tasks in Spec Kit.

### 5. Update Docs & Commit

- Write `ODOO_CUSTOM_MODULE_AUDIT.md` and `.json`.
- Update per-module `TECHNICAL_GUIDE.md`.
- Ensure Spec Kits exist and include tasks for refactor/removal.
- Run tests / linters / OCA checks.

---

## Guardrails

- **No new business logic.** Only audit, classify, and plan refactor/removal.
- Always prefer: **CE first → OCA second → IPAI last**.
- Target state: **exactly 2 custom IPAI modules** providing:
  - PH tax localization (`ipai_bir_compliance`).
  - PPM reporting/dashboards beyond CE/OCA (`ipai_finance_ppm`).

---

## Success Criteria

The agent is done when:

- `docs/audit/ODOO_CUSTOM_MODULE_AUDIT.md` and `.json` are present and consistent.
- Custom module count: **89 → 2** (or justified exceptions with migration-out plans).
- All other modules are either:
  - Marked `REPLACE_WITH_OCA` with identified replacements.
  - Marked `DEPRECATE` with `installable=False` set.
- Spec Kits exist for the 2 kept modules.
- Technical guides updated with audit banners.

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
