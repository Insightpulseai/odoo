---

# Azure Database for PostgreSQL (Flexible Server) — IPAI Grounded Knowledge Pack

> **Scope**: This pack is scoped to the InsightPulseAI production instance `pg-ipai-odoo` (PG 16, General Purpose, Southeast Asia). Every section cites the Microsoft Learn URL it grounds on. It does **not** duplicate the generic category index at `~/.claude/skills/azure-database-postgresql/SKILL.md` — it complements it with IPAI-specific gap analysis.
>
> **Intended save path (if you choose to write it)**: `docs/skills/azure-postgresql-ipai-grounded.md` — note: I am returning this inline per the parent-agent protocol, not writing the file.
>
> **Honest posture**: This is not a "100% production ready" claim. Several items below are `not-started` or `in-progress`. Where Microsoft does not document a specific behavior, I say so explicitly.
>
> **Last updated**: 2026-04-14. All URLs are `learn.microsoft.com` unless noted.

---

## 0. IPAI canonical instance snapshot

| Attribute | Value | Source of truth |
|---|---|---|
| Server name | `pg-ipai-odoo` | memory: `pg-ipai-odoo` (General Purpose, Fabric mirroring). Old `ipai-odoo-dev-pg` deprecated |
| Engine | PostgreSQL 16 (Flexible Server) | CLAUDE.md Stack row |
| Tier | General Purpose | MEMORY.md Data Platform |
| Region | Southeast Asia (primary) | CLAUDE.md; runtime FQDN `blackstone-0df78186.southeastasia.azurecontainerapps.io` |
| Paired region (DR) | East Asia | Azure region pairs (SEA ↔ East Asia) |
| Current subscription | Subscription 1 (`536d8cf6-…`) | Prompt context |
| Target subscription | Sponsored (`eba824fb-…`) | project_sponsored_sub_migration_adr.md (ADR-002: native-move, DNS stays) |
| Logical DBs | `odoo_dev`, `odoo_staging`, `odoo`, `test_<module>` | CLAUDE.md Quick Reference |
| Schemas in `odoo` / `odoo_dev` | `public` (Odoo ORM), `ops` (Pulser), `platform` (cross-cutting) | prompt context |
| Tenancy | Multi-company via `res.company` (IPAI=1, W9=2, OMC=3, TBWA\SMP=4) | project_tenant_map_20260414.md |
| Access posture | Private endpoint; no public IP | prompt context + CLAUDE.md Rule #10 |
| AuthN target | Entra Managed Identity for service workloads | prompt context |
| PgBouncer | OFF (target: ON for prod) | prompt context |
| Fabric mirroring | **ACTIVE** (workspace `fcipaidev`) | project_fabric_finance_ppm.md |
| MCP path | `ipai-odoo-mcp` (ACA, 13 tools), `ipai-odoo-connector` (JSON-RPC writes) | prompt context |
| Tag contract | `ssot/azure/tagging-standard.yaml` v3 (17 required tags) | prompt context |
| Backup tier tag | `backup_tier: critical` | prompt context |

---

## 1. Production readiness checklist for `pg-ipai-odoo`

Each row: [MS Learn recommendation] + [IPAI state] + [URL]. "State" is `DONE`, `IN-PROGRESS`, or `NOT-STARTED` per evidence I have; items flagged `UNVERIFIED` are inferred from memory and should be re-checked with `az postgres flexible-server show`.

| # | Item | MS Learn recommendation | IPAI state | Source URL |
|---|---|---|---|---|
| 1 | Pick right compute tier & SKU | "Pick the right tier and SKU … Azure Advisor provides rightsizing" | DONE (General Purpose chosen; Burstable rejected because Fabric mirroring requires GP/MO) | https://learn.microsoft.com/azure/well-architected/service-guides/postgresql#cost-optimization ; https://learn.microsoft.com/fabric/mirroring/azure-database-postgresql#network-requirements |
| 2 | Configure zone-redundant High Availability | Enable HA (same-zone or zone-redundant) for production workloads | **UNVERIFIED** — not confirmed in memory. If off, this is a P1 gap for `backup_tier: critical`. | https://learn.microsoft.com/azure/well-architected/service-guides/postgresql |
| 3 | Use Private Link / private endpoint | "Connect to your databases over Azure Private Link" | DONE (private-endpoint-only) | https://learn.microsoft.com/azure/postgresql/network/concepts-networking-private-link |
| 4 | Enforce Microsoft Entra ID authentication | "Use Microsoft Entra ID for authentication and authorization to enhance identity management" | IN-PROGRESS — Entra admins set; MI for service workloads partial. See Section 2. | https://learn.microsoft.com/azure/postgresql/security/security-entra-configure |
| 5 | Enable PgBouncer (built-in) | "Enable support for PgBouncer to optimize connection pooling" | NOT-STARTED (prompt: "currently OFF, target ON for prod") | https://learn.microsoft.com/azure/postgresql/connectivity/concepts-pgbouncer |
| 6 | Enable Query Store | "Use query store to track query performance over time" | UNVERIFIED | https://learn.microsoft.com/azure/postgresql/well-architected#performance-efficiency |
| 7 | Enable Query Performance Insight | "Identify top resource-consuming and long-running queries" | UNVERIFIED | https://learn.microsoft.com/azure/postgresql/well-architected#performance-efficiency |
| 8 | Enable index tuning + intelligent tuning | "Use index tuning with query store" / "Use intelligent tuning" | UNVERIFIED | https://learn.microsoft.com/azure/postgresql/well-architected#performance-efficiency |
| 9 | Backup retention aligned to criticality | 7-35 days; critical workloads trend to 35 | UNVERIFIED; with `backup_tier: critical` tag expectation is max (35) | https://learn.microsoft.com/azure/postgresql/backup-restore/concepts-backup-restore#moving-from-other-backup-storage-options-to-geo-redundant-backup-storage |
| 10 | Geo-redundant backup storage | "Only configurable at server creation" — pick GRS for DR | **UNVERIFIED** — if not enabled at creation it cannot be added later. Requires dump+restore to new server if missing. | https://learn.microsoft.com/azure/postgresql/backup-restore/concepts-backup-restore#moving-from-other-backup-storage-options-to-geo-redundant-backup-storage |
| 11 | Row-level security & connection throttling | "Configure row-level security"; "Enable `connection_throttling`" | NOT-STARTED at server parameter layer (Odoo enforces at ORM) | https://learn.microsoft.com/azure/well-architected/service-guides/postgresql#security |
| 12 | Logical replication (`wal_level=logical`) for Fabric mirroring | Required prerequisite for `azure_cdc` | DONE (Fabric mirroring active implies this) | https://learn.microsoft.com/azure/postgresql/integration/concepts-fabric-mirroring#prerequisites |
| 13 | System-assigned Managed Identity (SAMI) | Required for Fabric mirroring; also used for `azure_storage`, `azure_ai` | DONE (Fabric mirroring active confirms SAMI on) | https://learn.microsoft.com/azure/postgresql/security/security-managed-identity-overview#uses-of-managed-identities-in-azure-database-for-postgresql |
| 14 | Regular security audit + MS baseline review | Review the security baseline | NOT-STARTED (no audit evidence in repo) | https://learn.microsoft.com/security/benchmark/azure/baselines/azure-database-for-postgresql-flexible-server-security-baseline |
| 15 | Stay current on PG major versions | "Latest versions come with in-place upgrade" | DONE on PG 16 (PG 17, 18 now available — no action required until 16 EOL) | https://learn.microsoft.com/azure/postgresql/configure-maintain/how-to-perform-major-version-upgrade |

