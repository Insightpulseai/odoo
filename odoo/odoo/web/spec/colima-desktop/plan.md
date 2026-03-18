# Colima Desktop Implementation Plan

## Context

**Why this change is needed:**

Colima is a CLI-first Docker runtime for macOS that provides a lightweight alternative to Docker Desktop. While excellent for command-line users, it lacks the "control plane" UX that Docker Desktop provides: visual status indicators, point-and-click resource configuration, kubernetes toggles, and diagnostics export.

This project creates a **Docker Desktop-like control plane for Colima** that provides:
1. **CLI-first foundation** - A daemon + CLI that wraps Colima operations with a stable REST API
2. **Optional desktop UI** - An Electron menubar app for visual management
3. **Deterministic state** - All configuration and logs under `~/.colima-desktop/`
4. **Security-first design** - Electron contextIsolation, no privileged operations in renderer
5. **Integration not forking** - Uses Colima's CLI, never patches/forks core

**What prompted this:**

User requested an Electron-based "Colima Desktop" after completing the IPAI Control Plane VS Code extension. The goal is to replicate modern SaaS developer workflows (Vercel/Supabase/Odoo.sh style) but for local Colima VM management.

**Intended outcome:**

A production-ready desktop control plane that:
- Provides one-click-equivalent operations (start/stop/restart, resource tuning, K8s toggle)
- Works headlessly (daemon + CLI) for server/automation use cases
- Offers optional Electron UI for developers who prefer visual controls
- Maintains Colima's philosophy (lightweight, CLI-compatible, no vendor lock-in)

---

## Architecture Overview

**Hybrid approach:** CLI + daemon core (`tools/`) with separate optional Electron UI (`apps/`)

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interfaces                         │
├─────────────────────┬───────────────────────────────────────┤
│   CLI (yargs)       │   Electron UI (optional)              │
│   colima-desktop    │   menubar + main window               │
│   status/start/stop │   React + Vite                        │
│   config/logs/diag  │   contextBridge API                   │
└──────────┬──────────┴────────────────┬──────────────────────┘
           │                           │
           │   HTTP (localhost:35100)  │
           ▼                           ▼
    ┌──────────────────────────────────────────────┐
    │         Daemon (Fastify REST API)            │
    │  /v1/status /v1/lifecycle /v1/config        │
    │  /v1/logs /v1/diagnostics /v1/docker        │
    └───────────────────┬──────────────────────────┘
                        │
           ┌────────────┴────────────┐
           │  Colima CLI Integration  │
           │  colima start/stop/...   │
           │  lima logs / docker ctx  │
           └─────────────────────────┘
```

**Why this architecture:**
- ✅ Follows repo's CLI-first philosophy (matches `agent-router`, `diagramflow`)
- ✅ Electron UI is optional enhancement, not core dependency
- ✅ Daemon can run headless for server/automation scenarios
- ✅ Clean separation of concerns (business logic vs presentation)
- ✅ Easier testing (daemon unit tests separate from UI integration tests)

---

## Directory Structure

```
/Users/tbwa/Documents/GitHub/Insightpulseai/odoo/

spec/colima-desktop/              # Spec Kit bundle (SSOT)
├── constitution.md               # Non-negotiables, security, architecture rules
├── prd.md                        # Requirements (from user spec patches)
├── plan.md                       # This file
└── tasks.md                      # Generated task breakdown (after approval)

tools/colima-desktop/             # Core daemon + CLI (standalone npm package)
├── src/
│   ├── daemon/                   # REST API server
│   │   ├── server.ts            # Fastify app, PID management, graceful shutdown
│   │   ├── routes/
│   │   │   ├── status.ts        # GET /v1/status (state, resources, uptime)
│   │   │   ├── lifecycle.ts     # POST /v1/lifecycle/{start,stop,restart}
│   │   │   ├── config.ts        # GET/PUT /v1/config (cpu, memory, disk, k8s)
│   │   │   ├── logs.ts          # GET /v1/logs?tail=N&source={colima,lima,daemon}
│   │   │   ├── diagnostics.ts   # POST /v1/diagnostics (tar.gz bundle)
│   │   │   └── docker.ts        # GET/POST /v1/docker/context
│   │   └── services/
│   │       ├── colima.ts        # Colima CLI wrapper (typed, error-handled)
│   │       ├── kubernetes.ts    # K8s toggle + kubecontext validation
│   │       ├── docker-context.ts # docker context management
│   │       └── diagnostics.ts   # Bundle creation (config + logs + versions)
│   ├── cli/                     # yargs CLI
│   │   ├── index.ts             # yargs app setup
│   │   └── commands/
│   │       ├── daemon.ts        # start/stop/status daemon
│   │       ├── status.ts        # colima-desktop status
│   │       ├── start.ts         # colima-desktop start [--cpu N]
│   │       ├── stop.ts          # colima-desktop stop
│   │       ├── restart.ts       # colima-desktop restart
│   │       ├── config.ts        # get/set config
│   │       └── logs.ts          # tail logs
│   ├── shared/                  # Shared types + utilities
│   │   ├── types.ts             # API contracts, config schema, state models
│   │   ├── config.ts            # YAML config loader/validator
│   │   └── api-client.ts        # Daemon REST client (for CLI)
│   └── index.ts                 # Entry points (daemon + CLI)
├── test/
│   ├── unit/                    # vitest unit tests
│   │   ├── colima.test.ts      # CLI wrapper parsing
│   │   ├── config.test.ts      # YAML validation
│   │   └── api-client.test.ts  # REST client
│   └── integration/             # End-to-end tests
│       ├── daemon.test.ts      # Daemon lifecycle
│       └── cli.test.ts         # CLI commands
├── package.json                 # Standalone package (NOT in pnpm workspace)
├── tsconfig.json
├── vitest.config.ts
└── README.md

