# IPAI Control Center Docs - Deployment Guide

## Vercel Project Configuration

**Project**: `ipai-control-center-docs`
**Team**: `jake-tolentinos-projects-c0369c83`
**Framework**: Next.js 14 + Nextra 3

---

## GitHub Secrets Setup

To enable automatic deployment, add these secrets to your GitHub repository:

**Repository Settings → Secrets and variables → Actions → New repository secret**

### Required Secrets

1. **`VERCEL_ORG_ID`**
   ```
   team_wphKJ7lHA3QiZu6VgcotQBQM
   ```

2. **`VERCEL_PROJECT_ID`**
   ```
   prj_NuljvFC1QaQzNQV8uw53YDIguh9j
   ```

3. **`VERCEL_TOKEN`**
   - Create a token at: https://vercel.com/account/tokens
   - Select scope: Full Account
   - Copy the token value
   - Add it as a secret (never commit this!)

---

## Deployment Workflow

### Automatic Deployment

The GitHub Actions workflow (`.github/workflows/deploy-ipai-control-center-docs.yml`) automatically deploys when:

1. **Push to main** affecting:
   - `spec/ipai-control-center/**`
   - `apps/ipai-control-center-docs/**`
   - `vercel.json`

2. **Manual trigger** via GitHub Actions UI

### Manual Deployment (Local)

```bash
# Navigate to docs directory
cd apps/ipai-control-center-docs

# Install dependencies
npm install

# Build locally
npm run build

# Deploy to Vercel
vercel --prod
```

---

## Verification

### Check Deployment Status

```bash
# Check GitHub Actions workflow runs
gh run list --workflow "Deploy IPAI Control Center Docs (Vercel)" --limit 5

# Check Vercel deployments
vercel ls
```

### Local Development

```bash
cd apps/ipai-control-center-docs
npm install
npm run dev
# Visit http://localhost:3007
```

---

## Project Structure

```
apps/ipai-control-center-docs/
├── pages/
│   ├── index.mdx           # Overview page
│   ├── constitution.md     # Constitution spec
│   ├── prd.md              # Product Requirements Document
│   ├── plan.md             # Delivery Plan
│   ├── tasks.md            # Task Breakdown
│   ├── _app.jsx            # Next.js app wrapper
│   └── _meta.js            # Nextra navigation config
├── next.config.mjs         # Next.js + Nextra configuration
├── theme.config.jsx        # Nextra theme settings
├── package.json            # Dependencies
└── .vercel/
    └── project.json        # Vercel project configuration
```

---

## Troubleshooting

### Build Fails

Check build logs:
```bash
npm run build
```

Common issues:
- Missing dependencies: `npm install`
- Nextra version: Ensure `nextra@^3.0.0`
- Node version: Requires Node 18+

### Deployment Fails

1. Verify GitHub secrets are set correctly
2. Check workflow logs in GitHub Actions
3. Ensure `.vercel/project.json` is committed
4. Verify Vercel token has correct permissions

### Pages Not Updating

1. Spec files are copied, not symlinked
2. After updating `spec/ipai-control-center/*.md`, copy to `pages/`:
   ```bash
   cp spec/ipai-control-center/constitution.md apps/ipai-control-center-docs/pages/
   cp spec/ipai-control-center/prd.md apps/ipai-control-center-docs/pages/
   cp spec/ipai-control-center/plan.md apps/ipai-control-center-docs/pages/
   cp spec/ipai-control-center/tasks.md apps/ipai-control-center-docs/pages/
   ```

---

## Next Steps

1. ✅ Vercel project linked (`ipai-control-center-docs`)
2. ⏳ Add GitHub secrets (VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID)
3. ⏳ Merge `feat/ipai-control-center-docs` to `main`
4. ⏳ Verify automatic deployment succeeds
5. ⏳ Share production URL with stakeholders

---

## Production URL

After deployment, the docs will be available at:
```
https://ipai-control-center-docs-<hash>.vercel.app
```

Custom domain can be configured in Vercel project settings.
