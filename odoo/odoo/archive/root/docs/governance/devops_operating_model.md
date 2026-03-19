# DevOps Operating Model — Five Pillars

> Maps the five Microsoft DevOps pillars to the InsightPulse AI platform model.
> **SSOT**: `ssot/governance/operating-model.yaml`
> **Ref**: [What is DevOps?](https://learn.microsoft.com/en-us/devops/what-is-devops)

---

## Authority Split (Unchanged)

| Surface | Authority |
|---------|-----------|
| Azure Boards | Execution coordination, work-item traceability |
| GitHub | Code, PRs, CI gates, issue triage |
| Repo docs | Specs, architecture doctrine, SSOT files |
| Runtime state | Live evidence (health checks, metrics, logs) |

Hierarchy: **Epic → Issue → Task** (Basic process). No changes.

---

## Pillar 1: Plan Efficient Workloads

**Status**: Addressed, partially explicit.

| Aspect | Where |
|--------|-------|
| Portfolio planning | Azure Boards (7 Epics, 25 Issues, Delivery Plans) |
| Sprint cadence | 14-day sprints, shared across area paths |
| Dependency management | Predecessor/Successor links in Boards |
| Capacity model | Solo-operator model (scales via vertical teams) |

**Gaps to close**:
- Explicit workload priority rules (must-have vs. nice-to-have per sprint)
- FinOps guardrails (Azure cost thresholds per workload)
- Capacity planning guidance for scaling beyond solo-operator

**Canonical doc**: `ssot/governance/azdo-execution-hierarchy.yaml`

---

## Pillar 2: Develop Modern Software

**Status**: Well-covered.

| Aspect | Where |
|--------|-------|
| Spec → Code → PR → Merge → Deploy | Spec bundles → GitHub PR (AB#ID) → CI gates → AzDo CD |
| Dev environment | `.devcontainer/`, `docker-compose.yml`, `Makefile` |
| Inner/outer loop parity | Same scripts local and CI (`make lint`, `make test`) |
| MCP/agent-assisted development | AzDo MCP tool layer (FEAT-003-04) |

**Canonical doc**: [AZURE_DEVOPS_OPERATING_MODEL.md](../architecture/AZURE_DEVOPS_OPERATING_MODEL.md)

---

## Pillar 3: Deliver Quality Services

**Status**: Operational — test taxonomy, shift-left doctrine, quality gates, and release readiness documented.

| Aspect | Where |
|--------|-------|
| Testing doctrine (L0–L4 taxonomy) | `quality_engineering_model.md` § 0 |
| Shift-left rule | Most testing before merge; PRs fail on required levels |
| Pipeline gate mapping | `infra/ssot/ci_cd_policy_matrix.yaml` § `testing_policy` |
| Definition of Done | `azdo-execution-hierarchy.yaml` § `definition_of_done` |
| PR quality gates | GitHub required status checks (CI green, review approved) |
| Release readiness | `quality_engineering_model.md` § 4 |
| Rollback criteria | `quality_engineering_model.md` § 5 (threshold-based) |
| Evidence capture | `docs/evidence/<stamp>/` per deployment |

**Quality is not only release testing** — it is produced by fast, reliable, early tests. Test health and engineering velocity are tracked together: flaky tests are engineering debt with a 1-sprint triage SLA.

**Remaining gaps**:

- L3 integration test automation (navigation smoke defined, not all implemented)
- Flakiness dashboard (tracking defined, tooling not yet built)

**Canonical doc**: [quality_engineering_model.md](../architecture/quality_engineering_model.md)

---

## Pillar 4: Operate Reliable Systems

**Status**: Operational — SLI/SLO, incident response, monitoring goals, and observability model documented.

| Aspect | Where |
|--------|-------|
| Monitoring goals (TTD/TTM/TTR) | `reliability_operating_model.md` § 1 |
| SLI / SLO per service | `reliability_operating_model.md` § 2-3 |
| Incident response flow | `reliability_operating_model.md` § 5 |
| Backup / DR | `reliability_operating_model.md` § 6 |
| Telemetry, synthetic, RUM | `observability_model.md` |
| Health checks | Required per ACA workload |
| Runtime evidence | `docs/evidence/` bundles |

**Monitoring is mandatory for production**: Deployment is not complete without monitoring confirmed active. Production monitoring data feeds backlog prioritization and validated learning.

**Remaining gaps**:

- RUM instrumentation (Application Insights JS SDK not yet deployed to Odoo web client)
- Synthetic monitoring automation (availability tests defined but not all implemented)
- Formal multi-region DR plan

**Canonical docs**:

- [reliability_operating_model.md](../architecture/reliability_operating_model.md)
- [observability_model.md](../architecture/observability_model.md)

---

## Pillar 5: DevSecOps

**Status**: Addressed — identity, secrets, pipeline security, container controls documented.

| Aspect | Where |
|--------|-------|
| Shift-left security | GHAS (secret scanning, code scanning, dependency review) |
| Pipeline security | Azure Pipelines + GitHub Actions required gates |
| Identity / access | Entra ID + Azure RBAC + managed identities |
| Secrets authority | Azure Key Vault (`kv-ipai-dev`) |
| Runtime security | Defender for Containers + Azure Policy |
| Observability | Azure Monitor + Application Insights |
| Findings → work items | Security findings triage back to Azure Boards |

**Canonical doc**: [devsecops_operating_model.md](../architecture/devsecops_operating_model.md)

---

## Pillar Maturity Summary

| Pillar | Maturity | Primary Gap |
|--------|----------|-------------|
| Plan efficient workloads | Directional | FinOps guardrails, priority rules |
| Develop modern software | Operational | Lifecycle doc consolidation |
| Deliver quality services | Operational | Synthetic test automation |
| Operate reliable systems | Operational | RUM instrumentation, multi-region DR |
| DevSecOps | Operational | Findings-to-work-item automation |

---

## Cross-References

- [operating-model.yaml](../../ssot/governance/operating-model.yaml) — tool authority
- [azdo-execution-hierarchy.yaml](../../ssot/governance/azdo-execution-hierarchy.yaml) — work items
- [devsecops_operating_model.md](../architecture/devsecops_operating_model.md) — Pillar 5 detail
- [quality_engineering_model.md](../architecture/quality_engineering_model.md) — Pillar 3 detail
- [reliability_operating_model.md](../architecture/reliability_operating_model.md) — Pillar 4 detail
- [observability_model.md](../architecture/observability_model.md) — telemetry, synthetic, RUM
- [AZURE_DEVOPS_OPERATING_MODEL.md](../architecture/AZURE_DEVOPS_OPERATING_MODEL.md) — Pillar 2 detail

---

*Last updated: 2026-03-17*
