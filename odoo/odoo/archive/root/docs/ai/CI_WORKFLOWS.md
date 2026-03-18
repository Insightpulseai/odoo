# CI/CD Pipelines
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.
> Full taxonomy: [docs/ci/WORKFLOW_TAXONOMY.md](../ci/WORKFLOW_TAXONOMY.md) (audited 2026-03-08)

---

**360 total workflows** (audited 2026-03-08). Only 2 are reusable (`workflow_call`).
Every push to main triggers up to 268 workflow runs.

Run `ls .github/workflows/*.yml | wc -l` for current count.

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
| `build-odoo19-ee-parity.yml` | Build Odoo CE 19 with EE parity |
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

## Family Distribution (audited 2026-03-08)

| Family | Count | % |
|--------|------:|--:|
| odoo-module-ci | 132 | 36.5% |
| spec-policy-gate | 79 | 21.8% |
| deploy-release | 40 | 11.0% |
| agent-ai | 29 | 8.0% |
| infrastructure | 20 | 5.5% |
| security-scan | 18 | 5.0% |
| docs-gen | 16 | 4.4% |
| node-app-ci | 15 | 4.1% |
| scheduled-maintenance | 7 | 1.9% |
| python-lint | 3 | 0.8% |
| other/stub | 3 | 0.9% |

## Deprecated (safe to delete)

4 workflows confirmed self-deprecated:
- `domain-lint.yml` — references .net domain
- `no-deprecated-repo-refs.yml` — self-labeled deprecated
- `odoo-import-artifacts.yml` — marked LEGACY
- `terraform-cloudflare-dns.yml` — marked "(deprecated)"

## Consolidation Target

See [WORKFLOW_TAXONOMY.md](../ci/WORKFLOW_TAXONOMY.md) for the 3-layer consolidation plan
(reusable workflows → org templates → repo wrappers). Target: ~238 workflows after Phase 1-4.

See `.github/workflows/` for the full list.
