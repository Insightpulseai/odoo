# Schema + Namespace Policy (SSOT)

## Repo namespaces
- `addons/`: ONLY `ipai_*` modules
- `vendor/`: third-party only (OCA, mirrors). NO `ipai_*`
- `runtime/`: compose + env templates + ops scripts
- `infra/`: deployment/ops automation
- `docs/`: contracts + runbooks
- `apps/`, `packages/`: reserved

## Postgres schema namespaces (Supabase-first)
Core platform schemas:
- `core` (tenancy/RBAC)
- `clients` (customers/subscriptions)
- `ops` (runs/events/artifacts/audit)
- `agents` (registry/executions)

Domain schemas allowed (must still attach to tenant model):
- `odoo`, `scout`, `superset`

## Table naming
- snake_case, lower
- no spaces, no caps
