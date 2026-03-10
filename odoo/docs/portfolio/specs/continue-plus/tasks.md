# Continue+ Tasks

## Spec Reference
`spec/continue-plus/`

---

## Phase 1: Spec-Kit Structure

- [x] Create `spec/continue-plus/constitution.md` - Invariant rules
- [x] Create `spec/continue-plus/prd.md` - Product requirements
- [x] Create `spec/continue-plus/plan.md` - Implementation plan
- [x] Create `spec/continue-plus/tasks.md` - This checklist

## Phase 2: Enforcement Tooling

- [x] Create `scripts/spec-kit-enforce.py` - Validation script
  - [x] Check spec bundle presence
  - [x] Detect placeholders (TODO/TBD/LOREM)
  - [x] Enforce minimum content (≥100 words)
  - [x] Output JSON report for CI
- [x] Create `.github/workflows/spec-kit-enforce.yml` - CI workflow
  - [x] Run on all PRs
  - [x] Fail on missing spec for `/ship` commits
  - [x] Warn on placeholders

## Phase 3: CI-Aware Execution

- [x] Create `.github/workflows/agent-preflight.yml` - Diff classifier
  - [x] Detect code vs docs vs infra changes
  - [x] Output `run_odoo` boolean
  - [x] Gate downstream jobs
- [ ] Update existing Odoo workflows with `paths-ignore`
  - [ ] `.github/workflows/test.yml`
  - [ ] `.github/workflows/pre-commit.yml`
  - [ ] Other OCA workflows

## Phase 4: Continue Integration

- [x] Create `.continue/rules/agentic.md` - Agent behavior rules
- [x] Create `.continue/prompts/plan.md` - /plan command
- [x] Create `.continue/prompts/implement.md` - /implement command
- [x] Create `.continue/prompts/verify.md` - /verify command
- [x] Create `.continue/prompts/ship.md` - /ship command
- [ ] Update `.continue/config.json` with slash commands

## Phase 5: CI Templates Library

- [x] Create `infra/ci/continue-plus/` directory
- [x] Create `odoo-paths-ignore.yml` - Reusable paths-ignore
- [x] Create `preflight-classify.yml` - Reusable classifier
- [x] Create `spec-kit-check.yml` - Reusable spec validation
- [x] Create `README.md` - Usage instructions

## Phase 6: Documentation

- [ ] Update `CLAUDE.md` with Continue+ integration
- [ ] Add Continue+ to implementation plan
- [ ] Create migration guide for existing repos

---

## Verification Evidence

| Check | Status | Notes |
|-------|--------|-------|
| Spec bundle complete | PENDING | |
| Placeholders removed | PENDING | |
| Enforcement script works | PENDING | |
| CI workflows pass | PENDING | |
| Continue commands work | PENDING | |

---

## Notes

- Phase 1-2 are blocking for `/ship`
- Phase 3-4 can be done in parallel
- Phase 5 is nice-to-have for ecosystem reuse
