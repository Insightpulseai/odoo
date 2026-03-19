# OdooOps Runner — Supabase Edge Function

Serverless worker that executes build/deploy runs for the OdooOps Console platform.

## Architecture

**Event Loop Pattern:**
```
Queue → Claim → Execute → Report → Finish
```

**Execution Phases:**
1. **Build Image** - Create GHCR container from git SHA
2. **Deploy Runtime** - Deploy container to target environment
3. **Smoke Tests** - Health checks and basic validation
4. **Capture Artifacts** - Store build logs, images, evidence

## Deployment

### Manual Deploy
```bash
# Deploy Edge Function
supabase functions deploy ops-runner

# Set secrets
supabase secrets set WORKER_ID=runner-01
```

### Automated Deploy (GitHub Actions)
```yaml
# .github/workflows/deploy-runner.yml
- name: Deploy ops-runner
  run: supabase functions deploy ops-runner
  env:
    SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
```

## Usage

### Invoke Manually
```bash
# Trigger runner (claims next queued run)
curl -X POST \
  https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/ops-runner \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY"
```

### Scheduled Invocation (Cron)
```sql
-- Create scheduled job (runs every minute)
SELECT cron.schedule(
  'ops-runner-scheduler',
  '* * * * *',
  $$
    SELECT net.http_post(
      url := 'https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/ops-runner',
      headers := '{"Authorization": "Bearer ' || current_setting('app.supabase_anon_key') || '"}'::jsonb
    );
  $$
);
```

### Event-Driven (Database Trigger)
```sql
-- Trigger runner when run status changes to 'queued'
CREATE OR REPLACE FUNCTION ops.trigger_runner()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status = 'queued' THEN
    PERFORM net.http_post(
      url := 'https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/ops-runner',
      headers := '{"Authorization": "Bearer ' || current_setting('app.supabase_anon_key') || '"}'::jsonb
    );
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER runs_trigger_runner
  AFTER INSERT OR UPDATE ON ops.runs
  FOR EACH ROW
  EXECUTE FUNCTION ops.trigger_runner();
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Service role key for RPC calls |
| `WORKER_ID` | No | Worker identifier (auto-generated if not set) |

## Workflow

1. **Claim Run:**
   ```typescript
   const { data: run } = await supabase.rpc('claim_next_run', {
     p_worker_id: workerId
   })
   ```

2. **Execute Phases:**
   ```typescript
   for (const phase of phases) {
     await appendEvent(supabase, run.run_id, 'info', `Starting ${phase.name}`)
     await phase.execute(runContext)
     await appendEvent(supabase, run.run_id, 'info', `Completed ${phase.name}`)
   }
   ```

3. **Finish Run:**
   ```typescript
   await supabase.rpc('finish_run', {
     p_run_id: run.run_id,
     p_status: success ? 'success' : 'failed',
     p_metadata: { worker_id, completed_at, phases_completed }
   })
   ```

## Monitoring

### View Runner Logs
```bash
# Real-time logs
supabase functions logs ops-runner --follow

# Recent logs
supabase functions logs ops-runner --tail 100
```

### View Run Events
```sql
-- View events for specific run
SELECT created_at, level, message, payload
FROM ops.run_events
WHERE run_id = 'run-abc123'
ORDER BY created_at DESC;

-- View recent runs
SELECT run_id, status, started_at, finished_at
FROM ops.runs
ORDER BY queued_at DESC
LIMIT 10;
```

## Error Handling

**Phase Failures:**
- Errors captured in `run_events` with `level='error'`
- Run marked as `failed` status
- Subsequent phases skipped
- No automatic retry (manual re-queue via `ops.queue_run()`)

**Runner Failures:**
- Run remains in `claimed` status
- Manual intervention required to reset status
- Consider implementing timeout cleanup:
  ```sql
  -- Reset stuck runs (>30 min in 'claimed')
  UPDATE ops.runs
  SET status = 'queued', claimed_by = NULL
  WHERE status = 'claimed'
    AND started_at < NOW() - INTERVAL '30 minutes';
  ```

## Testing

### Local Testing
```bash
# Install Supabase CLI
brew install supabase/tap/supabase

# Start local Supabase
supabase start

# Serve function locally
supabase functions serve ops-runner

# Invoke locally
curl -X POST http://localhost:54321/functions/v1/ops-runner \
  -H "Authorization: Bearer eyJhbGc..."
```

### Integration Testing
```sql
-- Queue test run
SELECT ops.queue_run(
  p_project_id := 'test-project',
  p_env := 'dev',
  p_git_sha := 'abc123def456',
  p_git_ref := 'refs/heads/feature/test'
);

-- Invoke runner
-- (via HTTP POST or trigger)

-- Verify run completed
SELECT run_id, status, finished_at
FROM ops.runs
WHERE project_id = 'test-project'
ORDER BY queued_at DESC
LIMIT 1;

-- Verify events logged
SELECT level, message
FROM ops.run_events
WHERE run_id = (
  SELECT run_id FROM ops.runs
  WHERE project_id = 'test-project'
  ORDER BY queued_at DESC
  LIMIT 1
);
```

## Production Considerations

**Concurrency:**
- Multiple runner instances can run concurrently
- `claim_next_run()` uses `FOR UPDATE SKIP LOCKED` for safe claiming
- Set `WORKER_ID` to unique value per instance for tracking

**Scalability:**
- Edge Functions auto-scale with load
- Database connection pooling handled by Supabase
- Consider rate limits on external API calls (GitHub, DigitalOcean)

**Security:**
- Use service role key (not anon key) for RPC calls
- Store secrets in Supabase Vault (not environment variables)
- Validate run ownership before executing sensitive operations
- Enable RLS policies on ops tables

## Future Enhancements

- [ ] Real GitHub Actions integration for image builds
- [ ] DigitalOcean API integration for deployments
- [ ] Staging DB cloning (pg_dump/restore)
- [ ] SBOM generation (Syft)
- [ ] Artifact upload to Supabase Storage
- [ ] Rollback capability (redeploy previous digest)
- [ ] Parallel phase execution where safe
- [ ] Custom phase plugins via metadata
