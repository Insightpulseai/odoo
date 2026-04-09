# Go-Live SMART Targets -- Azure Boards Staging

> Copy each issue below into Azure Boards (ipai-platform project).
> Format: Problem / Outcome / Acceptance Criteria / Artifacts
> Source: `ssot/delivery/go_live_plan.yaml` targets TGT-001 through TGT-008

---

## TGT-001: Complete identity readiness for go-live

**Type:** Issue
**Area:** Identity / Security
**Due:** 2026-03-22
**Priority:** Critical

**Problem:**
Security Defaults are disabled in Entra ID. Emergency-admin MFA enrollment is incomplete. The platform cannot be exposed to production traffic without an enforced identity baseline.

**Outcome:**
Both native Entra admins have MFA enrolled. Security Defaults are enabled (or equivalent Conditional Access policy deployed). Identity baseline is locked before any runtime exposure.

**Acceptance Criteria:**
- [ ] MFA evidence for both `admin@insightpulseai.com` and `emergency-admin@insightpulseai.com`
- [ ] Security Defaults enabled in Entra ID (screenshot or CLI evidence)
- [ ] Evidence linked from `docs/runbooks/ODOO18_GO_LIVE_CHECKLIST.md` section 1

**Artifacts:**
- Entra portal screenshot showing Security Defaults = Enabled
- MFA enrollment confirmation for both accounts
- Evidence committed to `docs/delivery/evidence/identity/`

---

## TGT-002: Enable persistent storage for ACA-hosted Odoo

**Type:** Issue
**Area:** Infrastructure
**Due:** 2026-03-24
**Priority:** Critical

**Problem:**
Odoo filestore is ephemeral on ACA. Any container restart loses all uploaded attachments, report PDFs, and session data. This is a data durability blocker for the System of Record.

**Outcome:**
Azure Files share is provisioned, mounted to all 3 ACA containers (web, worker, cron), and validated to survive container restarts.

**Acceptance Criteria:**
- [ ] Azure Files share exists in `rg-ipai-dev`
- [ ] ACA volume mount wired into `ipai-odoo-dev-web`, `ipai-odoo-dev-worker`, `ipai-odoo-dev-cron`
- [ ] Restart persistence test passes (upload attachment, restart container, verify attachment survives)
- [ ] Mount evidence linked from go-live checklist section 2

**Artifacts:**
- `az containerapp show` output with volume mount configuration
- Persistence test log (upload -> restart -> verify)
- Evidence committed to `docs/delivery/evidence/storage/`

---

## TGT-003: Validate Azure pipeline deploy path

**Type:** Issue
**Area:** CI/CD / Release
**Due:** 2026-03-23
**Priority:** Critical

**Problem:**
The `ci-cd.yml` pipeline is authored but has never been executed end-to-end. Release truth is not established. The `ipai-build-pool` agent pool may not be available or correctly configured.

**Outcome:**
Pipeline runs from commit to deployed ACA revision. All stages (build, test, deploy) complete successfully. Agent pool is verified or replaced with hosted pool.

**Acceptance Criteria:**
- [ ] `ci-cd.yml` deploy stage completes in Azure DevOps
- [ ] `ipai-build-pool` verified and functional, or replaced with `ubuntu-latest`
- [ ] Pipeline run log stored as evidence
- [ ] ACA revision shows pipeline-deployed image

**Artifacts:**
- ADO pipeline run URL with green stages
- ACA revision evidence (`az containerapp revision list`)
- Evidence committed to `docs/delivery/evidence/pipeline/`

---

## TGT-004: Prove cron fix works in execution

**Type:** Issue
**Area:** Odoo Runtime
**Due:** 2026-03-24
**Priority:** High

**Problem:**
Odoo cron/server actions fail with `analytic_account_id` field drift error. This blocks Finance PPM scheduled operations and month-end close workflows.

**Outcome:**
The field reference is corrected for Odoo 18 schema. Cron job executes without error on a test database and then on production.

**Acceptance Criteria:**
- [ ] Module test DB (`test_ipai_finance_ppm`) execution log exists
- [ ] Cron path exercised successfully (server action completes)
- [ ] Evidence linked from go-live checklist section 4

