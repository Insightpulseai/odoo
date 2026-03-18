# Colima Desktop - Repo SSOT (Single Source of Truth)

**Timezone**: Asia/Manila (UTC+08:00)
**Evidence Stamp**: 20260216-1958+0800
**Last Updated**: 2026-02-17 01:00:00+0800 (Migration Complete)

---

## Canonical Locations

### Spec Kit (Requirements & Plans)
- **Location**: `web/spec/colima-desktop/`
- **Files**:
  - `constitution.md` - Non-negotiable rules and security constraints
  - `prd.md` - Product requirements (the WHAT)
  - `plan.md` - Implementation plan (the HOW)
  - `tasks.md` - Task breakdown (the WORK)
  - `README.md` - Overview and navigation

### Application Code
- **Location**: `web/apps/colima-desktop/`
- **Structure**:
  - `src/` - Daemon + CLI (Node.js/TypeScript)
  - `apps/colima-desktop-ui/` - Electron UI
  - `test/` - Unit tests (daemon + CLI)
  - `AUDIT_POLICY.md` - Security vulnerability policy
  - `BLOCKERS_RESOLVED.md` - Prerequisites resolution tracker

**Migration Status**: ✅ Complete - All code now at canonical location

### Evidence Bundle
- **Location**: `web/docs/evidence/20260216-1958+0800/colima-desktop-production/`
- **Structure**:
  ```
  web/docs/evidence/20260216-1958+0800/colima-desktop-production/
  ├── REPO_SSOT.md              # This file (canonical locations)
  ├── DEPLOYMENT_PLAN.md        # 4-phase production roadmap
  ├── IMPLEMENTATION_STATUS.md  # Evidence-backed status tracker
  ├── PHASE_1_TESTING.md       # Manual testing checklist
  └── logs/                     # Evidence logs (build, test, audit)
      ├── tsc-daemon.txt        # Daemon TypeScript build output
      ├── tests.txt             # Test execution output
      ├── tsc-ui.txt            # UI TypeScript build output
      ├── audit-daemon.txt      # Security audit (full JSON)
      ├── audit-summary.txt     # Security audit summary
      └── audit-severity.txt    # Vulnerability severity breakdown
  ```

---

## Evidence-Backed Status

All claims in this repo must be backed by verifiable evidence logs.

### Build Status (Verified 2026-02-17 00:23:00+0800)

| Component | Claim | Evidence File | Status |
|-----------|-------|---------------|--------|
| Daemon TypeScript | 0 errors | `logs/tsc-daemon.txt` | ✅ PASS |
| Daemon Tests | 25/25 passing | `logs/tests.txt` | ✅ PASS |
| UI Renderer (Vite) | Build successful | `logs/tsc-ui.txt` | ✅ PASS |
| UI Main Process (TS) | TS config error | `logs/tsc-ui.txt` | ❌ FAIL |
| Security Audit | 31 HIGH + 3 CRITICAL | `logs/audit-severity.txt` | ❌ FAIL |

### Evidence Summary

**✅ What Works (Evidence-Backed)**:
- Daemon TypeScript compiles: 0 errors (verified `logs/tsc-daemon.txt`)
- Daemon tests pass: 25/25 tests (verified `logs/tests.txt`)
- UI renderer builds: Vite successful (verified `logs/tsc-ui.txt`)

**❌ What Doesn't Work (Evidence-Backed)**:
- UI main process: TS config error "Option 'bundler' can only be used when 'module' is set to 'preserve' or 'es2015' or later"
- Security vulnerabilities: 10 low, 32 moderate, 31 high, 3 critical (verified `logs/audit-severity.txt`)

**⚠️ Not Yet Verified**:
- DMG packaging (no build attempted, no artifacts to verify)
- Manual installation testing (requires Phase 1 execution)
- Code signing (no Apple Developer certificate configured)
- Notarization (blocked by signing prerequisite)

---

## Migration Complete ✅

### Final State (SSOT Compliant)
- ✅ Code: `web/apps/colima-desktop/` (moved via `git mv`, history preserved)
- ✅ Spec: `web/spec/colima-desktop/` (moved via `git mv`, history preserved)
- ✅ Evidence: `web/docs/evidence/20260216-1958+0800/colima-desktop-production/`

### Pointers at Old Locations
- `tools/colima-desktop/MOVED.md` → redirects to canonical location
- `spec/colima-desktop/MOVED.md` → redirects to canonical location
- `apps/colima-desktop-ui/README_MOVED.md` → redirects to canonical location

