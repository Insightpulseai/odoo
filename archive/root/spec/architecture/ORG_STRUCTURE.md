# Org Structure Spec: InsightPulseAI Odoo

## Level 3 Canonical Org Structure

| Level 2 (Anchor) | Level 3 (Functional Block)           | Component / Responsibility                        |
| ---------------- | ------------------------------------ | ------------------------------------------------- |
| `addons/`        | `oca/`                               | OCA parity modules; EE-replacement layer          |
| `addons/`        | `ipai/`                              | Integration bridges, AI glue, platform adapters   |
| `addons/`        | `local/`                             | Minimal local customizations where needed         |
| `config/`        | `dev/`, `staging/`, `prod/`          | Environment-as-code runtime configs               |
| `docker/`        | `compose/`, Dockerfiles              | Local/runtime container contracts                 |
| `scripts/`       | `dev/`, `ci/`, `odoo/`               | Bootstrap, validation, rendering, CI helpers      |
| `ssot/`          | `odoo/`                              | Addon inventory, ordering, parity baseline, locks |
| `supabase/`      | `migrations/`, `functions/`          | Control-plane schema and Edge Functions           |
| `infra/`         | `deploy/`, `terraform/` or other IaC | Environment provisioning and release artifacts    |
| `spec/`          | `architecture/`, feature bundles     | Contracts, PRDs, plans, tasks                     |
| `docs/`          | `architecture/`, `development/`      | Human-readable guidance and evidence              |

## Vertical Decomposition

```text
Insightpulseai/odoo
├── addons/
│   ├── oca/      # OCA parity layer
│   ├── ipai/     # Integration bridges / glue
│   └── local/    # Minimal repo-local custom addons
├── config/
│   ├── dev/
│   ├── staging/
│   └── prod/
├── docker/
│   ├── compose/
│   ├── Dockerfile.dev
│   ├── Dockerfile.prod
│   └── Dockerfile.test
├── scripts/
│   ├── ci/
│   ├── dev/
│   └── odoo/
├── ssot/
│   └── odoo/
│       ├── addons.manifest.yaml
│       ├── oca-baseline.yaml
│       └── oca.lock.ce19.json
├── supabase/
│   ├── migrations/
│   └── functions/
├── infra/
│   ├── deploy/
│   └── terraform/
├── spec/
│   ├── architecture/
│   └── <feature>/
└── docs/
    ├── architecture/
    └── development/
```

## Key Boundary Rules

### 1. Addon Isolation

No non-Odoo app/runtime code in `addons/` (e.g., no Next.js apps, no standalone TS bundles, no Supabase app logic).

### 2. OCA-First Parity Policy

`addons/ipai/*` must not duplicate parity functionality already satisfied by `addons/oca/*`.

### 3. Single Runtime Contract

Only one canonical local runtime contract centered on root `docker-compose.yml`, `config/dev/odoo.conf`, and `ssot/odoo/*`.

### 4. SSOT Before Derived Config

Rendered configuration files must derive from `ssot/odoo/*` as their authoritative source.
