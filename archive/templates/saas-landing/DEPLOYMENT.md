# SaaS Landing Page - Deployment Guide

## 🎯 What's Ready

✅ **Code Deployed to Git**:
- Commit: `c77b5eb72126a406db1e92a27a3fb57cadf5f0ea`
- Branch: `feat/stripe-saas-starter-migration`
- GitHub: https://github.com/Insightpulseai/odoo

✅ **Features Built**:
- Next.js 16 landing page with Odoo.sh design
- Interactive dashboard (`/dashboard`)
- Odoo CMS integration via REST API
- Real-time deployment monitoring
- Platform metrics and logs

✅ **Backend Ready** (Pending Installation):
- Odoo module: `ipai_platform_api`
- 8 REST API endpoints
- Platform feature and deployment models
- n8n webhook integration

## 🚀 Quick Deploy (3 Steps)

### Step 1: Deploy Frontend to Vercel

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo/templates/saas-landing

# Run deployment script
./deploy.sh
```

**Or manually**:
```bash
vercel --prod
```

### Step 2: Configure Environment Variables

In Vercel Dashboard (https://vercel.com/dashboard):

```env
NEXT_PUBLIC_ODOO_URL=https://erp.insightpulseai.com
NEXT_PUBLIC_ODOO_DB=odoo
NEXT_PUBLIC_PLATFORM_NAME=InsightPulse.ai
NEXT_PUBLIC_ENABLE_DEPLOYMENTS=true
NEXT_PUBLIC_ENABLE_SHELL=false
```

### Step 3: Install Odoo Module (When Docker Fixed)

```bash
# SSH to server
ssh root@178.128.112.214

# Install module
docker exec odoo-prod odoo -d odoo -i ipai_platform_api --stop-after-init
docker restart odoo-prod
```

## 📊 Current Status

| Component | Status | URL |
|-----------|--------|-----|
| Frontend Code | ✅ Ready | Git commit c77b5eb |
| Next.js App | ⏳ Pending Deploy | Run `./deploy.sh` |
| Odoo Module | ✅ Ready | In Git at `addons/ipai/ipai_platform_api/` |
| Odoo Backend | ⚠️ Docker Issue | Container needs addons mount |
| API Endpoints | ⏳ Pending Module Install | Will be at `/api/platform/*` |

## 🔗 Integration Architecture

```
Vercel (Frontend)
    ↓ HTTPS/JSON-RPC
https://erp.insightpulseai.com (Odoo Backend)
    ↓ Webhooks
n8n + MCP (Platform Kit)
```

## 🧪 Testing After Deployment

```bash
# Test frontend
curl https://your-app.vercel.app/

# Test dashboard
curl https://your-app.vercel.app/dashboard

# Test API endpoints (after Odoo module installed)
curl -X POST https://erp.insightpulseai.com/api/platform/features \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{}}'
```

## ⚠️ Known Issues

### 1. Odoo Container Configuration
**Issue**: `/mnt/extra-addons` not mounted, database auth failure

**Solution**: Fix docker-compose.yml to mount addons directory:
```yaml
volumes:
  - ./addons/ipai:/mnt/extra-addons/ipai
```

### 2. Domain Name
**Note**: Using `erp.insightpulseai.com` (not `.net` - deprecated per CLAUDE.md)

## 📚 Documentation

- **Integration Guide**: [INTEGRATION.md](./INTEGRATION.md)
- **User Guide**: [README.md](./README.md)
- **Odoo Module**: `addons/ipai/ipai_platform_api/`

## 🆘 Troubleshooting

**Problem**: Vercel deployment fails
- **Solution**: Run `./deploy.sh` and follow prompts

**Problem**: API calls return errors
- **Solution**: Check Odoo module is installed and CORS is enabled

**Problem**: Dashboard shows mock data
- **Solution**: Verify `NEXT_PUBLIC_ODOO_URL` is set correctly

## 📞 Support

- GitHub Issues: https://github.com/Insightpulseai/odoo/issues
- Documentation: `docs/ai/`
- Commit Reference: `c77b5eb72126a406db1e92a27a3fb57cadf5f0ea`
