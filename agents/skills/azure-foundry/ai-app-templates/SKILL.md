# Skill: Azure AI App Templates

## Metadata

| Field | Value |
|-------|-------|
| **id** | `azure-ai-app-templates` |
| **domain** | `azure_foundry` |
| **source** | https://learn.microsoft.com/en-us/azure/developer/ai/intelligent-app-templates |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, infra, web |
| **tags** | templates, rag, chat, multi-agent, aca, azd, reference-architecture |

---

## What They Are

Production-ready reference implementations for AI apps on Azure. Two categories: **building blocks** (focused patterns) and **end-to-end solutions** (full deployable apps). All deploy via `azd up`.

Gallery: https://azure.github.io/ai-app-templates/

## Key Templates (Python)

### End-to-End Solutions

| Template | Repo | Stack | AI Models | Relevance |
|----------|------|-------|-----------|-----------|
| **Chat with your data (RAG)** | `azure-search-openai-demo` | ACA, Azure AI Search, Blob, Document Intelligence | GPT-4o, GPT-4o-mini | **High** — same RAG pattern as ipai-odoo-copilot |
| **Contoso Chat Retail Copilot** | `contoso-chat` | ACA, Foundry, Cosmos DB, AI Search, Prompty | GPT-4, GPT-3.5 | **High** — RAG + eval + FastAPI + GenAIOps |
| **Multi-Agent Creative Writing** | `agent-openai-python-prompty` | AKS, AI Search, Bing, Foundry | GPT-4, DALL-E | **Medium** — multi-agent pattern reference |
| **Speech-to-Text Summarization** | `summarization-openai-python-promptflow` | ACA, Foundry, Speech | GPT-3.5 | **Low** — not in current scope |
| **Assistant API Analytics** | `assistant-data-openai-python-promptflow` | ML Service, AI Search, Foundry | GPT-4 | **Low** — analytics copilot pattern |

### Building Blocks (Python)

| Block | Description | Relevance |
|-------|-------------|-----------|
| **Document security for RAG** | Permission-aware answers — authorized vs unauthorized content | **High** — need for multi-tenant Odoo |
| **Evaluate chat answers** | Eval against ground truth, compare before/after changes | **High** — extends our eval pattern |
| **Load balance with ACA** | 3 Azure OpenAI endpoints behind ACA load balancer | **Medium** — useful at scale |
| **Load balance with APIM** | Same pattern via API Management | **Medium** — aligns with AI gateway plan |
| **Load test with Locust** | Simulate users, find TPM bottlenecks | **Medium** — needed before production |
| **Keyless auth** | Passwordless Azure connections | **High** — aligns with managed identity |

### Key Templates (Java)

| Template | Repo | Notable |
|----------|------|---------|
| **Multi-Agent Banking Assistant** | `agent-openai-java-banking-assistant` | Uses Document Intelligence for invoice OCR + payment agent. **Very relevant** — same pattern as expense OCR → Odoo |

## Architecture Pattern (RAG Chat App)

```
Client (React/Next.js)
    ↓
Backend (FastAPI on ACA)
    ├── Azure OpenAI (GPT-4o) — reasoning
    ├── Azure AI Search — retrieval (vector + semantic)
    ├── Azure Document Intelligence — document processing
    └── Azure Blob Storage — source documents
```

## IPAI Adoption Priority

| Template | Why | Action |
|----------|-----|--------|
| `azure-search-openai-demo` | Reference RAG pattern for ipai-odoo-copilot | Fork and adapt for Odoo/OCA/BIR docs |
| Document security block | Multi-tenant permission-aware RAG | Study pattern for tenant isolation |
| Eval block | Ground truth evaluation | Integrate with cloud-evaluation skill |
| Banking Assistant (Java) | Invoice OCR → payment agent | Reference for expense-processing skill |
| Keyless auth block | Managed identity pattern | Already aligned, validate implementation |

## `azd` Deployment Pattern

All templates use Azure Developer CLI:

```bash
# Clone template
azd init -t azure-search-openai-demo

# Provision + deploy
azd up

# Clean up
azd down
```

This maps to IPAI's Bicep + GitHub Actions deployment — `azd` could simplify Foundry copilot deployment.

