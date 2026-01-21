# 🚀 Deployment Checklist

Use this checklist to deploy your Ops Control Room to production.

---

## Pre-Deployment

### ✅ Code Ready
- [ ] All files saved and committed
- [ ] No TypeScript errors (`tsc --noEmit`)
- [ ] Build succeeds (`pnpm run build`)
- [ ] All environment variables documented

### ✅ Supabase Setup
- [ ] Supabase project created
- [ ] Database schema applied (`/supabase/schema.sql`)
- [ ] RLS policies enabled and tested
- [ ] Realtime publication configured
- [ ] Service role key secured (never committed)

### ✅ Edge Function
- [ ] Function code complete (`/supabase/functions/ops-executor/`)
- [ ] All secrets set (`supabase secrets list`)
- [ ] Function deployed (`supabase functions deploy ops-executor`)
- [ ] Function tested (manual curl or cron)
- [ ] Logs reviewed (`supabase functions logs ops-executor`)

### ✅ Testing
- [ ] Local development works (`pnpm run dev`)
- [ ] Can create runs
- [ ] Events stream in real-time
- [ ] Artifacts display correctly
- [ ] Error handling works
- [ ] Multiple concurrent runs work

---

## Frontend Deployment

### Option A: Figma Make

**Steps:**
1. Build the app
   ```bash
   pnpm run build
   ```

2. Upload `/dist` folder to Figma Make

3. Set environment variables in Figma Make settings:
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`

4. Publish

**Result:** Your app is live on Figma's CDN.

---

### Option B: Vercel

**Steps:**
1. Install Vercel CLI
   ```bash
   npm i -g vercel
   ```

2. Deploy
   ```bash
   vercel
   ```

3. Set environment variables in Vercel dashboard:
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`

4. Production deploy
   ```bash
   vercel --prod
   ```

**Result:** Your app is live on `your-project.vercel.app`.

---

### Option C: Netlify

**Steps:**
1. Build the app
   ```bash
   pnpm run build
   ```

2. Install Netlify CLI
   ```bash
   npm i -g netlify-cli
   ```

3. Deploy
   ```bash
   netlify deploy --dir=dist --prod
   ```

4. Set environment variables in Netlify dashboard:
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`

**Result:** Your app is live on `your-project.netlify.app`.

---

### Option D: Static Hosting (AWS S3, Google Cloud Storage, etc)

**Steps:**
1. Build the app
   ```bash
   pnpm run build
   ```

2. Upload `/dist` to your CDN

3. Configure environment variables (depends on hosting)

4. Set up HTTPS (required for Supabase WebSocket)

**Result:** Your app is live on your custom domain.

---

## Backend Deployment (Supabase)

### 1. Database
```bash
# Already done if you applied schema.sql
# Verify tables exist:
supabase db remote
```

### 2. Edge Function
```bash
# Deploy
supabase functions deploy ops-executor

# Verify
supabase functions list

# Check logs
supabase functions logs ops-executor --tail
```

### 3. Cron Job (Auto-execution)
```sql
-- Run this in Supabase SQL Editor
create extension if not exists pg_cron;

select cron.schedule(
  'ops-executor-cron',
  '* * * * *',  -- Every minute
  $$
  select
    net.http_post(
      url := 'https://your-project.supabase.co/functions/v1/ops-executor',
      headers := '{"Authorization": "Bearer your-anon-key"}'::jsonb
    )
  $$
);

-- Verify it's scheduled
select * from cron.job;
```

---

## Post-Deployment

### ✅ Smoke Tests
- [ ] Visit production URL
- [ ] Type a command (e.g., "deploy staging")
- [ ] Runbook card appears
- [ ] Click "Run"
- [ ] Log viewer opens
- [ ] Events stream in real-time
- [ ] Run completes successfully

### ✅ Monitoring
- [ ] Check Supabase Dashboard > Logs
- [ ] Check Edge Function logs
- [ ] Check browser console for errors
- [ ] Test on multiple browsers
- [ ] Test on mobile device

### ✅ Performance
- [ ] Page load time < 2s
- [ ] Event streaming latency < 500ms
- [ ] No memory leaks (open log viewer for 5 minutes)
- [ ] Database queries optimized (check Supabase query performance)

### ✅ Security
- [ ] No secrets in browser
- [ ] HTTPS enabled
- [ ] RLS policies working
- [ ] Service role key not exposed
- [ ] External API tokens secured

---

## Production Settings

### Recommended Supabase Settings

1. **Database Connection Pooling**
   - Enable connection pooler (Supabase Dashboard > Database > Connection pooling)

2. **Realtime Limits**
   - Set max connections (default: 200)
   - Set rate limits if needed

3. **Edge Function Timeout**
   - Default: 150s (increase if needed)

4. **Row Level Security**
   - Verify policies are enabled
   - Test with non-admin user

### Recommended Frontend Settings

1. **Environment Variables**
   ```env
   VITE_SUPABASE_URL=https://your-project.supabase.co
   VITE_SUPABASE_ANON_KEY=your-anon-key
   ```

2. **Build Optimizations**
   - Minification enabled (default in Vite)
   - Tree shaking enabled (default)
   - Code splitting enabled (default)

---

## Rollback Plan

If something goes wrong:

### Frontend Rollback
1. **Vercel:** Revert to previous deployment in dashboard
2. **Netlify:** Rollback in dashboard > Deploys
3. **Figma Make:** Re-upload previous build
4. **Static:** Re-upload previous `/dist` folder

### Backend Rollback

#### Edge Function
```bash
# List deployments
supabase functions list

