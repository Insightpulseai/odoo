# Tasks — InsightPulseAI Workload Center

## Phase 1 — Workload Registry and Topology

- [ ] Define canonical workload schema (name, owner, environments, components, endpoints, image, config)
- [ ] Define environment/component topology schema
- [ ] Create `ssot/workload-center/registry.yaml` — canonical workload registry
- [ ] Create `ssot/workload-center/topology-schema.yaml` — environment/component schema
- [ ] Implement register-existing-workload flow (`scripts/workload/register.sh`)
- [ ] Register Odoo ERP workload (web + worker + cron + PG)
- [ ] Implement workload metadata view (`scripts/workload/inspect_topology.sh`)
- [ ] Implement release/history model (timestamped deploy records with evidence links)

## Phase 2 — Lifecycle Operations Surface

- [ ] Create `scripts/workload/deploy.sh` — build + push + deploy all ACA apps (atomic digest)
- [ ] Add deploy action contract (image → ACR → ACA, same digest for web/worker/cron)
- [ ] Create `scripts/workload/start_stop.sh` — scale-to-zero / resume for non-prod
- [ ] Add start/stop action contract (ACA minReplicas=0 / restore)
- [ ] Create `scripts/workload/upgrade.sh` — promote staging → prod (same image digest)
- [ ] Add upgrade action contract (staging validation → prod deploy → post-deploy verify)
- [ ] Add maintenance-state contract (gate traffic, disable crons, flag in registry)
- [ ] Create `scripts/workload/inspect_health.sh` — cross-plane health (ACA + PG + endpoints)
- [ ] Create `scripts/workload/inspect_cost.sh` — Azure Cost Management scoped to IPAI RGs
- [ ] Add workload-level quality-insight placeholders (readiness score, recommendations)

## Phase 3 — Monitoring and Cost Surface

- [ ] Define workload health summary contract (aggregated status from ACA + PG + probes)
- [ ] Define environment status rollups (per-env health badge)
- [ ] Define cost summary contract (monthly cost by workload, by environment, by RG)
- [ ] Add drill-through/link-out pattern to deeper observability tools (Azure Monitor, AppInsights)
- [ ] Create Azure Monitor dashboard for workload-level health view

## Phase 4 — Policy and Drift Controls

