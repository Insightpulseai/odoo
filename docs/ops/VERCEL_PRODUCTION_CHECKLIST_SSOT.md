# Vercel Production Checklist SSOT

Canonical pre/post-deploy checklist for all `apps/ops-console` production releases.
Run this before every merge to `main`.

---

## Pre-Deploy

### Environment Variables
- [ ] All required vars set for **Production** environment in Vercel Project Settings
- [ ] All required vars set for **Preview** environment (staging-safe values)
- [ ] All required vars set for **Development** environment (`.env.local` matches)
- [ ] No secrets in `NEXT_PUBLIC_*` vars (client-visible)
- [ ] `SUPABASE_MANAGEMENT_API_TOKEN` — server-only, never `NEXT_PUBLIC_`
- [ ] `SUPABASE_SERVICE_ROLE_KEY` — server-only, never `NEXT_PUBLIC_`

### Custom Domain & Protection
- [ ] Custom domain configured in Vercel Project → Domains
- [ ] SSL certificate auto-renewed (Vercel-managed)
- [ ] **Deployment Protection** enabled (Project Settings → General → Deployment Protection)
- [ ] Password or Vercel Authentication set for Preview environments

### PR Readiness
- [ ] All Preview comments resolved (`vercel-toolbar` threads closed)
- [ ] All CI gates green: `ops-console-check`, `ops-console-playwright`, `ops-console-bundle-size`
- [ ] No `TODO` or `FIXME` in files changed by this PR

---

## Deploy

### Build Validation
- [ ] `npm run build` passes locally (0 errors, 0 new ESLint warnings)
- [ ] Bundle size delta ≤ 20% from previous build (reported by `ops-console-bundle-size` workflow)
- [ ] No new `any` TypeScript suppressions in diff
- [ ] No new `// eslint-disable` comments without justification comment above

### Deployment Trigger
```bash
# Production deploy via git (recommended)
git push origin main

# Manual deploy via CLI (emergency only)
cd apps/ops-console && vercel --prod
```

---

## Post-Deploy

### Health Checks (within 5 min of deploy)
- [ ] Health endpoint responds `200`: `curl -s https://<domain>/api/health | jq .status`
- [ ] Main page loads without JS errors (check browser console)
- [ ] At least one authenticated route loads successfully

### Core Web Vitals (within 24h)
- [ ] LCP ≤ 2.5 s (Largest Contentful Paint)
- [ ] INP ≤ 200 ms (Interaction to Next Paint)
- [ ] CLS ≤ 0.1 (Cumulative Layout Shift)
- Source: Vercel Analytics → Web Vitals tab

### Error Monitoring
- [ ] Error rate ≤ 0.1% in first 30 min (Vercel Functions → Error Rate)
- [ ] No 5xx spikes in Vercel Deployments → Runtime Logs

---

## Rollback

### When to Rollback
- Error rate > 1% sustained for > 5 min
- Health endpoint returns non-200
- Critical data mutation bug discovered

### How to Rollback
```bash
# Instant rollback to previous production deployment
vercel rollback

# Or via dashboard: Deployments → previous deployment → Promote to Production
```

**Expected recovery time**: < 2 min (Vercel instant rollback, no re-build).

### Post-Rollback
- [ ] Create GitHub Issue documenting the incident
- [ ] Add failing case to Playwright smoke tests before re-deploying
- [ ] Notify team in Slack `#ops-console-deploys`

---

## Related Docs

| Doc | Purpose |
|-----|---------|
| `docs/ops/VERCEL_MONOREPO.md` | Workspace registration, skip-unaffected, env vars |
| `docs/ops/VERCEL_PREVIEWS.md` | Preview deployments, Toolbar comments, reviewer workflow |
| `docs/ops/VERCEL_DOCS_SSOT.md` | Canonical Vercel docs URLs (MCP, monorepos, AI Gateway) |
| `docs/ops/SUPABASE_VERCEL.md` | Env var sync contract |
| `docs/platform/GOLDEN_PATH.md` | Full release lane contract |
