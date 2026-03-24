# aca-private-networking

**Impact tier**: P0 -- Security Exposure

## Purpose

Close the network isolation gap where Azure Container Apps (ACA) hosting Odoo
communicate with PostgreSQL Flexible Server over public endpoints without NSG
restrictions or private endpoints. The benchmark audit found: no VNet
integration for ACA, no private endpoint for PG, no NSG rules restricting PG
access to the ACA subnet.

## When to Use

- Hardening network posture for Odoo runtime on Azure.
- Preparing for a security review or go-live gate.
- Responding to an audit finding about public database endpoints.

## Required Evidence (inspect these repo paths first)

| Path | What to look for |
|------|-----------------|
| `infra/azure/modules/vnet.bicep` | VNet definition, subnets, NSG rules |
| `infra/azure/modules/postgres-flexible.bicep` | Network properties, public access flag |
| `infra/azure/odoo-runtime.bicep` | ACA environment VNet integration |
| `infra/azure/main.bicep` | Module composition, parameter passing |
| `infra/ssot/azure/resources.yaml` | VNet and NSG resource entries |
| `docs/audits/ODOO_AZURE_ENTERPRISE_BENCHMARK.md` | Networking gap row |

## Microsoft Learn MCP Usage

Run at least these three queries:

1. `microsoft_docs_search("Azure Container Apps VNet integration internal environment")`
   -- retrieves ACA VNet injection requirements (internal vs external).
2. `microsoft_docs_search("Azure PostgreSQL Flexible Server private endpoint VNet")`
   -- retrieves PG private access options (VNet integration vs private endpoint).
3. `microsoft_docs_search("Azure NSG rules deny public access PostgreSQL subnet")`
   -- retrieves NSG best practices for database subnet isolation.

Optional:

4. `microsoft_code_sample_search("bicep container app environment vnet subnet", language="bicep")`
5. `microsoft_docs_fetch("https://learn.microsoft.com/en-us/azure/container-apps/vnet-custom-internal")`

## Workflow

1. **Inspect repo** -- Read VNet, PG, and ACA Bicep modules. Record whether
   ACA environment has `vnetConfiguration`, whether PG has `publicNetworkAccess:
   'Disabled'`, and whether NSGs exist.
2. **Query MCP** -- Run the three searches. Capture subnet sizing requirements
   for ACA (minimum /23), PG VNet integration vs private endpoint trade-offs,
   NSG rule syntax.
3. **Compare** -- Identify: (a) Is ACA environment VNet-integrated? (b) Is PG
   public access disabled? (c) Do NSG rules restrict PG subnet to ACA subnet
   only?
4. **Patch** -- Update Bicep modules:
   - Add VNet with at least two subnets: `snet-aca` (/23) and `snet-pg` (/24).
   - Configure ACA environment with `vnetConfiguration.infrastructureSubnetId`.
   - Set PG `publicNetworkAccess: 'Disabled'` and configure VNet integration or
     private endpoint.
   - Add NSG on `snet-pg` allowing inbound 5432 only from `snet-aca`.
5. **Verify** -- Bicep lints clean. SSOT YAML updated. No public PG access
   remains in any Bicep file.

## Outputs

| File | Change |
|------|--------|
| `infra/azure/modules/vnet.bicep` | VNet, subnets, NSGs |
| `infra/azure/modules/postgres-flexible.bicep` | Disable public access, VNet integration |
| `infra/azure/odoo-runtime.bicep` | ACA VNet injection |
| `infra/azure/main.bicep` | Wire VNet outputs to PG and ACA modules |
| `infra/ssot/azure/resources.yaml` | VNet, subnet, NSG entries |
| `docs/evidence/<stamp>/aca-private-networking/` | Bicep diffs, MCP excerpts |

## Completion Criteria

- [ ] ACA environment is VNet-integrated (has `infrastructureSubnetId`).
- [ ] PG Flexible Server has `publicNetworkAccess: 'Disabled'`.
- [ ] PG is accessible only from the ACA subnet (VNet integration or private endpoint).
- [ ] NSG on the PG subnet allows inbound 5432 only from the ACA subnet CIDR.
- [ ] NSG denies all other inbound to the PG subnet by default.
- [ ] SSOT `resources.yaml` includes VNet, subnet, and NSG entries.
- [ ] Evidence directory contains Bicep diffs and MCP query excerpts.
