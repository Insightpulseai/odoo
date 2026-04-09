# VS Code Recommended Policies — Insightpulseai/odoo

> 13 policies derived from VS Code official documentation, mapped to this repo's conventions.
> Source URLs accompany each policy. Enforcement mechanism noted where applicable.
> Last updated: 2026-03-02

---

## Policy Table

| # | Policy | Enforcement | Source |
|---|--------|-------------|--------|
| 1 | **Dev Container must use `colima` docker context** — `devcontainer.json` must set `"dockerContext": "colima"` and reference `scripts/devcontainer/preflight.sh` as `initializeCommand`. `colima-odoo` context is Supabase-isolation only; never use it for devcontainers. | CI: `.github/workflows/devcontainer-context-guard.yml` | [Developing inside a Container](https://code.visualstudio.com/docs/devcontainers/containers) |
| 2 | **Copilot must use `.github/copilot-instructions.md`** — All contributors work with Copilot auto-loading the repo-level instructions file. Never duplicate those instructions in personal/workspace settings. Edit the shared file instead. | Auto-loaded by VS Code Copilot; no CI gate needed | [Prompt engineering in VS Code](https://code.visualstudio.com/docs/copilot/guides/prompt-engineering-guide) |
| 3 | **MCP server secrets via `inputs`, never hardcoded** — `.vscode/mcp.json` (tracked in git) must use the `inputs` array for all credentials. Literal token values are forbidden. Reference `ssot/secrets/registry.yaml` for identifier names. | Pre-commit: secret scanning hook | [Add and manage MCP servers in VS Code](https://code.visualstudio.com/docs/copilot/customization/mcp-servers) |
| 4 | **Extensions recommended via `.vscode/extensions.json`** — Required extensions (`ms-vscode-remote.remote-containers`, `ms-python.python`, `github.copilot`, `github.copilot-chat`, `ms-azuretools.vscode-docker`) must appear in the `recommendations` array. Optional extensions go in `unwantedRecommendations` only when they conflict with the stack. | Dev Container setup instruction | [Additional components and tools](https://code.visualstudio.com/docs/setup/additional-components) |
| 5 | **Agent mode requires tool approval for write operations** — Any Copilot Agent tool that produces file edits, git commits, or external API calls must wait for explicit contributor approval before executing. Never configure agents to auto-approve destructive tools. | Documented in `.github/copilot-instructions.md` §Agentic Loop | [Use tools with agents](https://code.visualstudio.com/docs/copilot/agents/agent-tools) |
| 6 | **Reusable prompts live in `prompts/`** — Sharable agent invocations are stored as `prompts/*.prompt.md` files (not chat history). New prompt templates follow the frontmatter schema: `mode`, `tools`, `description`. | Team convention; Copilot prompt file spec | [Prompt engineering in VS Code](https://code.visualstudio.com/docs/copilot/guides/prompt-engineering-guide) |
| 7 | **Smart actions are drafts only** — Copilot smart actions (commit message, test generation, docs generation) produce drafts for human review. Never treat smart-action output as authoritative without review. In particular, generated commit messages must be checked against the `feat|fix|chore(scope): description` convention. | Documented in `CONTRIBUTING.md` §Copilot | [AI smart actions in VS Code](https://code.visualstudio.com/docs/copilot/copilot-smart-actions) |
| 8 | **`code --version` must succeed before Dev Container open** — The VS Code CLI (`code`) must be on PATH and `code --version` must exit 0. Run `bash scripts/dev/vscode_doctor.sh` to verify. Dev Container open will fail if the CLI is not reachable. | `scripts/dev/vscode_doctor.sh` (exit 0/1) | [Additional components and tools](https://code.visualstudio.com/docs/setup/additional-components) |
| 9 | **Org policy governs `chat.agent.enabled`** — If GitHub Copilot agent mode is disabled by organization policy, contributors must not attempt to circumvent it via personal settings. The documented workaround is to request the admin to enable `chat.agent.enabled` for the org. | Org admin; noted in `CONTRIBUTING.md` §Copilot | [How AI works in VS Code](https://code.visualstudio.com/docs/copilot/core-concepts) |
| 10 | **Shell integration enabled in Dev Container** — `.devcontainer/devcontainer.json` `customizations.vscode.settings` must include `"terminal.integrated.shellIntegration.enabled": true` and `"terminal.integrated.defaultProfile.linux": "zsh"` so Copilot can read terminal output as context and Zsh aliases load correctly. | Dev Container setup | [Terminal Basics](https://code.visualstudio.com/docs/terminal/basics) |
| 11 | **Python interpreter pinned to repo venv** — `.devcontainer/devcontainer.json` `customizations.vscode.settings` must set `"python.defaultInterpreterPath": "/workspaces/odoo/.venv/bin/python"` and `"python.terminal.activateEnvironment": true`. This ensures Pylance and Copilot have correct Odoo 18 type context. | Dev Container setup | [Getting Started with Python in VS Code](https://code.visualstudio.com/docs/python/python-tutorial) |
| 12 | **`#codebase` search enabled for Copilot** — `"github.copilot.chat.codeSearch.enabled": true` must be set in `.vscode/settings.json` (workspace-scoped, tracked in git) so that `#codebase` context variable auto-indexes `addons/ipai/` and the monorepo root for all contributors. | `.vscode/settings.json` (tracked) | [GitHub Copilot tips and tricks](https://code.visualstudio.com/docs/copilot/copilot-tips-and-tricks) |
| 13 | **MCP servers must be declared in `.vscode/mcp.json`** — New MCP servers are registered via `code --add-mcp` (user-scoped) or by editing `.vscode/mcp.json` (workspace-scoped, shared). The workspace file is the canonical source for repo contributors; user-level registrations are personal and should not substitute for the shared file. | `.vscode/mcp.json` (tracked) | [Add and manage MCP servers in VS Code](https://code.visualstudio.com/docs/copilot/customization/mcp-servers) |

---

## Verification commands

```bash
# Policy 1 — docker context
python scripts/ci/check_devcontainer_docker_context.py

# Policy 2 — copilot-instructions.md exists and is non-empty
test -s .github/copilot-instructions.md && echo "OK" || echo "MISSING"

# Policy 3 — no literal secrets in mcp.json (basic check)
grep -Ei '(token|password|secret)\s*[:=]\s*"[A-Za-z0-9+/=_-]{20,}"' .vscode/mcp.json && echo "FAIL: literal secret found" || echo "OK"

# Policy 4 — required extensions declared
python -c "import json; e=json.load(open('.vscode/extensions.json')); r=e.get('recommendations',[]); required=['ms-vscode-remote.remote-containers','ms-python.python','github.copilot','github.copilot-chat']; missing=[x for x in required if x not in r]; print('MISSING:',missing) if missing else print('OK')"

# Policy 6 — prompts directory exists with at least one file
ls prompts/*.prompt.md 2>/dev/null | wc -l | xargs -I{} sh -c '[ {} -ge 1 ] && echo "OK ({} prompts)" || echo "MISSING"'

# Policy 8 — VS Code CLI reachable
bash scripts/dev/vscode_doctor.sh

# Policies 10-12 — devcontainer settings
python -c "
import json
c=json.load(open('.devcontainer/devcontainer.json'))
s=c.get('customizations',{}).get('vscode',{}).get('settings',{})
checks=[
  ('terminal.integrated.shellIntegration.enabled', True),
  ('python.defaultInterpreterPath', '/workspaces/odoo/.venv/bin/python'),
]
for k,v in checks:
  status='OK' if s.get(k)==v else f'MISSING (got {s.get(k)!r})'
  print(f'{k}: {status}')
"
```

### Policy 14 — Delegate GitHub auth to `gh` CLI keyring; never use VS Code's own session

**Source**: <https://code.visualstudio.com/docs/sourcecontrol/overview>

VS Code maintains its own GitHub credential session (`github.gitAuthentication`) independently of the `gh` CLI keyring. When these two credential sources diverge — e.g. VS Code session is valid but `gh` keyring is `jgtolentino`, or VS Code session expires — tools in VS Code's child processes get conflicting tokens → HTTP 401.

**Set in `.devcontainer/devcontainer.json` `customizations.vscode.settings`**:

```json
{
  "github.gitAuthentication": false,
  "git.autofetch": true
}
```

`github.gitAuthentication: false` tells VS Code to skip its own OAuth flow and let `gh` CLI handle all GitHub auth via keyring. One credential source → zero 401 conflicts.

**Verify**:

```bash
# Inside Dev Container — confirm no VS Code GitHub session is active
code --list-extensions | grep GitHub.vscode-pull-request-github
# Then open any PR in VS Code — it should use gh CLI auth, not prompt for VS Code sign-in
```

---

## See also

- [`docs/dev/vscode/INDEX.md`](INDEX.md) — Full page-by-page reference table
- [`ssot/devex/vscode.yaml`](../../../ssot/devex/vscode.yaml) — Machine-readable SSOT config
- [`.github/copilot-instructions.md`](../../../.github/copilot-instructions.md) — Copilot behavioural rules
- [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) — Contributor prerequisites and Copilot modes
