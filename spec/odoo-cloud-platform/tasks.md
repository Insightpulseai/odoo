# Tasks — Odoo Cloud Platform (IPAI)

## Phase 1: Control-plane SSOTs (foundational)

- [x] `platform/ssot/architecture/odoo-cloud-platform-bom.yaml` (stub)
- [x] `platform/ssot/runtime/branch-environment-contract.yaml` (stub)
- [x] `platform/ssot/release/odoo-cloud-release-gates.yaml` (stub)
- [ ] `platform/ssot/ui/odoo-cloud-platform-ui.yaml` (deferred)

## Phase 2: Promotion pipeline

- [ ] `azure-pipelines-odoo-promote.yml` — branch → env promotion with gates
- [ ] Smoke test stage (pre-promote)
- [ ] Eval gate stage (reads `platform/ssot/release/odoo-cloud-release-gates.yaml`)
- [ ] Evidence capture stage (writes to `docs/evidence/<ts>/odoo-promote/`)

## Phase 3: Backup / restore

- [ ] Automated backup cron against pg-ipai-odoo
- [ ] Restore runbook at `docs/runbooks/odoo-backup-restore.md`
- [ ] Timed restore drill; capture evidence
- [ ] RTO/RPO targets recorded in branch-env contract

## Phase 4: Release gate integration

- [ ] Tie odoo-cloud-release-gates.yaml to ssot/release/go-live-readiness.yaml
- [ ] Require Khalil (FD) approval for prod promotions affecting finance
- [ ] Produce readiness review per spec/_templates/go-live-readiness-template.md

## Phase 5: Operator dashboard (optional / deferred)

- [ ] Power BI dashboard over promotion history + env health
- [ ] Databricks PPM Control Tower integration
- [ ] Read-only; no writes from dashboard

## Phase 6: Pulser-assisted operator actions

- [ ] Bind `pulser_erp` pack tasks: suggest_promotion, summarize_env_state,
      prepare_safe_action
- [ ] Tools: odoo_read + guarded_odoo_write (never commit prod without FD approval)
- [ ] Judges: `erp_mutation_guard_judge` + `branch_context_judge` + `policy_judge`

## Out of scope for first cutover

- Full Odoo.sh parity (features like Live Deploy, fork-from-prod)
- Cross-region HA/DR
- Customer-facing self-service environments (only platform operators for now)
- AI-native Studio replacement (per ee-capability-target-map.yaml)

## Related
- [constitution.md](constitution.md)
- [prd.md](prd.md)
- [plan.md](plan.md)
