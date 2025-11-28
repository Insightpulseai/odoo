# CLAUDE.md — Odoo CE Project

## Quick Reference

**Stack**: Odoo CE 18.0 (OCA) + n8n + Mattermost + PostgreSQL 15

**Supabase Project**: `spdtwktxdalcfigzeqrz` (external integrations only)

**Common Commands**:
```bash
docker compose up -d              # Start stack
./scripts/deploy-odoo-modules.sh  # Deploy module
./scripts/ci/run_odoo_tests.sh    # Run tests
```

## External Memory (Just-in-Time Retrieval)

Detailed config stored in SQLite for reduced context usage:

```bash
python .claude/query_memory.py config       # Supabase/DB config
python .claude/query_memory.py arch         # Architecture components
python .claude/query_memory.py commands     # All commands
python .claude/query_memory.py rules        # Project rules
python .claude/query_memory.py deprecated   # Deprecated items
python .claude/query_memory.py all          # Everything
```

## Critical Rules

1. **Secrets**: Use `.env` files, never hardcode (see `.env.example`)
2. **Database**: Odoo uses local PostgreSQL (`db`), NOT Supabase
3. **Supabase**: Only for n8n workflows, task bus, external integrations
4. **Deprecated**: Never use `xkxyvboeubffxxbebsll` or `ublqmilcjtpnflofprkr`

## Architecture

```
Mattermost <-> n8n <-> Odoo <-> PostgreSQL (local)
                |
                v
            Supabase (external integrations)
```

---
*Query `.claude/project_memory.db` for detailed configuration*
