# Vercel Stack Details

> **Purpose**: Vercel deployment configuration for LLM agents.
> **Team**: InsightPulse AI

---

## Connected Projects

### Active Projects

| Project | Repository | Domain | Purpose |
|---------|------------|--------|---------|
| `shelf-nu` | `jgtolentino/shelf.nu` | shelf.insightpulseai.net | Asset management |
| `scout-dashboard` | `jgtolentino/scout-dashboard` | scout.insightpulseai.net | Retail analytics |
| `tbwa-agency-dash` | `jgtolentino/tbwa-agency-dash` | agency.insightpulseai.net | Agency dashboard |

### Project Configuration Pattern

All Vercel projects follow this pattern:

```
Framework: Next.js 14+
Node Version: 20.x
Build Command: pnpm build
Output Directory: .next
Install Command: pnpm install
```

---

## Supabase Integration

All frontend projects connect to the same Supabase instance:

| Environment Variable | Value |
|---------------------|-------|
| `NEXT_PUBLIC_SUPABASE_URL` | `https://spdtwktxdalcfigzeqrz.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | (from Supabase dashboard) |
| `SUPABASE_SERVICE_ROLE_KEY` | (for server-side only) |

### Data Access Pattern

```
Vercel Edge → Supabase PostgREST API
                    ↓
            RLS-protected tables
                    ↓
            kb.*, agent_mem.*, ops_advisor.*
```

---

## Environment Variables

### Common Variables

| Variable | Description | Where Set |
|----------|-------------|-----------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase API URL | Project Settings |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Anon key for client | Project Settings |
| `SUPABASE_SERVICE_ROLE_KEY` | Service key for server | Project Settings |
| `OPENAI_API_KEY` | For embeddings | Project Settings |

### Project-Specific Variables

**shelf-nu**:
```env
NEXT_PUBLIC_APP_NAME=Shelf
NEXT_PUBLIC_ODOO_URL=https://erp.insightpulseai.net
```

**scout-dashboard**:
```env
NEXT_PUBLIC_APP_NAME=Scout
NEXT_PUBLIC_SUPERSET_URL=https://bi.insightpulseai.net
```

**tbwa-agency-dash**:
```env
NEXT_PUBLIC_APP_NAME=Agency Dashboard
NEXT_PUBLIC_TENANT_ID=tbwa
```

---

## Deployment Configuration

### Production Deployments

| Setting | Value |
|---------|-------|
| Production Branch | `main` |
| Preview Branches | All PR branches |
| Root Directory | `/` (default) |
| Build Cache | Enabled |

### Domain Configuration

| Project | Production Domain | Preview Pattern |
|---------|-------------------|-----------------|
| shelf-nu | shelf.insightpulseai.net | shelf-*-team.vercel.app |
| scout-dashboard | scout.insightpulseai.net | scout-*-team.vercel.app |
| tbwa-agency-dash | agency.insightpulseai.net | agency-*-team.vercel.app |

---

## Edge Functions

### Common Edge Patterns

```typescript
// Middleware for auth
import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs';

export async function middleware(req: NextRequest) {
  const res = NextResponse.next();
  const supabase = createMiddlewareClient({ req, res });
  await supabase.auth.getSession();
  return res;
}
```

### API Routes

| Route Pattern | Purpose | Auth Required |
|---------------|---------|---------------|
| `/api/health` | Health check | No |
| `/api/auth/*` | Auth callbacks | No |
| `/api/v1/*` | Protected API | Yes |
| `/api/webhooks/*` | External webhooks | Signature |

---

## Build & Deploy Commands

### CLI Operations

```bash
# Link project
vercel link --project=shelf-nu

# Deploy preview
vercel deploy

# Deploy production
vercel deploy --prod

# View deployments
vercel ls

# View logs
vercel logs shelf-nu --follow

# Promote preview to production
vercel promote <deployment-url>
```

### Environment Management

```bash
# List env vars
vercel env ls

# Add env var
vercel env add NEXT_PUBLIC_FEATURE_FLAG

# Pull env to local
vercel env pull .env.local
```

---

## Caching Configuration

### Edge Caching

```typescript
// In API routes
export const config = {
  runtime: 'edge',
};

export default async function handler(req: Request) {
  return new Response(data, {
    headers: {
      'Cache-Control': 's-maxage=60, stale-while-revalidate=3600',
    },
  });
}
```

### ISR (Incremental Static Regeneration)

```typescript
// In page components
export const revalidate = 60; // Revalidate every 60 seconds
```

---

## Monitoring & Analytics

### Web Analytics

Enabled on all projects:
- Page views
- Unique visitors
- Top pages
- Referrers

### Speed Insights

Metrics tracked:
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Time to First Byte (TTFB)
- Cumulative Layout Shift (CLS)

---

## Integration with CI/CD

### GitHub Actions Trigger

```yaml
# .github/workflows/vercel-deploy.yml
name: Vercel Deploy
on:
  push:
    branches: [main]
    paths:
      - 'apps/web/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

---

## Troubleshooting

### Build Failures

```bash
# Check build logs
vercel logs <deployment-url> --since 1h

# Test build locally
vercel build

# Check for env var issues
vercel env ls production
```

### Runtime Errors

```bash
# View function logs
vercel logs <deployment-url> --output json | jq '.[] | select(.type == "error")'

# Check edge function size
vercel inspect <deployment-url>
```

### Domain Issues

```bash
# Verify DNS
dig shelf.insightpulseai.net

# Check SSL cert
openssl s_client -connect shelf.insightpulseai.net:443 -servername shelf.insightpulseai.net

# Force SSL renewal
vercel certs issue shelf.insightpulseai.net
```

---

## Project Inventory Query

For LLM agents to discover Vercel projects:

```sql
-- Query ops_kg for Vercel nodes
SELECT n.*, e.predicate, n2.label as related
FROM kg.nodes n
LEFT JOIN kg.edges e ON n.id = e.from_node
LEFT JOIN kg.nodes n2 ON e.to_node = n2.id
WHERE n.kind = 'vercel_project'
ORDER BY n.label;
```

This data is populated by the infrastructure discovery job.
