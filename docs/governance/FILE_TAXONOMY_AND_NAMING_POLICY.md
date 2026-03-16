# File Taxonomy and Naming Policy

## Purpose

Define canonical file extensions, placement rules, naming rules, and CI enforcement for the repository.

## Core Principles

- One canonical name per concept
- One canonical location per artifact type
- Human-readable docs use Markdown
- Machine-readable SSOT uses YAML or JSON
- Runtime code lives only in its owning plane
- Historical wrong names may remain only in reconciliation notes
- Generated artifacts must declare their generator and be drift-checked

## Canonical Extension Taxonomy

### Human-readable narrative artifacts

- `.md` — architecture docs, runbooks, ADRs, research, spec files

### Machine-readable source of truth

- `.yaml` / `.yml` — SSOT, manifests, workflows, policy, inventory
- `.json` — contracts, indexes, generated inventories, API-facing config
- `.schema.json` — schemas

### Code and runtime artifacts

- `.py` — Odoo modules, tooling, scripts, tests
- `.ts` / `.tsx` — frontend/backend TypeScript and React
- `.sql` — migrations, bootstrap SQL, reporting SQL
- `.xml` — Odoo data/views/security/demo files
- `.csv` — Odoo access/demo/seed data
- `.sh` — shell scripts
- `.conf` — runtime config

### Infrastructure artifacts

- `.tf` — Terraform
- `.bicep` — Azure Bicep
- `.parameters.json` — Azure deployment parameters

### Diagram sources

- `.drawio`, `.mmd`, `.puml` — diagram source
- `.png`, `.svg` — exported/rendered diagram assets

## Placement Rules

### docs/

Allowed: `.md`, diagram source/assets (`.drawio`, `.mmd`, `.puml`, `.png`, `.svg`)

Not allowed: runtime code, primary SSOT config, deploy logic as sole source of truth

### ssot/

Allowed: `.yaml`, `.yml`, `.json`, `.schema.json`

Not allowed: prose-heavy docs, executable scripts, app code

### spec/

Allowed — fixed spec bundle files only:
- `constitution.md`
- `prd.md`
- `plan.md`
- `tasks.md`

### addons/

Allowed: Odoo module code and Odoo-owned assets only (`.py`, `.xml`, `.csv`, `.js`, `.scss`, `.po`, `.pot`)

### infra/

Allowed: IaC, deployment contracts, infra CI (`.tf`, `.bicep`, `.json`, `.yaml`, `.yml`, `.sh`)

### agents/

Allowed: personas, skills, judges, evals, benchmarks, templates

## Naming Rules

### Canonical docs

Use `UPPER_SNAKE_CASE.md` for architecture/governance/reference docs.

Examples: `CANONICAL_URLS.md`, `AZURE_DEVOPS_RUNTIME_STATE.md`

### Machine-readable files

Use `lowercase_snake_case`.

Examples: `azure_devops.yaml`, `org_topology.yaml`

### Directories

Use lowercase kebab-case or fixed canonical names.

Examples: `agent-platform`, `data-intelligence`

### Spec files

Must use exact fixed names: `constitution.md`, `prd.md`, `plan.md`, `tasks.md`

## Canonical Names That Must Not Drift

| Canonical | Forbidden alias |
|-----------|----------------|
| `data-intelligence` | `lakehouse` |
| `platform` | `ops-platform` |
| `design` | `design-system` |
| `addons/oca` | `addons/OCA` |
| `odoo_dev`, `odoo_staging`, `odoo` | any other DB names |

## Historical Reconciliation Rule

Historical names may appear only in:
- migration notes
- reconciliation notes
- audit trail docs

They must not appear in:
- active CI config
- active SSOT values
- active runtime docs
- current README contracts

## Generated Artifact Rule

Generated artifacts must declare their generator and are enforced by CI drift checks.

## CI Enforcement

CI must fail on:
- extension-placement violations
- naming drift
- spec bundle drift
- generated artifact drift
- SSOT/schema validation failures

## Rollout Plan

| Phase | Behavior |
|-------|----------|
| Phase 1 (warn-only) | Log violations, fail only on malformed SSOT and missing spec files |
| Phase 2 (hard fail) | Block PRs on alias drift, bad placement, spec drift |
| Phase 3 (generated drift) | Add generator checks for schema/docs/diagram exports |