**Artifacts:**
- `test_ipai_finance_ppm` install log
- Cron execution log showing successful completion
- Evidence committed to `docs/delivery/evidence/odoo-runtime/`

---

## TGT-005: Create core business smoke test for go-live

**Type:** Issue
**Area:** Quality / Testing
**Due:** 2026-03-25
**Priority:** High

**Problem:**
No automated or scripted smoke test exists for core business paths. Go-live functional verification is ad-hoc and unrepeatable.

**Outcome:**
A deterministic smoke test script covers login, sales order, invoice, project, and Finance PPM paths. Results are captured as evidence.

**Acceptance Criteria:**
- [ ] `scripts/odoo/smoke_test.sh` exists and is executable
- [ ] Login, SO creation, invoice posting, project/task workflow, PPM dashboard covered
- [ ] Results stored in evidence pack

**Artifacts:**
- `scripts/odoo/smoke_test.sh` committed to repo
- Smoke test output log
- Evidence committed to `docs/delivery/evidence/odoo-runtime/`

---

## TGT-006: Create the canonical go-live runbook

**Type:** Issue
**Area:** Documentation / Governance
**Due:** 2026-03-22
**Status:** DONE (2026-03-19)
**Priority:** Medium

**Problem:**
The manifest contract references a go-live runbook that did not exist. Without a canonical checklist, go/no-go decisions are subjective.

**Outcome:**
A 9-section go-live checklist exists at the canonical path, covering pre-flight through go/no-go decision.

**Acceptance Criteria:**
- [x] `docs/runbooks/ODOO18_GO_LIVE_CHECKLIST.md` exists
- [x] All 9 sections present (identity, infra, DB, runtime, modules, integrations, security, smoke test, go/no-go)
- [x] Manifest contract passes

**Artifacts:**
- `docs/runbooks/ODOO18_GO_LIVE_CHECKLIST.md` (created 2026-03-19)

---

## TGT-007: Build the POC evidence pack

**Type:** Issue
**Area:** Evidence / Adopt Stage Gate
**Due:** 2026-03-26
**Priority:** Critical
**Depends on:** TGT-001, TGT-002, TGT-003, TGT-004, TGT-005, TGT-006

**Problem:**
The CAF Adopt stage gate requires a complete evidence pack demonstrating platform readiness. No such pack exists yet.

**Outcome:**
A self-contained evidence directory exists with all CP-1 through CP-7 artifacts linked, architecture diagrams, runtime screenshots, Azure inventory, and a demo script executable by one operator.

**Acceptance Criteria:**
- [ ] `docs/delivery/evidence/poc-pack/` exists with all artifacts
- [ ] CP-1 through CP-7 evidence artifacts linked or included
- [ ] Readiness summary is reproducible (not self-reported)
- [ ] Demo script can be executed by one operator

**Artifacts:**
- Architecture diagram (Mermaid or draw.io)
- Runtime screenshots (Odoo login, dashboard, ACA overview, PG metrics)
- Azure resource inventory snapshot
- One-page demo narrative
- Operator demo script
- Evidence committed to `docs/delivery/evidence/poc-pack/`

---

## TGT-008: Align Boards to the actual go-live plan

**Type:** Issue
**Area:** Governance / Project Management
**Due:** 2026-03-21
**Priority:** Medium

**Problem:**
Azure Boards items do not fully reflect the go-live critical path. Some CP items lack Board items. Cron fix and evidence pack have no Board representation. Duplicate work items exist across boards.

**Outcome:**
Every critical path item has exactly one Board item. No duplicate work items. Cron fix and evidence pack are tracked.

**Acceptance Criteria:**
- [ ] Every CP-1 through CP-8 item has one corresponding Board item
- [ ] No duplicate work items across POC, Finance PPM, and Expense/Copilot boards
- [ ] Cron fix (CP-4) has a Board item
- [ ] Evidence pack (CP-8) has a Board item

**Artifacts:**
- Board item IDs mapped to CP items in `ssot/delivery/go_live_plan.yaml`
- Screenshot of Board state after alignment

---

*Generated: 2026-03-19 | Source: ssot/delivery/go_live_plan.yaml*
