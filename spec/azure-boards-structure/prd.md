# Azure Boards Structure — Product Requirements Document

> Complete specification for the Azure Boards 3-project structure within Azure DevOps organization `insightpulseai`.
> Governance: `spec/azure-boards-structure/constitution.md`

---

## 1. Users and Personas

| Persona | Role | Primary Project(s) |
|---------|------|-------------------|
| DevOps Engineer | Manages runtime infrastructure, CI/CD pipelines, deployment automation | `platform`, `erp-saas` |
| Finance Lead | Reviews ERP features, compliance requirements, approval workflows | `erp-saas` |
| Data Engineer | Builds data pipelines, analytics models, lakehouse infrastructure | `lakehouse` |
| Platform Operator | Manages shared services, control plane, agent orchestration | `platform` |
| Product Owner | Prioritizes backlogs, reviews delivery, manages roadmap | All |
| Engineering Manager | Sprint planning, capacity management, velocity tracking | All |

---

## 2. Project Definitions

### 2.1 `erp-saas`

**Scope**: Odoo runtime, OCA/IPAI modules, tenant/release management, ERP integrations, environment hardening, deployment/readiness.

**Area Paths**: `Runtime`, `Modules`, `Integrations`, `Security`, `Release`

**Primary GitHub Repos**: `odoo`, `odoo-modules`

#### Epic Groups and Features

**Epic: [ERP] ERP Runtime**
- [ERP] Odoo CE 19.0 base deployment and configuration
- [ERP] PostgreSQL 16 database management and optimization
- [ERP] Odoo configuration-as-code framework
- [ERP] Multi-worker process management (Gunicorn/Gevent)
- [ERP] Static asset serving and CDN integration
- [ERP] Session management and caching (Redis)
- [ERP] Logging, structured output, and log aggregation
- [ERP] Health check endpoints and readiness probes

**Epic: [ERP] Tenant & Environment Management**
- [ERP] Single-tenant deployment model (production)
- [ERP] Environment promotion pipeline (dev → staging → prod)
- [ERP] Database backup and point-in-time recovery
- [ERP] Configuration drift detection
- [ERP] Environment variable and secrets management
- [ERP] Odoo database manager lockdown (`list_db=False`)

**Epic: [ERP] Business Modules**
- [ERP] OCA module selection and compatibility matrix
- [ERP] IPAI custom module development (`ipai_*`)
- [ERP] Finance modules (AP, AR, GL, budgeting, BIR compliance)
- [ERP] HR modules (attendance, payroll, leave, expense)
- [ERP] CRM and sales pipeline modules
- [ERP] Inventory and warehouse management
- [ERP] Project and timesheet modules
- [ERP] Website and e-commerce (internal portal)
- [ERP] Enterprise parity tracking (CE + OCA + IPAI >= 80%)

**Epic: [ERP] Integration Layer**
- [ERP] Slack connector (`ipai_slack_connector`)
- [ERP] n8n webhook endpoints for Odoo events
- [ERP] Supabase bridge for external data sync
- [ERP] Mailgun SMTP integration (`mg.insightpulseai.com`)
- [ERP] Azure AD / Entra ID SSO integration
- [ERP] REST API exposure for external consumers
- [ERP] PDF generation and document management

**Epic: [ERP] Security & Compliance**
- [ERP] BIR filing compliance (Philippines tax authority)
- [ERP] Role-based access control (RBAC) hardening
- [ERP] Audit trail and change logging
- [ERP] Data encryption at rest and in transit
- [ERP] Vulnerability scanning and dependency audit
- [ERP] GDPR-aligned data handling procedures
- [ERP] IP allowlisting and network segmentation

**Epic: [ERP] Release Engineering**
- [ERP] Semantic versioning for IPAI modules
- [ERP] Module dependency resolution and install ordering
- [ERP] Pre-release validation gates (lint, test, migrate)
- [ERP] Blue-green deployment strategy
- [ERP] Rollback procedures and database migration reversal
- [ERP] Release notes generation and changelog

**Epic: [ERP] Observability & Support**
- [ERP] Application performance monitoring (APM)
- [ERP] Error tracking and alerting
- [ERP] User session analytics
- [ERP] Support ticket integration
- [ERP] SLA monitoring and uptime tracking
- [ERP] Capacity planning and resource utilization

---

### 2.2 `lakehouse`

**Scope**: Databricks lakehouse, marketing intelligence, customer 360, data pipelines, ML/AI, BI/dashboards.

**Area Paths**: `Foundation`, `Pipelines`, `Customer360`, `Marketing`, `ML-AI`, `Governance`

**Primary GitHub Repos**: `lakehouse`

#### Epic Groups and Features

**Epic: [DATA] Data Foundation**
- [DATA] Databricks workspace provisioning and configuration
- [DATA] Unity Catalog setup and namespace management
- [DATA] Delta Lake storage layer (Bronze/Silver/Gold/Platinum)
- [DATA] Medallion architecture enforcement
- [DATA] Cluster policies and compute management
- [DATA] Storage account configuration and access control
- [DATA] Network security and private endpoints

