# Phase 3 Universal Manual Harness Implementation Summary

**Date**: 2026-02-12 03:18
**Scope**: Tool-agnostic Playwright manual testing harness
**Status**: ✅ Complete
**Commit**: 39bab67d

---

## Context

**Problem**: Original Phase 3 plan relied on Claude-specific `/chrome` command, creating vendor lock-in and limiting portability to other tools (Codex, Copilot, Gemini).

**Solution**: Convert Phase 3 to universal Playwright-based manual harness that works with any editor/agent/tool.

---

## Implementation Details

### Scripts Added (templates/saas-landing/scripts/)

#### 1. verify_local_e2e.sh (Idempotent Local Verification)
```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

: "${PLAYWRIGHT_PROJECT:=chromium}"
: "${BASE_URL:=http://localhost:3000}"

echo "==> pnpm install"
pnpm install --frozen-lockfile

echo "==> install playwright browsers"
pnpm playwright install --with-deps

echo "==> run e2e (${PLAYWRIGHT_PROJECT})"
PLAYWRIGHT_BASE_URL="${BASE_URL}" pnpm test:e2e --project="${PLAYWRIGHT_PROJECT}"
```

**Features**:
- Environment variable overrides (PLAYWRIGHT_PROJECT, BASE_URL)
- Idempotent (safe to run repeatedly)
- Fresh install every time (--frozen-lockfile)

#### 2. update_visual_baselines.sh (Visual Regression Baseline Updater)
```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> pnpm install"
pnpm install --frozen-lockfile

echo "==> install playwright browsers"
pnpm playwright install --with-deps

echo "==> update snapshots for visual spec"
pnpm playwright test dashboard-visual.spec.ts --update-snapshots
```

**Features**:
- Updates visual regression baselines
- Idempotent
- Commits required after running

#### 3. chrome_cdp_attach.mjs (Optional CDP Attach Harness)
```javascript
import { chromium } from '@playwright/test';

const cdpURL = process.env.CDP_URL || 'http://127.0.0.1:9222';
const targetURL = process.env.TARGET_URL || 'http://localhost:3000/dashboard';
const outPath = process.env.OUT_PATH || 'cdp-dashboard.png';

(async () => {
  const browser = await chromium.connectOverCDP(cdpURL);
  const context = browser.contexts()[0] || await browser.newContext();
  const page = context.pages()[0] || await context.newPage();
  await page.goto(targetURL, { waitUntil: 'domcontentloaded' });
  await page.screenshot({ path: outPath, fullPage: true });
  await browser.close();
  console.log(`Wrote screenshot: ${outPath}`);
})();
```

**Features**:
- Playwright-based CDP attach (tool-agnostic)
- Environment variable configuration
- Works with any existing Chrome debugging session

---

### Package Scripts Added

```json
{
  "test:e2e:headed": "playwright test --project=chromium --headed",
  "test:e2e:codegen": "playwright codegen http://localhost:3000/dashboard",
  "chrome:cdp:attach": "node scripts/chrome_cdp_attach.mjs"
}
```

**Pre-existing scripts** (already in package.json):
- `test:e2e:ui` - Interactive test explorer
- `test:e2e:debug` - Step debugger

---

### Documentation Added

#### BROWSER_AUTOMATION_PHASE3_UNIVERSAL.md (181 lines)

**Sections**:
1. One-time setup instructions
2. Manual/exploratory modes (headed, UI, debug, codegen)
3. Idempotent scripts documentation
4. Visual baseline update workflow
5. Optional CDP attach instructions
6. Why Playwright for manual testing
7. Quick reference table
8. Examples (debugging, creating tests, visual regression)
9. Cross-browser manual testing
10. CI/CD integration workflow
11. Resources

**Key Message**: Tool-agnostic, works with any editor/agent

---

### Documentation Updated

#### tests/manual/chrome-integration.md

**Changes**: Added Phase 3 universal section at bottom:
- Links to BROWSER_AUTOMATION_PHASE3_UNIVERSAL.md
- Lists key features (headed, UI, debug, codegen, CDP)
- Notes portability (works with any editor/tool)

---

## Benefits

### Tool-Agnostic
- ✅ Works with Claude Code
- ✅ Works with GitHub Copilot / OpenAI Codex
- ✅ Works with Gemini Code Assist
- ✅ Works with any editor (VS Code, JetBrains, Vim, etc.)
- ❌ No vendor lock-in to Claude-specific features

### Portable
- Playwright features available everywhere
- Standard package scripts (pnpm/npm/yarn compatible)
- Cross-platform (macOS, Linux, Windows)

### Idempotent
- Scripts can be run repeatedly safely
- Fresh install every time (--frozen-lockfile)
- No state pollution between runs

### Universal
- Headed mode (see browser window)
- UI runner (interactive test explorer with time travel)
- Step debugger (pause, inspect, step through)
- Codegen (record actions → generate TypeScript)
- CDP attach (connect to existing Chrome)

---

## Usage Examples

### Manual Exploration
```bash
cd templates/saas-landing

# See browser window during tests
pnpm test:e2e:headed

# Interactive test explorer
pnpm test:e2e:ui

# Step-through debugger
pnpm test:e2e:debug

# Record actions → generate code
pnpm test:e2e:codegen
```

