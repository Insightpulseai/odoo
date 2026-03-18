# Azure Sample Code Catalog — Benchmark Knowledge Base

> **Doctrine**: Sample catalog entries are implementation fixtures, NOT architecture doctrine.
> Extract patterns into contracts before standardizing. Never adopt samples wholesale.

---

## Source

- [Azure Samples GitHub Organization](https://github.com/azure-samples)
- [Azure Sample Catalog](https://azure.microsoft.com/en-us/resources/samples/)
- [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/)

---

## How to Use This Knowledge Base

1. **Browse** the sample catalog for patterns matching your workload
2. **Evaluate** each sample for secure-by-default posture
3. **Extract** the pattern using the `sample-to-contract-extraction` skill
4. **Adapt** to the canonical platform stack (ACA, Azure PG, Key Vault, Front Door)
5. **Never** copy a sample wholesale — extract the pattern, discard the scaffold

---

## Highest-Value Pattern Categories

### 1. Secure-by-Default Azure Functions

**Samples**:
- `azure-samples/functions-quickstart-python-azd` — Python Functions + azd + Flex Consumption
- `azure-samples/functions-quickstart-dotnet-azd` — C# Functions + azd + Flex Consumption
- `azure-samples/functions-quickstart-typescript-azd` — TypeScript Functions + azd

**Pattern**: Flex Consumption plan + managed identity + VNet + azd deployment
**Secure defaults**: Managed identity for downstream access, VNet integration, no API keys
**Platform relevance**: Event-driven workloads (timers, webhooks, event processors)

### 2. Entra-Authenticated AI Apps

**Samples**:
- `azure-samples/openai-chat-app-entra-auth-builtin` — OpenAI + Entra + built-in auth
- `azure-samples/openai-chat-app-entra-auth-local` — OpenAI + Entra + local auth
- `azure-samples/azure-search-openai-demo` — RAG + OpenAI + Entra

**Pattern**: ACA/App Service app → managed identity → Entra token → Azure OpenAI
**Secure defaults**: Keyless access, managed identity, no API key fallback
**Platform relevance**: AI copilot, RAG, chat interfaces — directly relevant to Odoo AI integration

### 3. Full-Stack ACA Templates

**Samples**:
- `azure-samples/todo-python-mongo-aca` — Python + MongoDB + ACA
- `azure-samples/todo-nodejs-mongo-aca` — Node.js + MongoDB + ACA
- `azure-samples/todo-csharp-sql` — C# + SQL + ACA

**Pattern**: Frontend + API + database on ACA with azd
**Secure defaults**: Varies — check each for managed identity and VNet
**Platform relevance**: ACA deployment patterns, registry integration, scaling

### 4. Data Integration Patterns

**Samples**:
- `azure-samples/cosmos-db-change-feed-dotnet` — Cosmos DB change feed processing
- `azure-samples/event-grid-dotnet-publish-consume` — Event Grid pub/sub
- `azure-samples/service-bus-dotnet-messaging` — Service Bus messaging

**Pattern**: Event-driven data processing with managed services
**Secure defaults**: Check for managed identity vs connection strings
**Platform relevance**: Event-driven architecture, data pipeline triggers

### 5. Infrastructure as Code Patterns

**Samples**:
- `azure-samples/aca-bicep-templates` — ACA Bicep patterns
- `azure-samples/azure-quickstart-templates` — ARM/Bicep quick starts
- `azure-samples/terraform-azure-modules` — Terraform modules

**Pattern**: IaC patterns for Azure resources
**Secure defaults**: Varies — always verify managed identity and VNet
**Platform relevance**: Infrastructure provisioning patterns

---

## Extraction Workflow

```
1. Identify sample → 2. Review structure → 3. Audit security → 4. Abstract pattern
→ 5. Check platform alignment → 6. Draft contract → 7. Register in index
```

Use the `sample-to-contract-extraction` skill for systematic extraction.

---

## Anti-Patterns

| Anti-Pattern | Why It's Wrong | Correct Approach |
|-------------|----------------|------------------|
| Copy entire sample repo | Brings scaffold, dependencies, opinions | Extract pattern only |
| Use sample's auth model directly | May use API keys or old patterns | Verify and adapt to Entra/MI |
| Skip security audit | Sample may have insecure defaults | Always audit MI, VNet, keyless |
| Treat sample as architecture | Samples are fixtures, not doctrine | Extract pattern into contract |
| Ignore platform deviations | Sample may target App Service | Adapt to canonical ACA stack |

---

## Cross-references

- `agents/personas/sample-fixture-curator.md`
- `agents/skills/sample-to-contract-extraction/`
- `agents/skills/azd-template-selection/`
- `agents/knowledge/benchmarks/azure-developer-cli.md`
