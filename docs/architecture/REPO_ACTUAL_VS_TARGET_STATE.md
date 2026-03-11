# Repo Actual vs Target State

## Purpose

Separate the current real repository state from the intended decomposed target state.

## Actual current state

This repository currently functions as an Odoo-led platform monorepo containing:

- ERP runtime artifacts (`addons/`, `config/`, `docker/`)
- shared infra artifacts (`infra/`)
- platform app artifacts (`platform/`)
- web/public app artifacts (`web/`)
- Supabase/control-plane artifacts (`supabase/`)
- agent/runbook assets (`agents/`)
- automation assets (`automations/`)
- design assets (`design/`)
- lakehouse/analytics assets (`lakehouse/`)
- ops-platform artifacts (`ops-platform/`)

## Canonical current truth

Despite its breadth, the canonical responsibilities that remain authoritative here today are:

- Odoo runtime
- addon stacks (`addons/oca/`, `addons/ipai/`)
- Odoo environment config (`config/dev/`, `config/staging/`, `config/prod/`)
- ERP deployment contracts
- ERP-specific SSOT
- ERP runtime docs/evidence

## Target decomposition

The desired end state is:

| Target repo | Owns |
|---|---|
| `odoo` | ERP runtime, addons, Odoo config, ERP deployment contracts, ERP SSOT |
| `platform` | OdooOps console, platform admin/control-plane apps, Supabase artifacts |
| `infra` | Shared infrastructure, cloud/network/edge, IaC |
| `web` | Public website, apex surfaces |
| `agents` | Shared agent/skill/runbook assets |
| `automations` | Shared workflow assets |
| `design-system` | Shared design assets/tokens |
| `lakehouse` | Databricks and analytics platform |

## What stays in `odoo` after decomposition

- `addons/`
- `config/`
- `docker/`
- ERP-specific `docs/`
- ERP-specific `scripts/`
- ERP-specific `spec/`
- ERP-specific `ssot/`
- `tests/`
- runtime `evidence/`

## What ultimately moves out

- `platform/`
- `web/`
- `infra/`
- `agents/`
- `automations/`
- `design/`
- `lakehouse/`
- `ops-platform/`
- non-ERP `supabase/`

## Runtime contract (normalized)

| Environment | Database | Config | Runtime surface |
|---|---|---|---|
| Local | `odoo_dev` | `config/dev/odoo.conf` | Docker Compose (`colima-odoo`) |
| Staging | `odoo_staging` | `config/staging/odoo.conf` | Azure Container Apps |
| Production | `odoo_prod` | `config/prod/odoo.conf` | Azure Container Apps |

Historical references such as `odoo_core`, `odoo_stage`, `odoo_db`, or bare `odoo` as the canonical production database are non-canonical and should be treated as legacy references only.

## Edge model (normalized)

- **Cloudflare** = authoritative DNS only
- **Azure Front Door** = public application edge for all app surfaces
- **ACA / Azure origins** = backend runtimes
- **Azure Key Vault** = certs/secrets
- **Zoho** = mail

## Interpretation rule

When actual repo contents and older README language conflict, the actual root tree takes precedence for classification, while ERP runtime contracts remain the canonical operational baseline.
