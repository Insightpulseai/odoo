# Command Reference

Complete list of natural language commands → runbook mappings.

## 🚀 Deploy Commands

| Command | Runbook | Environment | Tools |
|---------|---------|-------------|-------|
| `deploy prod` | Deploy to production | prod | GitHub, Vercel, Supabase |
| `deploy staging` | Deploy to staging | staging | GitHub, Vercel, Supabase |
| `deploy dev` | Deploy to dev | dev | GitHub, Vercel, Supabase |
| `deploy api prod` | Deploy API service | prod | GitHub, Vercel, Supabase |
| `deploy web staging` | Deploy web app | staging | GitHub, Vercel |

**Inputs:**
- Environment (prod/staging/dev)
- Repo (default: jgtolentino/odoo-ce)
- Target (vercel/full-stack/api-service)
- Branch (default: main)
- Run migrations (boolean, default: true)

**Risks:**
- ⚠️ Production deployment (if env=prod)
- ⚠️ Database migrations
- ℹ️ Potential downtime

**Example Output:**
```
[INFO] Starting deploy execution...
[INFO] Vercel: Building application...
[SUCCESS] Vercel: ✓ Build completed (3.2s)
[INFO] Supabase: Running database migrations...
[SUCCESS] Supabase: ✓ Migrations applied (2 new migrations)
[SUCCESS] Vercel: ✓ Deployment successful
  → url: https://app-xyz123.vercel.app
```

---

## 🔍 Health Check Commands

| Command | Runbook | Environment | Tools |
|---------|---------|-------------|-------|
| `check prod status` | Health check | prod | Supabase, Vercel, DigitalOcean |
| `check staging` | Health check | staging | Supabase, Vercel, DigitalOcean |
| `health check prod` | Health check | prod | Supabase, Vercel, DigitalOcean |
| `status prod` | Health check | prod | Supabase, Vercel, DigitalOcean |

**Inputs:**
- Environment (prod/staging/dev)

**Risks:**
- ℹ️ Read-only operation (safe to re-run)

**Example Output:**
```
[INFO] Running health checks...
[SUCCESS] Vercel: ✓ API Gateway: healthy (45ms)
[SUCCESS] Supabase: ✓ Database: healthy (12ms)
[WARN] Supabase: ⚠ Storage: degraded (210ms)
[SUCCESS] DigitalOcean: ✓ Compute: healthy (35ms)
[WARN] Storage service showing elevated latency. Recommend investigation.
```

---

## 📝 Spec Generation Commands

| Command | Runbook | Output | Tools |
|---------|---------|--------|-------|
| `generate spec` | Generate spec kit | 4 markdown files + PR | GitHub |
| `generate spec for dashboard` | Generate spec kit | 4 markdown files + PR | GitHub |
| `create prd for auth` | Generate spec kit | 4 markdown files + PR | GitHub |
| `spec for user settings` | Generate spec kit | 4 markdown files + PR | GitHub |

**Inputs:**
- Repo (default: jgtolentino/odoo-ce)
- Target (default: spec/ops-control-room)
- Notes (optional description)

**Risks:**
- ℹ️ Will create new spec files
- ℹ️ May update existing documentation

**Files Generated:**
1. `constitution.md` — Project principles & constraints
2. `prd.md` — Product requirements document
3. `plan.md` — Implementation plan
4. `tasks.md` — Breakdown of tasks

**Example Output:**
```
[INFO] Analyzing requirements...
[SUCCESS] ✓ Generated spec/constitution.md
[SUCCESS] ✓ Generated spec/prd.md
[SUCCESS] ✓ Generated spec/plan.md
[SUCCESS] ✓ Generated spec/tasks.md
[INFO] GitHub: Creating pull request...
[SUCCESS] GitHub: ✓ PR created: #847 'Add spec for User Dashboard'
  → pr_url: https://github.com/org/repo/pull/847
  → branch: spec/user-dashboard
```

---

## 🚨 Incident Triage Commands

