# Quick Start: Deploy to Vercel

## Option 1: Deploy via GitHub (Recommended)

### Step 1: Push to GitHub
Already done! The code is at: `github.com/jgtolentino/odoo-ce/apps/odoo-frontend-shell`

### Step 2: Import to Vercel

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select: `jgtolentino/odoo-ce`
4. **Root Directory**: `apps/odoo-frontend-shell`
5. Click "Deploy"

### Step 3: Configure Environment Variables

In Vercel dashboard during import:
- `NEXT_PUBLIC_ODOO_URL` = `https://erp.insightpulseai.com`
- `NEXT_PUBLIC_ODOO_DB` = `odoo`

### Step 4: Deploy

Click "Deploy" button. You'll get a URL like:
```
https://odoo-frontend-shell-abc123.vercel.app
```

---

## Option 2: Deploy via Vercel CLI

### Step 1: Login to Vercel

```bash
vercel login
# Select: Continue with GitHub
```

### Step 2: Navigate to Project

```bash
cd /Users/tbwa/odoo-ce/apps/odoo-frontend-shell
```

### Step 3: Deploy

```bash
vercel
```

Follow prompts:
- Set up and deploy? **Y**
- Which scope? **Select your account**
- Link to existing project? **N**
- Project name? **odoo-frontend-shell**
- Directory? **./** (current)
- Override settings? **N**

### Step 4: Add Environment Variables

```bash
vercel env add NEXT_PUBLIC_ODOO_URL production
# Paste: https://erp.insightpulseai.com

vercel env add NEXT_PUBLIC_ODOO_DB production
# Paste: odoo
```

### Step 5: Redeploy

```bash
vercel --prod
```

---

## What You Get

✅ **Preview URL**: `https://odoo-frontend-shell-abc123.vercel.app`
✅ **Custom Domain**: Configure in Vercel dashboard
✅ **Automatic HTTPS**: SSL included
✅ **CDN**: Global edge network
✅ **Analytics**: Built-in traffic analytics

---

## Test the Deployment

1. Open the Vercel URL
2. Login with Odoo credentials:
   - Username: `admin`
   - Password: Your Odoo password
3. Should connect to `https://erp.insightpulseai.com`

---

## Troubleshooting

### CORS Errors

If you see CORS errors, Odoo backend needs to allow Vercel domain:

**Nginx config** (`/etc/nginx/sites-available/odoo`):
```nginx
location / {
    # Existing config...

    # Add CORS for Vercel
    add_header 'Access-Control-Allow-Origin' 'https://odoo-frontend-shell-abc123.vercel.app' always;
    add_header 'Access-Control-Allow-Credentials' 'true' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Content-Type, Cookie, Set-Cookie' always;

    if ($request_method = 'OPTIONS') {
        return 204;
    }
}
```

Restart nginx:
```bash
ssh root@178.128.112.214 "systemctl reload nginx"
```

### Session Errors

Odoo sessions are cookie-based. Ensure:
- `withCredentials: true` in axios config (already set)
- Same-site cookies configured on Odoo
- HTTPS on both frontend and backend

### Build Errors

```bash
# Test build locally
cd apps/odoo-frontend-shell
pnpm install
pnpm build
```

---

## Next Steps

1. **Custom Domain**: Add `odoo.tbwa-smp.com` in Vercel dashboard
2. **Production Deploy**: Use `vercel --prod` for production deployment
3. **CI/CD**: Connect GitHub repo for automatic deployments
4. **Analytics**: Enable Vercel Analytics in dashboard

---

## Support

- **Vercel Dashboard**: https://vercel.com/dashboard
- **Deployment Docs**: https://vercel.com/docs/deployments/overview
- **Next.js on Vercel**: https://nextjs.org/docs/app/building-your-application/deploying
