# Colima Desktop - Production Deployment Plan

**Date**: 2026-02-16
**Status**: ✅ **Plan Approved - Ready for Execution**
**Validation**: 85% confidence (high confidence with enhancements)

---

## Executive Summary

**Current State**: Colima Desktop is 90% complete (Phase 4) with:
- ✅ TypeScript: 0 errors across daemon, CLI, and Electron UI
- ✅ Tests: 25/25 passing (100% pass rate)
- ✅ DMG Packaging: Verified working (x64 + arm64)
- ✅ CI/CD: Packaging gate prevents false production-ready claims

**Gaps Blocking Production**:
1. ❌ No manual DMG testing on clean macOS systems
2. ❌ No Apple code signing certificate configured
3. ❌ No Apple notarization workflow
4. ❌ No Homebrew formula for distribution
5. ❌ No user documentation (installation, usage, troubleshooting)

**Timeline**: 4.5-5.5 weeks total
- 4.5 weeks if Apple Developer account ready
- 5.5 weeks if starting from scratch (includes account setup)

---

## Phase Overview

| Phase | Duration | Focus | Deliverables |
|-------|----------|-------|--------------|
| Pre-Phase 0 | 1 week (optional) | Apple Developer account setup | Active account, certificate, credentials |
| Phase 1 | 1 week | Manual DMG verification | Test matrix completion, evidence bundle |
| Phase 2 | 1.5 weeks | Code signing & notarization | Signed DMGs, notarization tickets |
| Phase 3 | 1 week | Homebrew distribution | Formula, tap repo, automation |
| Phase 4 | 1 week | Documentation & release | User docs, release, monitoring |

---

## Pre-Phase 0: Apple Developer Account Setup (Optional - Week 0)

**Goal**: Ensure Apple Developer infrastructure ready before Phase 1

**Skip If**: You already have an active Apple Developer account with valid certificate

### Tasks

1. **Apple Developer Account**
   - [ ] Apply for Apple Developer Program enrollment
   - [ ] Wait for approval (24-48 hours typical)
   - [ ] Complete payment ($99/year)
   - [ ] Verify account active at developer.apple.com

2. **Certificate Generation**
   - [ ] Log in to Apple Developer portal
   - [ ] Navigate to Certificates, Identifiers & Profiles
   - [ ] Create "Developer ID Application" certificate
   - [ ] Download certificate and install in macOS Keychain
   - [ ] Verify: `security find-identity -v -p codesigning`

3. **Notarization Credentials**
   - [ ] Create app-specific password at appleid.apple.com
   - [ ] Store credentials securely
   - [ ] Configure environment variables:
     - `APPLE_ID` (your Apple ID email)
     - `APPLE_APP_SPECIFIC_PASSWORD` (generated password)
     - `APPLE_TEAM_ID` (from Developer portal)

### Deliverables
- Active Apple Developer account (verified)
- Developer ID certificate installed in Keychain
- App-specific password created
- Environment variables configured in `~/.zshrc` or CI secrets

### Verification
```bash
# Check certificate
security find-identity -v -p codesigning

# Check environment variables
echo $APPLE_ID
echo $APPLE_TEAM_ID
# Don't echo password, just verify it's set
[ -n "$APPLE_APP_SPECIFIC_PASSWORD" ] && echo "Password set"
```

---

## Phase 1: Manual Verification (Week 1)

**Goal**: Verify DMG installation works on clean macOS systems (x64 + arm64)

### Test Matrix (8 scenarios × 2 architectures)

| Scenario | Intel Mac | Apple Silicon | Evidence Required |
|----------|-----------|---------------|-------------------|
| Clean install (no Colima) | ☐ | ☐ | Screenshot + logs |
| Upgrade (Colima installed) | ☐ | ☐ | Before/after state |
| Daemon port conflict (35100) | ☐ | ☐ | Error handling |
| VM start/stop/restart | ☐ | ☐ | Logs + status API |
| Settings persistence | ☐ | ☐ | Config YAML diff |
| Logs viewer (3 sources) | ☐ | ☐ | UI screenshot |
| Diagnostics export | ☐ | ☐ | tar.gz inspection |
| macOS 12 vs 13 vs 14 | ☐ | ☐ | Version matrix |

