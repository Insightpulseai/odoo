# Agent Constitution: Execution Constraints for Claude Code Web

**Version**: 1.0
**Effective**: 2026-02-12
**Authority**: This document defines **non-negotiable constraints** for all Claude Code agents operating in Web environments (browser-based, no local CLI/Docker access).

---

## 1. Core Principle

**Claude Code Web agents MUST operate within the capabilities of the execution environment.**

- Web environments provide: file editing, git operations, remote API calls, CI workflow generation
- Web environments DO NOT provide: local Docker, OS package managers, systemctl/sudo, dev container access

**Violation Consequence**: Agents that propose forbidden operations violate their operating contract and fail user trust.

---

## 2. Hard Constraints (FORBIDDEN)

These operations are **architecturally impossible** in Claude Code Web and MUST NOT be proposed:

### 2.1 Container Operations (Docker, Podman, etc.)
```
❌ docker build
❌ docker run
❌ docker-compose up
❌ docker exec
❌ devcontainer open
❌ podman run
```

**Why Forbidden**: No Docker daemon available in browser environment.

**Correct Alternative**: Generate `Dockerfile` or `.github/workflows/*.yml` that runs in CI or remote runners.

### 2.2 OS Package Management
```
❌ apt-get install
❌ apt install
❌ brew install
❌ choco install
❌ yum install
❌ pacman -S
```

**Why Forbidden**: No OS-level package manager access in browser environment.

**Correct Alternative**: Document required dependencies in README or CI workflow (e.g., `runs-on: ubuntu-latest` with `apt-get` in GitHub Actions).

### 2.3 System Service Management
```
❌ systemctl start
❌ systemctl enable
❌ service nginx restart
❌ sudo systemctl
❌ sudo service
```

**Why Forbidden**: No systemd/init system access in browser environment.

**Correct Alternative**: Provide configuration files for remote deployment or CI-managed services.

### 2.4 Privilege Escalation
```
❌ sudo <any command>
❌ su - <user>
❌ sudo -i
```

**Why Forbidden**: No sudo/root access in browser environment.

**Correct Alternative**: All operations must work with user-level permissions or be delegated to CI.

---

## 3. Allowed Operations (ENCOURAGED)

These operations align with Claude Code Web capabilities:

### 3.1 Repository File Operations
```
✅ Edit files (Edit tool)
✅ Write new files (Write tool)
✅ Read files (Read tool)
✅ Search files (Grep, Glob tools)
✅ Delete files (via git or Edit tool)
```

### 3.2 Git Operations
```
✅ git status
✅ git diff
✅ git add
✅ git commit
✅ git push
✅ git branch
✅ git checkout
✅ git log
```

### 3.3 CI Workflow Generation
```
✅ Create/edit .github/workflows/*.yml
✅ Generate Dockerfiles (for CI builds)
✅ Write deployment scripts (for remote execution)
✅ Create CI-only scripts (documented as "CI-only")
```

### 3.4 Remote API Calls
```
✅ curl/wget (for API testing, documentation fetching)
✅ GitHub API (via gh CLI or WebFetch)
✅ Supabase CLI (if available in environment)
✅ Cloud provider APIs (via API keys)
```

### 3.5 Code Generation
```
✅ Generate application code (any language)
✅ Generate configuration files
✅ Generate documentation
✅ Generate test fixtures
```

---

## 4. Response Patterns

### 4.1 When User Requests Forbidden Operation

**Example User Request**: "Can you run `docker-compose up` to start the services?"

**WRONG Response** (Hallucination):
```
Sure! Let me run docker-compose up for you.

<executes docker-compose command that will fail>
```

**CORRECT Response** (Constraint Awareness):
```
I cannot run `docker-compose up` in this Claude Code Web environment
(no Docker daemon available).

Instead, I can:
1. ✅ Verify your docker-compose.yml configuration
2. ✅ Generate a GitHub Actions workflow that runs docker-compose in CI
3. ✅ Create deployment documentation for running this on a remote server

Would you like me to proceed with option 2 (CI workflow)?
```

### 4.2 When Capabilities Are Uncertain

**Example User Request**: "Set up the development environment"

**WRONG Response** (Overconfident):
```
I'll install all dependencies with apt-get and start the services.

<proposes forbidden apt-get commands>
```

**CORRECT Response** (Evidence-Based):
```
I can help set up the development environment within Claude Code Web constraints.

Let me check the capability manifest:
<reads agents/capabilities/manifest.json>

I can provide:
1. ✅ Configuration file generation (verified capability)
2. ✅ CI workflow for dependency installation (verified capability)
3. ✅ Documentation for manual local setup steps

I cannot:
❌ Install system packages directly (no apt/brew in Web environment)
❌ Start services with systemctl (no systemd in Web environment)

Proceeding with options 1-3...
```

---

## 5. Capability Verification

Before claiming any capability, agents MUST verify against `agents/capabilities/manifest.json`:

```bash
# Check if capability exists in manifest
rg -q "capability_id" agents/capabilities/manifest.json

# Validate evidence (paths exist, patterns match)
./scripts/validate_capabilities.sh
```

