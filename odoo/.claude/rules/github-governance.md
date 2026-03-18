---
paths:
  - ".github/**"
---

# GitHub Governance

> GitHub plan details, Apps, Projects v2, PR discipline, commit conventions, CI/CD pipeline inventory.

---

## GitHub App: pulser-hub

```
App ID: 2191216
Client ID: Iv23liwGL7fnYySPPAjS
Webhook URL: https://n8n.insightpulseai.com/webhook/github-pulser
```

**Capabilities:**
- Webhooks -> n8n -> Odoo task creation
- OAuth -> "Sign in with GitHub" for apps
- Installation tokens -> Secure API access

---

## GitHub Projects v2 — API Limits

### Iteration Fields (Quarter/Sprint)

Iteration **values** (Quarter/Sprint) **CANNOT** be created via GitHub API as of 2026.

**Behavior when asked to configure iterations:**
1. Mark the step as: `PHASE_REQUIRES_UI(GitHub iterations API missing)`
2. Output a one-paragraph checklist only (no screen-by-screen guide)
3. Continue automating everything else (fields, statuses, syncing, labels)

**Manual UI Setup Required:**

For **Roadmap** (`Quarter` field):
- Length: 3 months
- Start date: 2026-01-01
- Generate: 4 cycles (Q1-Q4)

For **Execution Board** (`Sprint` field):
- Length: 14 days
- Start date: Next Monday
- Generate: 12-26 cycles

**What CAN be automated:**
- Project creation (`gh project create`)
- Field creation (`gh project field-create --data-type ITERATION`)
- Single select fields with options
- Status fields
- Labels and milestones
- Issue/PR linking

**What CANNOT be automated:**
- Iteration values/cycles
- Iteration start dates
- Iteration lengths

---

## PR Discipline

### Commit Convention

```
feat|fix|refactor|docs|test|chore(scope): description
```

Examples:
- `feat(finance-ppm): add month-end close wizard`
- `fix(workspace): resolve portal access issue`
- `docs(claude): update CLAUDE.md with architecture`
- `chore(ci): add spec validation workflow`

### Chore Scope Conventions (OCA-style)

| Scope | When to Use |
|-------|-------------|
| `chore(oca):` | OCA layer: submodules, `oca.lock.json`, `oca-aggregate.yml`, pins |
| `chore(repo):` | Repo-wide maintenance (docs regen, formatting, housekeeping) |
| `chore(ci):` | Workflows, gating, pre-commit, drift checks |
| `chore(deps):` | Python/Node deps, devcontainer, toolchain pins |
| `chore(deploy):` | Docker compose, nginx, env templates, infra docs |

See [docs/OCA_CHORE_SCOPE.md](docs/OCA_CHORE_SCOPE.md) for full conventions.

### PR Rules

1. Small, focused commits with descriptive messages
2. Run verification before pushing
3. Update docs + tests alongside code changes

---

## CI/CD Pipelines

> **355 total workflows** in `.github/workflows/` (audited 2026-03-08). Key workflows below.

### Core Pipelines

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci-odoo-ce.yml` | Push/PR | Main Odoo CE tests |
| `ci-odoo-oca.yml` | Push/PR | OCA module compliance |
| `spec-kit-enforce.yml` | Push/PR | Validate spec bundle structure |
| `repo-structure.yml` | Push/PR | Verify repo structure |
| `all-green-gates.yml` | Push/PR | All gates must pass |

### Build & Deploy

| Workflow | Purpose |
|----------|---------|
| `build-unified-image.yml` | Build unified Docker image |
| `build-seeded-image.yml` | Build pre-seeded image |
| `deploy-production.yml` | Production deployment |
| `deploy-odoo-prod.yml` | Odoo-specific deployment |

### Quality Gates

| Workflow | Purpose |
|----------|---------|
| `seeds-validate.yml` | Validate seed data |
| `spec-validate.yml` | Validate spec completeness |
| `spec-and-parity.yml` | Enterprise parity checks |
| `infra-validate.yml` | Infrastructure templates |

### Monitoring

| Workflow | Purpose |
|----------|---------|
| `health-check.yml` | Health check execution |
| `finance-ppm-health.yml` | Finance PPM checks |
| `ipai-prod-checks.yml` | IPAI production checks |

---

*Last updated: 2026-03-16*
