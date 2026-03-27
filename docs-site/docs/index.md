---
title: InsightPulse AI Documentation
description: AI-first ERP platform on Odoo CE 19 + Azure
---

# InsightPulse AI Documentation

Welcome to the InsightPulse AI platform documentation. This site covers the architecture, development workflow, deployment, and integration patterns for the AI-first ERP platform built on Odoo CE 19.

## Platform at a glance

| Component | Technology |
|-----------|-----------|
| **ERP** | Odoo CE 19.0 + OCA + `ipai_*` modules |
| **Runtime** | Azure Container Apps (Southeast Asia) |
| **Data platform** | Databricks + Unity Catalog |
| **Analytical lake** | Azure Data Lake Storage Gen2 |
| **AI compute** | Microsoft Foundry |
| **Identity** | Microsoft Entra ID (SSO) |
| **DNS** | Azure DNS (authoritative) |
| **CI/CD** | Azure DevOps Pipelines |
| **Chat** | Slack |

## Documentation sections

<div class="grid cards" markdown>

-   :material-lan:{ .lg .middle } **Architecture**

    ---

    System topology, authority model, data flows, and target end state.

    [:octicons-arrow-right-24: Architecture](architecture/index.md)

-   :material-robot:{ .lg .middle } **AI-first development**

    ---

    Agent workflow, spec-kit methodology, Claude Code integration, and MCP servers.

    [:octicons-arrow-right-24: AI-first](ai-first/index.md)

-   :material-puzzle:{ .lg .middle } **Odoo modules**

    ---

    Module philosophy, finance system, BIR compliance, HR, and enterprise parity.

    [:octicons-arrow-right-24: Modules](modules/index.md)

-   :material-cloud-upload:{ .lg .middle } **Deployment**

    ---

    Azure Container Apps, Docker, CI/CD pipelines, and DNS routing.

    [:octicons-arrow-right-24: Deployment](deployment/index.md)

-   :material-connection:{ .lg .middle } **Integrations**

    ---

    Supabase, ADLS ETL, SAP Concur/Joule, Slack, n8n, and Azure AI.

    [:octicons-arrow-right-24: Integrations](integrations/index.md)

-   :material-file-document-check:{ .lg .middle } **Contracts**

    ---

    Data authority, reverse ETL guardrails, and cross-system contracts.

    [:octicons-arrow-right-24: Contracts](contracts/index.md)

</div>
