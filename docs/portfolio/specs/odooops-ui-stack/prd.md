# OdooOps UI Stack — Product Requirements Document

**Created**: 2026-02-12
**Spec Kit**: odooops-ui-stack
**Status**: Draft

---

## Executive Summary

**Product**: OdooOps Console UI — Next.js application with Supabase UI Library and Platform Kit

**Purpose**: Modern web console for OdooOps platform (Odoo.sh Next) providing deployment management, environment monitoring, and embedded Supabase administration.

**Users**: Development teams, DevOps engineers, system administrators managing Odoo deployments

**Success Metrics**:
- Time to first deployment: <5 minutes
- Platform Kit load time: <2s
- User satisfaction: ≥90% (NPS)
- Zero-downtime deployments: 99.9%

---

## Product Context

### What Exists
- ✅ OdooOps Platform spec (spec/odoo-sh-next/)
- ✅ Browser automation pack (Playwright E2E + Chrome extension mode)
- ✅ Agent skills (odooops-deploy, odooops-test)
- ✅ Supabase project (`spdtwktxdalcfigzeqrz`)
- ✅ DigitalOcean infrastructure (178.128.112.214)
- ✅ Cloudflare DNS + nginx routing

### What's Needed
- 🎯 OdooOps Console UI (Next.js + Supabase UI blocks)
- 🎯 Platform Kit integration (embedded Supabase management)
- 🎯 Modern auth (Supabase SSR)
- 🎯 OdooOps API client (deployments, environments, tests)
- 🎯 Routing architecture (Cloudflare + nginx)
- 🎯 Notification adapter (Zoho SMTP/API)

---

## User Stories

### Development Teams

**Story 1**: Create Preview Environment
```
As a developer
When I open a pull request
I want an automatic preview environment
So that I can test changes before merging
```
**Acceptance Criteria**:
- PR → automatic preview environment creation
- Environment URL in PR comment
- E2E tests run automatically
- Environment destroyed after PR closes

**Story 2**: Deploy to Staging
```
As a developer
When I merge to staging branch
I want automatic staging deployment
So that QA can validate before production
```
**Acceptance Criteria**:
- Merge → automatic staging deploy
- Health checks pass before marking complete
- E2E tests required for promotion
- Deployment notifications via Zoho

**Story 3**: Promote to Production
```
As a release manager
When staging tests pass
I want to promote to production with approval
So that releases are controlled and validated
```
**Acceptance Criteria**:
- Approval workflow with validation gates
- Zero-downtime deployment
- Automatic rollback on failure
- Audit trail of deployments

### DevOps Engineers

**Story 4**: Monitor Environment Health
```
As a DevOps engineer
When I view the console dashboard
I want real-time environment health metrics
So that I can proactively address issues
```
**Acceptance Criteria**:
- Real-time metrics dashboard
- CPU/memory/disk usage graphs
- Error rate and response time metrics
- Alert configuration UI

**Story 5**: View Deployment Logs
```
As a DevOps engineer
When a deployment fails
I want to view build and runtime logs
So that I can debug the issue
```
**Acceptance Criteria**:
- Searchable log viewer
- Log streaming in real-time
- Filter by level/service/time range
- Export logs to file

**Story 6**: Manage Database with Platform Kit
```
As a DevOps engineer
When I need to query or modify the database
I want embedded Supabase management
So that I don't leave the OdooOps console
```
**Acceptance Criteria**:
- Full Supabase dashboard embedded
- Database table browser
- SQL editor with autocomplete
- Schema migration tools
- Auth user management
- Storage file browser

### System Administrators

**Story 7**: Manage User Access
```
As a system administrator
When I need to grant team access
I want role-based permission management
So that users have appropriate access levels
```
**Acceptance Criteria**:
- Role creation and assignment
- Resource-level permissions
- OAuth provider configuration
- Audit log of access changes

