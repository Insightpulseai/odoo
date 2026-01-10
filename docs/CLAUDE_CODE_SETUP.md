# Claude Code Setup Guide

**Practical "use it tomorrow" setup + prompt pack for Odoo + React UI work**

## What Claude Code Is (Operationally)

A terminal-native agent that can:
- Read/understand your repo
- Edit files + run commands
- Make commits/PRs
- Pull from external sources via MCP (Drive/Figma/Slack)

It's basically "coding agent + shell runner" with a CLI interface.

## Install + Run

```bash
# macOS/Linux/WSL
curl -fsSL https://claude.ai/install.sh | bash

# Navigate to project
cd ~/odoo-ce

# Start Claude Code
claude
```

## Project Bootstrap (Already Complete)

Your repo already has the essential structure:

### 1. `CLAUDE.md` (Project Rules) ✅

Located at root - defines non-negotiables:
- Branch naming conventions
- Lint/test commands
- PR template rules
- Spec-kit enforcement
- Odoo module layout
- Secrets management

### 2. Unified Verification Command ✅

**Single entrypoint**: `./scripts/verify.sh`

```bash
# What it runs:
./scripts/verify.sh
# → repo structure check
# → spec validation
# → Python syntax
# → Formatting (black, isort)
# → Local CI

# Quick mode (syntax only):
./scripts/verify.sh --quick
```

This is what CI and Claude both run for consistency.

## Claude Code Prompt Pack

Copy/paste these into `claude -p "..."` for common tasks:

### A) Odoo: Mount React Chat UI in Backend

```bash
claude -p "
Implement an Odoo 18 CE module under addons/ipai/ipai_chat_ui that mounts a React chat surface as a web client action.

Requirements:
- __manifest__.py declares web.assets_backend for mount js + css + compiled bundle
- Provide minimal OWL/JS action registry entry action 'ipai_chat_surface'
- Add backend menu item to open the action
- Include scripts/odoo_smoke.sh updates to verify module installs + action loads
- Add tests (Python or JS) for basic invariants

Run repo lint/tests and fix until green.
"
```

### B) Token Bridge: Fluent/OpenAI Tokens → Odoo SCSS

```bash
claude -p "
Create a token bridge between Control Room and Odoo:

1. Add static/src/tokens.css with CSS variables:
   - Colors (--tbwa-yellow: #F1C100, --tbwa-black: #000000)
   - Radius, shadow, typography

2. Add Odoo SCSS mapping file to bind to backend theme variables

3. Apply tokens to chat surface components:
   - Message composer
   - Message bubbles
   - Sidebar navigation

4. Document in docs/ui/TOKENS.md

Keep diffs minimal and maintain OCA compliance.
"
```

### C) Convert Mock UI to Reusable Component Library

```bash
claude -p "
Refactor apps/control-room/src/app into organized component library:

Structure:
- src/components/
  - Nav, ChatPanel, StatusTable, Toggle, KpiCard
- src/pages/
  - Overview, Projects, Docs, Settings
- src/lib/
  - types, helpers, smokeTests

Add:
- Basic unit tests for smokeTests
- Page routing tests
- Component prop validation

Follow existing Fluent UI v9 patterns.
"
```

### D) Odoo Module Scaffolding (OCA Compliant)

```bash
claude -p "
Scaffold new Odoo 18 CE module: ipai_<module_name>

Follow OCA standards:
- addons/ipai/ipai_<module_name>/
- Proper __init__.py and __manifest__.py
- Security (ir.model.access.csv)
- Views (list, form, search)
- Tests in tests/ directory
- README.rst with installation/configuration

Auto-add to:
- .githooks/pre-commit validation
- scripts/deploy-odoo-modules.sh
- docs/modules/ipai_<module_name>.md

Run verification: ./scripts/verify.sh
"
```

### E) Finance PPM Dashboard Enhancement

```bash
claude -p "
Enhance ipai_finance_ppm dashboard with new chart:

1. Add new ECharts visualization for [metric name]
2. Create controller endpoint /ipai/finance/ppm/api/[metric]
3. Update dashboard template to include new chart
4. Add backend service method to calculate metric
5. Write tests for metric calculation

Requirements:
- Follow existing ECharts patterns in ipai_finance_ppm_dashboard
- Maintain TBWA branding (#F1C100 yellow, #000000 black)
- Add to docs/ppm/architecture.md

Run: ./scripts/verify.sh
"
```

### F) n8n Workflow Creation

```bash
claude -p "
Create n8n workflow for [workflow name]:

1. Design workflow JSON for automations/n8n/workflows/
2. Document in automations/n8n/README_[WORKFLOW].md
3. Add credentials requirements
4. Include test/validation steps

Pattern:
- Use webhook triggers
- Odoo XML-RPC nodes for data fetching
- Mattermost notification nodes
- Error handling with retry logic

Reference existing workflows in automations/n8n/
"
```

### G) Fix Failing CI Job

```bash
claude -p "
Fix CI job: [job name from .github/workflows/]

Steps:
1. Read .github/workflows/[job].yml
2. Identify failure from GitHub Actions logs
3. Fix root cause (don't just skip tests)
4. Verify locally: ./scripts/verify.sh
5. Update workflow if needed
6. Test fix in PR

Maintain strict quality gates - no shortcuts.
"
```

### H) Spec-Kit Enforcement

```bash
claude -p "
Create spec bundle for: [feature name]

Structure:
spec/[feature-slug]/
├── constitution.md   # Non-negotiables
├── prd.md            # Product requirements
├── plan.md           # Implementation plan
└── tasks.md          # Task checklist

Follow template from spec/pulser-master-control/

Validate: ./scripts/spec_validate.sh
"
```

## Using Docs Indexing

