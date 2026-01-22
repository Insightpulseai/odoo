# Pending Tasks Auto Audit

**Generated:** 2026-01-21
**Source:** Comprehensive scan of spec bundles, TODO comments, deployment docs

---

## Executive Summary

| Priority | Count | Description |
|----------|-------|-------------|
| CRITICAL | 1 | Blocks downstream work (Ops Control Room schema only) |
| HIGH | 8 | Should address in next sprint |
| MEDIUM | 15 | Feature completion |
| LOW | 20+ | Documentation and polish |

**CRITICAL Issues Resolved** (2/3):
- ✅ OCA Project aggregation (already in oca-aggregate.yml)
- ✅ Workbook → Seed year validation (Check 5 added)

---

## 1. CRITICAL - Blocking Issues

### 1.1 OCA Project Modules - RESOLVED ✅

**Location:** `oca-aggregate.yml` (line 42)
**Status:** RESOLVED - project repository IS in active merges

```yaml
# Tier 3: Project Management (Finance PPM dependency)
- oca project 18.0
```

**Verified:**
- ✅ `oca-aggregate.yml` includes `oca project 18.0` at line 42
- ✅ `oca.lock.json` has project modules configured
- ✅ No action needed

### 1.2 Ops Control Room Schema Access (M0)

**Location:** `spec/ops-control-room/tasks.md`
**Status:** BLOCKS all downstream ops-control work

Tasks pending:
- [ ] Fix Supabase PostgREST configuration
- [ ] Create `ops` schema with proper permissions
- [ ] Verify API access for RLS policies
- [ ] Document schema access patterns

### 1.3 Excel Workbook → Seed Alignment - ENHANCED ✅

**Location:** `scripts/seed_finance_close_from_xlsx.py`
**Status:** Enhanced with year mismatch validation

**Completed:**
- [x] Add year mismatch validation (Check 5): Blocks export when BIR approval year < period covered year
- [x] Validation passed on current workbook (no year mismatches detected)

**Remaining (optional enhancements):**
- [ ] Add `task_code` column to align across all sheets (current: auto-generated)
- [ ] Add `stage_id` using external IDs (current: uses labels)
- [ ] Add `assignee_login` for unambiguous user mapping (current: uses employee_code)
- [ ] Separate employee metadata from task rows in source (current: embedded)

---

## 2. HIGH Priority - Next Sprint

### 2.1 Finance PPM Enhancements

**Location:** Various Finance PPM modules

| Task | File | Status |
|------|------|--------|
| Add `task_code` to month-end tasks | `ipai_finance_close_seed` | TODO |
| Map stages to OCA `project_stage_state` | `ipai_project_program` | TODO |
| Wire Supabase Logframe CSV export | `scripts/` | TODO |
| Add Gantt chart date calculation from workbook | `ipai_finance_ppm_dashboard` | TODO |

### 2.2 CI/CD Gaps

| Workflow | Issue | Action |
|----------|-------|--------|
| `spec-kit-enforce.yml` | Some bundles missing constitution.md | Add missing files |
| `module-gating.yml` | New IPAI modules not in allow-list | Update allow-list |
| `finance-ppm-health.yml` | Hardcoded credentials | Use secrets |

### 2.3 Python TODO Comments (Code Debt)

| File | Line | TODO |
|------|------|------|
| `addons/ipai/ipai_mail_integration/controllers/mail_oauth.py` | 33-35 | Exchange code for tokens, store securely |
| `addons/ipai_ask_ai/models/afc_rag_service.py` | 178, 301 | Integrate OpenAI/Claude |
| `addons/ipai/ipai_ppm_monthly_close/models/ppm_close_task.py` | 251,261,273 | Integrate Odoo messaging/n8n |
| `addons/ipai_bir_tax_compliance/models/res_partner.py` | 64 | BIR TIN verification API |
| `addons/ipai/ipai_ai_agents/models/source.py` | 75 | Trigger actual reindex |
| `mcp/local/app/main.py` | 336 | Implement Odoo XML-RPC client |

