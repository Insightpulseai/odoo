# Azure Platform Maturity Benchmark — Tasks

**Last Updated**: 2026-03-11

---

## Phase 1: Scoring Framework

- [ ] Define weighted scoring rubric in `infra/ssot/azure/platform_maturity_benchmark.yaml`
- [ ] Implement `scripts/infra/azure_maturity_score.py` scoring engine
  - [ ] Parse rubric YAML and evidence YAML
  - [ ] Compute per-criterion, per-domain, and aggregate scores
  - [ ] Enforce pass/cutover thresholds from constitution
  - [ ] Output scored result as JSON
- [ ] Implement `scripts/infra/collect_azure_evidence.sh` wrapper
  - [ ] Discover available CLI tools (az, gh, terraform, curl)
  - [ ] Dispatch per-domain probe scripts
  - [ ] Aggregate evidence fragments into single YAML

## Phase 2: Domain Probes

### Identity & Governance
- [ ] Probe: Entra ID tenant configuration (MFA, conditional access)
- [ ] Probe: Managed identity assignments on ACA/App Service
- [ ] Probe: RBAC role assignments and custom role definitions
- [ ] Probe: Resource tagging policy compliance
- [ ] Probe: Azure Policy assignment and compliance state

### Networking
- [ ] Probe: VNet topology and NSG rules
- [ ] Probe: Cloudflare DNS/proxy/WAF configuration
- [ ] Probe: TLS termination mode (edge + origin)
- [ ] Probe: DNS record management (YAML-first validation)

### Compute & Runtime
- [ ] Probe: ACA revision management and scaling rules
- [ ] Probe: ACR image lifecycle (signing, scanning, pruning)
- [ ] Probe: Container resource limits and autoscale config
- [ ] Probe: Health probe configuration (liveness, readiness, startup)

### Monitoring & Observability
- [ ] Probe: Log Analytics workspace and retention config
- [ ] Probe: Application Insights instrumentation
- [ ] Probe: Distributed tracing configuration
- [ ] Probe: Alert rules and action group routing

### Backup & Disaster Recovery
- [ ] Probe: PostgreSQL backup schedule and retention
- [ ] Probe: Filestore backup and versioning
- [ ] Probe: DR runbook existence and test date
- [ ] Probe: RTO/RPO target definitions and measurement

### Deployment & Promotion Discipline
- [ ] Probe: GitHub Actions workflow structure and gates
- [ ] Probe: Environment promotion path (dev → staging → prod)
- [ ] Probe: IaC coverage (Terraform/Bicep state analysis)
- [ ] Probe: Rollback mechanism verification

## Phase 3: CI Gate

- [ ] Create `.github/workflows/azure-maturity-gate.yml`
  - [ ] Wire evidence collection to GitHub Actions secrets
  - [ ] Run scoring engine and assert thresholds
  - [ ] Upload scorecard as workflow artifact
- [ ] Add gate to production promotion workflow as required check

## Phase 4: Reporting

- [ ] Implement `scripts/infra/azure_maturity_report.py` markdown generator
- [ ] Generate domain gap report with remediation priorities
- [ ] Add historical score append to `infra/ssot/azure/maturity_history.json`
- [ ] Verify end-to-end: evidence → score → gate → report
