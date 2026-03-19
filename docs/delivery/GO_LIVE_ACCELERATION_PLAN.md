# Go-Live Acceleration Plan

> **Version:** 1.2.0 | **Date:** 2026-03-20 | **Owner:** Jake Tolentino
> **CAF Stage:** Ready (45-55%), entering Adopt
> **Target:** First live POC demonstration with evidence pack
> **SSOT:** `ssot/delivery/go_live_plan.yaml`

---

## 1. Executive Summary

The InsightPulse AI platform has completed Strategy and Plan phases. The Odoo runtime is active on Azure Container Apps with PostgreSQL, native Entra admins exist, and the six-plane architecture is codified. However, several critical blockers prevent a safe go-live:

1. **Azure Front Door not deployed** -- all traffic hits ACA directly, no WAF, no edge TLS termination
2. ~~**Azure Files not mounted**~~ -- **RESOLVED 2026-03-20**: Azure Files share `odoo-filestore` mounted to all 3 ACA apps; persistence verified across restart and redeploy
3. ~~**Security Defaults disabled**~~ -- **RESOLVED 2026-03-20**: Security Defaults enabled via Graph PowerShell; 3/4 admins MFA-enrolled
4. **Odoo cron broken** -- `analytic_account_id` field drift causes server action failure
5. **No pipeline has run** -- ci-cd.yml is authored but unexecuted
6. **No database-per-tenant validation** -- tenancy model is untested
7. **Azure Boards CSVs not imported** -- ADO access blocked for ceo@ account

The plan below identifies the strict critical path, cuts scope to the minimum viable go-live, and defines 6 parallel worktrees that can execute simultaneously without merge conflicts.

---

## 2. Go-Live Critical Path (Ordered)

These items are strictly sequential. Each depends on the prior.

| Order | Blocker | Board Ref | Why First | Done Criteria |
|-------|---------|-----------|-----------|---------------|
| CP-1 | Re-enable Security Defaults / enroll emergency-admin MFA | TASK-003 | Identity baseline must be locked before any runtime exposure | Both native admins have MFA enrolled; Security Defaults ON or CA policy deployed |
| CP-2 | Deploy Azure Files + mount to ACA | Phase 1 tasks.md | Odoo filestore is ephemeral -- any restart loses attachments | Azure Files share exists; ACA volume mount active; Odoo writes survive container restart |
| CP-3 | Deploy Azure Front Door + validate routing | Phase 1 tasks.md | Public edge is the WAF/TLS boundary; without it, no production exposure | AFD routes to ACA origins; WAF managed rules active; `erp.insightpulseai.com` resolves through AFD |
| CP-4 | Fix Odoo cron job (`analytic_account_id` drift) | Go-Live Checklist 4.2 | Broken cron blocks Finance PPM and month-end close operations | Server action runs without error; cron log shows success |
| CP-5 | Run first pipeline deploy (ci-cd.yml) | TASK-005.1, OBJ-002 | Release truth must be established before declaring go-live | Pipeline runs end-to-end in ADO; artifacts deployed to dev ACA; release evidence captured |
| CP-6 | Validate database-per-tenant routing | Go-Live Checklist 3 | Tenancy model must be proven before onboarding any tenant | `dbfilter` set; hostname-to-database routing tested; external API validated |
| CP-7 | Smoke test core business paths | Go-Live Checklist 4.4 | Functional verification of the SoR | Login, sales order, invoice, project/task, Finance PPM all complete without error |
| CP-8 | Produce POC evidence pack | ISSUE-006 | Evidence is the gate to Adopt stage | Architecture diagram, runtime screenshots, Azure inventory, demo narrative, demo script all exist |

---

## 3. Go-Live Scope Cut

### Must-Do (blocks go-live)

| Item | Rationale |
|------|-----------|
| Security Defaults / MFA enforcement | Identity baseline is non-negotiable |
| Azure Files persistent storage | Data durability for SoR |
| Azure Front Door + WAF | Public edge security |
| Fix broken cron/server actions | Odoo must be functionally clean |
| First pipeline deploy | Release truth must be proven |
| Database-per-tenant validation | Tenancy model must work |
| Core business path smoke test | SoR must function |
| POC evidence pack | Gate to Adopt stage |
| Grant ceo@ Basic access to ADO | Unblocks Boards import and daily operations |

