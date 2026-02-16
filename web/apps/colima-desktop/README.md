# Colima Desktop

Docker Desktop-like control plane for Colima on macOS.

**Status:** Phase 1 - Foundation (In Progress)

---

## Overview

Colima Desktop provides a **Docker Desktop-like control plane** for [Colima](https://github.com/abiosoft/colima), the lightweight Docker runtime for macOS.

**Architecture:**
- **CLI-first foundation**: Daemon + CLI that wraps Colima with a stable REST API
- **Optional Electron UI**: Menubar app for visual management (coming in Phase 3)
- **Deterministic state**: All configuration and logs under `~/.colima-desktop/`
- **Security-first**: Electron contextIsolation, no privileged operations in renderer
- **Integration not forking**: Uses Colima's CLI, never patches/forks core

---

## Project Structure

```
tools/colima-desktop/
├── src/
│   ├── daemon/              # REST API server (Fastify)
│   │   ├── server.ts       # Main daemon entrypoint
│   │   ├── routes/         # API endpoints
│   │   └── services/       # Business logic
│   │       ├── colima.ts   # ✅ Colima CLI wrapper (implemented)
│   │       ├── kubernetes.ts
│   │       ├── docker-context.ts
│   │       └── diagnostics.ts
│   ├── cli/                # Command-line interface (yargs)
│   │   ├── index.ts
│   │   └── commands/
│   └── shared/             # Shared utilities
│       ├── types.ts        # ✅ API contracts (implemented)
│       ├── config.ts       # ✅ YAML config management (implemented)
│       └── api-client.ts
├── test/
│   ├── unit/
│   └── integration/
├── spec/                   # Spec Kit bundle
│   └── colima-desktop/
│       ├── constitution.md # ✅ Non-negotiables (implemented)
│       ├── plan.md         # ✅ Implementation plan (implemented)
│       ├── prd.md          # Requirements (coming)
│       └── tasks.md        # Task breakdown (coming)
└── README.md               # This file
```

---

## Implementation Status

### Phase 1: Foundation & Spec Kit ✅ (Current)

**Completed:**
- ✅ Spec Kit bundle (`spec/colima-desktop/`)
  - ✅ `constitution.md` - Non-negotiable rules and security constraints
  - ✅ `plan.md` - Complete implementation plan
- ✅ Directory structure scaffolded
- ✅ TypeScript configuration (`tsconfig.json`)
- ✅ Build tooling (vitest, ESLint)
- ✅ **Core services implemented:**
  - ✅ `src/shared/types.ts` - Complete API contracts and type system
  - ✅ `src/daemon/services/colima.ts` - Colima CLI wrapper with full CRUD operations
  - ✅ `src/shared/config.ts` - YAML config loader with validation and atomic writes

**Next Steps:**
1. Implement unit tests for core services (vitest)
2. Create daemon REST API server (Fastify)
3. Build CLI commands (yargs)

### Phase 2: Daemon + CLI Core (Week 3-4)

**Planned:**
- Fastify daemon with all v1 API endpoints
- Daemon lifecycle management (start/stop/status, PID file)
- yargs CLI (status, start, stop, restart, config, logs, diagnostics)
- REST API client for CLI → daemon communication
- Integration tests

### Phase 3: Electron UI (Week 5-6)

**Planned:**
- Electron menubar app (macOS tray integration)
- React UI components (Status, Controls, Settings, Logs)
- Preload script (contextBridge security boundary)
- IPC handlers (REST API delegation)
- electron-builder packaging (DMG)

### Phase 4: Polish, Docs, CI (Week 7-8)

**Planned:**
- Comprehensive README documentation
- Makefile targets
- CI workflow (lint, typecheck, test, build)
- Security audit (Electron security linter)
- Homebrew formula (optional)

---

## Key Design Decisions

### 1. CLI-First Architecture

**Why:** Daemon + CLI must work without Electron UI

```
CLI ──→ Daemon (REST API) ──→ Colima CLI
         ↑
         │
    Electron UI (optional)
```

**Benefits:**
- Scriptable automation (CI/CD, server environments)
- Headless deployment (no GUI required)
- Testable without UI complexity

### 2. No Colima Forking

**Constitution Rule:** Integration via `colima` CLI only. Never patch/fork Colima core.

**Why:**
- Maintain compatibility with upstream releases
- Respect project boundaries
- Avoid maintenance burden of forks

**Implementation:**
- All operations via `colima` CLI binary
- Config edits follow Colima conventions
- Docker context managed via `docker context` CLI

### 3. Security-First Electron Design

**Constitution Rules:**
- contextIsolation: MUST be enabled
- nodeIntegration: MUST be disabled
- sandbox: MUST be enabled
- Preload script: Only interface via contextBridge

**Why:**
- Renderer process cannot access Node.js APIs
- No privileged operations in untrusted code
- Narrow API surface prevents security vulnerabilities

### 4. Deterministic State Management

**All state under `~/.colima-desktop/`:**

```
~/.colima-desktop/
├── config.yaml           # User configuration
├── daemon.pid            # Daemon process ID (lock file)
├── logs/
│   ├── daemon.log       # Structured JSON logs
│   ├── colima.log       # Captured Colima CLI output
│   └── lima.log         # Captured Lima output
└── diagnostics/         # Generated bundles
```

**Why:**
- Predictable state location
- Easy backup/restore
- No hidden files scattered across system

### 5. Atomic Writes

**Pattern:** Write to `.tmp` → rename (atomic operation)

**Why:**
- Prevents corruption if write interrupted
- Filesystem guarantees atomicity of rename
- Config always valid (never partial state)

---

## API Design (v1)

**Base URL:** `http://localhost:35100/v1`

**Endpoints:**

### Status
```
GET /v1/status
Response:
{
  "state": "running" | "stopped" | "starting" | "stopping" | "error",
  "cpu": { "allocated": 4, "usage_percent": 23.5 },
  "memory": { "allocated_gb": 8, "used_gb": 3.2 },
  "disk": { "allocated_gb": 60, "used_gb": 12.5 },
  "kubernetes": { "enabled": false, "context": null },
  "docker_context": { "active": "colima", "socket": "~/.colima/default/docker.sock" },
  "uptime_seconds": 86400,
  "colima_version": "0.9.0",
  "lima_version": "1.0.2"
}
```

### Lifecycle
```
POST /v1/lifecycle/start
Body: { cpu?: number, memory?: number, disk?: number }

POST /v1/lifecycle/stop

POST /v1/lifecycle/restart
Body: { cpu?: number, memory?: number, disk?: number }
```

### Configuration
```
GET /v1/config
PUT /v1/config
Body: { cpu?: number, memory?: number, disk?: number, kubernetes?: boolean }
```

### Logs
```
GET /v1/logs?tail=200&source=colima|lima|daemon
```

### Diagnostics
```
POST /v1/diagnostics
Response: { bundle_path, size_bytes, timestamp, contents }
```

---

## Configuration

**Location:** `~/.colima-desktop/config.yaml`

**Schema:**
```yaml
daemon:
  port: 35100
  host: localhost
  autostart: false

colima:
  cpu: 4
  memory: 8
  disk: 60
  kubernetes: false
  runtime: docker

logs:
  retention_days: 7
  max_lines: 1000
  level: info
```

**Validation:**
- CPU: 1-16 cores
- Memory: 1-32 GB
- Disk: 20-200 GB
- Host: must be `localhost` or `127.0.0.1` (security constraint)

---

## Development

### Prerequisites

- Node.js >= 18.0.0
- pnpm
- Colima installed (`brew install colima`)

### Build

```bash
cd tools/colima-desktop
pnpm install
pnpm build
```

### Test

```bash
pnpm test              # Run all tests
pnpm test:watch        # Watch mode
pnpm test:coverage     # Coverage report
```

### Lint

```bash
pnpm lint              # ESLint
pnpm typecheck         # TypeScript
```

---

## Installation (Coming)

### From Source

```bash
cd tools/colima-desktop
pnpm install
pnpm build
pnpm link --global
```

### Homebrew (Phase 4)

```bash
brew tap insightpulseai/tap
brew install colima-desktop
```

---

## Usage (Coming)

### Daemon

```bash
# Start daemon
colima-desktop daemon start

# Stop daemon
colima-desktop daemon stop

# Check daemon status
colima-desktop daemon status
```

### VM Operations

```bash
# Check VM status
colima-desktop status

# Start VM
colima-desktop start --cpu 4 --memory 8

# Stop VM
colima-desktop stop

# Restart VM
colima-desktop restart
```

### Configuration

```bash
# Show config
colima-desktop config get

# Update config
colima-desktop config set --cpu 6 --kubernetes true

# Set specific key
colima-desktop config set --cpu 6
```

### Logs

```bash
# Tail daemon logs
colima-desktop logs --tail 50 --source daemon

# Tail Colima logs
colima-desktop logs --tail 100 --source colima

# Follow logs (live)
colima-desktop logs --follow
```

### Diagnostics

```bash
# Generate diagnostics bundle
colima-desktop diagnostics

# Output: ~/.colima-desktop/diagnostics/diag-YYYYMMDD-HHMM.tar.gz
```

---

## Testing

### Unit Tests

```bash
cd tools/colima-desktop
pnpm test
```

**Coverage Target:** >80%

**Test Files:**
- `test/unit/colima.test.ts` - Colima CLI wrapper
- `test/unit/config.test.ts` - Config validation
- `test/unit/api-client.test.ts` - REST client

### Integration Tests

```bash
pnpm test:integration
```

**Scenarios:**
- Daemon lifecycle (start → API calls → stop)
- CLI → Daemon → Colima (mocked)
- Config changes → restart required flag

---

## Contributing

See `spec/colima-desktop/constitution.md` for non-negotiable rules and constraints.

**Key Principles:**
1. **No Colima forking** - Integration via CLI only
2. **Security first** - Electron contextIsolation, no privileged renderer operations
3. **CLI-first** - Daemon + CLI must work without UI
4. **Deterministic state** - All state under `~/.colima-desktop/`
5. **Safe restarts** - Explicit user approval for resource changes

---

## License

MIT

---

## Related Projects

- [Colima](https://github.com/abiosoft/colima) - Container runtimes on macOS (and Linux) with minimal setup
- [Lima](https://github.com/lima-vm/lima) - Linux virtual machines on macOS
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) - Official Docker GUI (commercial)

---

**Maintained by:** InsightPulse AI
**Repository:** [Insightpulseai/odoo](https://github.com/Insightpulseai/odoo)
**Spec Kit:** `spec/colima-desktop/`