### Local Verification
```bash
# Full test suite with fresh install
./scripts/verify_local_e2e.sh

# Override browser/URL
PLAYWRIGHT_PROJECT=firefox BASE_URL=http://localhost:3001 ./scripts/verify_local_e2e.sh
```

### Visual Baseline Updates
```bash
# Update snapshots
./scripts/update_visual_baselines.sh

# Review changes
git diff tests/e2e/specs/*.spec.ts-snapshots

# Commit if intentional
git add tests/e2e/specs/*.spec.ts-snapshots
git commit -m "test: update baselines for new button style"
```

### Optional CDP Attach
```bash
# Start Chrome with remote debugging
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="$(pwd)/.chrome-profile"

# Verify connection
curl -s http://127.0.0.1:9222/json/version | jq .

# Attach via Playwright
pnpm chrome:cdp:attach

# Custom CDP/URL/output
CDP_URL="http://127.0.0.1:9222" \
TARGET_URL="http://localhost:3000/dashboard" \
OUT_PATH="custom-screenshot.png" \
pnpm chrome:cdp:attach
```

---

## Validation

### Pre-Commit Checks
```
✅ Generate addons README files from fragments - Passed
✅ Generate addons icons - Passed
✅ trim trailing whitespace - Passed
✅ fix end of files - Passed
✅ check json - Passed
✅ check for merge conflicts - Passed
✅ check for added large files - Passed
```

### Files Changed
```
6 files changed, 244 insertions(+), 1 deletion(-)
- BROWSER_AUTOMATION_PHASE3_UNIVERSAL.md (NEW) - 181 lines
- package.json (MODIFIED) - 3 new scripts
- scripts/chrome_cdp_attach.mjs (NEW) - 15 lines
- scripts/update_visual_baselines.sh (NEW) - 12 lines
- scripts/verify_local_e2e.sh (NEW) - 15 lines
- tests/manual/chrome-integration.md (MODIFIED) - 17 lines added
```

---

## Comparison: Before vs After

### Before (Claude-Specific)
```bash
# Claude Code only
claude --chrome
/chrome navigate to http://localhost:3000/dashboard
```

**Issues**:
- ❌ Vendor lock-in to Claude Code
- ❌ Doesn't work with Codex/Copilot/Gemini
- ❌ Requires special Claude extension
- ❌ Not reproducible in CI

### After (Universal Playwright)
```bash
# Works with any tool/editor
pnpm test:e2e:headed     # See browser
pnpm test:e2e:ui         # Interactive explorer
pnpm test:e2e:debug      # Step debugger
pnpm test:e2e:codegen    # Record → generate code
```

**Benefits**:
- ✅ Tool-agnostic (works everywhere)
- ✅ Portable (standard Playwright features)
- ✅ Idempotent (scripts safe to re-run)
- ✅ CI-compatible (same tools as automation)

---

## Integration with Existing Infrastructure

### CI/CD Workflows (No Changes Required)
- `.github/workflows/saas-landing-e2e.yml` - Automated multi-browser testing
- `.github/workflows/saas-landing-visual-regression.yml` - Visual regression on PRs

**Workflow**:
1. Develop tests locally using `pnpm test:e2e:ui` or `pnpm test:e2e:codegen`
2. Run `./scripts/verify_local_e2e.sh` before committing
3. Push changes - CI runs full test suite automatically
4. Visual changes trigger visual regression workflow

### Automation Phase 1 & 2 (Unchanged)
- 13 tests × 3 browsers = 39 automated checks
- GitHub Actions multi-browser matrix
- Visual regression baselines

**Phase 3 complements automation**:
- Automation: Regression testing, CI/CD
- Manual harness: Exploratory testing, debugging, test development

---

## Rollback Strategy

If Phase 3 changes cause friction:

```bash
# Option 1: Revert commit
git log --oneline -n 10
git revert 39bab67d

# Option 2: Ignore Phase 3 files (keep Phase 1 & 2)
# Simply don't use the new scripts/commands
# Existing automation (Phase 1 & 2) unaffected
```

---

## Next Steps (User Verification)

1. **Try headed mode**: `cd templates/saas-landing && pnpm test:e2e:headed`
2. **Try UI runner**: `pnpm test:e2e:ui`
3. **Try codegen**: `pnpm test:e2e:codegen` (record actions, generates code)
4. **Run verification script**: `./scripts/verify_local_e2e.sh`
5. **Update baselines** (if needed): `./scripts/update_visual_baselines.sh`

---

## Resources

- **Phase 3 Guide**: `templates/saas-landing/BROWSER_AUTOMATION_PHASE3_UNIVERSAL.md`
- **Scripts**: `templates/saas-landing/scripts/`
- **Manual Testing**: `templates/saas-landing/tests/manual/chrome-integration.md`
- **Playwright Docs**: https://playwright.dev/docs/intro
- **Playwright UI Mode**: https://playwright.dev/docs/test-ui-mode
- **Playwright Codegen**: https://playwright.dev/docs/codegen

---

**Implementation Status**: ✅ Complete
**Commit**: 39bab67d
**Last Updated**: 2026-02-12 03:18

---

*Evidence generated by Claude Code execution agent*
