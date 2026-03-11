# Odoo.sh-Equivalent Platform — PRD

**Version**: 1.0.0
**Status**: Draft
**Last Updated**: 2026-03-11
**Owner**: InsightPulse AI Platform Team

---

## Executive Summary

A self-hosted platform specification that replaces Odoo.sh capabilities with an open, CLI-first, GitOps-driven alternative. Defines the canonical personas, capability taxonomy, environment promotion model, and Developer UX requirements that `odoo/` implementation specs consume.

---

## Personas

### Developer

**Goal**: Ship features 3x faster with full environment isolation and instant feedback.

**Access scope**: Feature branches, development environments, logs, shell, CI results.

**Key workflows**:
- Create feature environment from branch (< 3 min)
- View live logs for any running environment
- Open shell/exec session into running container
- Review diffs and staged changes before promotion
- Access spec-aware context for the active feature

#### Developer UX Capabilities

The platform provides a high-productivity operator experience for developers:

**Core Navigation**
- Structural outline view: jump through modules, classes, methods, manifests, XML views, specs, and runbooks
- Breadcrumb navigation: always show current repo/file/module path
- Pinned working set: keep critical files, specs, and logs pinned during a task
- Fast file/action launcher: open files, commands, environments, logs, and runbooks from one command surface

**Editing Productivity**
- Multi-cursor / bulk edit support
- Collapsible regions / code folding
- Bracket and structure awareness
- Symbol rename / safe refactor helpers
- Quick preview for generated artifacts (YAML, JSON, markdown, HTML/email)

**Context Awareness**
- Diff-first workflow: always surface changed files, staged changes, and generated drift
- Spec-aware context panel: show linked constitution/prd/plan/tasks for the active feature
- Runtime context panel: show current environment, Docker context, target DB, active branch, deployment target
- SSOT reference links: fast access to canonical policy/docs from the current file

**Run / Debug Ergonomics**
- One-command task runner
- Per-environment run targets: dev / staging / prod-safe commands separated clearly
- Live logs panel
- Exec / shell entry point
- Port and health visibility
- Benchmark/test launch shortcuts

**Review and Validation**
- True diff stories: easy comparison of expected vs actual generated output
- Inline validation feedback
- Policy/gate visibility
- Preview for email/template rendering
- Evidence artifact browser: quick open for reports, logs, screenshots, benchmark outputs

**Focus and Workflow Control**
- Zen/focus mode
- Moveable panels/views
- Split layout presets: code + logs, spec + implementation, diff + terminal, benchmark + evidence
- Follow-cursor outline filtering
- Minimal distraction mode for long debugging sessions

**Collaboration and Traceability**
- PR/issue/spec cross-links
- Commit / release context
- Deployment history view
- Environment promotion visibility
- Rollback/runbook quick access

### Tester (QA)

**Goal**: Validate that staged changes match spec requirements before production promotion.

**Access scope**: Staging environments, test execution, diff/comparison tools, evidence artifacts.

**Key workflows**:
- Access staging environment matching a PR
- Run test suites against staging
- Compare expected vs actual output (diff stories)
- Review evidence artifacts from CI runs
- Validate gate passage before promotion approval

### Project Manager

**Goal**: Track release readiness and make informed go/no-go decisions.

**Access scope**: Dashboards, deployment history, promotion status, gate results.

**Key workflows**:
- View deployment history and promotion pipeline
- Check gate status across all environments
- Review maturity benchmark scores
- Track feature completion against spec tasks
- Approve or defer production promotions

### System Administrator

**Goal**: Maintain platform health, security, and operational continuity.

**Access scope**: Full platform access including secrets management, DNS, monitoring, and backup/restore.

**Key workflows**:
- Manage DNS records and domain routing
- Configure monitoring alerts and thresholds
- Execute backup and restore operations
- Manage secrets rotation and access policies
- Review audit logs and security events

---

## Capability Taxonomy

### C1: Git Integration & CI

| Capability | Dev | QA | PM | SysAdmin |
|------------|-----|----|----|----------|
| Branch-based environment creation | Write | Read | Read | Write |
| CI pipeline trigger and monitoring | Write | Read | Read | Write |
| Build history and artifact access | Read | Read | Read | Read |
| Submodule/dependency management | Write | — | — | Write |

### C2: Logs & Runtime Visibility

| Capability | Dev | QA | PM | SysAdmin |
|------------|-----|----|----|----------|
| Live log tailing | Write | Read | — | Write |
| Log search and filtering | Read | Read | — | Read |
| Structured log queries | Read | Read | — | Read |
| Log retention configuration | — | — | — | Write |

### C3: Exec / Shell Access

| Capability | Dev | QA | PM | SysAdmin |
|------------|-----|----|----|----------|
| Shell into dev environment | Write | — | — | Write |
| Shell into staging environment | Read | — | — | Write |
| Shell into production | — | — | — | Write |
| Command execution audit trail | Read | Read | Read | Read |

### C4: Staging & Promotion

