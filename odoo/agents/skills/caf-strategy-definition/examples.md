# Examples — caf-strategy-definition

## Example 1: Migration-motivated strategy

**Input**: Organization running Odoo on DigitalOcean VMs, wants to move to Azure for compliance and scalability.

**Output**:
- Motivation: Migrate (critical business events: compliance requirements, data center exit)
- Business outcomes:
  - Fiscal: 30% reduction in infrastructure management overhead
  - Agility: Provisioning time from 2 days to 15 minutes (ACA)
  - Reach: Southeast Asia region with global CDN via Front Door
  - Engagement: 99.9% SLA vs current best-effort availability
- Financial model: DO VMs ($180/mo) vs Azure ACA ($220/mo) — net increase offset by managed services savings
- Digital estate: Odoo web (Rehost → ACA), PostgreSQL (Refactor → managed PG), n8n (Rehost → ACA)
- First project: Migrate PostgreSQL to Azure Database for PostgreSQL Flexible Server
- Risks: [data transfer latency during migration, DNS propagation during cutover]

## Example 2: Innovation-motivated strategy

**Input**: Platform stable on Azure, now wants to add AI agent capabilities using Azure AI services.

**Output**:
- Motivation: Innovate (differentiation through technology, AI-driven operations)
- Business outcomes:
  - Fiscal: Reduce manual data entry by 60% via AI document processing
  - Agility: New agent deployment in hours, not weeks
  - Reach: API-first design enables partner integrations
  - Engagement: Copilot experience increases user productivity by 40%
- Financial model: Azure OpenAI ($50/mo estimate) + Document Intelligence ($30/mo) = $80/mo incremental
- Digital estate: AI services (Rebuild — cloud-native), Copilot UI (Rebuild), Agent runtime (Rebuild)
- First project: Deploy Azure Document Intelligence for invoice OCR
- Risks: [AI model accuracy requires training data, cost scaling with usage]

## Example 3: Governance-motivated strategy

**Input**: Rapid cloud growth with inconsistent resource naming, no cost controls, no policy enforcement.

**Output**:
- Motivation: Govern (control complexity, enforce consistency, manage costs)
- Business outcomes:
  - Fiscal: 20% cost reduction through right-sizing and orphan resource cleanup
  - Agility: Self-service provisioning within policy guardrails
  - Reach: Consistent governance across all environments (dev, staging, prod)
  - Engagement: Engineering team confidence in compliant-by-default resources
- Financial model: Azure Policy (free) + Cost Management (free) + Azure Advisor (free)
- Digital estate: All existing resources (Rehost — governance overlay, no migration needed)
- First project: Implement naming convention policy and cost budget alerts
- Risks: [policy enforcement may break non-compliant resources, requires audit first]
