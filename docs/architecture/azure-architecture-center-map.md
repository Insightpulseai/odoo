# Azure Architecture Center — IPAI Stack Full Map

**Status**: canonical
**Authority**: [ssot/architecture/azure-architecture-center-map.yaml](../../ssot/architecture/azure-architecture-center-map.yaml)
**Upstream**: https://learn.microsoft.com/azure/architecture/

---

## Canonical summary (one sentence)

> IPAI stack maps to Azure Architecture Center as a **landing-zone-based,
> Entra-secured, Azure Container Apps-hosted enterprise web + ERP + agentic
> AI architecture**, with **Foundry chat/agent baselines** for the AI runtime
> and a **Databricks/Fabric lakehouse + BI plane** for analytics.

---

## Stack-to-architecture matrix

| IPAI layer | Canonical repo/path | Azure Architecture Center lane | Best-fit reference |
|---|---|---|---|
| Platform foundation | [infra/](../../infra/), [platform/](../../platform/) | Landing zone / Well-Architected | CAF + WAF |
| Identity | [ssot/identity/](../../ssot/identity/) | Identity architecture design | Identity in multitenant architectures |
| Public sites | [web/](../../web/) (`insightpulseai.com`, `w9studio.net`) | Enterprise web app patterns | Securely managed web apps |
| ERP | [addons/](../../addons/) (`erp.insightpulseai.com`) | Web app + database workload | Choose container service + DB guidance |
| Agent runtime | [agent-platform/](../../agent-platform/) | AI architecture design | Foundry chat baseline + agent orchestration |
| Agent definitions | [agents/](../../agents/) | AI workload app design support | Agent orchestration / eval support |
| Retrieval | `agent-platform/src/agent_platform/retrieval/` | RAG architecture | Develop + optimize a RAG implementation |
| Data intelligence | [data-intelligence/](../../data-intelligence/) | Analytics architecture design | Databricks modern analytics + Fabric analytics |
| BI / semantic | Fabric / BI outputs | Enterprise BI with Fabric | Analytics end-to-end with Fabric |
| Domain AI workspace | `web/apps/prismalab/` | AI app + RAG + document workflows | Foundry chat baseline + multimodal/document |
| Edge / API protection | [infra/](../../infra/) + gateways | Secure web apps / API protection | App Gateway + API Management |
| Security posture | all | Security architecture design | Zero-trust / secure managed apps |

---

## Target operating model

### Control planes

| Concern | Owner |
|---|---|
| Identity | Entra ID |
| Infrastructure | Azure landing zone + `infra/` |
| Application | `platform/` |
| AI runtime | `agent-platform/` |
| Analytics | `data-intelligence/` |

### User-facing planes

