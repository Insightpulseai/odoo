# Continue+ CI Templates

Reusable CI workflow snippets for OCA/Odoo repositories with agent-aware execution.

## Problem Solved

When using IDE agents (Claude Code, Continue), changes to:
- Spec files (`spec/**`)
- Agent config (`.claude/**`, `.continue/**`)
- Documentation (`docs/**`, `*.md`)
- CI/infra (`.github/**`, `scripts/**`)

...incorrectly trigger full Odoo CI matrix runs, causing:
- Red PRs for non-code changes
- Wasted CI minutes
- Slower merge velocity

## Templates

### 1. `odoo-paths-ignore.yml`

Drop-in `paths-ignore` configuration for Odoo CI workflows.

**Usage**: Copy the `on.pull_request.paths-ignore` section to your workflow.

### 2. `preflight-classify.yml`

Reusable workflow that classifies changed files and outputs gating flags.

**Usage**: Call as a reusable workflow, then gate jobs on `run_odoo` output.

### 3. `spec-kit-check.yml`

Validates spec bundles meet Continue+ requirements.

**Usage**: Add to PRs that touch `spec/**`.

## Quick Start

### Option A: Add paths-ignore to existing workflows

Edit your `.github/workflows/test.yml`:

```yaml
on:
  pull_request:
    paths-ignore:
      - 'spec/**'
      - '.claude/**'
      - '.continue/**'
      - 'CLAUDE.md'
      - 'docs/**'
      - 'scripts/**'
      - '.github/workflows/spec-kit-*.yml'
      - '.github/workflows/agent-*.yml'
```

### Option B: Use preflight classification

1. Copy `agent-preflight.yml` to `.github/workflows/`
2. Reference the output in downstream jobs:

```yaml
jobs:
  preflight:
    uses: ./.github/workflows/agent-preflight.yml

  odoo-tests:
    needs: preflight
    if: needs.preflight.outputs.run_odoo == 'true'
    # ... rest of job
```

## Path Classification Rules

| Pattern | Category | Triggers Odoo CI |
|---------|----------|------------------|
| `addons/**` | code | YES |
| `odoo/**` | code | YES |
| `oca/**` | code | YES |
| `tests/**` | tests | YES |
| `docs/**` | docs | NO |
| `*.md` | docs | NO |
| `spec/**` | spec | NO |
| `.claude/**` | agent | NO |
| `.continue/**` | agent | NO |
| `CLAUDE.md` | agent | NO |
| `.github/**` | infra | NO |
| `scripts/**` | infra | NO |
| `deploy/**` | infra | NO |
| `infra/**` | infra | NO |

## Verification

To verify path classification is working:

1. Create a docs-only PR
2. Check that `agent-preflight` job shows `run_odoo=false`
3. Check that Odoo CI jobs are skipped

## FAQ

**Q: What if I need Odoo CI for infra changes?**

A: Modify the classification rules in `agent-preflight.yml`. The default is conservative (skip non-code).

**Q: How do I debug classification?**

A: Check the `agent-preflight` job summary in GitHub Actions. It shows all flags and changed files.

**Q: Can I use this with OCA's standard CI?**

A: Yes. Add the `paths-ignore` section to OCA's `.github/workflows/*.yml` files.
