# Claude Code Chrome Integration - Manual Test Checklist

## Setup
1. Start dev server: `pnpm dev`
2. Start Chrome with debugging: `chrome --remote-debugging-port=9222`
3. Start Claude Code: `claude --chrome`

## Test Cases

### Theme Selector Validation
- [ ] `/chrome navigate to http://localhost:3000/dashboard`
- [ ] `/chrome screenshot initial state` → Save as baseline
- [ ] `/chrome click select dropdown` → Verify themes visible
- [ ] `/chrome select "dark"` → Verify charts update
- [ ] `/chrome screenshot dark theme` → Compare with baseline

### Environment Switching
- [ ] `/chrome click "Staging" button`
- [ ] Verify header changes to "Staging Environment"
- [ ] `/chrome screenshot staging view`

### Tab Navigation
- [ ] `/chrome click "Deployment Logs" tab`
- [ ] Verify log console appears
- [ ] `/chrome click "Monitoring" tab`
- [ ] Verify metrics cards visible

## Automated Screenshot Comparison
Use `claude --chrome` to capture screenshots, then compare with Playwright baselines:

```bash
# Capture with Chrome extension
claude --chrome screenshot --name dashboard-chrome.png

# Compare with Playwright baseline
compare dashboard-chrome.png dashboard-shine.png diff.png
```

## Notes
- Chrome extension provides alternative manual validation workflow
- Use for exploratory testing and visual verification
- Playwright tests provide automated regression coverage

---

## Phase 3 (Universal / Tool-Agnostic)

**Recommended**: Use Playwright for manual/exploratory work across any tool (Codex/Copilot/Claude/Gemini):

See: `../../BROWSER_AUTOMATION_PHASE3_UNIVERSAL.md`

**Key features**:
- **Headed mode**: `pnpm test:e2e:headed` (see browser window)
- **UI runner**: `pnpm test:e2e:ui` (interactive test explorer)
- **Step debugger**: `pnpm test:e2e:debug` (pause and inspect)
- **Codegen**: `pnpm test:e2e:codegen` (record actions → generate code)
- **CDP attach**: `pnpm chrome:cdp:attach` (attach to existing Chrome)

**Portable**: Works with any editor/tool, not just Claude Code.
