# Vercel Integrations

> **Generated:** 2026-01-21
> **Organization:** insightpulseai
> **Purpose:** Frontend deployments and edge functions for Odoo CE stack

---

## Installed Integrations

| Integration | Category | Purpose | Billing |
|-------------|----------|---------|---------|
| **Supabase** | Database | PostgreSQL, Auth, Realtime | Via Vercel |
| **Inngest** | DevTools | Event-driven workflows | Via Vercel |
| **Autonoma AI** | Testing | E2E test automation | Via Vercel |
| **Groq** | AI | Fast LLM inference | Via Vercel |
| **Neon** | Database | Serverless Postgres (backup) | Via Vercel |
| **GitHub Issues** | Productivity | Issue tracking sync | Free |
| **Auth0** | Authentication | Alternative OAuth provider | Via Vercel |
| **Slack** | Messaging | Notifications and alerts | Free |

---

## Supabase Integration

### Configuration

The Supabase integration provides:
- Automatic environment variable injection
- Database branch previews
- Edge Function deployments

### Environment Variables (Auto-Injected)

```bash
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ... (production only)
```

### Usage in Vercel Projects

```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
)
```

---

## Inngest Integration

### Purpose

Inngest provides event-driven background jobs for:
- Odoo webhook processing
- Long-running data sync tasks
- Scheduled catalog updates

### Configuration

```typescript
// inngest/client.ts
import { Inngest } from 'inngest'

export const inngest = new Inngest({
  id: 'odoo-ce-stack',
  eventKey: process.env.INNGEST_EVENT_KEY,
})
```

### Example: Odoo Module Sync

```typescript
// inngest/functions/sync-odoo-modules.ts
import { inngest } from '../client'
import { supabase } from '@/lib/supabase'

export const syncOdooModules = inngest.createFunction(
  { id: 'sync-odoo-modules', name: 'Sync Odoo Modules to Supabase' },
  { cron: '0 */6 * * *' }, // Every 6 hours
  async ({ step }) => {
    // Fetch modules from Odoo
    const modules = await step.run('fetch-modules', async () => {
      const response = await fetch(`${process.env.ODOO_URL}/jsonrpc`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: {
            service: 'object',
            method: 'execute_kw',
            args: [
              process.env.ODOO_DATABASE,
              2, // uid
              process.env.ODOO_PASSWORD,
              'ir.module.module',
              'search_read',
              [[['state', '=', 'installed']]],
              { fields: ['name', 'shortdesc', 'category_id', 'installed_version'] },
            ],
          },
          id: 1,
        }),
      })
      return response.json()
    })

    // Sync to Supabase
    await step.run('sync-to-supabase', async () => {
      const { error } = await supabase
        .from('odoo_modules')
        .upsert(
          modules.result.map((m: any) => ({
            module_name: m.name,
            display_name: m.shortdesc,
            is_installed: true,
            installed_version: m.installed_version,
            last_synced_at: new Date().toISOString(),
          })),
          { onConflict: 'module_name' }
        )
      if (error) throw error
    })

    return { synced: modules.result.length }
  }
)
```

---

## Groq Integration

### Purpose

Groq provides fast LLM inference for:
- AI-assisted features in IPAI modules
- Natural language processing
- Code generation helpers

### Configuration

```typescript
// lib/groq.ts
import Groq from 'groq-sdk'

export const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY,
})
```

### Example: Document Classification

```typescript
// api/classify-document.ts
import { groq } from '@/lib/groq'

export async function classifyDocument(content: string) {
  const response = await groq.chat.completions.create({
    model: 'mixtral-8x7b-32768',
    messages: [
      {
        role: 'system',
        content: 'Classify the following document into categories: invoice, receipt, contract, or other.',
      },
      { role: 'user', content },
    ],
    temperature: 0.1,
  })

  return response.choices[0].message.content
}
```

---

## Autonoma AI Integration

### Purpose

Automated end-to-end testing for:
- Odoo web interface testing
- API endpoint validation
- User workflow testing

### Configuration

```typescript
// autonoma.config.ts
export default {
  baseUrl: process.env.ODOO_URL,
  tests: [
    {
      name: 'Login Flow',
      steps: [
        { action: 'navigate', url: '/web/login' },
        { action: 'fill', selector: '#login', value: 'admin' },
        { action: 'fill', selector: '#password', value: '{{ODOO_PASSWORD}}' },
        { action: 'click', selector: 'button[type="submit"]' },
        { action: 'assert', selector: '.o_home_menu', exists: true },
      ],
    },
  ],
}
```

---

## Slack Integration

### Purpose

Notifications for:
- Deployment status
- CI/CD pipeline results
- Error alerts

### Webhook Configuration

```bash
# .env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../...
SLACK_CHANNEL=#odoo-deployments
```

### Example: Deployment Notification

```typescript
// lib/slack.ts
export async function notifyDeployment(status: 'success' | 'failure', message: string) {
  await fetch(process.env.SLACK_WEBHOOK_URL!, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      channel: process.env.SLACK_CHANNEL,
      attachments: [
        {
          color: status === 'success' ? '#36a64f' : '#ff0000',
          title: `Odoo Deployment ${status.toUpperCase()}`,
          text: message,
          ts: Math.floor(Date.now() / 1000),
        },
      ],
    }),
  })
}
```

---

## Vercel Projects

| Project | Purpose | URL |
|---------|---------|-----|
| `control-room` | Admin dashboard | control-room.vercel.app |
| `mcp-jobs` | Job orchestration UI | v0-open-in-v0-aw4uzb0sw-tbwa.vercel.app |
| `ipai-docs` | Documentation site | docs.insightpulseai.com |

---

## CI/CD Integration

### vercel.json

```json
{
  "version": 2,
  "builds": [
    { "src": "apps/control-room/**", "use": "@vercel/next" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "apps/control-room/api/$1" }
  ],
  "env": {
    "ODOO_URL": "@odoo_url",
    "SUPABASE_URL": "@supabase_url",
    "SUPABASE_ANON_KEY": "@supabase_anon_key"
  }
}
```

### GitHub Actions Integration

```yaml
# .github/workflows/vercel-deploy.yml
name: Vercel Deploy

on:
  push:
    branches: [main]
    paths:
      - 'apps/control-room/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: apps/control-room
```

---

## Environment Setup

### Required Secrets in Vercel

| Secret | Source |
|--------|--------|
| `ODOO_URL` | Production Odoo URL |
| `ODOO_DATABASE` | Database name |
| `ODOO_PASSWORD` | Admin password |
| `SUPABASE_URL` | Auto-injected |
| `SUPABASE_ANON_KEY` | Auto-injected |
| `GROQ_API_KEY` | Groq dashboard |
| `SLACK_WEBHOOK_URL` | Slack app settings |
| `INNGEST_EVENT_KEY` | Inngest dashboard |

---

*See [PROGRAMMATIC_CONFIG_PLAN.md](../PROGRAMMATIC_CONFIG_PLAN.md) for full CI/CD configuration*