### Should-Do (improves go-live quality but not blocking)

| Item | Rationale |
|------|-----------|
| Import 3 Board CSVs to ADO | Tracks execution in planned truth surface |
| OCA 56-module baseline hydration | Improves EE parity but not functionally blocking |
| Application Insights + alerts | Observability should be live at go-live |
| Centralized observability dashboard | Improves operability |
| Custom Odoo image in ACR | Repeatability; currently manual |
| AB#-linked commits | Ties code truth to planned truth |

### Defer (post go-live)

| Item | Rationale |
|------|-----------|
| Databricks workspace activation | Intelligence layer is Phase 2 |
| Unity Catalog governance | Requires Databricks first |
| APIM provisioning | Agent tool boundary is Phase 3 |
| Foundry runtime hardening (OBJ-003) | Agent runtime is Phase 3 |
| Public advisory assistant (OBJ-004) | Requires Foundry first |
| M365 Business Premium redemption | External blocker; does not block POC |
| Keycloak-to-Entra cutover | Transitional state is acceptable for POC |
| Expense OCR pipeline | Phase 2+ feature |
| Copilot bounded actions | Phase 3 feature |
| SAP Concur integration | Future; no Concur tenant |
| CDC/lakehouse pipeline | Phase 2 intelligence layer |
| Tableau Cloud publication | Requires lakehouse |
| Automation consolidation (OBJ-005) | Post go-live operational maturity |
| OLTP/OLAP separation (OBJ-006) | Phase 2+ |
| VNet injection for Databricks | Not needed until Databricks activates |
| Defender for Cloud | Should-do but deferred to post-POC |
| Azure Policy for unmanaged resources | Governance hardening, post-POC |

---

## 4. Parallel Worktree Plan

Six independent lanes that can execute simultaneously. Each lane touches different files/resources with minimal conflict risk.

| # | Lane | Branch | Board Items | Merge Order | Conflict Risk |
|---|------|--------|-------------|-------------|---------------|
| W1 | edge-and-network | `accel/edge-network` | CP-3, Go-Live 2.x | 2 | Low -- touches `infra/azure/`, `ssot/network/` |
| W2 | odoo-runtime | `accel/odoo-runtime` | CP-4, CP-6, CP-7, Go-Live 3.x, 4.x | 3 | Low -- touches `addons/ipai/`, `config/`, Odoo DB |
| W3 | storage-and-persistence | `accel/storage` | CP-2, Go-Live 5.x | 1 | Low -- touches `infra/azure/modules/`, ACA config |
| W4 | pipeline-and-release | `accel/pipeline` | CP-5, TASK-005.x, OBJ-002 | 4 | Low -- touches `.azure/pipelines/`, `docker/` |
| W5 | observability | `accel/observability` | TASK-006, TASK-007, Go-Live 9.x | 5 | Low -- touches `infra/azure/modules/`, `ssot/capabilities/` |
| W6 | evidence-and-boards | `accel/evidence` | CP-8, ISSUE-006, ISSUE-007, Board CSVs | 6 | None -- touches `docs/`, `docs/boards/` |

---

## 5. Agent Assignment Plan

### W1: Edge and Network

**Mission:** Deploy Azure Front Door with dev parameter file, validate routing for all canonical hostnames, enable WAF managed rules.

**Scope:**
- `infra/azure/modules/front-door.bicep` (if exists) or `infra/azure/parameters/front-door-dev.parameters.json`
- `ssot/network/public_endpoints.yaml` (read-only reference)
- Azure Front Door portal/CLI deployment

**Allowed files:** `infra/azure/**`, `ssot/network/**`
**Forbidden files:** `addons/`, `apps/`, `packages/`, `spec/`

**Outputs:**
1. AFD deployment evidence (az CLI output or Bicep deployment log)
2. `curl -I https://erp.insightpulseai.com` showing AFD headers
3. WAF policy active evidence
4. Updated `ssot/network/public_endpoints.yaml` if status changes

**Exit criteria:**
- All canonical hostnames in `public_endpoints.yaml` route through AFD
- WAF managed rules active
- Host header behavior validated

