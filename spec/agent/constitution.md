# Agent Constitution: Execution Constraints for Claude Code

**Version**: 2.0
**Effective**: 2026-02-22
**Authority**: This document defines execution constraints for Claude Code agents. Updated to reflect actual Claude Code Web environment capabilities.

---

## 1. Core Principle

**Claude Code Web sessions run in a full Linux container with local CLI capabilities.** Agents MUST attempt commands directly before refusing. Never preemptively refuse an operation — try it first, report the real error if it fails.

---

## 2. Available Capabilities (USE DIRECTLY)

These work in Claude Code Web containers. Execute them — do not redirect to CI.

### 2.1 Shell & CLI
```
✅ bash, sh, zsh
✅ git (all operations)
✅ curl, wget
✅ node, npm, npx, pnpm
✅ python3, pip, pip3
✅ make, gcc, g++ (build tools)
✅ jq, yq, sed, awk, grep, find
✅ ssh-keygen, openssl (crypto tools)
```

### 2.2 Package Management
```
✅ apt-get install (packages available in Ubuntu container)
✅ npm install / npm install -g
✅ pip install / pip install --user
✅ npx <package> (one-shot execution)
```

### 2.3 Build & Test
```
✅ npm run build / npm test
✅ python -m pytest
✅ make / make test
✅ eslint, prettier, black, ruff (linters)
```

### 2.4 Repository & File Operations
```
✅ Edit, Write, Read files (native tools)
✅ Glob, Grep (search tools)
✅ git add, commit, push, branch, merge, rebase
✅ GitHub API via curl (through egress proxy)
```

### 2.5 Network
```
✅ curl / wget to external APIs
✅ GitHub API (api.github.com via egress proxy)
✅ npm registry, PyPI, apt repositories
```

---

## 3. Genuinely Unavailable (Container Limitations)

These fail due to real container architecture constraints — not policy:

### 3.1 Docker-in-Docker
```
❌ docker build / docker run / docker-compose
```
**Why**: No Docker daemon socket mounted in the container.
**Alternative**: Generate CI workflows (`.github/workflows/*.yml`).

### 3.2 System Services
```
❌ systemctl / service (no systemd)
```
**Alternative**: Run processes in foreground or generate CI/deployment workflows.

### 3.3 GUI / Browser
```
❌ xdg-open / open (no display server)
```
**Alternative**: Headless CLI tools, output URLs for user to open.

### 3.4 Direct Push to `main`
```
❌ git push origin main (blocked by proxy — claude/ branches only)
```
**Alternative**: Push to `claude/` branch, create PR via GitHub API, merge via API or user action.

---

## 4. Response Pattern

### When command might work: TRY IT FIRST
```
User: "Install jq"
Agent: <runs apt-get install -y jq>
       Done. jq installed.
```

### When command genuinely fails: EXPLAIN REAL ERROR
```
User: "Run docker-compose up"
Agent: <attempts command>
       docker-compose failed — no Docker daemon in this container.
       I'll create a CI workflow instead.
```

### NEVER do this:
```
❌ "I cannot run that in this web environment"  (without trying)
❌ "Let me generate a CI workflow instead"       (when direct execution works)
❌ "Would you like me to..."                     (just do it)
```

---

## 5. Capability Manifest

Verified capabilities live in `agents/capabilities/manifest.json`. This is a reference for what the project has validated, not a restriction on what agents can execute.

**Important**: The manifest tracks *project-specific* capabilities (Odoo module scaffolding, Supabase integration, etc.), NOT general CLI capabilities. General CLI capabilities are available by default.

---

## 6. CI-First (Only When Necessary)

Generate CI workflows ONLY for operations that genuinely cannot run locally:
- Docker builds and container orchestration
- Deployment to remote servers (SSH, DigitalOcean, etc.)
- Operations requiring secrets not available locally
- Long-running processes that exceed session timeouts

For everything else: **execute directly**.

---

## 7. Amendment History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-02-12 | Initial — overly restrictive, assumed no CLI access |
| 2.0 | 2026-02-22 | Rewritten — reflects actual container capabilities, execute-first policy |

---

**This constitution is binding for all Claude Code agents operating in this repository.**

*Last Updated: 2026-02-22*
*Version: 2.0*