## Foundry Solution Templates (Portal)

Source: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/ai-template-get-started

Available via Foundry portal → Discover → Solution Templates.

| Template | GitHub Repo | Use Cases | IPAI Relevance |
|----------|------------|-----------|----------------|
| **Get started with AI chat** | `Azure-Samples/get-started-with-ai-chat` | Interactive chat apps, baseline RAG | **High** — copilot baseline |
| **Get started with AI agents** | `Azure-Samples/get-started-with-ai-agents` | Autonomous AI agents | **High** — agent bootstrap |
| **Agentic apps for unified data** | `microsoft/agentic-applications-for-unified-data-foundation-solution-accelerator` | Sales analytics, customer insights, NL on structured data | **High** — Databricks + Odoo analytics |
| **Multi-agent release manager** | `Azure-Samples/openai/.../release_manager` | Release coordination, dependency mapping, health assessment | **Medium** — ops automation pattern |
| **Call center voice agent** | `Azure-Samples/call-center-voice-agent-accelerator` | Customer support, product catalog, self-service | **Low** — no voice use case yet |
| **Conversation knowledge mining** | `microsoft/Conversation-Knowledge-Mining-Solution-Accelerator` | Extract knowledge from conversations | **Medium** — Slack/Teams mining |
| **Multi-agent workflow automation** | `microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator` | Complex workflow automation | **High** — maps to n8n→agent pattern |
| **Multi-modal content processing** | `microsoft/content-processing-solution-accelerator` | Process diverse content types (docs, images, audio) | **High** — invoice/receipt/BIR processing |
| **Document generation** | `microsoft/document-generation-solution-accelerator` | Auto-generate documents from data | **Medium** — BIR form generation |
| **Client meeting copilot** | `microsoft/Build-your-own-copilot-Solution-Accelerator` | Meeting productivity | **Low** — not in scope |
| **Code modernization** | `microsoft/Modernize-your-code-solution-accelerator` | Legacy code updates | **Low** — no legacy codebase |
| **Conversational agent** | `Azure-Samples/Azure-Language-OpenAI-Conversational-Agent-Accelerator` | Conversational experiences | **Medium** — copilot patterns |
| **SharePoint retrieval** | `microsoft/app-with-sharepoint-knowledge` | Retrieve + summarize SharePoint data | **Medium** — if M365 integration needed |

### Template → IPAI Repo Mapping (per runtime strategy)

| Template | IPAI Target Repo |
|----------|-----------------|
| Get started with AI agents | `agents/` |
| Get started with AI chat | `web/` |
| Multi-agent workflow automation | `agents/` + `automations/` |
| Multi-modal content processing | `odoo/` (document flows) |
| Agentic apps for unified data | `lakehouse/` |
| Multi-agent release manager | `ops-platform/` |
| Document generation | `odoo/` (BIR forms) |

### Usage

```bash
# From Foundry portal: Discover → Solution Templates → Open in GitHub
# Or clone directly:
git clone https://github.com/Azure-Samples/get-started-with-ai-agents.git
cd get-started-with-ai-agents
azd up
```

**Rule** (from `org__foundry__runtime_strategy__v1.policy.yaml`): Templates are **bootstrap sources only** — extract patterns, don't deploy tutorial code to production.

---

## azd (Azure Developer CLI) Templates

Source: https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/azd-templates
Gallery: https://azure.github.io/awesome-azd/

### What azd Templates Are

Standard code repos with `azd` config + IaC files. One command (`azd up`) provisions Azure resources + deploys app code. Supports Bicep and Terraform.

### azd Template Structure

```
my-template/
├── infra/                    # Bicep or Terraform IaC
│   ├── main.bicep            # Root infrastructure
│   └── modules/              # Resource modules
├── src/                      # Application source code
│   ├── api/                  # Backend
│   └── web/                  # Frontend
├── azure.yaml                # Maps src folders → Azure resources
├── .azure/                   # Environment configs + vars
├── .github/                  # GitHub Actions CI/CD
│   └── workflows/
├── .azdo/                    # Azure Pipelines (optional)
├── .devcontainer/            # Dev Container config (optional)
└── README.md
```

### Key Files

