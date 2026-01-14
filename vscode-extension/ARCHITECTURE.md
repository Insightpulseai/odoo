# Extension Architecture

## Design Philosophy

**Goal**: Turn "Odoo dev in a repo + docker" into a **deterministic, one-command, agent-friendly cockpit**.

**Principles**:
1. **Zero Configuration** - Auto-detect everything, no manual setup
2. **Agent-First** - Machine-readable state exports for AI/automation
3. **Hot-Reload Aware** - Know when to restart vs hot-reload
4. **One Command** - Golden paths for common operations
5. **Fail-Safe** - Warnings for destructive actions

## Core Components

### 1. Sandbox State Detection (`detectSandboxState()`)

**Auto-Detects**:
- Repo root via `vscode.workspace.workspaceFolders`
- Sandbox path (configurable, default: `sandbox/dev`)
- Git branch/commit via `git` commands
- Compose file presence (`docker-compose.yml` vs `docker-compose.production.yml`)
- Running containers via `docker compose ps --format json`
- DB target via `.env` file inspection
- Addons path via `odoo.conf` parsing

**Returns**: `SandboxState` object with complete runtime context

**Invoked**:
- On extension activation (if `autoDetect` enabled)
- After any sandbox command (up/down/restart)
- On demand via "Show Status" command

### 2. Canonical Status Banner (`printCanonicalBanner()`)

**Purpose**: Human-readable summary of sandbox state

**Format**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Odoo Live Sandbox - Canonical Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 Environment
🐳 Containers
💾 Database
📂 Addons Path
🏥 Health
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Quick Actions (Cmd+Shift+P)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Outputs**: VSCode Output Channel ("Odoo Live Sandbox")

### 3. Command Handlers

All commands follow this pattern:
1. Detect sandbox state
2. Validate prerequisites
3. Create terminal with correct `cwd`
4. Send command text
5. Show terminal
6. (Optional) Refresh status after delay

**Terminal vs Direct Exec**:
- **Terminal**: User needs to see output / interact (logs, shells, module install)
- **Direct Exec**: Silent background operations (state export)

### 4. Status Bar Integration

**Displays**: Health indicator with icon
- `$(check) Odoo: healthy` - All containers running
- `$(warning) Odoo: degraded` - Some containers down
- `$(x) Odoo: down` - No containers running
- `$(error) Odoo: Not detected` - Sandbox not found

**Clickable**: Opens canonical status banner

### 5. Machine-Readable State Export

**File**: `sandbox/dev/sandbox_state.json`

**Schema**:
```typescript
interface SandboxState {
  repoRoot: string;
  sandboxPath: string;
  composeFile: string;
  branch: string;
  commit: string;
  containers: {name: string; status: string; ports: string}[];
  dbTarget: string | null;
  addonsPath: string | null;
  health: 'healthy' | 'degraded' | 'down' | 'unknown';
  timestamp: string; // ISO 8601
}
```

**Use Cases**:
- Claude Code agents can read this to understand runtime state
- CI/CD can verify sandbox before running tests
- Documentation can auto-update with current config

## Command Implementation Details

### Hot-Reload Safe Commands

**Update Apps List**:
```bash
docker compose exec -T odoo odoo -d odoo --update-apps-list --stop-after-init
```
- `-T`: No TTY (allows piping)
- `--stop-after-init`: Runs operation and exits (no server restart)

**Install/Upgrade Module**:
```bash
docker compose exec -T odoo odoo -d odoo -i MODULE_NAME --stop-after-init
docker compose exec -T odoo odoo -d odoo -u MODULE_NAME --stop-after-init
```
- `-i`: Install (first time)
- `-u`: Upgrade (after code changes)
- Both are hot-reload safe if `dev_mode=reload` enabled

### Restart-Required Commands

**Rebuild Assets**:
```bash
docker compose restart odoo
```
- Required for JS/SCSS changes
- Extension warns user before executing

