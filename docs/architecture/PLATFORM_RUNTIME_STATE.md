# Platform Runtime State

> Canonical view of runtime infrastructure state across all platform planes.
> Updated: 2026-03-08

---

## Azure Subscription Runtime State

### Current state

Azure subscription 1 is already provisioned as an active AI/data platform substrate, not an empty or planning-only subscription. The current resource inventory includes Azure Databricks, Azure OpenAI, Azure AI Search, Document Intelligence, Computer Vision, Language, Key Vault, Application Insights, Log Analytics, managed identities, virtual networking, and a Databricks access connector.

### Resource posture

The current estate is development-weighted. Resource naming and grouping are centered on `*-dev`, including `rg-ipai-ai-dev`, `rg-ipai-shared-dev`, and `dbw-ipai-dev`. This indicates a real development landing zone rather than a promoted multi-environment runtime.

### Present in inventory

Core AI/data foundation presently visible in the subscription includes:

- Azure Databricks (`dbw-ipai-dev`)
- Azure OpenAI (`oai-ipai-dev`)
- Azure AI Search (`srch-ipai-dev`)
- Document Intelligence (`docai-ipai-dev`)
- Computer Vision (`vision-ipai-dev`)
- Language (`lang-ipai-dev`)
- Key Vault (`kv-ipai-dev`)
- Application Insights (`appi-ipai-dev`)
- Log Analytics (`managed-appi-ipai-dev-ws`)
- Virtual network (`vnet-ipai-databricks`)
- Network security group (`nsg-dbw-ipai-dev`)
- Databricks access connector (`unity-catalog-access-connector`)
- Multiple managed identities for agents and Databricks execution paths

### Not yet evidenced in current Azure inventory

The current resource inventory does not yet evidence a complete Azure-native Odoo runtime layer. The following target-state components are not presently visible in the exported subscription inventory:

- Azure-hosted Odoo application runtime
- Azure Database for PostgreSQL for Odoo
- Azure Container Registry
- Azure Front Door / WAF ingress layer
- explicit stage/prod Odoo runtime separation
- ERP-specific deployment promotion path

### Interpretation

Azure capability is not the blocker. The subscription already contains the foundations for AI, analytics, identity, observability, and network governance. The remaining gap is to elevate Odoo into a first-class Azure workload shape on top of that substrate.

### Positioning

SAP remains the ecosystem maturity benchmark on Azure, especially across data, analytics, AI, and Microsoft integration surfaces. Odoo is a broad business platform across Community and Enterprise editions, but unlike SAP it does not arrive with SAP-grade Azure ecosystem depth. The target state is therefore to engineer that workload posture explicitly through repo-owned architecture, IaC, CI/CD, observability, security, and governed integration layers.


---

## DigitalOcean Runtime State

See `DEPLOY_TARGET_MATRIX.md` and `PROD_RUNTIME_SNAPSHOT.md` for current DO droplet state.

---

## Supabase Runtime State

See `SUPABASE_CONTROL_PLANE.md` for current Supabase project state.

---

## Vercel Runtime State

See `VERCEL_CONTROL_PLANE_DEPLOYMENT.md` for current Vercel deployment state.
