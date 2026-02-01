# Claude Code Web (Cloud Sandbox) Execution Contract

> **Pattern**: Claude Code Web = cloud sandbox. You don't run on a local machine; you execute **inside the web session**, set **env vars in that session**, and **verify via logs + DB queries**.

---

## Environment Assumptions

| Assumption | Details |
|------------|---------|
| **Execution Context** | Cloud/web sandbox (Claude Code Web / Codex Web) |
| **No Local Access** | Do NOT assume local machine access |
| **Primary DB** | PostgreSQL 15 (Docker container `db`, NOT Supabase) |
| **Supabase Role** | External integrations only (project: `spdtwktxdalcfigzeqrz`) |
| **Scripts** | Prefer repo-local scripts and deterministic commands |
| **Secrets** | Injected via Web session's Environment Variables UI (never committed) |

---

## Architecture Context

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Web Sandbox Execution Context                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────┐    ┌──────────────────────────────────────┐   │
│   │  Web Sandbox    │    │         Docker Compose Stack          │   │
│   │  (Claude Code)  │───►│                                       │   │
│   │                 │    │   PostgreSQL ◄── Odoo CE (8069/70/71) │   │
│   │  - Run scripts  │    │       │                               │   │
│   │  - Read/Write   │    │       └── n8n ◄── Mattermost          │   │
│   │  - Verify       │    │                                       │   │
│   └─────────────────┘    └──────────────────────────────────────┘   │
│                                     │                                │
│                                     ▼                                │
│                          ┌──────────────────┐                        │
│                          │     Supabase     │ (external only)        │
│                          │ spdtwktxdalcfigzeqrz │                    │
│                          └──────────────────┘                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Secrets / Environment Injection

### Required Variables (Set in Web Session UI)

When a variable is required, set these in the web session's Environment Variables UI:

**Database (PostgreSQL - Primary)**
```
DB_HOST=db
DB_PORT=5432
DB_USER=odoo
DB_PASSWORD=<set-in-session>
DB_NAME=odoo_core
```

**Odoo Server**
```
ADMIN_PASSWD=<set-in-session>
ODOO_PORT=8069
```

**Supabase (External Integrations Only)**
```
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
NEXT_PUBLIC_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_ANON_KEY=<set-in-session>
SUPABASE_SERVICE_ROLE_KEY=<set-in-session>
```

**Integrations (Optional)**
```
N8N_HOST=n8n
N8N_PORT=5678
MATTERMOST_URL=https://mattermost.insightpulseai.com
```

> **CRITICAL**: Never print secret values. Only print variable names.

---

## Database Operations

### Dual Database Architecture

| Database | Purpose | Location |
|----------|---------|----------|
| **PostgreSQL** | Primary Odoo/ERP data | Docker container `db` |
| **Supabase** | External integrations, n8n workflows, task bus | Cloud (spdtwktxdalcfigzeqrz) |

### PostgreSQL Schema Changes (Primary)

All Odoo-related schema changes delivered as SQL migrations in:
```
db/migrations/*.sql
```

**Naming convention:**
```
YYYYMMDDHHMM_DESCRIPTION.sql
```

**Example:**
```
202601090001_ADD_NEW_FIELD.sql
```

### Supabase Schema Changes (External)

All Supabase changes delivered as SQL migrations in:
```
supabase/migrations/*.sql
```

**Apply migrations:**
```bash
# If Supabase CLI available
supabase db push
supabase migration up

# If no CLI, provide SQL file for Supabase SQL Editor
# Or use Edge Function at supabase/functions/db-migrate/index.ts
```

### Edge Functions

Located in:
```
supabase/functions/*/index.ts
```

Deploy with:
```bash
supabase functions deploy <function-name>
```

---

## Verification Protocol

### After EVERY Mutation, Output Verification Block

```markdown
## Verification

### Database Check
```sql
-- Run this in PostgreSQL (Docker)
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name LIKE 'ipai_%';
```

### Health Endpoint
```bash
curl -s http://localhost:8069/ipai/idp/healthz | jq .
```

### Logs
```bash
docker compose logs -f odoo-core --tail=50
```
```

### Standard Verification Commands

