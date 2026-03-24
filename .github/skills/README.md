# Azure/Odoo Benchmark Gap-Closure Skills

Focused skill pack for coding agents closing the highest-confidence gaps
identified in the Odoo-on-Azure enterprise benchmark audit.

## Authority Order

When resolving a gap, agents MUST consult sources in this strict order:

1. **Repo evidence first** -- inspect the exact files listed in each skill's
   "Required evidence" section. The repo is the system of record for current state.
2. **Microsoft Learn MCP second** -- use the `microsoft_docs_search`,
   `microsoft_code_sample_search`, and `microsoft_docs_fetch` tools to retrieve
   first-party Microsoft guidance. The `.codex/config.toml` file registers the
   server at `https://learn.microsoft.com/api/mcp`.
3. **Docs and specs third** -- consult `docs/`, `spec/`, and `infra/ssot/` for
   architectural decisions and delivery plans already captured in the repo.

Agents MUST NOT invent configuration values. If a parameter (SKU, CIDR, policy
ID) is not found in sources 1-3, the agent must flag it as a required decision
and stop.

## Usage Rules

- Each skill directory contains `SKILL.md` (contract) and `examples.md` (worked
  patterns).
- Skills are grouped by impact tier (P0/P1/P2). Agents should prioritize P0
  skills when multiple gaps are open.
- Every skill follows a 5-step workflow: inspect repo, query MCP, compare,
  patch, verify.
- Completion criteria in each `SKILL.md` are hard gates -- the agent may not
  claim a gap is closed until every criterion is met.
- Evidence artifacts go to `docs/evidence/<YYYYMMDD-HHMM>/<skill-name>/`.

## Impact Tiers

### P0 -- Data Loss / Security Exposure

| Skill | Gap |
|-------|-----|
| `azure-pg-ha-dr` | PG HA, backup retention, geo-backup, RPO/RTO |
| `entra-mfa-ca-hardening` | MFA enforcement, Conditional Access, P1 path |
| `aca-private-networking` | NSGs, private endpoints, PG subnet restriction |

### P1 -- Operational Readiness

| Skill | Gap |
|-------|-----|
| `azure-observability-baseline` | App Insights, Log Analytics, alerts |
| `odoo-image-supply-chain` | ACR build, vuln scanning, image signing |
| `odoo-release-promotion` | dev/staging/prod gates, migration verify, rollback |
| `azure-policy-guardrails` | Require tags, deny public PG, require KV |

### P2 -- Quality / Accuracy

| Skill | Gap |
|-------|-----|
| `odoo-copilot-evals` | Expand from 2 to 50+ test cases, adversarial, regression |
| `service-matrix-truth` | Remove nginx stubs from active inventory, align reality |

## MCP Server Configuration

The Microsoft Learn MCP server is registered in `.codex/config.toml`:

```toml
[mcp_servers.microsoft-learn]
url = "https://learn.microsoft.com/api/mcp"
```

Agents with MCP support will auto-discover this server. For agents without
`.codex` support, invoke the tools directly:

- `microsoft_docs_search` -- breadth search, returns up to 10 chunks
- `microsoft_code_sample_search` -- code snippets with optional language filter
- `microsoft_docs_fetch` -- full page markdown from a known URL
