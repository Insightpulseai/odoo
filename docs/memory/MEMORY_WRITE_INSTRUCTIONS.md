# MEMORY_WRITE_INSTRUCTIONS.md

Instructions for persisting the canonical context and memory distillation to long-term storage.

---

## Variant A: Memory Tool API (if available)

If your environment supports a memory tool API call, use the following payload:

```json
{
  "operation": "upsert",
  "namespace": "projects",
  "key": "jgtolentino/odoo-ce",
  "value": {
    "project": {
      "name": "odoo-ce",
      "repo_url": "https://github.com/jgtolentino/odoo-ce",
      "wiki_url": "https://github.com/jgtolentino/odoo-ce/wiki",
      "owner": "jgtolentino",
      "production_url": "https://erp.insightpulseai.com"
    },
    "purpose": "Self-hosted Odoo 18 Community Edition + OCA stack with InsightPulse AI (IPAI) custom modules for PH expense/travel, equipment booking, finance month-end close, and BIR tax compliance.",
    "stack": {
      "runtime": ["Odoo 18 CE", "Python 3.10+", "Node.js >= 18.0.0"],
      "datastores": ["PostgreSQL 16 (primary ERP)", "Supabase (external integrations only)"],
      "infra": ["Docker", "DigitalOcean Droplet", "Nginx (reverse proxy)", "GHCR (container registry)"]
    },
    "conventions": {
      "docs": ["CLAUDE.md for agent instructions", "spec/ bundles with 4-file structure", "docs/data-model/ for DBML/ERD/ORM artifacts"],
      "commands": ["docker compose -f deploy/docker-compose.prod.yml up -d", "docker compose exec -T odoo odoo -d DB -i MODULE --stop-after-init", "./scripts/repo_health.sh", "./scripts/ci_local.sh"],
      "ci_gates": ["ci-odoo-ce.yml", "all-green-gates.yml", "spec-kit-enforce.yml", "repo-structure.yml"]
    },
    "constraints": ["CE + OCA only", "No odoo.com upsells", "Self-hosted via Docker", "Deterministic docs + seeds with drift gates"]
  },
  "metadata": {
    "captured_at": "2026-01-21",
    "source_commit": "76c23e3b822fbe5e9ed9854ba8107f24af2bca11"
  }
}
```

---

## Variant B: SQL Upsert (Supabase/PostgreSQL)

If using a SQL-based memory store, execute the following upsert:

```sql
-- Assumes a `project_memory` table exists with: id (text PK), data (jsonb), updated_at (timestamptz)
INSERT INTO project_memory (id, data, updated_at)
VALUES (
  'jgtolentino/odoo-ce',
  '{
    "project": {
      "name": "odoo-ce",
      "repo_url": "https://github.com/jgtolentino/odoo-ce",
      "wiki_url": "https://github.com/jgtolentino/odoo-ce/wiki",
      "owner": "jgtolentino",
      "production_url": "https://erp.insightpulseai.com"
    },
    "purpose": "Self-hosted Odoo 18 Community Edition + OCA stack with InsightPulse AI (IPAI) custom modules for PH expense/travel, equipment booking, finance month-end close, and BIR tax compliance.",
    "stack": {
      "runtime": ["Odoo 18 CE", "Python 3.10+", "Node.js >= 18.0.0"],
      "datastores": ["PostgreSQL 16 (primary ERP)", "Supabase (external integrations only)"],
      "infra": ["Docker", "DigitalOcean Droplet", "Nginx (reverse proxy)", "GHCR (container registry)"]
    },
    "constraints": ["CE + OCA only", "No odoo.com upsells", "Self-hosted via Docker", "Deterministic docs + seeds with drift gates"]
  }'::jsonb,
  NOW()
)
ON CONFLICT (id) DO UPDATE SET
  data = EXCLUDED.data,
  updated_at = NOW();
```

---

## Variant C: Git-Based Memory Store

For deterministic, version-controlled memory storage:

### Step 1: Copy files to memory repository

```bash
set -euo pipefail

# Set your memory repo path
MEM_REPO_DIR="${MEM_REPO_DIR:-/path/to/memory-repo}"
SLUG="odoo-ce"

# Create target directory
mkdir -p "$MEM_REPO_DIR/spec/$SLUG/"

# Copy memory bundle files
cp docs/memory/CANONICAL_CONTEXT.md "$MEM_REPO_DIR/spec/$SLUG/canonical_context.md"
cp docs/memory/MEMORY_DISTILLATION.json "$MEM_REPO_DIR/spec/$SLUG/memory_distillation.json"
cp docs/memory/MEMORY_WRITE_INSTRUCTIONS.md "$MEM_REPO_DIR/spec/$SLUG/memory_write_instructions.md"
```

### Step 2: Commit and push

```bash
cd "$MEM_REPO_DIR"
git add "spec/$SLUG/"
git commit -m "memory: capture canonical context for $SLUG (2026-01-21)"
git push origin main
```

### Step 3: Rollback (if needed)

```bash
cd "$MEM_REPO_DIR"
git revert HEAD
git push origin main
```

---

## File Inventory

After storage, verify these files exist:

| File | Purpose |
|------|---------|
| `CANONICAL_CONTEXT.md` | Full structured project context |
| `MEMORY_DISTILLATION.json` | Durable facts only (machine-readable) |
| `MEMORY_WRITE_INSTRUCTIONS.md` | This file - storage instructions |

---

## Refresh Cadence

Re-run the context capture when:

1. Major version changes (e.g., Odoo 18 → 19)
2. Significant architecture changes (new canonical modules)
3. Stack changes (new datastores, infra providers)
4. Quarterly review (recommended)

**Do NOT refresh for**:
- Minor commits
- Feature additions that don't change architecture
- Bug fixes
- Documentation updates
