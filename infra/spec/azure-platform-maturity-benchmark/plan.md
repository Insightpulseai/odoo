# Azure Platform Maturity Benchmark — Implementation Plan

**Version**: 1.0.0
**Status**: Draft
**Last Updated**: 2026-03-11

---

## Phased Implementation

### Phase 1: Scoring Framework (Week 1-2)

**Objective**: Establish the benchmark scoring engine and evidence collection pipeline.

**Deliverables**:
1. `scripts/infra/azure_maturity_score.py` — Scoring engine that reads evidence YAML and computes weighted scores
2. `infra/ssot/azure/platform_maturity_benchmark.yaml` — Machine-readable rubric with domain/criterion definitions
3. `scripts/infra/collect_azure_evidence.sh` — Shell wrapper that runs `az` CLI probes and writes evidence YAML

**Technical Approach**:
- Scoring engine reads `platform_maturity_benchmark.yaml` for weights and level definitions
- Evidence collector runs per-domain probe scripts and writes structured output
- Score computation is deterministic: same evidence YAML always produces same score

### Phase 2: Domain Probes (Week 3-5)

**Objective**: Implement automated evidence collection for all six domains.

**Deliverables per domain**:

| Domain | Probe Script | Evidence Key |
|--------|-------------|--------------|
| Identity & Governance | `scripts/infra/probes/identity.sh` | `az ad`, `az role`, `az policy` |
| Networking | `scripts/infra/probes/networking.sh` | `az network`, Cloudflare API |
| Compute & Runtime | `scripts/infra/probes/compute.sh` | `az containerapp`, ACR queries |
| Monitoring | `scripts/infra/probes/monitoring.sh` | `az monitor`, App Insights API |
| Backup & DR | `scripts/infra/probes/backup.sh` | `az backup`, pg_dump verification |
| Deployment | `scripts/infra/probes/deployment.sh` | `gh run list`, Terraform state |

**Technical Approach**:
- Each probe script outputs a domain evidence YAML fragment
- Probes are idempotent and read-only (no mutations)
- Missing CLI access degrades gracefully (unknown score, not failure)

### Phase 3: CI Gate Integration (Week 6-7)

**Objective**: Wire the benchmark into GitHub Actions as a pre-cutover gate.

**Deliverables**:
1. `.github/workflows/azure-maturity-gate.yml` — CI workflow that runs scoring
2. Gate logic: block production promotion if `aggregate_score < 85` or any `domain_score < 60`
3. Scorecard artifact uploaded to workflow run

**Technical Approach**:
- Workflow triggered on `workflow_dispatch` and optionally on PR to `main` (deploy paths)
- Evidence collection requires Azure credentials via GitHub Actions secrets
- Score output written to `docs/evidence/<timestamp>/azure-maturity/`

### Phase 4: Dashboard & Reporting (Week 8)

**Objective**: Human-readable reporting for stakeholders.

**Deliverables**:
1. `scripts/infra/azure_maturity_report.py` — Generates markdown report from scored evidence
2. Gap report highlighting domains below target with remediation priorities
3. Historical score tracking (append to `infra/ssot/azure/maturity_history.json`)

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Azure CLI access unavailable in CI | Probe scripts degrade gracefully; manual evidence upload supported |
| Cloudflare API rate limits | Cache probe results; run probes on schedule, not per-commit |
| Scoring rubric drift | Constitution locks rubric as append-only |
| False confidence from high scores | Require evidence attachments for any criterion scored L3+ |

---

## Integration Points

| Consumer | What It Reads | Purpose |
|----------|---------------|---------|
| `odoo/` spec bundles | Aggregate score + domain scores | Runtime cutover readiness |
| `infra/spec/odoosh-equivalent-platform/` | Compute + Deployment domain scores | Platform capability validation |
| CI pipeline | Gate result JSON | Promotion blocking |
| Project management | Gap report markdown | Sprint planning input |
