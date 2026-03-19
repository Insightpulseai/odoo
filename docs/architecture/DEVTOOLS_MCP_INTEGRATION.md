# DevTools MCP Integration — Preview Shell

> How to use browser debugging with the Preview Shell via MCP.

---

## Overview

The Preview Shell at `localhost:3100/preview` supports agent-assisted browser debugging via the Playwright MCP server already configured in `.mcp.json`.

No additional code is needed — the existing Playwright MCP tools provide full browser inspection capability.

---

## Available MCP Tools for Debugging

| Tool | Purpose |
|------|---------|
| `browser_navigate` | Navigate to preview shell pages |
| `browser_snapshot` | Capture accessible DOM snapshot for visual inspection |
| `browser_console_messages` | Read console output (errors, warnings, logs) |
| `browser_evaluate` | Run JavaScript in the browser context |
| `browser_click` | Interact with UI elements |
| `browser_take_screenshot` | Capture visual screenshot |
| `browser_network_requests` | Inspect network activity |

---

## Common Debugging Workflows

### 1. Inspect diagnostics panel state

```
browser_navigate → http://localhost:3100/preview/components
browser_console_messages → check for captured errors
browser_snapshot → verify DiagnosticsPanel rendered
```

### 2. Trigger and verify error capture

```
browser_navigate → http://localhost:3100/preview/components
browser_click → "Trigger Error" button
browser_console_messages → confirm error captured
browser_snapshot → verify error appears in DiagnosticsPanel
```

### 3. Verify production stripping

```
browser_navigate → http://localhost:3100/preview (production build)
browser_snapshot → confirm DevToolbar and DiagnosticsPanel are absent
```

---

## Configuration

The Playwright MCP server is configured in `.mcp.json`:

```json
{
  "playwright": {
    "type": "stdio",
    "command": "npx",
    "args": ["@anthropic-ai/mcp-playwright@latest"]
  }
}
```

No additional configuration is needed.

---

*Source: Preview Shell architecture (2026-03-18)*