| Command | Runbook | Output | Tools |
|---------|---------|--------|-------|
| `fix production error` | Incident triage | Root cause + PR with fix | Vercel, GitHub, Supabase |
| `fix prod error` | Incident triage | Root cause + PR with fix | Vercel, GitHub, Supabase |
| `incident prod` | Incident triage | Root cause + PR with fix | Vercel, GitHub, Supabase |
| `error in production` | Incident triage | Root cause + PR with fix | Vercel, GitHub, Supabase |

**Inputs:**
- Environment (prod/staging/dev)
- Notes (paste error snippet or link)

**Risks:**
- ⚠️ Production incident (if env=prod)
- ℹ️ Will create PR with proposed fix

**Example Output:**
```
[INFO] Analyzing error logs...
[WARN] Vercel: Found 127 occurrences in the last hour
[INFO] Root cause identified: Database connection pool exhaustion
[INFO] Generating fix proposal...
[SUCCESS] ✓ Fix proposal ready:
  → Increase connection pool size
  → Add connection retry logic
[SUCCESS] GitHub: ✓ PR created: #848 'Fix: Increase DB connection pool size'
  → pr_url: https://github.com/org/repo/pull/848
```

---

## 🗄️ Schema Sync Commands

| Command | Runbook | Output | Tools |
|---------|---------|--------|-------|
| `run schema sync` | Database schema sync | ERD + migrations | Supabase, GitHub |
| `schema sync prod` | Database schema sync | ERD + migrations | Supabase, GitHub |
| `sync database schema` | Database schema sync | ERD + migrations | Supabase, GitHub |
| `generate erd` | Database schema sync | ERD + migrations | Supabase, GitHub |

**Inputs:**
- Environment (prod/staging/dev)
- Target (default: schema/exports)

**Risks:**
- 🚫 Schema changes can be destructive
- ⚠️ Always dry run first
- ⚠️ Verify migrations before applying

**Example Output:**
```
[INFO] Supabase: Comparing schemas...
[INFO] Supabase: Found 3 differences:
  → 2 new tables
  → 1 modified column
[SUCCESS] ✓ Generated ERD diagram (DBML format)
[SUCCESS] ✓ Migration files generated (dry-run mode)
[WARN] Review migrations before applying to production
```

---

## 🎯 Command Patterns

### Environment Detection
- `prod` → production
- `staging` / `stag` → staging
- Default → production (if not specified)

### Service Detection
- `api` → api-service
- `web` → web-app
- Default → full-stack

### Action Detection
- `deploy` → deploy runbook
- `check` / `status` / `health` → healthcheck runbook
- `spec` / `prd` / `generate` → spec runbook
- `fix` / `error` / `incident` → incident runbook
- `schema` / `sync` / `migration` → schema_sync runbook

---

## 🔧 Advanced Usage

### Chaining Commands (Future)
```
User: Deploy staging, then run health check
→ Creates 2 runbooks in sequence
```

### Conditional Execution (Future)
```
User: Deploy prod only if staging is healthy
→ Adds conditional check before deployment
```

### Scheduled Runbooks (Future)
```
User: Check prod status every hour
→ Creates cron job for health checks
```

### Rollback (Future)
```
User: Rollback last deployment
→ Reverts to previous deployment
```

---

## 📚 Integration-Specific Commands

### Vercel
- `deploy to vercel`
- `check vercel status`
- `get vercel logs`

### Supabase
- `run supabase migrations`
- `check supabase health`
- `introspect database`

### GitHub
- `create pr for X`
- `trigger workflow Y`
- `check actions status`

### DigitalOcean
- `check droplet status`
- `restart droplet`
- `scale droplet`

---

## 💡 Tips

1. **Be specific with environment:**
   - ✅ `deploy prod`
   - ❌ `deploy` (defaults to prod, which is risky)

2. **Include context in error fixes:**
   - ✅ `fix prod error: HTTP 500 on /api/users`
   - ❌ `fix error`

3. **Name your specs clearly:**
   - ✅ `generate spec for user dashboard`
   - ❌ `generate spec`

4. **Always review before running:**
   - Check inputs
   - Read risk flags
   - Verify target environment

5. **Use Edit to customize:**
   - Click "Edit" to modify inputs
   - Especially for production runbooks

---

**Try it now:** Type any command from this list in the demo! 🚀
