# Error Recovery Playbooks (Claude)

## Git Errors

### Push Rejected (403)
```bash
# Verify branch name matches session
git branch --show-current  # Should be claude/<feature>-<session_id>

# Force push only if explicitly authorized
git push -u origin $(git branch --show-current)
```

### Merge Conflict
```bash
# Fetch latest and rebase
git fetch origin main
git rebase origin/main

# If conflicts, resolve and continue
git add .
git rebase --continue
```

## CI Failures

### Pre-commit Hook Failed
```bash
# Run formatting
black addons/ipai/
isort addons/ipai/

# Verify
./scripts/ci_local.sh

# Create NEW commit (don't amend if hook modified files)
git add . && git commit -m "fix: address pre-commit issues"
```

### Odoo Tests Failed
```bash
# Run specific test
./scripts/ci/run_odoo_tests.sh <module_name>

# Check logs
docker compose logs odoo-core --tail 100

# Fix and re-run
```

## Database Errors

### Migration Failed
```sql
-- Check migration status
SELECT * FROM supabase_migrations.schema_migrations ORDER BY version DESC LIMIT 5;

-- Rollback if needed (manual)
-- Then fix migration and re-apply
supabase db push
```

### RLS Policy Denied
```sql
-- Check current role
SELECT current_user, current_setting('role');

-- Use service role for admin operations
-- Or adjust RLS policy if incorrect
```

## Webhook Errors

### Signature Verification Failed
```bash
# Check webhook secret matches
echo $GITHUB_WEBHOOK_SECRET | sha256sum

# Verify payload format (raw body required)
# Check Edge Function logs
supabase functions logs marketplace-webhook
```

### Sync Stuck in Processing
```sql
-- Find stuck syncs
SELECT * FROM marketplace.artifact_syncs
WHERE status = 'syncing'
AND created_at < NOW() - INTERVAL '10 minutes';

-- Reset to pending for retry
UPDATE marketplace.artifact_syncs
SET status = 'pending'
WHERE status = 'syncing'
AND created_at < NOW() - INTERVAL '10 minutes';
```

## Recovery Checklist

1. Identify error type (git, CI, DB, webhook)
2. Check logs for root cause
3. Apply appropriate fix
4. Verify fix worked
5. Document if recurring issue
