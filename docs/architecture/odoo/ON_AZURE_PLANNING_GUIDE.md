# Odoo on Azure Planning Guide

## Benchmark-aligned planning guide for InsightPulseAI

## Relationship to canonical target state

This planning guide defines **how to reach** the target state. The target state itself is defined in:

- [`INSIGHTPULSEAI_ODOO_ON_AZURE_TARGET_STATE.md`](./INSIGHTPULSEAI_ODOO_ON_AZURE_TARGET_STATE.md) — the destination
- This document — planning and execution doctrine to get there

---

## 1. Purpose

This document defines the planning doctrine for the InsightPulseAI Odoo on Azure target state.

It uses the Microsoft SAP on Azure planning guide as the benchmark for planning rigor:

- define boundary conditions first
- validate supported configuration second
- define workload topology third
- define operations, governance, and go-live gates last

This guide does **not** copy SAP workload implementation. It adapts the planning discipline to:

- Odoo 18
- Azure Container Apps
- Azure Database for PostgreSQL Flexible Server
- Microsoft Entra
- Azure landing zones
- Azure DevOps + GitHub delivery
- Foundry Agent Service
- Azure Document Intelligence

## 2. Benchmark doctrine

The benchmark pattern is:

1. Establish compliance, identity, network, and support boundaries before choosing implementation details.
2. Maintain a supported-configuration matrix for every critical workload dependency.
3. Treat environment, system, component, and landscape as separate planning concepts.
4. Treat workload topology and operational controls as first-class architecture artifacts.
5. Require a formal go-live checklist and evidence-backed acceptance gates.

## 3. Canonical definitions

### 3.1 Landscape

The complete InsightPulseAI Azure estate for Odoo, platform, data, and agent workloads.

### 3.2 Environment

A governed deployment stage such as:

- dev
- staging
- prod

### 3.3 System

A deployable runtime unit such as:

- `odoo-dev`
- `odoo-staging`
- `odoo-prod`
- `agent-platform-dev`
- `agent-platform-prod`

### 3.4 Component

A bounded functional part of a system, such as:

- Odoo web runtime
- PostgreSQL database
- Redis cache
- Foundry hosted agent runtime
- Document Intelligence extraction service
- Front Door ingress
- Key Vault secret store

## 4. Boundary conditions

Define these before implementation begins.

### 4.1 Identity and access

- Microsoft Entra is the canonical identity plane.
- Human access uses Entra identities and role-based access.
- Workload-to-workload access uses managed identities or equivalent server-side identities.
- Agent identities are governed and must not operate as anonymous mutation actors.

### 4.2 Network and ingress

- Azure landing zone network guardrails apply to all workloads.
- Odoo, Foundry, OCR, and supporting services must be deployed into workload landing zones.
- No separate AI landing zone is required.

### 4.3 Data and approval boundaries

- Odoo is the transactional system of record.
- OCR and agent outputs are proposal-first for financial and compliance-affecting actions.
- High-impact writes require approval and audit logging.

### 4.4 Secret handling

- Secrets live in Key Vault or equivalent secure store.
- No plaintext credentials live in repo-managed config.

## 5. Supported configuration matrix

Maintain and version the following matrix.

| Surface | Canonical target |
| --- | --- |
| Odoo | 19.x |
| Database | Azure Database for PostgreSQL Flexible Server |
| Runtime | Azure Container Apps |
| Identity | Microsoft Entra |
| Edge | Azure Front Door |
| Agent runtime | Foundry Agent Service |
| OCR / extraction | Azure Document Intelligence |
| Delivery spine | Azure DevOps Boards + Azure Pipelines |
| Code authority | GitHub until deliberate Azure Repos cutover |

### 5.1 Required compatibility checks

- Odoo version ↔ addon compatibility
- Odoo runtime ↔ PostgreSQL version
- Odoo runtime ↔ ACA contract
- Foundry SDK/runtime ↔ hosted agent deployment contract
- Document Intelligence API/model version ↔ extraction contract
- identity/network/security controls ↔ landing-zone policy

## 6. Landing-zone and platform topology

### 6.1 Platform landing zone responsibilities

- shared identity integration
- connectivity and network policy
- observability and management
- shared security controls
- shared delivery guardrails

### 6.2 Application landing zone responsibilities

Deploy workload systems into application landing zones, including:

- `odoo-dev`, `odoo-staging`, `odoo-prod`
- `platform-dev`, `platform-prod`
- `agent-platform-dev`, `agent-platform-prod`
- `data-intelligence-dev`, `data-intelligence-prod`

### 6.3 No separate AI landing zone

Foundry and Document Intelligence are deployed into the relevant workload landing zones as normal application components.

## 7. Workload topology

### 7.1 Odoo workload

- Odoo 18 web/runtime on Azure Container Apps
- PostgreSQL Flexible Server as the primary database
- Redis for runtime coordination/caching where required
- Front Door as ingress
- Odoo actions and automation rules as the trigger surface

### 7.2 Foundry workload

Host multiple bounded agents:

- Odoo Copilot agent
- document triage agent
- finance review agent
- compliance/workflow agent

### 7.3 Document Intelligence workload

Use Document Intelligence first for:

- OCR / Read
- layout extraction
- table extraction
- prebuilt extraction where applicable
- custom extraction for local templates/forms

### 7.4 Knowledge and tool layer

Agents use scoped tools and grounded knowledge, not unrestricted ORM/database mutation.

## 8. Odoo integration model

### 8.1 Trigger layer

Use Odoo:

- server actions
- automation rules
- cron jobs
- client actions
- contextual UI buttons

### 8.2 Odoo modules

At minimum:

- `ipai_odoo_copilot`
- `ipai_document_intelligence_bridge`
- `ipai_copilot_actions`

### 8.3 Job and audit model

Persist:

- request context
- source record / attachment
- external job ids
- status lifecycle
- output payload
- confidence
- approval state
- audit trail

## 9. Foundry agent model

### 9.1 Agent boundaries

Do not use one giant agent. Use bounded role-specific agents.

### 9.2 Tool boundaries

Allow only narrow tools, such as:

- `get_record_context`
- `submit_ocr_job`
- `write_review_result`
- `create_activity`
- `post_chatter_note`

### 9.3 Evaluation and observability

Every agent must support:

- tracing
- evaluation
- versioning
- deployment promotion
- rollback readiness

## 10. OCR and extraction model

### 10.1 Processing sequence

1. Odoo receives document/attachment.
2. Odoo action creates OCR job.
3. Document Intelligence extracts text/structure/fields.
4. Output is normalized.
5. Foundry interprets business meaning.
6. Odoo stores proposal and routes approval/review.

### 10.2 Output rules

- OCR output must be normalized before Odoo writeback.
- Financial/compliance outputs must be proposal-first.
- Low-confidence outputs must require review.

## 11. Delivery and governance

### 11.1 Authority model

- Azure = cloud/runtime/control access
- Azure DevOps = planning/governance spine
- GitHub = current engineering truth until Azure Repos cutover
- Repo SSOT files = intended-state truth
- IaC / migrations / pipelines / tests = executable truth

### 11.2 Azure DevOps shape

One project: `ipai-platform`

Target repos: `odoo`, `infra`, `platform`, `agents`, `automations`, `web`, `design`, `data-intelligence`, `agent-platform`, `docs`, `templates`

## 12. Go-live gates

A workload is not ready until all of these are true:

- supported configuration matrix is complete
- identity/network/secret model is approved
- Odoo health checks pass
- agent deployments are reachable and versioned
- OCR extraction paths are validated
- proposal/approval gates are in place
- observability and audit logs exist
- rollback path is documented and tested

## 13. Repo ownership mapping

| Repo | Responsibility |
| --- | --- |
| `odoo` | ERP runtime, addons, actions, UI, audit/job models |
| `infra` | landing-zone implementation, network, edge, runtime infra |
| `platform` | control-plane services and normalized AI/OCR contracts |
| `agent-platform` | Foundry hosted agents, tools, evals |
| `data-intelligence` | Databricks/lakehouse/semantic outputs |
| `docs` | cross-platform architecture and governance |
| `templates` | starter/scaffold assets only |

## 14. Planning checklist

- [ ] boundary conditions defined
- [ ] naming and authority model frozen
- [ ] landing-zone placement decided
- [ ] supported configuration matrix approved
- [ ] runtime topology documented
- [ ] module and agent ownership assigned
- [ ] OCR and approval model defined
- [ ] release and rollback lanes defined
- [ ] go-live gates agreed
