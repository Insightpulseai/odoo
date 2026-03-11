# Phase 3 Universal Harness - Quick Reference

**Status**: ✅ Complete (Commit: 39bab67d)
**Date**: 2026-02-12 03:18

---

## What Was Shipped

**Tool-agnostic Playwright manual testing harness** that works with Claude Code, Codex, Copilot, Gemini, or any editor/agent.

---

## Commands Quick Reference

### Manual Testing (Interactive)

```bash
cd templates/saas-landing

# Headed mode (see browser window)
pnpm test:e2e:headed

# UI runner (interactive test explorer with time travel)
pnpm test:e2e:ui

# Step debugger (pause, inspect, step through)
pnpm test:e2e:debug

# Codegen (record actions → generate TypeScript code)
pnpm test:e2e:codegen
```

### Local Verification (Idempotent Scripts)

```bash
# Full E2E test suite with fresh install
./scripts/verify_local_e2e.sh

# Update visual regression baselines
./scripts/update_visual_baselines.sh

# Override defaults
PLAYWRIGHT_PROJECT=firefox BASE_URL=http://localhost:3001 ./scripts/verify_local_e2e.sh
```

### Optional CDP Attach

```bash
# Start Chrome with debugging (terminal 1)
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="$(pwd)/.chrome-profile"

# Attach via Playwright (terminal 2)
cd templates/saas-landing
pnpm chrome:cdp:attach

# Custom configuration
CDP_URL="http://127.0.0.1:9222" \
TARGET_URL="http://localhost:3000/dashboard" \
OUT_PATH="screenshot.png" \
pnpm chrome:cdp:attach
```

---

## Key Features

| Feature | Command | Use Case |
|---------|---------|----------|
| **Headed Mode** | `pnpm test:e2e:headed` | See browser window during tests |
| **UI Runner** | `pnpm test:e2e:ui` | Interactive test explorer with time travel |
| **Step Debugger** | `pnpm test:e2e:debug` | Pause, inspect, step through tests |
| **Codegen** | `pnpm test:e2e:codegen` | Record actions → generate TypeScript |
| **CDP Attach** | `pnpm chrome:cdp:attach` | Connect to existing Chrome session |
| **Local Verify** | `./scripts/verify_local_e2e.sh` | Full test suite (idempotent) |
| **Update Baselines** | `./scripts/update_visual_baselines.sh` | Visual regression snapshots |

---

## Tool Compatibility

✅ Works with:
- Claude Code
- GitHub Copilot / OpenAI Codex
- Google Gemini Code Assist
- JetBrains IDEs
- VS Code
- Any editor/agent

❌ No vendor lock-in:
- Not dependent on Claude-specific features
- Standard Playwright commands
- Universal package scripts

---

## Files Added

```
templates/saas-landing/
├── BROWSER_AUTOMATION_PHASE3_UNIVERSAL.md (181 lines) - Complete guide
├── scripts/
│   ├── verify_local_e2e.sh (executable) - Local verification
│   ├── update_visual_baselines.sh (executable) - Snapshot updater
│   └── chrome_cdp_attach.mjs - Optional CDP attach
├── package.json (3 new scripts added)
└── tests/manual/chrome-integration.md (updated with universal link)
```

---

## Integration with Existing Automation

### Phase 1 & 2 (Automated - Unchanged)
- 13 tests × 3 browsers = 39 automated checks
- GitHub Actions CI/CD workflows
- Visual regression on PRs

### Phase 3 (Manual - New)
- Headed mode, UI runner, debugger, codegen
- Idempotent verification scripts
- Optional CDP attach

**Relationship**: Phase 3 complements automation for exploratory testing and test development.

---

## Next Steps

1. **Try UI runner**: `cd templates/saas-landing && pnpm test:e2e:ui`
2. **Try codegen**: `pnpm test:e2e:codegen` (record actions, generates code)
3. **Run verification**: `./scripts/verify_local_e2e.sh`
4. **Read guide**: `BROWSER_AUTOMATION_PHASE3_UNIVERSAL.md`

---

## Validation Status

✅ All scripts executable
✅ Package.json updated (7 test-related scripts)
✅ Documentation complete
✅ Pre-commit hooks passed
✅ Git commit successful (39bab67d)

---

## Resources

- **Phase 3 Guide**: `BROWSER_AUTOMATION_PHASE3_UNIVERSAL.md`
- **Manual Testing Doc**: `tests/manual/chrome-integration.md`
- **Scripts**: `scripts/` directory
- **Playwright Docs**: https://playwright.dev/docs/intro

---

**Summary**: Tool-agnostic manual testing harness complete. Works with any editor/agent. No vendor lock-in.
