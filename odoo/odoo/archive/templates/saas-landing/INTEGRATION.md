# Platform Kit + Odoo CMS Integration Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Public-Facing Layer                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │   Next.js SaaS Landing (templates/saas-landing/)         │  │
│  │   - Landing page (/)                                      │  │
│  │   - Dashboard (/dashboard)                                │  │
│  │   - Dynamic content from Odoo CMS                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ API Calls
┌─────────────────────────────────────────────────────────────────┐
│                      Platform Kit Layer                          │
│  ┌──────────────┬──────────────┬──────────────┬─────────────┐  │
│  │   Supabase   │     n8n      │     MCP      │   Vercel    │  │
│  │  (Database)  │ (Automation) │ (Jobs/Tasks) │  (Hosting)  │  │
│  └──────────────┴──────────────┴──────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ RPC/REST
┌─────────────────────────────────────────────────────────────────┐
│                       Odoo Backend Layer                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │   Odoo 19 CE + OCA Modules                               │  │
│  │   - Website/CMS module                                    │  │
│  │   - ipai_platform_theme                                   │  │
│  │   - REST API endpoints                                    │  │
│  │   - Business logic & database                             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Integration Points

### 1. Next.js Frontend → Odoo CMS API

**Objective**: Fetch dynamic content (blog posts, features, pricing) from Odoo CMS

**Implementation**:

```typescript
// lib/odoo-api.ts
const ODOO_URL = process.env.NEXT_PUBLIC_ODOO_URL || 'https://erp.insightpulseai.com'
const ODOO_DB = process.env.NEXT_PUBLIC_ODOO_DB || 'odoo'

export async function fetchOdooBlogPosts() {
  const response = await fetch(`${ODOO_URL}/website/blog/posts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'call',
      params: { db: ODOO_DB }
    })
  })
  return response.json()
}

export async function fetchOdooFeatures() {
  // Fetch features from Odoo website module
}

export async function fetchOdooPricing() {
  // Fetch pricing plans from Odoo product catalog
}
```

### 2. Platform Kit Services Integration

**Supabase**: User authentication, session management, real-time notifications
```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export async function signInWithOdoo(email: string, password: string) {
  // OAuth flow with Odoo backend
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'custom',
    options: {
      redirectTo: `${ODOO_URL}/auth/callback`
    }
  })
  return { data, error }
}
```

**n8n Workflows**: Automate deployment pipelines, notifications
```typescript
// lib/n8n-webhooks.ts
const N8N_WEBHOOK_URL = process.env.N8N_WEBHOOK_URL

export async function triggerDeployment(branch: string, environment: string) {
  const response = await fetch(`${N8N_WEBHOOK_URL}/deploy`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ branch, environment })
  })
  return response.json()
}
```

**MCP Jobs**: Task queue for long-running operations
```typescript
// lib/mcp-client.ts
export async function queueBuildJob(projectId: string, commitHash: string) {
  // Use MCP to queue build jobs
  // Integrates with web/mcp-coordinator
}
```

### 3. Odoo CMS Configuration

**Create Website Pages in Odoo**:
```bash
# SSH into Odoo server
ssh root@178.128.112.214

# Create website pages via Odoo CLI
docker exec odoo-web-1 odoo shell -d odoo -c /etc/odoo/odoo.conf << EOF
from odoo.api import Environment

# Create landing page content
env = Environment(cr, uid, {})
Page = env['website.page']

landing_content = Page.create({
    'name': 'Platform Features',
    'url': '/api/features',
    'view_id': env.ref('website.layout').id,
    'website_published': True
})
EOF
```

### 4. Environment Variables Setup

**Next.js (`templates/saas-landing/.env.local`)**:
```bash
# Odoo Backend
NEXT_PUBLIC_ODOO_URL=https://erp.insightpulseai.com
NEXT_PUBLIC_ODOO_DB=odoo
ODOO_API_KEY=your_api_key_here

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# n8n Webhooks
N8N_WEBHOOK_URL=https://n8n.insightpulseai.com/webhook

# MCP Coordinator
MCP_API_URL=https://mcp.insightpulseai.com
```

**Odoo (`odoo.conf`)**:
```ini
[options]
# Allow CORS for Next.js frontend
proxy_mode = True
cors = *
```

## Implementation Steps

### Step 1: Create Odoo API Module

```bash
# Create ipai_platform_api module
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo/addons/ipai
./scaffold.sh ipai_platform_api "Platform API Bridge"
```

**Module structure**:
```python
# addons/ipai/ipai_platform_api/controllers/main.py
from odoo import http
from odoo.http import request