**Dependencies:** None (can start immediately)

---

### W2: Odoo Runtime

**Mission:** Fix broken cron, validate tenancy routing, smoke-test core business paths.

**Scope:**
- `addons/ipai/ipai_finance_ppm/` (fix `analytic_account_id` field reference)
- Odoo database configuration (`dbfilter`, hostname routing)
- Core module installation verification

**Allowed files:** `addons/ipai/**`, `config/**`, `odoo19/**`, `scripts/odoo/**`
**Forbidden files:** `infra/`, `.azure/`, `ssot/network/`, `ssot/security/`

**Outputs:**
1. Cron fix commit with test evidence
2. `dbfilter` configuration evidence
3. Hostname-to-database routing test log
4. Core business path smoke test results (login, SO, invoice, project, PPM)

**Exit criteria:**
- Zero broken cron jobs
- Hostname routing maps correctly to tenant databases
- All core business paths complete without error

**Dependencies:** W3 (storage must be mounted before smoke test captures persistent state)

---

### W3: Storage and Persistence

**Mission:** Deploy Azure Files share, mount to ACA, verify Odoo filestore persistence across container restarts.

**Scope:**
- `infra/azure/modules/azure-files.bicep` (deploy)
- ACA volume mount configuration
- Filestore persistence validation

**Allowed files:** `infra/azure/**`
**Forbidden files:** `addons/`, `apps/`, `spec/`, `.azure/pipelines/`

**Outputs:**
1. Azure Files deployment evidence
2. ACA volume mount evidence (`az containerapp show` output)
3. Persistence test: upload attachment, restart container, verify attachment survives

**Exit criteria:**
- Azure Files share exists and is mounted
- Odoo filestore survives container restart

**Dependencies:** None (can start immediately)

---

### W4: Pipeline and Release

**Mission:** Execute the first real pipeline run through Azure DevOps. Validate agent pool, secrets, and deployment path.

**Scope:**
- `.azure/pipelines/ci-cd.yml` (validate and run)
- `docker/` (Odoo image build)
- ADO variable groups and service connections

**Allowed files:** `.azure/**`, `docker/**`, `Makefile`
**Forbidden files:** `addons/`, `ssot/security/`, `ssot/network/`

**Outputs:**
1. Pipeline run URL and status
2. Build artifact evidence
3. Deployment to dev ACA evidence
4. Release evidence artifacts

**Exit criteria:**
- Pipeline runs from commit to deployed ACA
- Self-hosted agent pool is used (or hosted pool if self-hosted not ready)
- Secrets/variables resolve correctly

**Dependencies:** W1 (AFD should be live so smoke test after deploy hits the real edge)

---

### W5: Observability

**Mission:** Enable Application Insights instrumentation, configure baseline alerts, wire Log Analytics.

**Scope:**
- `infra/azure/modules/log-analytics.bicep` (deploy if not already)
- Application Insights configuration for ACA
- Azure Monitor alert rules

**Allowed files:** `infra/azure/**`, `ssot/capabilities/**`
**Forbidden files:** `addons/`, `apps/`, `.azure/pipelines/`

**Outputs:**
1. Application Insights resource connected to ACA
2. Log Analytics workspace receiving container logs
3. Alert rules for: Odoo HTTP 5xx, PostgreSQL availability, ACA restart count
4. Evidence screenshots of telemetry flowing

**Exit criteria:**
- Container logs visible in Log Analytics
- At least 3 alert rules active
- Application Insights shows request telemetry

**Dependencies:** None (can start immediately)

---

### W6: Evidence and Boards

**Mission:** Produce the POC evidence pack and import Board CSVs (once ADO access is unblocked).

**Scope:**
- `docs/delivery/` (evidence artifacts)
- `docs/boards/` (CSV import)
- `docs/wiki/` (wiki content)
- Architecture diagrams

**Allowed files:** `docs/**`
**Forbidden files:** `addons/`, `infra/`, `ssot/security/`

**Outputs:**
1. POC architecture diagram (Mermaid or draw.io)
2. Runtime screenshots (Odoo login, dashboard, ACA overview, PG metrics)
3. Azure resource inventory snapshot
4. One-page demo narrative
5. Demo script (operator-ready)
6. Board CSV import evidence (when ADO unblocked)

