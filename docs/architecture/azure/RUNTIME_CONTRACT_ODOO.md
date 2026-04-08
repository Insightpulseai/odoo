# Runtime Contract — Azure-Hosted Odoo

> Version: 1.0.0
> Last updated: 2026-03-15
> Canonical repo: `odoo`
> Parent doctrine: `docs/architecture/AZURE_ODOOSH_EQUIVALENT_TARGET_STATE.md`

## Purpose

Define the repo-owned runtime contract for the Azure-hosted Odoo stack.

This file governs:
- Addon discovery
- Dependency loading
- Stage-aware runtime expectations
- Shell/debug assumptions
- Smoke validation expectations
- Evidence outputs tied to code/runtime behavior

## Runtime Principle

The runtime substrate may change, but the runtime contract may not drift casually.

```text
Same repo contract.
Same database names.
Same addon discovery rules.
Same dependency rules.
Same smoke expectations.
```

## Canonical Naming

### Databases (underscores — canonical, never renamed)

| Database | Environment | Purpose |
|----------|-------------|---------|
| `odoo_dev` | dev | Clean control development |
| `odoo_dev_demo` | dev (aux) | Showroom/demo data |
| `odoo_staging` | staging | Staging rehearsal |
| `odoo` | production | Production |

Database names are canonical and must not be renamed to match hyphenated environment labels.

### Environments (hyphens — Azure resource/infra labels only)

- `odoo-dev` → hosts `odoo_dev`
- `odoo-staging` → hosts `odoo_staging`
- `odoo-production` → hosts `odoo`

## Addon Contract

### Canonical addon layout

Preferred addon layers:

1. `addons/oca` — OCA community modules
2. `addons/ipai` — IPAI bridge/custom modules
3. `addons/local` — Local overrides (if needed)

### Rules

- OCA-first policy applies
- `ipai_*` modules are for thin bridge / integration behavior
- Addon discovery must remain deterministic
- Addon ordering must be derivable from repo-owned manifest / SSOT files

### Submodule support

The repo may use Git submodules for addon dependencies.

- `.gitmodules` must be valid if present
- Submodule-backed addon directories must satisfy addon discovery rules
- CI must fail if declared submodules are missing or inconsistent

## Python Dependency Contract

Repo-owned Python dependencies must be declared through `requirements.txt` files or an explicitly approved equivalent.

### Rules

- No hidden system-package assumptions
- No undocumented runtime pip installs
- Dependencies must be reproducible from source control
- Dependency changes must be attributable to commit history

## Runtime Shell / Debug Contract

Operator/runtime access must support at minimum:

- Inspect logs
- Run Odoo shell (`odoo-bin shell`)
- Run module install/update commands
- Run smoke checks
- Inspect DB connection/config at runtime where permitted

Supported operational categories:

- Module update (`-u module_name --stop-after-init`)
- Shell-based investigation (`odoo-bin shell -d odoo_dev`)
- Read-only DB diagnostics
- Stage verification
- Migration checks

## Database Contract

The application must assume canonical databases mapped to the environment model.

### Rules

- Dev DB (`odoo_dev`) may be disposable
- Staging DB (`odoo_staging`) must be refreshable from neutralized prod-derived input
- Production DB (`odoo`) is authoritative
- Schema changes must be tracked through code / migrations / install-update flows
- Destructive manual SQL against production is outside the normal contract

## Stage-Aware Safety Contract

### dev (`odoo_dev`)

- Demo data allowed (in `odoo_dev_demo`)
- Outbound email suppressed or redirected to Mailpit (port 1025)
- Destructive integrations disabled by default
- Tests and installability checks are expected

### staging (`odoo_staging`)

- Production-derived but neutralized data
- No real customer-facing outbound email (MailHog sink, port 1025)
- No real payment execution
- Cron jobs disabled or allowlisted
- Final smoke validation expected

### production (`odoo`)

- Authoritative business runtime
- Only approved release candidates deployed
- Monitoring and evidence mandatory

## Smoke Validation Contract

Each deployable candidate must support smoke validation for:

- Runtime boot
- DB connection
- Addon path integrity
- Key HTTP health endpoints (`/web/health`)
- Selected critical module import/install/update path
- No obvious missing dependency failure

## Evidence Contract

Each validated release candidate should reference evidence including:

- Commit SHA
- Stage name and database
- Addon inventory summary
- Dependency summary
- Smoke result summary
- Migration/install/update notes if applicable

## Failure Conditions

A candidate is non-compliant if any of the following are true:

- Addon discovery is nondeterministic
- Required dependencies are not repo-declared
- `.gitmodules` exists but is broken
- Database names drift from canonical values
- No smoke validation path exists
- Runtime evidence cannot be tied to a code revision