### Tasks

1. **Manual DMG Testing**
   - [ ] Test x64 DMG on Intel Mac (macOS 12+)
   - [ ] Test arm64 DMG on Apple Silicon Mac (macOS 12+)
   - [ ] Verify app launches, daemon starts, CLI commands work
   - [ ] Document installation issues or permission prompts

2. **Installation Flow Validation**
   - [ ] Clean install on system without Colima pre-installed
   - [ ] Upgrade scenario (existing Colima installation)
   - [ ] Verify state directory creation (`~/.colima-desktop/`)
   - [ ] Test daemon port binding (35100) and conflict resolution

3. **Security Validation**
   - [ ] Verify Electron security settings (contextIsolation, sandbox)
   - [ ] Test IPC boundaries (no privileged operations in renderer)
   - [ ] Validate subprocess execution safety (no shell injection)
   - [ ] Review file permissions on config files

### Deliverables
- Manual test report: `docs/evidence/<YYYYMMDD-HHMM>/colima-desktop/manual-testing.md`
- Test evidence bundle: Screenshots, logs, before/after state
- Compatibility matrix: macOS 12/13/14 + Intel/Apple Silicon results
- Issue list: Any bugs found during manual testing
- Installation guide draft: `apps/colima-desktop-ui/INSTALL.md`

### Test Commands
```bash
# Build DMGs
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo/apps/colima-desktop-ui
pnpm build && pnpm package

# Verify artifacts
ls -lh dist/*.dmg

# Manual testing workflow
# 1. Mount DMG: open dist/Colima\ Desktop-0.1.0.dmg
# 2. Drag to Applications
# 3. Launch from Applications
# 4. Test all features
# 5. Capture evidence
```

---

## Phase 2: Code Signing & Notarization (Week 2)

**Goal**: Configure Apple Developer certificate and notarization workflow

### Prerequisites
- Apple Developer account with valid certificate
- `APPLE_ID`, `APPLE_APP_SPECIFIC_PASSWORD`, `APPLE_TEAM_ID` environment variables

### Tasks

1. **Certificate Setup**
   - [ ] Obtain "Developer ID Application" certificate from Apple Developer portal
   - [ ] Install certificate in macOS Keychain
   - [ ] Configure `electron-builder` for code signing
   - [ ] Update `apps/colima-desktop-ui/package.json` with signing config

2. **Pre-Flight Validation** (before notarization)
   - [ ] Run codesign verification: `codesign --verify --deep --strict "Colima Desktop.app"`
   - [ ] Validate Info.plist completeness (CFBundleIdentifier, version keys)
   - [ ] Check unsigned binaries: `find "Colima Desktop.app" -type f -perm +111 -exec codesign -dvv {} \;`
   - [ ] Test with local Gatekeeper: `spctl -a -vv "Colima Desktop.app"`
   - [ ] Review entitlements against Electron security requirements
   - [ ] Document pre-flight results: `docs/evidence/<YYYYMMDD-HHMM>/colima-desktop/pre-flight.md`

3. **Notarization Workflow**
   - [ ] Add notarization step to `electron-builder` config
   - [ ] Create app-specific password for notarization
   - [ ] Configure GitHub Actions secrets (if automating)
   - [ ] Test notarization on manual build

4. **CI Integration** (Optional)
   - [ ] Add signing secrets to GitHub Actions
   - [ ] Create workflow: `.github/workflows/colima-desktop-release.yml`
   - [ ] Automate: build → sign → notarize → upload DMG as release asset
   - [ ] Test workflow on draft release

### Deliverables
- Signed DMG files (both architectures)
- Notarization ticket receipt (Apple)
- Updated `electron-builder.config.js` with signing config
- CI workflow (if automated): `.github/workflows/colima-desktop-release.yml`