**Exit criteria:**
- Evidence pack is complete and committed to `docs/delivery/`
- Demo can be executed by one operator

**Dependencies:** W1 + W2 + W3 must complete first (evidence must reflect working state)

---

## 6. Sequential Execution Plan (Critical Path Items)

### CP-1: Re-enable Security Defaults

**Why:** Identity is the foundation. All other work builds on a secure identity baseline.
**Inputs:** Access to Entra admin portal, `emergency-admin@insightpulseai.com` credentials
**Steps:**
1. Sign in as `emergency-admin@insightpulseai.com`
2. Complete MFA enrollment (Microsoft Authenticator or FIDO2 key)
3. Sign in as `admin@insightpulseai.com`, navigate to Entra > Properties > Security Defaults
4. Re-enable Security Defaults
5. Verify both accounts can sign in with MFA
**Evidence:** Entra portal screenshot showing Security Defaults = Enabled
**Done when:** Both admins have MFA; Security Defaults ON

### CP-2: Deploy Azure Files + Mount (W3)

**Why:** Without persistent storage, the SoR loses attachments on any container event.
**Inputs:** `infra/azure/modules/azure-files.bicep`, ACA resource names
**Steps:**
1. Deploy Azure Files share via Bicep or az CLI
2. Configure ACA volume mount pointing to the share
3. Restart Odoo container
4. Upload a test attachment via Odoo UI
5. Force container restart
6. Verify attachment survives
**Evidence:** `az containerapp show` with volume mount; attachment visible after restart
**Done when:** Filestore persists across restarts

### CP-3: Deploy Azure Front Door (W1)

**Why:** Public edge with WAF is a non-negotiable production gate.
**Inputs:** `infra/azure/parameters/front-door-dev.parameters.json` with real ACA FQDNs
**Steps:**
1. Deploy AFD profile with Bicep or az CLI using dev parameter file
2. Add origin groups pointing to ACA FQDNs
3. Configure routes for `erp.insightpulseai.com` and other canonical hostnames
4. Enable WAF with managed rule sets
5. Update Cloudflare DNS CNAME to point at AFD endpoint
6. Validate end-to-end routing
**Evidence:** `curl -I https://erp.insightpulseai.com` with AFD response headers
**Done when:** All canonical hostnames route through AFD with WAF active

### CP-4: Fix Odoo Cron (W2)

**Why:** Broken server actions block Finance PPM, the primary business capability.
**Inputs:** Cron log showing `analytic_account_id` error; Odoo 19 field schema
**Steps:**
1. Identify the server action referencing `analytic_account_id` on `project.project`
2. Determine the correct Odoo 19 replacement (likely `analytic_plan_id` or a relational path)
3. Update the module code
4. Test install on disposable DB (`test_ipai_finance_ppm`)
5. Verify cron runs without error
**Evidence:** Cron log showing successful execution; test DB install log
**Done when:** Cron job completes without field error

### CP-5: First Pipeline Deploy (W4)

**Why:** Release truth is not established until a pipeline has actually run.
**Inputs:** `.azure/pipelines/ci-cd.yml`, ADO project, service connection
**Steps:**
1. Grant ceo@ Basic access level in ADO (currently blocked)
2. Import pipeline definition from `.azure/pipelines/ci-cd.yml`
3. Configure variable groups and service connection references
4. Trigger pipeline run
5. Verify all stages complete
6. Verify deployment reaches ACA
**Evidence:** ADO pipeline run URL showing green stages; ACA showing new revision
**Done when:** Pipeline deploys to dev ACA with all stages green

### CP-6: Validate DB-per-Tenant (W2)

**Why:** Tenancy model is architectural. Cannot serve tenants without proven routing.
**Inputs:** PostgreSQL server, Odoo configuration, hostname list
**Steps:**
1. Create a second test database on `ipai-odoo-dev-pg`
2. Set `dbfilter` in Odoo config
3. Test hostname-to-database routing with different Host headers
4. Verify external API calls respect the Host header
5. Document the routing behavior
**Evidence:** curl/httpie commands showing correct database selection per hostname
**Done when:** Routing is proven and documented

