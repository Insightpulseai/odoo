# Consolidated Execution Backlog

**Generated**: 2026-03-13T18:00+08:00
**Repo**: `Insightpulseai/odoo` @ branch `chore/mcp-normalize-tier1`
**Method**: 5-agent parallel sweep (spec bundles, code TODOs, GitHub issues/PRs, CI failures, docs action items)

---

## 1. Executive Summary

| Metric | Value |
|--------|-------|
| **Total actionable tasks** | 87 |
| **Blocked** | 14 (CI billing lock blocks all PR merges + workflow-dependent tasks) |
| **Ready (can execute now)** | 31 |
| **Stale/Obsolete** | 19 |
| **Critical path items** | 4 |
| **Spec bundles audited** | 8 |
| **Open GitHub Issues** | 1 |
| **Open PRs** | 3 (1 has merge conflicts) |
| **Orphan branches** | 4 |
| **Code TODOs (actionable)** | 42 |
| **Deprecated platform refs in workflows** | 7 files |
| **Pending contracts (no CI validator)** | 7 |

### Critical Path

1. **P0 — Resolve GitHub Actions billing lock** — all CI is dead, 3 PRs blocked
2. **P0 — Merge PR #576** (MCP normalize) — current working branch
3. **P0 — Merge PR #575** (Azure target state lock) — SSOT foundation
4. **P1 — Resolve PR #573 merge conflicts** (platform CI normalization) — large platform PR

### Highest-Risk Stale Items

- `docs/guides/runbooks/digitalocean.md` — 6 TODO placeholders, references deleted infrastructure
- `docs/operations/VERCEL_PRODUCTION_CHECKLIST_SSOT.md` — entire checklist for deprecated platform
- 7 pending contracts (C-03, C-04, C-05, C-06, C-08, C-09) — no docs, no CI validators
- 13 scaffold-only ipai modules with no real implementation (just `# TODO: Add specific fields`)

---

## 2. Canonical Task Inventory

### INFRASTRUCTURE & CI (Critical Path)

| ID | Title | Source | Status | Priority | Blocker | Next Action |
|----|-------|--------|--------|----------|---------|-------------|
| GH-567 | Azure DevOps Pipeline: Authorize Managed DevOps Pool | GitHub Issue | OPEN | P1 | None | Assign owner, authorize pool |
| CI-001 | Resolve GitHub Actions billing lock | CI sweep | BLOCKED | **P0** | Billing | Pay/resolve GitHub billing |
| PR-576 | chore(mcp): migrate shared MCP config to root .mcp.json | GitHub PR | READY | P0 | CI (billing) | Merge after CI unblocked |
| PR-575 | chore(ssot): lock Azure-native target state + Tableau connector | GitHub PR | READY | P0 | CI (billing) | Merge after CI unblocked |
| PR-573 | feat(platform): CI normalization, Azure migration, platform SSOT | GitHub PR | CONFLICTING | P1 | Merge conflicts + CI | Resolve conflicts, rebase on main |
| CI-002 | Remove DigitalOcean refs from 3 workflow files | CI sweep | READY | P1 | None | Edit `infra-cloudflare-dns.yml`, `docker-build-n8n.yml`, `docker-build-odoo.yml` |
| CI-003 | Remove Vercel refs from 3 workflow files | CI sweep | READY | P1 | None | Edit `ssot-snapshot.yml`, `secrets-audit.yml`, `ssot-validate.yml` |
| CI-004 | Clean up 4 orphan branches | GitHub | READY | P2 | None | Delete `chore/billing-smoke`, `claude/developer-ux-*`, `claude/setup-odoo-*`, `docs/readme-*` |

### DEVCONTAINER (Just Completed)

| ID | Title | Source | Status | Priority | Next Action |
|----|-------|--------|--------|----------|-------------|
| DC-001 | post-create.sh sudo chown fix | Session work | DONE | — | Committed `0fc375ae66` |
| DC-002 | devcontainer.json colima-odoo guard | Session work | DONE | — | Committed `0fc375ae66` |
| DC-003 | Devcontainer drift guard CI workflow | Session work | DONE | — | Committed `0fc375ae66` |