| Surface | Domain |
|---|---|
| Corporate / platform front door | [www.insightpulseai.com](https://www.insightpulseai.com) |
| ERP front door | [erp.insightpulseai.com](https://erp.insightpulseai.com) |
| Domain AI workspace | [prismalab.insightpulseai.com](https://prismalab.insightpulseai.com) |
| Studio / creative front door | [www.w9studio.net](https://www.w9studio.net) |

### System-of-record planes

| Plane | Technology |
|---|---|
| Transactional SoR | Odoo / PostgreSQL |
| Analytics lakehouse / semantic | Databricks + Fabric + Power BI |
| Agent runtime / retrieval | Foundry-backed AI runtime |

---

## 12 architecture lanes

### 01. Platform foundation
**AAC**: Landing zone / Well-Architected
**Repos**: `infra/`, `platform/`
Owns: naming/subscription structure, policy + RBAC, private-networking stance, workload isolation, cost + operational guardrails. See [production-foundation adoption](production-ai-foundation-adoption.md).

### 02. Identity and access
**AAC**: Identity architecture design
**SSOT**: [entra_target_state.yaml](../../ssot/identity/entra_target_state.yaml)
Three-authority model: Zoho/Google = mailbox, Entra = workforce/admin/guest/app, Entra B2B = external.

### 03. Public edge and web security
**AAC**: Enterprise web app patterns / Secure web apps
**SSOT**: [site-template-adoption.yaml](../../ssot/web/site-template-adoption.yaml)
Four surfaces: ERP (no template), IPAI (Get started with AI agents), PrismaLab (agents + multimodal/doc), W9Studio (Get Started with Chat). Consider **Backends for Frontends** if separate BFFs needed for ERP-adjacent UI, PrismaLab, and public web.

### 04. Compute / runtime
**AAC**: Choose a container service / Azure Container Apps
**Target**: Azure Container Apps for Odoo-adjacent services, agent runtime, web/API. Avoid AKS unless there's a genuine Kubernetes control-plane need.

### 05. ERP / transactional
**AAC**: Enterprise web app + database workload
**Repo**: `addons/`, domain `erp.insightpulseai.com`
Role clarity: transactional SoR only — **not** agent runtime, analytics, or marketing frontend.

### 06. AI runtime and copilots
**AAC**: AI architecture design / Foundry chat baseline / AI agent orchestration
**SSOT**: [agent_framework_adoption.yaml](../../ssot/agent-platform/agent_framework_adoption.yaml)
Home for `agent-platform/`, model/provider abstraction, orchestration, grounded/cited responses, tool-calling, handoff design. MAF runtime substrate with Foundry as default provider.

### 07. Retrieval / grounding / knowledge
**AAC**: RAG implementation
**Modules**: `agent-platform/src/agent_platform/{retrieval,attachments,tools/docintel}/`
Home for search/index design, reranking, citations, document-centric domain assistants (PrismaLab).

### 08. Data intelligence / lakehouse / BI
**AAC**: Analytics architecture design
**Repo**: `data-intelligence/`
**Invariant (CLAUDE.md #9, #13)**: Databricks + Unity Catalog = primary engineering plane; Fabric = mirroring/OneLake complement; Power BI = primary BI surface.

### 09. Real-time / evented ops
**AAC**: Event and stream architecture
**Status**: deferred until clear use case. Rule: route runtime exhaust to analytics plane, never mix streaming infra into transactional repos.

### 10. Multitenancy / client isolation
**AAC**: SaaS and multitenant applications
**Current posture**: single operator tenant + selected B2B guests + multiple product domains. Not yet a generalized SaaS multitenant platform.

### 11. Security / zero trust
**AAC**: Security architecture design
Cross-cutting: CA/MFA/PIM, WAF, API protection, secrets + MI, content safety, Foundry access governance. Covers public site protection, ERP isolation, agent backend auth, admin access constraints.

### 12. Application design patterns
**AAC**: Architecture fundamentals / Cloud design patterns
Most relevant: Backends for Frontends, AI workload application design, agent/chat baselines, standard cloud design patterns (resiliency, decomposition, async boundaries).

---

## Non-goals

- Not merging transactional (Odoo) with analytics (Databricks/Fabric).
- Not placing agent runtime inside `web/` or `addons/`.
- Not starting from streaming/event architecture without a clear use case.
- Not adopting generalized multitenant SaaS before a real tenant-per-customer requirement.
- Not escalating compute substrate to AKS without genuine Kubernetes need.

---

## Related doctrine

| Topic | SSOT | Doc |
|---|---|---|
| Entra identity 3-authority model | [entra_target_state.yaml](../../ssot/identity/entra_target_state.yaml) | [identity-architecture.md](identity-architecture.md) |
| MAF runtime adoption | [agent_framework_adoption.yaml](../../ssot/agent-platform/agent_framework_adoption.yaml) | [agent-framework-adoption.md](agent-framework-adoption.md) |
| 3-layer agent delivery stack | [agent_delivery_stack.yaml](../../ssot/agent-platform/agent_delivery_stack.yaml) | — |
| Public site template adoption | [site-template-adoption.yaml](../../ssot/web/site-template-adoption.yaml) | [site-template-adoption.md](site-template-adoption.md) |
| Production foundation accelerator | [production-ai-foundation-adoption.yaml](../../ssot/governance/production-ai-foundation-adoption.yaml) | [production-ai-foundation-adoption.md](production-ai-foundation-adoption.md) |
| Foundry chat baseline (subset mapping) | — | [FOUNDRY_CHAT_BASELINE_MAPPING.md](FOUNDRY_CHAT_BASELINE_MAPPING.md) |

---

## References

- Azure Architecture Center root: https://learn.microsoft.com/azure/architecture/
- Cloud Adoption Framework: https://learn.microsoft.com/azure/cloud-adoption-framework/
- Well-Architected Framework: https://learn.microsoft.com/azure/well-architected/
- Foundry chat baseline: https://learn.microsoft.com/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat
- RAG design and evaluation: https://learn.microsoft.com/azure/architecture/ai-ml/guide/rag/rag-solution-design-and-evaluation-guide
- Backends for Frontends: https://learn.microsoft.com/azure/architecture/patterns/backends-for-frontends
- Multitenant guidance: https://learn.microsoft.com/azure/architecture/guide/multitenant/