### Summary
- **Done (5)**: Tier, Private Link, logical replication, SAMI, major version currency.
- **In-progress (1)**: Entra MI for services (Section 2).
- **Not-started (3)**: PgBouncer, RLS/connection throttling at server layer, security-baseline audit.
- **Unverified (6)**: HA, Query Store, QPI, index tuning, retention, geo-redundant backup. These are checkable with `az postgres flexible-server show --resource-group <rg> --name pg-ipai-odoo -o json` and `az postgres flexible-server parameter list …`.

---

## 2. Entra Managed Identity auth wiring (service workloads only)

**Doctrine**: For `ipai-odoo-mcp`, `ipai-odoo-connector`, and any Azure Function / Container App that talks to `pg-ipai-odoo`, use Entra MI + short-lived access token in the `password` field. No stored passwords for service principals.

### 2.1 Server-side: enforce MI-only auth mode

Portal / CLI: set **Authentication** to `Microsoft Entra authentication only` (the stricter of the two modes offered by Flexible Server).

> Source: https://learn.microsoft.com/azure/postgresql/security/security-entra-configure#prerequisites
>
> "In the Azure portal, during server provisioning, select either **PostgreSQL and Microsoft Entra authentication** or **Microsoft Entra authentication only** as the authentication method."

Caveat per Microsoft: you can also set this post-creation via **Security → Authentication**. An Entra admin (user, group, service principal, **or** managed identity) must exist before switching to MI-only — otherwise you lock yourself out.

### 2.2 Create one DB role per consumer MI

Connect as the Entra admin and create a PG role that maps to each consumer's MI:

```sql
-- Run in the `postgres` database (not the target DB)
select * from pgaadauth_create_principal('mi-ipai-odoo-mcp',      false, false);
select * from pgaadauth_create_principal('mi-ipai-odoo-connector',false, false);
```

Then in the target DB (`odoo`, `odoo_dev`, `odoo_staging`), grant schema-scoped privileges — not superuser:

```sql
-- In odoo database
GRANT CONNECT ON DATABASE odoo TO "mi-ipai-odoo-mcp";
GRANT USAGE ON SCHEMA public, ops, platform TO "mi-ipai-odoo-mcp";
GRANT SELECT ON ALL TABLES IN SCHEMA public, ops, platform TO "mi-ipai-odoo-mcp";   -- read-only MCP
-- write MI for the connector
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public, ops TO "mi-ipai-odoo-connector";
```

> Source: https://learn.microsoft.com/azure/postgresql/security/security-connect-with-managed-identity#create-an-azure-database-for-postgresql-user-for-your-managed-identity

### 2.3 Client-side: token acquisition

Two options. For MCP/connector running on ACA, use managed-identity token endpoint (IMDS):

- Endpoint: `http://169.254.169.254/metadata/identity/oauth2/token`
- Params: `api-version=2018-02-01`, `resource=https://ossrdbms-aad.database.windows.net`, `client_id=<MI client id>`

> Source: https://learn.microsoft.com/azure/postgresql/security/security-connect-with-managed-identity#retrieve-the-access-token-from-the-azure-instance-metadata-service

For Python (psycopg2/psycopg3) the canonical pattern:

```python
from azure.identity import DefaultAzureCredential  # or ManagedIdentityCredential with client_id
import psycopg
cred = DefaultAzureCredential()
token = cred.get_token("https://ossrdbms-aad.database.windows.net/.default").token
conn = psycopg.connect(
    host="pg-ipai-odoo.postgres.database.azure.com",
    dbname="odoo",
    user="mi-ipai-odoo-mcp",
    password=token,          # the access token, not a static password
    sslmode="require",
)
```

Token expires (default ~60 min); refresh before reconnecting. Pooled connections must rotate token at pool-refill time.

> Microsoft documents the token-as-password pattern here: https://learn.microsoft.com/azure/postgresql/security/security-entra-configure#use-a-token-as-a-password-for-signing-in-with-client-psql

### 2.4 Bicep module requirements

Minimum for MI-only prod:

```bicep
resource pg 'Microsoft.DBforPostgreSQL/flexibleServers@2023-12-01-preview' = {
  name: 'pg-ipai-odoo'
  location: 'southeastasia'
  sku: { name: 'Standard_D2ds_v5', tier: 'GeneralPurpose' }  // example; match current SKU
  identity: { type: 'SystemAssigned' }   // required for Fabric mirroring, azure_storage, azure_ai
  properties: {
    version: '16'
    authConfig: {
      activeDirectoryAuth: 'Enabled'
      passwordAuth: 'Disabled'           // strict MI-only
      tenantId: subscription().tenantId
    }
    network: {
      // no publicNetworkAccess here → private endpoint only
      delegatedSubnetResourceId: null     // using PE model, not VNet injection
    }
    highAvailability: { mode: 'ZoneRedundant' }    // fix #2 above
    backup: { backupRetentionDays: 35, geoRedundantBackup: 'Enabled' }  // fix #9, #10
  }
}

resource entraAdmin 'Microsoft.DBforPostgreSQL/flexibleServers/administrators@2023-12-01-preview' = {
  parent: pg
  name: '<object-id-of-admin-group>'
  properties: {
    principalType: 'Group'   // recommended over single-user admin
    principalName: 'sg-ipai-pg-admins'
    tenantId: subscription().tenantId
  }
}
```

Microsoft explicitly flags the dependency-ordering issue: "To have Microsoft Entra principals take ownership of the user databases in any deployment procedure, add explicit dependencies within your deployment (Terraform or Azure Resource Manager) module to ensure that Microsoft Entra authentication is turned on before you create any user databases."