| Check | Command |
|-------|---------|
| **Repo Structure** | `./scripts/repo_health.sh` |
| **Spec Bundles** | `./scripts/spec_validate.sh` |
| **Full CI Suite** | `./scripts/ci_local.sh` |
| **Stack Health** | `./scripts/stack_verify.sh` |
| **Enhanced Health** | `./scripts/enhanced_health_check.sh` |
| **Odoo Health** | `./scripts/healthcheck_odoo.sh` |

### Quick Verification Script

```bash
./scripts/web_sandbox_verify.sh
```

---

## Web Sandbox Checklist

### Before Starting

- [ ] Set environment variables in web session settings
- [ ] Verify Docker stack is running: `docker compose ps`
- [ ] Check database connectivity: `./scripts/db_verify.sh`

### During Development

- [ ] Use repo scripts (not local-only commands)
- [ ] Follow agent workflow: `explore → plan → implement → verify → commit`
- [ ] Run verification after each mutation
- [ ] Keep changes minimal and focused

### After Changes

- [ ] Run `./scripts/repo_health.sh`
- [ ] Run `./scripts/spec_validate.sh`
- [ ] Verify with `./scripts/web_sandbox_verify.sh`
- [ ] Check logs panel in web UI

---

## Output Format Requirements

### File Changes
Always provide:
- Full file path
- Complete file contents
- Verification commands

```markdown
**File:** `path/to/file.py`

```python
# Complete file contents here
```

**Verify:**
```bash
python3 -m py_compile path/to/file.py
```
```

### SQL Migrations
Always provide:
- Migration file path
- Complete SQL with rollback
- Verification query

```markdown
**Migration:** `db/migrations/202601090001_ADD_FIELD.sql`

```sql
-- UP
ALTER TABLE my_table ADD COLUMN new_field VARCHAR(100);

-- DOWN (for rollback reference)
-- ALTER TABLE my_table DROP COLUMN new_field;
```

**Verify:**
```sql
SELECT column_name FROM information_schema.columns
WHERE table_name = 'my_table' AND column_name = 'new_field';
```
```

### Commands
Always use fenced code blocks:
```bash
# Command with description
./scripts/some_script.sh
```

---

## Agent Workflow Integration

### Available Commands

| Command | Description |
|---------|-------------|
| `/project:plan` | Create detailed implementation plan |
| `/project:implement` | Execute plan with minimal changes |
| `/project:verify` | Run all verification checks |
| `/project:ship` | Orchestrate full workflow end-to-end |
| `/project:fix-github-issue` | Fix a specific GitHub issue |

### Workflow Pattern

```
1. explore    → Understand current state
2. plan       → Create implementation plan (use TodoWrite)
3. implement  → Execute with minimal changes
4. verify     → Run verification scripts
5. commit     → Commit with conventional message
```

### Tool Restrictions

The web sandbox enforces allowed tools per `.claude/settings.json`:

- **File ops**: Edit, Read, Write, Glob, Grep
- **Git ops**: status, diff, add, commit, push, log, branch
- **GitHub**: `gh *` commands
- **CI scripts**: repo_health.sh, spec_validate.sh, verify.sh, ci_local.sh

---

## Common Operations

### Start Docker Stack
```bash
docker compose up -d
```

### Run Odoo Tests
```bash
./scripts/ci/run_odoo_tests.sh
```

### Deploy IPAI Modules
```bash
./scripts/deploy-odoo-modules.sh
```

### Check Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f odoo-core

# Last 100 lines
docker compose logs --tail=100 odoo-core
```

### Database Access
```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U odoo -d odoo_core

# Run verification SQL
./scripts/db_verify.sh                              # Or use --sql flag for manual copy/paste
```

---

## Health Endpoints

| Service | Endpoint | Port |
|---------|----------|------|
| **Odoo Core** | `/ipai/idp/healthz` | 8069 |
| **Control Room API** | `/health` | 8789 |
| **Pulser Runner** | `/health` | 8788 |
| **MCP Coordinator** | `/health` | (varies) |

### Health Check Commands
```bash
# Odoo health
curl -s http://localhost:8069/ipai/idp/healthz

