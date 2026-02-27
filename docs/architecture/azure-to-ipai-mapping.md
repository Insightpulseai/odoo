# Azure to IPAI Product Mapping

This reference maps common Microsoft Azure products to their equivalents within the Insightpulseai (IPAI) ecosystem (Odoo 19, Supabase, DigitalOcean, and GitHub).

## Popular Services

| Azure Product              | IPAI Equivalent                | Description / Notes                                    |
| :------------------------- | :----------------------------- | :----------------------------------------------------- |
| **App Service**            | **Odoo Runtime (Docker)**      | Running on DigitalOcean Droplets.                      |
| **Azure Functions**        | **Supabase Edge Functions**    | Or Odoo Scheduled Actions for internal logic.          |
| **Azure SQL / SQL DB**     | **Supabase Postgres**          | Or Managed Postgres on DigitalOcean.                   |
| **DocumentDB (Cosmos)**    | **Supabase (Postgres JSONB)**  | Postgres with JSONB provides similar NoSQL-like power. |
| **Microsoft Entra ID**     | **Supabase Auth / Odoo OAuth** | SSO and directory synchronization.                     |
| **Virtual Machines**       | **DigitalOcean Droplets**      | The base infrastructure layer.                         |
| **Azure Kubernetes (AKS)** | **Docker Compose (Current)**   | Simplifies orchestration for current size.             |
| **Azure Copilot**          | **Antigravity / IPAI Agents**  | The AI-powered development and operations companion.   |

## Developer Tools

| Azure Product          | IPAI Equivalent             | Description / Notes                            |
| :--------------------- | :-------------------------- | :--------------------------------------------- |
| **Azure Pipelines**    | **GitHub Actions**          | CI/CD and automation.                          |
| **Azure Boards**       | **GitHub Projects**         | Task tracking and team collaboration.          |
| **Microsoft Dev Box**  | **GitHub Codespaces**       | Secure cloud-hosted development environments.  |
| **App Configuration**  | **GitHub Environments**     | Centralized secrets and environment variables. |
| **DevTest Labs**       | **Template Repositories**   | Standardized project bootstrapping.            |
| **Playwright Testing** | **Playwright + GH Actions** | E2E testing scale-out.                         |

## Specialized Services

| Azure Product          | IPAI Equivalent               | Description / Notes                          |
| :--------------------- | :---------------------------- | :------------------------------------------- |
| **Azure Arc**          | **Odoo Ops Console**          | Management layer for multi-cloud visibility. |
| **Azure AI / Foundry** | **IPAI Agent Registry**       | Building and managing specialized AI skills. |
| **Azure Monitor**      | **Managed Grafana / Loki**    | Integrated into the Odoo Ops stack.          |
| **Service Bus**        | **Supabase Realtime / Redis** | Messaging and eventing between components.   |
