# Microsoft DevOps Lifecycle — IPAI Surface Mapping

**Date**: 2026-03-01
**Version**: 1.0.0
**Scope**: Insightpulseai/odoo monorepo — all four DevOps lifecycle phases
**Assessment SSOT**: `ssot/advisor/assessments/microsoft_devops_lifecycle.yaml`
**Remediation Workbook**: `ssot/advisor/workbooks/devops_baseline.yaml`

---

## 1. Microsoft DevOps Lifecycle Model

Microsoft's DevOps framework organizes software delivery into four continuous
phases that form a loop. Each phase feeds the next, and Operate feeds back into
Plan.

```
┌─────────────────────────────────────────────────────────────────┐
│                  Microsoft DevOps Lifecycle                     │
│                                                                 │
│   ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐  │
│   │          │      │          │      │          │      │          │  │
│   │  PLAN    │─────▶│ DEVELOP  │─────▶│ DELIVER  │─────▶│ OPERATE  │  │
│   │          │      │          │      │          │      │          │  │
│   └──────────┘      └──────────┘      └──────────┘      └──────────┘  │
│         ▲                                                    │         │
│         └────────────────────────────────────────────────────┘         │
│                         (continuous feedback)                           │
└─────────────────────────────────────────────────────────────────┘

PLAN:     Backlog, requirements, specifications, OKRs
DEVELOP:  Code authoring, review, quality gates, agentic coding
DELIVER:  CI/CD pipelines, deployment environments, release gates
OPERATE:  Monitoring, alerting, incident response, automation
```