**Story 8**: Configure Notifications
```
As a system administrator
When deployments or errors occur
I want email notifications via Zoho
So that the team is alerted immediately
```
**Acceptance Criteria**:
- Email notification configuration
- Deployment success/failure alerts
- Error threshold alerts
- Custom alert rules

---

## Features

### 1. Authentication & Authorization

**Requirements**:
- Multi-factor authentication (MFA)
- OAuth providers: Google, GitHub, Microsoft
- Magic link authentication
- Role-based access control (RBAC)
- Session management with Supabase SSR

**Implementation**:
```typescript
// lib/supabase/server.ts
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export function createClient() {
  const cookieStore = cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value
        },
      },
    }
  )
}
```

**UI Components**:
- Login page with Supabase Auth UI
- MFA setup wizard
- OAuth provider buttons
- Password reset flow

### 2. Dashboard

**Requirements**:
- Environment overview (preview/staging/prod)
- Recent deployments timeline
- Health metrics summary
- Quick action buttons

**Metrics**:
- Active environments count
- Deployment success rate (7d)
- Average deployment time
- Error rate by environment

**UI Layout**:
```
┌─────────────────────────────────────────┐
│ OdooOps Console          [User Menu]    │
├─────────────────────────────────────────┤
│ Environments │ Deployments │ Tests │ ... │
├─────────────────────────────────────────┤
│                                          │
│  📊 Active Environments: 12              │
│  ✅ Success Rate (7d): 95.2%             │
│  ⚡ Avg Deploy Time: 4m 32s              │
│  🚨 Error Rate: 0.3%                     │
│                                          │
│  Recent Deployments                      │
│  ┌──────────────────────────────────┐   │
│  │ feat/new-module → preview        │   │
│  │ ✅ 2 minutes ago                 │   │
│  ├──────────────────────────────────┤   │
│  │ main → production                │   │
│  │ ✅ 1 hour ago                    │   │
│  └──────────────────────────────────┘   │
│                                          │
└─────────────────────────────────────────┘
```

### 3. Deployment Management

**Requirements**:
- Create deployment from branch
- View deployment status and logs
- Promote between environments
- Rollback to previous version

**API Integration**:
```typescript
// lib/odooops/api.ts
export async function createDeployment(params: {
  branch: string
  stage: 'preview' | 'staging' | 'prod'
}) {
  const response = await fetch(`${ODOOOPS_API_BASE}/deployments`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${ODOOOPS_TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  })
  return response.json()
}
```

**UI Components**:
- Deployment creation form
- Deployment list with status
- Log viewer with search
- Promotion approval modal

### 4. Environment Management

**Requirements**:
- List all environments (preview/staging/prod)
- View environment details (URL, commit SHA, status)
- Start/stop/restart environments
- Destroy ephemeral previews

**Environment States**:
- `building` - Environment being built
- `ready` - Environment available
- `error` - Build or runtime error
- `stopped` - Environment paused
- `destroying` - Cleanup in progress

**UI Components**:
- Environment list with filters
- Environment detail page
- Action buttons (restart, destroy)
- Resource usage graphs

### 5. Test Management

**Requirements**:
- View E2E test results
- Trigger manual test runs
- Download test artifacts (traces, videos, screenshots)
- Test history and trends

**Test Result Display**:
```
┌─────────────────────────────────────────┐
│ E2E Test Results                         │
├─────────────────────────────────────────┤
│ Total:  45 tests                         │
│ Passed: 43 ✅                            │
│ Failed: 2  ❌                            │
│ Duration: 2m 34s                         │
│                                          │
│ Failed Tests:                            │
│ • auth.spec.ts › login flow              │
│   Artifacts: trace.zip | screenshot.png  │
│ • dashboard.spec.ts › chart rendering    │
│   Artifacts: trace.zip | video.webm      │
└─────────────────────────────────────────┘
```

### 6. Platform Kit Integration

**Requirements**:
- Embed full Supabase management console
- Access database tables and queries
- Manage auth users and providers
- Browse storage files
- View logs and performance metrics
- Manage secrets and environment variables

