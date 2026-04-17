# Runbook: Azure Postgres MCP Server — IPAI setup

## What this wires

```
ipai-copilot (Foundry project)
  → ipai-pg-mcp-server (new ACA, azmcp image)
  → pg-ipai-odoo (PostgreSQL Flex, SEA)
```

## What IPAI already has (no need to provision)

| Resource | Status | Note |
|---|---|---|
| `pg-ipai-odoo` | ✓ Live | rg-ipai-dev-odoo-data, SEA |
| `ipai-copilot-resource` | ✓ Live | Foundry hub, East US 2 |
| `ipai-copilot` | ✓ Live | Foundry project, East US 2 |
| `ipai-odoo-dev-env-v2` | ✓ Live | ACA environment to host new MCP container |
| `acripaiodoo` | ✓ Live | Container Registry (not needed — azmcp uses public image) |

## What gets created by azd up

| Resource | Name | Notes |
|---|---|---|
| Container App | `ipai-pg-mcp-server` | Runs official `azmcp` image, SEA |
| Entra ID App Registration | auto-named | MCP server auth identity |
| Managed Identity | `ipai-pg-mcp-server` MI | Used by ACA to auth to pg-ipai-odoo |
| Role assignment | Reader on pg-ipai-odoo | Foundry MI authenticates to MCP server |

## Region note

`pg-ipai-odoo` is **Southeast Asia**. The new MCP ACA must also be deployed to SEA
(set `location: southeastasia` in parameters — see `infra/main.parameters.json`).
Foundry (`ipai-copilot-resource`) is in East US 2 — cross-region call from
Foundry → MCP server (SEA). Latency ~150ms acceptable for agent queries, not for
real-time Odoo UI. Accept this tradeoff until Foundry reaches SEA GA.

## Decision: new ACA vs reuse ipai-mcp-dev

`ipai-mcp-dev` currently runs the n8n/IPAI MCP server (custom image).
Deploy the Postgres MCP server as a **separate ACA** (`ipai-pg-mcp-server`) to:
- Keep identities isolated (separate MI per MCP surface)
- Avoid disrupting existing MCP routes
- Match the demo's security model (dedicated Postgres-only MI)

---

## Step-by-step

### Prerequisites

```bash
az login
azd auth login
az account set --subscription eba824fb-332d-4623-9dfb-2c9f7ee83f4e
```

### Step 1: Clone and configure

```bash
git clone https://github.com/Azure-Samples/azure-postgres-mcp-demo
cd azure-postgres-mcp-demo

# Copy IPAI-specific parameters
cp /path/to/ipai-pg-mcp/infra/main.parameters.json infra/main.parameters.json
```

### Step 2: Deploy

```bash
azd env new ipai-pg-mcp-dev
azd up
```

Deployment takes ~2 minutes. Capture the output:

```bash
azd env get-values
# CONTAINER_APP_IDENTITY_NAME=ipai-pg-mcp-server-<suffix>
# CONTAINER_APP_URL=https://ipai-pg-mcp-server-<suffix>.southeastasia.azurecontainerapps.io
# ENTRA_APP_CLIENT_ID=<uuid>
```

### Step 3: Create pg principal

```bash
# Connect to pg-ipai-odoo via Entra ID
export PGHOST=pg-ipai-odoo.postgres.database.azure.com
export PGUSER=<admin-username>
export PGPORT=5432
export PGDATABASE=postgres
export PGPASSWORD="$(az account get-access-token \
  --resource https://ossrdbms-aad.database.windows.net \
  --query accessToken --output tsv)"

psql

# Inside psql — replace with actual identity name from azd env get-values
SELECT * FROM pgaadauth_create_principal('ipai-pg-mcp-server-<suffix>', false, false);
\q
```

### Step 4: Grant schema access

```bash
PGDATABASE=odoo psql < scripts/setup-pg-mcp-access.sql
# Edit the SQL file first: replace <CONTAINER_APP_IDENTITY_NAME>
```

### Step 5: Connect to Foundry portal

1. Portal → `ipai-copilot-resource` → Go to Foundry portal
2. Start building → Create agent → name: `odoo-pg-agent`
3. Tools → Add → Catalog → Azure Database for PostgreSQL → Create
4. Connect tool with endpoint → enter `CONTAINER_APP_URL`
5. Auth: Microsoft Entra → Project Managed Identity
6. Audience: `ENTRA_APP_CLIENT_ID` value
7. Save

Add agent instructions:

```
You are a helpful Odoo ERP data analyst. Use the PostgreSQL MCP tools
to query the Odoo database and answer questions about accounting,
invoices, sales orders, and purchase orders.
```

Parameters:
```json
{
  "database": "odoo",
  "resource-group": "rg-ipai-dev-odoo-data",
  "server": "pg-ipai-odoo",
  "subscription": "eba824fb-332d-4623-9dfb-2c9f7ee83f4e",
  "user": "ipai-pg-mcp-server-<suffix>"
}
```

### Step 6: Test

```
List all tables in the Odoo database
Show me the 10 most recent invoices from account_move
How many open purchase orders are in the purchase_order table?
Show the schema for res_partner
```

---

## Schema access scope (principle of least privilege)

| Schema | Access | Reason |
|---|---|---|
| `public` | SELECT all tables | Odoo SOR data |
| `ops` | SELECT all tables | IPAI run events, metering |
| `mdm` | SELECT all tables | Master data overlays |
| `audit` | None (deny) | Append-only audit trail — no agent reads |
| `marketplace` | None (deny) | Billing data — exclude |

## Cleanup (remove MCP server)

```bash
azd down --purge
# Then revoke pg principal:
# DROP ROLE "ipai-pg-mcp-server-<suffix>";
```
