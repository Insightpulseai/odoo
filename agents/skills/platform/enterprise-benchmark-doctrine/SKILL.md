# Enterprise Benchmark Doctrine

> Platform skill: Defines what "enterprise-grade" means across 5 benchmark lanes.
> Use this to evaluate maturity of `agents/`, `lakehouse/`, `ops-platform/`, `.github/`, and `automations/`.

---

## Benchmark Lanes

| Lane | Benchmark Source | Repo Scope |
|------|-----------------|------------|
| **SDLC** | Microsoft AI-led SDLC | `.github/`, `automations/`, `spec/` |
| **Agent Runtime** | Microsoft Agent Framework + M365 Agents SDK | `agents/` |
| **Data Engineering** | Azure Databricks Well-Architected Framework | `lakehouse/`, `odoo/infra/databricks/` |
| **Enterprise Data Products** | SAP Databricks / Delta Sharing | `lakehouse/` (federation + sharing) |
| **Control Plane** | Palantir Foundry API (ontology model) | `ops-platform/`, `infra/ssot/` |

---

## Lane 1: AI-Led SDLC

**Source**: [Microsoft Tech Community — AI-Led SDLC](https://techcommunity.microsoft.com/blog/appsonazureblog/an-ai-led-sdlc-building-an-end-to-end-agentic-software-development-lifecycle-wit/4491896)

### Reference Architecture

```
User Story → Spec Kit → GitHub Issue → Coding Agent → PR Review →
Code Quality Review → Deterministic CI/CD → Azure Deployment →
SRE Monitoring → GitHub Sub-Agent (Issue Creation) → [Loop Back]
```

### Agents in the Loop

| Agent | Role | IPAI Equivalent |
|-------|------|-----------------|
| **Spec Kit** | Requirements → executable specs, respects "constitution" | `spec/` bundles + `supreme` skill |
| **Coding Agent** | Scoped task → branch + commits + PR | GitHub Copilot coding agent / Claude Code |
| **Code Quality Agent** | PR review, static analysis, auto-fixes | CodeQL + PMD + custom review workflows |
| **SRE Agent** | Monitors logs/metrics/traces, proposes remediation | Azure SRE Agent + n8n alerting |

### Pass/Fail Criteria

- [ ] Spec-first: every significant change starts from a spec bundle
- [ ] Agent handoff: issues auto-created from spec, auto-assigned to coding agent
- [ ] PR validation: automated code quality review on every PR
- [ ] Deterministic CI/CD: non-agentic, reproducible deploy pipeline
- [ ] SRE feedback loop: production issues auto-create GitHub issues for remediation
- [ ] Human gates: review checkpoints between agent phases

---

## Lane 2: Agent Runtime

**Sources**:
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) — orchestration/runtime
- [Microsoft 365 Agents SDK](https://github.com/microsoft/agents) — enterprise channels
- [GitHub Copilot SDK](https://github.com/github/copilot-sdk) — embedded UX (Technical Preview only)

### Capabilities Benchmark

| Capability | Agent Framework | M365 Agents SDK | Copilot SDK |
|-----------|----------------|-----------------|-------------|
| Graph-based workflows | Yes | — | — |
| Human-in-the-loop | Yes | Yes | — |
| Checkpointing | Yes | — | — |
| OpenTelemetry | Yes | — | — |
| DevUI | Yes | — | — |
| Multi-channel (Teams, web) | — | Yes | — |
| BYOK (Azure AI Foundry) | — | — | Yes (key-based) |
| Production readiness | GA | GA | **Technical Preview** |

### Pass/Fail Criteria

- [ ] Versioned agent manifests with semantic versioning
- [ ] Tool contracts: each tool has typed input/output schema
- [ ] Eval manifests: deterministic evaluation suites per agent
- [ ] Traceability: OpenTelemetry spans from request to response
- [ ] Promotion policy: dev → staging → prod gates
- [ ] Deterministic publish gates: CI blocks broken agents
- [ ] Graph workflows: multi-agent coordination with checkpointing

### IPAI Benchmark Split

- **Orchestration/runtime** → benchmark against Agent Framework
- **Enterprise channels** → benchmark against M365 Agents SDK
- **Embedded Copilot UX** → reference only until Copilot SDK exits preview

---

## Lane 3: Data Engineering (Lakehouse)

**Source**: [Azure Databricks Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/service-guides/azure-databricks)

### Pillar Requirements

#### Reliability
- Cluster automatic-restart policies
- Job retry with exponential backoff
- Structured streaming with fault-tolerant state
- Delta Lake ACID transactions + time travel
- DLT expectations for data validation
- Multiregion deployment for DR (future)

#### Cost Optimization
- Cluster policies limiting instance types and autoscale bounds
- System tables for usage tracking (`system.billing`, `system.compute`)
- Serverless compute where it improves reliability
- Cost Management integration for budgets/alerts

#### Governance
- Unity Catalog as single governance layer
- Premium tier for advanced security features
- Approved regions and workspace policies
- Data lineage tracking through Unity Catalog
- Column-level and row-level security

#### Operational Excellence
- DAB (Databricks Asset Bundles) for IaC
- CI/CD with `databricks bundle validate` + `deploy`
- Comprehensive monitoring and alerting
- Job orchestration with dependency management

### Pass/Fail Criteria

- [ ] Unity Catalog-first: all tables governed, no hive_metastore
- [ ] Medallion architecture: Bronze → Silver → Gold with DLT
- [ ] Resilient jobs: retry policies, timeout settings, failure handling
- [ ] Cost visibility: system tables queried, budget alerts configured
- [ ] DLT expectations: data quality rules on every Silver/Gold table
- [ ] Delta Lake: ACID transactions, schema enforcement, time travel
- [ ] IaC: all pipelines/jobs defined in DAB, not created via UI
- [ ] Monitoring: job health, pipeline lag, cluster utilization tracked

---

## Lane 4: Enterprise Data Products

**Source**: [SAP Databricks / SAP BDC Delta Sharing](https://docs.databricks.com/aws/en/delta-sharing/sap-bdc/)

### Reference Pattern

```
Odoo PG → JDBC Extract → ADLS Bronze → DLT Pipeline →
Unity Catalog Gold → Delta Sharing → Consumer Catalogs
```

### Capabilities

| Capability | Description | IPAI Status |
|-----------|-------------|-------------|
| Zero-copy sharing | Delta Sharing protocol, no data duplication | Planned |
| Derived data products | Curated Gold tables with business semantics | Active (8 Gold views) |
| Governed metadata | Unity Catalog lineage + column-level security | Partial |
| Share-back | Publish derived products to consuming systems | Planned |
| Cross-engine interop | Iceberg/Delta Lake open table formats | Planned |

### Pass/Fail Criteria

- [ ] Productized Gold tables: named, documented, versioned business views
- [ ] Delta Sharing enabled: at least one share for cross-team consumption
- [ ] Metadata-rich: column descriptions, table comments, lineage tracked
- [ ] Share-back: derived data products publishable to consumers
- [ ] Open format: Delta Lake / Iceberg for cross-engine compatibility

---

## Lane 5: Control Plane / Ontology

**Source**: [Palantir Foundry API](https://www.palantir.com/docs/foundry/api/v2/general/overview/introduction/)

### Foundry API Surface (Benchmark)

| Resource | Description | IPAI Equivalent |
|----------|-------------|-----------------|
| Ontologies | Business object type registry | `agents/registry/skills-index.json` |
| Object Types | Typed entities with properties | Agent manifests, tool contracts |
| Actions | Executable operations on objects | Skills, n8n workflows |
| Queries | Structured data retrieval | Databricks SQL, Superset queries |
| Object Sets | Collections with filters | Unity Catalog schemas/views |
| Datasets | Backing data stores | ADLS + Delta Lake tables |
| Attachments/Views | Evidence, artifacts | `docs/evidence/` bundles |

### Pass/Fail Criteria

- [ ] Model registry: agents, tools, skills have versioned manifests
- [ ] Promotion state: each resource has dev/staging/prod lifecycle
- [ ] Evidence registry: audit trail for deployments, changes, incidents
- [ ] Action metadata: every skill/action has typed input/output/side-effects
- [ ] Data product registry: Gold tables cataloged with ownership + SLA
- [ ] Environment ownership: every resource has an owning team/principal
- [ ] Policy metadata: compliance constraints documented per resource

---

## Scorecard Template

| Lane | Benchmark | Current | Target | Gap |
|------|-----------|---------|--------|-----|
| SDLC | AI-led SDLC loop | Spec bundles + CI exist, no SRE agent | Full loop with SRE feedback | SRE agent, auto-issue creation |
| Agent Runtime | Agent Framework | Skills registry, no graph workflows | Observable, governed, checkpointed | OpenTelemetry, eval manifests, promotion |
| Data Engineering | Databricks WAF | DLT pipeline built, untested | Resilient, cost-visible, governed | Deploy + test, system tables, DLT expectations |
| Data Products | SAP Databricks | 8 Gold views, no Delta Sharing | Productized, shareable, metadata-rich | Delta Sharing, column descriptions |
| Control Plane | Palantir Foundry | Skills-index.json, SSOT map | Ontology-grade metadata model | Action types, promotion state, evidence registry |

---

## Doctrine Rules

1. **Benchmark against the lane, not the vendor.** Use Microsoft/Databricks/Palantir patterns as structural references, not as stack adoption targets.
2. **GitHub Copilot SDK is reference-only.** Do not treat Technical Preview as a production baseline.
3. **Unity Catalog is non-negotiable.** Every table, view, and function must be governed through UC.
4. **Spec-first is the SDLC primitive.** No implementation without a spec bundle.
5. **Observable by default.** Every agent, pipeline, and service must emit structured telemetry.
6. **Data products, not data dumps.** Gold tables are products with owners, SLAs, and metadata.
7. **Control plane earns trust incrementally.** Start with registry → add promotion → add evidence → add ontology.