# Control Room API health
curl -s http://localhost:8789/health

# Pulser Runner health
curl -s http://localhost:8788/health
```

---

## Troubleshooting

### Module Not Found
```bash
# Check module exists in addons path
docker compose exec odoo-core ls /mnt/extra-addons/ipai/

# Update module list
docker compose exec odoo-core odoo -d odoo_core -u base
```

### Database Connection Issues
```bash
# Check PostgreSQL status
docker compose ps postgres
docker compose logs postgres

# Test connection
docker compose exec postgres pg_isready -U odoo
```

### Permission Errors
```bash
# Fix addon permissions
chmod -R 755 addons/ipai/
```

### Migration Failures
```bash
# Check migration status
docker compose exec postgres psql -U odoo -d odoo_core -c \
  "SELECT * FROM ir_module_module WHERE state = 'to upgrade';"
```

---

## Quick Reference

### Verification Sequence
```bash
./scripts/repo_health.sh && \
./scripts/spec_validate.sh && \
./scripts/ci_local.sh
```

### Commit Convention
```
feat|fix|refactor|docs|test|chore(scope): description
```

### Before Push Checklist
- [ ] All verification scripts pass
- [ ] No secrets in code
- [ ] Conventional commit message
- [ ] PR references spec bundle (if applicable)

---

## VS Code Environments vs Claude Code Capabilities

This section maps the main VS Code–style environments to the actual capabilities Claude Code can use in each one. Use this as the routing matrix when deciding where to run agentic work.

### Comparison Matrix

| Environment | Claude Surface | Execution Surface | Terminal Access | Docker Control | MCP Servers | Best For |
|-------------|----------------|-------------------|-----------------|----------------|-------------|----------|
| **VS Code Desktop + CLI** | CLI + extension | Local machine | **Full** | **Full** | **Full** | Heavy refactors, Docker orchestration, MCP debugging |
| **VS Code Web + Claude Web** | Browser panel | Browser sandbox | **None** | **None** | Indirect (HTTP only) | Light edits, docs, planning |
| **GitHub Codespaces + CLI** | CLI inside container | Remote container | **Full inside** | **Full inside** | **Full inside** | Full power, cloud hosted |
| **Remote Tunnels + CLI** | CLI + extension | Remote host | **Full on remote** | **Full on remote** | **Full on remote** | Hybrid local UX, remote compute |

### Environment Selection Guidelines

| Need | Recommended Environment |
|------|------------------------|
| Full agentic power (Docker, MCP, DevContainers) | VS Code Desktop + CLI inside DevContainer |
| Cloud-hosted full power | GitHub Codespaces + Claude Code |
| Quick edits from browser-only device | VS Code Web + Claude Code Web |
| Persistent cloud server with local UX | Remote Tunnels + Claude Code |

### Recommended Default for Agentic ERP/Analytics Work

For the Odoo + Supabase + Superset + Next.js stack:

1. **Primary**: VS Code Desktop + DevContainer + Claude Code CLI
   - Maximum control over Docker, MCP servers, local "data center in a box"
   - Host OS protected by container boundary

2. **Cloud variant**: GitHub Codespaces with same `.devcontainer/devcontainer.json`
   - Mirrors local DevContainer model
   - Offloads CPU/RAM to GitHub infra

3. **Browser-only fallback**: VS Code Web + Claude Code Web
   - Documentation, reviews, small patches, planning only
   - Route stack-level operations to DevContainer/Codespace

### Key Limitations by Environment

| Environment | Cannot Do |
|-------------|-----------|
| **VS Code Web** | No terminal, no Docker, no local shell, MCP only if proxied via HTTPS |
| **Codespaces** | Needs quota, Docker-in-Docker must be enabled, network egress policies apply |
| **Remote Tunnels** | Requires tunnel daemon running, security hardening on remote host |

> **See also**: [docs/architecture/AGENTIC_AI_ERP_ANALYTICS.md](./docs/architecture/AGENTIC_AI_ERP_ANALYTICS.md) for the full architectural convergence document.

---

*For full project documentation, see [CLAUDE.md](./CLAUDE.md)*
*For external memory queries, use: `python .claude/query_memory.py <category>`*