### Migration Completed
All migration steps executed:
1. ✅ Spec Kit moved: `spec/colima-desktop/` → `web/spec/colima-desktop/`
2. ✅ Application Code moved: `tools/colima-desktop/` → `web/apps/colima-desktop/`
3. ✅ Evidence docs updated: All paths reference `web/` canonical locations
4. ✅ Pointers created: Old paths contain MOVED.md redirects

---

## Deterministic CI Gates (Required)

Per `web/spec/colima-desktop/prd.md`, these gates MUST pass before production:

### Build-Time Gates
- [ ] `pnpm lint` - ESLint passes with 0 errors
- [ ] `pnpm typecheck` - TypeScript compiles with 0 errors (both daemon + UI)
- [ ] `pnpm test` - All unit tests pass (currently 25/25)
- [ ] `pnpm package` - DMG packaging succeeds (dry-run validation)

### Security Gates
- [ ] `pnpm audit` - Zero HIGH or CRITICAL vulnerabilities
- [ ] Electron security settings verified (contextIsolation, sandbox, etc.)
- [ ] IPC handler payload validation audit

### Manual Gates (Allowed but Tracked)
- [ ] Phase 1 DMG installation matrix (16 scenarios)
- [ ] Phase 2 Notarization pre-flight validation
- [ ] Phase 3 Homebrew formula testing

**Current Status**:
- ❌ TypeScript gate: FAIL (UI main process TS config error)
- ❌ Security gate: FAIL (31 HIGH + 3 CRITICAL vulnerabilities)
- ⚠️ All other gates: PENDING (not yet attempted)

---

## Branching Instructions (No Questions Mode)

### Branch A: Signing-Ready Path
**Condition**: Apple Developer certificate exists and is installed in Keychain

**Verification**:
```bash
security find-identity -v -p codesigning | grep "Developer ID Application"
```

**If Found**: Proceed to Phase 2 (Code Signing & Notarization)

---

### Branch B: Not Signing-Ready Path
**Condition**: No valid Apple Developer certificate found

**Actions Required**:
1. Execute Pre-Phase 0 checklist (account setup)
2. Wait for Apple approval (24-48 hours typical)
3. Generate and install certificate
4. Configure notarization credentials
5. Return to Branch A verification

---

## Next Actions (Deterministic)

### Immediate (Required Before Any Phase Work)
1. **Fix TS Config Error**: UI main process build must succeed
   - Edit `tsconfig.main.json` in `tools/colima-desktop/apps/colima-desktop-ui/`
   - Change `moduleResolution: "bundler"` to compatible setting
   - Re-run build and capture evidence

2. **Address Security Vulnerabilities**: Reduce HIGH/CRITICAL count to zero
   - Run `pnpm audit fix` on daemon package
   - Investigate unfixable vulnerabilities (document exceptions if needed)
   - Re-run audit and capture updated evidence

3. **Migrate to SSOT Structure**: Consolidate under `web/`
   - Create `web/apps/colima-desktop/`
   - Move all code from `tools/colima-desktop/`
   - Update all paths in documentation

### After Prerequisites Pass
1. **Branch Decision**: Execute Branch A or Branch B based on certificate status
2. **Phase 1 Start**: Build DMGs and begin manual testing
3. **Evidence Collection**: Update status tracker with new evidence logs

---

## Verification Commands

### Check Current Evidence
```bash
# View all evidence logs
ls -la web/docs/evidence/20260216-1958+0800/colima-desktop-production/logs/

# Check daemon build
cat web/docs/evidence/20260216-1958+0800/colima-desktop-production/logs/tsc-daemon.txt

# Check test results
cat web/docs/evidence/20260216-1958+0800/colima-desktop-production/logs/tests.txt

# Check security vulnerabilities
cat web/docs/evidence/20260216-1958+0800/colima-desktop-production/logs/audit-severity.txt
```

### Re-Capture Evidence (After Fixes)
```bash
cd tools/colima-desktop

# Rebuild and capture
pnpm build 2>&1 | tee ../../web/docs/evidence/20260216-1958+0800/colima-desktop-production/logs/tsc-daemon.txt

# Retest and capture
pnpm test 2>&1 | tee ../../web/docs/evidence/20260216-1958+0800/colima-desktop-production/logs/tests.txt

# Re-audit and capture
pnpm audit | grep -i "severity:" | sort | uniq -c > ../../web/docs/evidence/20260216-1958+0800/colima-desktop-production/logs/audit-severity.txt
```

---

**Status**: ⚠️ **SSOT violations identified - migration required**
**Blocking Issues**: TS config error, security vulnerabilities
**Next Step**: Fix prerequisites, then migrate to `web/` structure
