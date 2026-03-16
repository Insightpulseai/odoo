# Cloud Adoption Strategy — Odoo on Azure (Future Target State)

> CAF-aligned strategy with OKR operating model.
> Repo naming: control-plane, agent-platform, data-intelligence.

---

## Mission Statement

Build and operate a secure, governed, repeatable Azure-native business platform where:
- **odoo** = ERP and transactional system of record
- **control-plane** = enterprise orchestration and registry layer
- **agent-platform** = AI and copilot execution layer
- **data-intelligence** = governed analytics and intelligence layer

All delivered through standardized Azure landing zones and a product-oriented operating model.

## What Must Be True When Migration Is Done

1. **Azure landing zones are the permanent foundation** — identity, connectivity, governance, security, observability inherited, not rebuilt per workload
2. **Odoo is the production ERP core on Azure** — not partial, not transitional
3. **Shared management operating model** — platform teams own foundation, workload teams operate within guardrails
4. **Responsibilities assigned to named owners** — governance, security, management, workload operation documented
5. **Product model, not project model** — durable ownership, not fragmented handoffs

## Target Repo Model (L2)

| Repo | Role | CAF Mapping |
|------|------|-------------|
| `.github` | Org governance, reusable CI | Shared governance |
| **`control-plane`** | Registry, orchestration, catalog, tenants | Platform services |
| **`infra`** | Landing zones, networking, identity, policy | Platform foundation |
| **`odoo`** | ERP transactional core | Application workload |
| **`agent-platform`** | Foundry agents, tools, policies, evals | Application workload |
| **`data-intelligence`** | Databricks, Lakeflow, Apps, Unity Catalog | Application workload |
| **`web`** | Product surfaces, portals, docs | Application workload |
| **`automations`** | Jobs, workflows, scheduled execution | Application workload |
| `design-system` | Design tokens, components | Support |
| `templates` | Bootstrap scaffolds | Support |

## Annual OKR

**Objective**: Build a cloud-ready organization that operates Azure safely, repeatedly, and at scale.

| KR | Measure |
|----|---------|
| KR1 | Cloud operating model selected, documented, approved |
| KR2 | Governance/security/management owners named and documented |
| KR3 | Cloud skill gaps assessed, role-based enablement in execution |
| KR4 | Quarterly reviews with visible progress, blockers, corrections |

## Quarterly Team OKRs

### Platform Team
- Shared platform operating model approved
- Governance/security/management owners named
- Landing-zone prerequisites defined
- Environment provisioning path documented

### Workload Teams
- Workload owner identified per product
- Required cloud skills mapped per team
- Team onboarding checklist completed
- Platform↔workload handoff points agreed

### Leadership
- Cloud priorities published and leadership-approved
- Success measures agreed (resilience, speed, control)
- Monthly review active for decisions and blockers
- Cross-functional steering group operating

## Operating Model: Shared Management

### Platform team owns
- Governance baseline
- Identity baseline
- Connectivity baseline
- Management and observability baseline
- Landing-zone products
- Environment provisioning path

### Workload teams own
- Workload architecture
- Deployment readiness
- Service operation inside guardrails
- Application-level reliability and business outcomes

## Success Measures

| Dimension | Measure |
|-----------|---------|
| Resilience | RTO/RPO met, backup/restore rehearsed |
| Governance | Policy compliance %, named owners, audit evidence |
| Delivery speed | Time from commit to prod, deploy frequency |
| Business value | New AI/data capabilities enabled, ERP uptime |
| Operating model | Quarterly review cadence, team OKR completion |

## Short Version

> InsightPulseAI will complete its migration by operating Odoo as the Azure-hosted ERP core on standardized Azure landing zones, with clear separation between platform and workload services, automated and governed infrastructure, and a product-oriented operating model with measurable business outcomes.