### CP-7: Core Business Path Smoke Test (W2)

**Why:** The SoR must function before go-live can be declared.
**Steps:**
1. Login as admin
2. Create a sales order, confirm, create invoice
3. Create a project, add tasks, transition states
4. Access Finance PPM dashboard
5. Verify no error in cron/scheduled actions
**Evidence:** Screenshots or test script output for each path
**Done when:** All paths complete without error

### CP-8: POC Evidence Pack (W6)

**Why:** Evidence is the gate to Adopt stage and the asset for stakeholder demo.
**Steps:**
1. Create architecture diagram reflecting deployed state
2. Capture runtime screenshots
3. Export Azure resource inventory
4. Write one-page demo narrative
5. Write operator demo script
**Evidence:** All artifacts committed to `docs/delivery/`
**Done when:** Evidence pack is complete and demo-executable

---

## 7. Merge and Release Strategy

### Merge Order

| Order | Worktree | Branch | Why This Order |
|-------|----------|--------|----------------|
| 1 | W3 Storage | `accel/storage` | Foundation -- persistence must exist before anything else |
| 2 | W1 Edge | `accel/edge-network` | Public edge before runtime validation |
| 3 | W2 Odoo Runtime | `accel/odoo-runtime` | Fix runtime on top of persistent storage + edge |
| 4 | W4 Pipeline | `accel/pipeline` | Release truth on top of working runtime |
| 5 | W5 Observability | `accel/observability` | Telemetry on top of everything |
| 6 | W6 Evidence | `accel/evidence` | Evidence captures the final working state |

### Integration Validation Gates

Between each merge:

1. **After W3:** Verify Odoo filestore survives restart (`curl` upload + restart + `curl` download)
2. **After W1:** Verify `curl -I https://erp.insightpulseai.com` returns AFD headers
3. **After W2:** Run smoke test script against production hostname
4. **After W4:** Verify pipeline can deploy a no-op change end-to-end
5. **After W5:** Verify Application Insights shows request telemetry for smoke test
6. **After W6:** Verify evidence pack is complete and demo script runs

---

## 8. Board State Update Recommendations

Only move items where evidence exists. Do not speculate.

### Move to Done (evidence exists)

| Board Item | Evidence |
|------------|----------|
| TASK-001 (domain verified) | insightpulseai.com verified in M365 -- confirmed 2026-03-18 |
| TASK-002 (emergency accounts) | admin@ and emergency-admin@ created -- confirmed 2026-03-18 |
| TASK-004 (operationalize ADO project) | ipai-platform project id b4267980 -- confirmed 2026-03-10 |
| TASK-005 (agent pools + WIF) | ci-cd.yml references pools and connections -- confirmed 2026-03-15 |
| Phase 0 tasks.md items marked [x] | Devcontainers, architecture YAML, Bicep modules, parameters -- all committed |

### Move to Done (session 2026-03-20)

| Board Item | Evidence |
|------------|----------|
| TASK-003 (MFA baseline) | Security Defaults enabled, 3/4 admins MFA-enrolled — 2026-03-20 |
| CP-2 (Azure Files + ACA mount) | Azure Files mounted to all 3 ACA apps, persistence verified — 2026-03-20 |

### Move to Doing (work actively in progress)

| Board Item | Status |
|------------|--------|
| TASK-006 (App Insights + Log Analytics) | Resources exist but not fully wired |

### Move to Blocked

| Board Item | Blocker |
|------------|---------|
| ISSUE-007 (Startup benefits / M365) | M365 Business Premium not redeemed; zero SKUs |
| Board CSV import | ceo@ needs Basic access level in ADO |

### Keep in New/Backlog (no work started)

| Board Item | Reason |
|------------|--------|
| All Phase 2 (Intelligence Layer) items | Deferred post go-live |
| All Phase 3 (Agent Runtime) items | Deferred post go-live |
| All Phase 4 (Enterprise Hardening) items | Deferred post go-live |
| OBJ-003 through OBJ-006 | All deferred |

---

## 9. File/Path Impact by Lane

