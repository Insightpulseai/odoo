# Examples: SaaS Networking Design

## Example 1: Single-Stamp Networking (Canonical Stack)

**Scenario**: Single stamp in Southeast Asia for Odoo CE platform.

**VNET topology**:
```
vnet-ipai-prod-sea-001 (10.1.0.0/16)
├── snet-compute    (10.1.1.0/24)  — Container Apps Environment
├── snet-data       (10.1.2.0/24)  — Private endpoints (PG, Redis, Storage)
├── snet-mgmt       (10.1.3.0/24)  — Bastion, monitoring agents
└── snet-integration (10.1.4.0/24) — Service Bus, Event Hub endpoints
```

**Private endpoints**:
| Service | Private Endpoint | Private DNS Zone |
|---------|-----------------|------------------|
| PostgreSQL | pe-pg-ipai-prod-sea-001 | privatelink.postgres.database.azure.com |
| Redis | pe-redis-ipai-prod-sea-001 | privatelink.redis.cache.windows.net |
| Key Vault | pe-kv-ipai-prod-sea-001 | privatelink.vaultcore.azure.net |
| Storage | pe-st-ipai-prod-sea-001 | privatelink.blob.core.windows.net |

**Front Door routing**:
```
Front Door: ipai-fd-prod
├── Route: *.erp.insightpulseai.com
│   └── Origin: cae-ipai-prod-sea-001 (Container Apps)
├── Route: {tenant}.erp.insightpulseai.com
│   └── Origin: resolved via tenant catalog → stamp endpoint
└── WAF Policy: waf-ipai-prod (OWASP 3.2, rate limit: 1000 req/min/tenant)
```

---

## Example 2: Multi-Stamp with Custom Domains

**Scenario**: Two stamps (APAC, US) with enterprise tenants using custom domains.

**Custom domain onboarding**:
1. Tenant requests custom domain: `erp.acme.com`
2. Platform generates CNAME verification: `_dnsauth.erp.acme.com → {verification-token}.frontdoor.azure.com`
3. Tenant creates CNAME record
4. Platform verifies DNS propagation
5. Front Door provisions managed TLS certificate
6. Routing rule created: `erp.acme.com → stamp-sea-001`

**DNS automation** (subdomain-registry.yaml):
```yaml
tenant_domains:
  - tenant_id: acme-corp
    type: custom
    domain: erp.acme.com
    stamp: stamp-sea-001
    tls: front-door-managed
    verified: true

  - tenant_id: globex-inc
    type: platform
    domain: globex.erp.insightpulseai.com
    stamp: stamp-eus-001
    tls: front-door-managed
    verified: true
```

---

## Example 3: Enterprise Private Connectivity

**Scenario**: Enterprise tenant requires Private Link from their Azure subscription.

**Architecture**:
```
Tenant Azure Subscription          Platform Stamp
├── vnet-acme-prod                 ├── vnet-ipai-prod-sea-001
│   └── Private Endpoint ──────── │   └── Private Link Service
│       (pe-ipai-acme)            │       (pls-ipai-prod-sea-001)
```

- Platform exposes Private Link Service on the compute subnet
- Tenant creates Private Endpoint in their VNET targeting the Private Link Service
- Traffic flows over Azure backbone, never over public internet
- Front Door not involved — tenant accesses Odoo directly via private endpoint
