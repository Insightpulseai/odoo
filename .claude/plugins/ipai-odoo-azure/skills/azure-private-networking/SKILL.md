---
name: azure-private-networking
description: Azure private networking rules for IPAI platform services
triggers:
  - keywords: ["private endpoint", "VNet", "NSG", "private link", "service connector"]
layer: B-platform
---

# Azure Private Networking Skill

Network topology for IPAI:

1. All data-plane connections (PG, Key Vault, ACR) use private endpoints or service connectors
2. PostgreSQL (`pg-ipai-odoo`) accepts connections only from ACA environment subnet
3. Key Vault (`kv-ipai-dev`) access via managed identity — no public endpoint required
4. ACR (`ipaiodoodevacr`) pull via managed identity from ACA environment
5. Front Door → ACA ingress is the only public path (TLS terminated at AFD)
6. Never expose PG port 5432 to public internet
7. Never create public IP resources without AFD/WAF in front
8. NSG rules: deny-all-inbound default, allow only ACA subnet → PG subnet on 5432
9. Service connectors preferred over manual connection strings for ACA → PG
10. DNS: Azure Private DNS zones for `privatelink.postgres.database.azure.com`
