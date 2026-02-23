# CI/CD Policy Matrix

## Repository Classification

- **Type:** Odoo monorepo (OCA-style core) with embedded Supabase control-plane subtree
- **Primary runtime boundary:** `addons/`
- **Embedded control plane:** `supabase/`
- **Policy sources:** `ssot/`, `spec/`, `docs/architecture/*`

## Purpose

Define path-scoped CI/CD enforcement rules so:

- Odoo-first runtime quality remains the highest priority
- Supabase control-plane checks are enforced without redefining repo identity
- docs/spec/agent-only changes do not trigger unnecessary full runtime validation
- agent-generated output is gated by deterministic checks

---

## Enforcement Model

### Gate Levels

| Level | Name | Description |
|-------|------|-------------|
| P0 | Blocking / merge-blocking | Must pass before merge |
| P1 | Deploy-blocking | Required before staging/prod deploy |
| P2 | Non-blocking warning | Advisory; produces evidence/artifacts |
| P3 | Scheduled audit | Periodic drift/compliance checks |

### Trigger Modes

- Pull Request (path-scoped)
- Push to `main`
- Manual dispatch
- Scheduled (cron)

### Change Scope Resolution

CI jobs MUST be path-scoped and only run relevant checks for touched subtrees:

| Changed path | Triggered checks |
|-------------|-----------------|
| `addons/**` | Odoo runtime checks |
| `supabase/**` | Supabase control-plane checks |
| `.github/**`, `scripts/**`, `ssot/**` | Policy/infrastructure checks |
| `docs/**`, `spec/**`, `agents/**`, `skills/**` | Documentation/agent governance checks |

---

## Subtree Policy Matrix

### A. `addons/` — Odoo Runtime (Primary, OCA-style governed)

#### Classification

- **Priority:** Highest
- **Identity impact:** Defines repository runtime behavior
- **Conventions:** OCA-style for `addons/oca/*`; thin bridge/meta only for `addons/ipai/*`

#### Blocking PR Gates (P0)

- Manifest sanity (`__manifest__.py` presence/format/version/deps)
- Python lint/static checks (scoped to changed modules)
- XML parse validation and view inheritance sanity
- Transaction safety scan (forbidden `cr.commit()` / `cr.rollback()` except allowlisted cases)
- Exception hygiene scan (broad exception catches flagged/blocked based on policy)
- Odoo install/upgrade smoke for changed modules (`-i`/`-u` path)
- Targeted tests for changed modules (Python)
- JS/Owl tests when web assets in changed modules are touched (if applicable)

#### Deploy-Blocking Gates (P1)

- Expanded install/upgrade matrix for touched modules + dependencies
- Critical navigation smoke (core apps + touched modules)
- Asset integrity verification for web-affecting changes
- Log/traceback sanity on boot and module upgrade

#### Advisory / Audit (P2/P3)

- Performance regression sampling (query count / timing)
- Coverage trends
- Deprecated API usage scan (warn-first)

#### Evidence Outputs

- Install/upgrade logs
- Test reports (JUnit/XML if available)
- Failed xpath/template diagnostics
- Traceback excerpts with module attribution

---

### B. `supabase/` — Embedded Control Plane (Non-Odoo subtree)

#### Classification

- **Priority:** High (secondary to `addons/`)
- **Identity impact:** Control-plane / data-plane support, not repo primary runtime
- **Conventions:** Supabase-native layout and tooling

#### Blocking PR Gates (P0)

- SQL migration syntax/validation checks
- Migration ordering / timestamp naming sanity
- Edge Function lint/build/test (changed functions only)
- Scheduler binding verification (no comment-only scheduled state for functions declared as scheduled)
- Config schema validation (`config.toml` / environment contract checks where applicable)

#### Deploy-Blocking Gates (P1)

- Migration dry-run / apply verification in test environment
- Edge Function deploy package integrity
- Scheduler registration drift check against SSOT (if scheduler SSOT exists)

#### Advisory / Audit (P2/P3)

- Function cold-start/perf snapshots
- Orphaned function detection
- Cron drift audits

#### Evidence Outputs

- Migration validation logs
- Function build artifacts
- Scheduler binding report
- Drift report (expected vs actual)

---

### C. `.github/`, `scripts/`, `ssot/` — Governance & Enforcement Layer

#### Classification

- **Priority:** High (enables trust in all other gates)
- **Identity impact:** CI/CD correctness and policy determinism
- **Conventions:** Repo-native governance + SSOT schemas

#### Blocking PR Gates (P0)

