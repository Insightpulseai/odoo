# Documentation Program — Azure Boards Scaling Model

> Multi-team portfolio model for the Odoo-on-Azure documentation program.
> Process model: Agile | Hierarchy: Epic → Feature → User Story → Task

---

## Team Hierarchy

One program root plus repo-aligned delivery teams.

| Team | Purpose | Primary Repo Alignment |
|---|---|---|
| `ipai-platform` | Portfolio/program rollup | Cross-repo |
| `ipai-docs` | Overview, planning, reference, publishing | `docs` |
| `ipai-platform-control` | Workload center, monitoring, AI platform control plane | `platform` |
| `ipai-infra` | Deployment automation, networking, runtime infra patterns | `infra` |
| `ipai-odoo-runtime` | Odoo runtime, how-to, connector-surface docs | `odoo` |
| `ipai-agents` | AI platform runtime boundaries, AI-led SDLC, agent docs | `agents` |
| `ipai-data-intelligence` | Lakehouse, BI, data-platform docs | `data-intelligence` |

---

## Area Paths

```
ipai-platform
ipai-platform\docs
ipai-platform\platform
ipai-platform\infra
ipai-platform\odoo
ipai-platform\agents
ipai-platform\data-intelligence
```

### Mapping Rule

| Work owned by... | Area Path |
|---|---|
| `docs` repo | `ipai-platform\docs` |
| `platform` directory | `ipai-platform\platform` |
| `infra` directory | `ipai-platform\infra` |
| `odoo` (repo root) | `ipai-platform\odoo` |
| `agents` directory | `ipai-platform\agents` |
| `data-intelligence` directory | `ipai-platform\data-intelligence` |

---

## Iteration Paths

```
ipai-platform
ipai-platform\Docs
ipai-platform\Docs\Foundation
ipai-platform\Docs\Wave-1
ipai-platform\Docs\Wave-2
ipai-platform\Docs\Hardening
```

### Iteration Scope

| Iteration | Scope |
|---|---|
| `Foundation` | Taxonomy, overview, workload-center, benchmark map, doc authority model |
| `Wave-1` | Monitoring, deployment automation, runtime, integrations |
| `Wave-2` | AI platform, engineering, data-intelligence |
| `Hardening` | Evidence closure, drift reconciliation, cross-link cleanup |

---

## Portfolio Hierarchy

### Epic Level

| Epic | Business Value | Time Criticality |
|---|---|---|
| Odoo on Azure Workload Documentation | 100 | 95 |
| AI Platform Documentation | 95 | 90 |
| Engineering Documentation | 90 | 85 |
| Data Intelligence Documentation | 90 | 80 |
| Governance and Drift Remediation Documentation | 100 | 100 |

### Feature Level

Features represent document families or major bundles:

- Overview Family
- Workload Center Family
- Monitoring Family
- Deployment Automation Family
- Runtime Family
- Planning and Reference Family
- Integrations Family
- AI Platform Index / Foundry Control Plane / Retrieval / Agent Boundaries
- Engineering Index / Spec-Driven Dev / Agent Delivery / CI/CD / SRE Loop
- Data Intelligence Index / Lakehouse / Ingestion / Consumption
- Drift Model / Rebuildability

---

## Delivery Plans

Use Azure Boards Delivery Plans for cross-team doc coordination.

### Swimlanes

| Swimlane | Team |
|---|---|
| Cross-repo narrative | `ipai-docs` |
| Control-plane docs | `ipai-platform-control` |
| IaC / deployment docs | `ipai-infra` |
| Odoo runtime docs | `ipai-odoo-runtime` |
| Agent / engineering docs | `ipai-agents` |
| Data-platform docs | `ipai-data-intelligence` |

### Timeline Items

Show **Features only** (not individual page tasks):

- Overview Family
- Workload Center Family
- Monitoring Family
- Deployment Automation Family
- AI Platform Index + Foundry Control Plane
- Engineering Index + Spec-Driven Development
- Data Intelligence Index + Lakehouse and Governance

### Dependency Tags

| Tag | Meaning |
|---|---|
| `depends-platform` | Requires platform control-plane work |
| `depends-infra` | Requires IaC / deployment work |
| `depends-odoo` | Requires Odoo runtime work |
| `depends-agents` | Requires agent / engineering work |
| `depends-data` | Requires data-intelligence work |

---

## Dashboard Model

### Dashboard 1 — Program

Target audience: Program lead

- Epic progress
- Feature completion by Area Path
- Blocked Features
- Evidence closure count
- Drift-remediation status

### Dashboard 2 — Team Execution

One per team. Target audience: Team contributors

- Active User Stories
- Overdue `EVIDENCE:` items
- Doc pages missing review
- Current iteration throughput

### Dashboard 3 — Leadership

Target audience: Leadership / stakeholders

- Progress by Epic
- Top blockers
- Readiness status by documentation family
- Governance-drift remediation trend

---

## Refinement Inputs Needed

The following values should be confirmed before final Azure DevOps import:

- [ ] Azure DevOps project name
- [ ] Area Path tree (confirmed above, needs Azure DevOps setup)
- [ ] Iteration names and date ranges
- [ ] Team names (confirmed above, needs Azure DevOps setup)
- [ ] Process template (assumed: Agile)

---

## Related Documents

- `docs/planning/DOC_PROGRAM_BACKLOG.md` — full backlog hierarchy
- `docs/planning/DOC_PROGRAM_IMPORT.csv` — Azure Boards CSV import file
- `docs/planning/IPAI_AZURE_BOARDS_BACKLOG.md` — platform-wide backlog (risks, readiness, security)
- `docs/odoo-on-azure/reference/doc-authority.md` — documentation ownership model

---

*Created: 2026-04-05 | Version: 1.0*
