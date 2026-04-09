# POC Evidence Pack — Odoo 18 Go-Live

## Date: 2026-03-20 (updated)
## Purpose: Go-live readiness evidence for critical-path items

---

## Evidence Index

| CP | Item | Status | Evidence File |
|----|------|--------|---------------|
| CP-1 | MFA / Identity | PARTIAL | [cp1-identity-mfa-assessment.md](cp1-identity-mfa-assessment.md), [cp1-mfa-cli-evidence.md](cp1-mfa-cli-evidence.md) |
| CP-2 | ACA persistent storage | DONE | [cp2-storage-validation.md](cp2-storage-validation.md) |
| CP-3 | WAF / Front Door | DONE | [cp3-waf-validation.md](cp3-waf-validation.md) |
| CP-4 | Cron fix proof | DONE | [cp4-cron-validation.md](cp4-cron-validation.md) |
| CP-5 | Deploy pipeline | DONE | [cp5-pipeline-validation.md](cp5-pipeline-validation.md) |
| CP-6 | DB tenancy hardening | DONE | `list_db=False` via command override (rev 0000051), `admin_passwd` randomized per boot, `dbfilter=^odoo$` on all 3 apps |
| CP-7 | Smoke test | CONDITIONAL PASS | [cp7-smoke-test.md](cp7-smoke-test.md) |
| CP-8 | Evidence pack | THIS FILE | All CPs documented |

## Session Evidence (2026-03-18/19/20)

Additional evidence from these sessions (not tied to a specific CP):

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
| Docker image pinned (all 3 apps) | DONE | `sha256:5c9bf027aedc...` — web rev 0000051, worker rev 0000021, cron rev 0000022 |
| list_db=False enforced | DONE | Command override copies config to /tmp, patches list_db+admin_passwd, re-exports ODOO_RC |
| DB manager blocked | DONE | Shows "database manager has been disabled by the administrator" |
| Entra Security Defaults enabled | DONE | via Microsoft Graph PowerShell |
| MFA registration campaign | DONE | all_users target, microsoftAuthenticator |
| admin@ MFA enrolled | DONE | via Entra portal |

## Readiness Summary

### Ready for go-live
- Odoo ERP runtime (live, assets serving, login working)
- Azure Files persistent storage (filestore mounted on all 3 ACA apps)
- WAF in Prevention mode (Microsoft_DefaultRuleSet 2.1 + BotManager + custom rules)
- Azure Front Door routing (13 custom domains, HTTPS redirect, x-azure-ref confirmed)
- Security hardening (proxy_mode, dbfilter=^odoo$, db manager blocked)
- Session security (HttpOnly, X-Frame-Options, CSP)
- Deploy pipeline (hosted runners, validated)
- Cron system (active, has executed)
- KV-backed secrets (all 3 ACA apps)
- Daily asset health check (CI workflow)
- Secret drift check (CI script)
- Entra Security Defaults (MFA enforced tenant-wide)
- Docker image pinned to known-good digest (web app)

### Remaining items (non-blocking for soft go-live)
- CP-1: emergency-admin@ needs interactive MFA enrollment (Security Defaults will force it on next login)
- Broken Docker image (`sha256:de4c5365...`): Investigate root cause (not blocking — all apps on known-good image)
- Clean up failed ACA revisions (0000035, 0000039-0000042, 0000044-0000046, 0000049-0000050)

### Go/No-Go recommendation

**GO** — All critical-path items (CP-1 through CP-8) are resolved or have evidence. MFA enforced tenant-wide via Entra Security Defaults. DB tenancy hardened (list_db=False, admin_passwd randomized, dbfilter locked). All 3 ACA apps pinned to known-good Docker image. WAF in Prevention mode. Persistent storage mounted. Deploy pipeline validated.

---

*Assembled: 2026-03-19, updated: 2026-03-20*
