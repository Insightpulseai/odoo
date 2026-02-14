# Deployment Guide: Vercel Sandbox

Quick deployment guide for TBWA Odoo Frontend Shell using Vercel Sandbox.

## Prerequisites

- Vercel CLI installed: `npm i -g vercel`
- Vercel account (free tier works)
- Git repository pushed to GitHub

## Vercel Sandbox Deployment

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Login to Vercel

```bash
vercel login
```

### 3. Deploy to Sandbox

From `apps/odoo-frontend-shell/`:

```bash
vercel deploy --sandbox
```

Output:
```
🔍  Inspect: https://vercel.com/your-name/odoo-frontend-shell/...
✅  Preview: https://odoo-frontend-shell-abc123.vercel.app
```

### 4. Configure Environment Variables

**Via Vercel CLI:**
```bash
vercel env add NEXT_PUBLIC_ODOO_URL
# Enter: https://erp.insightpulseai.com

vercel env add NEXT_PUBLIC_ODOO_DB
# Enter: odoo
```

**Via Vercel Dashboard:**
1. Go to https://vercel.com/dashboard
2. Select project: `odoo-frontend-shell`
3. Settings → Environment Variables
4. Add:
   - `NEXT_PUBLIC_ODOO_URL` = `https://erp.insightpulseai.com`
   - `NEXT_PUBLIC_ODOO_DB` = `odoo`

### 5. Redeploy with Environment Variables

```bash
vercel deploy --sandbox
```

## Vercel Sandbox Features

| Feature | Description |
|---------|-------------|
| **Instant URL** | Auto-generated shareable preview URL |
| **HTTPS** | Automatic SSL certificate |
| **Lifetime** | 30 days (extendable) |
| **Environments** | Separate preview/production environments |
| **Logs** | Real-time function and build logs |
| **Analytics** | Traffic and performance metrics |

## Accessing the Sandbox

### Get Deployment URL

```bash
vercel ls
```

### Open in Browser

```bash
vercel open
```

### View Logs

```bash
vercel logs
```

## Production Deployment

When ready for production:

```bash
# Link to project
vercel link

# Deploy to production
vercel --prod
```

## Domain Configuration

### Custom Domain (Production Only)

1. Vercel Dashboard → Project Settings → Domains
2. Add domain: `odoo.tbwa-smp.com`
3. Configure DNS:
   ```
   CNAME  odoo  cname.vercel-dns.com
   ```

## Monitoring

### Check Deployment Status

```bash
vercel inspect <deployment-url>
```

### View Analytics

```bash
vercel analytics
```

## Troubleshooting

### Deployment Fails

```bash
# Check build logs
vercel logs <deployment-url>

# Verify build locally
pnpm build
```

### CORS Errors

Ensure Odoo backend allows CORS:
- Check `vercel.json` headers configuration
- Verify Odoo nginx config allows `https://*.vercel.app`

### Environment Variables Not Applied

```bash
# List all env vars
vercel env ls

# Pull env vars locally
vercel env pull .env.local
```

### 404 on Routes

Next.js App Router requires:
- `next.config.ts` properly configured
- Static routes exported for Edge

## Cleanup

### Remove Deployment

```bash
vercel rm <deployment-url>
```

### Remove Project

```bash
vercel remove odoo-frontend-shell
```

## CI/CD Integration

### GitHub Actions (Automatic Deployment)

Create `.github/workflows/vercel-deploy.yml`:

```yaml
name: Vercel Sandbox Deploy

on:
  push:
    branches: [feature/*, sandbox/*]
    paths:
      - 'apps/odoo-frontend-shell/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Vercel CLI
        run: npm install --global vercel@latest

      - name: Pull Vercel Environment
        run: vercel pull --yes --environment=preview --token=${{ secrets.VERCEL_TOKEN }}
        working-directory: apps/odoo-frontend-shell

      - name: Build Project
        run: vercel build --token=${{ secrets.VERCEL_TOKEN }}
        working-directory: apps/odoo-frontend-shell

      - name: Deploy to Vercel Sandbox
        run: vercel deploy --prebuilt --token=${{ secrets.VERCEL_TOKEN }}
        working-directory: apps/odoo-frontend-shell
```

**Required Secrets:**
- `VERCEL_TOKEN` - Get from https://vercel.com/account/tokens
- `VERCEL_ORG_ID` - From `.vercel/project.json`
- `VERCEL_PROJECT_ID` - From `.vercel/project.json`

## Support

- **Vercel Docs**: https://vercel.com/docs
- **Next.js Deployment**: https://nextjs.org/docs/deployment
- **Sandbox Docs**: https://vercel.com/docs/vercel-sandbox
