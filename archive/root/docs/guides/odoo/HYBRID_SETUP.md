# Hybrid OdooOps Portal - Setup Complete ✅

**Path 3: Hybrid Best-of-Both** - QWeb shell + Next.js Tailwind dashboard with shared design tokens.

## What Was Created

### 1. Odoo QWeb Shell Module (`ipai_odooops_shell`)

**Location:** `addons/ipai/ipai_odooops_shell/`

**Features:**
- ✅ Server-rendered QWeb navigation shell (no React hydration issues)
- ✅ User authentication via Odoo (auth="user")
- ✅ Iframe embed for Next.js dashboard
- ✅ Shared CSS design tokens (sync with Tailwind)
- ✅ Routes: `/odooops` (main), `/odooops/healthz` (health check)

**Files Created:**
```
addons/ipai/ipai_odooops_shell/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py
├── static/src/css/
│   └── shell.css
└── views/
    ├── menu.xml
    └── shell_templates.xml
```

### 2. Next.js Dashboard App (`odooops-dashboard`)

**Location:** `web/odooops-dashboard/`

**Features:**
- ✅ Next.js 14 App Router
- ✅ Tailwind CSS with shared design tokens
- ✅ TypeScript
- ✅ Example components (MetricCard, ProjectCard)
- ✅ Dashboard page with metrics grid + project cards

**Files Created:**
```
web/odooops-dashboard/
├── package.json
├── tsconfig.json
├── next.config.mjs
├── postcss.config.mjs
├── tailwind.config.ts
├── .gitignore
├── README.md
├── app/
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
└── components/
    ├── MetricCard.tsx
    └── ProjectCard.tsx
```

### 3. Shared Design Tokens

**Location:** `design-tokens/tokens.json`

**Tokens:**
- Colors: primary, bg, text, border, success, warning, error
- Spacing: nav-height, sidebar-width
- Typography: font-family

**Synced In:**
- Odoo CSS vars (`shell.css`)
- Tailwind config (`tailwind.config.ts`)
- Next.js globals (`globals.css`)

## Installation & Usage

### Step 1: Install Odoo Module

```bash
# Navigate to Odoo directory
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo

# Install the module
./odoo-bin -d odoo_dev --addons-path=addons,addons/ipai \
  -i ipai_odooops_shell --stop-after-init

# Run Odoo
./odoo-bin -d odoo_dev --http-port 8069 --addons-path=addons,addons/ipai
```

### Step 2: Install & Run Next.js Dashboard

```bash
# Navigate to dashboard
cd web/odooops-dashboard

# Install dependencies
npm install

# Run development server
npm run dev
# Runs on http://localhost:3000
```

### Step 3: Access the Portal

1. Open Odoo: `http://localhost:8069`
2. Login with your Odoo credentials
3. Navigate to: `http://localhost:8069/odooops`
4. You'll see:
   - Odoo QWeb navigation shell (top nav)
   - Next.js dashboard embedded (iframe)

## Verification

### Health Check

```bash
# Check Odoo shell
curl -I http://localhost:8069/odooops/healthz
# Should return: 200 OK

# Check Next.js dashboard
curl -I http://localhost:3000
# Should return: 200 OK
```

### Visual Verification

**Expected Result:**
- Top navigation bar with "OdooOps" brand + nav links (Dashboard, Projects, etc.)
- User name displayed on right
- Dashboard content below showing:
  - 4 metric cards (Projects: 12, Deployments: 48, Health: 98%, WAF: A+)
  - 3 project cards (Production ERP, Staging CMS, Dev Portal)

## Production Deployment

### Deploy Next.js to Vercel

```bash
cd web/odooops-dashboard
vercel --prod
# Note the deployment URL
```

### Update Odoo Environment

```bash
# Set environment variable in your Odoo deployment
export NEXTJS_DASHBOARD_URL="https://odooops-dashboard.vercel.app"

# Or via Odoo UI: Settings → Technical → System Parameters
# Key: NEXTJS_DASHBOARD_URL
# Value: https://odooops-dashboard.vercel.app
```

## Design Token Workflow

### Update Tokens

Edit `design-tokens/tokens.json`:

```json
{
  "colors": {
    "primary": "#3b82f6"  // Change this
  }
}
```

### Sync to Both Systems

**Odoo:** Update `addons/ipai/ipai_odooops_shell/static/src/css/shell.css`:
```css
:root {
  --odooops-primary: #3b82f6;  /* Sync from tokens.json */
}
```

**Next.js:** Update `web/odooops-dashboard/tailwind.config.ts`:
```typescript
colors: {
  primary: "#3b82f6",  // Sync from tokens.json
}
```

## No Hydration Issues ✅

**Why this works:**
- Odoo QWeb shell: Server-rendered HTML (no client-side hydration)
- Next.js dashboard: Runs in isolated iframe (handles its own hydration)
- No shared React context between them = no mismatch possible

## Architecture Benefits

1. **Best of Both Worlds:**
   - Odoo: Auth, navigation, server-side rendering
   - Next.js: Rich interactive dashboards, modern tooling

2. **Shared Design System:**
   - Consistent look and feel
   - Single source of truth for tokens

3. **Independent Deployment:**
   - Update Next.js dashboard without touching Odoo
   - Scale each service independently

4. **Security:**
   - Odoo handles authentication
   - Next.js runs in separate domain (if needed)

## Next Steps

### Add More Dashboard Pages

Create new routes in Next.js:
```bash
# Example: Observability page
mkdir web/odooops-dashboard/app/observability
# Add page.tsx there
```

### Add Supabase Integration

Connect to `ops.*` tables for real data:
```typescript
// In Next.js components
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)
```

### Add More Components

- WAF posture cards
- Advisor findings table
- Observability charts
- CMS content editor

## Troubleshooting

### Iframe not loading

**Check CORS:**
- Next.js must allow iframe embedding
- Add to `next.config.mjs`:
```javascript
async headers() {
  return [
    {
      source: '/(.*)',
      headers: [
        { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
      ],
    },
  ]
}
```

### Styles not matching

**Verify tokens are synced:**
```bash
# Check Odoo CSS vars
cat addons/ipai/ipai_odooops_shell/static/src/css/shell.css | grep "odooops-primary"

# Check Tailwind config
cat web/odooops-dashboard/tailwind.config.ts | grep "primary"

# Check tokens source
cat design-tokens/tokens.json | grep "primary"
```

## Evidence

**Created:** 2026-02-14 07:12 UTC

**Files Modified:** 19

**Modules:** 2 (Odoo QWeb shell, Next.js dashboard)

**Status:** ✅ Ready to ship

---

**For questions or issues, see:**
- Odoo module: `addons/ipai/ipai_odooops_shell/`
- Next.js app: `web/odooops-dashboard/README.md`
- Design tokens: `design-tokens/tokens.json`
