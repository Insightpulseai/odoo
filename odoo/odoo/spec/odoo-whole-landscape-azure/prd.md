# PRD — Odoo Whole-Landscape on Azure

## Objective

Design and document a complete enterprise-grade Azure architecture for the full Odoo ecosystem — not just a single app deployment. Treat it as a whole-landscape problem: hub/shared services, production, non-production, DR, with all connected platforms.

## Required deliverables

A. Executive summary
B. Whole-landscape reference architecture (hub/prod/nonprod/DR)
C. Component inventory by plane (6 planes)
D. Environment topology matrix
E. Data flow and source-of-truth matrix
F. Identity/security model (Zero Trust)
G. HA/DR design with RPO/RTO by plane
H. Vertical/solution consolidation matrix (marketing, retail, media, finance, AI)
I. Desired outcomes → architecture mapping
J. Risks / assumptions / constraints
K. Phased implementation roadmap
L. Canonical target state recommendation

## Scope — 10 design sections

1. **Whole-landscape topology** — hub, prod, nonprod, DR, subscription boundaries, management groups
2. **Workload planes** — transactional, control, data-intelligence, agent, workspace, automation
3. **Odoo-specific technical architecture** — app tier, PG, filestore, workers, cron, ingress, SSO, backup, module lifecycle, multi-company, environments
4. **Integration and data architecture** — canonical write path, read models, operational mirror, analytics mirror, API strategy, agent context, writeback rules, field authority
5. **Security architecture** — Zero Trust, Entra ID, secrets, encryption, RBAC, network segmentation, private endpoints, WAF, SIEM, separation of duties
6. **Reliability and DR architecture** — RPO/RTO per plane, zonal/regional resilience, backup topology, failover design, degraded-mode operation
7. **Operations and platform engineering** — IaC, CI/CD, environment promotion, health checks, policy gates, observability, runbooks
8. **Vertical and solution consolidation** — what stays in Odoo vs Databricks vs Foundry vs Supabase/Plane/web per vertical
9. **Desired outcomes and scorecard** — business outcomes mapped to architecture decisions
10. **Benchmarking and tradeoffs** — SAP whole-landscape comparison, where Odoo is simpler, where custom discipline is required

## Benchmark model

SAP whole-landscape architecture → adapted for Odoo:
- SAP app servers → Odoo web + worker + cron (Container Apps)
- SAP HANA → PostgreSQL Flexible Server
- SAP Web Dispatcher → Azure Front Door
- SAP BW → Databricks (data-intelligence)
- SAP Fiori → Odoo web client + web/ frontend apps
- SAP BTP → Azure AI Foundry agents
- SAP SolMan → Ops console + observability stack

## Add-on constraint

Use the SAP whole-landscape benchmark structurally, but adapt it honestly for Odoo: show what maps directly, what needs custom platform discipline, and what enterprise controls must be added around Odoo to reach a comparable operational maturity.