class PlatformAPIController(http.Controller):

    @http.route('/api/platform/features', type='json', auth='public', methods=['POST'], csrf=False)
    def get_features(self):
        """Return features for Next.js landing page"""
        Feature = request.env['website.feature'].sudo()
        features = Feature.search([('published', '=', True)])
        return {
            'features': [{
                'id': f.id,
                'title': f.name,
                'description': f.description,
                'icon': f.icon_url,
            } for f in features]
        }

    @http.route('/api/platform/deployments', type='json', auth='user', methods=['POST'], csrf=False)
    def trigger_deployment(self, branch, environment):
        """Trigger deployment via n8n"""
        # Call n8n webhook
        # Queue MCP job
        # Update Odoo deployment record
        return {'status': 'queued', 'deployment_id': 123}
```

### Step 2: Update Next.js App with API Integration

```typescript
// app/api/features/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  const odooUrl = process.env.NEXT_PUBLIC_ODOO_URL

  const response = await fetch(`${odooUrl}/api/platform/features`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'call',
      params: {}
    })
  })

  const data = await response.json()
  return NextResponse.json(data.result)
}
```

```tsx
// app/page.tsx - Update features section
'use client'
import { useEffect, useState } from 'react'

export default function Page() {
  const [features, setFeatures] = useState([])

  useEffect(() => {
    fetch('/api/features')
      .then(res => res.json())
      .then(data => setFeatures(data.features))
  }, [])

  return (
    // ... existing code
    <section id="features">
      {features.map(feature => (
        <Card key={feature.id}>
          <CardTitle>{feature.title}</CardTitle>
          <CardDescription>{feature.description}</CardDescription>
        </Card>
      ))}
    </section>
  )
}
```

### Step 3: Deploy Integration

**Vercel Deployment**:
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy Next.js app
cd templates/saas-landing
vercel --prod

# Configure environment variables in Vercel dashboard
```

**Odoo Module Installation**:
```bash
# SSH to Odoo server
ssh root@178.128.112.214

# Install ipai_platform_api
docker exec odoo-web-1 odoo -d odoo -i ipai_platform_api --stop-after-init
docker restart odoo-web-1
```

**n8n Workflow Setup**:
1. Create workflow: `Platform Deployment Trigger`
2. Add webhook trigger: `/webhook/deploy`
3. Add nodes: Odoo API call → MCP queue → Slack notification

### Step 4: Configure Reverse Proxy (nginx)

```nginx
# /etc/nginx/sites-available/insightpulseai.com.conf

# Next.js frontend (Vercel)
server {
    server_name insightpulseai.com www.insightpulseai.com;

    location / {
        proxy_pass https://saas-landing-production.vercel.app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Odoo backend
server {
    server_name erp.insightpulseai.com;

    location / {
        proxy_pass http://localhost:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API endpoints accessible from frontend
    location /api/platform/ {
        proxy_pass http://localhost:8069;
        add_header Access-Control-Allow-Origin *;
    }
}
```

## Testing Integration

```bash
# Test Odoo API endpoints
curl -X POST https://erp.insightpulseai.com/api/platform/features \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{}}'

# Test Next.js API route
curl https://insightpulseai.com/api/features

# Test deployment trigger
curl -X POST https://n8n.insightpulseai.com/webhook/deploy \
  -H "Content-Type: application/json" \
  -d '{"branch":"main","environment":"production"}'
```

## Benefits of This Integration

1. **Separation of Concerns**: Next.js handles public marketing, Odoo handles business logic
2. **Performance**: Static generation for landing pages, dynamic for dashboard
3. **CMS Control**: Non-technical users manage content in Odoo CMS
4. **Single Source of Truth**: Odoo database is canonical for all data
5. **Platform Kit Orchestration**: n8n/MCP handle complex workflows
6. **Scalability**: Vercel CDN for frontend, Odoo for backend

## Next Steps

1. **Create `ipai_platform_api` Odoo module**
2. **Add API routes to Next.js app**
3. **Configure environment variables**
4. **Deploy to Vercel**
5. **Set up n8n workflows**
6. **Configure nginx reverse proxy**
7. **Test end-to-end integration**

Would you like me to implement any of these steps?
