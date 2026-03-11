# OdooOps Agent Skills

Agent skills for working with OdooOps platform (Odoo.sh Next). These skills extend AI coding agents (Claude Code, Cursor, GitHub Copilot, etc.) with deployment and testing capabilities.

## Available Skills

### odooops-deploy

Deploy Odoo applications to OdooOps platform with preview/staging/production environments.

**Use when:**
- "Deploy my Odoo app"
- "Create a preview environment"
- "Deploy to staging"
- "Promote to production"

**Features:**
- Ephemeral preview environments per PR/branch
- Staging validation with masked production data
- Production deployments with promotion gates
- Automatic build triggering and environment provisioning

### odooops-test

Run Playwright E2E tests against any OdooOps environment.

**Use when:**
- "Run tests"
- "Test my deployment"
- "Check if the app works"
- "Run E2E suite"

**Features:**
- Full Playwright test suite execution
- Artifact collection (traces, videos, screenshots)
- Headless and headed modes
- Chrome extension support (Phase 3)

### odooops-logs

Fetch logs from OdooOps environments for debugging.

**Use when:**
- "Show me the logs"
- "Check deployment logs"
- "Debug this error"
- "What happened?"

**Features:**
- Real-time log streaming
- Historical log retrieval
- Filtered log queries (by level, service, time range)
- JSON parsing for structured logs

### odooops-status

Check deployment and test status across environments.

**Use when:**
- "Check deployment status"
- "What's the health of my app?"
- "Show test history"
- "Environment overview"

**Features:**
- Environment health checks
- Test run history
- Build status tracking
- Resource usage metrics

## Installation

### Claude Code / Claude.ai

1. Copy skill directory to `~/.claude/skills/`:
   ```bash
   cp -r skills/odooops/odooops-deploy ~/.claude/skills/
   cp -r skills/odooops/odooops-test ~/.claude/skills/
   ```

2. Restart Claude Code

### Cursor / Copilot

Skills are auto-detected from the `skills/` directory when working in this repository.

## Configuration

Set these environment variables:

```bash
export ODOOOPS_API_BASE="https://api.odooops.io"
export ODOOOPS_TOKEN="your-api-token"
export ODOOOPS_PROJECT_ID="your-project-id"
```

Generate tokens at: `https://odooops.io/settings/tokens`

## Usage Examples

### Deploy to Preview

```bash
# From command line
bash skills/odooops/odooops-deploy/scripts/deploy.sh preview

# Or ask Claude Code
"Deploy my current branch to a preview environment"
```

### Run E2E Tests

```bash
# From command line
bash skills/odooops/odooops-test/scripts/test.sh env_preview_abc123

# Or ask Claude Code
"Run E2E tests against the preview environment"
```

### Complete Workflow

```bash
# 1) Deploy to staging
bash skills/odooops/odooops-deploy/scripts/deploy.sh staging release/v1.2.0

# 2) Run E2E tests
bash skills/odooops/odooops-test/scripts/test.sh <staging-env-id>

# 3) Check status
bash skills/odooops/odooops-status/scripts/status.sh <staging-env-id>

# 4) If green, promote to production
bash skills/odooops/odooops-deploy/scripts/promote.sh <staging-env-id> prod
```

## Integration with Browser Automation Pack

These skills integrate with the browser automation pack ([`spec/odooops-browser-automation/`](../../spec/odooops-browser-automation/)):

- **odooops-deploy** uses `scripts/odooops/env_create.sh` and `scripts/odooops/env_wait_ready.sh`
- **odooops-test** runs the Playwright suite from `tests/e2e/`
- **GitHub Actions** workflow (`.github/workflows/e2e-playwright.yml`) orchestrates these skills automatically

## Skill Format

Skills follow the [Agent Skills](https://agentskills.io/) format:

```
skills/
  odooops/
    odooops-deploy/
      SKILL.md              # Skill definition with metadata
      scripts/
        deploy.sh           # Executable script
```

## Development

### Creating New Skills

1. Create skill directory:
   ```bash
   mkdir -p skills/odooops/skill-name/scripts
   ```

2. Write `SKILL.md` with metadata:
   ```markdown
   ---
   name: skill-name
   description: When to use this skill...
   ---
   # Skill Name
   ...
   ```

3. Create executable scripts in `scripts/`

4. Test locally before committing

### Best Practices

- Keep `SKILL.md` under 500 lines
- Write scripts that output JSON to stdout
- Write status messages to stderr
- Use `set -e` for fail-fast behavior
- Reference other scripts via relative paths

## Related Documentation

- [Browser Automation Pack](../../spec/odooops-browser-automation/) - E2E testing integration
- [Odoo.sh Next PRD](../../spec/odoo-sh-next/prd.md) - Platform specification
- [OdooOps API Scripts](../../scripts/odooops/) - Low-level API clients

## License

LGPL-3 (same as Odoo CE)
