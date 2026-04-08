# AI Operating Model: Claude Code + VS Code Web + Foundry

> Canonical operating model for AI-assisted development across InsightPulse AI.
> Defines environment split, Foundry integration, repo file contracts, and execution flows.
>
> Last updated: 2026-03-14

---

## Environment Split

### VS Code Web (vscode.dev)

**Role**: Lightweight review, quick edits, repo browsing.

- Access via `vscode.dev/github/Insightpulseai/<repo>`
- No terminal, no build, no debug
- Suitable for: code review, small text edits, markdown updates, file navigation
- No extension execution beyond web-compatible extensions

### Claude Code Web

**Role**: Autonomous cloud execution against GitHub repos.

- Clones the target repo, runs setup scripts, executes tasks, pushes branches
- Full terminal access with sandboxed compute
- Suitable for: implementation tasks, refactoring, test execution, CI-equivalent validation
- Creates branches and commits; human reviews via GitHub PR

### VS Code Desktop + Devcontainer

**Role**: Local high-fidelity implementation, debug, and test.

- Full devcontainer support (`.devcontainer/devcontainer.json`)
- Local PostgreSQL, Odoo runtime, OCA modules
- Suitable for: complex debugging, performance profiling, integration testing
- Claude CLI available in integrated terminal

### Claude CLI in Terminal

**Role**: Deterministic execution and handoff.

- `claude` command in local terminal or devcontainer
- `claude --remote` for cloud-backed execution
- `claude --teleport` to resume a cloud session locally
- `claude --resume` to continue a previous session
- Suitable for: scripted workflows, CI integration, deterministic task execution

### Azure AI Foundry

**Role**: Model and provider control plane.

- Resource: `data-intel-ph-resource` (in `rg-data-intel-ph`)
- Project: `proj-ipai-claude` (in `rg-ipai-ai-dev`)
- Provides: model hosting, API key management, usage tracking, content filtering
- Not a development environment -- strictly a model/provider control plane

### GitHub

**Role**: Canonical source control and PR workflow.

- All repos under `Insightpulseai` org
- Branch protection on `main` with required reviews
- Status checks gate merges
- GitHub Actions as primary CI/CD automation surface

### GitHub Actions

**Role**: Primary AI automation surface.

- `anthropics/claude-code-action@v1` for PR review automation
- Standard test/lint/build workflows
- Triggered by push, PR, schedule, or workflow_dispatch

### Azure DevOps

**Role**: Optional auxiliary execution surface.

- Used selectively for Azure-native deployments
- ARM service connections with workload identity federation
- Key Vault-backed variable groups
- Not competing with GitHub Actions -- additive only

---

## Foundry Environment Contract

```bash
# Required environment variables
CLAUDE_CODE_USE_FOUNDRY=1
ANTHROPIC_FOUNDRY_RESOURCE=data-intel-ph-resource

# Alternative: explicit base URL
# ANTHROPIC_FOUNDRY_BASE_URL=https://data-intel-ph-resource.services.ai.azure.com/anthropic
```

### Auth Options

1. **API key**: Set `ANTHROPIC_FOUNDRY_API_KEY` (stored in `kv-ipai-dev` as `azure-ai-foundry-api-key`)
2. **Azure credential chain**: `az login`, `DefaultAzureCredential`, or managed identity -- no API key needed

### Required RBAC

| Role | Scope | Purpose |
|------|-------|---------|
| Azure AI User | Foundry resource (`data-intel-ph-resource`) | Model invocation |
| Cognitive Services User | Foundry resource (`data-intel-ph-resource`) | API access |

---

## Repo File Structure Contract

Every repo participating in the AI operating model must maintain these files:

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Repo-level instructions for Claude Code (behavioral rules, stack context, conventions) |
| `.claude/settings.json` | Team-shared Claude configuration (allowed/denied commands, MCP servers) |
| `.claude/settings.local.example.json` | Template for local overrides (not committed with real values) |
| `.mcp.json` | Project-scoped MCP server configuration |
| `.devcontainer/devcontainer.json` | Container execution environment definition |
| `.github/workflows/claude-review.yml` | PR review automation using `anthropics/claude-code-action@v1` |
| `scripts/install_pkgs.sh` | Setup script for cloud sessions (runs on session start) |
| `scripts/verify.sh` | Verification runner (deterministic checks) |

---

## Settings Policy

### Allowed Commands

Commands that Claude Code is permitted to execute without confirmation:

- `pytest`, `python -m pytest`
- `npm test`, `npm run lint`, `npm run build`
- `git status`, `git diff`, `git add`, `git commit`, `git log`
- `./scripts/verify.sh`, `./scripts/repo_health.sh`

### Denied Paths

Paths that Claude Code must never read:

- `./.env`
- `./.env.*`
- `./secrets/**`

### Session Start Hook

On session initialization, Claude Code runs `scripts/install_pkgs.sh` to install required dependencies for the execution environment. This ensures cloud sessions have the same toolchain as local devcontainers.

---

## MCP Policy

MCP server connections are defined in `.mcp.json` at the project root. Policy rules:

- Allow/deny is configured per server name and URL pattern
- Project-scoped servers go in `.mcp.json` (committed, shared)
- Personal servers go in `~/.claude.json` (not committed)
- HTTP remote transport is preferred over SSE
- No MCP servers should expose secrets in their configuration

---

## Execution Flow

### 1. Lightweight Browse

```
vscode.dev/github/Insightpulseai/<repo>
```

Use for: reading code, reviewing PRs, small markdown edits. No terminal required.

### 2. Autonomous Remote Execution

```
Claude Code Web  -or-  claude --remote
```

Use for: implementation tasks that need full compute (build, test, lint). Claude clones the repo, runs `scripts/install_pkgs.sh`, executes the task, pushes a branch.

### 3. Resume Locally

```
claude --teleport  -or-  claude --resume
```

Use for: picking up a cloud session in a local terminal. Preserves context and conversation state.

### 4. Local Implementation

```
VS Code Desktop + devcontainer + Claude CLI
```

Use for: complex debugging, integration testing, performance work. Full local runtime with PostgreSQL, Odoo, and OCA modules.

---

## Best Practices

1. **Explore before acting**: Read the codebase before making changes. Never guess at structure or conventions.
2. **Plan before implementing**: Create an explicit plan. Validate assumptions against existing code.
3. **Implement with minimal diffs**: Prefer editing existing files over creating new ones. Small, focused changes.
4. **Verify deterministically**: Run `scripts/verify.sh` or equivalent. Never claim success without evidence.
5. **Commit with convention**: Follow `feat|fix|refactor|docs|test|chore(scope): description` format.
6. **Keep GitHub canonical**: All source changes flow through GitHub PRs. Azure DevOps pipelines consume, not originate.

---

## Anti-Patterns

- Running Odoo on the host machine instead of inside a devcontainer
- Storing secrets in `.claude/settings.json` or `.mcp.json`
- Using Azure DevOps repos as primary source control (GitHub is canonical)
- Skipping verification and claiming success based on build-started messages
- Broad refactors when a minimal diff achieves the same goal
- Creating new files when editing existing files would suffice