| File | Purpose |
|------|---------|
| `azure.yaml` | Maps source code folders to Azure resources for deployment |
| `infra/main.bicep` | Root Bicep template defining all Azure resources |
| `.azure/` | Environment variables, subscription info, deploy state |

### azd Workflow

```bash
# 1. Clone template
azd init --template <template-name>

# 2. Authenticate
azd auth login

# 3. Provision + deploy (one command)
azd up

# 4. Iterate locally, then redeploy
azd up

# 5. Clean up
azd down
```

### azd Starter Templates (IaC-Only)

| Template | Repo | IaC |
|----------|------|-----|
| **Bicep Starter** | `Azure-Samples/azd-starter-bicep` | Bicep + devcontainer + CI/CD |
| **Terraform Starter** | `Azure-Samples/azd-starter-terraform` | Terraform + devcontainer + CI/CD |

### azd App Templates (Python)

| Template | Host | Stack |
|----------|------|-------|
| React + Python API + MongoDB | App Service | Cosmos DB MongoDB, Bicep |
| React + Python API + MongoDB (Terraform) | App Service | Cosmos DB MongoDB, Terraform |
| Containerized React + Python API + MongoDB | **ACA** | Cosmos DB MongoDB, Bicep |
| Static React + Functions + Python API + MongoDB | Static Web Apps + Functions | Cosmos DB MongoDB, Bicep |

### azd App Templates (Node.js)

| Template | Host | Stack |
|----------|------|-------|
| React + Node.js API + MongoDB | App Service | Cosmos DB MongoDB, Bicep |
| React + Node.js API + MongoDB (Terraform) | App Service | Cosmos DB MongoDB, Terraform |
| Containerized React + Node.js API + MongoDB | **ACA** | Cosmos DB MongoDB, Bicep |
| Static React + Functions + Node.js API + MongoDB | Static Web Apps + Functions | Cosmos DB MongoDB, Bicep |
| Kubernetes React + Node.js API + MongoDB | **AKS** | Cosmos DB MongoDB, Bicep |

### azd App Templates (C# / Java)

| Template | Host | Stack |
|----------|------|-------|
| C# + Cosmos SQL | App Service | Cosmos DB SQL, Bicep |
| C# + SQL Database | App Service | Azure SQL, Bicep |
| C# Static + Functions + SQL | Static Web Apps + Functions | Azure SQL, Bicep |
| Java + MongoDB | App Service | Cosmos DB MongoDB, Bicep |
| Java Containerized + MongoDB | **ACA** | Cosmos DB MongoDB, Bicep |

---

## IPAI azd Adoption Recommendation

### Which Templates to Fork

| IPAI Repo | Recommended azd Template | Why |
|-----------|------------------------|-----|
| `agents/` | `get-started-with-ai-agents` | Agent bootstrap with Foundry SDK |
| `web/` | `get-started-with-ai-chat` | RAG chat baseline for ops console |
| `odoo/` | `content-processing-solution-accelerator` | Multi-modal doc processing (invoices, BIR) |
| `lakehouse/` | `agentic-applications-for-unified-data-foundation` | Analytics + NL queries on structured data |
| `infra/` | `azd-starter-bicep` | IaC foundation with CI/CD |

### azd for IPAI Deployment

Current IPAI deployment: Bicep + GitHub Actions → ACA.
azd adds: single-command deploy, environment management, template standardization.

```bash
# Example: deploy Foundry copilot
azd init --template get-started-with-ai-agents
# Customize: replace sample agent with ipai-odoo-copilot config
# Edit azure.yaml to map to our infra/azure/modules/
azd up --environment dev
```

### azd vs Current Bicep + GitHub Actions

| Aspect | Current (Bicep + GHA) | azd |
|--------|----------------------|-----|
| Provisioning | `az deployment group create` | `azd up` |
| Multi-env | Manual per env | `azd env select dev/staging/prod` |
| App deploy | GHA workflow → ACA revision | `azd deploy` (automatic) |
| Template sharing | Custom scripts | `azd init --template` |
| Clean up | Manual `az group delete` | `azd down` |

**Recommendation**: Adopt `azd` for new Foundry-specific resources (AI projects, model deployments). Keep Bicep + GHA for ACA/networking/security where more control is needed. They're complementary.
