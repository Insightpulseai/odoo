# Cloud Adoption Framework — Strategy (Complete)

> Tailored rewrite of Microsoft CAF Strategy methodology for the InsightPulse AI platform.
> Cross-references: `CAF_TEAM_MODEL.md`, `MIGRATION_OUTCOME_GATE.md`, `unified_strategy.yaml`

---

## Mission

Build a self-hosted, governed, repo-first enterprise platform where Odoo is the ERP system of record, Azure AI Foundry is the agent control plane, Azure Databricks is the intelligence backbone, and all execution is validated through machine-readable SSOT, CI gates, and evidence-backed operations.

---

## Step 1: Assess Current Cloud Adoption Strategy

### Assessment dimensions

| Dimension | Question |
|---|---|
| Identity baseline | Is Entra ID verified, MFA enforced, named accounts in use? |
| Delivery baseline | Are all Azure deploys through YAML pipelines with WIF? |
| Foundry baseline | Is the agent runtime production-hardened with telemetry? |
| Odoo baseline | Is Odoo CE 18 running on Azure ACA with managed PG? |
| Data baseline | Is OLTP/OLAP separation contracted with CDC? |
| Edge baseline | Does Front Door route to healthy origins with TLS? |
| Observability baseline | Are App Insights, Log Analytics, Monitor alerts active? |
| Operating-model baseline | Is the product-plane ownership model documented and enforced? |

### Assessment outputs

- Current-state maturity summary
- Gap register (what is documented but not implemented)
- Risk register (what is live but not governed)
- Prioritized remediation actions
- Reassessment cadence: monthly

### Assessment reference

See `docs/architecture/LIVE_STATE_DEFINITION.md` for the four live-state gates.

---

## Step 2: Define Motivations, Mission, and Objectives

### 2.1 Motivations

#### Reduce business risk

- Security and identity baseline across all platform planes
- Data governance through SSOT and medallion architecture
- Compliance management (BIR, financial close, audit trail)
- Financial transparency through governed cost tagging

#### Accelerate innovation

- AI adoption via Foundry agents with governed tool boundaries
- Cloud-native capabilities via Azure Container Apps
- Faster delivery via spec-driven agentic SDLC
- Democratized data access via governed Databricks products

#### Enhance agility and efficiency

- Simplified operations via automation consolidation
- Scalable services via Azure-native infrastructure
- Software-defined compliance via CI gates and SSOT validators

### 2.2 Motivation classification

| Motivation | Priority | Urgency |
|---|---|---|
| Security / identity baseline | High | High |
| Delivery control plane (AzDO/GitHub/CI) | High | High |
| Foundry/agent runtime hardening | High | High |
| Odoo SoR stabilization | High | High |
| OLTP/OLAP separation | High | Medium |
| Automation consolidation | High | Medium |
| Public advisory assistant | High | Medium |
| Observability/security baseline | High | High |
| Sustainability | Medium | Low |

### 2.3 Strategic objectives

| # | Objective | Target date | Success measure |
|---|---|---|---|
| OBJ-001 | Identity baseline | Apr 14 | MFA 100%, named accounts, emergency access |
| OBJ-002 | Azure DevOps operationalization | Apr 21 | 100% deploys through YAML, 3 pools, 3 WIF |
| OBJ-003 | Foundry runtime hardening | Apr 28 | Production-readiness checklist 100% |
| OBJ-004 | Public advisory assistant | May 5 | Live, zero browser-side secrets |
| OBJ-005 | Automation consolidation | May 19 | 100% inventoried, 70% dedup |
| OBJ-006 | OLTP/OLAP separation | May 19 | CDC approved, medallion contract defined |
| OBJ-007 | Observability + security baseline | Apr 21 | App Insights + Monitor + Defender active |

### 2.4 Success measures

- MFA coverage = 100%
- All Azure deploys through YAML pipelines = true
- Zero browser-side secrets for public AI surfaces = true
- 100% automation inventory coverage = true
- CDC contract approved and implemented = true
- Observability active across all production-critical services = true
- Successful end-to-end business workflow through public ingress = true

---

## Step 3: Define the Strategy Team

### Solo-founder + agent model

One human holds all CAF strategy-team functions. Agents are execution and review functions, not separate humans.

| CAF function | Mapping |
|---|---|
| Executive sponsor | Jake |
| Business decision maker | Jake |
| IT decision maker | Jake |
| Lead architect | Jake + chief-architect agent |
| Central IT / platform | Jake + azure-platform agent |
| Security | Jake + security-judge agent |
| Compliance | Jake + governance-judge agent |
| Finance / FinOps | Jake + finops-judge agent |
| Workload execution | odoo-runtime, foundry-agent, data-intelligence agents |
| Release / delivery | release-ops agent |