### Code Changes
```javascript
// apps/colima-desktop-ui/electron-builder.config.js
module.exports = {
  productName: 'Colima Desktop',
  appId: 'com.insightpulseai.colima-desktop',
  mac: {
    hardenedRuntime: true,
    gatekeeperAssess: false,
    entitlements: 'build/entitlements.mac.plist',
    entitlementsInherit: 'build/entitlements.mac.plist',
    identity: 'Developer ID Application: Your Name (TEAM_ID)'
  },
  afterSign: 'build/notarize.js',
  // ... rest of config
}
```

### Verification Commands
```bash
# Verify signing
codesign --verify --deep --strict "Colima Desktop.app"

# Check signature
codesign -dvv "Colima Desktop.app"

# Test Gatekeeper
spctl -a -vv "Colima Desktop.app"
```

---

## Phase 3: Homebrew Distribution (Week 3)

**Goal**: Create Homebrew formula for easy installation

### Tasks

1. **Formula Creation**
   - [ ] Create formula file: `Formula/colima-desktop.rb`
   - [ ] Define download URL (GitHub release asset)
   - [ ] Add SHA256 checksum calculation
   - [ ] Specify dependencies (if any)
   - [ ] Define installation steps (copy .app to Applications)

2. **Tap Repository Setup**
   - [ ] Create GitHub repo: `insightpulseai/homebrew-colima-desktop`
   - [ ] Add formula to `Formula/colima-desktop.rb`
   - [ ] Configure GitHub release workflow to auto-update formula
   - [ ] Test installation: `brew install insightpulseai/colima-desktop/colima-desktop`

3. **Documentation**
   - [ ] Update README with Homebrew installation instructions
   - [ ] Add uninstall instructions
   - [ ] Document upgrade process (`brew upgrade colima-desktop`)

### Deliverables
- Homebrew formula: `Formula/colima-desktop.rb`
- Tap repository: `insightpulseai/homebrew-colima-desktop`
- Formula automation script: `scripts/update-formula.sh` (for version bumps)
- CI workflow: Auto-calculate SHA256 on release (`.github/workflows/release-homebrew.yml`)
- Installation docs: Updated `README.md` with Homebrew section
- Formula update guide: `CONTRIBUTING.md` section on formula maintenance

### Example Formula
```ruby
class ColimaDesktop < Formula
  desc "Desktop GUI for Colima - container runtimes on macOS"
  homepage "https://github.com/insightpulseai/odoo"
  version "0.1.0"

  if Hardware::CPU.intel?
    url "https://github.com/insightpulseai/odoo/releases/download/v0.1.0/Colima-Desktop-0.1.0.dmg"
    sha256 "CALCULATE_THIS"
  else
    url "https://github.com/insightpulseai/odoo/releases/download/v0.1.0/Colima-Desktop-0.1.0-arm64.dmg"
    sha256 "CALCULATE_THIS"
  end

  def install
    prefix.install "Colima Desktop.app"
  end

  def caveats
    <<~EOS
      To start Colima Desktop, open it from Applications or run:
        open "#{prefix}/Colima Desktop.app"
    EOS
  end
end
```

### Verification Commands
```bash
# Test formula locally
brew install --build-from-source Formula/colima-desktop.rb

# Verify installation
ls -la /Applications/Colima\ Desktop.app

# Test launch
open /Applications/Colima\ Desktop.app
```

---

## Phase 4: Documentation & Release (Week 4)

**Goal**: Complete user documentation and publish first release

### Tasks

1. **User Documentation**
   - [ ] Installation guide (Homebrew, manual DMG)
   - [ ] Quick start guide (first launch, creating Colima instance)
   - [ ] Feature reference (menubar, CLI commands, daemon API)
   - [ ] Troubleshooting guide (common issues, logs location)
   - [ ] Security model explanation (why no auto-install, privilege separation)

2. **First-Launch Experience Enhancement**
   - [ ] Add Colima detection check on app startup
   - [ ] Show setup guide if Colima not found
   - [ ] In-app link to manual Colima setup: `brew install colima`
   - [ ] FAQ section: "Why doesn't the app install Colima automatically?"
   - [ ] Link to constitution.md security rationale