- [ ] Add naming/tagging/config policy checks (`scripts/validation/detect_drift.sh`)
- [ ] Add environment parity checks (staging config must match prod contract)
- [ ] Add drift detection and recommendation rules
- [ ] Block promotion on critical contract drift (CI gate in AzDO pipeline)
- [ ] Define custom Azure Policy: no-plaintext-secrets-in-aca
- [ ] Define custom Azure Policy: backup-immutability-required
- [ ] Define custom Azure Policy: defender-enabled-on-subscription
- [x] Assign policies in audit mode to `rg-ipai-*` resource groups — `infra/azure/modules/policy-tag-governance.bicep` (#647)
- [ ] Remediate flagged resources
- [ ] Switch policies from audit to deny/enforce
- [ ] Inventory all plaintext secrets in ACA env vars
- [ ] Create `scripts/workload/secret_migrate.sh` — migrate plaintext to KV references
- [ ] Execute secret migration for all ACA apps
- [ ] Verify zero plaintext secrets via `secret_posture.sh`
- [ ] Enable Defender for Cloud on all subscriptions
- [ ] Create Log Analytics workspace + enable Sentinel
- [ ] Configure basic detection rules (failed auth, resource deletion, policy violation)
- [ ] Create `docs/contracts/SECURITY_HARDENING_CONTRACT.md`

## Phase 5 — Validation Framework

- [ ] Create `scripts/validation/platform_validate.sh` — central orchestrator
- [ ] Create `scripts/validation/health_probes.sh` — endpoint health validation
- [ ] Create `scripts/validation/contract_checks.sh` — addons path, image digest, env parity
- [ ] Create `scripts/validation/secret_posture.sh` — detect plaintext secrets
- [ ] Create `scripts/validation/ha_checks.sh` — backup, replica, failover validation
- [ ] Create `scripts/validation/evidence_report.sh` — structured JSON/HTML evidence
- [ ] Add per-workload workspace/config model (validation targets per registered workload)
- [ ] Add config validation test suite
- [ ] Add HA/recovery validation suite
- [ ] Add smoke/regression validation suite (module install, endpoint health)
- [ ] Generate structured HTML/JSON evidence reports
- [ ] Attach validation evidence to release records
- [ ] Add validation stage to AzDO deploy pipeline (post-deploy gate)
- [ ] Configure validation to block promotion if critical checks fail
- [ ] Document framework in `docs/architecture/platform-validation-framework.md`
- [ ] Register contract in `docs/contracts/PLATFORM_CONTRACTS_INDEX.md`

### 5.1 Resilience Contracts (sub-phase)

- [ ] Audit current PG backup configuration
- [ ] Define backup policy contract: `docs/contracts/BACKUP_POLICY_CONTRACT.md`
- [ ] Enable geo-redundant backup on `pg-ipai-odoo`
- [ ] Configure backup retention (minimum 7 days, target 14 days)
- [ ] Enable soft-delete on backup vault
- [ ] Document ACA replica policy per service role (web: 1-3, worker: 1-2, cron: exactly 1)
- [ ] Define failover posture contract: `docs/contracts/FAILOVER_POSTURE_CONTRACT.md`
- [ ] Define recovery SLA contract: `docs/contracts/RECOVERY_SLA_CONTRACT.md` (RPO < 1h, RTO < 4h)
- [ ] Create `docs/runbooks/disaster-recovery.md`
- [ ] Schedule first DR test on staging environment

## Phase 5.2 — Foundry Registry Overlay

- [ ] Define Foundry resource/project registration schema
- [ ] Define agent/workflow/tool registration schema with repo-source tracking
- [ ] Define ownership and repo-mapping schema
- [ ] Import existing Foundry resources into registry (ipai-copilot-resource, ipai-copilot)

## Phase 5.3 — Promotion and Evidence Binding

- [ ] Define promotion state machine (draft → staged → validated → promoted → retired)
- [ ] Define evidence artifact schema (type, checksum, source, timestamp)
- [ ] Define release-to-evidence binding rules (no promotion without evidence)
- [ ] Wire promotion gate into AzDO pipeline

## Phase 5.4 — Policy Overlay and Drift Reconciliation

- [ ] Define org policy overlay model (IPAI-specific policies not covered by Foundry)
- [ ] Define repo conformance checks (registered assets match deployed assets)
- [ ] Define drift/reconciliation output format (diff between registry and Foundry state)
- [ ] Schedule periodic reconciliation (cron or pipeline)

## Phase 5.5 — Pulser Control Plane (Joule Benchmark)

- [ ] Define **Pulser Formation** schema (env, tenant, systems, config)
- [ ] Create `ssot/pulser/formations.yaml` — formation registry
- [ ] Define **Capability Package** schema (tools, intents, grounding)
- [ ] Create `ssot/pulser/capabilities.yaml` — capability registry
- [ ] Define **Grounding Source** and **Pipeline** metadata schema
- [ ] Implement Pulser onboarding flow (`scripts/pulser/onboard_tenant.sh`)
- [ ] Implement Capability promotion gate (`scripts/pulser/promote_capability.sh`)
- [ ] Implement Identity Binding registry (`ssot/pulser/identity_bindings.yaml`)
- [ ] Document Pulser control plane in `docs/architecture/pulser-control-plane.md`

### Initial Capability Packages
- `pulser_finance_info`, `pulser_finance_navigation`, `pulser_finance_actions`
- `pulser_collections_info`, `pulser_collections_navigation`, `pulser_collections_actions`
- `pulser_procurement_info`, `pulser_procurement_navigation`, `pulser_procurement_actions`
- `pulser_bir_compliance_info`
- `pulser_exec_insights_info`

## Phase 6 — MVP Hardening / Exit Criteria

- [ ] At least one existing workload registered in Workload Center (Odoo ERP)
- [ ] One workload can be deployed and operated from the Workload Center CLI
- [ ] One release path is blocked on failed validation/policy checks
- [ ] One evidence-backed promotion path works end-to-end (staging → prod)
- [ ] Health, quality, and cost are visible at workload level
- [ ] Re-score all 9 SAP-on-Azure benchmark dimensions
- [ ] Document delta closure in `docs/audits/sap-benchmark-rescore/`
- [ ] Produce consolidated scorecard (target: 8/9 Low gap)
- [ ] Capture evidence pack in `docs/evidence/<stamp>/workload-center/`
- [ ] Create `docs/architecture/workload-center.md` — architecture overview
- [ ] Update `docs/architecture/ACTIVE_PLATFORM_BOUNDARIES.md` with Workload Center plane
- [ ] Create operator quickstart: `docs/runbooks/workload-center-ops.md`
- [ ] Update this tasks.md with final status
