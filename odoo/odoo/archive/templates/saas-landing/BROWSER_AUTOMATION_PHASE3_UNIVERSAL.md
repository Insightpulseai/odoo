# Phase 3 (Universal): Manual / Exploratory Browser Automation (Tool-Agnostic)

This project already uses Playwright for CI/regression. Phase 3 is **not** Claude-specific.
It provides a universal manual harness that works with **any** agent/tool (Codex/Copilot/Claude/Gemini).

## One-time setup

```bash
cd templates/saas-landing
pnpm install
pnpm playwright install --with-deps
```

## Manual / exploratory modes (portable)

**Headed run** (see browser window):
```bash
pnpm test:e2e:headed
```

**UI runner** (interactive test explorer):
```bash
pnpm test:e2e:ui
```

**Step debugger** (pause execution, inspect state):
```bash
pnpm test:e2e:debug
```

**Record actions → generate test code**:
```bash
pnpm test:e2e:codegen
```

## Idempotent local verify script

Run complete E2E test suite with fresh install:
```bash
./scripts/verify_local_e2e.sh
```

Override defaults:
```bash
PLAYWRIGHT_PROJECT=firefox BASE_URL=http://localhost:3001 ./scripts/verify_local_e2e.sh
```

## Visual baseline update (snapshots)

Generate or update visual regression baselines:
```bash
./scripts/update_visual_baselines.sh
```

After running, commit the updated snapshot files:
```bash
git add tests/e2e/specs/*.spec.ts-snapshots
git commit -m "test: update visual regression baselines"
```

## Optional: attach to an existing Chrome (CDP)

If you already run Chrome with remote debugging, you can attach via Playwright (tool-agnostic):

**Start Chrome with remote debugging**:
```bash
# macOS
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="$(pwd)/.chrome-profile" \
  --disable-popup-blocking

# Linux
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$(pwd)/.chrome-profile" \
  --disable-popup-blocking

# Verify connection
curl -s http://127.0.0.1:9222/json/version | jq .
```

**Attach via Playwright CDP**:
```bash
# Default: localhost:9222, dashboard URL
pnpm chrome:cdp:attach

# Custom CDP/URL/output
CDP_URL="http://127.0.0.1:9222" \
TARGET_URL="http://localhost:3000/dashboard" \
OUT_PATH="custom-screenshot.png" \
pnpm chrome:cdp:attach
```

## Why Playwright for Manual Testing?

**Tool-agnostic**: Works with Claude Code, Codex, GitHub Copilot, Gemini, or any editor

**Features**:
- **Headed mode**: See browser window during test execution
- **UI runner**: Point-and-click test explorer with time travel debugging
- **Step debugger**: Pause at any point, inspect page state, step through actions
- **Codegen**: Record browser actions, generates TypeScript test code
- **CDP attach**: Connect to existing Chrome sessions for debugging

**No lock-in**: Unlike Claude-specific `/chrome` commands, these work everywhere

## Quick Reference

| Command | Purpose | Use Case |
|---------|---------|----------|
| `pnpm test:e2e` | Run all tests (headless) | CI/CD, regression testing |
| `pnpm test:e2e:headed` | Run with visible browser | Manual validation, debugging |
| `pnpm test:e2e:ui` | Interactive test explorer | Test development, debugging |
| `pnpm test:e2e:debug` | Step-through debugger | Debugging failing tests |
| `pnpm test:e2e:codegen` | Record → generate code | Creating new tests |
| `pnpm chrome:cdp:attach` | Connect to Chrome CDP | Advanced debugging |
| `./scripts/verify_local_e2e.sh` | Full verification run | Pre-commit validation |
| `./scripts/update_visual_baselines.sh` | Update snapshots | Visual regression updates |

## Examples

### Debug a failing test
```bash
# Run with UI to see what's happening
pnpm test:e2e:ui

# Or use step debugger
pnpm test:e2e:debug
```

### Create a new test by recording
```bash
# Start codegen, perform actions in browser
pnpm test:e2e:codegen

# Generated code appears in terminal
# Copy into new test file
```

### Visual regression workflow
```bash
# 1. Make UI changes
# 2. Update baselines
./scripts/update_visual_baselines.sh

# 3. Review changes
git diff tests/e2e/specs/*.spec.ts-snapshots

# 4. Commit if intentional
git add tests/e2e/specs/*.spec.ts-snapshots
git commit -m "test: update baselines for new button style"
```

### Cross-browser manual testing
```bash
# Test in Firefox
PLAYWRIGHT_PROJECT=firefox pnpm test:e2e:headed

# Test in WebKit (Safari)
PLAYWRIGHT_PROJECT=webkit pnpm test:e2e:headed
```

## Integration with CI/CD

These manual tools complement the automated CI/CD workflows:
- `.github/workflows/saas-landing-e2e.yml` - Automated multi-browser testing
- `.github/workflows/saas-landing-visual-regression.yml` - Visual regression on PRs

**Workflow**:
1. Develop tests locally using `pnpm test:e2e:ui` or `pnpm test:e2e:codegen`
2. Run `./scripts/verify_local_e2e.sh` before committing
3. Push changes - CI runs full test suite automatically
4. Visual changes trigger visual regression workflow

## Resources

- [Playwright Test Documentation](https://playwright.dev/docs/intro)
- [Playwright UI Mode](https://playwright.dev/docs/test-ui-mode)
- [Playwright Codegen](https://playwright.dev/docs/codegen)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