### Destructive Commands

**Sandbox Down with Volumes**:
```bash
docker compose down -v --remove-orphans
```
- Shows modal warning: "Stop & Remove Volumes (DANGER)"
- Requires explicit user confirmation
- Only safe for local dev, never production

## Configuration Schema

### Extension Settings

```json
{
  "odooLiveSandbox.sandboxPath": {
    "type": "string",
    "default": "sandbox/dev",
    "description": "Canonical sandbox directory relative to repo root"
  },
  "odooLiveSandbox.autoDetect": {
    "type": "boolean",
    "default": true,
    "description": "Auto-detect sandbox on workspace open"
  },
  "odooLiveSandbox.showBanner": {
    "type": "boolean",
    "default": true,
    "description": "Show canonical status banner on activation"
  }
}
```

## Extension Lifecycle

### Activation Flow

```
1. Extension activates (onStartupFinished)
   ↓
2. Create Output Channel + Status Bar Item
   ↓
3. Check config: autoDetect enabled?
   ↓ Yes
4. detectSandboxState()
   ↓
5. Update status bar
   ↓
6. Check config: showBanner enabled?
   ↓ Yes
7. printCanonicalBanner()
   ↓
8. Ready for user commands
```

### Command Execution Flow

```
User triggers command
   ↓
1. detectSandboxState()
   ↓
2. Validate (sandbox exists? containers running?)
   ↓
3. Create terminal with correct cwd
   ↓
4. Send command text
   ↓
5. Show terminal
   ↓
6. (Optional) Refresh status after delay
```

## File Structure

```
vscode-extension/
├── package.json          # Extension manifest
│   ├── activationEvents  # When to activate
│   ├── contributes
│   │   ├── commands      # Command palette entries
│   │   └── configuration # Settings schema
│   └── scripts           # Build/package scripts
│
├── tsconfig.json         # TypeScript config
│
├── src/
│   └── extension.ts      # Main extension code
│       ├── activate()            # Entry point
│       ├── deactivate()          # Cleanup
│       ├── detectSandboxState()  # Auto-detection
│       ├── printCanonicalBanner() # Status display
│       └── Command handlers:
│           ├── sandboxUp()
│           ├── sandboxDown()
│           ├── sandboxRestart()
│           ├── showLogs()
│           ├── dbShell()
│           ├── odooShell()
│           ├── updateAppsList()
│           ├── installModule()
│           ├── rebuildAssets()
│           ├── runHealthCheck()
│           └── exportState()
│
├── README.md             # User documentation
├── ARCHITECTURE.md       # This file
├── .gitignore
└── .vscodeignore
```

## Dependencies

**Runtime**:
- VSCode API: `vscode` module
- Node.js built-ins: `path`, `fs`, `child_process`

**Dev**:
- TypeScript compiler
- VSCode types
- ESLint
- VSCE (packaging tool)

**External Tools Required** (on system):
- `git` - Branch/commit detection
- `docker` + `docker compose` - Container management

## Testing Strategy

### Manual Testing Checklist

- [ ] Open `odoo-ce` repo → banner shows
- [ ] Status bar shows correct health
- [ ] "Sandbox: Up" starts containers
- [ ] "Sandbox: Down" stops containers (with warning)
- [ ] "Sandbox: Restart" restarts Odoo only
- [ ] "Tail Odoo Logs" opens terminal with logs
- [ ] "DB Shell" opens psql
- [ ] "Odoo Shell" opens Odoo Python shell
- [ ] "Update Apps List" runs without restart
- [ ] "Install Module" prompts for name + action
- [ ] "Rebuild Assets" warns about restart
- [ ] "Run Health Check" executes script
- [ ] "Export State" creates JSON file

### Automated Testing (Future)

**Unit Tests**:
- `detectSandboxState()` with mock filesystem
- Parse `docker compose ps` JSON output
- Parse `.env` and `odoo.conf` files

