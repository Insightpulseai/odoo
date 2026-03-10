# Constitution: Odoo.sh Next (API-First Odoo CI + Hosting)

## 1) Purpose

Build the best-in-class continuous delivery platform for Odoo (Community + Enterprise) that:

- Treats Git as the source of truth for code and environment topology
- Creates reproducible, auditable deploys to dev / preview / staging / production
- Offers first-class automation via CLI + API (no UI dependency)

## 2) Principles (Non-negotiables)

1. **API-first, UI-optional**
   Every action possible via CLI/API (create env, restore backup, promote build, rotate secrets, scale workers).
2. **Reproducible builds**
   Pinned dependencies; immutable build artifacts; deterministic pipelines; signed releases.
3. **Separation of concerns**
   Build, deploy, data ops (restore/mask), and runtime scaling are independent but composable.
4. **Safe-by-default**
   Least-privilege access; environment isolation; mandatory secret hygiene; audit trails for privileged operations.
5. **Fast feedback**
   Ephemeral preview environments per PR/branch; parallel test stages; caching of dependencies and Odoo addons.
6. **Portable hosting**
   Same product runs on managed cloud (SaaS) or self-hosted in your infra (DigitalOcean/K8s/VMs).
7. **Operational transparency**
   Clear SLOs, metrics, logs, traces, cost attribution per environment.

## 3) Tenets for Odoo-Specific Excellence

- Supports multi-repo setups: core + custom addons + OCA overlays.
- Supports multiple Odoo versions, including "minor/patch" images when feasible (container-based).
- Data workflows are first-class: snapshot, restore, seed, mask/anonymize, diff, and promote.

## 4) Product Boundaries

### In-scope

- Git integration (GitHub/GitLab), CI/CD, ephemeral preview envs
- Dev/Staging/Prod environments with promotion pipelines
- SSH/exec access with policy and auditing
- Backups, restores, scheduled snapshots, data masking
- Observability: metrics/logs/traces, release markers, health gates
- Scaling knobs: workers, storage, cron concurrency, queue workers
- Addon registry/cache and buildpack system for Odoo

### Out-of-scope (initial)

- Odoo feature development itself
- Full managed DBA beyond platform-provided automation
- Building a general PaaS for non-Odoo apps

## 5) Decision Record Rules

- Architecture changes require an ADR in `spec/odoo-sh-next/adr/`
- Security-sensitive changes require threat model update in `spec/odoo-sh-next/security/`
