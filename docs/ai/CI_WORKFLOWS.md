# CI/CD Pipelines
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

153 total workflows. Run `ls .github/workflows/ | wc -l` for current count.

## Core Pipelines

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | Push/PR | Main CI tests |
| `odoo-ci-gate.yml` | Push/PR | Odoo-specific CI gate |
| `ci-odoo-oca.yml` | Push/PR | OCA module compliance |
| `spec-kit-enforce.yml` | Push/PR | Validate spec bundle structure |
| `repo-structure.yml` | Push/PR | Verify repo structure |
| `all-green-gates.yml` | Push/PR | All gates must pass |
| `canonical-gate.yml` | Push/PR | Canonical setup validation |
| `agent-preflight.yml` | Push/PR | Agent preflight checks |
| `ai-naming-gate.yml` | Push/PR | AI naming convention enforcement |

## Build & Deploy

| Workflow | Purpose |
|----------|---------|
| `build-unified-image.yml` | Build unified Docker image |
| `build-seeded-image.yml` | Build pre-seeded image |
| `build-odoo-ce19-ee-parity.yml` | Build Odoo CE 19 with EE parity |
| `deploy-production.yml` | Production deployment |
| `deploy-odoo-prod.yml` | Odoo-specific deployment |
| `cd-production.yml` | Continuous delivery to production |
| `branch-promotion.yml` | Branch promotion workflow |

## Quality Gates

| Workflow | Purpose |
|----------|---------|
| `seeds-validate.yml` | Validate seed data |
| `spec-validate.yml` | Validate spec completeness |
| `spec-and-parity.yml` | Enterprise parity checks |
| `infra-validate.yml` | Infrastructure templates |
| `azure-waf-parity.yml` | Azure WAF parity gates |
| `auto-install-parity-modules.yml` | Auto-install parity modules |
| `backlog-coverage.yml` | Backlog coverage tracking |

## Security

| Workflow | Purpose |
|----------|---------|
| `audit-contract.yml` | Security audit contract |
| `auth-email-ai-gate.yml` | Auth/email AI gate |

## Monitoring

| Workflow | Purpose |
|----------|---------|
| `health-check.yml` | Health check execution |
| `finance-ppm-health.yml` | Finance PPM checks |
| `ipai-prod-checks.yml` | IPAI production checks |

See `.github/workflows/` for the full list.
