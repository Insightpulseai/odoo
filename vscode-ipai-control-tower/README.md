# IPAI Control Tower — VS Code Extension

Platform assistant and doctrine enforcement for the InsightPulseAI stack.

## Features

- **`@ipai` chat participant** — ask about Odoo 18 CE, Azure-native infrastructure, BIR compliance, and IPAI platform doctrine. Backed by `ipai-copilot` (Foundry SDK 2.x, `claude-sonnet-4-6`).
- **Doctrine diagnostics** — real-time warnings when code violates IPAI platform rules: `<tree>` view in Odoo XML, hardcoded secrets, deprecated Supabase patterns, non-Azure-native workloads.
- **Control Tower sidebar** — Doctrine status, `ops.agent_runs` log, and installed Odoo module tree.
- **Commands** — scaffold Odoo modules, validate views, open Foundry portal, show agent runs.

## Setup

### 1. Install

```bash
cd vscode-ipai-control-tower
npm install
npm run install-local
```

Or from a pre-built `.vsix`:

```bash
code --install-extension ipai-control-tower-0.1.0.vsix
```

### 2. Configure

Open VS Code settings (`Cmd+,`) and search for `ipai`:

| Setting | Default | Description |
|---|---|---|
| `ipai.foundry.endpoint` | `https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot` | Foundry SDK 2.x endpoint |
| `ipai.foundry.deployment` | `claude-sonnet-4-6` | Model deployment name |
| `ipai.odoo.serverUrl` | `http://localhost:8069` | Odoo instance for adapter |
| `ipai.doctrine.enableOnSave` | `true` | Run diagnostics on save |

Authentication uses `DefaultAzureCredential` — run `az login` before using the chat participant.

### 3. Use

**Chat:**
```
@ipai /doctrine Is this correct Odoo 18 view syntax?
@ipai /bir How do I generate BIR Form 2307 for vendor X?
@ipai /migrate Map CustTable to res.partner
@ipai /infra What's the ACA resource spec for copilot-gateway?
```

**Commands (Cmd+Shift+P):**
- `IPAI: Check doctrine compliance` — lint current file
- `IPAI: Scaffold Odoo module` — generate `ipai_*` module scaffold
- `IPAI: Validate Odoo views` — detect `<tree>` usage (must be `<list>`)

## Doctrine rules enforced

| Rule | Trigger |
|---|---|
| `<tree>` in XML views | Error — use `<list>` in Odoo 18 |
| `supabase` import or URL | Warning — Supabase is deprecated |
| `DigitalOcean` / `DO droplet` reference | Warning — no new DO workloads |
| Hardcoded `sk-`, `eyJ`, API key patterns | Error — use Key Vault |
| `AzureOpenAI()` direct SDK call | Warning — use `AIProjectClient` (Foundry SDK 2.x) |

## Development

```bash
npm run watch          # watch mode
# F5 in VS Code → "Launch Extension" (uses .vscode/launch.json)
npm run test           # run extension tests
```

## Architecture

```
src/
  extension.ts         — activate() entry point
  adapters/            — Odoo JSON-RPC, ops-platform, Foundry connections
  chat/
    ipaiParticipant.ts — @ipai chat participant handler
  commands/            — VS Code command registrations
  diagnostics/
    doctrineDiagnostics.ts — DiagnosticsCollection + lint rules
  views/               — TreeDataProviders for sidebar panels
  testing/             — Extension test runner
```
