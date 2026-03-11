# Tasks: Odoo CE DevOps Master Plan

## Task Status Legend
- ✅ Complete
- 🔄 In Progress
- 🔲 Pending
- ❌ Blocked

---

## Phase 0: Platform Readiness

| # | Task | Status | Owner | Evidence |
|---|------|--------|-------|----------|
| 0.1 | Create spec kit structure | ✅ | Claude | `docs/spec/` exists |
| 0.2 | Generate llms.txt | ✅ | Claude | 227 lines |
| 0.3 | Generate llms-full.txt | ✅ | Claude | Full context |
| 0.4 | Create llms-txt-check workflow | ✅ | Claude | `.github/workflows/llms-txt-check.yml` |
| 0.5 | Create ci-runbot workflow | ✅ | Claude | `.github/workflows/ci-runbot.yml` |
| 0.6 | Create docs-drift-gate workflow | ✅ | Claude | `.github/workflows/docs-drift-gate.yml` |
| 0.7 | Create parity check script | ✅ | Claude | `odoo/scripts/check_odoosh_parity.py` |
| 0.8 | Update CLAUDE.md | ✅ | Claude | Current |
| 0.9 | Run Phase 0 gate | ✅ | Claude | 11/11 passed |

**Phase 0 Result**: ✅ GO

---

## Phase 1: Infrastructure Baseline

| # | Task | Status | Owner | Evidence |
|---|------|--------|-------|----------|
| 1.1 | Create root docker-compose.yml | ✅ | Claude | `docker-compose.yml` |
| 1.2 | Verify prod compose | ✅ | Claude | `deploy/docker-compose.prod.yml` |
| 1.3 | Verify Dockerfile | ✅ | Claude | `docker/Dockerfile.ce19` |
| 1.4 | Create full_backup.sh | ✅ | Claude | `odoo/scripts/backup/full_backup.sh` |
| 1.5 | Create restore_test.sh | ✅ | Claude | `odoo/scripts/backup/restore_test.sh` |
| 1.6 | Create security configs | ✅ | Claude | `security/Caddyfile.shell` |
| 1.7 | Create threat model | ✅ | Claude | `security/WEB_SHELL_THREAT_MODEL.md` |
| 1.8 | Create DR runbook | ✅ | Claude | `docs/DR_RUNBOOK.md` |
| 1.9 | Run Phase 1 gate | ✅ | Claude | 9/9 passed |

**Phase 1 Result**: ✅ GO

---

## Phase 2: Database Initialization

| # | Task | Status | Owner | Evidence |
|---|------|--------|-------|----------|
| 2.1 | Create DB init runbook | ✅ | Claude | `docs/DB_INIT_RUNBOOK.md` |
| 2.2 | Verify env template | ✅ | Claude | `.env.example` exists |
| 2.3 | Verify Docker CLI | ✅ | Claude | Available |
| 2.4 | Run Phase 2 gate | ✅ | Claude | 7/7 passed |
| 2.5 | Start PostgreSQL | 🔲 | DevOps | Pending execution |
| 2.6 | Create databases | 🔲 | DevOps | Per runbook |
| 2.7 | Initialize schema | 🔲 | DevOps | Per runbook |
| 2.8 | Create DB roles | 🔲 | DevOps | Per runbook |
| 2.9 | Capture baseline | 🔲 | DevOps | Per runbook |
| 2.10 | Commit evidence | 🔲 | DevOps | Per runbook |

**Phase 2 Gate**: ✅ GO (Ready for execution)

---

## Phase 3: CE + OCA Parity

| # | Task | Status | Owner | Evidence |
|---|------|--------|-------|----------|
| 3.1 | Generate oca.lock.json | 🔲 | Claude | |
| 3.2 | Setup OCA submodules | 🔲 | Claude | |
| 3.3 | Verify IPAI modules | 🔲 | Claude | |
| 3.4 | Create ci-odoo.yml | 🔲 | Claude | |
| 3.5 | Create ee_parity_mapping.yml | 🔲 | Claude | |
| 3.6 | Run module tests | 🔲 | CI | |
| 3.7 | Run Phase 3 gate | 🔲 | Claude | |

**Phase 3 Result**: 🔲 PENDING

---

## Phase 4: Odoo.sh Operational Parity

| # | Task | Status | Owner | Evidence |
|---|------|--------|-------|----------|
| 4.1 | GAP 1: Branch promotion | ✅ | Claude | `.github/workflows/branch-promotion.yml` |
| 4.2 | GAP 2: Runbot dashboard | ✅ | Claude | `.github/workflows/ci-runbot.yml` |
| 4.3 | GAP 3: Multi-DC backups | ✅ | Claude | `odoo/scripts/backup/`, `docs/DR_RUNBOOK.md` |
| 4.4 | GAP 4: Web shell | ✅ | Claude | `docker-compose.shell.yml` |
| 4.5 | Run Phase 4 gate | 🔲 | Claude | Awaiting Phase 3 |

**Phase 4 Result**: ✅ Implementations complete, gate pending Phase 3

---

## Phase 5: Enterprise Extras

| # | Task | Status | Owner | Evidence |
|---|------|--------|-------|----------|
| 5.1 | Configure Superset | 🔲 | BI Architect | |
| 5.2 | Deploy MCP servers | 🔲 | DevOps | |
| 5.3 | Create monitoring schema | 🔲 | DevOps | |
| 5.4 | Schedule DR drills | 🔲 | DevOps | |
| 5.5 | Run Phase 5 gate | 🔲 | Claude | |

**Phase 5 Result**: 🔲 PENDING

---

## Phase 6: Production Launch

| # | Task | Status | Owner | Evidence |
|---|------|--------|-------|----------|
| 6.1 | Final parity validation | 🔲 | Claude | |
| 6.2 | Complete GO LIVE checklist | 🔲 | DevOps | |
| 6.3 | Execute cutover | 🔲 | DevOps | |
| 6.4 | Verify SLA | 🔲 | Finance SSC | |
| 6.5 | Document lessons learned | 🔲 | All | |

**Phase 6 Result**: 🔲 PENDING

---

## Phase 7: Operate & Learn

| # | Task | Status | Owner | Evidence |
|---|------|--------|-------|----------|
| 7.1 | Setup monitoring alerts | 🔲 | DevOps | |
| 7.2 | Define incident playbooks | 🔲 | DevOps | |
| 7.3 | Schedule quarterly reviews | 🔲 | Finance SSC | |
| 7.4 | Plan next iteration | 🔲 | All | |

**Phase 7 Result**: 🔲 FUTURE

---

## Summary

| Phase | Status | Passed | Total |
|-------|--------|--------|-------|
| 0 | ✅ GO | 11 | 11 |
| 1 | ✅ GO | 9 | 9 |
| 2 | ✅ GO | 7 | 7 |
| 3 | 🔲 PENDING | - | - |
| 4 | 🔄 PARTIAL | 4 | - |
| 5 | 🔲 PENDING | - | - |
| 6 | 🔲 PENDING | - | - |
| 7 | 🔲 FUTURE | - | - |

**Overall Progress**: Phases 0-2 gates passed, ready for Phase 2 execution (DB init)