**Rule**: The human stays accountable. Agents are execution and review functions.

See `docs/operating-model/CAF_TEAM_MODEL.md` for the full team model.

---

## Step 4: Prepare the Organization

### 4.1 Leadership buy-in

As sole executive:
- Explicitly accept or reject strategic priorities
- Explicitly accept or reject risk
- Explicitly approve resource allocation
- Explicitly define what needs protected deployment gates

### 4.2 Align organizational strategies

| Strategy layer | Alignment |
|---|---|
| Business | Packaged SaaS ERP / AI / data offerings |
| Digital | Self-hosted, agent-assisted platform experiences |
| IT | Azure landing zones, secure runtime, CI/CD, control plane |
| Cloud adoption | Migration and modernization sequence across all layers |

### 4.3 Operating-model readiness

| Bucket | Assessment |
|---|---|
| People | One human authority + maker/judge agents |
| Processes | Spec-driven, PR-driven, evidence-driven delivery |
| Technology | Azure / Odoo / Foundry / Databricks / Cloudflare / GitHub |
| Partners | Microsoft, Databricks, OCA/Odoo, Cloudflare, TBWA/SMP |

### 4.4 Project → Product shift

Persistent product-plane ownership replaces temporary project delivery.

**Platform products**: infra, platform

**Workload products**: odoo, agent-platform, data-intelligence, web, automations

**Enablement products**: .github, agents, design, templates, docs

### 4.5 Partner relationships

| Partner | Role |
|---|---|
| Microsoft Azure | Primary cloud platform, AI Foundry, DevOps |
| Databricks | Intelligence/data backbone, Unity Catalog |
| OCA / Odoo | ERP community ecosystem, module parity |
| Cloudflare | Edge DNS, CDN (DNS-only mode for Front Door) |
| GitHub | Source control, CI/CD, org governance |
| TBWA/SMP | Client context, packaging requirements |

---

## Step 5: Inform the Strategy

### 5.1 Cost efficiency

- Default to managed services where differentiation is low
- Self-host only where it creates control/cost/feature advantage
- Treat idle infrastructure as a defect
- Require environment-level cost visibility by workload and product
- Tie cost to service catalog, tags, and ownership

### 5.2 AI strategy

- AI use cases must map to measurable business friction
- Azure AI Foundry is the primary agent platform
- MCP is the preferred interoperability/tool boundary
- AI data must be governed and lineage-aware via Databricks
- Public copilots must be advisory-only unless an operator boundary is deliberately introduced
- Azure DevOps MCP is the canonical agent-access layer for Boards/PRs/builds

### 5.3 Security

- Identity-first rollout (Entra ID before any runtime)
- Secret boundaries by environment (Key Vault, never in git)
- Secure-by-default public surfaces (zero browser-side secrets)
- Least-privilege RBAC
- Security as a judge function (security-judge agent), not just a final gate

### 5.4 Resiliency

- Classify systems by business criticality
- Define RTO/RPO per product plane (Odoo SoR and public ingress first)
- Ensure rollback exists before calling anything "live"
- Treat business continuity as a strategy outcome, not just an infra feature

### 5.5 Sustainability

- Right-sizing and idle resource cleanup
- Efficient architecture choices (managed services where appropriate)
- Reporting and brand narrative readiness
- Not the first gate for current migration, but shapes ongoing decisions

---

## Strategy outputs

| Output | Location |
|---|---|
| Mission statement | This document |
| Objective catalog | `ssot/governance/unified_strategy.yaml` |
| KPI/KR map | `ssot/governance/enterprise_okrs.yaml` |
| Operating-model readiness | `docs/operating-model/CAF_TEAM_MODEL.md` |
| Product-plane ownership | `ssot/repo/org_topology.yaml` |
| Migration outcome gates | `docs/operating-model/MIGRATION_OUTCOME_GATE.md` |
| Live-state definition | `docs/architecture/LIVE_STATE_DEFINITION.md` |
| AI-led SDLC lifecycle | `ssot/governance/ai_led_sdlc.yaml` |
| Risk register | `ssot/governance/platform-strategy-2026.yaml` (risks section) |
| Reassessment cadence | Monthly |

---

## Strategy → Plan linkage

Strategy defines motivations and objectives. The Plan stage converts them into an actionable operating model with documented ownership. See `docs/operating-model/CAF_PREPARE_ORGANIZATION_COMPLETE.md` for:

- Cloud journey classification per product plane
- Operating model decision (shared management + centralized human accountability)
- Governance / security / management / AI responsibility maps
- Partner roles and review cadence

## Review cadence

- Monthly: reassess maturity against live-state gates
- Quarterly: reassess strategic objectives and program alignment
- Per-objective: reassess on completion or target-date miss
