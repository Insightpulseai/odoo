# Claude Code Web — Cloud Sandbox Execution Contract

> **Source**: [Anthropic Official Docs](https://code.claude.com/docs/en/claude-code-on-the-web) + [Remote Control](https://code.claude.com/docs/en/remote-control)
>
> **Pattern**: Claude Code on the Web runs on **Anthropic-managed VMs**. Remote Control runs on **your local machine** and is controlled from any browser/phone.

---

## Two Modes of Operation

| Mode | Runs On | Use Case |
|------|---------|----------|
| **Claude Code on the Web** | Anthropic cloud VMs | Async tasks, parallel work, repos not cloned locally |
| **Remote Control** | Your local machine | Continue local work from phone/browser, full MCP access |

Both accessed at [claude.ai/code](https://claude.ai/code) and the Claude mobile app (iOS/Android).

---

## Who Can Use It

| Plan | Access |
|------|--------|
| **Pro** | Yes |
| **Max** | Yes |
| **Team** | Yes (admin must enable in [admin settings](https://claude.ai/admin-settings/claude-code)) |
| **Enterprise** | Yes (premium seats or Chat + Claude Code seats) |

---

## Claude Code on the Web

### Getting Started

1. Visit [claude.ai/code](https://claude.ai/code)
2. Connect your GitHub account
3. Install the Claude GitHub App on your repositories
4. Select your default environment
5. Submit your coding task
6. Review changes in diff view, iterate with comments, then create a PR

### How It Works

1. **Repository cloning**: Your repo is cloned to an Anthropic-managed VM
2. **Environment setup**: Setup script runs (if configured)
3. **Network configuration**: Internet access configured per your settings
4. **Task execution**: Claude analyzes code, makes changes, runs tests
5. **Completion**: Changes pushed to a branch, ready for PR creation

### Cloud Environment — Pre-installed Tools

The universal image (Ubuntu 24.04) includes:

| Category | Available |
|----------|-----------|
| **Python** | Python 3.x with pip, poetry, common scientific libraries |
| **Node.js** | Latest LTS with npm, yarn, pnpm, bun |
| **Ruby** | 3.1.6, 3.2.6, 3.3.6 (default: 3.3.6) with gem, bundler, rbenv |
| **PHP** | 8.4.14 |
| **Java** | OpenJDK with Maven and Gradle |
| **Go** | Latest stable with module support |
| **Rust** | Rust toolchain with cargo |
| **C++** | GCC and Clang compilers |
| **PostgreSQL** | Version 16 |
| **Redis** | Version 7.0 |

Run `check-tools` in a cloud session to see full list.

### Setup Scripts

Setup scripts run when a new cloud session starts, **before** Claude Code launches. They run as root on Ubuntu 24.04.

Configure in the environment settings dialog:

```bash
#!/bin/bash
# Install gh CLI (not in default image)
apt update && apt install -y gh

# Install project dependencies
pip install -r requirements.txt || true
npm install || true
```

**Key rules:**
- Runs only on **new** sessions (skipped on resume)
- If script exits non-zero, session fails to start — use `|| true` for non-critical commands
- Needs network access to install packages

### Setup Scripts vs SessionStart Hooks

| | Setup Scripts | SessionStart Hooks |
|---|---|---|
| **Attached to** | Cloud environment (UI) | Repository (`.claude/settings.json`) |
| **Runs** | Before Claude Code, new sessions only | After Claude Code, every session including resumed |
| **Scope** | Cloud environments only | Both local and cloud |
| **Use for** | Tools the cloud needs but your laptop has | Project setup that should run everywhere |

### SessionStart Hook Example

In `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/scripts/install_pkgs.sh"
          }
        ]
      }
    ]
  }
}
```

Script at `scripts/install_pkgs.sh`:

```bash
#!/bin/bash

# Only run in remote/cloud environments
if [ "$CLAUDE_CODE_REMOTE" != "true" ]; then
  exit 0
fi

npm install
pip install -r requirements.txt
exit 0
```

Make executable: `chmod +x scripts/install_pkgs.sh`

**Persist env vars** by writing to `$CLAUDE_ENV_FILE` from within the hook.

### Network Access

#### Access Levels

| Level | Behavior |
|-------|----------|
| **Limited** (default) | Allowlisted domains only (package registries, GitHub, cloud platforms) |
| **Full** | Unrestricted internet access |
| **None** | No internet (Anthropic API still reachable) |

#### GitHub Proxy

All GitHub operations go through a dedicated proxy:
- Manages authentication securely (scoped credentials inside sandbox)
- Restricts `git push` to the current working branch only
- Enables cloning, fetching, and PR operations

#### Default Allowed Domains (Limited mode)

Includes: GitHub, npm, PyPI, RubyGems, crates.io, Maven, Docker registries, Ubuntu archives, Google Cloud, Azure, AWS, and more. See [full list](https://code.claude.com/docs/en/claude-code-on-the-web#default-allowed-domains).

### Environment Variables

Set in the environment settings UI as key-value pairs (`.env` format):

```
API_KEY=your_api_key
DEBUG=true
```

### Terminal ↔ Web Handoff

#### From Terminal to Web (`--remote`)

```bash
# Start a cloud task from terminal
claude --remote "Fix the authentication bug in src/auth/login.ts"

# Plan locally, execute remotely
claude --permission-mode plan    # collaborate on approach
claude --remote "Execute the migration plan in docs/migration-plan.md"

# Parallel tasks
claude --remote "Fix the flaky test in auth.spec.ts"
claude --remote "Update the API documentation"
claude --remote "Refactor the logger to use structured output"
```

Monitor with `/tasks`.

#### From Web to Terminal (`--teleport`)

| Method | Command |
|--------|---------|
| Inside Claude Code | `/teleport` or `/tp` |
| From command line | `claude --teleport` (interactive) or `claude --teleport <session-id>` |
| From `/tasks` | Press `t` to teleport |
| From web UI | Click "Open in CLI" |

**Requirements**: Clean git state, correct repository, branch pushed to remote, same Claude account.

#### Select Remote Environment

```bash
# Choose which environment to use for --remote
/remote-env
```

### Diff View

When Claude makes changes, a diff stats indicator appears (`+12 -1`). Select it to:
- Review changes file by file
- Comment on specific changes
- Iterate with Claude before creating a PR

### Security & Isolation

- **Isolated VMs**: Each session runs in an isolated, Anthropic-managed VM
- **No inbound ports**: Sandbox never opens inbound connections
- **Credential protection**: Git credentials and signing keys are never inside the sandbox
- **Scoped credentials**: Authentication handled through secure proxy

### Session Management

- **Archive**: Hover over session in sidebar → click archive icon
- **Delete**: Filter archived sessions → click delete (permanent, cannot undo)
- **Share (Team/Enterprise)**: Toggle Private ↔ Team visibility
- **Share (Pro/Max)**: Toggle Private ↔ Public visibility

### Limitations

- GitHub repositories only (no GitLab/Bitbucket)
- Session handoff is one-way: web → terminal only (not terminal → web for existing sessions)
- `--remote` creates a **new** session (cannot push existing terminal session)
- Rate limits shared with all Claude/Claude Code usage

---

## Remote Control

### What It Does

Connects [claude.ai/code](https://claude.ai/code) or the Claude mobile app to a Claude Code session **running on your machine**. Nothing moves to the cloud.

### Start a Remote Control Session

```bash
# New session
claude remote-control
claude remote-control --name "Odoo Dev"

# From inside an existing Claude Code session
/remote-control
/rc
/remote-control My Project
```

### Flags

| Flag | Purpose |
|------|---------|
| `--name "Title"` | Custom session name visible in session list |
| `--verbose` | Detailed connection and session logs |
| `--sandbox` / `--no-sandbox` | Enable/disable filesystem & network isolation |

### Connect from Another Device

- **Open session URL** displayed in terminal
- **Scan QR code** (press spacebar to toggle) → opens in Claude mobile app
- **Browse to** [claude.ai/code](https://claude.ai/code) → find session by name (green dot = online)

### Enable for All Sessions

Inside Claude Code: `/config` → **Enable Remote Control for all sessions** → `true`

### Key Properties

| Property | Detail |
|----------|--------|
| **Runs on** | Your local machine |
| **MCP servers** | Fully available |
| **Local files** | Full access |
| **Connection** | Outbound HTTPS only, no inbound ports |
| **Auto-reconnect** | Survives sleep/network drops (up to ~10 min) |
| **Concurrent sessions** | One remote session per Claude Code instance |
| **Terminal** | Must stay open |

---

## Odoo Project: Environment Configuration

### Recommended Setup Script (Cloud Environment UI)

```bash
#!/bin/bash
# Pre-install tools for Odoo CE development
apt update && apt install -y gh postgresql-client libpq-dev || true

# Python dependencies
pip install -r requirements.txt || true

# Node.js dependencies
npm install || true
```

### Required Environment Variables (Cloud Environment UI)

```
DB_HOST=db
DB_PORT=5432
DB_USER=odoo
DB_PASSWORD=<set-in-session>
DB_NAME=odoo_core
ADMIN_PASSWD=<set-in-session>
ODOO_PORT=8069
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
NEXT_PUBLIC_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_ANON_KEY=<set-in-session>
SUPABASE_SERVICE_ROLE_KEY=<set-in-session>
```

### Verification Protocol

After every mutation, run:

```bash
./scripts/repo_health.sh && \
./scripts/spec_validate.sh && \
./scripts/ci_local.sh
```

### Quick Reference

| Check | Command |
|-------|---------|
| Pre-installed tools | `check-tools` |
| Repo structure | `./scripts/repo_health.sh` |
| Spec bundles | `./scripts/spec_validate.sh` |
| Full CI suite | `./scripts/ci_local.sh` |
| Stack health | `./scripts/web_sandbox_verify.sh` |

---

## Capability Parity: Web = Local CLI

Claude Code on the Web runs the **same agent** as the local CLI. It has full terminal access, can run arbitrary commands, install packages, execute tests, and interact with all CLI tools available in the cloud VM.

| Capability | Local CLI | Claude Code on the Web | Remote Control |
|------------|-----------|----------------------|----------------|
| **Full terminal access** | Yes | Yes | Yes (your machine) |
| **Run tests** | Yes | Yes | Yes |
| **Install packages** | Yes | Yes (via setup scripts + apt/pip/npm) | Yes |
| **Git operations** | Yes | Yes (via GitHub proxy) | Yes |
| **File read/write/edit** | Yes | Yes | Yes |
| **Run build tools** | Yes | Yes | Yes |
| **Execute scripts** | Yes | Yes | Yes |
| **MCP servers** | Yes | No (cloud VM) | Yes (your machine) |
| **Docker control** | Yes | No (no Docker-in-Docker) | Yes (your machine) |
| **Local filesystem** | Yes | Cloned repo only | Yes |
| **Parallel sessions** | One per terminal | Multiple simultaneous | One per instance |

### Execution Surfaces

| Environment | Execution Surface | Best For |
|-------------|-------------------|----------|
| **Claude Code on the Web** | Anthropic cloud VM (full CLI) | Async tasks, parallel work, repos not cloned locally |
| **Remote Control** | Your local machine (full CLI) | Continue local work from phone/browser |
| **VS Code Desktop + CLI** | Local machine | Docker orchestration, MCP servers |
| **GitHub Codespaces + CLI** | Remote container | Full power, cloud hosted |

### Recommended for Odoo Stack

1. **Async/Parallel**: Claude Code on the Web via `--remote` (full CLI power, multiple tasks)
2. **Local + Docker/MCP**: VS Code Desktop + DevContainer + Claude Code CLI
3. **Mobile/Remote**: Remote Control (continue local sessions from phone)
4. **Cloud variant**: GitHub Codespaces (mirrors local DevContainer)

---

*Source: [Claude Code on the Web](https://code.claude.com/docs/en/claude-code-on-the-web) | [Remote Control](https://code.claude.com/docs/en/remote-control)*
*Last updated: 2026-03-07*