| Lane | Files Modified | Files Created | Files Read-Only |
|------|---------------|---------------|-----------------|
| W1 Edge | `infra/azure/parameters/front-door-dev.parameters.json` | AFD deployment scripts | `ssot/network/public_endpoints.yaml` |
| W2 Odoo Runtime | `addons/ipai/ipai_finance_ppm/**`, `config/dev/odoo.conf` | Test evidence logs | `ssot/architecture/platform-boundaries.yaml` |
| W3 Storage | `infra/azure/modules/azure-files.bicep` | ACA mount config script | None |
| W4 Pipeline | `.azure/pipelines/ci-cd.yml`, `docker/Dockerfile.*` | Variable group docs | None |
| W5 Observability | `infra/azure/modules/log-analytics.bicep` | Alert rule definitions | `ssot/capabilities/azure_service_mapping.yaml` |
| W6 Evidence | None | `docs/delivery/evidence/**` | All SSOT YAMLs, all wiki MDs |

Conflict risk is minimal because each lane touches distinct file paths.

---

## 10. Evidence Checklist

Every lane must produce evidence before claiming done.

| Lane | Required Evidence | Format | Location |
|------|------------------|--------|----------|
| W1 Edge | AFD deployment log, curl headers, WAF policy | CLI output + screenshot | `docs/delivery/evidence/edge/` |
| W2 Odoo Runtime | Cron fix test log, dbfilter test, smoke test results | Test output + screenshots | `docs/delivery/evidence/odoo-runtime/` |
| W3 Storage | Azure Files deployment, mount config, persistence test | CLI output | `docs/delivery/evidence/storage/` |
| W4 Pipeline | Pipeline run URL, stage logs, ACA revision | ADO link + CLI output | `docs/delivery/evidence/pipeline/` |
| W5 Observability | App Insights telemetry, alert rules, log query results | Screenshots + CLI | `docs/delivery/evidence/observability/` |
| W6 Evidence | Architecture diagram, screenshots, inventory, narrative, script | MD + PNG/SVG | `docs/delivery/evidence/poc-pack/` |

---

## 11. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| M365 Business Premium never redeemed | High | Medium | Continue with Entra ID Free + Security Defaults; CA policies deferred |
| ADO access for ceo@ remains blocked | High | Medium | Use admin@ for Board operations; escalate through M365 admin |
| Azure Front Door deployment fails | Medium | High | Fall back to ACA direct ingress with Cloudflare proxy; document as transitional |
| `analytic_account_id` fix cascades | Medium | Medium | Test on disposable DB; do not modify OCA source |
| Self-hosted agent pool unavailable | Medium | Medium | ci-cd.yml already has `ubuntu-latest` fallback |
| Solo operator capacity constraint | High | High | Strict scope cut; defer everything not on critical path; use agents for evidence generation |
| Odoo module conflicts on OCA hydration | Medium | Medium | Deferred to should-do; test install each module individually on `test_<module>` DB |

---

## Appendix: Board Item to Critical Path Mapping

| Critical Path | POC Board | Finance PPM Board | Expense/Copilot Board |
|---------------|-----------|--------------------|-----------------------|
| CP-1 (MFA) | ISSUE-007 (related) | -- | -- |
| CP-2 (Storage) | TASK-001.1 (related) | -- | -- |
| CP-3 (AFD) | TASK-001.3 | -- | -- |
| CP-4 (Cron fix) | -- | FIN-I4.2 (related) | -- |
| CP-5 (Pipeline) | TASK-005.1 through 005.5 | -- | -- |
| CP-6 (Tenancy) | TASK-001.5 (related) | -- | -- |
| CP-7 (Smoke test) | TASK-001.5 | FIN-I5.1 (related) | -- |
| CP-8 (Evidence) | ISSUE-006 (all tasks) | -- | -- |

---

## Session Evidence (2026-03-19)

Items completed during the Phase 0-to-1 acceleration sessions (2026-03-18/19):

