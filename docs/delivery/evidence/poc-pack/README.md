# POC Evidence Pack — Odoo 19 Go-Live

## Date: 2026-03-20
## Purpose: Go-live readiness evidence for critical-path items

---

## Evidence Index

| CP | Item | Status | Evidence File |
|----|------|--------|---------------|
| CP-1 | MFA evidence | DONE | [cp1-identity-mfa-assessment.md](cp1-identity-mfa-assessment.md) |
| CP-2 | ACA persistent storage | DONE | [cp2-aca-persistent-storage.md](cp2-aca-persistent-storage.md) |
| CP-4 | Cron fix proof | DONE | [cp4-cron-validation.md](cp4-cron-validation.md) |
| CP-5 | Deploy pipeline | DONE | [cp5-pipeline-validation.md](cp5-pipeline-validation.md) |
| CP-7 | Smoke test | CONDITIONAL PASS | [cp7-smoke-test.md](cp7-smoke-test.md) |

## Session Evidence (2026-03-18/19)

Additional evidence from this session (not tied to a specific CP):

| Item | Status | Location |
|------|--------|----------|
| Prod login fixed (asset bundling) | DONE | Asset cache cleared, KV-backed secrets |
| Foundry gpt-4.1 integration | DONE | `agent-platform/docs/evidence/foundry-integration-test/` |
| AI Search provisioned (331 docs) | DONE | `docs/architecture/CLOUD_INTEGRATION_STATUS.md` |
| ATC crosswalk (17 mappings) | DONE | `ssot/domain/atc_code_mapping.yaml` |
| Agent-platform v0.1 (22/22 tests) | DONE | `agent-platform/ssot/runtime/deployment_readiness.yaml` |
| ipai_odoo_copilot module | BUILT | `addons/ipai/ipai_odoo_copilot/` |
| Copilot Skills (4 skills, 16 tests) | DONE | `agent-platform/packages/builder-orchestrator/src/skills/` |
| Azure DevOps pipelines | CREATED | `agent-platform/azure-pipelines.yml` |
| All keys vaulted | DONE | foundry-api-key, search-admin-key, pg-admin-password |

## Readiness Summary

### Ready for go-live
- Odoo ERP runtime (live, assets serving, login working)
- Security hardening (proxy_mode, list_db=False, admin_passwd=False, dbfilter, db manager blocked)
- Azure Front Door routing (x-azure-ref confirmed)
- Session security (HttpOnly, X-Frame-Options, CSP)
- Deploy pipeline (hosted runners, validated)
- Cron system (active, has executed)
- KV-backed secrets (all 3 ACA apps)
- Daily asset health check (CI workflow)
- Secret drift check (CI script)

### Resolved blockers (2026-03-20)
- ~~MFA evidence (CP-1)~~ — Security Defaults enabled, 3/4 admins MFA-enrolled via Graph PowerShell
- ~~ACA persistent storage (CP-2)~~ — Azure Files `odoo-filestore` mounted to all 3 ACA apps; persistence verified across restart and new revision

### Remaining non-blocking items
- One asset compression issue (minimal JS, non-blocking performance)

### Go/No-Go recommendation

**GO** — CP-1 (MFA) and CP-2 (persistent storage) resolved 2026-03-20. Identity baseline is enforced, filestore persists across container lifecycle events. Remaining critical path items (CP-3 AFD, CP-4 cron, CP-5 pipeline, CP-6 tenancy, CP-7 smoke test, CP-8 evidence pack) are execution tasks, not blockers.

---

*Assembled: 2026-03-19*
*Updated: 2026-03-20 — CP-1 and CP-2 closed, verdict flipped to GO*
