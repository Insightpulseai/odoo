# MCP Servers Inventory

> **Locked:** 2026-04-15
> **Authority:** [`.mcp.json`](../../.mcp.json) (canonical config)
> **Companion:** [`docs/skills/stack-build-map.md`](../skills/stack-build-map.md)
> **Doctrine:** per-agent allowlist required (3-tier defense per CLAUDE.md §Agentic Workflow Security)

---

## All 8 MCP servers (post-2026-04-15 update)

| # | Server | Type | Status | Tool prefix | Source |
|---|---|---|---|---|---|
| 1 | `github` | Remote (HTTP) | ✅ live | `mcp__github__*` | `api.githubcopilot.com/mcp/` |
| 2 | `microsoft-learn` | Remote (HTTP) | ✅ live | `mcp__microsoft-learn__*` | `learn.microsoft.com/api/mcp` |
| 3 | `azure` | Local (npx) | ✅ live | `mcp__azure__*` (200+ tools, 40+ services) | `@azure/mcp@latest` v2.0.0 |
| 4 | `azure-devops` | Local (npx) | ✅ live | `mcp__azure-devops__*` | `@azure-devops/mcp` v2.5.0 |
| 5 | **`foundry`** | Local (uvx) | ✅ NEW (this update) | `mcp__foundry__*` | `azure-ai-foundry/mcp-foundry` (Python via uvx, MIT) |
| 6 | `playwright` | Local (npx) | ✅ live | `mcp__playwright__*` | `@playwright/mcp@latest` v0.0.70 |
| 7 | `figma` | Remote (HTTP) | ✅ live | `mcp__figma__*` | `figma.com/mcp` |
| 8 | **`databricks-genie`** | Local (Python) | ⏸ configured (manual install) | `mcp__databricks-genie__*` | `alexxx-db/databricks-genie-mcp` |

---

## What changed (2026-04-15)

- ➕ Added `foundry` MCP entry (pinned to `azure-ai-foundry/mcp-foundry` via uvx)
- ➕ Added `databricks-genie` MCP entry (skeleton; requires manual install)
- 🔁 Reordered to group Azure-related servers together

---

## Coverage matrix

| Capability area | Server(s) covering it |
|---|---|
| Azure Database for PostgreSQL | `azure` (`mcp__azure__postgres`) |
| Azure resources (general) | `azure` (200+ tools) |
| Foundry models + agents + projects | `azure` (`mcp__azure__foundry`) + new `foundry` MCP (Python upstream) |
| Azure DevOps (Boards, Pipelines, Wiki, Test Plans) | `azure-devops` |
| GitHub repos / PRs / issues | `github` |
| Microsoft Learn docs | `microsoft-learn` |
| Browser automation | `playwright` |
| Figma design files | `figma` |
| **Databricks Genie (NL → SQL on Unity Catalog)** | `databricks-genie` (configured, awaiting install) |

---

## Foundry MCP — wired today

```jsonc
"foundry": {
  "command": "uvx",
  "args": [
    "--prerelease=allow",
    "--from",
    "git+https://github.com/azure-ai-foundry/mcp-foundry.git",
    "run-azure-ai-foundry-mcp"
  ],
  "env": {
    "AZURE_AI_FOUNDRY_ENDPOINT": "https://ipai-copilot-resource.services.ai.azure.com/api/projects/proj-ipai-copilot"
  }
}
```

**Pre-req:**
- `uvx` installed ✅ (verified — Homebrew v0.9.5)
- Foundry project `proj-ipai-copilot` ⏸ pending creation on `ipai-copilot-resource`
- Entra MI auth via `DefaultAzureCredential` ✅

**Known limitation:**
- The OSS upstream `azure-ai-foundry/mcp-foundry` last-pushed 2025-11-19 (~5mo)
- Microsoft has a newer cloud Foundry MCP bundled in `microsoft/azure-skills` plugin
- We use the OSS path here for explicit pinning + portability; the cloud version is implicit via `azure` entry's `mcp__azure__foundry` tools

---

## Databricks Genie MCP — configured but not installed

```jsonc
"databricks-genie": {
  "command": "python3",
  "args": ["-m", "databricks_genie_mcp.server"],
  "env": {
    "DATABRICKS_HOST": "https://adb-e7d89eabce4c330c.0.azuredatabricks.net",
    "DATABRICKS_GENIE_SPACE_ID": "TBD_PER_GENIE_SPACE",
    "_NOTE": "Requires manual install...",
    "_REPO": "https://github.com/alexxx-db/databricks-genie-mcp",
    "_STATUS": "configured-but-not-yet-installed"
  }
}
```

