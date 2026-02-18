# CONSTITUTION — Colima Desktop

## Core Principles

### 1. No Colima Forking
**Integration via `colima` CLI only. Never patch/fork Colima core.**

- All Colima operations MUST use the official `colima` CLI binary
- No modification of Colima source code
- No forking of Colima repository
- Integration points: CLI commands, config files, socket paths only

**Rationale:** Maintain compatibility with upstream Colima releases, respect project boundaries, avoid maintenance burden of forks.

---

### 2. Security First

#### Electron Security Model
- **contextIsolation**: MUST be enabled (renderer cannot access Node.js APIs)
- **nodeIntegration**: MUST be disabled (renderer runs in isolated context)
- **sandbox**: MUST be enabled (renderer process sandboxed)
- **Preload script**: Only interface between main and renderer

#### IPC Security
- Use `ipcMain.handle` / `ipcRenderer.invoke` pattern (request-response)
- NEVER expose raw `ipcRenderer` to renderer process
- Validate ALL IPC payloads before execution
- Narrow API surface via `contextBridge` only

#### Renderer Process Constraints
- No privileged operations (spawn, fs, socket) in renderer
- All privileged operations delegated to main process
- Main process validates and executes on behalf of renderer

**Verification:**
```typescript
// ✅ ALLOWED - Preload script
contextBridge.exposeInMainWorld('colima', {
  status: () => ipcRenderer.invoke('colima:status')
});

// ❌ FORBIDDEN - Raw ipcRenderer exposure
contextBridge.exposeInMainWorld('ipc', ipcRenderer);
```

---

### 3. CLI-First Architecture

**Daemon + CLI must work without Electron UI.**

#### Dependency Graph
```
CLI ──→ Daemon (REST API) ──→ Colima CLI
         ↑
         │
    Electron UI (optional)
```

#### Requirements
- All operations scriptable via CLI
- Daemon provides REST API (localhost only)
- UI is optional enhancement, not requirement
- CLI communicates with daemon via HTTP (localhost:35100)
- Fallback: CLI can call Colima directly if daemon not running

**Verification:**
```bash
# MUST work without UI
colima-desktop daemon start
colima-desktop status
colima-desktop start --cpu 4
colima-desktop stop
```

---

### 4. Deterministic State Management

**All state under `~/.colima-desktop/` — no hidden files elsewhere.**

#### State Directory Structure
```
~/.colima-desktop/
├── config.yaml           # User configuration
├── daemon.pid            # Daemon process ID (lock file)
├── logs/
│   ├── daemon.log       # Daemon logs (JSON lines)
│   ├── colima.log       # Captured colima CLI output
│   └── lima.log         # Captured lima output
└── diagnostics/         # Generated bundles
    └── diag-YYYYMMDD-HHMM.tar.gz
```

#### Atomic Writes
- Write to `.tmp` file first
- Rename to final name (atomic operation)
- Prevents corruption if write interrupted

```typescript
// ✅ ALLOWED - Atomic write
await fs.writeFile(`${configPath}.tmp`, yaml);
await fs.rename(`${configPath}.tmp`, configPath);

// ❌ FORBIDDEN - Direct write (corruption risk)
await fs.writeFile(configPath, yaml);
```

#### Validation
- All config changes validated BEFORE applying
- Schema validation (Zod/JSON Schema)
- Range checks (CPU: 1-16, Memory: 1-32GB)
- Fail early on invalid config

---

### 5. Safe Restarts

**Resource changes require explicit user approval.**

#### Restart-Required Flag
- Config changes set `restart_required: true` flag
- No auto-restart on config change
- User confirms restart via CLI or UI

```typescript
// ✅ ALLOWED - Set flag, wait for user
PUT /v1/config { cpu: 6 }
→ { success: true, restart_required: true }

// User must explicitly restart:
POST /v1/lifecycle/restart

// ❌ FORBIDDEN - Auto-restart
PUT /v1/config { cpu: 6 }
→ Automatically restarts VM
```

#### User Flow
1. User changes config (CPU/RAM/Disk)
2. Daemon validates, saves, returns `restart_required: true`
3. UI shows warning: "Changes require VM restart. Continue?"
4. User clicks "Restart" → calls `/v1/lifecycle/restart`
5. Daemon applies changes and restarts VM

---

### 6. Evidence-Based Operations

**All operations verifiable via logs and status endpoints.**

#### Structured Logging
- JSON format (parseable)
- Timestamp, level, message, context
- Log rotation (max 1000 lines per file)
- Retention policy (7 days default)

```json
{
  "timestamp": "2026-02-15T14:30:15.123Z",
  "level": "info",
  "message": "Starting Colima VM",
  "context": { "cpu": 4, "memory": 8, "disk": 60 }
}
```

#### Diagnostics Bundle
- Captures full state at point in time
- Config, logs (last 1000 lines), versions, docker info
- Compressed tar.gz for sharing
- No sensitive data (redact secrets)

#### Status Endpoint
- Real-time state (running, stopped, error)
- Resource usage (CPU%, RAM usage)
- Uptime, versions (Colima, Lima)

---

### 7. macOS Only (v1)

**No Linux/Windows support initially.**

#### Platform Constraints
- Colima is macOS-specific (relies on Lima/QEMU)
- launchd for daemon management (macOS-native)
- macOS menubar for UI (NSStatusItem)
- System Preferences integration (Login Items)

#### Future Considerations
- v2: Linux support (if Colima adds Linux backend)
- v2: Windows support (via WSL2 or Windows Colima)

---

## Security Boundaries

### Electron Process Model

#### Main Process (Privileged)
**Owns:**
- All privileged operations (spawn, fs, socket)
- Daemon REST API client
- Colima CLI execution
- PID file management
- Log file access

