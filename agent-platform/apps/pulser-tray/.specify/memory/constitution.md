# Constitution — Pulser Tray

> Governing principles for the Pulser Tray systray shell.
> Spec/plan/tasks deferred until dependencies (Service Bus, Platform API, Odoo MCP) ship in R2-R3.

---

## 1. Purpose

Pulser Tray is a **systray shell** — the thinnest native wrapper that puts a persistent icon in the macOS menu bar / Windows system tray. The icon surfaces live Pulser agent activity via OS notifications and opens a webview panel for artifact preview and human-in-the-loop approvals.

It is NOT a desktop application. The webview loads the same ops-console UI. Tauri provides exactly three things a browser cannot: tray icon, OS-native notifications, and a global approve hotkey. Everything else is the web surface.

The ops-console stays authoritative. The tray is ambient presence on top of it.

### Build sequence

1. **Web-first.** Run viewer + artifact previewer + approve flow ships as an ops-console route. No new app. Works on any device.
2. **Systray wrapper when demand proves it.** Tauri wraps the same webview. Incremental cost is small because the UI already exists. The constitution governs this wrapper.

## 2. Non-negotiable principles

### 2.1 Read + approve only

The tray never initiates writes to business data. It may:
- Display agent run status, artifacts, and diffs
- Approve, retry, or cancel a run via the Platform API's human-in-the-loop gate
- Open a source record in browser (GitHub, ADO, Odoo)

It may NOT:
- Create invoices, journal entries, or any Odoo transactional record
- Modify agent instructions or tool configuration
- Push code or merge PRs

### 2.2 Per-user isolation

Each user gets a dedicated Service Bus subscription with tenant filter. A tray client authenticated as user A cannot receive events from tenant B. This is enforced at the subscription level, not in client code.

### 2.3 Azure-native only

| Concern | Technology | Forbidden |
|---|---|---|
| Auth | Entra ID OAuth 2.0 device code flow | API keys, local passwords |
| Token cache | OS keyring via tauri-plugin-stronghold | Plaintext, .env files |
| Event stream | Azure Service Bus topic subscription | WebSocket to custom server, polling |
| Artifact storage | Azure Blob (SAS URL from Platform API) | Local cache as source of truth |
| Telemetry | App Insights OTLP | Custom telemetry, Mixpanel, Segment |
| Distribution | Azure Pipelines → Azure Blob | GitHub Actions, Vercel, Homebrew tap |
| Code signing | Key Vault-backed cert (Windows), Apple notarization via `xcrun notarytool` | Self-signed, unsigned |

### 2.4 Tauri 2 as systray shell

Runtime is Tauri 2 (Rust core + system WebView). Not Electron. Not native-only. Tauri's job is limited to three things a browser cannot do:

1. **Tray icon** — persistent presence in menu bar / system tray
2. **OS notifications** — native APNS / WinRT push
3. **Global hotkey** — approve/dismiss without switching windows

The webview inside Tauri loads the ops-console web UI. No separate frontend. If Tauri disappeared, the ops-console route still works — you just lose ambient presence.

### 2.5 Spec-kit awareness

The tray recognizes `.specify/` directory trees and renders them as workflow views (constitution → spec → plan → tasks → contracts). This is a first-class feature, not an afterthought. Clicking a phase opens the artifact in the preview pane. Clicking a feature ID opens the matching ADO work item.

## 3. Blast-radius guardrails

1. **No direct Odoo DB access.** All Odoo interaction goes through `ipai-odoo-mcp` or the Platform API. The tray never holds a database connection string.
2. **No credential storage beyond OS keyring.** Entra tokens cached in stronghold (hardware-backed where available). No refresh tokens in config files.
3. **No background writes.** The tray may poll or subscribe to events, but never silently modifies state. Every write action requires an explicit user gesture (click approve, click retry).
4. **Notification-only by default.** OS notifications alert the user; they choose whether to act. No auto-approve, no auto-retry.

## 4. Target platforms

- macOS (Apple Silicon + Intel) — `.dmg`
- Windows 10/11 (x64 + arm64) — `.msi`
- Linux is out of scope (no target users)

## 5. Dependencies (must ship before tray development starts)

| Dependency | Owner | Target |
|---|---|---|
| Azure Service Bus namespace + `agent-runs` topic | Platform engineering | R2 |
| Platform API (`/runs`, `/artifacts`, `/actions`) | Platform engineering | R2 |
| `ipai-odoo-mcp` server | Odoo platform | R2-R3 |
| Tray Entra app registration | Identity | Pre-dev (trivial) |

## 6. Artifact preview scope

The tray previews artifacts in-pane without download or external app:

| Type | Engine |
|---|---|
| Spec-kit docs | markdown-it + custom spec-kit plugin |
| Markdown / MDX | markdown-it + Prism + Mermaid |
| Word (.docx) | docx-preview |
| PowerPoint (.pptx) | pptx-parser + thumbnail strip |
| Excel / CSV | SheetJS |
| PDF | PDF.js |
| Code (.py, .ts, .sql, .bicep, .xml) | Monaco read-only |
| Structured (.json, .yaml, .toml) | Monaco with language mode |
| Diagrams (.mermaid, .svg) | Mermaid CLI / native SVG |
| Images | Native `<img>` |
| Notebooks (.ipynb) | nbviewer-style render |

## 7. Repo placement

```
agent-platform/apps/pulser-tray/
```

This is the Agent plane, apps directory, following existing `agent-platform/` conventions.

## 8. What this document does NOT decide

- Specific API contract (deferred to `contracts/tray-api.openapi.yaml` in spec phase)
- Task breakdown and sequencing (deferred to `tasks.md`)
- UI/UX design and component library (Fluent 2 tokens from `design/foundations/tenants/pulser.tokens.json` assumed but not locked)
- Versioning and release cadence
- Multi-agent orchestration patterns (depends on MAF integration shape)

## 9. Cross-references

- `design/foundations/tenants/pulser.tokens.json` — Pulser vertical brand ramp
- `docs/architecture/vertical-boundaries.md` — three-vertical doctrine
- `CLAUDE.md` §"Agentic Workflow Security Doctrine" — 3-tier defense, zero-secret agents
- Memory `feedback_foundry_reuse_doctrine.md` — canonical Foundry reuse
- Memory `project_odoo_mcp_server_p0_gap.md` — Odoo MCP dependency

---

*Status: constitution locked. Spec/plan/tasks deferred until R2 dependencies ship.*
