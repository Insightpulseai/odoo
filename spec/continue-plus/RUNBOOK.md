# Continue+ Runbook

**Version**: 1.0.0
**Date**: 2025-12-22

This runbook documents how to run Continue locally and configure headless automation.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Headless Automation](#headless-automation)
4. [Command Reference](#command-reference)
5. [CI Integration](#ci-integration)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

```bash
# Node.js 18+ (for Continue CLI)
node --version  # v18.x or v20.x

# Python 3.11+ (for validation scripts)
python3 --version  # Python 3.11.x

# PyYAML (for YAML validation)
pip install pyyaml

# Git (for version control)
git --version
```

### Repository Setup

```bash
# Clone the repository
git clone <repo-url>
cd odoo-ce

# Make scripts executable
chmod +x scripts/*.sh

# Verify setup
./scripts/validate-continue-config.sh
```

---

## Local Development

### 1. IDE Integration (VS Code)

Install the Continue extension from the VS Code marketplace:

```
Name: Continue
Publisher: Continue
Link: https://marketplace.visualstudio.com/items?itemName=Continue.continue
```

After installation:

1. Open Command Palette (Cmd/Ctrl + Shift + P)
2. Search for "Continue: Focus Continue Input"
3. The Continue panel will open in the sidebar

### 2. Configuration Files

The Continue configuration lives in `.continue/`:

```
.continue/
├── config.json           # Main configuration
├── rules/
│   ├── agentic.md        # Role boundaries
│   ├── spec-kit.yaml     # Spec enforcement rules
│   ├── notion-ppm.yaml   # Domain-specific rules
│   └── medallion-architecture.yaml
└── prompts/
    ├── plan.md           # /plan command prompt
    ├── implement.md      # /implement command prompt
    ├── verify.md         # /verify command prompt
    └── ship.md           # /ship command prompt
```

### 3. Using Slash Commands

In the Continue chat panel:

```
/plan Add user authentication to the API

/implement Follow the plan in spec/auth-feature/plan.md

/verify

/ship
```

### 4. Spec-Driven Workflow

1. **Create spec bundle**:
   ```bash
   mkdir -p spec/my-feature
   touch spec/my-feature/{constitution,prd,plan,tasks}.md
   ```

2. **Define requirements** in `prd.md`

3. **Run /plan** to generate implementation plan

4. **Review and approve** the plan in `plan.md`

5. **Run /implement** to make changes

6. **Run /verify** to check all tests pass

7. **Run /ship** to generate PR

---

## Headless Automation

### 1. Install Continue CLI

```bash
# Install globally
npm install -g @anthropic-ai/continue

# Or use npx
npx @anthropic-ai/continue --version
```

### 2. Configuration for Headless

Create `.continuerc.json` in repo root:

```json
{
  "model": "claude-3-5-sonnet-20241022",
  "temperature": 0,
  "contextWindowLimit": 100000,
  "roles": {
    "planner": {
      "allowEdit": false
    },
    "implementer": {
      "allowEdit": true
    },
    "verifier": {
      "allowEdit": true,
      "allowExecute": ["pytest", "npm test", "pre-commit"]
    }
  }
}
```

### 3. Running Headless Commands

```bash
# Run a plan command
npx continue run --prompt "/plan Add dark mode support" --output plan-output.md

# Run implementation
npx continue run --prompt "/implement" --context spec/dark-mode/plan.md

# Run verification
npx continue run --prompt "/verify"

# Create PR
npx continue run --prompt "/ship" --output pr-description.md
```

### 4. Mission Control Pattern

For complex workflows, use the Mission Control pattern:

```bash
# Define a mission
cat > mission.yaml << 'EOF'
name: feature-implementation
steps:
  - command: /plan
    input: "Add rate limiting to API endpoints"
    output: spec/rate-limiting/plan.md
  - command: /implement
    context: spec/rate-limiting/plan.md
  - command: /verify
    retries: 3
  - command: /ship
    output: pr-description.md
EOF

# Execute mission
npx continue mission run mission.yaml
```

### 5. GitHub Actions Integration

See `.github/workflows/all-green-gates.yml` for CI gates.

For headless PR creation:

```yaml
name: Continue Headless
on:
  push:
    paths:
      - 'spec/**/plan.md'

jobs:
  implement:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Continue CLI
        run: npm install -g @anthropic-ai/continue

      - name: Run implementation
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          npx continue run --prompt "/implement"
          npx continue run --prompt "/verify"

      - name: Create PR
        run: |
          npx continue run --prompt "/ship" --output pr.md
          gh pr create --body-file pr.md
```

---

## Command Reference

### /plan

Creates an implementation plan without making edits.

**Input**: Description of what to build
**Output**: Structured plan in `spec/<slug>/plan.md`

**Sections**:
- Scope
- Assumptions
- Files to Change
- Risks / Rollback
- Verification Commands
- Tasks

### /implement

Executes the plan with minimal diffs.

**Input**: Plan file or context
**Output**: Code changes matching the plan

**Rules**:
- Only edit files listed in plan
- Prefer minimal diffs
- Document any deviations

### /verify

Runs checks and fixes until green.

**Input**: None (uses plan verification commands)
**Output**: Verification report

**Rules**:
- Run each verification command
- Fix failures (up to 3 retries)
- Cannot add new features
- Only minimal fixes allowed

### /ship

Generates PR-ready package with evidence.

**Input**: Completed implementation
**Output**: PR description, commit message

**Includes**:
- Summary
- Spec reference
- Files changed
- Verification evidence
- Tasks completed

---

## CI Integration

### Gate Workflow

The `all-green-gates.yml` workflow enforces:

1. **Spec Kit Validation** - All bundles have required files
2. **Policy Check** - No secrets, no Enterprise deps
3. **Continue Config** - Valid configuration
4. **Syntax Check** - Valid JSON/YAML

### Running Gates Locally

```bash
# Run all gates
./scripts/validate-spec-kit.sh
./scripts/policy-check.sh
./scripts/validate-continue-config.sh
```

### Branch Protection

Configure branch protection to require:

- `all-green-gates / All Green` must pass
- PR reviews required
- No direct pushes to main

---

## Troubleshooting

### Common Issues

#### 1. Spec validation fails

```bash
# Check specific bundle
./scripts/validate-spec-kit.sh my-feature

# Common fixes:
# - Add missing files (constitution/prd/plan/tasks.md)
# - Add more content (≥10 lines per file)
# - Remove placeholder text (TODO, TBD)
```

#### 2. Policy check fails

```bash
# Run with diff mode
./scripts/policy-check.sh --diff

# Common violations:
# - Hardcoded secrets → use env vars
# - Enterprise imports → use OCA alternatives
# - Debug statements → remove before commit
```

#### 3. Continue config invalid

```bash
# Validate config
./scripts/validate-continue-config.sh

# Common fixes:
# - Fix JSON syntax in config.json
# - Fix YAML syntax in rules/*.yaml
# - Add missing prompts
```

#### 4. Headless authentication

```bash
# Set API key
export ANTHROPIC_API_KEY=your-key

# Or use .env file
echo "ANTHROPIC_API_KEY=your-key" >> .env

# Verify
npx continue auth status
```

### Debug Mode

Enable verbose logging:

```bash
# For scripts
DEBUG=1 ./scripts/validate-spec-kit.sh

# For Continue CLI
CONTINUE_DEBUG=1 npx continue run --prompt "/plan test"
```

### Getting Help

- Continue docs: https://docs.continue.dev
- Spec issues: Check `spec/<slug>/constitution.md` rules
- CI failures: Check GitHub Actions logs

---

## Quick Reference Card

```bash
# Validate everything
./scripts/validate-spec-kit.sh && \
./scripts/policy-check.sh && \
./scripts/validate-continue-config.sh

# Create new feature
mkdir -p spec/my-feature
# Edit constitution.md, prd.md, plan.md, tasks.md

# Run workflow
# In VS Code: /plan, /implement, /verify, /ship
# Headless: npx continue run --prompt "/plan ..."

# Pre-commit check
git add .
./scripts/validate-spec-kit.sh
./scripts/policy-check.sh --diff
git commit -m "feat(scope): description"
```

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-22 | Initial runbook |