3. **Developer Documentation**
   - [ ] Architecture overview (diagram from plan.md)
   - [ ] API reference (daemon endpoints, CLI commands)
   - [ ] Contributing guide (build, test, package)
   - [ ] Release process documentation

4. **Release Preparation**
   - [ ] Finalize version number (0.1.0 or 1.0.0?)
   - [ ] Create changelog from commit history
   - [ ] Tag release in git: `git tag -a v0.1.0 -m "Initial release"`
   - [ ] Create GitHub release with signed DMGs
   - [ ] Announce release (internal channels, Homebrew tap)

5. **Post-Release Monitoring**
   - [ ] Monitor issue reports for installation problems
   - [ ] Track Homebrew install analytics (if available)
   - [ ] Collect user feedback on security model (no auto-install)
   - [ ] Plan next iteration based on feedback

### Deliverables
- User docs: `apps/colima-desktop-ui/docs/` (install, quickstart, reference, troubleshooting)
- Developer docs: `tools/colima-desktop/CONTRIBUTING.md`, `API.md`
- Changelog: `apps/colima-desktop-ui/CHANGELOG.md`
- GitHub release: v0.1.0 with signed DMGs
- Homebrew formula updated with v0.1.0 checksums

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Code signing fails (cert issues) | Medium | High | Test signing on local machine first, have backup manual signing process |
| Notarization rejected by Apple | Medium | High | Review Apple requirements, test with sample app first, have manual fallback |
| Homebrew formula broken | Low | Medium | Test installation on clean system before publishing, provide manual DMG option |
| DMG doesn't work on older macOS | Low | Medium | Document minimum macOS version (12+), test on multiple OS versions |
| Security model confuses users | Medium | Low | Clear documentation explaining "no auto-install" rationale, provide manual Colima setup guide |

---

## Success Criteria

### Core Criteria (must pass)
- [ ] Signed DMGs verified on clean macOS systems (Intel + Apple Silicon)
- [ ] Notarization ticket received from Apple (no Gatekeeper warnings)
- [ ] Homebrew installation works: `brew install insightpulseai/colima-desktop/colima-desktop`
- [ ] User docs complete (install, quickstart, reference, troubleshooting)
- [ ] GitHub release published with signed DMGs and changelog
- [ ] Zero critical bugs reported in first 2 weeks post-release

### Enhanced Criteria (from validation)
- [ ] Notarization pre-flight: Local Gatekeeper test passes before Apple submission
- [ ] Test matrix completion: 8 scenarios validated (Intel + Apple Silicon × 4 scenarios each)
- [ ] Formula automation: SHA256 auto-generated on release via CI workflow
- [ ] First-launch UX: Colima detection + setup guide implemented
- [ ] Evidence bundle: Manual test reports, screenshots, logs captured in `docs/evidence/`

### Optional (nice-to-have)
- [ ] CI workflow automates future releases (signing + notarization + Homebrew formula update)
- [ ] Formula-bot integration for automated Homebrew tap updates

---

## Timeline Summary

| Phase | Duration | Cumulative | Notes |
|-------|----------|------------|-------|
| Pre-Phase 0: Apple Account Setup | 1 week (optional) | Week 0 | Skip if already configured |
| Phase 1: Manual Verification | 1 week | Week 1 | Structured test matrix |
| Phase 2: Code Signing & Notarization | 1.5 weeks | Week 2.5 | Includes pre-flight + buffer |
| Phase 3: Homebrew Distribution | 1 week | Week 3.5 | With automation |
| Phase 4: Documentation & Release | 1 week | Week 4.5 | With first-launch UX |
| **Total (Account Ready)** | **4.5 weeks** | **~1 month** | |
| **Total (From Scratch)** | **5.5 weeks** | **~1.3 months** | Includes account setup |

---

## Next Actions

1. **Immediate**: Verify Apple Developer account status
2. **Phase 1 Start**: Build fresh DMGs and begin manual testing
3. **Evidence Collection**: Document all test results in evidence bundle
4. **Phase 2 Prep**: While testing, prepare code signing configuration

**Status**: ✅ **Plan approved - ready to proceed with Phase 1**
