# File Taxonomy and Naming Policy

> **Version**: 1.0.0
> **Scope**: Organization-wide file extension rules, placement rules, and naming doctrine.

## 1. Canonical File Extension Taxonomy

### A. Human-Facing Narrative Docs
- **`.md`**: Architecture docs, runbooks, research, ADRs, README, specs.
  - Allowed in: `docs/`, `spec/`, repo root `README.md`, `agents/knowledge/`
- **`.txt`**: Raw transient notes or imported plain text references.
  - Allowed in: `archive/` or `docs/research/raw/` only.

*Rule: Use `.md` for anything humans are expected to read, review, or approve.*

### B. Machine-Readable Source-of-Truth
- **`.yaml` / `.yml`**: SSOT, manifests, policy, inventory, workflow config.
  - Allowed in: `ssot/`, `.github/workflows/`, `agents/templates/`, `infra/ci/`
- **`.json`**: Contracts, schema, indexes, machine inventories, app config.
  - Allowed in: `contracts/`, `ssot/`, app/package roots, `reports/`
- **`.schema.json`**: JSON Schema contracts.
  - Allowed in: `contracts/`, `schemas/`

*Rule: Prefer `.yaml` for hand-edited config. Prefer `.json` for machine-generated boundaries.*

### C. Code Files
- **`.py`**: Odoo modules, scripts, platform logic (in `addons/`, `scripts/`, `agent-platform/`, `tests/`).
- **`.ts` / `.tsx`**: Web or agent-platform typescript/react logic.
- **`.sh`**: Shell scripts (`scripts/`, `infra/scripts/`, `.githooks/`).
- **`.sql`**: Migrations, reporting SQL (`supabase/migrations/`, `sql/`).
- **`.xml`**: Odoo views/data (`addons/**/views/`, `addons/**/data/`).
- **`.csv`**: Odoo seed data (`addons/**/data/`, `data/seeds/`).

*Rule: Code lives only in its owning plane. No runnable code in `docs/` or `ssot/`.*

### D. Infrastructure and Deployment
- **`.tf`**: Terraform (`infra/terraform/`, `infra/modules/`).
- **`.bicep` / `.parameters.json`**: Azure Bicep (`infra/azure/`).
- **`.yaml`**: CI/CD Pipelines (`.github/workflows/`, `infra/ci/`).
- **`.env.example`**: Example variables (Repo root).
- **`.conf`**: Odoo config (`config/dev/`, `config/prod/`).

### E. Specs and Decisions
Fixed-name files exactness required:
- `spec/<slug>/constitution.md`
- `spec/<slug>/prd.md`
- `spec/<slug>/plan.md`
- `spec/<slug>/tasks.md`

### F. Diagrams
- **`.drawio` / `.mmd` / `.puml`**: Diagram source (`docs/architecture/diagrams/`).
- **`.png` / `.svg`**: Exports (`docs/architecture/diagrams/exported/`, `docs/assets/`).

*Rule: Store the source diagram; do not rely strictly on exported PNGs.*

---

## 2. Directory Placement Rules

- **`docs/`**: Human-readable canonical docs only. No code.
- **`ssot/`**: Machine-readable truth only (`.yaml`, `.json`). No prose docs.
- **`spec/`**: Spec Kit bundle only.
- **`addons/`**: Odoo module code and assets only.
- **`infra/`**: IaC and deployment contracts.
- **`agents/`**: Agent doctrine, evals, templates.
- **`web/` / `platform/`**: App code and runtime config.

---

## 3. Canonical Naming Rules

1. **Directories**: Lowercase kebab-case (e.g., `agent-platform`, `data-intelligence`).
2. **Canonical Docs**: `UPPER_SNAKE_CASE.md` (e.g., `REPO_ACTUAL_VS_TARGET_STATE.md`).
3. **Machine-Readable**: `lowercase_snake_case` (e.g., `ssot/azure/azure_devops.yaml`).
4. **Spec Bundles**: Fixed names (`constitution.md`, `prd.md`, `plan.md`, `tasks.md`).

---

## 4. Drift Prevention & Extinct Terms

- **One Canonical Name**: Do not allow synonyms.
  - `lakehouse` -> **`data-intelligence`**
  - `ops-platform` -> **`platform`**
  - `design-system` -> **`design`**
- **Reconciliation Only**: Historical variants only appear in migration notes, never in active code or SSOT.
- **Generated Annotations**: Any generated artifact must declare its generator at the top of the file.

---

## 5. CI Enforcement Engine

The CI pipeline strictly blocks violations of this policy via `.github/workflows/`:
- `file-taxonomy-check.yml` (Blocks wrong extensions in wrong folders).
- `naming-drift-check.yml` (Blocks forbidden variants like `lakehouse` or `addons/OCA`).
- `spec-kit-enforce.yml` (Blocks incomplete spec bundles).
- `generated-artifact-drift.yml` (Fails if generated docs drift from source).
- `ssot-schema-validate.yml` (Validates shape of JSON/YAML).