apps/colima-desktop-ui/          # Optional Electron UI (standalone)
├── src/
│   ├── main/                    # Electron main process (privileged)
│   │   ├── index.ts             # App lifecycle, BrowserWindow setup
│   │   ├── menu.ts              # Menubar integration (macOS tray)
│   │   ├── preload.ts           # contextBridge API (security boundary)
│   │   └── ipc-handlers.ts      # ipcMain.handle (REST API delegation)
│   ├── renderer/                # React UI (unprivileged)
│   │   ├── App.tsx              # Root component
│   │   ├── components/
│   │   │   ├── Status.tsx       # Status panel (CPU, RAM, uptime)
│   │   │   ├── Controls.tsx     # Start/Stop/Restart buttons
│   │   │   ├── Settings.tsx     # Resource sliders + K8s toggle
│   │   │   └── Logs.tsx         # Log viewer (tail -f style)
│   │   └── hooks/
│   │       └── useColima.ts     # React hooks for window.colima API
│   └── shared/
│       └── types.ts             # Shared with daemon (API contracts)
├── package.json                 # Standalone Electron app
├── electron-builder.yml         # DMG packaging config
├── vite.config.ts               # Vite for renderer build
└── README.md
```

**Key organizational decisions:**
1. **tools/colima-desktop/** is **standalone** (not in pnpm workspace) - matches `agent-router` pattern
2. **apps/colima-desktop-ui/** is **standalone** - Electron apps typically self-contained
3. **spec/colima-desktop/** follows Spec Kit convention (constitution, prd, plan, tasks)
4. **State lives in user home**: `~/.colima-desktop/` (config, logs, PID file)

---

## Technology Stack

### Daemon + CLI (`tools/colima-desktop/`)

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **HTTP Framework** | Fastify 4.x | Faster than Express, excellent TypeScript support, plugin ecosystem |
| **CLI Framework** | yargs 17.x | Matches `diagramflow` precedent, robust arg parsing, help generation |
| **Build Tool** | TypeScript 5.7+ | Standard in repo, type safety, matches all tools |
| **Test Runner** | vitest 2.x | Repo standard, fast, ESM-native |
| **Config Format** | YAML | Matches repo pattern (`agent-router`, workflow files) |
| **Process Manager** | Node child_process | Built-in, sufficient for `colima` CLI spawning |

### Electron UI (`apps/colima-desktop-ui/`)

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Desktop Framework** | Electron 28+ | User requirement, mature ecosystem, cross-platform potential |
| **UI Framework** | React 18 | Matches `ops-control` and `web/*` apps in repo |
| **Build Tool** | Vite 5.x | Fast HMR, excellent React+TS support, matches `ops-control` |
| **State Management** | Zustand | Lightweight, no boilerplate, good for simple daemon-backed state |
| **Packaging** | electron-builder | Industry standard, DMG/AppImage/exe support |
| **E2E Testing** | Playwright | Can test Electron apps, already in repo for VS Code extension |

### Shared

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Node Runtime** | >= 18.0.0 | Repo requirement (root package.json engines) |
| **Package Manager** | pnpm | Repo standard (workspace config) |
| **Linting** | ESLint 9 (flat config) | Matches recent VS Code extension work |
| **Formatting** | Prettier (optional) | Not strictly required, repo doesn't enforce |

---

## State Management

### Configuration (`~/.colima-desktop/config.yaml`)

```yaml
# Daemon settings
daemon:
  port: 35100              # REST API port
  host: localhost          # Bind address (localhost only for security)
  autostart: false         # Launch daemon on login (macOS launchd)

# Colima VM configuration
colima:
  cpu: 4                   # CPU cores
  memory: 8                # RAM in GB
  disk: 60                 # Disk in GB
  kubernetes: false        # Enable/disable K8s
  runtime: docker          # docker | containerd (future)

# Logging
logs:
  retention_days: 7        # Auto-cleanup after N days
  max_lines: 1000          # Max lines per log file before rotation
  level: info              # debug | info | warn | error
```

### Runtime State (`~/.colima-desktop/`)

```
~/.colima-desktop/
├── config.yaml           # User configuration (YAML)
├── daemon.pid            # Daemon process ID (lock file)
├── logs/
│   ├── daemon.log       # Daemon structured logs (JSON lines)
│   ├── colima.log       # Captured colima CLI output
│   └── lima.log         # Captured lima output
└── diagnostics/         # Generated bundles
    └── diag-20260215-1430.tar.gz
```

**State management rules:**
1. **Atomic writes** - Write to `.tmp` then rename (prevent corruption)
2. **Validation** - All config changes validated before applying
3. **Cleanup** - Old logs auto-deleted after `retention_days`
4. **No hidden state** - All persistent data under `~/.colima-desktop/`

---

## Critical Files

Based on this plan, the **5 most critical files** for implementation are:

### 1. `tools/colima-desktop/src/daemon/services/colima.ts`
**Why critical:** Core integration layer with Colima CLI; single source of truth for all VM operations

**Responsibilities:**
- Spawn `colima` commands (`start`, `stop`, `status`, `list`, `version`)
- Parse stdout/stderr into typed interfaces
- Handle errors (command not found, non-zero exit, timeout)
- Provide typed API for all Colima operations

### 2. `tools/colima-desktop/src/daemon/server.ts`
**Why critical:** Daemon entrypoint; registers all routes, manages lifecycle, handles graceful shutdown

**Responsibilities:**
- Create Fastify app
- Register all v1 routes
- PID file management
- Graceful shutdown handlers (SIGTERM, SIGINT)

### 3. `apps/colima-desktop-ui/src/main/preload.ts`
**Why critical:** Electron security boundary; only interface between renderer and privileged operations

**Security requirements:**
- contextIsolation: enabled (MUST)
- nodeIntegration: disabled (MUST)
- sandbox: enabled (MUST)

### 4. `spec/colima-desktop/constitution.md`
**Why critical:** Non-negotiable constraints; defines what can and cannot be done

### 5. `tools/colima-desktop/src/shared/types.ts`
**Why critical:** Shared type definitions; ensures type safety across daemon, CLI, and UI

---

## Phased Implementation

### Phase 1: Foundation & Spec Kit (Week 1-2)

**Goals:**
- Establish Spec Kit bundle (SSOT)
- Scaffold directory structure
- Set up build tooling
- Implement core services

**Deliverables:**
1. ✅ `spec/colima-desktop/` bundle (constitution, prd, plan, tasks)
2. ✅ `tools/colima-desktop/` directory structure
3. ✅ TypeScript config, package.json, basic build
4. ✅ Colima CLI wrapper service (`services/colima.ts`)
5. ✅ Config YAML schema + loader (`shared/config.ts`)
6. ✅ Unit tests for core services (vitest)

**Verification:**
```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo/tools/colima-desktop
pnpm install
pnpm build
pnpm test  # All tests pass
node dist/index.js --help  # CLI loads
```

**Risks:** Low (follows established repo patterns)

---

### Phase 2: Daemon + CLI Core (Week 3-4)

**Goals:**
- Build REST API daemon
- Implement CLI commands
- Integration testing

**Deliverables:**
1. ✅ Fastify daemon
2. ✅ Daemon lifecycle (start/stop/status)
3. ✅ yargs CLI (status, start, stop, restart, config, logs, diagnostics)
4. ✅ REST API client
5. ✅ Integration tests

**Risks:** Medium (Fastify new to repo)

---

### Phase 3: Electron UI (Week 5-6)

**Goals:**
- Build Electron menubar app
- Implement React UI components
- Security audit

**Deliverables:**
1. ✅ Electron app structure
2. ✅ Menubar tray integration
3. ✅ Main window (Settings, Logs)
4. ✅ Preload + contextBridge
5. ✅ IPC handlers
6. ✅ React components
7. ✅ electron-builder config

**Risks:** High (no Electron precedent in repo)

---

### Phase 4: Polish, Docs, CI (Week 7-8)

**Goals:**
- Documentation
- CI workflows
- Final testing
- Production readiness

**Deliverables:**
1. ✅ README documentation
2. ✅ Makefile targets
3. ✅ CI workflow
4. ✅ Security audit
5. ✅ Homebrew formula (optional)

**Risks:** Low

---

**Plan Status:** Draft - Pending Approval
**Version:** 1.0
**Author:** Claude (Plan Agent)
**Date:** 2026-02-15
**Repository:** /Users/tbwa/Documents/GitHub/Insightpulseai/odoo
