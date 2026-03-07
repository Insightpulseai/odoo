# Microsoft Azure Architecture Center & Assessments — Deep Research Index

**Date**: 2026-03-07
**Context**: Building architecture expertise for InsightPulse AI stack — patterns, frameworks, and assessments applicable to self-hosted infrastructure
**Note**: While Azure-specific, these frameworks encode **platform-agnostic architectural wisdom** applicable to any cloud or self-hosted deployment

---

## Table of Contents

1. [Azure Architecture Center — Structure](#1-azure-architecture-center--structure)
2. [Cloud Design Patterns — Complete Catalog](#2-cloud-design-patterns--complete-catalog)
3. [Architecture Styles](#3-architecture-styles)
4. [Well-Architected Framework — 5 Pillars](#4-well-architected-framework--5-pillars)
5. [Cloud Adoption Framework — 7 Phases](#5-cloud-adoption-framework--7-phases)
6. [Technology Choice Decision Trees](#6-technology-choice-decision-trees)
7. [Reference Architectures by Domain](#7-reference-architectures-by-domain)
8. [Industry Solutions](#8-industry-solutions)
9. [Microsoft Assessments — Complete Catalog](#9-microsoft-assessments--complete-catalog)
10. [Self-Hosted Applicability Matrix](#10-self-hosted-applicability-matrix)

---

## 1. Azure Architecture Center — Structure

**URL**: [learn.microsoft.com/en-us/azure/architecture/](https://learn.microsoft.com/en-us/azure/architecture/)

### Top-Level Sections

| Section | URL | Description |
|---------|-----|-------------|
| **Browse All** | [/browse/](https://learn.microsoft.com/en-us/azure/architecture/browse/) | Searchable catalog of all architectures |
| **Design Patterns** | [/patterns/](https://learn.microsoft.com/en-us/azure/architecture/patterns/) | 40+ cloud design patterns |
| **Architecture Styles** | [/guide/architecture-styles/](https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/) | Microservices, event-driven, N-tier, etc. |
| **Technology Choices** | [/guide/technology-choices/](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/technology-choices-overview) | Decision trees for compute, data, messaging |
| **App Architecture Guide** | [/guide/](https://learn.microsoft.com/en-us/azure/architecture/guide/) | Fundamentals guide |
| **Industry Solutions** | [/industries/](https://learn.microsoft.com/en-us/azure/architecture/industries/overview) | Healthcare, finance, retail, manufacturing |
| **What's New** | [/changelog](https://learn.microsoft.com/en-us/azure/architecture/changelog) | Latest updates |
| **GitHub (mspnp)** | [github.com/mspnp](https://github.com/mspnp) | Reference implementations |

### Related Frameworks

| Framework | URL | Relationship |
|-----------|-----|-------------|
| **Well-Architected Framework** | [/azure/well-architected/](https://learn.microsoft.com/en-us/azure/well-architected/) | Quality assessment of workloads |
| **Cloud Adoption Framework** | [/azure/cloud-adoption-framework/](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/) | Strategic migration/adoption guidance |
| **Industry Architecture Center** | [/industry/architecture-center](https://learn.microsoft.com/en-us/industry/architecture-center) | Industry-specific architectures |
| **Microsoft Assessments** | [/assessments/](https://learn.microsoft.com/en-us/assessments/) | Interactive assessment questionnaires |

---

## 2. Cloud Design Patterns — Complete Catalog

**URL**: [learn.microsoft.com/en-us/azure/architecture/patterns/](https://learn.microsoft.com/en-us/azure/architecture/patterns/)

### Full Pattern Index (40+ Patterns)

#### Data Management Patterns

| Pattern | Description | Self-Hosted Applicability |
|---------|-------------|--------------------------|
| **Cache-Aside** | Load data on demand into cache from a data store | High — Redis/Memcached with PostgreSQL |
| **CQRS** | Separate read and write operations into different models | High — Odoo read replicas |
| **Event Sourcing** | Append-only store to record events that describe actions on data | High — PostgreSQL event tables |
| **Index Table** | Create indexes over fields in data stores for queries | High — PostgreSQL indexes |
| **Materialized View** | Generate prepopulated views over data for queries | High — PostgreSQL materialized views |
| **Sharding** | Divide a data store into horizontal partitions | Medium — PostgreSQL partitioning |
| **Static Content Hosting** | Serve static content from a storage service | High — Nginx/MinIO |
| **Valet Key** | Use a token for restricted direct access to a resource | High — Pre-signed URLs (MinIO/S3) |

#### Design & Implementation Patterns

| Pattern | Description | Self-Hosted Applicability |
|---------|-------------|--------------------------|
| **Ambassador** | Create helper services that send network requests on behalf of a consumer | High — Envoy/Nginx sidecar |
| **Anti-Corruption Layer** | Implement a facade between new and legacy systems | High — API gateway layer |
| **Backends for Frontends** | Create separate backends for different client types | Medium — API per client |
| **Compute Resource Consolidation** | Consolidate multiple tasks into a single compute unit | High — Docker multi-service |
| **External Configuration Store** | Move configuration to a centralized location | High — Consul/etcd/.env files |
| **Gateway Aggregation** | Use a gateway to aggregate multiple requests into one | High — Nginx/API gateway |
| **Gateway Offloading** | Offload shared functionality to a gateway proxy | High — Nginx SSL termination |
| **Gateway Routing** | Route requests to multiple services using a single endpoint | High — Nginx reverse proxy |
| **Pipes and Filters** | Break a complex task into reusable elements | High — n8n workflow nodes |
| **Sidecar** | Deploy components of an app into a separate container | High — Docker Compose sidecars |
| **Strangler Fig** | Incrementally migrate a legacy system by replacing pieces | High — Gradual Odoo migration |

#### Messaging Patterns

| Pattern | Description | Self-Hosted Applicability |
|---------|-------------|--------------------------|
| **Asynchronous Request-Reply** | Decouple backend processing from a frontend host | High — Celery/RabbitMQ |
| **Choreography** | Let each service decide when and how a business operation is processed | High — Event-driven with n8n |
| **Claim Check** | Split a large message into a claim check and a payload | Medium — Reference IDs in messages |
| **Competing Consumers** | Enable multiple consumers to process messages concurrently | High — Worker pools |
| **Messaging Bridge** | Connect incompatible messaging systems | High — n8n as bridge |
| **Priority Queue** | Prioritize requests so higher priority received first | High — PostgreSQL priority queues |
| **Publisher/Subscriber** | Enable app to announce events to multiple consumers | High — Supabase Realtime/webhooks |
| **Queue-Based Load Leveling** | Use a queue as a buffer between a task and a service | High — Redis/RabbitMQ queues |
| **Sequential Convoy** | Process a set of related messages in a defined order | Medium — Ordered job queues |
| **Scheduler Agent Supervisor** | Coordinate actions across distributed services | High — MCP Jobs system |

#### Reliability Patterns

| Pattern | Description | Self-Hosted Applicability |
|---------|-------------|--------------------------|
| **Bulkhead** | Isolate elements into pools to prevent cascading failures | High — Docker resource limits |
| **Circuit Breaker** | Handle faults that take variable time to recover from | High — Python circuit breakers |
| **Compensating Transaction** | Undo work performed by a series of steps (saga rollback) | High — Database transaction rollbacks |
| **Health Endpoint Monitoring** | Implement functional checks in an application | High — `/web/health` endpoint |
| **Leader Election** | Coordinate actions by electing a leader instance | Medium — PostgreSQL advisory locks |
| **Quarantine** | Ensure external assets meet quality before consumption | Medium — Input validation layers |
| **Rate Limiting** | Limit the rate of requests to prevent resource exhaustion | High — Nginx rate limiting |
| **Retry** | Retry a failed operation with increasing delays | High — Exponential backoff in code |
| **Saga** | Manage data consistency across microservices | High — n8n saga workflows |
| **Throttling** | Control consumption of resources used by an application | High — Nginx/API rate limits |

#### Security Patterns

| Pattern | Description | Self-Hosted Applicability |
|---------|-------------|--------------------------|
| **Federated Identity** | Delegate authentication to an external identity provider | High — Keycloak SSO |
| **Gatekeeper** | Protect applications using a dedicated host instance | High — Nginx WAF |

#### Other Patterns

| Pattern | Description | Self-Hosted Applicability |
|---------|-------------|--------------------------|
| **Deployment Stamps** | Deploy multiple independent copies of application components | Medium — Multi-tenant Docker |
| **Edge Workload Configuration** | Configure workloads deployed on edge devices | Low — Not applicable |
| **Geode** | Deploy backend services into a set of geographical nodes | Low — Single-region hosting |

### AI Agent Orchestration Patterns (New 2025)

The Azure Architecture Center now includes patterns for **AI workloads with multiple autonomous agents**:

| Pattern | Description | IPAI Relevance |
|---------|-------------|----------------|
| **AI Agent Orchestration** | Coordinate multiple AI agents for complex tasks | Direct — Pulser/Claude agents |
| **Nondeterministic Output Handling** | Handle variable AI outputs | Direct — LLM response handling |
| **Dynamic Reasoning** | Enable AI agents to reason and adapt | Direct — Agent decision-making |

### Sources
- [Cloud Design Patterns](https://learn.microsoft.com/en-us/azure/architecture/patterns/)
- [Cloud Design Patterns - luke.geek.nz](https://luke.geek.nz/azure/cloud-design-patterns/)
- [Cloud Design Patterns - Grounded Architecture](https://grounded-architecture.io/cloud-design-patterns)

---

## 3. Architecture Styles

**URL**: [learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/](https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/)

| Style | Description | When to Use | IPAI Stack Mapping |
|-------|-------------|------------|-------------------|
| **N-Tier** | Traditional layered architecture (presentation, business, data) | Simple apps, legacy migration | Odoo CE (MVC/MVT) |
| **Web-Queue-Worker** | Web frontend + message queue + backend worker | Apps with resource-intensive processing | n8n + MCP Jobs + Supabase |
| **Microservices** | Small, independent services communicating via APIs | Complex domains, frequent updates | MCP servers, apps/ packages |
| **Event-Driven** | Publish-subscribe or event streaming architecture | Real-time, IoT, high-throughput | Supabase Realtime + webhooks |
| **CQRS** | Separate read/write models | Read-heavy with complex writes | Superset (read) + Odoo (write) |
| **Big Data** | Batch and real-time processing of large datasets | Analytics, data lakes | Superset + PostgreSQL |
| **Big Compute** | High-performance computing at scale | ML training, simulations | DO GPU droplets (if needed) |

### IPAI Stack Architecture Style

The InsightPulse AI stack is primarily a **Web-Queue-Worker + Event-Driven hybrid**:

```
[Odoo CE] ---webhooks---> [n8n] ---events---> [MCP Jobs]
    |                       |                      |
    +-- [PostgreSQL] <------+                      |
    +-- [Superset] <-------------------------------+
    +-- [Supabase Realtime] <----------------------+
```

### Sources
- [Architecture Styles](https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/)
- [Event-Driven Architecture](https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/event-driven)
- [Microservices Architecture](https://learn.microsoft.com/en-us/azure/architecture/microservices/)

---

## 4. Well-Architected Framework — 5 Pillars

**URL**: [learn.microsoft.com/en-us/azure/well-architected/](https://learn.microsoft.com/en-us/azure/well-architected/)

### The 5 Pillars

| # | Pillar | Goal | Key Questions | IPAI Self-Hosted Equivalent |
|---|--------|------|---------------|---------------------------|
| 1 | **Reliability** | Meet uptime/recovery targets | Can we recover from failures? What's our RTO/RPO? | PostgreSQL backups, Docker restart policies, health checks |
| 2 | **Security** | Defense-in-depth protection | Is data encrypted? Are identities verified? | Keycloak SSO, Nginx WAF, PostgreSQL RLS, .env secrets |
| 3 | **Cost Optimization** | Reduce unnecessary spend | Are we right-sized? What's utilization? | DO droplet sizing, self-hosted vs SaaS decisions |
| 4 | **Operational Excellence** | Smooth operations at scale | Can we monitor and diagnose? | GitHub Actions CI, n8n monitoring, Superset dashboards |
| 5 | **Performance Efficiency** | Adapt to load changes | Can we scale? Where are bottlenecks? | PostgreSQL tuning, Nginx caching, Docker scaling |

### Each Pillar Provides

- **Design Principles** — Foundational guidance
- **Design Review Checklists** — Actionable verification items
- **Cloud Design Patterns** — Mapped patterns per pillar
- **Tradeoff Analysis** — What you sacrifice for each pillar's gains

### New in 2025: Maturity Models

Microsoft introduced **maturity models** for each pillar — a structured approach to assess current state and identify improvements. Levels typically progress from:
1. **Ad hoc** (no formal processes)
2. **Defined** (documented but inconsistent)
3. **Managed** (consistent, monitored)
4. **Optimized** (continuous improvement, automated)

### New in 2025: Sustainable AI Workloads

Guidance on building AI workloads sustainably — environmental considerations for model design, data design, and operations.

### Well-Architected for Industry

Extended pillar guidance for specific industries:
- **Financial Services** — Regulatory compliance, data sovereignty
- **Healthcare** — HIPAA, patient data protection
- **Retail** — Customer experience, supply chain

### Sources
- [Well-Architected Framework Pillars](https://learn.microsoft.com/en-us/azure/well-architected/pillars)
- [What is Well-Architected](https://learn.microsoft.com/en-us/azure/well-architected/what-is-well-architected-framework)
- [What's New](https://learn.microsoft.com/en-us/azure/well-architected/whats-new)
- [Well-Architected for Industry](https://learn.microsoft.com/en-us/industry/well-architected/overview)

---

## 5. Cloud Adoption Framework — 7 Phases

**URL**: [learn.microsoft.com/en-us/azure/cloud-adoption-framework/](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/)

### Phase Diagram

```
Sequential (Foundation):
  Strategy --> Plan --> Ready --> Adopt
                                   |
Parallel (Operational):            |
  Govern ----+                     |
  Secure ----+-- (continuous) -----+
  Manage ----+
```

### All 7 Phases

| # | Phase | Purpose | Key Activities | Self-Hosted Equivalent |
|---|-------|---------|---------------|----------------------|
| 1 | **Strategy** | Define business justification | Identify drivers, define outcomes, build business case | CLAUDE.md cost philosophy, EE parity goals |
| 2 | **Plan** | Create actionable adoption plan | Catalog workloads, assess readiness, prioritize | Spec bundles, task breakdowns |
| 3 | **Ready** | Prepare technical foundation | Landing zones, IAM, governance baseline | DO droplet setup, Docker Compose, Nginx |
| 4 | **Adopt** | Execute migration/innovation | Migrate (lift-shift) or Innovate (rearchitect) | Odoo CE deployment, ipai_* module development |
| 5 | **Govern** | Implement policies and controls | Governance methodology, compliance, benchmarks | CLAUDE.md rules, CI gates, pre-commit |
| 6 | **Secure** | Enhance security posture | Risk management, defense-in-depth | Keycloak, RLS, GitLeaks, Semgrep |
| 7 | **Manage** | Operational excellence | Monitoring, backup, DR, optimization | Health checks, pg_dump, Docker restart |

### CAF Applicability to Self-Hosted

The CAF methodology is **platform-agnostic in principle** even though Azure-specific in implementation. The phases (Strategy -> Plan -> Ready -> Adopt -> Govern/Secure/Manage) apply to any infrastructure adoption:

| CAF Concept | Azure Implementation | IPAI Self-Hosted Implementation |
|-------------|---------------------|-------------------------------|
| Landing Zone | Azure subscription + resource groups | DO droplet + Docker Compose |
| Identity | Azure AD / Entra ID | Keycloak + Supabase Auth |
| Governance | Azure Policy | CLAUDE.md + CI workflows |
| Monitoring | Azure Monitor | Superset + n8n alerts + health checks |
| Cost Management | Azure Cost Management | DO billing + resource optimization |
| Security Baseline | Microsoft Defender | GitLeaks + Semgrep + Nginx WAF |

### Sources
- [Cloud Adoption Framework Overview](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/overview)
- [CAF on Azure.com](https://azure.microsoft.com/en-us/solutions/cloud-enablement/cloud-adoption-framework)

---

## 6. Technology Choice Decision Trees

**URL**: [learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/technology-choices-overview)

### Decision Trees Available

| Decision Area | URL | Key Decision Points |
|--------------|-----|-------------------|
| **Compute** | [compute-decision-tree](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/compute-decision-tree) | Migrate vs build new, serverless vs containers vs VMs |
| **Data Store** | [data-store-decision-tree](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/data-store-decision-tree) | Relational vs NoSQL vs graph vs time-series |
| **Messaging** | [messaging](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/technology-choices-overview) | Event Grid vs Event Hubs vs Service Bus |
| **AI/ML** | Part of compute tree | GPU vs CPU, managed vs self-hosted |

### Self-Hosted Decision Tree (IPAI Equivalent)

```
Need compute?
  +-- Web app --> Odoo CE (Docker)
  +-- Background jobs --> n8n / MCP Jobs
  +-- AI inference --> DO GPU droplet / HuggingFace
  +-- Static site --> Nginx / Vercel

Need data store?
  +-- Relational --> PostgreSQL 16
  +-- Document/JSON --> Supabase (PostgreSQL + JSONB)
  +-- File storage --> MinIO / Supabase Storage
  +-- Cache --> Redis
  +-- Search --> PostgreSQL FTS / pg_trgm
  +-- Vector --> pgvector (Supabase)

Need messaging?
  +-- Webhooks --> n8n
  +-- Job queue --> MCP Jobs (Supabase)
  +-- Real-time --> Supabase Realtime
  +-- Email --> Zoho Mail Bridge
  +-- Chat --> Slack
```

### Sources
- [Technology Choices Overview](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/technology-choices-overview)
- [Compute Decision Tree](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/compute-decision-tree)
- [Data Store Decision Tree](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/data-store-decision-tree)

---

## 7. Reference Architectures by Domain

**URL**: [learn.microsoft.com/en-us/azure/architecture/browse/](https://learn.microsoft.com/en-us/azure/architecture/browse/)

### Major Categories

| Domain | Example Architectures | Self-Hosted Relevance |
|--------|----------------------|----------------------|
| **Web Applications** | Basic web app, multi-region, serverless | High — Odoo CE + Nginx |
| **Data & Analytics** | Data warehouse, ETL, real-time analytics | High — PostgreSQL + Superset |
| **AI & Machine Learning** | ML ops, RAG, conversational AI | High — Claude/GPT + pgvector |
| **IoT** | IoT hub, edge computing, telemetry | Low — Future roadmap |
| **Identity** | SSO, B2C, multi-tenant auth | High — Keycloak |
| **DevOps** | CI/CD pipelines, GitOps, IaC | High — GitHub Actions |
| **Networking** | Hub-spoke, VPN, DNS | Medium — Cloudflare DNS + DO VPC |
| **Storage** | Blob storage, data lake, backup | High — MinIO + PostgreSQL |
| **Migration** | Legacy modernization, SAP migration | Medium — Odoo EE -> CE migration |
| **SAP** | SAP on Azure, S/4HANA | Low — We use Odoo, not SAP |
| **Security** | Zero Trust, threat protection | High — Keycloak + Nginx + RLS |
| **Containers** | AKS, microservices, service mesh | Medium — Docker Compose |

### Sources
- [Browse Azure Architectures](https://learn.microsoft.com/en-us/azure/architecture/browse/)
- [App Architecture Guide](https://learn.microsoft.com/en-us/azure/architecture/guide/)

---

## 8. Industry Solutions

**URL**: [learn.microsoft.com/en-us/azure/architecture/industries/overview](https://learn.microsoft.com/en-us/azure/architecture/industries/overview)

| Industry | URL | Key Focus Areas |
|----------|-----|----------------|
| **Healthcare** | [/industries/healthcare](https://learn.microsoft.com/en-us/azure/architecture/industries/healthcare) | HIPAA, patient data, clinical workflows |
| **Financial Services** | [/industries/finance](https://learn.microsoft.com/en-us/azure/architecture/industries/finance) | Regulatory compliance, fraud detection, risk |
| **Retail** | [/industries/retail](https://learn.microsoft.com/en-us/azure/architecture/industries/retail) | Customer experience, supply chain, POS |
| **Manufacturing** | [/industries/manufacturing](https://learn.microsoft.com/en-us/azure/architecture/industries/manufacturing) | IoT, predictive maintenance, quality |
| **Government** | Sovereign Cloud docs | Data sovereignty, compliance, security |

### Industry Architecture Center (Separate)

**URL**: [learn.microsoft.com/en-us/industry/architecture-center](https://learn.microsoft.com/en-us/industry/architecture-center)

Covers architectures for Microsoft Cloud for:
- Financial Services
- Healthcare
- Retail
- Manufacturing
- Sustainability

### Sources
- [Industry Solutions Overview](https://learn.microsoft.com/en-us/azure/architecture/industries/overview)
- [Microsoft Industry Docs](https://learn.microsoft.com/en-us/industry/)
- [Industry Architecture Center](https://learn.microsoft.com/en-us/industry/architecture-center)

---

## 9. Microsoft Assessments — Complete Catalog

**URL**: [learn.microsoft.com/en-us/assessments/](https://learn.microsoft.com/en-us/assessments/)
**Browse All**: [learn.microsoft.com/en-us/assessments/browse/](https://learn.microsoft.com/en-us/assessments/browse/)

### Assessment Types

| Type | Description | Cost |
|------|-------------|------|
| **Self-Directed** | Self-guided questionnaires with automated recommendations | Free |
| **Customer Success Team** | Expert-guided (requires Microsoft Unified Support) | Included in support contract |
| **Azure Expert Assessment** | Free assessments with certified Azure Experts | Free |

### How Assessments Work

1. Answer scenario-based questions about your workload/organization
2. Receive a **curated guidance report** with actionable recommendations
3. Optionally export to CSV for tracking
4. Can pull in **Azure Advisor** recommendations based on subscription
5. No account required for self-directed assessments

### Well-Architected Assessments (12+)

| Assessment | Description | URL |
|------------|-------------|-----|
| **Azure Well-Architected Review** | Core review across all 5 pillars | [Link](https://learn.microsoft.com/en-us/assessments/azure-architecture-review/) |
| **WAF Maturity Model** | Structured maturity assessment across pillars | [Link](https://learn.microsoft.com/en-us/assessments/af7d9889-8cb2-4b8b-b6bb-e5a2e2f2a59c/) |
| **AI Workload** | Well-Architected for AI workloads | [Link](https://learn.microsoft.com/en-us/assessments/ea306cce-c7fa-4a2b-89a6-bfefba6a9cf4/) |
| **SaaS Workload** | For ISVs building SaaS applications | [Browse](https://learn.microsoft.com/en-us/assessments/browse/) |
| **Data Services** | Reliability, cost, security for data workloads | [Browse](https://learn.microsoft.com/en-us/assessments/browse/) |
| **Analytics Workload** | Analytics-specific well-architected review | [Browse](https://learn.microsoft.com/en-us/assessments/browse/) |
| **Cognitive Search** | Search application assessment | [Browse](https://learn.microsoft.com/en-us/assessments/browse/) |
| **Azure Virtual Desktop** | AVD production readiness | [Link](https://learn.microsoft.com/en-us/assessments/1ef67c4e-b8d1-4193-b850-d192089ae33d/) |
| **Oracle on Azure IaaS** | Oracle workload assessment | [Browse](https://learn.microsoft.com/en-us/assessments/browse/) |
| **Machine Learning** | ML workload assessment | [Browse](https://learn.microsoft.com/en-us/assessments/browse/) |
| **Go-Live Assessment** | Pre-production readiness check | [Browse](https://learn.microsoft.com/en-us/assessments/browse/) |
| **Mission Critical** | Mission-critical workload evaluation | [Browse](https://learn.microsoft.com/en-us/assessments/browse/) |

### Cloud Adoption Assessments (5)

| Assessment | Description | URL |
|------------|-------------|-----|
| **Cloud Adoption Strategy Evaluator** | Assess strategy posture across motivations, outcomes, financials | [Link](https://learn.microsoft.com/en-us/assessments/8fefc6d5-97ac-42b3-8e97-d82701e55bab/) |
| **Cloud Journey Tracker** | Digital transformation comprehensiveness | [Browse](https://learn.microsoft.com/en-us/assessments/browse/) |
| **Governance Benchmark** | Current vs expected governance state | [Browse](https://learn.microsoft.com/en-us/assessments/browse/) |
| **Landing Zone Readiness** | Platform readiness for adoption | [Browse](https://learn.microsoft.com/en-us/assessments/browse/) |
| **SMART (Migration Readiness)** | Strategic migration assessment and readiness | [Browse](https://learn.microsoft.com/en-us/assessments/browse/) |

### Technical & Operational Assessments (8+)

| Assessment | Description |
|------------|-------------|
| **DevOps Assessment** | Evaluate capabilities across software release lifecycle |
| **Developer Velocity Index (DVI)** | Measure developer productivity and business impact |
| **AI Readiness Assessment** | AI adoption readiness across 7 pillars |
| **Analytics Journey Tracker** | Data/analytics maturity evaluation |
| **Application Modernization** | Gaps and guidance for app modernization |
| **Azure Stack HCI** | Hybrid cloud infrastructure assessment |
| **Sustainability Manager** | Environmental sustainability implementation |
| **Power Platform WAR** | Power Platform well-architected review |

### Industry-Specific Assessments

| Assessment | Industry |
|------------|----------|
| **Cloud for Financial Services WAR** | Financial Services |
| **Cloud for Healthcare Learner** | Healthcare |
| **Cloud for Retail Partner** | Retail |
| **Cloud for Sustainability Partner** | Sustainability |

### Sources
- [Microsoft Assessments Portal](https://learn.microsoft.com/en-us/assessments/)
- [Browse All Assessments](https://learn.microsoft.com/en-us/assessments/browse/)
- [Assessments FAQ](https://learn.microsoft.com/en-us/assessments/support/)
- [Azure Assessment Tools Blog](https://azure.microsoft.com/en-us/blog/navigate-a-seamless-cloud-modernization-with-microsoft-assessment-tools/)

---

## 10. Self-Hosted Applicability Matrix

### Which Azure frameworks apply to the IPAI self-hosted stack?

| Framework / Pattern | Azure-Specific? | Self-Hosted Applicable? | How to Apply |
|---------------------|----------------|------------------------|-------------|
| **Well-Architected 5 Pillars** | Principles are universal | **Yes — highly applicable** | Apply pillars to DO/Docker/PostgreSQL stack |
| **Cloud Design Patterns (40+)** | Platform-agnostic | **Yes — directly applicable** | Implement with PostgreSQL, Docker, n8n, Redis |
| **Architecture Styles** | Platform-agnostic | **Yes — directly applicable** | Already using Web-Queue-Worker + Event-Driven |
| **Cloud Adoption Framework** | Methodology is universal | **Yes — phases applicable** | Strategy/Plan/Ready/Adopt/Govern/Manage |
| **Technology Decision Trees** | Azure-specific services | **Partially** | Translate to self-hosted equivalents |
| **Reference Architectures** | Azure-specific | **Patterns applicable** | Adapt architecture patterns, not services |
| **Assessments** | Azure-focused | **Partially** | Use question frameworks, ignore Azure-specific items |
| **Industry Solutions** | Azure + M365 + Dynamics | **Low** | Domain knowledge useful, not implementations |

### IPAI Stack Self-Assessment Checklist (Inspired by WAF)

#### Reliability
- [ ] PostgreSQL automated backups (daily + WAL archiving)
- [ ] Docker restart policies (`unless-stopped` or `always`)
- [ ] Health endpoint monitoring (`/web/health` returns 200)
- [ ] Disaster recovery plan documented
- [ ] RTO/RPO targets defined

#### Security
- [ ] Keycloak SSO configured
- [ ] PostgreSQL Row-Level Security enabled
- [ ] Secrets in .env files, never in git
- [ ] Nginx WAF/rate limiting enabled
- [ ] GitLeaks + Semgrep in CI pipeline
- [ ] HTTPS/TLS everywhere

#### Cost Optimization
- [ ] DO droplet right-sized (not over-provisioned)
- [ ] Self-hosted vs SaaS decisions documented
- [ ] Monthly cost review process
- [ ] Unused resources identified and removed
- [ ] CE + OCA preferred over paid alternatives

#### Operational Excellence
- [ ] CI/CD pipeline operational (GitHub Actions)
- [ ] Monitoring dashboards (Superset)
- [ ] Alerting configured (Slack + n8n)
- [ ] Runbooks documented
- [ ] Change management process (PR reviews)

#### Performance Efficiency
- [ ] PostgreSQL query performance monitored
- [ ] Nginx caching configured
- [ ] Docker resource limits set
- [ ] Load testing performed
- [ ] Bottlenecks identified and addressed

### Sources
- [Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/)
- [Cloud Adoption Framework](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/)
- [Cloud Design Patterns](https://learn.microsoft.com/en-us/azure/architecture/patterns/)

---

## 11. Anti-Patterns Catalog

### Performance Anti-Patterns

**URL**: [learn.microsoft.com/en-us/azure/architecture/antipatterns/](https://learn.microsoft.com/en-us/azure/architecture/antipatterns/)

| Anti-Pattern | Problem | IPAI Relevance |
|--------------|---------|----------------|
| **Busy Database** | Offloading too much processing to the DB | High — PostgreSQL query optimization |
| **Busy Front End** | Resource-intensive tasks on foreground threads | High — Move heavy work to n8n/workers |
| **Chatty I/O** | Many small network requests with cumulative impact | High — Batch Odoo RPC calls |
| **Extraneous Fetching** | Retrieving more data than needed | High — Odoo ORM field selection |
| **Improper Instantiation** | Creating instances meant to be shared | Medium — Connection pooling |
| **Monolithic Persistence** | Single data store for different usage patterns | Medium — PostgreSQL + Redis + MinIO |
| **No Caching** | Repeatedly fetching same data | High — Nginx/Redis caching |
| **Noisy Neighbor** | One workload degrading others on shared resources | High — Docker resource limits |
| **Retry Storm** | Uncontrolled retry cascades | High — Exponential backoff |
| **Synchronous I/O** | Blocking threads on I/O operations | Medium — Async with n8n/Celery |

### Cloud Adoption Anti-Patterns (by Phase)

| Phase | URL | Key Anti-Patterns |
|-------|-----|-------------------|
| **Strategy** | [Link](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/antipatterns/strategy-antipatterns) | Adopting tech without clear strategy |
| **Plan** | [Link](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/antipatterns/plan-antipatterns) | Using preview services in production |
| **Ready** | [Link](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/antipatterns/ready-antipatterns) | Assuming high availability by default |
| **Migrate** | [Link](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/antipatterns/migrate-antipatterns) | Big-bang migrations without testing |
| **Govern** | [Link](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/antipatterns/govern-antipatterns) | IT becoming a gatekeeper |
| **Manage** | [Link](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/antipatterns/manage-antipatterns) | Applying on-premises management to cloud |

---

## 12. Ten Design Principles for Cloud Applications

**URL**: [learn.microsoft.com/en-us/azure/architecture/guide/design-principles/](https://learn.microsoft.com/en-us/azure/architecture/guide/design-principles/)

| # | Principle | Guidance | IPAI Application |
|---|-----------|----------|-----------------|
| 1 | **Design for self-healing** | Recover automatically from failures | Docker restart, health checks, auto-reconnect |
| 2 | **Make all things redundant** | Avoid single points of failure | PostgreSQL replicas, backup strategy |
| 3 | **Minimize coordination** | Reduce inter-service coordination | Async messaging via n8n/webhooks |
| 4 | **Design to scale out** | Scale horizontally | Docker Compose replicas |
| 5 | **Partition around limits** | Use partitioning for DB/network/compute | PostgreSQL table partitioning |
| 6 | **Design for operations** | Give ops teams the tools they need | Superset dashboards, Slack alerts |
| 7 | **Use managed services** | Prefer PaaS over IaaS | Self-hosted equivalent: Docker > bare metal |
| 8 | **Use the best data store** | Polyglot persistence | PostgreSQL + Redis + MinIO + pgvector |
| 9 | **Design for evolution** | Allow architectural changes over time | Modular ipai_* addons, MCP servers |
| 10 | **Build for business needs** | Justify every design decision | Cost-minimized philosophy |

---

## 13. AI Agent Orchestration Patterns (New 2025)

**URL**: [learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)

| Pattern | Description | IPAI Stack Mapping |
|---------|-------------|-------------------|
| **Sequential Orchestration** | Step-by-step with stage dependencies | Pulser pipeline: plan -> implement -> verify |
| **Group Chat Orchestration** | Multi-agent collaborative decision-making (limit 3 agents) | Claude + Codex agents collaborating |
| **Maker-Checker Loop** | One agent creates, another validates | implement -> verify agent workflow |

### Framework Interconnection

```
Cloud Adoption Framework (CAF)        Well-Architected Framework (WAF)
    Strategy -> Plan -> Ready              Reliability
         -> Adopt (Migrate/                Security
            Modernize/                     Cost Optimization
            Cloud-Native)                  Operational Excellence
         -> Govern/Secure/Manage           Performance Efficiency
              |                                 |
              v                                 v
         Azure Architecture Center
         +-- Architecture Styles (6)
         +-- Design Patterns (42)
         +-- Design Principles (10)
         +-- Technology Choices (decision trees)
         +-- Reference Architectures (by domain)
         +-- Anti-Patterns (10 performance + CAF phase)
         +-- Industry Solutions (5 industries)
         +-- AI Agent Patterns (3 orchestration types)
```

---

## Quick Reference: Key URLs

| Resource | URL |
|----------|-----|
| Architecture Center Home | https://learn.microsoft.com/en-us/azure/architecture/ |
| Browse All Architectures | https://learn.microsoft.com/en-us/azure/architecture/browse/ |
| Design Patterns | https://learn.microsoft.com/en-us/azure/architecture/patterns/ |
| Architecture Styles | https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/ |
| Technology Choices | https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/technology-choices-overview |
| Well-Architected Framework | https://learn.microsoft.com/en-us/azure/well-architected/ |
| WAF Pillars | https://learn.microsoft.com/en-us/azure/well-architected/pillars |
| Cloud Adoption Framework | https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ |
| Microsoft Assessments | https://learn.microsoft.com/en-us/assessments/ |
| Browse All Assessments | https://learn.microsoft.com/en-us/assessments/browse/ |
| Industry Solutions | https://learn.microsoft.com/en-us/azure/architecture/industries/overview |
| Industry Architecture Center | https://learn.microsoft.com/en-us/industry/architecture-center |
| GitHub Reference Implementations | https://github.com/mspnp |
| What's New | https://learn.microsoft.com/en-us/azure/architecture/changelog |

---

*Research compiled: 2026-03-07*
*Branch: claude/review-signavio-url-HffM8*
