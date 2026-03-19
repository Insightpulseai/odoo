# Azure Copilot Agent Operations — Learning Path Reference

> Source: Azure Copilot for Azure documentation, Azure Well-Architected Framework, Azure Advisor
> Treatment: Operational skill families for agent-assisted Azure platform management
> Cross-reference: docs/architecture/reference-benchmarks.md

---

## Agent Families

### 1. Deployment Operations

Validates Azure deployment topology including Container Apps provisioning, Front Door routing rules, managed identity bindings, and Key Vault secret references. Ensures every new service follows the canonical resource group and naming convention before it reaches production. Covers TLS termination, custom domain binding, and ingress configuration.

### 2. Migration Operations

Validates platform migration patterns when moving workloads between providers or services. Covers DigitalOcean to Azure Container Apps, Vercel to ACA, nginx to Front Door, and Mailgun to Zoho SMTP transitions. Ensures deprecated resources are confirmed inactive before source cleanup and that DNS cutover is atomic.

### 3. Observability Operations

Validates monitoring and observability posture for all platform services. Covers Application Insights instrumentation, Log Analytics workspace connectivity, Resource Graph query validation, and alert rule completeness. Ensures no production service operates without structured telemetry and that KQL queries from the catalog return expected results.

### 4. Optimization Operations

Validates cost and performance optimization across the Azure footprint. Covers SKU right-sizing, idle resource detection, reserved capacity evaluation, and autoscaling rule configuration. Uses Resource Graph queries to identify stale or zero-traffic resources and ensures no downgrade occurs without stakeholder approval and 30-day usage evidence.

### 5. Resiliency Operations

Validates high availability and disaster recovery posture for production services. Covers zone redundancy on PostgreSQL Flexible Server, Front Door health probe configuration, backup retention policies, and failover DNS routing. Ensures every production service has documented DR evidence and that single-zone deployments are flagged.

### 6. Troubleshooting Operations

Diagnoses runtime issues across the Azure platform stack. Covers container restart loops, DNS resolution failures, Key Vault access denied errors, TLS certificate chain issues, and network security rule conflicts. Uses structured diagnostic workflows with escalation triggers when root cause is not identified within three checks.

---

## Relationship to Platform

These six families map to the InsightPulse AI Azure footprint:

| Family | Primary Azure Resources |
|--------|------------------------|
| Deployment | Container Apps, Front Door, Key Vault, Managed Identity |
| Migration | Container Apps, Front Door, DNS (Cloudflare), SMTP (Zoho) |
| Observability | Application Insights, Log Analytics, Resource Graph, Monitor |
| Optimization | Advisor, Cost Management, Container Apps scaling, PostgreSQL SKU |
| Resiliency | PostgreSQL zone redundancy, Front Door health probes, Backup |
| Troubleshooting | Container Apps logs, Key Vault RBAC, DNS, TLS, NSG |

Cross-references:
- `docs/architecture/reference-benchmarks.md`
- `ssot/runtime/resource-graph-query-catalog.yaml`
- `docs/contracts/azure-resource-graph-contract.md`
- `.claude/rules/infrastructure.md`
