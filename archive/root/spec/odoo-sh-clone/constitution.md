# CONSTITUTION — Odoo.sh Clone (Better-than-Odoo.sh)

## 1) Mission
Deliver an Odoo.sh-equivalent platform for Odoo CE+OCA+ipai that provides:
- Branch → environment mapping (dev/staging/prod)
- Automated builds with immutable artifacts
- Staging builds that use *fresh copies of production data*
- Operational controls: logs, shell, backups, restores, upgrades, observability
- Enterprise governance: auditability, least privilege, deterministic infra, GitOps

## 2) Non-negotiables
1. **No manual UI steps for operations**: everything must be doable via CLI, API, or code.
2. **Git is the source of truth**: branch state drives environment state.
3. **Deterministic deploys**: artifacts are pinned by digest/SHA; rollback is one command.
4. **Prod safety**:
   - staging uses a fresh prod DB clone per build (no reused DBs)
   - prod writes are protected by approvals and policy gates
5. **Backups & retention**: minimum parity with Odoo.sh retention (7 daily / 4 weekly / 3 monthly) including DB + filestore + logs/sessions where applicable.
6. **Security**:
   - secrets never stored in Git
   - least privilege service accounts
   - RLS enforced on control-plane data
7. **Multi-tenancy**: support multiple Odoo instances/projects under one org.
8. **Portability**: must run on DigitalOcean + GitHub, with optional Kubernetes later.

## 3) Supported platforms
- GitHub (Org + Actions + GHCR + Codespaces)
- DigitalOcean (Droplets + Managed Postgres + optional DO Container Registry)
- Supabase (control plane DB + Edge Functions runner)

## 4) Interfaces (contracts)
- Control-plane API: versioned HTTP endpoints, OpenAPI first.
- Runtime: Odoo containers deployed via compose (initially) then optional k8s.
- Observability: logs/events written to control plane.

## 5) Quality gates
- Required checks on protected branches
- Build must publish artifacts + SBOM
- Security gates: SAST + dependency audit
- Smoke tests must run on every staging build

## 6) Definition of done
A repo with this spec ships:
- Control-plane schema + RLS
- Runner that claims jobs and executes builds
- Branch/environment mapping with policy gates
- Backup/restore + upgrade workflows
- Developer UX parity: logs, shell, editor-equivalent via Codespaces
