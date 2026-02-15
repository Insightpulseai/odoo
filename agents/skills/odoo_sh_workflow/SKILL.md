# SKILL: odoo_sh_workflow

## Intent

Execute an Odoo.sh-style workflow deterministically: branch → build → migrate → verify → promote, producing evidence at each step.

## Inputs

- repo_root (path)
- target_env: dev|stage|prod
- git_ref (branch or sha)
- db_name (must pass DB naming gate)
- evidence_root (default: docs/evidence/<YYYY-MM-DD>/odoo_sh_workflow/)

## Preconditions

- Model routing MUST run first; this skill should be low-cost-model safe except when deep debugging is required.
- Never use UI steps. Use scripts/CI/API only.
- Fail closed if environment config and DB naming gate do not pass.

## Procedure

1. Validate repository invariants
   - confirm config/{dev,staging,prod}/odoo.conf exists
   - confirm docker-compose env substitution is correct
   - confirm db naming gate allowlist is satisfied

2. Prepare run plan (diff-first)
   - compute what will change (git ref, config, migrations)
   - write plan to evidence

3. Execute build/test stage
   - run unit checks relevant to touched files
   - start/verify services if required by workflow runner
   - write logs + results to evidence

4. Apply migrations / upgrade modules (if requested)
   - run upgrade in controlled order
   - capture before/after module list and DB schema signature

5. Verification gates
   - health checks
   - smoke tests
   - basic data integrity checks

6. Promotion
   - promote artifact (immutable) to target env (if applicable)
   - record artifact id + refs

## Evidence Outputs

- plan.json
- run.log
- checks.json (lint/test results)
- migration_report.json (if applicable)
- health.json
- promotion.json (if applicable)

## Escalation

Escalate to remote model tier ONLY when:

- output is ambiguous, multi-step debugging required
- repeated failures with insufficient diagnostics
  Otherwise remain in cheap tier and rely on deterministic tooling.
