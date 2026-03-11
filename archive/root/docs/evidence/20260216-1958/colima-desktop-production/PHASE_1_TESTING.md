# Phase 1: Manual DMG Testing Checklist

**Date**: 2026-02-16
**Goal**: Verify DMG installation works on clean macOS systems (x64 + arm64)
**Status**: 🔄 **In Progress**

---

## Test Matrix

### Intel Mac (x64)

#### Scenario 1: Clean Install (No Colima Pre-installed)
- [ ] Download x64 DMG
- [ ] Mount DMG
- [ ] Drag to Applications
- [ ] Launch app
- [ ] Verify daemon starts
- [ ] Check state directory created: `~/.colima-desktop/`
- [ ] Test CLI commands
- [ ] **Evidence**: Screenshot + logs

#### Scenario 2: Upgrade (Existing Colima Installed)
- [ ] Verify existing Colima installation
- [ ] Install Colima Desktop
- [ ] Check coexistence
- [ ] Verify separate state directories
- [ ] **Evidence**: Before/after state comparison

#### Scenario 3: Daemon Port Conflict
- [ ] Start daemon (port 35100)
- [ ] Attempt to start second instance
- [ ] Verify error handling
- [ ] Check PID file behavior
- [ ] **Evidence**: Error logs

#### Scenario 4: VM Operations
- [ ] Start Colima VM via UI
- [ ] Stop Colima VM via UI
- [ ] Restart Colima VM via UI
- [ ] Verify status updates
- [ ] **Evidence**: Logs + status API responses

#### Scenario 5: Settings Persistence
- [ ] Change CPU/RAM/Disk settings
- [ ] Save configuration
- [ ] Restart app
- [ ] Verify settings retained
- [ ] **Evidence**: Config YAML diff

#### Scenario 6: Logs Viewer
- [ ] Open logs viewer
- [ ] Verify 3 sources displayed (colima, lima, daemon)
- [ ] Test log refresh
- [ ] **Evidence**: UI screenshot

#### Scenario 7: Diagnostics Export
- [ ] Generate diagnostics bundle
- [ ] Verify tar.gz created
- [ ] Extract and inspect contents
- [ ] **Evidence**: tar.gz file listing

#### Scenario 8: macOS Version Matrix
- [ ] Test on macOS 12 (if available)
- [ ] Test on macOS 13 (if available)
- [ ] Test on macOS 14 (if available)
- [ ] **Evidence**: Version-specific screenshots

---

### Apple Silicon (arm64)

#### Scenario 1: Clean Install (No Colima Pre-installed)
- [ ] Download arm64 DMG
- [ ] Mount DMG
- [ ] Drag to Applications
- [ ] Launch app
- [ ] Verify daemon starts
- [ ] Check state directory created: `~/.colima-desktop/`
- [ ] Test CLI commands
- [ ] **Evidence**: Screenshot + logs

#### Scenario 2: Upgrade (Existing Colima Installed)
- [ ] Verify existing Colima installation
- [ ] Install Colima Desktop
- [ ] Check coexistence
- [ ] Verify separate state directories
- [ ] **Evidence**: Before/after state comparison

#### Scenario 3: Daemon Port Conflict
- [ ] Start daemon (port 35100)
- [ ] Attempt to start second instance
- [ ] Verify error handling
- [ ] Check PID file behavior
- [ ] **Evidence**: Error logs

#### Scenario 4: VM Operations
- [ ] Start Colima VM via UI
- [ ] Stop Colima VM via UI
- [ ] Restart Colima VM via UI
- [ ] Verify status updates
- [ ] **Evidence**: Logs + status API responses

#### Scenario 5: Settings Persistence
- [ ] Change CPU/RAM/Disk settings
- [ ] Save configuration
- [ ] Restart app
- [ ] Verify settings retained
- [ ] **Evidence**: Config YAML diff

#### Scenario 6: Logs Viewer
- [ ] Open logs viewer
- [ ] Verify 3 sources displayed (colima, lima, daemon)
- [ ] Test log refresh
- [ ] **Evidence**: UI screenshot

#### Scenario 7: Diagnostics Export
- [ ] Generate diagnostics bundle
- [ ] Verify tar.gz created
- [ ] Extract and inspect contents
- [ ] **Evidence**: tar.gz file listing

#### Scenario 8: macOS Version Matrix
- [ ] Test on macOS 12 (if available)
- [ ] Test on macOS 13 (if available)
- [ ] Test on macOS 14 (if available)
- [ ] **Evidence**: Version-specific screenshots

---

## Security Validation

### Electron Security Settings
- [ ] Verify contextIsolation enabled
- [ ] Verify nodeIntegration disabled
- [ ] Verify sandbox enabled
- [ ] Check preload script uses contextBridge only
- [ ] **Evidence**: Security audit report

### IPC Boundaries
- [ ] Verify no privileged operations in renderer
- [ ] Test IPC request-response pattern
- [ ] Validate all IPC handlers
- [ ] **Evidence**: Code review notes

### Subprocess Execution Safety
- [ ] Verify no shell injection vulnerabilities
- [ ] Test command whitelisting
- [ ] Check input validation
- [ ] **Evidence**: Security test results

### File Permissions
- [ ] Check config file permissions
- [ ] Verify state directory permissions
- [ ] Test PID file ownership
- [ ] **Evidence**: Permission listings

---

## Pre-Build Checklist

Before starting manual testing, ensure:

- [ ] Build fresh DMGs: `cd apps/colima-desktop-ui && pnpm build && pnpm package`
- [ ] Verify artifacts: `ls -lh dist/*.dmg`
- [ ] Prepare evidence directory: `mkdir -p docs/evidence/$(date +%Y%m%d-%H%M)/colima-desktop/manual-testing`
- [ ] Prepare screenshot tool (macOS Screenshot: Cmd+Shift+5)
- [ ] Prepare log capture tool (Console.app or tail -f)

---

## Evidence Collection Template

For each test scenario, collect:

1. **Screenshots**
   - App launch
   - Settings panel
   - Logs viewer
   - Error messages (if any)

2. **Logs**
   - Daemon logs: `~/.colima-desktop/logs/daemon.log`
   - Colima logs: `~/.colima-desktop/logs/colima.log`
   - Lima logs: `~/.colima-desktop/logs/lima.log`

3. **Configuration Files**
   - Before state: `~/.colima-desktop/config.yaml`
   - After state: `~/.colima-desktop/config.yaml`

4. **System Information**
   - macOS version: `sw_vers`
   - Architecture: `uname -m`
   - Colima version: `colima version`

---

## Issue Tracking

### Issues Found
| Issue # | Severity | Description | Scenario | Status |
|---------|----------|-------------|----------|--------|
| | | | | |

### Severity Levels
- **Critical**: Blocks installation or launch
- **High**: Major feature broken
- **Medium**: Minor feature broken or UX issue
- **Low**: Cosmetic or minor annoyance

---

## Completion Criteria

Phase 1 is complete when:

- [ ] All 16 scenarios tested (8 × 2 architectures)
- [ ] Evidence bundle created for all scenarios
- [ ] Issues documented and severity assigned
- [ ] Manual test report written
- [ ] Installation guide draft created
- [ ] Security validation completed

---

**Next Steps**: After Phase 1 completion, proceed to Phase 2 (Code Signing & Notarization)
