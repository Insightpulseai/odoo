# Odoo Live Sandbox - Agent Dev Cockpit

**Turn "Odoo dev in a repo + docker" into a deterministic, one-command, agent-friendly cockpit.**

## Features (MVP)

### 1. Canonical Context Auto-Detect (Zero Mental Overhead)

On activation, the extension automatically detects:
- ✅ Repo root (`odoo-ce`)
- ✅ Canonical sandbox (`sandbox/dev`)
- ✅ Compose profile (local DB vs prod DB tunnel)
- ✅ Running services + ports
- ✅ Addons mount + active `addons_path`
- ✅ DB target + installed modules snapshot (optional)

**Value**: Every session starts "already oriented" - no drifting into wrong compose file / wrong DB / wrong branch.

### 2. One-Click "Golden Commands" (No Copy/Paste Archaeology)

Expose VSCode commands that run exact repo-approved flows:

- **Sandbox: Up** - Start sandbox containers
- **Sandbox: Down** - Stop containers (with optional volume removal)
- **Sandbox: Restart Odoo** - Restart Odoo container only
- **Sandbox: Logs** - Tail Odoo logs
- **DB: Shell** - Open PostgreSQL shell
- **Odoo: Shell** - Open Odoo Python shell
- **Odoo: Update Apps List** - Refresh module list
- **Odoo: Install/Upgrade Module** - Hot-reload safe module updates
- **Odoo: Rebuild Assets** - Force asset regeneration
- **Odoo: Run Health Check** - Execute health check script

**Value**: Removes 80% of dev friction + prevents wrong commands.

### 3. Hot-Reload Aware Module Lifecycle (No Unnecessary Restarts)

In dev, you shouldn't "stop Odoo" for most changes:

- **Python code changes**: Hot-reload works if `--dev=all` / `--dev=reload` enabled
- **XML/CSV data changes**: Needs `-u <module>` (upgrade) to apply
- **Security/ACL/RLS rules**: Usually `-u <module>` + refresh
- **JS/SCSS**: Asset rebuild (and sometimes hard reload)

**Planned**: File-change heuristics to suggest the right action.

### 4. Agent-Ready Outputs (Claude/Codex Can Act Without UI)

The extension emits **machine-readable session manifest** on activation:

- `sandbox_state.json` (ports, containers, DB name, addons paths)
- Current branch + commit
- Compose file in use
- Health status

**Value**: Any agent (Claude Code / Codex / CI runner) can pick up the same ground truth and run the right steps.

## Installation

### From Source (Development)

```bash
cd vscode-extension
npm install
npm run compile
code --install-extension $(npm run package --silent | tail -1)
```

### From Marketplace (Coming Soon)

Search for "Odoo Live Sandbox" by insightpulseai

## Usage

### Auto-Detection on Startup

When you open the `odoo-ce` repo, the extension automatically:
1. Detects sandbox environment
2. Shows canonical status banner in Output panel
3. Updates status bar with health indicator

### Command Palette

Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux) and type:

- `Odoo Live Sandbox: Show Status` - Display canonical status banner
- `Odoo Live Sandbox: Up` - Start sandbox containers
- `Odoo Live Sandbox: Restart Odoo` - Restart only Odoo container
- `Odoo Live Sandbox: Install/Upgrade Module` - Interactive module installer

### Status Bar

Click the status bar item (e.g., `✓ Odoo: healthy`) to show full status.

### Typical Workflow

```
1. Open odoo-ce repo in VSCode
2. Extension auto-detects sandbox → shows banner
3. Click "Odoo Live Sandbox: Up" if containers down
4. Edit Python/XML files → auto hot-reload
5. Edit JS/SCSS → click "Rebuild Assets"
6. Install module → "Install/Upgrade Module" command
7. Check health → "Run Health Check" command
```

## Configuration

### Settings

```json
{
  "odooLiveSandbox.sandboxPath": "sandbox/dev",
  "odooLiveSandbox.autoDetect": true,
  "odooLiveSandbox.showBanner": true
}
```

## Canonical Status Banner Example

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Odoo Live Sandbox - Canonical Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 Environment
   Repo:    /Users/tbwa/odoo-ce
   Sandbox: /Users/tbwa/odoo-ce/sandbox/dev
   Compose: docker-compose.yml
   Branch:  feat/production-docs (206a8cd2)

🐳 Containers (2 detected)
   ✅ odoo-ce              running         8069→8069
   ✅ odoo-ce-db-1         running         5432→5432

💾 Database
   Target: local

📂 Addons Path
   /mnt/extra-addons
   /usr/lib/python3/dist-packages/odoo/addons

🏥 Health: HEALTHY

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Quick Actions (Cmd+Shift+P):
   • Odoo Live Sandbox: Up/Down/Restart
   • Odoo Live Sandbox: Tail Odoo Logs
   • Odoo Live Sandbox: Install/Upgrade Module
   • Odoo Live Sandbox: Run Health Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Machine-Readable State Export

```json
{
  "repoRoot": "/Users/tbwa/odoo-ce",
  "sandboxPath": "/Users/tbwa/odoo-ce/sandbox/dev",
  "composeFile": "docker-compose.yml",
  "branch": "feat/production-docs",
  "commit": "206a8cd2",
  "containers": [
    {
      "name": "odoo-ce",
      "status": "running",
      "ports": "8069→8069"
    },
    {
      "name": "odoo-ce-db-1",
      "status": "running",
      "ports": "5432→5432"
    }
  ],
  "dbTarget": "local",
  "addonsPath": "/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons",
  "health": "healthy",
  "timestamp": "2026-01-14T10:30:00.000Z"
}
```

## Roadmap

### Phase 2: Smart Action Suggestions
- File-change heuristics → suggest right action
- If edited file is `models/*.py` → "Reload server (if needed)"
- If edited file is `views/*.xml` → suggest `-u module`
- If edited file is `static/src/**` → suggest asset rebuild

### Phase 3: CI Parity Locally
- "Run repo-structure gate"
- "Run spec-kit gate"
- "Run lint/tests"
- "Run drift checks (DBML/seeds)"

### Phase 4: Production-Safe Secret Handling
- Commands to set secrets via target surface
- GitHub Actions secrets integration
- DigitalOcean App/Registry vars
- Droplet `.env` file management

### Phase 5: Git Diff Explanation
- Summarize what changed (modules, seeds, infra)
- Map changes to Odoo impact ("needs -u", "restart", "asset rebuild")
- Generate PR description + verification checklist

## License

MIT

## Author

insightpulseai

## Repository

https://github.com/insightpulseai/odoo-live-sandbox