# Deploy previous version (if you have it)
git checkout <previous-commit>
supabase functions deploy ops-executor
```

#### Database
```sql
-- If you need to rollback schema changes
-- Create a backup first!

-- Example: Remove new column
alter table ops.runs drop column if exists new_column;
```

---

## Monitoring & Alerts

### Set Up Alerts

1. **Supabase Dashboard**
   - Enable email alerts for high CPU/memory
   - Set up alerts for failed Edge Function invocations

2. **Error Tracking**
   - Add Sentry/LogRocket for frontend errors
   - Monitor Edge Function logs

3. **Uptime Monitoring**
   - Use UptimeRobot or Pingdom
   - Monitor frontend URL + Edge Function endpoint

### What to Monitor

- [ ] Edge Function invocation count
- [ ] Edge Function error rate
- [ ] Database query performance
- [ ] Realtime connection count
- [ ] Frontend page load time
- [ ] API rate limit usage (Vercel, GitHub, etc)

---

## Scaling Considerations

### When You Outgrow Free Tier

1. **Supabase**
   - Upgrade to Pro ($25/mo) for:
     - 8GB database
     - 250GB bandwidth
     - Unlimited Edge Function invocations
     - Daily backups

2. **Vercel/Netlify**
   - Most hobby tiers are sufficient
   - Upgrade if you hit bandwidth limits

### Performance Optimization

1. **Database**
   - Add indexes on frequently queried columns
   - Archive old runs (move to separate table)
   - Use connection pooling

2. **Edge Function**
   - Add caching for read-heavy operations
   - Batch database writes where possible
   - Add retry logic with exponential backoff

3. **Frontend**
   - Implement virtual scrolling (already done)
   - Lazy load components
   - Add service worker for offline support

---

## Security Hardening

### Required for Production

1. **Add Authentication**
   ```typescript
   // Enable Supabase Auth
   const { data: { user } } = await supabase.auth.getUser();
   
   // Update RLS policies to use auth.uid()
   ```

2. **Add Rate Limiting**
   - Limit run creation (e.g., 10 runs/hour per user)
   - Implement in Edge Function or Supabase

3. **Add Audit Logging**
   - Log all run creations
   - Log all modifications
   - Store IP addresses (if required for compliance)

4. **Add Input Validation**
   - Sanitize user inputs
   - Validate runbook plans before execution
   - Prevent SQL injection (use parameterized queries)

---

## Compliance (If Needed)

### GDPR/Privacy
- [ ] Add privacy policy
- [ ] Add data retention policy
- [ ] Add ability to delete user data
- [ ] Log consent for data processing

### SOC 2 / ISO 27001
- [ ] Implement audit logging
- [ ] Add access controls (RBAC)
- [ ] Document security procedures
- [ ] Conduct security reviews

---

## Final Checklist

### Before Launch
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Secrets secured
- [ ] Monitoring configured
- [ ] Backups enabled
- [ ] Rollback plan documented
- [ ] Team trained on operations

### Launch Day
- [ ] Deploy to production
- [ ] Run smoke tests
- [ ] Monitor for 1 hour
- [ ] Share with stakeholders
- [ ] Gather feedback

### Post-Launch
- [ ] Monitor for 24 hours
- [ ] Fix any critical issues
- [ ] Document lessons learned
- [ ] Plan next iteration

---

## 🎉 You're Ready to Deploy!

Follow this checklist step-by-step, and you'll have a production-ready Ops Control Room.

**Questions?** Check:
- [SETUP.md](../SETUP.md) for detailed instructions
- [README.md](../README.md) for architecture overview
- Supabase docs for platform-specific questions

**Good luck! 🚀**