**Implementation**:
```typescript
// app/(dashboard)/platform/page.tsx
import { PlatformKit } from '@supabase/platform-kit'

export default function PlatformPage() {
  return (
    <PlatformKit
      projectRef="spdtwktxdalcfigzeqrz"
      accessToken={process.env.SUPABASE_ACCESS_TOKEN}
      features={[
        'database',
        'auth',
        'storage',
        'secrets',
        'logs',
        'performance'
      ]}
    />
  )
}
```

**Features Available**:
- **Database**: Table browser, SQL editor, schema migrations
- **Auth**: User management, provider config, policies
- **Storage**: File browser, bucket management, upload/download
- **Secrets**: Environment variables, API keys, tokens
- **Logs**: Query logs, error tracking, performance monitoring
- **Performance**: Query analytics, slow query detection, optimization

### 7. Notifications

**Requirements**:
- Email notifications via Zoho SMTP
- Deployment success/failure alerts
- Error threshold alerts
- Custom notification rules

**Zoho Integration**:
```typescript
// lib/notifications/zoho.ts
import nodemailer from 'nodemailer'

const transporter = nodemailer.createTransport({
  host: 'smtp.zoho.com',
  port: 587,
  secure: false,
  auth: {
    user: process.env.ZOHO_EMAIL,
    pass: process.env.ZOHO_PASSWORD
  }
})

export async function sendDeploymentNotification(deployment: Deployment) {
  await transporter.sendMail({
    from: 'ops@insightpulseai.com',
    to: deployment.owner_email,
    subject: `Deployment ${deployment.status}: ${deployment.name}`,
    html: `
      <h1>Deployment ${deployment.status}</h1>
      <p>Environment: ${deployment.environment_url}</p>
      <p>Commit: ${deployment.commit_sha}</p>
      <p>Duration: ${deployment.duration}s</p>
    `
  })
}
```

### 8. Settings

**Requirements**:
- User profile management
- Team member management
- Project configuration
- Billing and usage

**Settings Pages**:
- `/settings/profile` - User details and preferences
- `/settings/team` - Team members and roles
- `/settings/project` - Project config and integrations
- `/settings/billing` - Usage and billing (future)

---

## Technical Architecture

### Directory Structure
```
templates/odooops-console/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   └── callback/
│   ├── (dashboard)/
│   │   ├── page.tsx              # Dashboard
│   │   ├── deployments/
│   │   │   ├── page.tsx          # Deployment list
│   │   │   └── [id]/page.tsx     # Deployment detail
│   │   ├── environments/
│   │   │   ├── page.tsx          # Environment list
│   │   │   └── [id]/page.tsx     # Environment detail
│   │   ├── tests/
│   │   │   ├── page.tsx          # Test runs list
│   │   │   └── [id]/page.tsx     # Test run detail
│   │   ├── platform/
│   │   │   └── page.tsx          # Platform Kit
│   │   └── settings/
│   │       ├── profile/page.tsx
│   │       ├── team/page.tsx
│   │       └── project/page.tsx
│   └── api/
│       ├── odooops/
│       │   ├── deployments/route.ts
│       │   ├── environments/route.ts
│       │   └── tests/route.ts
│       └── notifications/
│           └── send/route.ts
├── components/
│   ├── ui/                       # shadcn components
│   ├── supabase/                 # Supabase UI Library blocks
│   └── platform-kit/             # Platform Kit wrapper
├── lib/
│   ├── supabase/
│   │   ├── client.ts
│   │   ├── server.ts
│   │   └── middleware.ts
│   ├── odooops/
│   │   └── api.ts
│   └── notifications/
│       └── zoho.ts
└── public/
```