**Forbidden:**
- Executing arbitrary user-provided commands
- Writing outside `~/.colima-desktop/`

#### Renderer Process (Unprivileged)
**Owns:**
- UI rendering (React)
- User input (forms, buttons)
- State management (Zustand)

**Forbidden:**
- Node.js API access (contextIsolation prevents)
- Filesystem access
- Child process spawning
- IPC beyond preload-exposed API

#### Preload Script (Security Boundary)
**Owns:**
- `contextBridge.exposeInMainWorld` API
- IPC request-response proxying
- Type-safe API surface

**Forbidden:**
- Raw `ipcRenderer` exposure
- Direct Node.js access in renderer
- Wildcard `send` passthrough

### IPC Security Model

#### Allowed Pattern (Request-Response)
```typescript
// Preload
contextBridge.exposeInMainWorld('colima', {
  status: () => ipcRenderer.invoke('colima:status')
});

// Main
ipcMain.handle('colima:status', async () => {
  // Validate request (none needed for status)
  const res = await fetch('http://localhost:35100/v1/status');
  return res.json();
});

// Renderer
const status = await window.colima.status();
```

#### Forbidden Pattern (Raw IPC)
```typescript
// ❌ NEVER DO THIS
contextBridge.exposeInMainWorld('ipc', ipcRenderer);

// Renderer can now call ANY ipc channel
window.ipc.send('execute-arbitrary-command', 'rm -rf /');
```

---

## Architecture Constraints

### Daemon

#### Single Process Enforcement
- PID file prevents concurrent daemons
- Startup checks for existing PID file
- Stale PID cleanup (check process exists)

```typescript
// Startup logic
if (await fs.exists(PID_FILE)) {
  const pid = await fs.readFile(PID_FILE, 'utf8');
  if (isProcessRunning(pid)) {
    throw new Error('Daemon already running');
  }
  await fs.unlink(PID_FILE); // Stale PID
}
await fs.writeFile(PID_FILE, process.pid.toString());
```

#### Graceful Shutdown
- SIGTERM/SIGINT handlers
- Clean up PID file
- Close HTTP server gracefully
- Flush logs before exit

#### REST API Constraints
- Bind to `localhost` ONLY (127.0.0.1)
- No remote access (security boundary)
- CORS: allow localhost origins only

---

### CLI

#### Daemon Communication
- Communicates with daemon via REST API (localhost:35100)
- Retries on connection refused (daemon may be starting)
- Timeout: 5 seconds for API calls

#### Fallback Behavior
- If daemon not running: show warning, offer to start daemon
- Optional: execute Colima CLI directly (bypass daemon)

```bash
# User runs:
colima-desktop status

# CLI checks daemon:
curl localhost:35100/v1/status
→ Connection refused

# CLI output:
Warning: Daemon not running. Start with: colima-desktop daemon start
Or use: colima status (direct)
```

---

### State Management

#### YAML Configuration
- Human-editable config file
- Schema validation on load
- Defaults for missing fields

#### Atomic Writes
```typescript
async function saveConfig(config: ColimaConfig) {
  const tmpPath = `${CONFIG_PATH}.tmp`;
  await fs.writeFile(tmpPath, yaml.stringify(config));
  await fs.rename(tmpPath, CONFIG_PATH); // Atomic
}
```

#### Validation Before Apply
```typescript
async function updateConfig(changes: Partial<ColimaConfig>) {
  const current = await loadConfig();
  const updated = { ...current, ...changes };

  // Validate BEFORE saving
  const result = ColimaConfigSchema.safeParse(updated);
  if (!result.success) {
    throw new ValidationError(result.error);
  }

  await saveConfig(updated);
  return { restart_required: requiresRestart(current, updated) };
}
```

---

## Forbidden Operations

### NEVER
1. **Fork/patch Colima** - Integration via CLI only
2. **Expose raw ipcRenderer** - Use contextBridge only
3. **Run privileged ops in renderer** - Main process only
4. **Auto-restart on config change** - User approval required
5. **Write state outside `~/.colima-desktop/`** - Deterministic state
6. **Bind daemon to 0.0.0.0** - localhost only (security)
7. **Execute arbitrary user commands** - Whitelist Colima operations only

### MUST
1. **Validate all config changes** - Schema + range checks
2. **Atomic writes** - Prevent corruption
3. **Graceful shutdown** - SIGTERM/SIGINT handlers
4. **Structured logging** - JSON format, retention policy
5. **Restart approval** - Explicit user action for restarts

---

## Compliance Verification

### Security Audit Checklist
- [ ] Electron `contextIsolation` enabled
- [ ] Electron `nodeIntegration` disabled
- [ ] Electron `sandbox` enabled
- [ ] Preload script uses `contextBridge` only
- [ ] IPC handlers validate all payloads
- [ ] No raw `ipcRenderer` exposure
- [ ] Daemon binds to localhost only
- [ ] No arbitrary command execution

### Architecture Checklist
- [ ] CLI works without daemon
- [ ] CLI works without UI
- [ ] Daemon enforces single instance (PID file)
- [ ] All state under `~/.colima-desktop/`
- [ ] Config changes require restart approval
- [ ] Atomic writes for all state files
- [ ] Graceful shutdown on SIGTERM

### Integration Checklist
- [ ] No Colima source code modifications
- [ ] All operations via `colima` CLI
- [ ] Config file edits follow Colima conventions
- [ ] Docker context management uses `docker context` CLI

---

**Constitution Status:** Canonical Reference
**Version:** 1.0
**Last Updated:** 2026-02-15
**Enforcement:** Non-negotiable — all implementations must comply
