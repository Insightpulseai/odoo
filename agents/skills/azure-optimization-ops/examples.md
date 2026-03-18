# Examples — azure-optimization-ops

## Example 1: Idle Container App detected

**Input**: Monthly cost review for `rg-ipai-agents-dev`

**Output**:
- Resource: `odoo-web` (Microsoft.App/containerApps) in `rg-ipai-agents-dev`
- Traffic: 0 requests/day for last 30 days
- Status: idle — retire candidate (documented in infrastructure.md)
- Current cost: ~$15/month (min replica 1)
- Recommendation: Scale to 0 replicas or delete after confirming no dependencies
- Savings: $15/month
- Blockers: stakeholder approval required — listed as retire candidate but not yet approved
- Evidence: `az monitor metrics list --resource /subscriptions/.../odoo-web --metric Requests --interval P30D`

## Example 2: PostgreSQL SKU right-sizing

**Input**: Review SKU for `ipai-odoo-dev-pg` in `rg-ipai-dev`

**Output**:
- Resource: `ipai-odoo-dev-pg` (Microsoft.DBforPostgreSQL/flexibleServers)
- SKU: General Purpose D2s_v3 (2 vCores, 8 GB RAM)
- Utilization: avg CPU 12%, avg memory 35% over 30 days
- Status: over-provisioned
- Current cost: ~$140/month
- Recommendation: Downgrade to Burstable B2s ($28/month) for dev environment
- Savings: ~$112/month
- Blockers: stakeholder approval required for SKU change
- Rollback: `az postgres flexible-server update --sku-name Standard_D2s_v3`
- Evidence: 30-day CPU and memory metrics from Azure Monitor

## Example 3: Orphaned public IP

**Input**: Resource Graph scan across all resource groups

**Output**:
- Resource: `pip-ipai-legacy-01` (Microsoft.Network/publicIPAddresses) in `rg-ipai-dev`
- Association: none — not attached to any NIC, load balancer, or NAT gateway
- Status: orphaned
- Current cost: ~$3.65/month (static IP)
- Recommendation: Delete after confirming no DNS records point to this IP
- Savings: $3.65/month
- Blockers: verify no external references before deletion
- Evidence: `resources | where type == 'microsoft.network/publicipaddresses' | where properties.ipConfiguration == ''`
