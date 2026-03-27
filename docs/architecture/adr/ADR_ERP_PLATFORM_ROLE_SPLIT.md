# ERP Platform Role Split

> Version: 1.0.0
> Canonical repo: `docs`

## Context
A modern Wholesale SaaS ERP requires transactional integrity, deep analytical scale, and advanced non-deterministic AI capabilities. Attempting to house all three workloads inside a single monolithic PostgreSQL database and Python runtime causes resource starvation, upgrade nightmares, and security vulnerabilities.

## Decision
- **System of Record (ERP)**: Odoo acts as the exclusive transactional core. It handles OLTP writes, user sessions, and immediate business logic. It must run on Azure Container Apps with Azure DB for PostgreSQL Flexible Server.
- **System of Intelligence (Data)**: Azure Databricks acts as the exclusive analytical layer. It ingests Odoo data via asynchronous pipelines, standardizes it in a Medallion architecture (Bronze -> Silver -> Gold), and serves it back to the platform via Unity Catalog and Serverless SQL.
- **System of Agency (AI)**: Microsoft Foundry acts as the exclusive AI orchestration layer. Anthropic Claude agents and Azure OpenAI models are managed, evaluated, and traced here. The ERP must call Foundry endpoints via API; agents must never execute arbitrary logic deep within Odoo transactions.

## Consequences
- Odoo database sizing can be strictly optimized for low-latency writes rather than vast analytical read scans.
- AI operations are structurally decoupled, meaning prompts can be versioned and deployed safely without requiring ERP downtime.
- The platform incurs the baseline cost of running three separate structural topologies (ACA + Databricks + Foundry).
- Cross-boundary state synchronization requires robust eventing via Azure Service Bus or Event Grid.
