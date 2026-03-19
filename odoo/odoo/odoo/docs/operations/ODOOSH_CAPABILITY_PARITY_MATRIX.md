# Odoo.sh Capability Parity Matrix

> Version: 1.0.0
> Last updated: 2026-03-15
> Parent: `docs/architecture/AZURE_ODOOSH_EQUIVALENT_TARGET_STATE.md`

## Purpose

Track which Odoo.sh-style platform capabilities are implemented, partially implemented, planned, or intentionally excluded in the Azure-native InsightPulseAI operating model.

## Status Legend

- `implemented` — working and evidenced
- `partial` — exists but incomplete or unevidenced
- `planned` — defined but not yet implemented
- `not-applicable` — intentionally excluded
- `blocked` — cannot proceed without prerequisite

## Matrix

| Capability | Benchmark behavior | Azure implementation target | Owner | Status | Evidence | Gap |
|---|---|---|---|---|---|---|
| Git-triggered build | New revision triggers build | GitHub webhook → pipeline run | infra | partial | Existing CI pipelines | Unify final deploy path |
| PR validation | Branch/PR validation before promotion | Repo CI + policy checks | odoo | partial | Existing workflow set | Add runtime contract gate |
| Dev environment | Safe iteration env | `odoo_dev` runtime | infra+odoo | partial | Local/dev sandbox | Standardize refresh/rebuild |
| Staging environment | Production-like test env | `odoo_staging` runtime | infra+odoo | planned | — | Implement neutralized refresh |
| Production environment | Stable live runtime | `odoo` runtime | infra+odoo | partial | Production runtime docs | Finalize promotion-only policy |
| Staging from prod data | Copy prod data for testing | Neutralized dump/snapshot refresh | infra | planned | — | Codify masking + import runbook |
| Non-prod mail catcher | No real outbound mail in dev/staging | SMTP sink / redirect / suppression | infra | planned | — | Choose sink implementation |
| Non-prod cron safety | Limited/disabled scheduled actions | Explicit cron allowlist by stage | odoo | planned | — | Add stage-aware policy |
| Runtime logs | Per-build runtime logs | Azure Monitor / container logs | infra | partial | Current logging evidence | Standardize views/retention |
| Shell access | Browser shell / SSH-like ops | Controlled exec into runtime | infra+odoo | partial | Existing runtime notes | Codify supported commands |
| Monitoring | Availability and runtime KPIs | App Insights + Log Analytics | infra | partial | Some monitoring docs | Full dashboard + alert rules |
| Dump / backup access | Download restore inputs | Backup artifacts in storage | infra | partial | Backup docs | Add restore evidence cadence |
| Restore workflow | Recover instance quickly | Restore runbook + tested drill | infra | planned | — | Perform first restore rehearsal |
| Python dependencies | Repo-owned dependency install | `requirements.txt` contract | odoo | implemented | Repo dependency files | Add CI validation |
| Addon dependencies | Support submodule-based addons | `.gitmodules` + addon discovery | odoo | implemented | Repo structure | Add CI submodule verification |
| Containerized runtime | Per-build isolated environment | Containerized runtime per env | infra+odoo | partial | Runtime docs | Strengthen stage parity |
| Build history | Revision-linked build records | Pipeline runs + evidence packs | infra | partial | Current pipeline evidence | Normalize evidence schema |
| Promotion workflow | Promote tested staging to prod | Runbook-driven staged promotion | infra | planned | — | Implement deploy gate |
| Health checks | Surface availability status | Health probes + dashboards | infra | partial | Current health scripts | Centralize into ops dashboard |
| Domain / DNS control | Platform DNS + custom domains | Cloudflare authoritative DNS | infra | implemented | DNS target-state docs | Continue hostname cleanup |
| SSL/TLS management | Managed certificates | Cloudflare + Azure ingress TLS | infra | partial | DNS/TLS docs | Validate all prod hostnames |
| Backup retention policy | Daily/weekly/monthly retention | Storage + DB retention policy | infra | partial | DB policy docs | Publish canonical retention table |
| Rollback workflow | Recover previous good release | Rollback runbook + prior artifact | infra | planned | — | Create first rollback drill |

## Priority Gaps

### P0 — Must have before claiming parity

- Staging refresh from neutralized production data
- Non-prod outbound mail suppression
- Release promotion workflow with evidence
- Restore rehearsal evidence

### P1 — Required for operational maturity

- Runtime contract CI gate
- Centralized monitoring views
- Explicit stage-aware cron policy
- Standardized shell / exec runbook

## Intentionally Excluded

| Capability | Rationale |
|---|---|
| Drag-and-drop UI promotion | Auditable pipeline promotion is preferred |
| Provider-specific hidden hosting abstraction | Azure-native contracts must remain explicit and repo-owned |
| Unbounded long-lived side processes | Not aligned with deterministic Odoo runtime doctrine |

## Review Cadence

Update this matrix when:
- Environment topology changes
- Promotion flow changes
- Backup/restore mechanism changes
- Runtime CI gates change
- Stage safety policy changes