> Source: https://learn.microsoft.com/azure/postgresql/security/security-entra-concepts#limitations-and-considerations

### 2.5 Network prerequisite for Entra admin ops on private PG

Because Entra is multi-tenant SaaS, the PG server needs outbound to `AzureActiveDirectory` service tag:
- NSG: outbound allow → `AzureActiveDirectory`
- If UDR used: `AzureActiveDirectory` → next hop `Internet`
- If custom DNS: `login.microsoftonline.com` and `graph.microsoft.com` must resolve publicly

> Source: https://learn.microsoft.com/azure/postgresql/security/security-entra-configure#prerequisites

### 2.6 Deleted-principal gotcha

If an Entra user/MI is deleted, the PG role remains but can no longer obtain tokens. For up to 60 minutes the already-issued token still works unless the role is also dropped. Rotation doctrine: when retiring a service, drop its PG role before deleting the MI.

> Source: https://learn.microsoft.com/azure/postgresql/security/security-entra-concepts#limitations-and-considerations

### 2.7 IPAI gap vs. MS best practice

| Aspect | MS best practice | IPAI current | Gap / action |
|---|---|---|---|
| `passwordAuth` | `Disabled` for stricter posture | Unknown; likely `Enabled` because Odoo itself connects with a DB password baked into `odoo.conf` | Migrate Odoo connection to MI via `ipai_auth_*` bridge, OR keep dual auth with Odoo password kept in Key Vault and service workloads on MI-only |
| Admin identity | Group, not single user | Unknown | Create `sg-ipai-pg-admins` Entra group, make it the admin |
| MI per consumer | One role per service MI | `ipai-odoo-mcp` and `ipai-odoo-connector` both need distinct roles | Create two roles with least-privilege grants (see 2.2) |

---

## 3. Private endpoint + VNet integration

### 3.1 Two distinct networking modes (important for IPAI)

Flexible Server has **two mutually exclusive** networking topologies:

| Mode | How | When to use |
|---|---|---|
| **Private access (VNet integration / VNet injection)** | Server NIC injected into a delegated subnet | Single-VNet scenarios, preferred when everything already lives in one VNet |
| **Public access + Private endpoint** | Server is a Private Link service; PE dropped into any consumer VNet | Multi-VNet, cross-subscription, hub-and-spoke |

> Source: https://learn.microsoft.com/azure/postgresql/network/concepts-networking-private and https://learn.microsoft.com/azure/postgresql/network/concepts-networking-private-link

Per prompt context, IPAI uses **private endpoint** (not VNet injection). This is the Microsoft-recommended alternative and is required if the pg server ever needs to be reachable from multiple VNets.

### 3.2 Required private DNS zone

For Private Link mode, the canonical zone is:

```
privatelink.postgres.database.azure.com
```

The PE registration name is a DNS `A` record inside that zone that resolves `pg-ipai-odoo.postgres.database.azure.com` → private IP.

> Source (portal default is exactly this zone name): https://learn.microsoft.com/azure/postgresql/network/how-to-networking-servers-deployed-public-access-add-private-endpoint — "Private DNS zone: Automatically set for you to `privatelink.postgres.database.azure.com`."

**Not** `postgres.database.azure.com` — that zone is for **VNet-injection** mode (which IPAI is not using).

### 3.3 Subnet delegation requirements

- **Private endpoint mode (IPAI)**: No subnet delegation required on the PE host subnet. It just needs a free /28+ address space and `privateEndpointNetworkPolicies` handled appropriately.
- **VNet-injection mode (not IPAI)**: Subnet must be delegated to `Microsoft.DBforPostgreSQL/flexibleServers` and cannot host other services.

> Source: https://learn.microsoft.com/azure/postgresql/network/concepts-networking-private — "Delegated subnet: … You deploy Azure resources into specific subnets within a virtual network."

### 3.4 Reaching it from ACA in a different VNet

ACA in `rg-ipai-dev-odoo-runtime` (env `ipai-odoo-dev-env-v2`) is in its own VNet. To reach the PE in the DB VNet:

1. **VNet peering** between ACA env VNet and DB VNet.
2. **Link the private DNS zone** `privatelink.postgres.database.azure.com` to the **ACA VNet** (not just the DB VNet) so that ACA-side resolvers return the PE's private IP.
3. **NSG** on ACA subnet: allow outbound to the PE IP on 5432 (and 6432 once PgBouncer is on).
4. No UDR / NVA needed unless hub-spoke.

> Source pattern (migration-service scenario, same DNS topology): https://learn.microsoft.com/azure/postgresql/migrate/migration-service/how-to-network-setup-migration-service#postgresql-source-private-ip-to-flexible-server-private-endpoint — "Ensure that both the VNets for the source and the target flexible server are linked to the private DNS zone."

### 3.5 RBAC split (important for IPAI 2-subscription model)

Microsoft documents that deploying a PE requires `Microsoft.Network/privateEndpoints/write` at the subnet and target scope, while PE-connection **approval** on the PG side requires `Microsoft.DBforPostgreSQL/flexibleServers/privateEndpointConnectionsApproval/action`. In enterprise splits the network team creates the PE and the DBA team approves it.

> Source: https://learn.microsoft.com/azure/postgresql/network/how-to-networking-servers-deployed-public-access-approve-private-endpoint

For IPAI the sub migration (Subscription 1 → Sponsored) is likely to force a PE re-create — see Section 7.

---

## 4. Fabric mirroring

### 4.1 Prerequisites (all required)

| # | Prerequisite | How | Source |
|---|---|---|---|
| 1 | Source tier is GP or Memory Optimized — **not Burstable** | Select at create time; changing tier later is a restart | https://learn.microsoft.com/fabric/mirroring/azure-database-postgresql#network-requirements |
| 2 | System-assigned Managed Identity on | Portal → Security → Identity → System assigned = On | https://learn.microsoft.com/azure/postgresql/security/security-managed-identity-overview |
| 3 | `wal_level = logical` | Server parameter; requires restart | https://learn.microsoft.com/azure/postgresql/integration/concepts-fabric-mirroring#prerequisites |
| 4 | `max_worker_processes` increased by +3 per mirrored DB | Server parameter; requires restart | ibid |
| 5 | `azure_cdc` extension allowlisted + preloaded | Server parameters `azure.extensions` and `shared_preload_libraries`; requires restart | ibid |
| 6 | Fabric capacity active (not paused) | `fcipaidev` — currently active per `project_fabric_finance_ppm.md` | https://learn.microsoft.com/fabric/mirroring/azure-database-postgresql-tutorial#prerequisites |
| 7 | Two Fabric tenant settings on | "Service principals can use Fabric APIs" + "Users can access OneLake externally" | ibid |
| 8 | Fabric workspace membership | User enabling mirroring must be **Member or Admin** of workspace (Contributor lacks Reshare) | ibid |
| 9 | Fabric-side connection role | Entra role or local PG role with `azure_cdc_admin` + `CREATE` on target DB + owner of tables | https://learn.microsoft.com/azure/postgresql/integration/concepts-fabric-mirroring#create-a-database-role-for-fabric-mirroring |
| 10 | Network reachability | Fabric VNet data gateway OR public/Azure-services bypass on PG OR PE reachable from gateway | https://learn.microsoft.com/fabric/mirroring/azure-database-postgresql#network-requirements |
| 11 | No read replica on primary | "Fabric Mirroring is not supported on a Read Replica, or on a Primary server where a Read Replica exists." | https://learn.microsoft.com/fabric/mirroring/azure-database-postgresql-tutorial#prerequisites |