- Workflow YAML syntax/lint
- Script syntax/static checks (Python/Bash as applicable)
- Policy script unit/smoke tests
- SSOT schema/shape validation (YAML/JSON contracts)
- Cross-file consistency checks (parity/allowlist/policy references if implemented)

#### Deploy-Blocking Gates (P1)

- Protected-branch workflow integrity checks
- Required-checks presence verification (ensure no accidental gate removal)

#### Advisory / Audit (P2/P3)

- Stale workflow detection
- Dead script detection
- SSOT drift reporting

#### Evidence Outputs

- Policy validation report
- Workflow lint output
- SSOT schema validation results

---

### D. `docs/`, `spec/`, `agents/`, `skills/` — Documentation, Spec Kit, Agent Governance

#### Classification

- **Priority:** Medium (unless policy/spec files are required by change type)
- **Identity impact:** Governance + reproducibility + agent behavior
- **Conventions:** Spec Kit bundles for initiatives; repo-native agent docs

#### Blocking PR Gates (P0) — conditional / path-scoped

- Markdown syntax/lint (if enabled)
- Link checks (internal docs links)
- Spec Kit completeness checks (`spec/<slug>/{constitution,prd,plan,tasks}.md`) for spec-governed changes
- Agent schema/structure validation when `agents/**` or `skills/**` changes
- Trilateral docs sync check (`CLAUDE.md` / `AGENTS.md` / `GEMINI.md`) if applicable

#### Deploy-Blocking Gates (P1)

- None by default (unless release process explicitly requires runbook/spec updates)

#### Advisory / Audit (P2/P3)

- Docs freshness checks
- Missing evidence references in runbooks
- Agent prompt drift checks

#### Evidence Outputs

- Docs lint/link reports
- Spec completeness report
- Agent registry validation report

---

## Cross-Cutting Policies

### Odoo-First Gating Priority

When multiple subtrees are changed in a PR:

1. `addons/` gates are evaluated as primary runtime risk
2. `supabase/` gates run for control-plane changes
3. Governance/docs checks run path-scoped and do not escalate runtime jobs unless directly required

### Path-Scoped Execution (Required)

Docs-only PRs MUST NOT trigger full Odoo install/upgrade matrices.
Policy-only PRs MUST NOT trigger runtime deploy validations unless workflows affecting deploy logic changed.

### Agent-Generated Change Safeguards

Changes authored by agents MUST produce:

- Scoped diff summary
- Evidence artifacts from executed checks
- Explicit list of skipped checks (if any)
- Failure reason + rollback note for partial execution

### Exception Handling for Temporary Policy Relaxation

Any temporary gate bypass must include:

- Owner
- Reason
- Expiry date
- Compensating control
- Follow-up task reference

---

## Initial Implementation Priority (Phased)

### Phase 1 — Immediate / Highest ROI

- `addons/` P0: manifest + XML parse + transaction safety + exception hygiene + changed-module install/upgrade smoke
- `supabase/` P0: migration validation + changed function build/lint
- Governance P0: workflow/script syntax + policy script checks
- Docs/spec P0 (conditional): Spec Kit completeness + agent file validation

### Phase 2

- JS/Owl test path (HOOT/web helpers)
- Scheduler binding drift checks
- Critical navigation smoke tests
- Trilateral docs sync enforcement

### Phase 3

- Performance trend audits
- Scheduled drift reporting
- Richer artifact/evidence dashboards

---

## Ownership Model (Agent/Persona-aligned)

| Owner | Scope |
|-------|-------|
| `odoo.backend.engineer` | Python/Odoo runtime checks |
| `odoo.frontend.engineer` | JS/Owl/assets tests |
| `odoo.xml.views.specialist` | XML/xpath/template checks |
| `odoo.test.engineer` | Test selection + regression expansion |
| `odoo.release.manager` | Release/deploy gating and evidence collation |
| `odooops.cicd.guard` | Workflow policy + gate orchestration |
| `supabase.controlplane.guard` | Migrations/functions/schedulers checks |

---

## Alignment Statement (Canonical Tree)

This policy matrix assumes and preserves the canonical repository structure:

- Odoo monorepo (OCA-style core) as primary repo identity
- Embedded `supabase/` control-plane subtree as secondary platform layer
- Distinct top-level boundaries for `config/`, `docker/`, `runtime/`, `scripts/`, `infra/`, `docs/`, `spec/`, `ssot/`, and optional `apps/`/`packages/`

**This document MUST NOT be interpreted as redefining the repository as a Supabase-first monorepo.**

> Optional next step: `ssot/ci_cd_policy_matrix.yaml` — machine-readable companion with schema version `v1`.
> Define only after this markdown is agreed as the policy contract.
