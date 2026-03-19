# Constitution — Odoo Whole-Landscape on Azure

## Non-negotiable rules

1. Odoo CE is the canonical transactional system of record
2. Databricks is the governed intelligence backbone (not Odoo, not Supabase)
3. Azure AI Foundry is the generative AI / agent runtime (not Databricks)
4. Supabase is the operational mirror / API / realtime edge (not SoR)
5. Plane is work-management projection and command surface (not SoR)
6. Self-hosted-first unless a managed Azure service is clearly superior and justified
7. OCA-first extension model; ipai_* only for thin bridges
8. Azure Well-Architected Framework five pillars apply to all design decisions
9. Azure landing zone design areas govern the infrastructure layer
10. SAP whole-landscape guidance is the structural benchmark — adapted, not copied

## Benchmark sources

- SAP whole-landscape architecture: https://learn.microsoft.com/en-us/azure/architecture/guide/sap/sap-whole-landscape
- Azure Well-Architected Framework: reliability, security, cost optimization, operational excellence, performance efficiency
- Azure landing zone design areas: tenant/subscription, identity, management groups, networking, security, management, governance, platform automation

## Source-of-truth hierarchy

1. Odoo PostgreSQL = canonical write model
2. Databricks Unity Catalog = governed read model / intelligence products
3. Supabase = operational mirror / API surface
4. Plane = work management projection
5. Foundry = agent runtime (consumes from #1 and #2)
