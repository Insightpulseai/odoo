# Supabase Environment Management

> **Quick Reference** for Supabase deployment and branching in this repository.
> See [Supabase Docs: Deployment & Branching](https://supabase.com/docs/guides/deployment) for official documentation.

---

## Environment Strategy

| Environment | Purpose | Implementation |
|-------------|---------|----------------|
| **Development** | Local development | `supabase start` (CLI) |
| **Staging/Preview** | Test migrations, PRs | [Supabase Branching](https://supabase.com/docs/guides/deployment/branching) |
| **Production** | Live users | Project `spdtwktxdalcfigzeqrz` |

---

## Quick Start

### Local Development

```bash
# Start local Supabase stack
supabase start

# Create new migration
supabase migration new <name>

# Apply migrations locally
supabase db reset
```

### Preview Branches

Push to `feature/*`, `claude/*`, or `fix/*` branches:

```bash
git checkout -b feature/my-change
# Make changes to supabase/migrations/ or supabase/functions/
git push -u origin feature/my-change
```

Supabase automatically creates an isolated preview environment. See PR comments for preview URLs.

### Production Deployment

Merge to `main` branch triggers automatic deployment:

1. Migrations applied to production database
2. Edge Functions deployed
3. Health verification executed

---

## Deployment Options

This repo supports three deployment methods (per [Supabase docs](https://supabase.com/docs/guides/deployment)):

| Method | When to Use | Workflow |
|--------|-------------|----------|
| **GitHub Integration** | Default (recommended) | `.github/workflows/supabase-branching.yml` |
| **Supabase CLI** | Manual deploys | `supabase db push` |
| **Terraform** | Infrastructure-as-code | See [Terraform Integration Guide](./SUPABASE_TERRAFORM_INTEGRATION.md) |

---

## Branch Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  1. Create Branch                                           │
│     git checkout -b feature/add-new-api                     │
│                                                             │
│  2. Supabase Creates Preview                                │
│     → Isolated database instance                            │
│     → Migrations applied from supabase/migrations/          │
│     → Seed data from supabase/seed.sql                      │
│                                                             │
│  3. Test Changes                                            │
│     → Preview URL in PR comment                             │
│     → Test migrations, Edge Functions, RLS policies         │
│                                                             │
│  4. Merge to Main                                           │
│     → Changes deploy to production automatically            │
│     → Preview branch deleted                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Configuration

### Required Secrets

| Secret | Description |
|--------|-------------|
| `SUPABASE_ACCESS_TOKEN` | CLI authentication |
| `SUPABASE_PROJECT_REF` | `spdtwktxdalcfigzeqrz` |
| `SUPABASE_URL` | `https://spdtwktxdalcfigzeqrz.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key for writes |

### Branching Config

From `supabase/config.toml`:

```toml
[branching]
enabled = true

[db.seed]
enabled = true
sql_paths = ["./seed.sql"]
```

---

## Key Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `supabase-branching.yml` | PR events, feature branches | Create/manage preview branches |
| `supabase-deploy.yml` | Push to main | Production deployment |
| `supabase-sql-rls-checks.yml` | PR changes | Validate RLS policies |

---

## Pricing

- Preview branches: ~$0.01344/hour (~$10/month if always running)
- Auto-pause after 7 days inactivity
- Usage counts toward subscription quota

---

## Related Documentation

**In this repo:**
- [Supabase Integration Architecture](../supabase-integration.md)
- [Branching Integration Details](./SUPABASE_BRANCHING_INTEGRATION.md)

**Official Supabase Docs:**
- [Deployment Overview](https://supabase.com/docs/guides/deployment)
- [Branching Guide](https://supabase.com/docs/guides/deployment/branching)
- [Branching via GitHub](https://supabase.com/docs/guides/deployment/branching/github)
- [Database Migrations](https://supabase.com/docs/guides/deployment/database-migrations)
- [Managing Environments](https://supabase.com/docs/guides/deployment/managing-environments)
- [Terraform Provider](https://supabase.com/docs/guides/deployment/terraform)
- [Terraform Tutorial](https://supabase.com/docs/guides/deployment/terraform/tutorial)
- [Terraform Reference](https://supabase.com/docs/guides/deployment/terraform/reference)

---

*Last updated: 2026-01-24*