### CONTRACTS & GOVERNANCE

| ID | Title | Source | Status | Priority | Next Action |
|----|-------|--------|--------|----------|-------------|
| C-03 | JWT Trust Contract — create doc + CI validator | Contracts index | PENDING | P2 | Create `docs/contracts/JWT_TRUST_CONTRACT.md` |
| C-04 | Task Queue Contract — create doc + CI validator | Contracts index | PENDING | P2 | Create doc |
| C-05 | Design Tokens Contract — create doc + CI validator | Contracts index | PENDING | P3 | Create doc |
| C-06 | Vercel Environment Variables — mark deprecated | Contracts index | OBSOLETE | P2 | Mark deprecated in index |
| C-08 | Platform Audit Events — create doc + CI validator | Contracts index | PENDING | P2 | Create doc |
| C-09 | GitHub Actions Secrets — create doc + CI validator | Contracts index | PENDING | P2 | Create doc |
| GOV-001 | Archive `VERCEL_PRODUCTION_CHECKLIST_SSOT.md` | Docs sweep | READY | P2 | Move to `docs/archive/` |
| GOV-002 | Archive/complete `docs/guides/runbooks/digitalocean.md` | Docs sweep | READY | P2 | Archive (infra deleted) |
| GOV-003 | Archive `docs/guides/runbooks/vercel.md` | Docs sweep | READY | P2 | Archive |

### SPEC BUNDLES — ACTIVE WORK

| ID | Title | Source | Status | Priority | Deps | Next Action |
|----|-------|--------|--------|----------|------|-------------|
| SPEC-01 | odoo-copilot: Batch 1 phases (B1.1–B1.4) | `spec/odoo-copilot/tasks.md` | IN PROGRESS | P1 | Devcontainer working | Execute B1.1 install verification |
| SPEC-02 | odoo-copilot: Phase 2 — wire bridge to provider stack | `spec/odoo-copilot/tasks.md` | BLOCKED | P2 | SPEC-01 | Complete after Batch 1 |
| SPEC-03 | odoo-copilot: Phase 3 — Slack identity + intent routing | `spec/odoo-copilot/tasks.md` | BLOCKED | P2 | SPEC-02, n8n | Wait |
| SPEC-04 | odoo-copilot-benchmark: Scenario Catalog (36 scenarios) | `spec/odoo-copilot-benchmark/tasks.md` | IN PROGRESS | P2 | Running Odoo | Create 36 scenarios across 4 domains |
| SPEC-05 | odoo-copilot-benchmark: Live execution + evidence | `spec/odoo-copilot-benchmark/tasks.md` | BLOCKED | P2 | SPEC-04, running Odoo | Wait |
| SPEC-06 | lakehouse: Phase 2 — pipeline implementation | `spec/lakehouse/tasks.md` | IN PROGRESS | P2 | Phase 1 contracts | Implement Bronze crawler |
| SPEC-07 | lakehouse: Restore 4 contract YAML files | `spec/lakehouse/tasks.md` | READY | P1 | None | Restore to `contracts/delta/` |
| SPEC-08 | enterprise-target-state: GitHub Projects setup | `spec/enterprise-target-state/tasks.md` | PENDING | P2 | UI required | Create 3 org-level Projects (requires GitHub UI) |
| SPEC-09 | enterprise-target-state: Slack integration contracts | `spec/enterprise-target-state/tasks.md` | PENDING | P2 | None | Document Slack event routes |
| SPEC-10 | platform-auth: Phase 2 — Enable SSO across apps | `spec/platform-auth/tasks.md` | BLOCKED | P1 | Keycloak + Azure ACA | Enable ipai_auth_oidc in prod |
| SPEC-11 | platform-auth: Phase 3 — Harden service auth | `spec/platform-auth/tasks.md` | BLOCKED | P2 | SPEC-10 | Audit n8n secrets |
| SPEC-12 | odoo-app-agent-skills: Final commit/push | `spec/odoo-app-agent-skills/tasks.md` | READY | P1 | None | `git add && git commit && git push` |
| SPEC-13 | chatgpt-ops-assistant: MCP server scaffold | `spec/chatgpt-ops-assistant/tasks.md` | IN PROGRESS | P2 | Supabase | Create migrations, deploy Edge Functions |
| SPEC-14 | odoo-erp-saas: Phase 1 — tenant provisioning | `spec/odoo-erp-saas/tasks.md` | PLANNED | P3 | Azure PG, ACA | Future — 105+ tasks |