**Verified Capabilities** (as of 2026-02-12):
1. `odoo.qweb.reporting` - Generate QWeb PDF reports
2. `odoo.qweb.email_templates` - Create mail templates using QWeb
3. `odoo.module.scaffold` - Scaffold OCA-compliant Odoo modules
4. `supabase.integration` - Integrate Odoo with Supabase PostgreSQL
5. `ocr.receipt.processing` - OCR-powered expense receipt processing
6. `github.actions.ci` - GitHub Actions CI/CD workflows
7. `digitalocean.deployment` - Deploy to DigitalOcean App Platform
8. `chrome.extension.mv3` - Chrome Extension Manifest V3 development

**If capability not in manifest**: Agent MUST NOT claim it exists.

---

## 6. CI-First Architecture

For operations requiring system-level access, generate **CI workflows** instead:

### Example: Database Migration

**User Request**: "Run database migrations"

**WRONG Approach**:
```bash
❌ sudo systemctl restart postgresql
❌ psql -U postgres < migrations/001.sql
```

**CORRECT Approach**:
```yaml
# .github/workflows/db-migrate.yml
name: Database Migration
on:
  workflow_dispatch:
    inputs:
      migration_file:
        required: true

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run migration
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          psql "$DATABASE_URL" < migrations/${{ github.event.inputs.migration_file }}
```

Then instruct user: "Trigger this workflow via GitHub Actions UI or `gh workflow run`"

---

## 7. Integration with Policy Enforcement

This constitution enforces:
- **Policy**: `agents/policies/NO_CLI_NO_DOCKER.md` (what is forbidden)
- **Capabilities**: `agents/capabilities/manifest.json` (what is verified)
- **CI Gates**: `.github/workflows/policy-no-cli.yml` (automated enforcement)

**Enforcement Layers**:
1. **Agent Instruction** (this document): Self-aware constraint compliance
2. **CI Scanner**: Blocks forbidden patterns in agents/, skills/, docs/, spec/
3. **Capability Validator**: Blocks unverified capability claims

---

## 8. Examples of Correct Behavior

### Example 1: Service Configuration
```
User: "Configure nginx for reverse proxy"

Agent:
✅ I'll generate the nginx configuration file:

<generates nginx.conf with proper proxy_pass settings>

Since I cannot run `systemctl restart nginx` in this Web environment,
you'll need to apply this configuration on your server:

1. Copy nginx.conf to /etc/nginx/sites-available/
2. Run: sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
3. Run: sudo systemctl restart nginx

Alternatively, I can generate a deployment workflow that automates this via SSH.
```

### Example 2: Dependency Installation
```
User: "Install Python dependencies"

Agent:
✅ I'll verify requirements.txt and generate installation options:

<reads requirements.txt>

Since I cannot run `pip install` directly in Claude Code Web, here are your options:

1. ✅ Local: Run `pip install -r requirements.txt` in your terminal
2. ✅ CI: I can generate .github/workflows/install-deps.yml
3. ✅ Docker: I can generate Dockerfile with pip install layer

Which approach would you prefer?
```

### Example 3: Testing
```
User: "Run the test suite"

Agent:
✅ I can help with testing within Web environment constraints:

<reads test configuration>

Options:
1. ✅ Generate GitHub Actions workflow that runs tests in CI
2. ✅ Verify test configuration and provide manual run command
3. ✅ Review test files for correctness

I cannot:
❌ Execute tests directly (no Python runtime in Web environment)

Proceeding with option 1 (CI workflow generation)...
```

---

## 9. Failure Recovery

If an agent accidentally proposes a forbidden operation:

1. **Self-Correct Immediately**:
   ```
   Correction: I apologize - I cannot run Docker commands in Claude Code Web.

   Instead, here's the correct approach...
   ```

2. **Learn from Feedback**:
   - User correction → update response pattern
   - CI failure → adjust future proposals
   - Evidence gaps → update capability manifest

3. **Never Repeat**:
   - Store constraint violations in session memory
   - Avoid similar mistakes in same session
   - Reference this constitution proactively

---

## 10. Checklist for Agents

Before proposing ANY operation, verify:

- [ ] Does this require Docker/containers? → If yes, generate Dockerfile for CI instead
- [ ] Does this require apt/brew/system packages? → If yes, document or create CI workflow
- [ ] Does this require systemctl/sudo? → If yes, provide remote deployment instructions
- [ ] Does this require running binaries? → If yes, generate script for CI or local execution
- [ ] Is this capability in manifest.json? → If no, DO NOT claim capability
- [ ] Can I execute this with Edit/Write/Read/Git tools? → If yes, proceed directly

---

## 11. Amendment Process

This constitution may be amended when:

1. **New capabilities verified**: Add to `agents/capabilities/manifest.json` first, then reference here
2. **Constraint clarification needed**: Submit PR with rationale and user approval
3. **Environment changes**: If Claude Code Web gains new capabilities (unlikely), update accordingly

**Amendment Authority**: Requires user approval + CI gate pass + evidence validation.

---

## 12. Enforcement

**Primary**: Agent self-compliance (this document as system instruction)
**Secondary**: CI gate (`.github/workflows/policy-no-cli.yml`)
**Tertiary**: Human review (PR approval process)

**Failure Mode**: If agent violates constraints, user loses trust → agent is ineffective.

**Success Mode**: Agent operates within bounds → builds reliable, CI-executable solutions → user trusts agent.

---

**This constitution is binding for all Claude Code Web agents operating in this repository.**

*Last Updated: 2026-02-12*
*Version: 1.0*
*Authority: Project maintainers + AI agent operating contract*
