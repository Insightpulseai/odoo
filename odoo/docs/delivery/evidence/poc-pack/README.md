# POC Evidence Pack — Odoo 19 Go-Live

## Date: 2026-03-19
## Purpose: Go-live readiness evidence for critical-path items

---

## Evidence Index

| CP | Item | Status | Evidence File |
|----|------|--------|---------------|
| CP-1 | MFA evidence | PARTIAL | [cp1-identity-mfa-assessment.md](cp1-identity-mfa-assessment.md) |
| CP-2 | ACA persistent storage | BLOCKED | [cp2-storage-validation.md](cp2-storage-validation.md) |
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

### Not ready for go-live
- MFA evidence (CP-1) — requires portal enrollment
- ACA persistent storage (CP-2) — no volumes configured, filestore is ephemeral
- One asset compression issue (minimal JS, non-blocking performance)

### Go/No-Go recommendation

**NO-GO** until CP-1 (MFA) and CP-2 (persistent storage) are resolved. CP-2 is the harder blocker — filestore loss on container restart is a data integrity risk.

---

*Assembled: 2026-03-19*