### CODE TODOs (Runtime-Critical)

| ID | Title | File | Line | Priority | Next Action |
|----|-------|------|------|----------|-------------|
| TODO-01 | Implement AI endpoint HTTP call | `ipai_enterprise_bridge/models/ipai_job.py` | 104 | P1 | Wire to Azure OpenAI |
| TODO-02 | Implement overdue booking detection | `ipai_enterprise_bridge/models/maintenance_equipment_integration.py` | 144 | P2 | Implement query logic |
| TODO-03 | Integrate monitoring system | `ipai_platform_api/controllers/main.py` | 152 | P2 | Wire to Azure Monitor |
| TODO-04 | Execute command via SSH/Docker | `ipai_platform_api/controllers/main.py` | 189 | P2 | Implement exec path |
| TODO-05 | Fetch platform plans from product.template | `ipai_platform_api/controllers/main.py` | 211 | P2 | Implement ORM query |
| TODO-06 | BIR TIN verification API integration | `ipai_bir_tax_compliance/models/res_partner.py` | 64 | P2 | Integrate when API available |

### CODE TODOs (Tech Debt — Scaffold Stubs)

| ID | Title | File | Priority |
|----|-------|------|----------|
| TD-01 | REST API: migrate to base_rest + API key validation | `ipai_rest_controllers/` | P2 |
| TD-02–TD-14 | 13 scaffold modules with empty models | `ipai_ai_automations`, `ipai_ai_fields`, `ipai_ai_livechat`, `ipai_documents_ai`, `ipai_equity`, `ipai_esg_social`, `ipai_esg`, `ipai_finance_tax_return`, `ipai_helpdesk_refund`, `ipai_planning_attendance`, `ipai_project_templates`, `ipai_sign`, `ipai_whatsapp_connector` | P3 |

### CODE TODOs (CI/Test)

| ID | Title | File | Priority |
|----|-------|------|----------|
| CI-T01 | Implement AI test generation logic | `ai-test-generation.yml:278,304` | P3 |
| CI-T02 | Implement parity baseline comparison | `tier0-parity-gate.yml:109` | P2 |
| CI-T03 | Add CVE blocking logic | `tier0-parity-gate.yml:173` | P2 |

---

## 3. De-duplication Report

### Duplicate Tasks Merged

| Merged Into | Sources | Reason |
|-------------|---------|--------|
| CI-002 (Remove DO refs) | 3 separate workflow files | Same cleanup, single commit |
| CI-003 (Remove Vercel refs) | 3 separate workflow files | Same cleanup, single commit |
| GOV-001/002/003 (Archive deprecated docs) | 3 runbook/checklist files | Same archival action |

### Conflicting Tasks

| Conflict | Sources | Resolution |
|----------|---------|------------|
| C-06 (Vercel ENV contract) | Contracts index says PENDING; infrastructure rules say Vercel deprecated | **Mark C-06 OBSOLETE** — Vercel is deprecated |
| `GO_LIVE_CHECKLIST_TEMPLATE.md` references DO + Vercel | Checklist vs decommission policy | **Archive or rewrite** for Azure-native target |
| C-18 (DigitalOcean API) marked Active | Infrastructure says DO deleted 2026-03-11 | **Mark C-18 DEPRECATED** |

### Stale/Obsolete Tasks

| Task | Reason | Action |
|------|--------|--------|
| All Vercel deployment tasks | Platform deprecated | Close/archive |
| All DigitalOcean infrastructure tasks | Droplet deleted 2026-03-11 | Close/archive |
| `docs/guides/runbooks/digitalocean.md` (6 TODOs) | Infrastructure deleted | Archive |
| `docs/operations/VERCEL_PRODUCTION_CHECKLIST_SSOT.md` | Platform deprecated | Archive |
| `docs/releases/GO_LIVE_CHECKLIST_TEMPLATE.md` DO/Vercel sections | Infrastructure deleted | Rewrite for Azure |
| odoo-copilot Phase 4 (Teams integration) | No Teams deployment planned | Defer/deprioritize |
| 13 scaffold-only ipai modules | Empty models, no business logic | Keep as backlog, don't treat as active |