**Epic: [DATA] Ingestion & Pipelines**
- [DATA] Structured data ingestion from Odoo (PostgreSQL CDC)
- [DATA] Semi-structured data ingestion (JSON, API responses)
- [DATA] Unstructured data ingestion (documents, receipts, images)
- [DATA] Real-time streaming pipelines (Kafka/Event Hub)
- [DATA] Batch ETL scheduling and orchestration
- [DATA] Data quality checks at ingestion
- [DATA] Schema evolution and migration handling

**Epic: [DATA] Customer 360**
- [DATA] Customer identity resolution and matching
- [DATA] Customer profile unification (CRM + finance + web)
- [DATA] Customer segmentation models
- [DATA] Lifetime value (LTV) calculation
- [DATA] Churn prediction and risk scoring
- [DATA] Customer journey mapping
- [DATA] Privacy-compliant data enrichment

**Epic: [DATA] Marketing Intelligence**
- [DATA] Campaign performance analytics
- [DATA] Channel attribution modeling
- [DATA] Content performance scoring
- [DATA] Social media metrics aggregation
- [DATA] Marketing spend optimization
- [DATA] A/B test analysis framework
- [DATA] Competitive intelligence data collection

**Epic: [DATA] AI / ML / Agents**
- [DATA] ML model training infrastructure
- [DATA] Feature store for ML features
- [DATA] Model registry and versioning
- [DATA] Model serving endpoints
- [DATA] Agent-assisted data analysis
- [DATA] NLP pipelines for document processing
- [DATA] Recommendation engine

**Epic: [DATA] Serving & Activation**
- [DATA] Apache Superset BI dashboard platform
- [DATA] Embedded analytics for Odoo
- [DATA] Data API endpoints for downstream consumers
- [DATA] Reverse ETL to operational systems
- [DATA] Report scheduling and distribution
- [DATA] Self-service analytics workspace
- [DATA] Data export and sharing protocols

**Epic: [DATA] Governance & Quality**
- [DATA] Data lineage tracking
- [DATA] Data quality monitoring and SLAs
- [DATA] PII detection and masking
- [DATA] Access control and data classification
- [DATA] Retention policies and data lifecycle
- [DATA] Compliance reporting (BIR, GDPR-aligned)
- [DATA] Cost monitoring and FinOps for data platform

---

### 2.3 `platform`

**Scope**: Supabase control plane, Azure runtime services, boards automation, agents, shared auth/config/observability, ops console.

**Area Paths**: `ControlPlane`, `BoardsAutomation`, `Agents`, `AzureRuntime`, `SharedServices`, `Observability`

**Primary GitHub Repos**: `platform`, `boards-automation`, `agents`, `infra`, `web`

#### Epic Groups and Features

**Epic: [PLAT] Control Plane**
- [PLAT] Supabase project management (`spdtwktxdalcfigzeqrz`)
- [PLAT] Edge Functions deployment and management
- [PLAT] Supabase Auth configuration and user management
- [PLAT] Supabase Vault for secrets management
- [PLAT] Realtime subscriptions for event distribution
- [PLAT] pgvector for semantic search and embeddings
- [PLAT] Supabase database schema management

**Epic: [PLAT] Boards Automation**
- [PLAT] Azure Boards API integration scripts
- [PLAT] Work item creation automation from templates
- [PLAT] Sprint planning automation
- [PLAT] Board compliance checking (constitution enforcement)
- [PLAT] Work item → GitHub PR linking automation
- [PLAT] Status synchronization (PR merge → work item Done)
- [PLAT] Reporting and metrics extraction

**Epic: [PLAT] Agent Platform**
- [PLAT] Agent orchestration framework
- [PLAT] Agent → Azure Boards trigger integration
- [PLAT] Agent → GitHub PR creation pipeline
- [PLAT] Agent task queue and scheduling
- [PLAT] Agent observability and audit logging
- [PLAT] Multi-agent coordination protocols
- [PLAT] Agent capability registry and discovery