### 4.2 Automated enablement page

Microsoft ships an in-portal automation on the PG server blade that configures items 3, 4, 5 (and prompts a restart). For IPAI this has already been run.

> Source: https://learn.microsoft.com/azure/postgresql/integration/concepts-fabric-mirroring#prerequisites — "A new page is available in the Azure portal to automate these prerequisite configurations."

### 4.3 Architecture (what actually happens)

1. `azure_cdc` background process takes an initial **snapshot** of selected tables → ships as Parquet to OneLake landing zone (signed with PG's SAMI).
2. Fabric replicator converts Parquet → **Delta** tables in the mirrored DB artifact.
3. Subsequent changes captured via **logical replication**, shipped as batched deltas.

> Source: https://learn.microsoft.com/azure/postgresql/integration/concepts-fabric-mirroring

### 4.4 Latency expectations

Microsoft does not publish a hard SLA for Fabric mirroring latency on Azure DB for PostgreSQL. The architecture is near-real-time (logical replication stream, batched to OneLake), but end-to-end lag depends on:
- Source WAL generation rate
- Source CPU/IOPS headroom (snapshot phase is heavy)
- Fabric capacity available SKU
- Size of each change batch

**Honest statement**: I do not have a documented latency number. Do not quote minute-level figures; monitor empirically via the Fabric mirrored-database monitoring view.

### 4.5 Failover behavior

From Microsoft: "Mirroring supports highly available Azure Database for PostgreSQL flexible server configurations. Replication continues seamlessly across failover events without requiring additional configuration."

> Source: https://learn.microsoft.com/fabric/mirroring/azure-database-postgresql#network-requirements

However — if SAMI is disabled or removed, mirroring fails: "After enabling the SAMI, if the SAMI is disabled or removed, the mirroring of Azure Database for PostgreSQL flexible server to Fabric OneLake will fail."

> Source: https://learn.microsoft.com/fabric/mirroring/azure-database-postgresql-how-to-data-security#security-requirements

### 4.6 WAL growth risk

Long-running transactions will pin WAL until commit/abort AND until the mirror catches up. If either the source or the mirror stalls, WAL can fill up storage. Monitor `Transaction Log Storage Used` metric.

> Source: https://learn.microsoft.com/azure/postgresql/flexible-server/concepts-logical#monitor

**IPAI-specific note**: This is a real concern because Odoo has cron jobs that open long transactions (e.g., large account reconciliation runs). Tag `backup_tier: critical` means we should alert on `txlogs_storage_used` > 50% of provisioned storage.

### 4.7 IPAI gap vs MS best practice

| Aspect | MS expected | IPAI current | Gap |
|---|---|---|---|
| Fabric role | Entra role preferred; local `fabric_user` only fallback | Unknown which is in use | Document which; prefer Entra |
| WAL storage alert | Monitor proactively | No alert documented | Add `txlogs_storage_used` alert (>50%) |
| No read replica on primary | Required | OK — no replica | Keep constraint if planning replicas later |

---

## 5. Vector search + pgvector for Pulser / IPAI AI features

### 5.1 When to use pgvector vs Azure AI Search

Microsoft positions pgvector/DiskANN as the **colocated-with-data** option — best when your vectors logically belong next to OLTP rows:

> "When you're using Azure Database for PostgreSQL as a vector store, you can store, index, and query embeddings alongside the original data. This approach eliminates the extra cost of replicating data in a separate, pure vector database."
>
> Source: https://learn.microsoft.com/azure/postgresql/azure-ai/generative-ai-vector-databases#how-does-a-vector-store-work

Decision heuristic for IPAI:

| Use case | Recommendation | Rationale |
|---|---|---|
| Semantic search over Odoo business records (invoices, contracts, partners) — ranked beside structured filters (company_id, date ranges) | **pgvector in `pg-ipai-odoo`** | Joins with Odoo tables; stays under multitenant `res.company` boundary |
| PrismaLab RAG corpus (systematic review literature) | **Azure AI Search** (already `prismalab-rag-v1` on `srch-ipai-dev`) | Hybrid BM25+vector + semantic reranker is AI Search's sweet spot |
| Pulser agent conversation memory | **pgvector in `ops` schema** | Already colocated with agent state |
| Large-corpus enterprise knowledge (>10M chunks) | **Azure AI Search** | Better horizontal scale story |

### 5.2 DiskANN vs HNSW vs IVFFlat

Three supported index types on Flexible Server:

| Algorithm | Speed-recall | Build time | Memory | Extension | Notes |
|---|---|---|---|---|---|
| **IVFFlat** (pgvector) | Lower | Fast | Low | `pgvector` | Requires data loaded before building; legacy |
| **HNSW** (pgvector) | Better | Slower | Higher | `pgvector` | Max 2000 dims |
| **DiskANN** (`pg_diskann`) | Best balance | Fast | Disk-friendly | `pg_diskann` (Azure) | Up to **16,000 dims** with Product Quantization |

> Source: https://learn.microsoft.com/azure/postgresql/extensions/how-to-optimize-performance-pgvector#indexing
> Source: https://learn.microsoft.com/azure/postgresql/extensions/how-to-use-pgdiskann#scale-efficiently-with-quantization-preview

**Decision for IPAI**:
- Embeddings dim ≤ 2000 and corpus ≤ 1M → HNSW is fine.
- Using `text-embedding-3-small` (1536 dims) → HNSW works. Using `text-embedding-3-large` (3072 dims) or Cohere-large (>2000 dims) → **must use DiskANN with quantization** because pgvector's HNSW is capped at 2000 dims.
- Large corpus + disk-backed index + fast build → **DiskANN**.

### 5.3 Integration pattern with Foundry gpt-4.1 + text-embedding-3-small

IPAI has:
- Foundry: `ipai-copilot-resource` (East US 2) with gpt-4.1 and `text-embedding-3-small`
- PG: `pg-ipai-odoo` (SEA) — **cross-region** to Foundry

The Microsoft-blessed colocated pattern uses the `azure_ai` extension to call Azure OpenAI **from inside** the database:

```sql
-- One-time per DB
CREATE EXTENSION IF NOT EXISTS azure_ai;
CREATE EXTENSION IF NOT EXISTS vector;

-- Configure endpoint (requires azure_ai_admin or similar)
SELECT azure_ai.set_setting('azure_openai.endpoint', 'https://ipai-copilot-resource.openai.azure.com/');
-- Auth: prefer SAMI (see Section 2); avoid API key

-- At write time: embed + store
INSERT INTO ops.doc_chunks(doc_id, chunk, embedding)
VALUES ($1, $2, azure_openai.create_embeddings('text-embedding-3-small', $2)::vector);

-- Index (HNSW, 1536 dims — fits)
CREATE INDEX ON ops.doc_chunks USING hnsw (embedding vector_cosine_ops);

-- Query
SELECT doc_id, chunk
FROM ops.doc_chunks
ORDER BY embedding <=> azure_openai.create_embeddings('text-embedding-3-small', $1)::vector
LIMIT 5;
```

> Source: https://learn.microsoft.com/azure/postgresql/integration/how-to-integrate-azure-ai#generate-vector-embeddings-with-azure-openai
> Source: https://learn.microsoft.com/azure/postgresql/azure-ai/generative-ai-enable-managed-identity-azure-ai

**Important IPAI caveat**: Calling Azure OpenAI from inside the DB requires the DB's SAMI to have `Cognitive Services OpenAI User` on `ipai-copilot-resource` AND network reachability. Since PG is private-endpoint-only, you need:
- Either `azure_ai` calls egress via an AOAI private endpoint reachable from the PG subnet, or
- AOAI public endpoint allowed (less preferred).

Alternative: do embeddings **outside** the DB (in `ipai-odoo-mcp` on ACA) and INSERT the vectors. This is simpler, more auditable, and the pattern I recommend for IPAI since the MCP already has Foundry access.

### 5.4 HNSW tuning quick reference

- Index: `CREATE INDEX … USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=64);`
- Query-time: `SET hnsw.ef_search = 100;` (default 40). Higher = better recall, slower.

> Source: https://learn.microsoft.com/azure/postgresql/extensions/how-to-optimize-performance-pgvector#indexing

### 5.5 Choosing the operator

| Distance | Operator | Op class |
|---|---|---|
| Cosine (recommended for OpenAI embeddings) | `<=>` | `vector_cosine_ops` |
| L2 / Euclidean | `<->` | `vector_l2_ops` |
| Inner product | `<#>` | `vector_ip_ops` |

> Source: https://learn.microsoft.com/azure/postgresql/extensions/how-to-optimize-performance-pgvector#selecting-the-index-access-function

---

## 6. Backup, PITR, geo-restore, and DR

### 6.1 What `backup_tier: critical` implies for IPAI

The tag `backup_tier: critical` is an IPAI SSOT label (`ssot/azure/tagging-standard.yaml` v3). It is **not** an Azure-native property — it is a policy input that Bicep/Terraform and ops runbooks read to derive real Azure settings. The mapping most consistent with Microsoft's backup doc is:

| IPAI tag | Recommended Azure settings |
|---|---|
| `backup_tier: critical` | `backupRetentionDays: 35` (max), `geoRedundantBackup: Enabled`, HA: ZoneRedundant, quarterly DR drill |

Microsoft confirms:
- Retention is `7-35 days` (default 7).
- Geo-redundancy can **only** be configured at server creation — cannot be changed after.

> Source: https://learn.microsoft.com/azure/postgresql/backup-restore/concepts-backup-restore#moving-from-other-backup-storage-options-to-geo-redundant-backup-storage

**IPAI risk flag**: If `pg-ipai-odoo` was not created with GRS enabled, achieving `backup_tier: critical` intent requires a **dump+restore to a new GRS-enabled server**. Verify now:
```bash
az postgres flexible-server show --resource-group <rg> --name pg-ipai-odoo \
  --query 'backup' -o json
```

### 6.2 Retention + PITR window

- Retention = PITR window. With 35 days, you can restore to any point in the last 35 days.
- Backups continue to be retained on **stopped** servers.
- Snapshot + WAL architecture: PITR first restores the nearest full backup, then replays WAL up to the target point.

> Source: https://learn.microsoft.com/azure/postgresql/backup-restore/concepts-backup-restore#point-in-time-recovery

### 6.3 PITR modes (3 variants, IPAI-usable)

| Mode | Use when | CLI |
|---|---|---|
| Latest restore point | "Restore now" | `az postgres flexible-server restore` (omit `--restore-time`) |
| Custom restore point | Specific timestamp (accidental drop, bad migration) | `--restore-time '2026-04-14T10:00:00Z'` |
| Fast restore (full backup only) | Fastest; skips WAL replay, restores to a full-backup point | `--restore-time` mapped to backup timestamp |

> Source: https://learn.microsoft.com/azure/postgresql/backup-restore/concepts-backup-restore#point-in-time-recovery (list of restore modes)

**PITR always creates a NEW server** with a new name. It does NOT overwrite the source. Plan a DNS/connection-string cutover as part of recovery.

### 6.4 Geo-restore to paired region (SEA ↔ East Asia)

Azure region pair for Southeast Asia = **East Asia**. To geo-restore:

```bash
az postgres flexible-server geo-restore \
  --resource-group rg-ipai-dr \
  --name pg-ipai-odoo-dr \
  --source-server /subscriptions/<sub>/resourceGroups/<src-rg>/providers/Microsoft.DBforPostgreSQL/flexibleServers/pg-ipai-odoo \
  --location eastasia
```

> Source: https://learn.microsoft.com/azure/postgresql/backup-restore/how-to-restore-paired-region#steps-to-restore-to-paired-region-geo-restore

Prerequisites (mandatory): `geoRedundantBackup: Enabled` at the source server. If not enabled, geo-restore is not available — this is the hard gate for IPAI's DR posture.

### 6.5 DR drill recommendation (not in MS doc, IPAI-specific)

Microsoft doesn't prescribe a cadence. For `backup_tier: critical`, a quarterly geo-restore drill that reaches "Odoo boots, login works, BIR-critical module loads" is the minimum defensible bar.

### 6.6 Backup storage cost gotcha

- First 100% of provisioned storage = free backup storage.
- Beyond that = $/GB/month.
- With GRS enabled, billing = `(2 × local_backup) - provisioned_storage`.
- Heavy WAL generation (e.g., large Odoo reconciliations, Fabric mirror lag) inflates backup size irrespective of DB size.

> Source: https://learn.microsoft.com/azure/postgresql/backup-restore/concepts-backup-restore#moving-from-other-backup-storage-options-to-geo-redundant-backup-storage

Watch metric: `backup_storage_used`.

---

## 7. Subscription migration path (Sub 1 → Sponsored)

### 7.1 Is cross-subscription move supported natively?

**Yes.** Microsoft's authoritative resource-move matrix lists:

| Resource type | Resource group | Subscription | Region move |
|---|---|---|---|
| `Microsoft.DBforPostgreSQL/flexibleServers` | **Yes** | **Yes** | No |

> Source: https://learn.microsoft.com/azure/azure-resource-manager/management/move-support-resources#microsoftdbforpostgresql

This aligns with ADR-002's choice of "A/no/safe-first, PG native-move, DNS stays, stateless redeploy first" (see `project_sponsored_sub_migration_adr.md`).

### 7.2 Hard constraints on the native move

Native resource-move (`Move-AzResource` / `az resource move`) has these enforced rules:

1. **Same tenant required** — source and destination subscription must share the same Microsoft Entra tenant. If IPAI's Sponsored sub is in a different tenant, native move is **not** available; fall back to dump+restore.
   > Source: https://learn.microsoft.com/azure/azure-resource-manager/management/move-resources-overview
2. **Resource types in a single move call must all support sub-move** at the relevant level.
3. **Dependent resources often move together** — PE connections on the PG side are tied to the server; the **PE resources themselves** (in consumer subscriptions) typically do **not** move and may need recreation. Private DNS zones are separate resources with their own rules.
4. **Downtime**: The move is essentially a control-plane re-registration; Microsoft does not publish a guaranteed zero-downtime SLA for the data plane during the move. Schedule as a maintenance window.

### 7.3 Region relocation is a different beast

The same matrix shows **Region move: No** for `flexibleServers`. For cross-region relocation (not IPAI's current case), Microsoft publishes a dedicated guide that uses dump+restore, not native move:

> Source: https://learn.microsoft.com/azure/azure-resource-manager/management/relocation/relocation-postgresql-flexible-server#redeploy-with-data

### 7.4 Fallback: pg_dump + pg_restore path

If native move fails (tenant mismatch, policy block, HA constraints), use the Microsoft-documented dump+restore pattern:

Key recommendations from the MS Learn "Best practices for pg_dump and pg_restore" doc:

| Knob | Value | Why |
|---|---|---|
| Source for dump | **PITR clone** of prod, not prod itself | Avoids CPU/IO impact on live server |
| `maintenance_work_mem` | Up to `2 GB` | Faster index build during restore |
| `max_parallel_maintenance_workers` | Up to 4 | Parallel index creation |
| `pg_dump --jobs` | Equal to or less than source vCores | Parallel table dump |
| Higher vCore SKU on target for restore | Yes | Bandwidth + CPU for faster restore |
| Disable HA on target during load | Yes | Avoid double-write overhead during bulk load |
| Create read replicas AFTER load | Yes | Same reason |
| Post-restore: revert parameters | Yes | Those are load-tuning values, not steady-state |

> Source: https://learn.microsoft.com/azure/postgresql/troubleshoot/how-to-pgdump-restore#best-practices-for-pg_dump
> Source: https://learn.microsoft.com/azure/postgresql/troubleshoot/how-to-bulk-load-data#best-practices-for-initial-data-loads

For online/near-zero-downtime dumps, use the **Azure Database for PostgreSQL Migration Service**:

> Source: https://learn.microsoft.com/azure/postgresql/migrate/migration-service/overview-migration-service-postgresql

Supported online sources include on-prem, IaaS VM, RDS, Aurora, Cloud SQL, AlloyDB, EDB, and Flexible Server itself. For a sub-to-sub on Flexible Server, the migration service can work as an online tool even though the intended use is cloud-to-cloud; validate in staging.

### 7.5 Which parts of the stack re-point vs. stay

| Component | Behavior on sub move |
|---|---|
| Server FQDN `pg-ipai-odoo.postgres.database.azure.com` | **Stays** — FQDN is tied to server name + public DNS record, not subscription |
| Private endpoint in **consumer** VNet | Likely needs recreation in the new sub (PE is its own resource; MS does not guarantee a cross-sub PE move) |
| `privatelink.postgres.database.azure.com` zone | Stays in whichever sub owns it; link the new-sub VNet |
| Managed Identity principal IDs | SAMI object IDs **change** when MI is recreated (see Fabric mirroring caveat) |
| Fabric mirroring | Breaks if SAMI is deleted/recreated during move; re-enable |
| Entra admin group | Unchanged |
| Backups | Stay with the server (server itself moves; its backups go with it) |

**Honest uncertainty**: The exact behavior of SAMI during subscription move is not cleanly documented in a single MS Learn page I found. Test in staging before attempting prod move. If SAMI cycles, Fabric mirroring must be re-initialized and every `pgaadauth_create_principal` MI-based role must be re-bound.

### 7.6 IPAI-specific execution order

1. Take PITR clone in Sub 1 → validate restore works.
2. Confirm tenant equality between Sub 1 and Sponsored sub.
3. Snapshot of: backup retention, HA config, all server parameters, all firewall/PE approvals, Entra admin list, PG roles with Entra binding.
4. Notify stakeholders; window the move.
5. Attempt `az resource move --ids <pg> --destination-subscription-id <sponsored>`.
6. If successful: re-approve PE connections, re-link private DNS zone from consumer VNets, re-test Fabric mirroring (may require SAMI re-grant), rotate MCP MI role bindings.
7. If failed: fall back to dump+restore on a fresh server in Sponsored sub, then DNS/connection-string cutover.

---

## 8. Monitoring + troubleshooting playbook

### 8.1 Canonical Azure Monitor metrics (default-enabled)

| Display name | Metric ID | Alert trigger recommendation for IPAI |
|---|---|---|
| Read IOPS | `read_iops` | >80% of provisioned IOPS for 5 min |
| Write IOPS | `write_iops` | >80% for 5 min |
| Storage percent | `storage_percent` | >80% |
| Storage Free | `storage_free` | absolute minimum 20 GiB |
| Transaction Log Storage Used | `txlogs_storage_used` | >50% of total storage (Fabric mirroring / long tx guard) |
| Network Out | `network_bytes_egress` | Baseline + alert on 3× deviation |
| Network In | `network_bytes_ingress` | Same |
| Read/Write Throughput | `read_throughput`/`write_throughput` | Same |

> Source: https://learn.microsoft.com/azure/postgresql/monitor/concepts-monitoring#metrics

Note: Microsoft flags "Metrics marked with ^ are emitted every minute but processed in five-minute batches" (the `iops`/`throughput` set). Build alerts with ≥5-min evaluation windows to avoid false negatives.

> Source: same URL

### 8.2 Enhanced metrics (opt-in)

Flexible Server exposes a larger set of **enhanced metrics** via the server parameter `metrics.collector_database_activity`. Not enabled by default — worth turning on for IPAI prod because the overhead is small and visibility is materially better.

> Source: https://learn.microsoft.com/azure/postgresql/server-parameters/concepts-server-parameters (non-engine parameters section mentioning `metrics.collector_database_activity`)

### 8.3 Server parameters to enable for slow-query tracing

| Parameter | Recommended IPAI value | Purpose | MS Learn |
|---|---|---|---|
| `pg_stat_statements.track` | `top` | Track top-level statements | https://learn.microsoft.com/azure/postgresql/server-parameters/param-customized-options |
| `pg_stat_statements.max` | `5000` (default) | Cap tracked statements | ibid |
| `pg_stat_statements.track_planning` | `on` | Plan-time tracking | ibid |
| `pg_stat_statements.save` | `on` (default) | Persist across restart | ibid |
| `pg_qs.query_capture_mode` | `all` or `top` | Query Store capture | https://learn.microsoft.com/azure/postgresql/monitor/concepts-query-store |
| `log_min_duration_statement` | `1000` ms | Log anything ≥ 1s | server parameters reference |
| `log_connections` / `log_disconnections` | `on` | Audit trail | ibid |
| `auto_explain.log_min_duration` | `5000` ms (opt-in extension) | EXPLAIN for very slow queries | ibid |
| `compute_query_id` | `on` (PG 14+) | Correlate `pg_stat_activity` ↔ `pg_stat_statements` | https://learn.microsoft.com/azure/postgresql/server-parameters/concepts-server-parameters |

### 8.4 Autovacuum & bloat watch

Odoo's multi-company workload generates significant row churn (stock.move, account.move.line, mail.message). Keep autovacuum visible:

- `autovacuum = on` (default; do not disable)
- `autovacuum_naptime` default 60s is fine for GP
- Monitor `n_dead_tup` via `pg_stat_user_tables` — alert on tables > 10% dead tuples
- For targeted bloat: `vacuum (analyze, verbose) <table>` before big index operations.

> Source: https://learn.microsoft.com/azure/postgresql/troubleshoot/how-to-autovacuum-tuning

### 8.5 Slow-query trace playbook

1. Get top-N by mean duration:
   ```sql
   SELECT queryid, calls, mean_exec_time, total_exec_time, rows, query
   FROM pg_stat_statements
   ORDER BY mean_exec_time DESC
   LIMIT 20;
   ```
2. For a specific `queryid`, correlate to current running sessions:
   ```sql
   SELECT pid, state, now()-query_start AS dur, query
   FROM pg_stat_activity WHERE query_id = <id>;
   ```
3. Use Query Store `azure_sys` DB:
   ```sql
   -- Top resource consumers, last 24h
   SELECT * FROM query_store.qs_view ORDER BY total_time DESC LIMIT 20;
   ```
4. Use `index_tuning` recommendations:
   ```sql
   SELECT * FROM IntelligentPerformance.DropIndexRecommendations;
   ```
   > Source: https://learn.microsoft.com/azure/postgresql/troubleshoot/how-to-bulk-load-data#best-practices-for-incremental-data-loads

### 8.6 Connection pressure — precursor to PgBouncer enable

Monitor:
- `active_connections` (enhanced metric)
- `max_connections` server parameter (scales with SKU)

If `active_connections / max_connections > 0.7` sustained, turn on built-in PgBouncer:

```bash
az postgres flexible-server parameter set -g <rg> -s pg-ipai-odoo \
  --name pgbouncer.enabled --value true
az postgres flexible-server parameter set -g <rg> -s pg-ipai-odoo \
  --name pgbouncer.pool_mode --value transaction   # default; best for Odoo
```

Then change Odoo's connection port from 5432 → 6432 in `odoo.conf` (or via env var `PGPORT=6432`).

> Source: https://learn.microsoft.com/azure/postgresql/connectivity/concepts-pgbouncer
> Source: https://learn.microsoft.com/azure/postgresql/server-parameters/param-pgbouncer (`pgbouncer.pool_mode` default = `transaction`)

**Odoo-specific caveat**: Odoo's ORM uses cursors in transaction-scoped ways that are compatible with PgBouncer **transaction** mode, but some Odoo admin tools (e.g. `pg_restore` from the odoo addon manager, backup cron) prefer a direct 5432 connection. Keep both ports open on the private endpoint.

### 8.7 Fabric mirroring health

Specific watch items:
- WAL retention lag (via logical replication slot): `SELECT slot_name, active, confirmed_flush_lsn FROM pg_replication_slots;`
- If any slot for `azure_cdc_*` is inactive for > X minutes — mirroring is stuck. Investigate.
- `txlogs_storage_used` metric (8.1) — proactive alarm.

> Source: https://learn.microsoft.com/azure/postgresql/flexible-server/concepts-logical#monitor

### 8.8 Azure Advisor + WAF

Regularly run Azure Advisor against the resource and resolve its PG-specific recommendations (rightsizing, security baseline drift, HA suggestions).

> Source: https://learn.microsoft.com/azure/well-architected/service-guides/postgresql

Use the Azure Security Baseline for Flexible Server as the audit rubric:
> https://learn.microsoft.com/security/benchmark/azure/baselines/azure-database-for-postgresql-flexible-server-security-baseline

---

## What we should do next (5 concrete action items)

1. **Verify + remediate backup posture** — run `az postgres flexible-server show -g <rg> -n pg-ipai-odoo --query 'backup' -o json`. If `geoRedundantBackup != "Enabled"` OR `backupRetentionDays < 35`, this is the biggest `backup_tier: critical` gap. Remediation for geo-redundancy requires dump+restore to a new server (it is create-time-only). Owner: data platform. ETA: before sub migration.

2. **Enforce MI-only auth for service workloads** — create Entra roles `mi-ipai-odoo-mcp` and `mi-ipai-odoo-connector` via `pgaadauth_create_principal`, grant schema-scoped (not superuser) privileges, update `ipai-odoo-mcp` and `ipai-odoo-connector` to acquire tokens via `DefaultAzureCredential`, and plan a path to set `passwordAuth: Disabled` (or keep dual-auth until Odoo core's DB connection is migrated). Cites: https://learn.microsoft.com/azure/postgresql/security/security-entra-configure

3. **Enable built-in PgBouncer in transaction mode** — set `pgbouncer.enabled=true`, `pgbouncer.pool_mode=transaction`, move Odoo to port 6432, keep 5432 open for backup tooling. Measure connection-count drop. Cites: https://learn.microsoft.com/azure/postgresql/connectivity/concepts-pgbouncer

4. **Add Azure Monitor alert rules for 3 WAL-critical signals** — `txlogs_storage_used > 50%`, `storage_percent > 80%`, `active_connections / max_connections > 70%` for 5 min. Ties into Fabric mirroring health and prevents storage-exhaustion outages during long Odoo reconciliations. Cites: https://learn.microsoft.com/azure/postgresql/monitor/concepts-monitoring#metrics

5. **Dry-run the subscription move in staging first** — on `odoo_staging` (or a PITR clone), execute `az resource move` from Sub 1 to Sponsored in a non-prod sub pair. Document SAMI object-id behavior (does it change? do Entra-bound PG roles need rebinding?), PE reconnection sequence, and Fabric mirroring recovery steps. This turns ADR-002's "native-move, safe-first" from a plan into a verified runbook. Cites: https://learn.microsoft.com/azure/azure-resource-manager/management/move-support-resources#microsoftdbforpostgresql

---

### Honest gap summary vs Microsoft's public documentation

| Topic | Microsoft docs clarity | Notes |
|---|---|---|
| Cross-sub move of Flexible Server | Clear — supported (matrix row) | Matrix confirms Yes |
| Cross-sub move of SAMI behavior during server move | **Not documented cleanly** | Test in staging; do not assume |
| Fabric mirroring end-to-end latency SLA | **Not published** | Monitor empirically |
| DR drill cadence | **Not prescribed** | IPAI-defined policy |
| `backup_tier: critical` → concrete Azure settings mapping | **Not documented** (it's an IPAI tag) | Defined in this pack; should codify in `ssot/azure/tagging-standard.yaml` |
| Odoo compatibility with PgBouncer transaction mode | Not in MS Learn; community-well-known | Verified empirically in Odoo community; safe for Odoo 18 |

---

### Referenced Microsoft Learn URLs (consolidated)

- https://learn.microsoft.com/azure/well-architected/service-guides/postgresql
- https://learn.microsoft.com/security/benchmark/azure/baselines/azure-database-for-postgresql-flexible-server-security-baseline
- https://learn.microsoft.com/azure/postgresql/security/security-entra-concepts
- https://learn.microsoft.com/azure/postgresql/security/security-entra-configure
- https://learn.microsoft.com/azure/postgresql/security/security-connect-with-managed-identity
- https://learn.microsoft.com/azure/postgresql/security/security-managed-identity-overview
- https://learn.microsoft.com/azure/postgresql/security/security-manage-entra-users
- https://learn.microsoft.com/azure/postgresql/network/concepts-networking-private
- https://learn.microsoft.com/azure/postgresql/network/concepts-networking-private-link
- https://learn.microsoft.com/azure/postgresql/network/how-to-networking-servers-deployed-public-access-add-private-endpoint
- https://learn.microsoft.com/azure/postgresql/network/how-to-networking-servers-deployed-public-access-approve-private-endpoint
- https://learn.microsoft.com/azure/postgresql/migrate/migration-service/how-to-network-setup-migration-service
- https://learn.microsoft.com/azure/postgresql/integration/concepts-fabric-mirroring
- https://learn.microsoft.com/fabric/mirroring/azure-database-postgresql
- https://learn.microsoft.com/fabric/mirroring/azure-database-postgresql-tutorial
- https://learn.microsoft.com/fabric/mirroring/azure-database-postgresql-how-to-data-security
- https://learn.microsoft.com/azure/postgresql/flexible-server/concepts-logical
- https://learn.microsoft.com/azure/postgresql/azure-ai/generative-ai-vector-databases
- https://learn.microsoft.com/azure/postgresql/azure-ai/generative-ai-azure-overview
- https://learn.microsoft.com/azure/postgresql/azure-ai/generative-ai-enable-managed-identity-azure-ai
- https://learn.microsoft.com/azure/postgresql/extensions/how-to-optimize-performance-pgvector
- https://learn.microsoft.com/azure/postgresql/extensions/how-to-use-pgdiskann
- https://learn.microsoft.com/azure/postgresql/integration/how-to-integrate-azure-ai
- https://learn.microsoft.com/azure/postgresql/backup-restore/concepts-backup-restore
- https://learn.microsoft.com/azure/postgresql/backup-restore/how-to-restore-paired-region
- https://learn.microsoft.com/azure/postgresql/backup-restore/how-to-restore-custom-restore-point
- https://learn.microsoft.com/azure/postgresql/backup-restore/how-to-restore-full-backup
- https://learn.microsoft.com/azure/azure-resource-manager/management/move-support-resources#microsoftdbforpostgresql
- https://learn.microsoft.com/azure/azure-resource-manager/management/move-resources-overview
- https://learn.microsoft.com/azure/azure-resource-manager/management/relocation/relocation-postgresql-flexible-server
- https://learn.microsoft.com/azure/postgresql/migrate/migration-service/overview-migration-service-postgresql
- https://learn.microsoft.com/azure/postgresql/troubleshoot/how-to-pgdump-restore
- https://learn.microsoft.com/azure/postgresql/troubleshoot/how-to-bulk-load-data
- https://learn.microsoft.com/azure/postgresql/troubleshoot/how-to-autovacuum-tuning
- https://learn.microsoft.com/azure/postgresql/monitor/concepts-monitoring
- https://learn.microsoft.com/azure/postgresql/monitor/concepts-query-store
- https://learn.microsoft.com/azure/postgresql/server-parameters/concepts-server-parameters
- https://learn.microsoft.com/azure/postgresql/server-parameters/param-customized-options
- https://learn.microsoft.com/azure/postgresql/server-parameters/param-pgbouncer
- https://learn.microsoft.com/azure/postgresql/connectivity/concepts-pgbouncer
- https://learn.microsoft.com/azure/postgresql/connectivity/concepts-connection-pooling-best-practices

---

---

*Last updated: 2026-04-15*
