# n8n Runtime Ownership

> Defines runtime authority, deployment model, credential management, and integration surfaces for n8n.

## Runtime Authority

| Attribute | Value |
|-----------|-------|
| **Platform role** | Required orchestration plane (Lane 4) |
| **Canonical host** | Azure Container App or Cloudflare-proxied external |
| **Public hostname** | `n8n.insightpulseai.com` |
| **DNS** | Cloudflare (proxied, not Azure Front Door) |
| **Container App** | External to `rg-ipai-dev-odoo-runtime` (Cloudflare-routed) |

## Environment Model

| Environment | Instance | Workflow Source |
|-------------|----------|----------------|
| Dev/Local | Local Docker or dev ACA | `automations/n8n/workflows/` (git) |
| Staging | Staging ACA (if provisioned) | Same git source, imported via API |
| Production | `n8n.insightpulseai.com` | Same git source, imported via API |

## Credential Authority

- n8n credentials are managed **inside n8n's credential store**, not in git
- Credential references in workflow JSONs use `{{ $credentials.<name>.<field> }}`
- Environment variables use `{{ $env.<VAR_NAME> }}`
- Secrets backing n8n credentials are sourced from **Azure Key Vault** (`kv-ipai-dev`)
- Never commit literal credential values in workflow JSON exports

## Deploy Path

```
Developer edits workflow in n8n UI
  → Export JSON via n8n API or UI
  → Commit to automations/n8n/workflows/<name>.json
  → CI validates (planned: .github/workflows/n8n-validate.yml)
  → Import to target environment via n8n API
```

**Import/export authority**: The repo is the source of truth. The n8n UI is the authoring surface. Conflicts are resolved by re-importing from git.

## Promotion Model

1. Author/edit workflow in dev n8n instance
2. Export JSON, commit to `automations/n8n/workflows/`
3. CI validates structure and credential references
4. Import to staging (manual or CI-triggered)
5. Validate in staging
6. Import to production

## Workflow Registry

All active workflows are registered in `ssot/n8n/workflow_registry.yaml`. Workflows not in the registry are considered unmanaged.

## n8n Owns (Required)

- Telegram/chat ingress and document capture
- App/workflow automation (Odoo side effects, approvals, scheduled jobs)
- Notifications (Slack, email via webhooks)
- Control-plane sync and event handling (GitHub webhooks, Plane sync)
- MCP bridge workflows (Claude AI agent tool execution)

## n8n Does NOT Own

- Primary analytical CDC for Azure PostgreSQL/Odoo → **Fabric Mirroring** (Lane 1)
- Primary analytical CDC for Supabase → **`supabase/etl`** (Lane 3)
- Governed data transformation and semantic serving → **Databricks + Unity Catalog** (Lane 2)
- Business reporting consumption → **Power BI** (Lane 2 output)

## Integration Surfaces

### Odoo Connector (`ipai_n8n_connector`)

- Odoo module providing webhook endpoints for n8n
- Located at `addons/ipai/ipai_n8n_connector/`
- Built-in n8n Odoo node covers: contacts, custom resources, notes, opportunities
- Broader ERP coverage via HTTP Request node against Odoo JSON-RPC/XML-RPC

### MCP API Bridge (`agents/mcp/n8n-api-bridge/`)

- TypeScript MCP server bridging Claude agents to n8n workflows
- Allows Claude to trigger, monitor, and manage n8n workflows
- Credential isolation: bridge uses n8n API key, never accesses workflow credentials directly

### Supabase Integration

- Built-in n8n Supabase node for row-level CRUD (create, get, get all, update, delete)
- Suitable for operational workflows, NOT bulk analytical replication
- For analytical CDC, use `supabase/etl` (Lane 3)

---

*Created: 2026-03-21*