**Epic: [PLAT] Azure Runtime Platform**
- [PLAT] DigitalOcean droplet management (odoo-production)
- [PLAT] Docker container orchestration
- [PLAT] Nginx reverse proxy and TLS termination
- [PLAT] Cloudflare DNS management
- [PLAT] SSL certificate automation (Let's Encrypt)
- [PLAT] Azure resource provisioning (Databricks, storage)
- [PLAT] Infrastructure-as-code (Terraform/Pulumi)

**Epic: [PLAT] Shared Services**
- [PLAT] Centralized authentication (Azure AD / Entra ID)
- [PLAT] Single sign-on across all platform surfaces
- [PLAT] Shared configuration management
- [PLAT] Secret rotation and lifecycle management
- [PLAT] API gateway and rate limiting
- [PLAT] Notification service (Slack, email)
- [PLAT] Audit logging and compliance trail

**Epic: [PLAT] Developer Experience**
- [PLAT] Local development environment setup automation
- [PLAT] Dev container and Codespace configurations
- [PLAT] CLI tooling for platform operations
- [PLAT] Documentation site and knowledge base
- [PLAT] Onboarding automation for new team members
- [PLAT] Template repositories and scaffolding
- [PLAT] Code quality gates and pre-commit hooks

**Epic: [PLAT] Observability & FinOps**
- [PLAT] Centralized logging aggregation
- [PLAT] Distributed tracing across services
- [PLAT] Uptime monitoring and alerting
- [PLAT] Cost tracking across DigitalOcean, Azure, Supabase
- [PLAT] Resource rightsizing recommendations
- [PLAT] Budget alerts and spend forecasting
- [PLAT] SLA dashboard and incident management

---

## 3. Board Configuration

### 3.1 Story Board Columns

| Column | Purpose | WIP Limit |
|--------|---------|-----------|
| New | Newly created, not yet triaged | None |
| Ready | Refined, estimated, ready for sprint | None |
| In Progress | Actively being worked on | 5 per team |
| Blocked | Cannot proceed due to dependency or issue | None |
| In Review | Code review, QA, or stakeholder review | 3 per team |
| Done | Accepted and deployed | None |

### 3.2 Task Board Columns

| Column | Purpose |
|--------|---------|
| To Do | Assigned but not started |
| Doing | Actively in progress |
| Review | Code review or verification |
| Done | Completed |

### 3.3 Swimlanes

| Swimlane | Purpose |
|----------|---------|
| Expedite | Critical/urgent items requiring immediate attention |
| Standard | Normal priority work |
| Debt / Hardening | Technical debt, refactoring, security hardening |

### 3.4 Tags

Canonical tag set (14 tags, max 15):

`odoo`, `oca`, `ipai`, `azure`, `databricks`, `supabase`, `agent`, `security`, `finops`, `marketing`, `customer360`, `runtime`, `deploy`, `observability`

---

## 4. Naming Conventions

| Work Item Type | Format | Example |
|----------------|--------|---------|
| Epic | `[DOMAIN] <Outcome>` | `[ERP] ERP Runtime` |
| Feature | `[DOMAIN] <Capability>` | `[ERP] Odoo CE 19.0 base deployment and configuration` |
| User Story | `As a <role>, I need <capability>, so that <outcome>` | `As a DevOps Engineer, I need health check endpoints, so that I can monitor Odoo readiness` |
| Task | `<Verb> <specific deliverable>` | `Configure Gunicorn worker count for production load` |

---

## 5. Custom Fields

| Field | Type | Values | Required On |
|-------|------|--------|-------------|
| Primary Repo | Single select | `odoo`, `lakehouse`, `platform`, `boards-automation`, `agents`, `infra`, `web` | Feature, Story |
| Deployment Surface | Single select | `none`, `azure-runtime`, `databricks`, `odoo-runtime`, `web`, `shared-platform` | Feature, Story |
| Risk Level | Single select | `low`, `medium`, `high` | Feature, Story |
| Verification Required | Single select | `unit`, `integration`, `deploy`, `manual-business-check` | Story, Task |

---

## 6. Dashboard Views

### 6.1 `erp-saas` Views

- **ERP Sprint Board**: Current sprint stories and tasks by column
- **ERP Module Status**: Features grouped by business module area
- **ERP Release Pipeline**: Stories in In Review or Done with deployment status
- **ERP Compliance**: Items tagged `security` or with BIR-related area paths
- **ERP Velocity**: Sprint burndown and velocity trend

### 6.2 `lakehouse` Views

- **Data Sprint Board**: Current sprint stories and tasks
- **Pipeline Status**: Features grouped by pipeline stage (Bronze → Platinum)
- **Customer 360 Progress**: Items in Customer360 area path
- **ML Model Tracker**: Items in ML-AI area path with deployment status
- **Data Quality Dashboard**: Items tagged with governance or quality

### 6.3 `platform` Views

- **Platform Sprint Board**: Current sprint stories and tasks
- **Agent Operations**: Items in Agents area path with status
- **Infrastructure Status**: Items in AzureRuntime area path
- **Boards Automation Health**: Items in BoardsAutomation area path
- **FinOps Tracker**: Items tagged `finops` with cost impact

### 6.4 Cross-Project Views

- **Delivery Plan**: Epics across all 3 projects on a timeline
- **Blocked Items**: All items in Blocked column across projects
- **Agent Activity**: All items tagged `agent` across projects
- **Security Posture**: All items tagged `security` across projects

---

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| GitHub-linked work items | 100% of code-triggering items | Automated compliance check |
| Zero Azure repos/pipelines | 0 items in prohibited services | Weekly audit |
| Agent-assisted PR creation | Operational for >= 1 pilot repo | End-to-end test |
| Sprint velocity | Measurable across all 3 projects | Sprint retrospective data |
| Board compliance | 100% conforming to constitution | Automated weekly check |
| Work item naming | >= 95% conforming to conventions | Quarterly audit |

---

*Governed by: `spec/azure-boards-structure/constitution.md`*
*SSOT: `ssot/azure/boards-structure.yaml`*
*Last updated: 2026-03-07*