**Reference**: [Microsoft — What is DevOps?](https://learn.microsoft.com/devops/what-is-devops)

---

## 2. IPAI Surface Mapping

The table below maps each DevOps lifecycle phase to the IPAI toolchain, the
canonical SSOT file governing that surface, and the posture check IDs defined
in the assessment YAML.

| Phase   | IPAI Tool / Surface                    | SSOT Reference                                     | Posture Check IDs                                                                                                     |
|---------|----------------------------------------|----------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| Plan    | Plane (project management)             | `plane.insightpulseai.com`                         | `plan_backlog_structure`, `plan_milestones_linked`                                                                    |
| Plan    | Spec Kit (`spec/<feature-slug>/`)      | `spec/agent/constitution.md`                       | `plan_spec_bundle_coverage`, `plan_spec_tasks_generated`                                                              |
| Develop | GitHub (`Insightpulseai/odoo`)         | `ssot/advisor/rulepacks/github_governance.yaml`    | `develop_feature_branches`, `develop_required_status_checks`, `develop_codeowners`                                   |
| Develop | VS Code + GitHub Copilot               | `.github/copilot-instructions.md`                  | `develop_copilot_instructions`                                                                                        |
| Develop | Ops Console agentic runs               | `apps/ops-console/app/api/runs/[runId]`            | `develop_agentic_coding_contract`                                                                                     |
| Deliver | GitHub Actions (153 workflows)         | `.github/workflows/`                               | `deliver_actions_minimum_permissions`                                                                                 |
| Deliver | Vercel (Next.js apps)                  | `infra/vercel/`                                    | `deliver_vercel_ci_gated`, `deliver_deployment_environments`                                                          |
| Deliver | DigitalOcean App Platform              | `ssot/infra/digitalocean/monitoring.yaml`          | `deliver_deployment_environments`, `deliver_rollback_runbooks`                                                        |
| Operate | DigitalOcean Monitoring (odoo-prod)    | `ssot/infra/digitalocean/monitoring.yaml`          | `operate_do_monitoring_alerts`                                                                                        |
| Operate | Supabase (`spdtwktxdalcfigzeqrz`)      | `supabase/migrations/`                             | `operate_supabase_migrations_only`                                                                                    |
| Operate | n8n (`n8n.insightpulseai.com`)         | `automations/n8n/workflows/`                       | `operate_n8n_workflows_in_repo`                                                                                       |
| Operate | Ops Advisor (ops-console)              | `ssot/advisor/`                                    | `operate_ops_advisor_resolution_rate`                                                                                 |

### Surface Ownership Summary

```
Plan:
  plane          → backlog, milestones, OKRs
  spec_kit       → constitution.md, prd.md, plan.md, tasks.md

Develop:
  github         → branch protection, rulesets, CODEOWNERS, secret scanning
  vscode_copilot → .github/copilot-instructions.md
  ops_runs       → agentic coding audit trail (ops.runs table)

Deliver:
  github_actions → CI pipelines, permissions, deployment jobs
  vercel         → Next.js production deployments, preview environments
  do_app_platform → backend service deployments (OCR, Agent, n8n)

Operate:
  do_monitoring  → droplet alerts (CPU, disk, memory, bandwidth)
  supabase       → schema migrations, ops.* tables, Vault
  n8n            → workflow automations, credential references
  ops_advisor    → finding scans, resolution tracking, workbooks
```

---

## 3. Gap Analysis Methodology

### 3.1 Running the Assessment

The assessment YAML (`ssot/advisor/assessments/microsoft_devops_lifecycle.yaml`)
is the machine-readable definition of expected posture. To evaluate current state:

1. **Trigger via Ops Console**: Navigate to ops.insightpulseai.com, select the
   `microsoft_devops_lifecycle` assessment, and click Run Scan.

2. **Trigger via platform events**: The Ops Advisor scheduled scan (configured in
   `ssot/advisor/`) runs the assessment on its configured schedule. Query results:
   ```sql
   SELECT * FROM ops.platform_events
   WHERE event_type = 'advisor_scan'
     AND payload->>'assessment_id' = 'microsoft_devops_lifecycle'
   ORDER BY created_at DESC LIMIT 5;
   ```

3. **Interpret findings**: Each failing posture check maps to a `gap_indicator`
   string in the assessment YAML. The finding record in `ops.advisor_findings`
   contains the check ID, severity, and gap description.

### 3.2 Using the Workbook

The devops_baseline workbook (`ssot/advisor/workbooks/devops_baseline.yaml`)
is the operator's remediation guide. It provides 12 ordered steps:

```
Step 1  → Run assessment, capture scan_id and open findings
Step 2  → Plan: Plane backlog + spec bundle coverage
Step 3  → Plan: tasks.md completeness for Develop-phase features
Step 4  → Develop: branch protection, CODEOWNERS, copilot instructions
Step 5  → Develop: agentic coding run traceability
Step 6  → Deliver: Vercel environment protection rules
Step 7  → Deliver: GitHub Actions permissions audit
Step 8  → Operate: DO monitoring alerts
Step 9  → Operate: n8n workflows in repo
Step 10 → Operate: Supabase migration-only schema changes
Step 11 → Operate: Ops Advisor resolution rate >= 80%
Step 12 → Scorecard: audit document committed to docs/audits/
```

Steps with `evidence_required: true` (steps 1, 2, 4, 6, 8, 11, 12) block
workbook completion in the Ops Console until the operator captures proof.

### 3.3 Severity Definitions

| Severity | Response SLA | Meaning                                                          |
|----------|--------------|------------------------------------------------------------------|
| high     | 24 hours     | Immediate risk: production can fail, code can merge unreviewed  |
| medium   | 7 days       | Posture degraded: manual workarounds needed                     |
| low      | 30 days      | Best practice gap: no immediate risk, but technical debt accrues |

### 3.4 Finding Resolution Flow

```
Scan creates finding → assigned to team member → remediation via workbook step
    → evidence captured → finding marked resolved → resolution rate updated
    → next scan confirms check passes → finding closed
```

---

## 4. Posture Improvement Roadmap

### Phase 1: Immediate (high-severity gaps — resolve within 24 hours)

Priority order based on blast radius:

1. **develop_feature_branches** — Protect main with org-level ruleset if not present.
   Blast radius: any contributor can push breaking changes directly to production.

2. **develop_required_status_checks** — Add ci/lint and ci/typecheck as required
   checks. Blast radius: untested code merges to main and deploys.

3. **operate_do_monitoring_alerts** — Create missing DO monitoring alerts.
   Blast radius: production outages go undetected.

4. **operate_supabase_migrations_only** — Audit for schema drift, capture in
   migrations. Blast radius: schema state is undocumented and un-rollbackable.

5. **deliver_vercel_ci_gated** — Confirm no Vercel project auto-deploys to
   production on push. Blast radius: broken builds go to production instantly.

### Phase 2: Short-term (medium-severity gaps — resolve within 7 days)

1. **develop_codeowners** — Add CODEOWNERS entries for ssot/, supabase/migrations/,
   .github/workflows/, infra/.

2. **develop_copilot_instructions** — Create .github/copilot-instructions.md with
   IPAI repo conventions (module naming, OCA-first, CE-only, commit format).

3. **deliver_deployment_environments** — Add required reviewers to the production
   GitHub environment.

4. **operate_n8n_workflows_in_repo** — Export all production n8n workflows to
   automations/n8n/workflows/ and commit.

5. **operate_ops_advisor_resolution_rate** — Triage open findings, assign owners,
   set deadlines. Target 80% resolution rate within 30 days.

6. **deliver_rollback_runbooks** — Author docs/runbooks/ROLLBACK.md covering all
   deployment surfaces.

### Phase 3: Ongoing (continuous improvement)

1. **plan_spec_bundle_coverage** — Enforce via CI: PRs that introduce a new Plane
   epic must include a spec bundle commit. Add to ci/spec-validate.sh.

2. **plan_spec_tasks_generated** — Add /speckit.tasks to the standard feature
   kickoff workflow. Enforce tasks.md presence in spec-validate CI check.

3. **develop_agentic_coding_contract** — Wire Claude Code to emit ops.runs records
   on every session that produces a commit. Use the ops-console API.

4. **deliver_actions_minimum_permissions** — Automated scan: grep all workflows for
   missing permissions declarations and open a PR to add minimum-scope permissions.

5. **plan_milestones_linked** — Quarterly Plane milestone creation becomes part of
   the quarterly planning ritual (not enforced by CI, enforced by process).

---

## 5. References

### Microsoft DevOps Framework

- [What is DevOps? — Microsoft Learn](https://learn.microsoft.com/devops/what-is-devops)
- [Plan — Microsoft DevOps](https://learn.microsoft.com/devops/plan/what-is-agile)
- [Develop — Microsoft DevOps](https://learn.microsoft.com/devops/develop/git/what-is-git)
- [Deliver — Microsoft DevOps](https://learn.microsoft.com/devops/deliver/what-is-continuous-delivery)
- [Operate — Microsoft DevOps](https://learn.microsoft.com/devops/operate/what-is-monitoring)

### IPAI SSOT Files

| File | Purpose |
|------|---------|
| `ssot/advisor/assessments/microsoft_devops_lifecycle.yaml` | Assessment YAML — posture checks per phase |
| `ssot/advisor/workbooks/devops_baseline.yaml` | Remediation workbook — 12-step operator guide |
| `ssot/advisor/rulepacks/github_governance.yaml` | GitHub WAF governance rulepack (Develop phase) |
| `ssot/infra/digitalocean/monitoring.yaml` | DO monitoring alert definitions (Operate phase) |
| `spec/agent/constitution.md` | Spec Kit governance rules (Plan phase) |
| `.github/copilot-instructions.md` | Copilot context for IPAI conventions (Develop phase) |
| `supabase/migrations/` | Supabase schema migration history (Operate phase) |
| `automations/n8n/workflows/` | n8n workflow JSON exports (Operate phase) |
| `apps/ops-console/app/api/runs/[runId]` | Agentic coding run audit API (Develop phase) |
| `docs/audits/` | Dated assessment scorecard outputs |

### Related Architecture Docs

- `docs/architecture/SSOT_BOUNDARIES.md` — Which surface owns what
- `docs/architecture/PLATFORM_REPO_TREE.md` — Canonical path registry
- `docs/runbooks/ROLLBACK.md` — Deployment rollback procedures
- `docs/contracts/PLATFORM_CONTRACTS_INDEX.md` — Cross-domain contracts

### Audit History

Audit scorecards are committed to `docs/audits/devops_lifecycle_<YYYYMMDD>.md`
after each workbook run. The first audit is created in step 12 of the devops_baseline
workbook and establishes the baseline. Subsequent audits track improvement over time.

Recommended review cadence: **quarterly** (every 90 days), or after any significant
infrastructure change affecting Plan, Develop, Deliver, or Operate surfaces.