| Item | Status | Detail |
|------|--------|--------|
| Prod login fixed | DONE | Asset bundling fixed + stale DB secret resolved |
| KV-backed secrets on all 3 ACA apps | DONE | web, worker, cron all using KV refs |
| Foundry gpt-4.1 integration | TESTED | ~3s latency, endpoint responds correctly |
| AI Search provisioned and seeded | DONE | `srch-ipai-dev`, 331 docs indexed |
| ATC crosswalk draft | COMPLETE | 17 BIR-standard mappings |
| ipai_odoo_copilot module | BUILT | 20 files, OWL systray widget |
| ipai_finance_ppm demo data | SEEDED | 95 tasks, 4-phase close |
| Agent-platform v0.1 runtime | OPERATIONAL | 22/22 tests passing |
| Copilot Skills framework | OPERATIONAL | 4 skills, 16 tests passing |
| Azure DevOps pipelines | CREATED | ci-cd.yml in ADO project ipai-platform |
| All keys vaulted | DONE | foundry, search, pg-admin, ADO PAT in kv-ipai-dev |
| Go-live runbook | CREATED | `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` (9 sections) |

---

## Deduplicated SMART Targets

Eight targets that map 1:1 to the critical path, with no overlapping work items.

### TGT-001: Complete identity readiness for go-live

- **Critical Path:** CP-1
- **Due:** 2026-03-22
- **Status:** DONE (completed 2026-03-20)
- **Owner:** platform_operator
- **Acceptance:**
  - [x] MFA evidence for required admin accounts
  - [x] Security defaults blocker removed
  - [x] Evidence linked from go-live plan
- **Evidence:** [cp1-identity-mfa-assessment.md](evidence/poc-pack/cp1-identity-mfa-assessment.md)

### TGT-002: Enable persistent storage for ACA-hosted Odoo

- **Critical Path:** CP-2
- **Due:** 2026-03-24
- **Status:** DONE (completed 2026-03-20)
- **Owner:** infrastructure_owner
- **Acceptance:**
  - [x] Azure Files mount wired into ACA
  - [x] Restart persistence test passes
  - [x] Mount evidence linked
- **Evidence:** [cp2-aca-persistent-storage.md](evidence/poc-pack/cp2-aca-persistent-storage.md)

### TGT-003: Validate Azure pipeline deploy path

- **Critical Path:** CP-5
- **Due:** 2026-03-23
- **Status:** BLOCKED
- **Owner:** release_operator
- **Acceptance:**
  - [ ] ci-cd.yml deploy stage completes
  - [ ] ipai-build-pool verified or replaced
  - [ ] Pipeline log stored

### TGT-004: Prove cron fix works in execution

- **Critical Path:** CP-4
- **Due:** 2026-03-24
- **Status:** PARTIAL
- **Owner:** workload_operator
- **Acceptance:**
  - [ ] Module test DB execution log exists
  - [ ] Cron path exercised successfully
  - [ ] Evidence linked from plan

### TGT-005: Create core business smoke test for go-live

- **Critical Path:** CP-7
- **Due:** 2026-03-25
- **Status:** MISSING
- **Owner:** quality_engineer
- **Acceptance:**
  - [ ] `scripts/odoo/smoke_test.sh` exists
  - [ ] Login, SO, invoice, project, PPM covered
  - [ ] Results in evidence pack

### TGT-006: Create the canonical go-live runbook

- **Critical Path:** N/A (supporting artifact)
- **Due:** 2026-03-22
- **Status:** DONE
- **Owner:** platform_operator
- **Acceptance:**
  - [x] `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` exists
  - [x] All 9 sections present
  - [x] Manifest contract passes
- **Evidence:** Created 2026-03-19

### TGT-007: Build the POC evidence pack

- **Critical Path:** CP-8
- **Due:** 2026-03-26
- **Status:** MISSING
- **Depends on:** TGT-001, TGT-002, TGT-003, TGT-004, TGT-005, TGT-006
- **Owner:** release_operator
- **Acceptance:**
  - [ ] `docs/delivery/evidence/poc-pack/` exists
  - [ ] CP-1 through CP-7 artifacts linked
  - [ ] Readiness summary reproducible

### TGT-008: Align Boards to the actual go-live plan

- **Critical Path:** N/A (governance)
- **Due:** 2026-03-21
- **Status:** PARTIAL
- **Owner:** platform_operator
- **Acceptance:**
  - [ ] Every CP item has one Board item
  - [ ] No duplicate work items
  - [ ] Cron and evidence pack have Board items
