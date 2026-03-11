# InsightPulse Cloud Platform - SaaS Landing Page

Next.js 16 SaaS landing page with Odoo CMS integration, inspired by Odoo.sh.

## Features

### Frontend (Next.js)
- 🎨 **Modern Landing Page** - Odoo.sh-inspired design with purple (#714B67) and teal (#00A09D) theme
- 📊 **Interactive Dashboard** - Real-time deployment monitoring and management
- ⚡ **Server Components** - Fast, SEO-friendly with Next.js 16
- 🎯 **Dynamic Content** - Features, pricing, and content from Odoo CMS
- 📱 **Responsive Design** - Mobile-first with Tailwind CSS
- 🔐 **Authentication Ready** - Supabase OAuth integration

### Backend Integration (Odoo 19)
- 🔌 **REST API Module** (`ipai_platform_api`) - JSON-RPC endpoints for frontend
- 📝 **CMS Management** - Manage features, deployments, and content in Odoo
- 🚀 **Deployment System** - Track and trigger deployments via n8n
- 📊 **Monitoring Dashboard** - View metrics and logs in Odoo
- 🔄 **Real-time Sync** - Supabase for live updates

### Platform Kit Integration
- **n8n Workflows** - Automated deployment pipelines
- **MCP Task Queue** - Background job processing
- **Supabase Auth** - User authentication and sessions
- **Vercel Hosting** - Global CDN deployment

## Quick Start

### 1. Frontend Setup

```bash
cd templates/saas-landing

# Copy environment variables
cp .env.example .env.local

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

Visit http://localhost:3000

### 2. Backend Setup (Odoo)

```bash
# Install Odoo module
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo

# Install ipai_platform_api
./scripts/odoo_install.sh ipai_platform_api

# Or via Odoo CLI
docker exec odoo-web-1 odoo -d odoo -i ipai_platform_api --stop-after-init
docker restart odoo-web-1
```

### 3. Configure Integration

**Odoo Configuration** (`Settings > Technical > System Parameters`):
```
n8n.webhook_url = https://n8n.insightpulseai.com/webhook/deploy
platform.frontend_url = https://insightpulseai.com
```

**CORS Configuration** (`/etc/odoo/odoo.conf`):
```ini
[options]
proxy_mode = True
cors = *
```

## Architecture

```
┌─────────────────────────────────────────┐
│  Next.js Frontend (Vercel)              │
│  - Landing page                         │
│  - Dashboard                            │
│  - API routes (/api/*)                  │
└──────────────┬──────────────────────────┘
               │ HTTP/JSON-RPC
               ↓
┌─────────────────────────────────────────┐
│  Odoo Backend (DO Droplet)              │
│  - ipai_platform_api module             │
│  - /api/platform/* endpoints            │
│  - CMS management                       │
└──────────────┬──────────────────────────┘
               │ Webhooks
               ↓
┌─────────────────────────────────────────┐
│  Platform Kit Services                   │
│  - n8n (automation)                     │
│  - MCP (job queue)                      │
│  - Supabase (auth/database)             │
└─────────────────────────────────────────┘
```

## API Endpoints

### Frontend API Routes (Next.js)
- `GET /api/features` - Fetch features from Odoo
- `GET /api/deployments` - List deployments
- `POST /api/deployments` - Trigger deployment
- `GET /api/metrics/[env]` - Environment metrics

### Backend API Endpoints (Odoo)
- `POST /api/platform/features` - Get published features
- `POST /api/platform/deployments` - List deployments
- `POST /api/platform/deploy` - Trigger deployment
- `POST /api/platform/logs` - Get build logs
- `POST /api/platform/metrics` - Get monitoring metrics
- `POST /api/platform/shell/execute` - Execute shell command
- `POST /api/platform/pricing` - Get pricing plans

## Usage

### Managing Features (Odoo)

1. Navigate to **Platform > Features**
2. Create new feature:
   - Title: "Auto-Scaling"
   - Description: "Scale resources automatically"
   - Icon: 📈
   - Category: Automation
   - Published: ✓
3. Feature automatically appears on landing page

### Triggering Deployments

**From Dashboard** (http://localhost:3000/dashboard):
1. Select environment (Production/Staging/Development)
2. Click "Deploy Now"
3. Monitor logs in real-time

**From Odoo** (Platform > Deployments):
1. Create deployment record
2. Set branch and environment
3. Click "Trigger Deployment"
4. View logs and status

### Monitoring

**Dashboard View**:
- CPU/Memory usage
- Response times
- Request rates
- Error rates

**Odoo View** (Platform > Deployments):
- Full build logs
- n8n execution tracking
- Deployment history

## Development

### Adding New Features

1. **Create in Odoo** (Platform > Features)
2. Feature automatically syncs to frontend via API
3. No code changes needed!

### Customizing Dashboard

Edit `app/dashboard/page.tsx`:
```tsx
// Add new tab
<TabsTrigger value="custom">Custom View</TabsTrigger>

<TabsContent value="custom">
  {/* Your custom content */}
</TabsContent>
```

### Adding API Endpoints

**Frontend** (`app/api/custom/route.ts`):
```typescript
export async function GET() {
  const data = await fetch('https://erp.insightpulseai.com/api/platform/custom')
  return NextResponse.json(data)
}
```

**Backend** (Odoo controller):
```python
@http.route('/api/platform/custom', type='json', auth='public', methods=['POST'], csrf=False, cors='*')
def custom_endpoint(self):
    return {'data': 'custom response'}
```

## Deployment

### Vercel (Frontend)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Configure environment variables in Vercel dashboard
```

### DigitalOcean (Backend)

```bash
# SSH to Odoo server
ssh root@178.128.112.214

# Update module
docker exec odoo-web-1 odoo -d odoo -u ipai_platform_api --stop-after-init
docker restart odoo-web-1
```

### nginx Configuration

```nginx
# Frontend (Vercel)
server {
    server_name insightpulseai.com;
    location / {
        proxy_pass https://saas-landing.vercel.app;
    }
}

# Backend API (Odoo)
server {
    server_name erp.insightpulseai.com;
    location /api/platform/ {
        proxy_pass http://localhost:8069;
        add_header Access-Control-Allow-Origin *;
    }
}
```

## Testing

```bash
# Test Odoo API
curl -X POST https://erp.insightpulseai.com/api/platform/features \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{}}'

# Test Next.js API
curl http://localhost:3000/api/features

# Test deployment trigger
curl -X POST http://localhost:3000/api/deployments \
  -H "Content-Type: application/json" \
  -d '{"branch":"main","environment":"production"}'
```

## Documentation

- **Full Integration Guide**: [INTEGRATION.md](./INTEGRATION.md)
- **Odoo Module**: `addons/ipai/ipai_platform_api/`
- **Platform Kit**: `infra/platform-kit/`

## Tech Stack

- **Frontend**: Next.js 16, React 19, Tailwind CSS, shadcn/ui
- **Backend**: Odoo 19 CE, Python 3.12, PostgreSQL 16
- **Platform**: Supabase, n8n, MCP, Vercel, DigitalOcean
- **Monitoring**: (To be integrated: Prometheus, Grafana)

## Support

For issues or questions:
- GitHub Issues: https://github.com/Insightpulseai/odoo/issues
- Odoo Platform Menu: **Platform > Features/Deployments**
- Documentation: `docs/ai/`

---

**Built with ❤️ by InsightPulse AI**