| Capability | Dev | QA | PM | SysAdmin |
|------------|-----|----|----|----------|
| Create staging from PR | Auto | Read | Read | Write |
| Promote staging → production | Request | Approve | Approve | Execute |
| Rollback production | — | — | — | Execute |
| Promotion gate configuration | — | — | — | Write |

### C5: Mail Catcher / Non-Prod Mail Sink

| Capability | Dev | QA | PM | SysAdmin |
|------------|-----|----|----|----------|
| View intercepted emails (dev/staging) | Read | Read | — | Read |
| Configure mail sink routing | — | — | — | Write |
| Forward test emails | Write | Write | — | Write |

### C6: Backups & Restore

| Capability | Dev | QA | PM | SysAdmin |
|------------|-----|----|----|----------|
| Trigger manual backup | — | — | — | Execute |
| View backup history | Read | — | Read | Read |
| Restore to staging | — | — | — | Execute |
| Restore to production | — | — | — | Execute |
| Backup schedule configuration | — | — | — | Write |

### C7: Monitoring & Availability

| Capability | Dev | QA | PM | SysAdmin |
|------------|-----|----|----|----------|
| View health dashboards | Read | Read | Read | Read |
| Configure alert thresholds | — | — | — | Write |
| View SLO/SLI metrics | Read | — | Read | Read |
| Incident response actions | — | — | — | Execute |

### C8: DNS & Domain Routing

| Capability | Dev | QA | PM | SysAdmin |
|------------|-----|----|----|----------|
| View active domain mappings | Read | — | — | Read |
| Configure branch-to-subdomain routing | — | — | — | Write |
| Manage production domain | — | — | — | Write |
| TLS certificate management | — | — | — | Write |

### C9: Deployment History & Release Readiness

| Capability | Dev | QA | PM | SysAdmin |
|------------|-----|----|----|----------|
| View deployment timeline | Read | Read | Read | Read |
| Compare environment versions | Read | Read | Read | Read |
| View gate pass/fail history | Read | Read | Read | Read |
| Access rollback runbooks | Read | — | — | Execute |

---

## Environment Promotion Model

```
Feature Branch ──push──→ [Dev Environment]
                              │
                         PR opened
                              │
                              ▼
                        [Staging Environment]
                              │
                     CI gates pass + approval
                              │
                              ▼
                      [Production Environment]
```

### Promotion Gates

| Gate | Required For | Automated |
|------|-------------|-----------|
| CI tests pass | staging → prod | Yes |
| Azure maturity score ≥ 85% | staging → prod | Yes |
| Odoo smoke test pass | staging → prod | Yes |
| QA sign-off | staging → prod | Manual |
| PM approval | staging → prod | Manual |
| No open P0 issues | staging → prod | Yes |

---

## Odoo.sh Feature Equivalence

| Odoo.sh Feature | Platform Equivalent | Implementation Stack |
|-----------------|---------------------|---------------------|
| Production environment | ACA production revision | Azure Container Apps |
| Staging environments | PR-linked ACA revisions | GitHub Actions + ACA |
| Development branches | Ephemeral ACA environments | GitHub Actions + ACA |
| Online editor | GitHub Codespaces / Claude Code | GitHub / Anthropic |
| Web shell / SSH | ACA exec + `az containerapp exec` | Azure CLI |
| Log tailing | Azure Monitor + Log Analytics | Azure Monitor |
| Build history | GitHub Actions run history | GitHub |
| Submodule management | Git submodules + gitaggregate | GitHub |
| Automated backups | Azure Backup + pg_dump cron | Azure + scripts |
| Mail catcher | Mailpit (dev/staging) | Self-hosted container |
| Module installation | `odoo --stop-after-init -i` via CI | GitHub Actions |
| Database manager | Disabled (single DB per env) | By design |

---

## Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Environment creation time | < 5 minutes |
| Build time (cached) | < 3 minutes |
| Log latency (write to visible) | < 10 seconds |
| Backup frequency (production) | Every 6 hours |
| RTO (production) | < 30 minutes |
| RPO (production) | < 6 hours |
| Platform availability | 99.5% |

---

## Output Artifacts

| Artifact | Format | Path |
|----------|--------|------|
| Capability matrix | YAML | `infra/ssot/platform/capability_matrix.yaml` |
| Persona definitions | YAML | `infra/ssot/platform/personas.yaml` |
| Odoo.sh equivalence map | YAML | `infra/ssot/platform/odoosh_equivalent_capabilities.yaml` |
| Promotion gate config | YAML | `infra/ssot/platform/promotion_gates.yaml` (future) |

---

## Dependencies

| Dependency | Source | Purpose |
|------------|--------|---------|
| Azure Platform Maturity Benchmark | `infra/spec/azure-platform-maturity-benchmark/` | Compute + Deployment domain scores |
| OdooOps Platform spec | `odoo/docs/portfolio/specs/odooops-platform/` | Runtime implementation details |
| SSOT Platform Rules | `.claude/rules/ssot-platform.md` | Governance constraints |
