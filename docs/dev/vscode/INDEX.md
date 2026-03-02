# VS Code Docs Index — Insightpulseai/odoo

> Curated reference: VS Code documentation pages mapped to concrete repo actions.
> Generated: 2026-03-02 | Source: `ssot/devex/vscode.yaml`
> Update: edit `ssot/devex/vscode.yaml`, then re-curate this table.

---

## Index

| Area | Doc page | URL | Why it matters | Repo action | Key setting / flag |
|------|----------|-----|----------------|-------------|-------------------|
| **Setup** | Additional components and tools | <https://code.visualstudio.com/docs/setup/additional-components> | Lists tools required beyond VS Code — Git (OCA submodules + all CI), Node.js (pnpm/Turborepo monorepo), TypeScript compiler (apps/ layer). First check in new-developer on-boarding. | Extend `scripts/devcontainer/preflight.sh` to assert `git --version`, `node --version`, `tsc --version` all exit 0 before container declared healthy. Add `scripts/dev/vscode_doctor.sh` for local pre-flight. | `postCreateCommand` |
| **Dev Containers** | Developing inside a Container | <https://code.visualstudio.com/docs/devcontainers/containers> | Canonical reference for `.devcontainer/devcontainer.json` — `dockerComposeFile`, `workspaceFolder`, `postCreateCommand`, `forwardPorts`. Getting these right keeps the Odoo + PostgreSQL + n8n stack reproducible across machines. | Audit `.devcontainer/devcontainer.json`: confirm `workspaceFolder=/workspaces/odoo`, `dockerComposeFile` points to `.devcontainer/docker-compose.devcontainer.yml`, `postCreateCommand` runs `preflight.sh`. | `workspaceFolder` |
| **Copilot** | How AI works in VS Code | <https://code.visualstudio.com/docs/copilot/core-concepts> | Explains Copilot context limits and the Ask (read-only) vs. Agent (code-modifying) mode distinction — critical in a repo with 550+ scripts, 43 custom modules, and 153 workflows. Prevents accidental in-session rewrites. | Document in `.github/copilot-instructions.md` which Copilot mode is appropriate per repo area: Ask for spec research, Agent only for `addons/ipai/` implementation tasks. | `github.copilot.chat.agent.runTasks` |
| **Copilot** | GitHub Copilot tips and tricks | <https://code.visualstudio.com/docs/copilot/copilot-tips-and-tricks> | Covers `#codebase`, `#file`, `#symbol` context variables for cross-repo reasoning without hitting context limits — essential when debugging cross-module Odoo inheritance chains or tracing n8n workflow JSON to a Supabase Edge Function. | Add `"github.copilot.chat.codeSearch.enabled": true` to `.vscode/settings.json` so `#codebase` queries auto-index `addons/ipai/`. | `github.copilot.chat.codeSearch.enabled` |
| **Copilot** | AI smart actions in VS Code | <https://code.visualstudio.com/docs/copilot/copilot-smart-actions> | Smart actions (Fix, Explain, Generate Tests, Generate Docs, Commit Message) are context-menu accessible without a prompt — useful for OCA `_inherit` overrides where Copilot can explain inherited base-Odoo methods and generate tests. | Ensure Python + Pylance extensions are in `.devcontainer/devcontainer.json` `extensions` array for full type-resolution context on Odoo Python modules. | `editor.codeActionsOnSave` |
| **Copilot** | Prompt engineering in VS Code | <https://code.visualstudio.com/docs/copilot/guides/prompt-engineering-guide> | Documents `.github/copilot-instructions.md` workspace file that auto-injects project context into every Copilot request — correct place for IPAI naming conventions, OCA-first philosophy, secrets policy, CE-only constraint. | Keep `.github/copilot-instructions.md` up-to-date with module naming convention (`ipai_<domain>_<feature>`), addons load order, banned patterns (no EE modules, no hardcoded secrets), commit format. | `.github/copilot-instructions.md` |
| **Copilot** | Use tools with agents | <https://code.visualstudio.com/docs/copilot/agents/agent-tools> | Explains Agent mode tool invocation (file read/write, terminal, MCP tools) — directly relevant since this repo runs 11 MCP servers. Understanding tool approval flow prevents unintended Supabase schema mutations or n8n workflow deploys triggered from chat. | Review `.vscode/mcp.json` to confirm each MCP server uses `inputs`-based secret refs (not hardcoded values) and that destructive servers (Supabase schema, DNS) require manual tool approval. | `github.copilot.chat.agent.runTasks` |
| **MCP** | Add and manage MCP servers in VS Code | <https://code.visualstudio.com/docs/copilot/customization/mcp-servers> | Defines `.vscode/mcp.json` schema (workspace-scoped) and user-profile `mcp.json` (global) for registering MCP servers — the mechanism by which this repo's 11 MCP servers become Copilot Agent tools. The `inputs` array is the correct way to inject secrets like `CF_API_TOKEN`. | Create/maintain `.vscode/mcp.json` (tracked, no secrets) with `servers` entries for each server in `mcp/servers/`, using `inputs` for every credential, aligned to `ssot/secrets/registry.yaml` identifiers. | `mcp.servers` |
| **Terminal** | Terminal Basics | <https://code.visualstudio.com/docs/terminal/basics> | Shell integration (command decorations, output capture, exit-code tracking) is what Copilot uses to read terminal output as context — critical for `./scripts/repo_health.sh` or `odoo-bin` failures. Getting the default shell profile right ensures Zsh aliases (Colima context switching, `DOCKER_HOST` mgmt) load inside the Dev Container. | Add `"terminal.integrated.shellIntegration.enabled": true` and `"terminal.integrated.defaultProfile.linux": "zsh"` to `.devcontainer/devcontainer.json` `customizations.vscode.settings`. | `terminal.integrated.shellIntegration.enabled` |
| **Python** | Getting Started with Python in VS Code | <https://code.visualstudio.com/docs/python/python-tutorial> | Covers interpreter selection (`python.defaultInterpreterPath`), venv auto-activation, and Pylance — needed for correct import resolution for Odoo 19 CE source tree and `addons/ipai/` modules inside the Dev Container where the venv lives at `/workspaces/odoo/.venv`. | Set in `.devcontainer/devcontainer.json` `customizations.vscode.settings`: `"python.defaultInterpreterPath": "/workspaces/odoo/.venv/bin/python"` and `"python.terminal.activateEnvironment": true`. | `python.defaultInterpreterPath` |

