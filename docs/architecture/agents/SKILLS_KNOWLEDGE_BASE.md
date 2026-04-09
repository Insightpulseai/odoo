# Agent Skills & Knowledge Base Architecture

> **Status**: Approved
> **Date**: 2026-03-22
> **Platform**: Azure AI Foundry Agent Service + Foundry IQ

---

## Architecture Position

```
Databricks (governed data)
    ↓ gold marts / Unity Catalog
Foundry IQ (managed knowledge base)
    ↓ agentic retrieval (MCP)
Foundry Agent Service (agent runtime)
    ↓ tools + skills
User surfaces (Odoo copilot, web, Teams)
```

## Knowledge Base Strategy — Foundry IQ

Foundry IQ is the managed knowledge layer. It provides:
- Multi-source knowledge bases (ADLS, SharePoint, OneLake, web)
- Automated chunking, vector embedding, metadata extraction
- Agentic retrieval: query decomposition → parallel search → rerank → synthesize
- Permission-aware responses via Entra identity
- MCP-based connection to Foundry Agent Service

### Knowledge Sources

| Source | Type | Content | Index |
|--------|------|---------|-------|
| `stipaidevlake/gold/` | ADLS Gen2 | Databricks gold marts (finance, PPM, projects) | `gold-marts-kb` |
| `odoo18-docs/` | Blob Storage | Odoo CE 18 documentation (RST-chunked) | `odoo18-docs` |
| `org-docs/` | Blob Storage | Architecture, contracts, specs, runbooks | `org-docs` |
| `azure-platform-docs/` | Blob Storage | Azure platform documentation | `azure-platform-docs` |
| Odoo ERP (federated) | Lakehouse Federation | Live ERP data via Unity Catalog | `odoo-erp-federated` |

### Knowledge Base Definitions

| Knowledge Base | Sources | Agents | Purpose |
|---------------|---------|--------|---------|
| `ipai-finance-kb` | gold-marts-kb, odoo-erp-federated | Finance copilot, PPM agent | Budget, forecast, risk, close status |
| `ipai-platform-kb` | org-docs, azure-platform-docs | Platform agent, ops agent | Architecture, contracts, runbooks |
| `ipai-odoo-kb` | odoo18-docs, odoo-erp-federated | Odoo copilot | Module docs, config help, ERP queries |

## Agent Skills — Tool Catalog

### Built-in Tools (Foundry Agent Service)

| Tool | Use | Status |
|------|-----|--------|
| **Foundry IQ / Azure AI Search** | Grounded RAG over knowledge bases | Target |
| **Code Interpreter** | Python analysis, chart generation | Target |
| **File Search** | Document-level retrieval | Target |
| **Web Search** | Real-time web grounding | Optional |
| **Function Calling** | Custom Odoo/Databricks tool dispatch | Target |

### Custom Tools (MCP + OpenAPI)

| Tool | Type | Endpoint | Purpose |
|------|------|----------|---------|
| `read_record` | OpenAPI → Odoo JSON-RPC | `/ipai/copilot/chat` | Read Odoo records |
| `search_records` | OpenAPI → Odoo JSON-RPC | `/ipai/copilot/chat` | Search Odoo models |
| `ask_copilot` | SQL UDF → Databricks | `platinum.ask_copilot()` | Ad-hoc finance analysis |
| `get_report` | OpenAPI → Odoo | Report metadata | Odoo report generation |
| `search_gold_marts` | Databricks SQL | SQL Warehouse | Direct gold mart queries |

### Agent-to-Agent (A2A)

| Agent | Role | Protocol |
|-------|------|----------|
| Finance Copilot | Budget/forecast/close analysis | A2A (preview) |
| Platform Agent | Architecture/contract queries | A2A (preview) |
| Odoo Copilot | ERP record queries | MCP → Odoo |

## Agent Definitions

### 1. Finance Copilot Agent