**To install:**

```bash
# 1. Clone
cd ~/Code
git clone https://github.com/alexxx-db/databricks-genie-mcp.git
cd databricks-genie-mcp

# 2. Install Python deps (use a venv)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Authenticate (one of)
# Option A — Entra MI (recommended for prod)
az login
export AZURE_CLIENT_ID=<sp-client-id>

# Option B — DBX PAT (dev only)
export DATABRICKS_HOST=https://adb-e7d89eabce4c330c.0.azuredatabricks.net
export DATABRICKS_TOKEN=<pat>

# 4. Find your Genie Space ID via Databricks UI
#    Workspace → AI/BI → Genie Spaces → <your space> → settings
export DATABRICKS_GENIE_SPACE_ID=<id>

# 5. Update .mcp.json with the absolute Python path of your venv
#    AND the real DATABRICKS_GENIE_SPACE_ID
```

**Pre-req:**
- Databricks workspace `dbw-ipai-dev` ✅ (per memory)
- Databricks Assistant + Pro/Serverless SQL warehouse: ⏸ verify current state
- A Genie Space created with relevant Unity Catalog access: ⏸ pending
- Auth via DBX PAT or Azure SP/MI: ⏸ pending

**Why deferred:**
- Requires per-Genie-Space-ID config (not just generic Databricks creds)
- Last upstream push 2025-05-12 (~11 months) — flag for staleness check before adoption
- Better wait for an official Microsoft/Databricks MCP if one ships

---

## Per-agent allowlist enforcement (CLAUDE.md doctrine)

Per `CLAUDE.md` §"Agentic Workflow Security Doctrine" — every agent MUST declare its MCP tool allowlist.

```yaml
# Example agent allowlist (tax-guru)
agent: tax_guru
mcp_allowlist:
  - mcp__azure__postgres            # read GL data
  - mcp__azure-devops__wit_*         # update Boards work items
  - mcp__microsoft-learn__*          # BIR docs lookup
forbidden:
  - mcp__github__*                   # not Tax Guru's concern
  - mcp__playwright__*               # not Tax Guru's concern
  - mcp__figma__*                    # not Tax Guru's concern
  - mcp__databricks-genie__*         # data-intel agent only
```

These allowlists live in agent config (TBD location — likely `agent-platform/agents/<name>/manifest.yaml`).

---

## Smoke test (quick verification)

```bash
# Each local MCP boots clean
npx -y @azure/mcp@latest --version          # → Azure.Mcp.Server 2.0.0
npx -y @playwright/mcp@latest --version      # → Version 0.0.70
npx -y @azure-devops/mcp --version           # → 2.5.0
uvx --version                                 # → uvx 0.9.5

# Foundry MCP cold start (first invocation downloads via uvx)
uvx --prerelease=allow --from git+https://github.com/azure-ai-foundry/mcp-foundry.git run-azure-ai-foundry-mcp --help

# Remote endpoints (HTTP MCPs)
curl -sI https://api.githubcopilot.com/mcp/ | head -1
curl -sI https://learn.microsoft.com/api/mcp | head -1
curl -sI https://figma.com/mcp | head -1
```

---

## Doctrine alignment

| Rule | Enforcement |
|---|---|
| Per-agent MCP allowlist (3-tier defense) | Documented per agent in `agent-platform/agents/*` (TBD) |
| No new MCP server without `.mcp.json` PR | This file change requires PR review |
| Pin versions | All `npx -y` use `@latest` (acceptable for HTTP-pulled tools); `uvx` pins by git ref |
| Remote MCP must use HTTPS | All HTTP entries use HTTPS |
| Entra MI auth where supported | Foundry uses MI; Databricks Genie supports MI when configured |

---

## Roadmap

| Server | Status | Action |
|---|---|---|
| `foundry` | ✅ wired this update | Verify boots after Foundry project creation |
| `databricks-genie` | ⏸ skeleton | Install + configure + create Genie Space — when data-intel skill activates |
| Future: `odoo-mcp-server` | ❌ P0 gap | Build per `capability-source-map.md` §coverage_gaps (no upstream OSS exists) |

---

## References

- [`.mcp.json`](../../.mcp.json) — canonical config
- [`docs/skills/stack-build-map.md`](../skills/stack-build-map.md) — agent-building track
- [`ssot/governance/upstream-adoption-register.yaml`](../../ssot/governance/upstream-adoption-register.yaml) — register
- [`docs/architecture/capability-source-map.md`](../architecture/capability-source-map.md) — what we consume
- Memory: `agent_framework_patterns`, `pulser_agent_classification`

---

*Last updated: 2026-04-15*
