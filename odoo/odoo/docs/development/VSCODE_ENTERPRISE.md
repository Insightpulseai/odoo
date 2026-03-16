# VS Code Enterprise Configuration

**SSOT**: `ssot/devex/vscode_enterprise.yaml`
**Ref**: [VS Code Enterprise docs](https://code.visualstudio.com/docs/setup/enterprise),
         [VS Code Copilot overview](https://code.visualstudio.com/docs/copilot/overview)

---

## Overview

VS Code for enterprise adds centrally managed policies, extension governance, and network configuration on top of the standard editor. This document explains how each lever maps to this repo's workflow.

---

## 1. Enterprise Policies

VS Code supports OS-level policy enforcement (Windows/macOS/Linux), allowing IT admins to lock down editor behaviour.

**Key policies in use** (see `ssot/devex/vscode_enterprise.yaml`):

| Policy | Setting | Reason |
|--------|---------|--------|
| `UpdateMode` | `manual` | Prevents auto-update disruptions during sprint |
| Extension enforcement | `allowlist` | Only approved extensions installable |
| Private marketplace | `false` (default) | Available if GitHub Enterprise + Copilot Business/Enterprise licensed |

Policies are declared in the SSOT but **enforced at the OS/MDM layer** (outside the repo).
The repo ships `.vscode/extensions.json` and `.vscode/settings.json` as the **project contract**; org policies may override these.

---

## 2. Extension Management

### Recommended extensions (`.vscode/extensions.json`)

Declared in the repo; developers are prompted to install on first open.

| Extension | Purpose |
|-----------|---------|
| `ms-vscode-remote.remote-containers` | Dev Containers |
| `ms-python.python` + `ms-python.pylance` | Python / Odoo modules |
| `ms-python.black-formatter` + `charliermarsh.ruff` | Formatting + linting |
| `github.copilot` + `github.copilot-chat` | AI assistance |
| `esbenp.prettier-vscode` + `dbaeumer.vscode-eslint` | TS/JS code quality |
| `redhat.vscode-yaml` | SSOT YAML editing |
| `github.vscode-github-actions` | CI workflow linting |

### Private marketplace

If the org upgrades to GitHub Enterprise + Copilot Business/Enterprise, VS Code can be configured to use a private marketplace so only vetted extensions are installable.
See VS Code docs: [Enterprise Extension Marketplace](https://code.visualstudio.com/docs/setup/enterprise#_extension-marketplace).

---

## 3. Network Configuration (Restricted Environments)

For environments behind a firewall or HTTPS proxy, VS Code requires the following:

- **Proxy**: VS Code uses system proxy settings by default. No additional config needed unless the proxy terminates TLS.
- **SSL certificates**: For HTTPS-intercepting proxies, the org's CA must be trusted by VS Code.
- **Allowlist hostnames** (minimum required):
  - `update.code.visualstudio.com` — editor updates
  - `marketplace.visualstudio.com` + `*.gallerycdn.vsassets.io` — extensions
  - `*.github.com` — Copilot authentication
  - `*.openai.azure.com` — Copilot model inference (Microsoft-hosted)

Full allowlist: [VS Code network connections](https://code.visualstudio.com/docs/setup/network).

---

## 4. GitHub Copilot in This Repo

### File-based instructions (higher priority than settings)

`.github/copilot-instructions.md` provides repo-level instructions that apply automatically to all contributors. VS Code recommends file-based instructions over settings-based instructions because they are version-controlled and consistent across machines.

### Model selection + pinning

VS Code Copilot allows choosing the active model per task. For this repo:

- **Default**: use Copilot's "latest" model (automatic best-available).
- **For migrations + CI debugging**: prefer a reasoning-capable model.
- **For refactors + boilerplate**: prefer a fast/cost-efficient model.

Pin models in `.github/copilot-instructions.md` or per-workflow instruction files for deterministic agentic runs.

### Agent Skills

VS Code Copilot supports portable "Agent Skills" (`agent-skills/` directory). Skills bundle instructions + scripts and work across VS Code, Copilot CLI, and the Copilot coding agent. See `agent-skills/` for this repo's skills.

### Agentic loop

When Copilot runs as an agent (Copilot coding agent or custom agent), it should follow the agentic loop defined in `docs/architecture/AGENTIC_CODING_CONTRACT.md`:

```
Plan → Patch → Verify (tests/gates) → PR
```

All agent runs must produce a PR and evidence. Runs must be logged to `ops.runs` / `ops.run_events`.

---

## References

- [VS Code Enterprise overview](https://code.visualstudio.com/docs/setup/enterprise)
- [VS Code Copilot overview](https://code.visualstudio.com/docs/copilot/overview)
- [Copilot best practices](https://code.visualstudio.com/docs/copilot/best-practices)
- [GitHub Copilot coding agent docs](https://docs.github.com/copilot/using-github-copilot/using-copilot-coding-agent)
- SSOT: `ssot/devex/vscode_enterprise.yaml`
- Copilot instructions: `.github/copilot-instructions.md`
- Agentic coding contract: `docs/architecture/AGENTIC_CODING_CONTRACT.md`