---

## 3. MEDIUM Priority - Feature Completion

### 3.1 Spec Bundle Tasks (Incomplete)

| Spec Bundle | Pending Tasks | Priority Items |
|-------------|---------------|----------------|
| `adk-control-room` | 100+ | Database setup, Tool framework, Agent runtime |
| `ipai-ai-platform-odoo18` | 195+ | KB chunks, search RPCs, testing |
| `pulser-master-control` | 57 | SLA enforcement, BPMN runtime |
| `ipai-ai-platform` | 80+ | Core AI enhancement, workspace primitives |
| `continue-plus` | 15+ | Spec bundle, CI workflows, migration guide |

### 3.2 Missing Architecture Documentation

| Document | Status |
|----------|--------|
| `docs/architecture/IPAI_AI_PLATFORM_ARCH.md` | Missing |
| `docs/architecture/IPAI_AI_PLATFORM_ERD.mmd` | Missing |
| `docs/api/openapi.ipai_ai_platform.yaml` | Missing |
| Data flow diagrams | Missing |
| Security boundary documentation | Missing |

### 3.3 Supabase Schema Tasks

| Schema | Table | Status |
|--------|-------|--------|
| `mcp_jobs` | `jobs`, `job_runs`, `job_events` | Implemented |
| `kb` | `chunks` (pgvector) | TODO |
| `ops` | `sessions`, `runs`, `run_events` | TODO |

---

## 4. LOW Priority - Polish & Documentation

### 4.1 Module READMEs Missing

- `addons/ipai/ipai_ai_agents_ui/README.md`
- `addons/ipai/ipai_ai_connectors/README.md`
- `addons/ipai/ipai_ai_sources_odoo/README.md`
- `addons/ipai/ipai_workspace_core/README.md`

### 4.2 tasks.md Checklist Items

From root `tasks.md`:
- Phase 0: CI guardrails (partial)
- Phase 1-5: Multiple items unchecked (though many implemented)

### 4.3 Go-Live Checklist Items

From `docs/releases/GO_LIVE_MANIFEST.md`:
- [ ] Manual QA (TBD)
- [ ] Product Owner sign-off (TBD)
- [ ] Release Manager approval
- [ ] Ops sign-off

---

## 5. Items Requiring External Access

These cannot be completed within the repo alone:

| Item | Required Access | Status |
|------|-----------------|--------|
| DigitalOcean deployment verification | Droplet SSH | TODO |
| Mailgun SMTP configuration | Mailgun API key | TODO |
| Supabase schema creation | Project credentials | TODO |
| BIR TIN API integration | BIR API access | TODO |
| Production database backup verification | PostgreSQL access | TODO |

---

## 6. Recommended Action Plan

### Immediate (This PR)

1. **Fix OCA aggregation** - Add project repo to `oca-aggregate.yml`
2. **Update seed script** - Add `task_code` generation from workbook
3. **Create validation script** - Python/SQL checks mirroring Excel Data Validation sheet

### Next Sprint

1. **Complete Ops Control Room M0** - Unblock downstream work
2. **Resolve Python TODOs** - Focus on Finance PPM and AI integration
3. **Update spec bundle tasks** - Mark completed items

### Backlog

1. **Architecture documentation** - Create missing ERD/data flow docs
2. **Module READMEs** - Add documentation to undocumented modules
3. **Go-Live checklist** - Complete UAT and sign-off process

---

## 7. Verification Commands

```bash
# Check for remaining TODOs in Python code
grep -r "TODO" --include="*.py" addons/ipai/ | wc -l

# Verify Finance PPM seed alignment
python scripts/seed_finance_close_from_xlsx.py
git diff --exit-code addons/ipai/ipai_finance_close_seed

# Check spec bundle completeness
./scripts/spec_validate.sh

# Repo health check
./scripts/repo_health.sh
```

---

*Generated by auto-review agent on 2026-01-21*
