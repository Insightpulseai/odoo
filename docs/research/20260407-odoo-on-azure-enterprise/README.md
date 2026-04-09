# Odoo-on-Azure Enterprise Platform: Research Report

> Research conducted 2026-04-07 | Confidence: HIGH (85%+)
> Goal: Map Azure-native templates, SDKs, and reference architectures to build
> "Odoo on Azure" as an enterprise ERP platform with Azure-native operating model maturity.
> Benchmarks: Odoo CE 18 + OCA (application), ACA Well-Architected (runtime), Foundry SDK (AI), AvaTax capability (tax/compliance), SAP-on-Azure (ops maturity only).

---

## Table of Contents

1. [Azure Developer CLI (azd) Templates](#1-azure-developer-cli-azd-templates)
2. [Microsoft Foundry SDK and Agent Templates](#2-microsoft-foundry-sdk-and-agent-templates)
3. [SAP on Azure Reference Architecture](#3-sap-on-azure-reference-architecture)
4. [Gap Analysis: Odoo vs SAP on Azure](#4-gap-analysis-odoo-vs-sap-on-azure)
5. [Buildable Templates and SDK Patterns](#5-buildable-templates-and-sdk-patterns)
6. [Recommended Roadmap](#6-recommended-roadmap)

---

## 1. Azure Developer CLI (azd) Templates

### 1.1 Template Gallery and Discovery

The official azd template gallery is at [azure.github.io/awesome-azd](https://azure.github.io/awesome-azd/) with the backing repo at [github.com/Azure/awesome-azd](https://github.com/Azure/awesome-azd). The full template index is maintained in `website/static/templates.json`.

Microsoft Learn documents the gallery system at [Explore Azure Developer CLI Template Galleries](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/azd-template-galleries).

### 1.2 `azd compose` Feature (Key for Odoo)

The `azd add` command enables composing resources without writing Bicep:

```bash
azd add  # Interactive: select Database > PostgreSQL, AI > OpenAI, Host > Container App
```

This generates an `azure.yaml` with structured resource declarations:

```yaml
services:
  webfrontend:
    type: host.containerapp
    uses:
      - azddb       # PostgreSQL
      - azdchat     # Azure OpenAI
resources:
  azddb:
    type: db.postgres
  azdchat:
    type: ai.openai
```

**Significance for Odoo**: This is the fastest path to scaffold an `azure.yaml` for Odoo CE that provisions ACA + PostgreSQL + OpenAI in one `azd up`.

Source: [Build a minimal template using azd compose](https://learn.microsoft.com/azure/developer/azure-developer-cli/compose-quickstart)

### 1.3 Directly Relevant azd Templates

| Template | Repo | Stack | Relevance |
|----------|------|-------|-----------|
| Python Django + PostgreSQL on ACA | [azure-django-postgres-aca](https://github.com/Azure-Samples/azure-django-postgres-aca) | Python, PostgreSQL, ACA, Bicep | **HIGH** -- closest to Odoo's stack (Python + PG + container) |
| LiteLLM on ACA + PostgreSQL | [Build5Nines/azd-litellm](https://github.com/Build5Nines/azd-litellm) | Python, PostgreSQL, ACA, ACR, App Insights | **HIGH** -- AI proxy with exact infra pattern |
| RAG on PostgreSQL | [rag-postgres-openai-python](https://github.com/Azure-Samples/rag-postgres-openai-python) | Python, PostgreSQL, OpenAI, ACA, Bicep | **HIGH** -- RAG pattern for Odoo copilot |
| Flask Surveys + Key Vault + PG | [flask-surveys-container-app](https://github.com/pamelafox/flask-surveys-container-app) | Python, PostgreSQL, Key Vault, ACA | **MEDIUM** -- Key Vault integration pattern |
| Ruby on Rails + PG on ACA | [azure-rails-starter](https://github.com/dbroeglin/azure-rails-starter) | Ruby, PostgreSQL, Key Vault, ACA, Bicep | **MEDIUM** -- Bicep patterns for env vars + secrets |
| Quarkus Java on ACA + PG | [java-on-aca-quarkus](https://github.com/Azure-Samples/java-on-aca-quarkus) | Java, PostgreSQL, MySQL, ACA, Monitor, Bicep | **MEDIUM** -- multi-service ACA pattern |
| Front Door + AKS End-to-End TLS | [aks-front-door-end-to-end-tls](https://github.com/Azure-Samples/aks-front-door-end-to-end-tls) | AKS, Front Door Premium, Key Vault, WAF, Bicep | **HIGH** -- Front Door + Key Vault TLS pattern |
| HA Zone-Redundant iPaaS | [highly-available-zone-redundant-ipaas](https://github.com/Azure-Samples/highly-available-zone-redundant-ipaas) | Front Door, Key Vault, App Service, Bicep | **MEDIUM** -- HA Front Door pattern |

### 1.4 Full-Stack Template Catalog

Microsoft maintains a full-stack template catalog at:
- [Full-stack deployment templates for azd](https://learn.microsoft.com/azure/developer/azure-developer-cli/full-stack-templates)
- [azd templates for Azure Container Apps](https://learn.microsoft.com/azure/container-apps/container-apps-cli-templates)

### 1.5 No Existing Odoo or ERP Template

There is **no existing azd template for Odoo or any open-source ERP** in the gallery. This is a greenfield opportunity. The `azure-django-postgres-aca` template is the closest starting point since Odoo is a Python/PostgreSQL web application.

---

## 2. Microsoft Foundry SDK and Agent Templates

### 2.1 Foundry Agent Service Overview

Microsoft Foundry Agent Service is the platform for building enterprise AI agents. Key components:

| Component | Function |
|-----------|----------|
| **Agent Runtime** | Hosts prompt agents and hosted agents; manages conversations, tool calls, lifecycle |
| **Tools** | Built-in: Azure AI Search, Bing Search, Code Interpreter, File Search, Function calling, MCP, Microsoft Fabric, OpenAPI, Browser Automation |
| **Models** | GPT-4o, Llama, DeepSeek, Claude (partner model) from model catalog |
| **Observability** | End-to-end tracing, metrics, Application Insights |
| **Identity** | Microsoft Entra, RBAC, content filters, virtual network isolation |
| **Publishing** | Version agents, stable endpoints, publish to Teams/M365 Copilot/Entra Agent Registry |

Source: [What is Microsoft Foundry Agent Service?](https://learn.microsoft.com/azure/foundry/agents/overview)

### 2.2 SDK Versions and Installation

**Python (primary for Odoo integration):**
```bash
pip install "azure-ai-projects>=2.0.0"
pip install azure-identity
```

**Agent Framework (newer, recommended):**
```python
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient, FoundryAgent, FoundryEmbeddingClient
from azure.identity import AzureCliCredential

# Option 1: App-owned agent with Foundry backend
agent = Agent(
    client=FoundryChatClient(
        project_endpoint="https://your-project.services.ai.azure.com",
        model="gpt-4o-mini",
        credential=AzureCliCredential(),
    ),
    name="OdooCopilot",
    instructions="You are a helpful ERP assistant.",
)

# Option 2: Service-managed agent (definition lives in Foundry)
agent = FoundryAgent(
    project_endpoint="https://your-project.services.ai.azure.com",
    agent_name="odoo-copilot",
    agent_version="1.0",
    credential=AzureCliCredential(),
)
```

Source: [Microsoft Foundry quickstart](https://learn.microsoft.com/azure/foundry/quickstarts/get-started-code), [Agent Framework Foundry provider](https://learn.microsoft.com/agent-framework/agents/providers/microsoft-foundry)

### 2.3 Key Templates and Solution Accelerators

| Template | Repo | Purpose |
|----------|------|---------|
| **foundry-agent-webapp** | [microsoft-foundry/foundry-agent-webapp](https://github.com/microsoft-foundry/foundry-agent-webapp) | Full web app: React 19 + ASP.NET Core 9 + Entra ID + Foundry agents + ACA deployment |
| **microsoft-foundry-baseline** | [Azure-Samples/microsoft-foundry-baseline](https://github.com/Azure-Samples/microsoft-foundry-baseline) | Network-isolated production baseline: App Service + WAF + Firewall + AI Search + Cosmos DB + Key Vault |
| **get-started-with-ai-agents** | [Azure-Samples/get-started-with-ai-agents](https://github.com/Azure-Samples/get-started-with-ai-agents) | Basic agent deployment on ACA |
| **Multi-Agent Automation Engine** | [microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator](https://github.com/microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator) | Multi-agent workflow: Agent Framework + Foundry + Cosmos DB |
| **Conversation Knowledge Mining** | [microsoft/Conversation-Knowledge-Mining-Solution-Accelerator](https://github.com/microsoft/Conversation-Knowledge-Mining-Solution-Accelerator) | Extract knowledge from conversations |
| **Document Generation** | [microsoft/document-generation-solution-accelerator](https://github.com/microsoft/document-generation-solution-accelerator) | AI-powered document creation from data |
| **Multi-modal Content Processing** | [microsoft/content-processing-solution-accelerator](https://github.com/microsoft/content-processing-solution-accelerator) | Process diverse content types (invoices, receipts) |
| **Foundry Starter Pack (.NET)** | [Azure/microsoft-agent-framework-foundry-starter-pack-net](https://github.com/Azure/microsoft-agent-framework-foundry-starter-pack-net) | .NET Aspire + Agent Framework + Foundry |

### 2.4 foundry-agent-webapp Architecture Detail

This is the most directly reusable template. Architecture:

- **Frontend**: React 19 + TypeScript + Vite + MSAL.js (Entra ID PKCE)
- **Backend**: ASP.NET Core 9 Minimal APIs + Azure.AI.Projects SDK
- **Auth**: Entra ID app registration (auto-created via Bicep) + User-Assigned Managed Identity
- **Infra**: ACA (0.5 vCPU, 1GB, scale-to-zero) + ACR (Basic) + Log Analytics + App Insights (dual) + Managed Identity
- **Deploy**: `azd init -t microsoft-foundry/foundry-agent-webapp && azd up` (10-12 min)

**Adaptation for Odoo**: Replace the React frontend with Odoo's web client. Replace ASP.NET backend with Odoo's Python backend. Keep the Entra ID auth, ACA deployment, and Foundry agent integration patterns.

### 2.5 microsoft-foundry-baseline Architecture Detail

Production-grade, network-isolated reference:

- **Network**: VNet with delegated subnets + Azure Firewall (egress) + Application Gateway WAF (ingress) + Private endpoints
- **Compute**: App Service Plan P1v3 (3 instances across AZs) + Windows VM jump box + Bastion
- **AI**: Azure OpenAI (GPT-4.1) + Azure AI Search (vector store) + Bing Search (grounding)
- **Data**: Cosmos DB (conversation history) + Azure Storage (GZRS + ZRS)
- **Security**: Key Vault (TLS certs + secrets) + Managed identities + Entra Agent ID + DDoS Protection
- **Observability**: Application Insights + Log Analytics

**Adaptation for Odoo**: This is the enterprise landing zone pattern. Replace App Service with ACA, add PostgreSQL Flexible Server, swap Cosmos DB for PostgreSQL-based conversation storage, keep all network/security/observability layers.

### 2.6 SAP Joule vs Foundry-based Odoo Copilot

| Dimension | SAP Joule | Buildable with Foundry |
|-----------|-----------|----------------------|
| **AI Models** | GPT-4o via Azure OpenAI (SAP Generative AI Hub, only on Azure) | Any model from Foundry catalog (GPT-4o, Claude, Llama, DeepSeek) |
| **Data Grounding** | SAP business data (S/4HANA, SuccessFactors, Ariba) | Odoo data via Azure AI Search + PostgreSQL pgvector |
| **Agent Builder** | Joule Studio (GA Q1 2026) | Foundry Agent Service + Agent Framework |
| **Tool Integration** | SAP BTP connectors | MCP servers, Azure Functions, Logic Apps, OpenAPI, Fabric |
| **Distribution** | SAP Fiori, SAP Start | Teams, M365 Copilot, Entra Agent Registry, custom web |
| **Licensing** | Consumption-based "AI Units" | Azure pay-per-use (OpenAI token pricing) |
| **Customization** | Limited to SAP-approved patterns | Full control (prompt agents, hosted agents, custom code) |

**Key insight**: SAP Joule is *built on Azure OpenAI*. Everything Joule does, we can replicate with Foundry Agent Service, with more flexibility and lower cost.

Sources:
- [SAP Joule and Microsoft Copilot integration](https://saxon.ai/blogs/when-sap-joule-meets-microsoft-copilot-whats-in-it-for-you/)
- [Unlock AI innovation with new joint capabilities from Microsoft and SAP](https://azure.microsoft.com/en-us/blog/unlock-ai-innovation-with-new-joint-capabilities-from-microsoft-and-sap/)
- [SAP AI Agents in 2026: Joule Studio Features](https://research.aimultiple.com/sap-ai-agents/)

---

## 3. SAP on Azure Reference Architecture

### 3.1 Official Reference Architectures

Microsoft maintains comprehensive SAP on Azure architectures at [Azure Architecture Center](https://learn.microsoft.com/azure/architecture/guide/sap/):

| Architecture | URL | Key Components |
|-------------|-----|----------------|
| SAP Landscape Architecture (whole) | [sap-whole-landscape](https://learn.microsoft.com/azure/architecture/guide/sap/sap-whole-landscape) | Hub-spoke VNets, ExpressRoute, prod/non-prod/DR subscriptions, SAP BTP via Private Link |
| SAP NetWeaver on Windows | [sap-netweaver](https://learn.microsoft.com/azure/architecture/guide/sap/sap-netweaver) | VMs, Load Balancer, ExpressRoute, Azure Monitor for SAP |
| SAP S/4HANA on Linux | [sap-s4hana](https://learn.microsoft.com/azure/architecture/guide/sap/sap-s4hana) | Linux VMs, HANA, HA clusters, Azure NetApp Files |
| SAP BW/4HANA | [run-sap-bw4hana-with-linux-virtual-machines](https://learn.microsoft.com/azure/architecture/reference-architectures/sap/run-sap-bw4hana-with-linux-virtual-machines) | BOBJ, Web Dispatcher, ASCS cluster, HANA |
| SAP HANA Scale-Up | [run-sap-hana-for-linux-virtual-machines](https://learn.microsoft.com/azure/architecture/reference-architectures/sap/run-sap-hana-for-linux-virtual-machines) | HANA HA, DR with cross-region replication |

### 3.2 Azure Center for SAP Solutions (ACSS)

ACSS is the managed service that makes SAP a "top-level workload" on Azure:

- **Guided deployment**: Creates compute, storage, networking per SAP best practices
- **Software installation**: Automates SAP S/4HANA installation
- **Virtual Instance for SAP (VIS)**: Logical representation of SAP system as Azure resource
- **Operations**: Start/stop SAP tiers, health monitoring, quality checks via Azure Advisor
- **Cost analysis**: SID-level cost visibility
- **RBAC**: Built-in roles (Administrator, Service, Reader)
- **Monitoring**: Integration with Azure Monitor for SAP solutions
- **Supported deployments**: Single server, Distributed, Distributed with HA

Source: [What is Azure Center for SAP solutions?](https://learn.microsoft.com/azure/sap/center-sap-solutions/overview)

### 3.3 SAP Deployment Automation Framework

Open-source at [github.com/Azure/sap-automation](https://github.com/Azure/sap-automation):

- **Terraform**: Infrastructure deployment (VMs, networking, storage)
- **Ansible**: OS configuration, HANA installation, application setup
- **Three-tier deployment**: Control Plane > Workload Zone > System
- **DevOps integration**: Azure DevOps pipelines, GitHub Actions
- **Multi-subscription**: Hub (control plane) + spoke (workload zones)

Structure:
```
DEPLOYER/     -- Control plane config
LIBRARY/      -- Terraform state + SAP media storage
LANDSCAPE/    -- Workload zone configs (per environment)
SYSTEM/       -- SAP system configs (per SID)
```

Source: [Plan your deployment of the SAP automation framework](https://learn.microsoft.com/azure/sap/automation/plan-deployment)

### 3.4 SAP on Azure Landing Zone Accelerator

Part of the Cloud Adoption Framework:

- Hub-spoke networking with ExpressRoute
- Separate subscriptions for prod, non-prod, DR
- Azure Firewall for egress control
- Application Gateway/WAF for ingress
- Azure NetApp Files for shared storage
- Azure Site Recovery for DR
- Azure Monitor for SAP solutions for observability
- Integration with Microsoft Fabric for analytics

Source: [SAP on Azure landing zone accelerator](https://learn.microsoft.com/azure/cloud-adoption-framework/scenarios/sap/enterprise-scale-landing-zone)

### 3.5 Azure Services SAP Uses

| Category | Services |
|----------|----------|
| **Compute** | VMs (M-series for HANA, E-series for app servers), Dedicated Hosts |
| **Storage** | Managed Disks (Premium SSD, Ultra), Azure NetApp Files, Azure Files |
| **Networking** | VNet, ExpressRoute, Load Balancer, Application Gateway, NSGs, Azure Firewall |
| **Database** | HANA on VMs, HANA Large Instances |
| **Identity** | Entra ID, RBAC |
| **Monitoring** | Azure Monitor, Azure Monitor for SAP, Application Insights, Log Analytics |
| **Security** | Key Vault, DDoS Protection, Azure Bastion |
| **DR** | Azure Site Recovery, Cross-region replication |
| **Integration** | Logic Apps (SAP connector), Azure Data Factory, Microsoft Fabric |
| **AI** | Joule via Azure OpenAI (through SAP BTP) |
| **Management** | Azure Center for SAP, Azure Advisor, Azure Policy |

---

## 4. Gap Analysis: Odoo vs SAP on Azure

### 4.1 Feature Parity Matrix

| Enterprise Capability | SAP on Azure | Odoo on Azure (Current) | Odoo on Azure (Achievable) | How to Close Gap |
|----------------------|-------------|------------------------|---------------------------|-----------------|
| **Guided Deployment** | ACSS (managed) | Manual | `azd` template with Bicep | Build `azd` template for Odoo CE |
| **IaC Automation** | SAP Automation Framework (Terraform + Ansible) | Ad-hoc scripts | Bicep + GitHub Actions | Create Odoo Deployment Automation Framework |
| **Landing Zone** | SAP Landing Zone Accelerator | None | Azure Landing Zone + Odoo workload | Fork ALZ pattern, add Odoo-specific modules |
| **Health Monitoring** | Azure Monitor for SAP | Basic infra monitoring | Custom Odoo provider for Azure Monitor | Build Odoo monitoring provider (Longpolling, cron, workers) |
| **Virtual Instance** | VIS (logical SAP system as Azure resource) | None | Custom Resource Provider | Azure Custom Resource Provider for Odoo instances |
| **AI Copilot** | SAP Joule (GPT-4o) | None | Foundry Agent Service | Build `ipai_ai_copilot` + Foundry agent |
| **Document Intelligence** | SAP Document Management | None | Azure Document Intelligence | Invoice/receipt extraction with prebuilt models |
| **Analytics** | SAP Analytics Cloud + Fabric | None | Power BI + Fabric + Databricks | Direct SQL/JDBC from Odoo PG to Databricks |
| **Workflow Automation** | SAP Workflow, BTP | Odoo Workflows | Odoo + Logic Apps + Power Automate | Expose Odoo workflows via API connectors |
| **Multi-Agent AI** | Joule Studio (multi-agent) | None | Multi-Agent Automation Engine | Adapt Microsoft's solution accelerator |
| **Compliance/Governance** | SAP GRC | `ipai_*` compliance modules | Azure Policy + Odoo modules | Implement BIR/PH compliance in Odoo + Azure Policy |
| **Cost Visibility** | ACSS cost analysis per SID | None | Azure Cost Management tags | Tag Odoo resources by instance/environment |
| **HA/DR** | HA clusters, Azure Site Recovery | Single instance | PostgreSQL HA + ACA multi-region | PostgreSQL Flexible Server HA + ACA geo-distribution |
| **Network Isolation** | Private VNets, NSGs, Firewall | Public | Private endpoint + VNet integration | ACA VNet integration + Private Link for PG |
| **Identity** | Entra ID via SAP BTP | Basic | Entra ID via OIDC | `ipai_auth_oidc` module |

### 4.2 What Makes SAP "Enterprise-Grade" (That We Must Replicate)

1. **First-class Azure integration**: SAP is a "top-level workload" with dedicated Azure services (ACSS, Monitor for SAP). Odoo needs equivalent Azure-aware tooling.

2. **Automated deployment with best practices**: ACSS + SAP Automation Framework handle sizing, networking, HA, and software installation automatically. We need an `azd` template that does the same for Odoo.

3. **Operational visibility**: VIS gives a single-pane view of SAP system health, status, and costs. We need an Odoo dashboard equivalent in Azure portal or Grafana.

4. **Quality checks and recommendations**: Azure Advisor integration for SAP-specific best practices. We need Odoo-specific health checks.

5. **Network-first security**: SAP architectures default to hub-spoke VNets, private endpoints, NSGs, and firewalls. Odoo deployments must match this posture.

6. **Compliance certification**: SAP has SOC 2, ISO 27001, GDPR compliance built into its Azure patterns. Odoo needs Azure Policy enforcement + compliance evidence.

7. **AI integration**: Joule provides context-aware AI within ERP workflows. Our Foundry-based copilot must be equally embedded in Odoo's UX.

---

## 5. Buildable Templates and SDK Patterns

### 5.1 Proposed `azd` Template Structure for Odoo on Azure

```
odoo-on-azure/
|-- azure.yaml                    # azd manifest
|-- infra/
|   |-- main.bicep                # Orchestrator
|   |-- main.parameters.json      # Environment parameters
|   |-- core/
|   |   |-- container-apps-environment.bicep
|   |   |-- container-app-odoo.bicep
|   |   |-- container-registry.bicep
|   |   |-- postgresql-flexible-server.bicep
|   |-- network/
|   |   |-- virtual-network.bicep
|   |   |-- front-door.bicep
|   |   |-- private-endpoints.bicep
|   |   |-- nsg.bicep
|   |-- security/
|   |   |-- key-vault.bicep
|   |   |-- managed-identity.bicep
|   |   |-- entra-app-registration.bicep
|   |-- ai/
|   |   |-- foundry-project.bicep
|   |   |-- openai-deployment.bicep
|   |   |-- document-intelligence.bicep
|   |   |-- ai-search.bicep
|   |-- observability/
|   |   |-- log-analytics.bicep
|   |   |-- application-insights.bicep
|   |   |-- dashboard.bicep
|   |-- governance/
|       |-- policy-assignments.bicep
|       |-- cost-tags.bicep
|-- src/
|   |-- odoo/
|   |   |-- Dockerfile
|   |   |-- odoo.conf.template
|   |   |-- requirements.txt
|   |   |-- addons/              # Custom ipai_* modules
|   |-- copilot/
|       |-- agent-definition.json
|       |-- tools/
|       |   |-- odoo-api-tool.json  # OpenAPI spec for Odoo JSON-RPC
|       |-- knowledge/
|           |-- index-config.json   # AI Search index for Odoo docs
|-- .github/
|   |-- workflows/
|       |-- ci.yml
|       |-- cd.yml
|-- scripts/
    |-- post-deploy.sh            # Odoo module installation
    |-- health-check.sh           # Endpoint verification
```

### 5.2 Key Bicep Patterns to Adopt

**From `azure-django-postgres-aca`** (closest stack match):
- Container App with PostgreSQL connection string from Key Vault
- Managed identity for ACR pull
- Environment variable injection from Bicep outputs

**From `aks-front-door-end-to-end-tls`** (Front Door pattern):
- Front Door Premium with custom domain
- TLS certificate from Key Vault
- Private Link to backend origin
- WAF policy attachment

**From `microsoft-foundry-baseline`** (enterprise security):
- VNet with delegated subnets
- Azure Firewall for egress
- Private endpoints for all PaaS services
- DDoS Protection Plan
- Managed identity chain

**From `azd-litellm`** (ACA + PG + AI proxy):
- Docker container build in ACR
- PostgreSQL Flexible Server provisioning
- Application Insights integration
- Secret management via environment variables

### 5.3 CI/CD Pipeline Pattern

**GitHub Actions (CI):**
```yaml
# .github/workflows/ci.yml
- Lint: pre-commit (Odoo + Bicep)
- Test: Odoo unit tests in disposable PostgreSQL
- Build: Docker image for Odoo CE + custom addons
- Validate: Bicep what-if deployment
- Security: Trivy container scan + SARIF upload
```

**Azure DevOps (CD):**
```yaml
# azure-pipelines.yml
stages:
  - stage: Deploy_Dev
    jobs:
      - job: Infrastructure
        steps: azd provision --environment dev
      - job: Application
        steps: azd deploy --environment dev
      - job: PostDeploy
        steps: odoo module install/upgrade
  - stage: Deploy_Staging
    # Gated approval
  - stage: Deploy_Prod
    # Gated approval + canary
```

### 5.4 Monitoring and Observability Template

Modeled after Azure Monitor for SAP solutions, build an "Azure Monitor for Odoo" pattern:

| Metric | Source | Collection |
|--------|--------|-----------|
| Odoo worker count | Odoo admin API | Custom metric via App Insights SDK |
| Longpolling connections | Odoo gevent | Custom metric |
| Cron job execution | Odoo ir.cron | Structured logging to Log Analytics |
| HTTP request latency | ACA ingress | Built-in ACA metrics |
| PostgreSQL connections | PG Flex Server | Built-in PG metrics |
| Database size | PG Flex Server | Built-in PG metrics |
| Container restarts | ACA | Built-in ACA metrics |
| AI agent invocations | Foundry | App Insights traces |

### 5.5 Enterprise Landing Zone Pattern for Odoo

Adapted from SAP Landing Zone Accelerator:

```
Management Groups:
  IPAI/
    Platform/
      Identity/        # Entra ID, Keycloak (transitional)
      Management/       # Log Analytics, Automation
      Connectivity/     # Hub VNet, Firewall, ExpressRoute/VPN
    Landing Zones/
      Odoo-Prod/        # Production subscription
        rg-odoo-prod-aca/       # ACA environment + Odoo containers
        rg-odoo-prod-data/      # PostgreSQL Flex Server
        rg-odoo-prod-ai/        # Foundry project + AI resources
        rg-odoo-prod-security/  # Key Vault + Managed Identities
      Odoo-NonProd/     # Dev + Staging subscription
        rg-odoo-dev-*/
        rg-odoo-staging-*/
    Sandbox/
      Odoo-Demo/        # Demo/showroom
```

### 5.6 Foundry Agent Definition for Odoo Copilot

```json
{
  "name": "odoo-copilot",
  "version": "1.0",
  "model": "gpt-4o",
  "instructions": "You are an ERP assistant for Odoo. You help users with sales orders, invoices, inventory, HR, and accounting tasks. Always reference Odoo field names and menu paths. Use tools to query live Odoo data.",
  "tools": [
    {
      "type": "azure_ai_search",
      "connection": "odoo-docs-index",
      "description": "Search Odoo documentation and knowledge base"
    },
    {
      "type": "function",
      "function": {
        "name": "search_odoo_records",
        "description": "Search Odoo records using domain filters",
        "parameters": {
          "model": "string (e.g., sale.order, account.move)",
          "domain": "array of Odoo domain tuples",
          "fields": "array of field names to return",
          "limit": "integer"
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "create_odoo_record",
        "description": "Create a new record in Odoo",
        "parameters": {
          "model": "string",
          "values": "object of field:value pairs"
        }
      }
    },
    {
      "type": "openapi",
      "spec_url": "https://odoo.insightpulseai.com/api/v1/openapi.json",
      "description": "Odoo REST API for CRUD operations"
    }
  ]
}
```

---

## 6. Recommended Roadmap

### Phase 1: Foundation (Weeks 1-4)

| Action | Template/SDK Source | Deliverable |
|--------|-------------------|-------------|
| Create `azd` template for Odoo CE on ACA + PG | [azure-django-postgres-aca](https://github.com/Azure-Samples/azure-django-postgres-aca), [azd-litellm](https://github.com/Build5Nines/azd-litellm) | `azure.yaml` + Bicep modules |
| Add Key Vault integration | [flask-surveys-container-app](https://github.com/pamelafox/flask-surveys-container-app) | Secrets in Key Vault, not env vars |
| Add Front Door + WAF | [aks-front-door-end-to-end-tls](https://github.com/Azure-Samples/aks-front-door-end-to-end-tls) | TLS termination + CDN |
| CI/CD pipeline | Standard azd patterns | GitHub Actions CI + Azure DevOps CD |
| Basic monitoring | ACA + PG built-in metrics | App Insights + Log Analytics |

### Phase 2: AI Integration (Weeks 5-8)

| Action | Template/SDK Source | Deliverable |
|--------|-------------------|-------------|
| Deploy Foundry project | [get-started-with-ai-agents](https://github.com/Azure-Samples/get-started-with-ai-agents) | Foundry project + GPT-4o deployment |
| Build Odoo copilot agent | [foundry-agent-webapp](https://github.com/microsoft-foundry/foundry-agent-webapp) | `ipai_ai_copilot` module + Foundry agent |
| Document Intelligence integration | [document-intelligence-code-samples](https://github.com/Azure-Samples/document-intelligence-code-samples) | Invoice/receipt auto-processing |
| Knowledge grounding | [rag-postgres-openai-python](https://github.com/Azure-Samples/rag-postgres-openai-python) | AI Search index over Odoo docs + data |

### Phase 3: Enterprise Hardening (Weeks 9-12)

| Action | Template/SDK Source | Deliverable |
|--------|-------------------|-------------|
| Network isolation (VNet + private endpoints) | [microsoft-foundry-baseline](https://github.com/Azure-Samples/microsoft-foundry-baseline) | Private ACA + PG + Foundry |
| Landing zone structure | [ALZ Bicep Accelerator](https://azure.github.io/Azure-Landing-Zones/bicep/gettingstarted/) | Management groups + subscriptions + policies |
| PostgreSQL HA | PG Flex Server zone-redundant HA | Automatic failover |
| Multi-agent workflows | [Multi-Agent-Custom-Automation-Engine](https://github.com/microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator) | Approval workflows, RFP review agents |
| Azure Policy enforcement | [ALZ policy definitions](https://github.com/Azure/Enterprise-Scale) | Compliance guardrails |

### Phase 4: Parity and Beyond (Weeks 13-16)

| Action | Template/SDK Source | Deliverable |
|--------|-------------------|-------------|
| "Azure Center for Odoo" dashboard | Custom Azure Workbook | Single-pane Odoo health/status/cost view |
| Analytics pipeline | Databricks JDBC + Fabric | Real-time Odoo data in Power BI |
| Multi-region DR | ACA geo-replication + PG read replicas | RPO < 1 hour |
| Publish to azd gallery | [awesome-azd contribution](https://github.com/Azure/awesome-azd) | Public template for community |
| Partner Center listing | [MAICPP enrollment](https://learn.microsoft.com/partner-center/) | ISV marketplace presence |

---

## Key Repository and Documentation Links

### Azure Templates and Samples
- [Awesome azd Gallery](https://azure.github.io/awesome-azd/) | [GitHub](https://github.com/Azure/awesome-azd)
- [azd Template Galleries Documentation](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/azd-template-galleries)
- [azd Templates for Container Apps](https://learn.microsoft.com/azure/container-apps/container-apps-cli-templates)
- [Full-stack azd Templates](https://learn.microsoft.com/azure/developer/azure-developer-cli/full-stack-templates)
- [Azure Landing Zones IaC Accelerator](https://azure.github.io/Azure-Landing-Zones/bicep/gettingstarted/)
- [Azure Verified Modules](https://azure.github.io/Azure-Verified-Modules/)

### Microsoft Foundry and AI
- [Foundry Agent Service Overview](https://learn.microsoft.com/azure/foundry/agents/overview)
- [Foundry Quickstart (Python)](https://learn.microsoft.com/azure/foundry/quickstarts/get-started-code)
- [Agent Framework Foundry Provider](https://learn.microsoft.com/agent-framework/agents/providers/microsoft-foundry)
- [AI Solution Templates](https://learn.microsoft.com/azure/foundry/how-to/develop/ai-template-get-started)
- [Tool Catalog](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-best-practice)
- [foundry-agent-webapp](https://github.com/microsoft-foundry/foundry-agent-webapp)
- [microsoft-foundry-baseline](https://github.com/Azure-Samples/microsoft-foundry-baseline)

### SAP on Azure
- [SAP Landscape Architecture](https://learn.microsoft.com/azure/architecture/guide/sap/sap-whole-landscape)
- [Azure Center for SAP Solutions](https://learn.microsoft.com/azure/sap/center-sap-solutions/overview)
- [SAP Deployment Automation Framework](https://github.com/Azure/sap-automation)
- [SAP Landing Zone Accelerator](https://learn.microsoft.com/azure/cloud-adoption-framework/scenarios/sap/enterprise-scale-landing-zone)
- [Azure Monitor for SAP Solutions](https://learn.microsoft.com/azure/sap/monitor/about-azure-monitor-sap-solutions)

### SAP AI and Copilot
- [SAP Joule AI Assistant](https://www.sap.com/products/artificial-intelligence/ai-assistant.html)
- [SAP Joule + Microsoft Copilot Integration](https://saxon.ai/blogs/when-sap-joule-meets-microsoft-copilot-whats-in-it-for-you/)
- [Microsoft + SAP AI Innovation](https://azure.microsoft.com/en-us/blog/unlock-ai-innovation-with-new-joint-capabilities-from-microsoft-and-sap/)

### Enterprise Patterns
- [Azure Landing Zone Architecture](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/)
- [Azure Landing Zone Deploy Options](https://learn.microsoft.com/azure/architecture/landing-zones/landing-zone-deploy)
- [Cloud Adoption Framework AI Agents](https://learn.microsoft.com/azure/cloud-adoption-framework/ai-agents/technology-solutions-plan-strategy)
- [Document Intelligence for Invoices](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/invoice?view=doc-intel-4.0.0)

---

*Research conducted using Microsoft Learn MCP, web search, and GitHub repository analysis.*
*Confidence levels: Template availability (HIGH), SDK versions (HIGH), SAP architecture details (HIGH), Gap analysis (MEDIUM-HIGH -- some Odoo-specific gaps require validation during implementation).*