Your repo has comprehensive documentation. Claude Code can index it:

```bash
# In Claude Code session:
claude -p "
Index project documentation:

1. Scan docs/ directory for all .md files
2. Create docs/claude_code/INDEX.md with:
   - Table of contents
   - File paths with descriptions
   - Key concepts and search terms

3. Generate llms.txt for external tools:
   - List all critical docs
   - Add navigation structure
   - Include module references

Output: docs/claude_code/llms.txt
"
```

## CI Integration Pattern

Your repo has extensive GitHub Actions. Claude Code can work with CI:

### Manual Trigger Workflow (Template)

```yaml
# .github/workflows/claude-fix.yml
name: claude-fix
on:
  workflow_dispatch:
    inputs:
      prompt:
        description: "What should Claude do?"
        required: true
        type: string

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Claude Fix
        env:
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
          PROMPT: ${{ inputs.prompt }}
        run: |
          # Wire Claude Code with prompt
          # (requires org auth setup)
          echo "$PROMPT" | claude

      - name: Verify
        run: ./scripts/verify.sh

      - name: Create PR
        if: success()
        uses: peter-evans/create-pull-request@v5
        with:
          title: "fix: Claude automated fix"
          body: "Automated fix via Claude Code"
```

## Repository-Specific Patterns

### Odoo Module Development

Your workflow:
1. Plan with spec bundle
2. Scaffold with OCA template
3. Implement models/views/security
4. Add to deployment scripts
5. Run verification
6. Create PR

**Claude Command**:
```bash
claude -p "Follow Odoo module development workflow for: [module name]"
```

### Control Room UI Development

Your workflow:
1. Design in Fluent UI v9
2. Implement with TBWA tokens
3. Test responsive breakpoints
4. Build production bundle
5. Visual QA

**Claude Command**:
```bash
claude -p "Follow Control Room UI development workflow for: [feature name]"
```

### Finance PPM Enhancement

Your workflow:
1. Check Finance PPM umbrella dependencies
2. Implement in correct sub-module
3. Update ECharts dashboard
4. Test with real BIR data
5. Document in runbook

**Claude Command**:
```bash
claude -p "Follow Finance PPM enhancement workflow for: [feature name]"
```

## Best Practices

### 1. Always Verify Before Commit

```bash
# Run this after any Claude Code changes:
./scripts/verify.sh

# If it fails, fix the issues before committing
```

### 2. Use Spec-Kit for Non-Trivial Work

```bash
# Create spec first:
claude -p "Create spec bundle for: [feature]"

# Then implement:
claude -p "Implement spec/[feature-slug]/plan.md"
```

### 3. Follow Odoo Conventions

Your repo enforces:
- OCA module structure
- Security (RLS, ir.model.access)
- View patterns (list, form, search, kanban)
- Test coverage requirements

**Claude Command**:
```bash
claude -p "Audit addons/ipai/[module]/ for OCA compliance"
```

### 4. Maintain CI Quality Gates

Your CI enforces:
- Python syntax (no syntax errors)
- Formatting (black, isort)
- Module install tests
- Spec validation
- Docker build success

**Never bypass these** - fix the root cause instead.

### 5. Use Project Memory for Complex Tasks

```bash
# Load project context:
python .claude/query_memory.py config

# Query specific areas:
python .claude/query_memory.py arch        # Architecture
python .claude/query_memory.py commands    # All commands
python .claude/query_memory.py rules       # Project rules
```

## Troubleshooting

### Claude Code Not Finding Files

**Issue**: Claude can't find modules or docs

**Fix**:
```bash
# Update project tree:
tree -L 3 -I 'node_modules|__pycache__|*.pyc|.git' > docs/REPO_TREE.generated.md

# Then tell Claude:
claude -p "Read docs/REPO_TREE.generated.md for project structure"
```

### Verification Failing

**Issue**: `./scripts/verify.sh` returns errors

**Fix**:
```bash
# Check individual steps:
./scripts/verify.sh --quick         # Syntax only
./scripts/repo_health.sh            # Structure
./scripts/spec_validate.sh          # Specs

# Fix reported issues before proceeding
```

### Module Not Installing

**Issue**: Odoo module fails to install

**Fix**:
```bash
# Check manifest:
python -c "import ast; ast.parse(open('addons/ipai/[module]/__manifest__.py').read())"

# Check security:
ls -la addons/ipai/[module]/security/ir.model.access.csv

# Test in docker:
docker compose exec odoo-core odoo -d odoo_core -i [module] --stop-after-init
```

## Quick Reference Card

```bash
# Essential Commands
./scripts/verify.sh                 # Full verification
./scripts/verify.sh --quick         # Syntax check only
./scripts/deploy-odoo-modules.sh    # Deploy Odoo modules
docker compose up -d                # Start stack
docker compose logs -f odoo-core    # View logs

# Claude Code Basics
claude                              # Start interactive session
claude -p "prompt here"             # One-shot command
claude -h                           # Help

# Verification Shortcuts
make lint                           # Python formatting
make test                           # Run all tests
make docs                           # Generate docs
```

## Next Steps

1. **Install Claude Code**: `curl -fsSL https://claude.ai/install.sh | bash`
2. **Try a prompt**: Use one of the prompts above
3. **Review output**: Check generated files and changes
4. **Verify**: Run `./scripts/verify.sh`
5. **Commit**: Follow git workflow from CLAUDE.md

## Resources

- **Main Docs**: `CLAUDE.md` (project rules)
- **External Memory**: `.claude/query_memory.py` (config DB)
- **Verification**: `scripts/verify.sh` (quality gates)
- **Workflows**: `.github/workflows/` (CI automation)
- **Module Docs**: `docs/modules/` (per-module guides)
- **Architecture**: `docs/architecture/` (system design)