---

## Quick reference: highest-leverage settings per file

### `.devcontainer/devcontainer.json` → `customizations.vscode.settings`

```json
{
  "python.defaultInterpreterPath": "/workspaces/odoo/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "terminal.integrated.shellIntegration.enabled": true,
  "terminal.integrated.defaultProfile.linux": "zsh",
  "github.copilot.chat.codeSearch.enabled": true
}
```

### `.vscode/settings.json` (workspace, tracked)

```json
{
  "github.copilot.chat.codeSearch.enabled": true
}
```

### `.vscode/mcp.json` — pattern (no literal secrets)

```json
{
  "servers": {
    "supabase": {
      "command": "...",
      "inputs": [
        { "id": "supabase_access_token", "type": "promptString", "password": true }
      ]
    }
  }
}
```

---

## Related files in this repo

| File | Purpose |
|------|---------|
| `.github/copilot-instructions.md` | Copilot behavioural rules (auto-loaded) |
| `.github/agents/FixBot.agent.md` | End-to-end implementation agent |
| `.github/agents/Reviewer.agent.md` | Read-only code review agent |
| `.github/agents/odoo-oca-triage.agent.md` | CE/OCA triage agent |
| `prompts/fixbot_end_to_end.prompt.md` | FixBot reusable prompt template |
| `prompts/review_only.prompt.md` | Reviewer reusable prompt template |
| `scripts/dev/vscode_doctor.sh` | VS Code CLI pre-flight check |
| `scripts/dev/docker_doctor.sh` | Docker pre-flight check |
| `.vscode/mcp.json` | MCP server registrations (workspace) |
| `.vscode/extensions.json` | Recommended extensions |
| `ssot/devex/vscode.yaml` | Machine-readable VS Code SSOT config |
| `ssot/devex/vscode_enterprise.yaml` | VS Code enterprise posture |