---

## 4. Azure Boards Mapping

**Status**: Azure Boards not configured for this repository. No Azure DevOps project connection detected.

| Finding | Detail |
|---------|--------|
| Azure DevOps pipeline | Issue #567 references Azure DevOps Pipeline authorization — suggests Azure DevOps is being set up |
| Board/project | Not yet created or not connected to this repo |
| Recommended action | Once Azure DevOps pipeline is authorized (#567), create a Board and sync from spec/*/tasks.md |

**Repo tasks missing from Azure Boards**: All 87 tasks (no board exists yet).
**Azure Boards items missing from repo**: N/A.

---

## 5. Repo TODO Sweep

### Runtime-Critical (6 items)

| File | Line | TODO |
|------|------|------|
| `addons/ipai/ipai_enterprise_bridge/models/ipai_job.py` | 104 | Implement actual HTTP call to AI endpoint |
| `addons/ipai/ipai_enterprise_bridge/models/maintenance_equipment_integration.py` | 144 | Implement overdue booking detection logic |
| `addons/ipai/ipai_platform_api/controllers/main.py` | 152 | Integrate with monitoring system |
| `addons/ipai/ipai_platform_api/controllers/main.py` | 189 | Execute command via SSH or Docker exec |
| `addons/ipai/ipai_platform_api/controllers/main.py` | 211 | Fetch platform plans from product.template |
| `addons/ipai/ipai_bir_tax_compliance/models/res_partner.py` | 64 | BIR TIN verification API integration |

### Test/CI (5 items)

| File | Line | TODO |
|------|------|------|
| `.github/workflows/ai-test-generation.yml` | 278 | Implement test logic based on specification |
| `.github/workflows/ai-test-generation.yml` | 304 | Implement based on specification |
| `.github/workflows/tier0-parity-gate.yml` | 109 | Implement baseline comparison logic |
| `.github/workflows/tier0-parity-gate.yml` | 173 | Add logic to block on critical CVEs |
| `.github/workflows/e2e-playwright.yml` | 91 | Supply Chrome extension via checkout or artifact |

### Docs/SSOT (4 items)

| File | Line | TODO |
|------|------|------|
| `docs/modules/SECURITY_MODEL.md` | 70 | Implement role-based access for Finance roles |
| `docs/modules/SECURITY_MODEL.md` | 244 | Implement page-level permissions |
| `docs/odoo/DATABASE_PROMOTION_WORKFLOW.md` | 90 | Add Odoo module installation command |
| `docs/guides/runbooks/digitalocean.md` | 8-28 | 6 TODO sections (all stale — archive) |

### Tech Debt (24 items)

- 13 scaffold-only modules with `# TODO: Add specific fields`
- `ipai_rest_controllers`: 6 TODOs for API key validation, rate limiting, base_rest migration
- 2 FIXME in upstream Odoo legal docs (not actionable)
- 3 misc placeholder items

---

## 6. Spec/Plan Drift

| Bundle | constitution | prd | plan | tasks | Coverage Quality | Drift |
|--------|-------------|-----|------|-------|-----------------|-------|
| **odoo-copilot** | MISSING | MISSING | MISSING | Present | tasks.md is detailed (60+ items) but no governance docs | HIGH — no constitution/prd/plan |
| **odoo-copilot-benchmark** | Present | MISSING | MISSING | Present | tasks.md good (7 epics); prd/plan missing | MEDIUM |
| **lakehouse** | MISSING | MISSING | Present | Present | plan.md + tasks.md aligned; 4 contract YAMLs missing | MEDIUM — restore contracts |
| **enterprise-target-state** | MISSING | Present | MISSING | Present | prd exists; tasks mostly done; plan missing | LOW |
| **platform-auth** | MISSING | MISSING | Present | Present | plan + tasks aligned; no prd/constitution | MEDIUM |
| **odoo-erp-saas** | MISSING | MISSING | MISSING | Present | tasks.md is massive (105+ items) but no other docs | HIGH — no governance |
| **odoo-app-agent-skills** | MISSING | MISSING | MISSING | Present | tasks ~97% done; just needs commit | LOW |
| **chatgpt-ops-assistant** | MISSING | MISSING | MISSING | Present | tasks detailed but ~15% done; no other docs | HIGH |

**Overall**: 7/8 bundles missing `constitution.md`, 6/8 missing `prd.md`, 5/8 missing `plan.md`. Only `tasks.md` is consistently present.

---

## 7. Recommended Execution Order

### DO NOW (this week)

| Rank | Task | Rationale |
|------|------|-----------|
| 1 | **Resolve GitHub Actions billing** (CI-001) | Blocks all CI, all PR merges, all deployments |
| 2 | **Merge PR #576** (MCP normalize) | Current branch, ready |
| 3 | **Merge PR #575** (Azure target state) | SSOT foundation |
| 4 | **Resolve PR #573 conflicts** | Large platform PR, merge conflicts |
| 5 | **Commit agent-skills** (SPEC-12) | 97% done, just needs git push |
| 6 | **Restore lakehouse contracts** (SPEC-07) | 4 YAML files, quick fix |
| 7 | **Archive deprecated docs** (GOV-001/002/003) | Remove stale references |

### NEXT (next 2 weeks)

| Rank | Task | Rationale |
|------|------|-----------|
| 8 | **Remove DO refs from workflows** (CI-002) | Dead infrastructure references |
| 9 | **Remove Vercel refs from workflows** (CI-003) | Deprecated platform references |
| 10 | **Mark C-06, C-18 deprecated** | Contract hygiene |
| 11 | **Clean orphan branches** (CI-004) | 4 branches with no PRs |
| 12 | **Authorize Azure DevOps pipeline** (GH-567) | Unblocks Azure-native CI |
| 13 | **odoo-copilot Batch 1** (SPEC-01) | Next copilot milestone |
| 14 | **platform-auth Phase 2** (SPEC-10) | SSO across apps |
| 15 | **Wire AI endpoint** (TODO-01) | Runtime-critical TODO |

### LATER (backlog)

| Rank | Task | Rationale |
|------|------|-----------|
| 16 | Create pending contracts (C-03, C-04, C-05, C-08, C-09) | Governance completeness |
| 17 | odoo-copilot Phases 2-6 | Depends on Batch 1 |
| 18 | Copilot benchmark scenarios | Depends on running Odoo |
| 19 | Lakehouse Phase 2-5 | Pipeline implementation |
| 20 | chatgpt-ops-assistant MCP server | Large scope |
| 21 | REST API base_rest migration (TD-01) | Tech debt |
| 22 | GitHub Projects setup (SPEC-08) | UI-only, not urgent |
| 23 | CI parity baseline logic (CI-T02/T03) | Nice-to-have gate |
| 24 | Spec bundle completeness (add prd/constitution) | Governance |

### CLOSE / DELETE / ARCHIVE

| Task | Action | Reason |
|------|--------|--------|
| C-06 (Vercel ENV contract) | Mark DEPRECATED | Vercel decommissioned |
| C-18 (DigitalOcean API contract) | Mark DEPRECATED | DO deleted 2026-03-11 |
| `VERCEL_PRODUCTION_CHECKLIST_SSOT.md` | Archive | Vercel deprecated |
| `docs/guides/runbooks/digitalocean.md` | Archive | DO deleted |
| `docs/guides/runbooks/vercel.md` | Archive | Vercel deprecated |
| `GO_LIVE_CHECKLIST_TEMPLATE.md` DO/Vercel sections | Rewrite | Dead infrastructure |
| 13 empty scaffold modules | Keep but deprioritize | No business logic yet |
| odoo-copilot Phase 4 (Teams) | Defer indefinitely | No Teams deployment |
| odoo-erp-saas (105+ tasks) | Keep as roadmap | P3 future work |

---

## 8. Machine-Readable Output

See companion file: `execution_backlog.json`
