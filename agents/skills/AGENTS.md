# AGENTS.md

This file provides guidance to AI coding agents (Claude Code, Cursor, Copilot, etc.) when working with code in this repository.

## Repository Overview

Odoo 19 CE enterprise-parity stack with OdooOps platform integration. Includes agent skills for deployment, testing, and operational workflows.

## Agent Skills

Skills are packaged instructions and scripts that extend agent capabilities. See [`skills/odooops/README.md`](odooops/README.md) for complete documentation.

### Available Skills

| Skill | Description | When to Use |
|-------|-------------|-------------|
| **odooops-deploy** | Deploy Odoo apps to OdooOps platform | "Deploy my app", "Create preview environment", "Deploy to staging" |
| **odooops-test** | Run Playwright E2E tests | "Run tests", "Test deployment", "Check if app works" |
| **odooops-logs** | Fetch environment logs | "Show logs", "Debug error", "What happened?" |
| **odooops-status** | Check deployment status | "Check status", "Environment health", "Test history" |

### Quick Start

```bash
# Deploy current branch to preview
bash skills/odooops/odooops-deploy/scripts/deploy.sh

# Run E2E tests against environment
bash skills/odooops/odooops-test/scripts/test.sh <env-id>

# Check deployment status
bash skills/odooops/odooops-status/scripts/status.sh <env-id>
```

## Creating New Skills

Follow the [Agent Skills](https://agentskills.io/) format. See Vercel's [agent-skills](https://github.com/vercel-labs/agent-skills) repository for reference patterns.

### Directory Structure

```
skills/
  odooops/
    {skill-name}/         # kebab-case directory name
      SKILL.md            # Required: skill definition with metadata
      scripts/            # Required: executable scripts
        {script}.sh       # Bash scripts (preferred)
```

### Skill Template

```markdown
---
name: skill-name
description: One sentence describing when to use this skill. Include trigger phrases.
metadata:
  author: insightpulseai
  version: "1.0.0"
  platform: odooops
---

# Skill Name

Brief description.

## How It Works

1. Step-by-step workflow
2. What the skill does
3. Expected outcomes

## Usage

\```bash
bash /mnt/skills/user/{skill-name}/scripts/{script}.sh [args]
\```

## Output

Show example output with JSON format for programmatic use.

## Present Results to User

Template for how agents should format results when presenting to users.

## Troubleshooting

Common issues and solutions.

## Related Skills

Links to complementary skills.
```

### Best Practices

- **Keep SKILL.md concise** (< 500 lines) - put detailed docs in separate files
- **Write specific descriptions** - helps agents know exactly when to activate
- **Output JSON to stdout** - machine-readable results for agent parsing
- **Status to stderr** - human-readable progress messages
- **Use `set -e`** - fail-fast behavior for scripts
- **Test locally first** - verify scripts work before committing

## Integration with Repository

### OdooOps Platform Integration

Skills integrate with the OdooOps platform ([spec/odoo-sh-next/](../spec/odoo-sh-next/)):

- **API Scripts** ([`scripts/odooops/`](../scripts/odooops/)) - Low-level API clients
- **E2E Tests** ([`tests/e2e/`](../tests/e2e/)) - Playwright test suite
- **CI Workflows** ([`.github/workflows/`](../.github/workflows/)) - GitHub Actions automation

### Browser Automation Pack

Skills leverage the browser automation pack ([spec/odooops-browser-automation/](../spec/odooops-browser-automation/)):

- **odooops-deploy** → Uses `env_create.sh` and `env_wait_ready.sh`
- **odooops-test** → Runs Playwright suite from `tests/e2e/`
- **GitHub Actions** → Orchestrates skills automatically on PR/push

## Configuration

Required environment variables:

```bash
# OdooOps API
export ODOOOPS_API_BASE="https://api.odooops.io"
export ODOOOPS_TOKEN="your-api-token"
export ODOOOPS_PROJECT_ID="your-project-id"

# Optional: Override defaults
export MAX_WAIT_SECONDS=1200  # Environment readiness timeout
export STAGE="preview"         # Default deployment stage
```

Generate tokens at: `https://odooops.io/settings/tokens`

## Development Workflow

### 1) Spec-Driven Development

Before building features, create a Spec Kit bundle in [`spec/`](../spec/):

```bash
mkdir -p spec/feature-name
# Create constitution.md, prd.md, plan.md, tasks.md
```

### 2) Implementation

Follow the plan from the spec:

```bash
# 1) Implement features
# 2) Add tests
# 3) Update docs
# 4) Create agent skill (if applicable)
```

### 3) Testing

```bash
# Run E2E tests
cd tests/e2e
npm run test

# Validate specs
./scripts/spec-kit/validate.sh feature-name

# Check pre-commit hooks
pre-commit run --all-files
```

### 4) Deployment

```bash
# Deploy to preview via skill
bash skills/odooops/odooops-deploy/scripts/deploy.sh preview

# Or via GitHub Actions (automatic on PR)
git push origin feature-branch
```

## Repository Structure

```
.
├── addons/                   # Odoo custom modules (ipai_*)
├── oca-parity/               # OCA community modules
├── spec/                     # Spec Kit bundles
│   ├── odoo-sh-next/         # OdooOps platform spec
│   └── odooops-browser-automation/  # E2E testing spec
├── scripts/                  # Automation scripts
│   └── odooops/              # OdooOps API clients
├── tests/                    # Test suites
│   └── e2e/                  # Playwright E2E tests
├── skills/                   # Agent skills
│   └── odooops/              # OdooOps platform skills
├── .github/workflows/        # CI/CD pipelines
└── CLAUDE.md                 # AI agent instructions (SSOT)
```

## Related Documentation

- [CLAUDE.md](../CLAUDE.md) - Primary agent instructions (SSOT)
- [Spec Kit System](../spec/) - Specification-driven development
- [OdooOps Platform](../spec/odoo-sh-next/) - Platform architecture
- [Browser Automation](../spec/odooops-browser-automation/) - E2E testing system
- [OCA Workflow](../docs/ai/OCA_WORKFLOW.md) - Community module integration

## Resources

- [Agent Skills Format](https://agentskills.io/)
- [Vercel Agent Skills](https://github.com/vercel-labs/agent-skills)
- [Claude Code Documentation](https://docs.anthropic.com/claude/docs/claude-code)
- [Anthropic Skills Guide](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