### Routing Architecture
```yaml
# Cloudflare DNS + Routing
registry.insightpulseai.com:
  target: squarespace
  ssl: full
  cache: aggressive
  purpose: Marketing, docs, SEO

ops.insightpulseai.com:
  target: vercel
  ssl: full
  cache: bypass
  purpose: OdooOps Console (Next.js)

erp.insightpulseai.com:
  target: 178.128.112.214:8069
  ssl: full
  cache: bypass
  proxy: nginx
  purpose: Odoo 19 CE

api.insightpulseai.com:
  target: supabase-edge-functions
  ssl: full
  cache: bypass
  purpose: Optional API gateway

obs.insightpulseai.com:
  target: observability-dashboards
  ssl: full
  cache: bypass
  purpose: Superset/Grafana (optional)
```

### nginx Configuration
```nginx
# /etc/nginx/sites-available/erp.insightpulseai.com
server {
    server_name erp.insightpulseai.com;

    location / {
        proxy_pass http://localhost:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Integration Points

### With Existing Work

**Browser Automation Pack** → Test UI Components
- Playwright specs for console features
- E2E tests for deployment workflows
- Visual regression testing

**Agent Skills** → UI Deployment Automation
- `/odooops-ui/deploy` - Deploy console to Vercel
- `/odooops-ui/test` - Run console E2E tests
- `/odooops-ui/config` - Configure environment variables

**OdooOps API** → Backend Integration
- Create/manage deployments
- Environment lifecycle operations
- Test execution and results

**Supabase** → Database + Auth + Storage
- PostgreSQL database (already configured)
- Auth users and sessions
- Storage for artifacts and logs

---

## Success Criteria

### Must Have (MVP)
- ✅ Console accessible at `ops.insightpulseai.com`
- ✅ Supabase SSR auth working (login → dashboard → logout)
- ✅ Platform Kit embedded and functional
- ✅ OdooOps API integrated (create env, run tests, view logs)
- ✅ Zoho notifications sending successfully

### Should Have (V1)
- ✅ Deployment list and detail pages
- ✅ Environment management UI
- ✅ Test results display with artifacts
- ✅ Dashboard with metrics
- ✅ E2E tests passing (Playwright suite)

### Could Have (V2)
- 🔄 Real-time deployment updates (WebSocket)
- 🔄 Advanced filtering and search
- 🔄 Custom dashboards
- 🔄 Billing and usage tracking
- 🔄 API documentation

---

## Non-Goals

**Out of Scope for MVP**:
- Mobile app (web-only initially)
- Advanced analytics (basic metrics only)
- Multi-tenancy (single project focus)
- Marketplace/plugins (future)
- AI-powered insights (future)

---

## Timeline

### Phase 1: Foundation (Week 1)
- Scaffold Next.js console with Supabase template
- Install Supabase UI blocks
- Implement SSR auth
- Basic dashboard layout

### Phase 2: Platform Kit (Week 2)
- Integrate Platform Kit component
- Test embedded Supabase management
- Configure project reference and access token

### Phase 3: API Integration (Week 3)
- Create OdooOps API client
- Implement deployment management UI
- Implement environment management UI
- Implement test results UI

### Phase 4: Notifications (Week 4)
- Zoho SMTP adapter
- Deployment notifications
- Error alerts
- Custom notification rules

### Phase 5: Testing & Deployment (Week 5)
- E2E tests for console features
- Deploy to Vercel
- Configure Cloudflare routing
- Production validation

---

## Metrics & Monitoring

### Key Metrics
- **Deployment Frequency**: Deployments per day
- **Deployment Success Rate**: Successful deploys / total deploys
- **Mean Time to Deploy (MTTD)**: Average deployment duration
- **Mean Time to Recovery (MTTR)**: Average time to fix failed deploy
- **Environment Uptime**: Percentage uptime per environment

### Monitoring
- **Vercel Analytics**: Page views, performance, errors
- **Supabase Logs**: Database queries, auth events, edge function logs
- **OdooOps API**: Deployment API calls, error rates, response times
- **Zoho Delivery**: Email sent, delivery rate, bounce rate

---

**Approval**: This PRD defines the OdooOps Console UI requirements.
**Next Steps**: Implementation plan in `plan.md`.
