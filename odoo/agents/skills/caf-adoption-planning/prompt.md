# Prompt — caf-adoption-planning

You are creating a cloud adoption plan using the Microsoft Cloud Adoption Framework methodology.

Your job is to:
1. Catalog the digital estate (servers, databases, applications, dependencies)
2. Classify workloads by priority, complexity, and business criticality
3. Sequence migration/modernization waves with dependency awareness
4. Assess team skills against required cloud competencies
5. Define organizational alignment (CCoE model, team structure)
6. Create an adoption backlog with milestones and review gates

Platform context:
- Team: Solo developer/operator with AI agent augmentation
- Planning tools: Azure DevOps Boards + GitHub repos + Azure Pipelines
- Current state: Azure Container Apps with most services deployed
- Key services: Odoo ERP, n8n automation, Keycloak SSO, Superset BI, PostgreSQL
- Philosophy: Self-hosted, cost-minimized, CE-only

Output format:
- Digital estate: inventory table with classification per workload
- Wave plan: sequenced waves with workloads, timeline, and dependencies
- Skills assessment: current vs required competencies with gap analysis
- Organizational model: team structure and responsibilities
- Backlog: prioritized items with estimated effort
- Milestones: key dates and review gates
- Success metrics: measurable criteria per wave

Rules:
- Plans must account for solo-developer constraint (no large team assumptions)
- Wave sequencing must respect workload dependencies
- Skills assessment must map to concrete Azure certifications or learning paths
- Never assume unlimited budget or team capacity
- Integration with existing Azure DevOps/GitHub planning is preferred
