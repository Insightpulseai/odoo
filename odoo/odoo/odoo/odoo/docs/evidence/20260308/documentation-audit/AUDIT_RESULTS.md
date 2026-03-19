# Documentation Baseline Audit — 2026-03-08

## Purpose

Full honest correction of CLAUDE.md and release docs to match verified codebase reality.
Triggered by: review against latest release `prod-20260302-0241` (194 commits since).

## Correction Rule Applied

> **Present tense = verified reality.**
> **Future tense = target state.**

---

## Discrepancy Ledger

| Item | Was Documented | Verified Actual | Correction |
|------|---------------|-----------------|------------|
| MCP servers | 11 in `mcp/servers/` | **1** (`plane/` only) | Fixed — 6 planned servers noted as "planned, not implemented" |
| Apps | 20-28 in `apps/` | **10** (2 substantial, 8 stubs) | Fixed — listed actual apps |
| IPAI modules | "80+ modules" / "43" | **68** in `addons/ipai/` + **41** at root | Fixed — documented split |
| Packages | 3 (was accurate in tree) | **3** | No change needed |
| GitHub workflows | 47 (tree) | **360** | Fixed |
| Scripts | "160+" | **986 files in 86 categories** | Fixed |
| Spec bundles | "32 feature specs" | **75** (7 incomplete) | Fixed |
| EE Parity | "≥80%" | **~35-45%** | Fixed — per-module status added |
| Release docs | Last updated 2026-01-06 | **61 days stale** | Updated to `prod-20260302-0241` |

### Modules Claimed in Parity Matrix But Not Found

| Module | Claimed Parity | Status After Audit |
|--------|---------------|-------------------|
| `ipai_approvals` | 95% | Planned (0%) |
| `ipai_dev_studio_base` | 70% | Planned (0%) |
| `ipai_planning` | 85% | Planned (0%) |
| `ipai_timesheet` | 85% | Planned (0%) |
| `ipai_knowledge_base` | 75% | Planned (0%) |
| `ipai_finance_consolidation` | 80% | Planned (0%) |
| `ipai_hr_attendance` | 95% | Planned (0%) |
| `ipai_hr_leave` | 95% | Planned (0%) |
| `ipai_hr_appraisal` | 80% | Planned (0%) |
| `ipai_field_service` | 75% | Planned (0%) |

### Modules Verified Live (With Substance Assessment)

| Module | Lines of Code | Has Tests | Honest Parity |
|--------|--------------|-----------|---------------|
| `ipai_enterprise_bridge` | 1,519 (12 models) | Yes (2 test files) | ~50% |
| `ipai_hr_payroll_ph` | 975 (5 models) | No | ~70% |
| `ipai_helpdesk` | 589 (4 models) | No | ~40% |
| `ipai_finance_ppm` | 223 (3 models) | No | ~40% |
| `ipai_bir_tax_compliance` | ~400 | No | ~60% |

---

## Files Modified

| File | Section Changed |
|------|----------------|
| `CLAUDE.md` (repo) | Directory structure, EE parity matrix, MCP servers, CI/CD count, spec count, module hierarchy |
| `~/.claude/CLAUDE.md` (global) | EE parity quick reference |
| `docs/releases/WHAT_SHIPPED.md` | Updated to `prod-20260302-0241` |
| `docs/releases/WHAT_SHIPPED.json` | Updated current_state to latest release |
| `docs/releases/GO_LIVE_MANIFEST.md` | Updated to `prod-20260302-0241` |
| `docs/evidence/20260308/documentation-audit/AUDIT_RESULTS.md` | This file (new) |

---

## Verification Commands

```bash
# MCP server count (should be 1)
ls -d mcp/servers/*/ 2>/dev/null | wc -l

# Apps count (should be ~10)
ls -d apps/*/ 2>/dev/null | wc -l

# IPAI module count in addons/ipai/ (should be ~68)
ls -d addons/ipai/*/ 2>/dev/null | wc -l

# Workflow count (should be ~360)
ls .github/workflows/*.yml 2>/dev/null | wc -l

# Script file count (should be ~986)
find scripts/ -type f 2>/dev/null | wc -l

# Spec bundle count (should be ~75)
ls -d spec/*/ 2>/dev/null | wc -l

# Missing modules (should all fail)
for m in ipai_approvals ipai_dev_studio_base ipai_planning ipai_timesheet ipai_knowledge_base; do
  test -d "addons/ipai/$m" && echo "FOUND: $m" || echo "MISSING: $m"
done
```

---

## Remaining Gaps (Out of Scope for This Audit)

1. **41 root-level ipai modules** need consolidation into `addons/ipai/`
2. **5+ planned modules** need implementation to reach parity target
3. **23 near-empty doc directories** need consolidation or removal
4. **7 incomplete spec bundles** need completion or archival
5. **Most Live modules lack test coverage** — blocks honest parity claims above ~50%
6. **360 workflows** need triage — unclear which are enforced vs. dormant