**Integration Tests**:
- Full activation flow in test workspace
- Command execution with mock terminals

## Extension Points for Future Phases

### Phase 2: File-Change Heuristics

**Watch for file changes**:
```typescript
vscode.workspace.onDidSaveTextDocument((doc) => {
  const ext = path.extname(doc.fileName);
  if (ext === '.py' || ext === '.xml') {
    vscode.window.showInformationMessage(
      'Hot-reload safe: Use "Install/Upgrade Module"'
    );
  } else if (ext === '.js' || ext === '.scss') {
    vscode.window.showWarningMessage(
      'Restart required: Use "Rebuild Assets"'
    );
  }
});
```

### Phase 3: CI Parity Locally

**Add commands**:
- `Odoo Live Sandbox: Run Repo Structure Gate`
- `Odoo Live Sandbox: Run Spec-Kit Gate`
- `Odoo Live Sandbox: Run Lint/Tests`

**Implementation**: Execute scripts from `scripts/ci_gate/` directory

### Phase 4: Secret Management

**Add commands**:
- `Odoo Live Sandbox: Set GitHub Secret`
- `Odoo Live Sandbox: Set DO App Var`
- `Odoo Live Sandbox: Edit Droplet .env`

**Implementation**: Use `gh` CLI, `doctl` CLI, and SSH for secret management

### Phase 5: Git Diff Explanation

**Add command**: `Odoo Live Sandbox: Generate PR Description`

**Implementation**:
1. Run `git diff main...HEAD`
2. Parse changed files (modules, seeds, infra)
3. Map to Odoo impact (needs -u, restart, asset rebuild)
4. Generate markdown PR description
5. Copy to clipboard or create PR directly

## Security Considerations

### Command Injection Prevention

**Safe**:
```typescript
terminal.sendText(`docker compose exec -T odoo odoo -d odoo -u ${moduleName} --stop-after-init`);
```

**Unsafe** (never do):
```typescript
exec(`docker compose exec -T odoo odoo -d odoo -u ${moduleName} --stop-after-init`);
```

**Why**: Terminal commands are sent as text, not executed directly by extension

### Credential Handling

**Never**:
- Store passwords in extension state
- Log sensitive environment variables
- Echo tokens in terminal output

**Always**:
- Read credentials from `.env` files
- Use environment variable placeholders
- Mask sensitive data in logs

## Performance Considerations

### Lazy Detection

**Don't**: Run `detectSandboxState()` on every command
**Do**: Cache state, refresh only after state-changing commands

### Async Everything

**Don't**: Use synchronous `execSync()` for long-running commands
**Do**: Use `execAsync()` with proper error handling

### Terminal Reuse

**Don't**: Create new terminal for every log tail
**Do**: Reuse existing terminal if already showing logs

## Accessibility

### Command Naming

**Consistent Prefix**: All commands start with "Odoo Live Sandbox:"

**Clear Actions**: Use verbs (Up, Down, Restart, Show, Run)

**Keyboard Friendly**: All commands accessible via Command Palette (Cmd+Shift+P)

### Status Indicators

**Icons**: Use semantic icons (`check`, `warning`, `error`)

**Color**: Don't rely on color alone (use icons + text)

**Clickable**: Status bar item clickable for more details

## Internationalization (Future)

**Hardcoded English**: All strings currently in English

**Future**: Extract strings to `package.nls.json` for localization

## Comparison with Existing Extension

**Published Extension** (`~/.vscode/extensions/insightpulseai.odoo-live-sandbox-0.1.0`):
- **Focus**: Live preview iframe (Figma-style)
- **Features**: Webview sidebar, auto-reload on file save

**This MVP Extension** (`vscode-extension/`):
- **Focus**: Agent dev cockpit (deterministic operations)
- **Features**: Auto-detection, one-click commands, state export

**Future**: Merge both - live preview + dev cockpit in one extension