```yaml
name: ipai-finance-copilot
model: gpt-4o
instructions: >
  You are a finance analyst for InsightPulse AI. Answer questions about
  budgets, forecasts, risks, and project financials using the finance
  knowledge base. Always cite sources.
tools:
  - foundry_iq:
      knowledge_base: ipai-finance-kb
  - code_interpreter: true
  - function_calling:
      - ask_copilot
      - read_record
      - search_records
```

### 2. Platform Agent

```yaml
name: ipai-platform-agent
model: gpt-4o
instructions: >
  You are a platform engineering assistant. Answer questions about
  architecture, contracts, SSOT, and infrastructure using the platform
  knowledge base.
tools:
  - foundry_iq:
      knowledge_base: ipai-platform-kb
  - web_search: true
```

### 3. Odoo Copilot Agent

```yaml
name: ipai-odoo-copilot
model: gpt-4o
instructions: >
  You are an Odoo 18 CE expert. Help users with module configuration,
  data queries, and ERP operations. Use the Odoo knowledge base for
  documentation and the ERP tools for live data.
tools:
  - foundry_iq:
      knowledge_base: ipai-odoo-kb
  - function_calling:
      - read_record
      - search_records
      - get_report
```

## Testing Strategy — Azure Test Plans

### Test Plan Structure

```
Test Plan: Agent Skills Validation
├── Suite: Knowledge Base Grounding
│   ├── TC-001: Finance KB returns budget data with citations
│   ├── TC-002: Platform KB returns architecture docs
│   └── TC-003: Odoo KB returns module documentation
├── Suite: Tool Execution
│   ├── TC-010: read_record returns Odoo partner data
│   ├── TC-011: search_records filters by company scope
│   ├── TC-012: ask_copilot returns budget analysis
│   └── TC-013: get_report returns report metadata
├── Suite: Permission Enforcement
│   ├── TC-020: Tenant-scoped queries return only tenant data
│   ├── TC-021: Blocked models are rejected
│   └── TC-022: Read-only mode blocks write tools
└── Suite: Agent Integration
    ├── TC-030: Finance copilot answers budget questions
    ├── TC-031: Platform agent answers architecture questions
    └── TC-032: Odoo copilot answers module questions
```

### Automated Test Integration

Azure Test Plans links to Azure Pipelines for automated test execution:

```yaml
# In azure-pipelines.yml
- task: PublishTestResults@2
  inputs:
    testResultsFormat: JUnit
    testResultsFiles: '**/test-results/*.xml'
    testRunTitle: 'Agent Skills Validation'
```

## Implementation Phases

### Phase 1 — Knowledge Base Setup
- Create Azure AI Search indexes for gold marts, Odoo docs, org docs
- Create Foundry IQ knowledge bases
- Connect knowledge sources to indexes
- Validate agentic retrieval with test queries

### Phase 2 — Agent Definitions
- Create Finance Copilot agent in Foundry
- Create Platform Agent in Foundry
- Upgrade Odoo Copilot to use Foundry Agent Service
- Connect agents to knowledge bases via MCP

### Phase 3 — Tool Registration
- Register Odoo tools as OpenAPI/function-calling tools
- Register Databricks SQL tools
- Configure tool permissions per agent
- Validate tool execution with test cases

### Phase 4 — Testing & Evaluation
- Create Azure Test Plans test suites
- Build automated eval pipeline (Foundry evals)
- Integrate test results with Azure Pipelines
- Track quality metrics in Azure DevOps dashboards

### Phase 5 — Production Promotion
- Deploy agents via Foundry Agent Service
- Connect to Odoo systray (existing copilot module)
- Monitor with App Insights telemetry
- Gate promotion on eval scores

## IQ Ecosystem Alignment

| IQ Workload | Scope | Our Use |
|-------------|-------|---------|
| **Foundry IQ** | Enterprise data (ADLS, SharePoint, web) | Primary knowledge layer |
| **Fabric IQ** | Analytics (OneLake, Power BI semantic models) | Future: BI-grounded agents |
| **Work IQ** | M365 collaboration signals | Future: if M365 Copilot adopted |
