# Odoo.sh-Equivalent Platform — Tasks

**Last Updated**: 2026-03-11

---

## Phase 1: Doctrine & SSOT Artifacts

- [x] Create `infra/ssot/platform/personas.yaml` with four canonical personas
- [x] Create `infra/ssot/platform/capability_matrix.yaml` with full C1-C9 taxonomy
- [x] Create `infra/ssot/platform/odoosh_equivalent_capabilities.yaml` with feature mapping
- [ ] Add CI schema validation for platform SSOT YAML files
- [ ] Verify capability matrix covers all Odoo.sh features from mapping doc

## Phase 2: Environment Lifecycle

- [ ] Implement `scripts/infra/aca_env_create.sh` for branch-based ACA provisioning
- [ ] Implement `scripts/infra/aca_env_destroy.sh` for environment teardown
- [ ] Create GitHub Actions workflow for auto-provisioning on branch push
- [ ] Implement 7-day idle TTL cleanup cron
- [ ] Implement PR-linked staging with database clone
- [ ] Create `ops.platform_environments` table migration
- [ ] Test: branch push → environment available in < 5 min

## Phase 3: Logs, Shell & Monitoring

- [ ] Configure Log Analytics workspace per environment tier
- [ ] Implement `scripts/infra/platform_logs.sh` for log tailing/search
- [ ] Implement `scripts/infra/platform_exec.sh` for shell access with persona gating
- [ ] Deploy Mailpit sidecar for dev/staging environments
- [ ] Create health dashboard endpoint aggregating all environment probes
- [ ] Test: log write → visible in query in < 10 seconds

## Phase 4: Promotion & Gates

- [ ] Create `.github/workflows/platform-promote.yml` promotion workflow
- [ ] Implement modular gate jobs (CI, maturity score, smoke test)
- [ ] Add manual approval steps for QA and PM personas
- [ ] Implement rollback via ACA revision swap
- [ ] Create `infra/ssot/platform/promotion_gates.yaml` gate configuration
- [ ] Test: full promotion cycle dev → staging → production

## Phase 5: Backup, DNS & Hardening

- [ ] Implement automated PostgreSQL backup pipeline
- [ ] Test restore from backup to staging environment
- [ ] Configure Cloudflare wildcard DNS for branch environments
- [ ] Implement deployment history tracking in `ops.deployment_history`
- [ ] Create `.devcontainer/` configuration for Codespaces integration
- [ ] Configure Claude Code SessionStart hooks for platform context
- [ ] Security review: validate persona isolation matches capability_matrix.yaml

## Developer UX Integration

- [ ] Validate structural outline navigation works with Odoo module structure
- [ ] Configure spec-aware context panel linking to `infra/spec/` bundles
- [ ] Set up runtime context panel showing environment + branch + DB target
- [ ] Configure split layout presets (code+logs, spec+impl, diff+terminal)
- [ ] Test diff-first workflow with spec-aware drift detection
- [ ] Validate evidence artifact browser for benchmark outputs
