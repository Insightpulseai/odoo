# Quality Engineering Model

> Defines testing doctrine, test taxonomy, release gates, rollback criteria, and service readiness.
> **SSOT**: `ssot/governance/azdo-execution-hierarchy.yaml` § `quality_gates`, `definition_of_done`
> **Ref**: [Shift testing left](https://learn.microsoft.com/en-us/devops/develop/shift-left-make-testing-fast-reliable)

---

## 0. Testing Doctrine

> Most quality signal must be produced before merge by fast, reliable,
> low-dependency tests owned by the people changing the code.

### Core Principles

1. **Shift left**: Most testing completes before merge to main. PRs fail on required test levels.
2. **Lowest level first**: Prefer lighter tests when they provide the same signal as heavier ones. Default to unit tests.
3. **Reliability over coverage**: Unreliable/flaky tests are engineering debt. Fix or delete — never ignore.
4. **No UI tests by default**: UI tests are discouraged because they tend to be unreliable. Use synthetic monitoring and API-level tests instead.
5. **Design for testability**: Testability is a primary design concern, reviewed alongside code quality and architecture.
6. **Test code = product code**: Test code is held to the same quality bar, review standard, and style as production code.
7. **Code-owner accountability**: Code owners are accountable for testing their components. Test code lives next to product code.
8. **Consistent environments**: Tests run the same way from local dev through CI and higher environments.

### Test Taxonomy (L0–L4)

| Level | Name | Dependencies | Where it runs | Example |
|-------|------|-------------|---------------|---------|
| L0 | Unit (in-memory) | None or mocks only | Pre-commit, PR | Python `unittest`, JS `vitest` |
| L1 | Unit (minimal deps) | Minimal external (config files, small fixtures) | Pre-commit, PR | Odoo `--test-enable` with mocked DB calls |
| L2 | Functional (bounded) | Real DB, filesystem, or service stubs | PR, pre-merge | Odoo test install in `test_<module>`, Supabase migration dry-run |
| L3 | Functional (deployed) | Deployed service environment, may use stubs | Pre-production | Navigation smoke, API integration tests against staging |
| L4 | Production-integrated | Live production (restricted, read-only where possible) | Post-deploy (controlled) | Synthetic monitoring, health probes |

### Pipeline Gate Mapping

| Stage | Required Levels | Policy Source |
|-------|----------------|---------------|
| Pre-commit (local) | L0, L1 | Developer discipline |
| Pull request (CI) | L0, L1, selected L2 | `infra/ssot/ci_cd_policy_matrix.yaml` P0 gates |
| Pre-merge to main | Required L2 | `infra/ssot/ci_cd_policy_matrix.yaml` P0 gates |
| Pre-production (CD) | Required L3 | `infra/ssot/ci_cd_policy_matrix.yaml` P1 gates |
| Post-deploy | Controlled L4 | Synthetic monitoring + health checks |

See `infra/ssot/ci_cd_policy_matrix.yaml` § `testing_policy` for the machine-readable gate mapping.

### Flakiness Policy

- A test that fails intermittently without code changes is **flaky**
- Flaky tests must be triaged within 1 sprint of detection
- Resolution options: fix, quarantine (with Azure Boards tracking Issue), or delete
- Quarantined tests do not block CI but are tracked as engineering debt
- Target: zero quarantined tests (flaky backlog must trend to zero)

---

## 1. Definition of Done

A work item is complete when ALL of these are true:

- [ ] Acceptance criteria verified with evidence
- [ ] Links to PRs, specs, or evidence docs present
- [ ] Security scans green (no open critical/high findings)
- [ ] Runtime health check passing (for deployed changes)
- [ ] No open Blocked By links
- [ ] Dashboard widgets reflect current state

---

## 2. Test Policy by Change Type

| Change Type | Required Tests | Evidence |
|-------------|---------------|----------|
| Odoo module change | Unit tests (`--test-enable`), test install in `test_<module>` | `docs/evidence/<stamp>/<module>/test.log` |
| Infrastructure change | `terraform plan` diff, smoke test post-apply | Plan output + health check |
| CI/CD pipeline change | Dry-run or test trigger on non-main branch | Workflow run log |
| Configuration change | Validate config syntax, restart affected service | Health check post-restart |
| Documentation change | Link validation, spell check (if configured) | CI green |

### Odoo Test Classification

Every test failure must be classified per `.claude/rules/testing.md`:

| Classification | Meaning | Action |
|----------------|---------|--------|
| `passes locally` | Init and tests clean | Mark as compatible |
| `init only` | Installs but has no tests | Note; cannot claim tested |
| `env issue` | Fails due to test env | Re-run with adjusted env or document limitation |
| `migration gap` | Incomplete 19.0 migration | Report upstream; do not patch locally |
| `real defect` | Functional failure | Fix or report with traceback |

---

## 3. PR Quality Gates

Required status checks on protected branches:

| Gate | Tool | Blocks Merge |
|------|------|:------------:|
| CI lint/typecheck | GitHub Actions | Yes |
| Unit tests | GitHub Actions | Yes |
| SSOT surface guard | GitHub Actions | Yes |
| Secret scanning | GHAS | Yes |
| Code scanning (SAST) | GHAS | Yes |
| Dependency review | GHAS | Yes |
| Reviewer approval | GitHub | Yes (1 review) |

---

## 4. Release Readiness Checklist

Before promoting from `dev` → `staging` → `prod`:

- [ ] All CI gates green on the merge commit
- [ ] Security scans show no new critical/high findings
- [ ] Container image vulnerability scan clean
- [ ] Build metadata includes commit hash and AB# work-item ID
- [ ] Changelog or PR summary documents what changed
- [ ] Rollback plan identified (previous healthy ACA revision)

---

## 5. Rollback Criteria

Rollback is triggered when any of these thresholds are breached post-deploy:

| Signal | Threshold | Action |
|--------|-----------|--------|
| Health check | Fails within 90 seconds | Automatic rollback (ACA revision shift) |
| HTTP 5xx rate | > 5% over 5 minutes | Manual rollback decision |
| Container restarts | > 3 in 15 minutes | Investigate → rollback if unresolved |
| Defender alert | Critical runtime anomaly | Immediate rollback + incident |

Rollback mechanism: ACA revision management — shift traffic to previous healthy revision.

---

## 6. Service Readiness for New Workloads

Before a new service is deployed to production:

- [ ] Health endpoint (`/health`) implemented and returning structured status
- [ ] Application Insights instrumentation configured
- [ ] Azure Monitor alerts defined (5xx, latency, restarts)
- [ ] Defender for Containers scanning enabled
- [ ] DNS entry in `infra/dns/subdomain-registry.yaml` (if public)
- [ ] Front Door origin configured (if public)
- [ ] Key Vault secrets provisioned
- [ ] Managed identity assigned
- [ ] Evidence captured in `docs/evidence/`

---

## Cross-References

- [devops_operating_model.md](../governance/devops_operating_model.md) — Pillar 3 mapping
- [devsecops_operating_model.md](devsecops_operating_model.md) — security gates
- [runtime_security.md](runtime_security.md) — runtime controls
- [platform_delivery_contract.md](platform_delivery_contract.md) — tooling consistency, automation, isolation
- [release_management_model.md](release_management_model.md) — progressive exposure, rollout rings
- [ci_cd_policy_matrix.yaml](../../infra/ssot/ci_cd_policy_matrix.yaml) — machine-readable gate mapping
- [azdo-execution-hierarchy.yaml](../../ssot/governance/azdo-execution-hierarchy.yaml) — DoD

---

*Last updated: 2026-03-17*
