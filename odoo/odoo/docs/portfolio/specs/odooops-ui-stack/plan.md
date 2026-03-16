# OdooOps UI Stack — Implementation Plan

**Created**: 2026-02-12
**Spec Kit**: odooops-ui-stack
**Status**: Ready for Implementation

---

## Overview

**Objective**: Build OdooOps Console UI with Supabase UI Library, Platform Kit, SSR auth, and OdooOps API integration.

**Duration**: 5 weeks

**Team**: 1 full-stack developer

**Technology Stack**:
- Next.js 14 (App Router)
- TypeScript (strict mode)
- Tailwind CSS
- Supabase JS + SSR
- Platform Kit (@supabase/platform-kit)
- Supabase UI Library (shadcn registry)
- Zoho SMTP (nodemailer)

---

## Phase 1: Foundation (Week 1)

### Objectives
- Scaffold Next.js application
- Install and configure Supabase UI blocks
- Implement basic authentication
- Create dashboard layout

### Tasks

#### Task 1.1: Scaffold Next.js Console
**Duration**: 2 hours

```bash
# Use official Supabase Next.js template
npx create-next-app -e with-supabase templates/odooops-console
cd templates/odooops-console

# Install additional dependencies
pnpm add @supabase/platform-kit nodemailer
pnpm add -D @types/nodemailer

# Configure environment variables
cp .env.example .env.local
```

**Environment Variables**:
```env
NEXT_PUBLIC_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon_key>
SUPABASE_SERVICE_ROLE_KEY=<service_role_key>
SUPABASE_ACCESS_TOKEN=<access_token>
ODOOOPS_API_BASE=https://api.odooops.io
ODOOOPS_TOKEN=<odooops_token>
ODOOOPS_PROJECT_ID=<project_id>
ZOHO_EMAIL=ops@insightpulseai.com
ZOHO_PASSWORD=<zoho_password>
```

#### Task 1.2: Install Supabase UI Blocks
**Duration**: 3 hours

```bash
# Install shadcn CLI
pnpm add -D @shadcn/ui

# Initialize shadcn
pnpx shadcn-ui init

# Install Supabase UI blocks
pnpx shadcn-ui add button
pnpx shadcn-ui add card
pnpx shadcn-ui add input
pnpx shadcn-ui add label
pnpx shadcn-ui add table
pnpx shadcn-ui add badge
pnpx shadcn-ui add dialog
pnpx shadcn-ui add dropdown-menu
pnpx shadcn-ui add tabs
pnpx shadcn-ui add toast
```

**Directory Structure**:
```
components/
├── ui/                  # shadcn components
│   ├── button.tsx
│   ├── card.tsx
│   ├── input.tsx
│   └── ...
└── supabase/           # Supabase-specific UI
    ├── auth-form.tsx   # Login/signup form
    ├── avatar.tsx      # User avatar
    └── ...
```

#### Task 1.3: Implement SSR Auth
**Duration**: 4 hours

**Create Supabase Server Client**:
```typescript
// lib/supabase/server.ts
import { createServerClient, type CookieOptions } from '@supabase/ssr'
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
        set(name: string, value: string, options: CookieOptions) {
          try {
            cookieStore.set({ name, value, ...options })
          } catch (error) {
            // Handle cookie error
          }
        },
        remove(name: string, options: CookieOptions) {
          try {
            cookieStore.set({ name, value: '', ...options })
          } catch (error) {
            // Handle cookie error
          }
        },
      },
    }
  )
}
```

**Create Supabase Browser Client**:
```typescript
// lib/supabase/client.ts
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

**Create Middleware for Auth**:
```typescript
// middleware.ts
import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return request.cookies.get(name)?.value
        },
        set(name: string, value: string, options: CookieOptions) {
          request.cookies.set({ name, value, ...options })
          response = NextResponse.next({
            request: {
              headers: request.headers,
            },
          })
          response.cookies.set({ name, value, ...options })
        },
        remove(name: string, options: CookieOptions) {
          request.cookies.set({ name, value: '', ...options })
          response = NextResponse.next({
            request: {
              headers: request.headers,
            },
          })
          response.cookies.set({ name, value: '', ...options })
        },
      },
    }
  )

  await supabase.auth.getUser()

  return response
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
```

**Create Login Page**:
```typescript
// app/(auth)/login/page.tsx
import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'

export default async function LoginPage() {
  const supabase = createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (user) {
    redirect('/')
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <AuthForm />
    </div>
  )
}
```

#### Task 1.4: Create Dashboard Layout
**Duration**: 3 hours

**Dashboard Page**:
```typescript
// app/(dashboard)/page.tsx
import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import { DashboardMetrics } from '@/components/dashboard/metrics'
import { RecentDeployments } from '@/components/dashboard/recent-deployments'

export default async function DashboardPage() {
  const supabase = createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect('/login')
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      <DashboardMetrics />
      <RecentDeployments />
    </div>
  )
}
```

**Dashboard Layout with Navigation**:
```typescript
// app/(dashboard)/layout.tsx
import { Navbar } from '@/components/layout/navbar'
import { Sidebar } from '@/components/layout/sidebar'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <main className="p-8">{children}</main>
      </div>
    </div>
  )
}
```

### Deliverables
- ✅ Next.js application scaffolded
- ✅ Supabase UI blocks installed
- ✅ SSR auth implemented and tested
- ✅ Dashboard layout with navigation

### Validation
```bash
# Run development server
pnpm dev

# Test authentication flow
# 1. Navigate to http://localhost:3000
# 2. Redirect to /login (not authenticated)
# 3. Login with Supabase credentials
# 4. Redirect to dashboard
# 5. Logout
# 6. Redirect to /login

# Verify SSR
curl -I http://localhost:3000
# Should return 307 redirect to /login when not authenticated
```

---

## Phase 2: Platform Kit Integration (Week 2)

### Objectives
- Integrate Platform Kit component
- Configure Supabase project reference
- Test embedded management features
- Create Platform Kit wrapper component

### Tasks

#### Task 2.1: Install Platform Kit
**Duration**: 1 hour

```bash
# Install Platform Kit package
pnpm add @supabase/platform-kit

# Verify installation
pnpm list @supabase/platform-kit
```

#### Task 2.2: Create Platform Kit Page
**Duration**: 3 hours

```typescript
// app/(dashboard)/platform/page.tsx
import { PlatformKit } from '@supabase/platform-kit'
import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'

export default async function PlatformPage() {
  const supabase = createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect('/login')
  }

  return (
    <div className="h-screen">
      <PlatformKit
        projectRef="spdtwktxdalcfigzeqrz"
        accessToken={process.env.SUPABASE_ACCESS_TOKEN!}
        features={[
          'database',
          'auth',
          'storage',
          'secrets',
          'logs',
          'performance'
        ]}
      />
    </div>
  )
}
```

#### Task 2.3: Create Platform Kit Wrapper
**Duration**: 2 hours

```typescript
// components/platform-kit/wrapper.tsx
'use client'

import { PlatformKit as BasePlatformKit } from '@supabase/platform-kit'
import { useState, useEffect } from 'react'

export function PlatformKit({
  projectRef,
  accessToken,
  features,
}: {
  projectRef: string
  accessToken: string
  features: string[]
}) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p>Loading Platform Kit...</p>
      </div>
    )
  }

  return (
    <BasePlatformKit
      projectRef={projectRef}
      accessToken={accessToken}
      features={features}
    />
  )
}
```

#### Task 2.4: Add Navigation Item
**Duration**: 1 hour

```typescript
// components/layout/sidebar.tsx
const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Deployments', href: '/deployments', icon: RocketIcon },
  { name: 'Environments', href: '/environments', icon: ServerIcon },
  { name: 'Tests', href: '/tests', icon: CheckCircleIcon },
  { name: 'Platform', href: '/platform', icon: DatabaseIcon }, // New
  { name: 'Settings', href: '/settings', icon: SettingsIcon },
]
```

### Deliverables
- ✅ Platform Kit integrated
- ✅ Platform Kit page accessible at `/platform`
- ✅ All features working (database, auth, storage, etc.)
- ✅ Navigation updated

### Validation
```bash
# Run development server
pnpm dev

# Test Platform Kit
# 1. Login to console
# 2. Navigate to /platform
# 3. Verify Platform Kit loads
# 4. Test database table browser
# 5. Test SQL editor
# 6. Test auth user management
# 7. Test storage file browser
# 8. Test secrets management
# 9. Test logs viewer
# 10. Test performance metrics
```

---

## Phase 3: OdooOps API Integration (Week 3)

### Objectives
- Create OdooOps API client
- Implement deployment management UI
- Implement environment management UI
- Implement test results UI

### Tasks

#### Task 3.1: Create OdooOps API Client
**Duration**: 4 hours

```typescript
// lib/odooops/api.ts
const ODOOOPS_API_BASE = process.env.ODOOOPS_API_BASE!
const ODOOOPS_TOKEN = process.env.ODOOOPS_TOKEN!
const ODOOOPS_PROJECT_ID = process.env.ODOOOPS_PROJECT_ID!

async function fetchAPI(path: string, options?: RequestInit) {
  const response = await fetch(`${ODOOOPS_API_BASE}${path}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${ODOOOPS_TOKEN}`,
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`)
  }

  return response.json()
}

export async function createDeployment(params: {
  branch: string
  stage: 'preview' | 'staging' | 'prod'
}) {
  return fetchAPI(`/projects/${ODOOOPS_PROJECT_ID}/deployments`, {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

export async function getDeployments() {
  return fetchAPI(`/projects/${ODOOOPS_PROJECT_ID}/deployments`)
}

export async function getDeployment(id: string) {
  return fetchAPI(`/projects/${ODOOOPS_PROJECT_ID}/deployments/${id}`)
}

export async function getEnvironments() {
  return fetchAPI(`/projects/${ODOOOPS_PROJECT_ID}/envs`)
}

export async function getEnvironment(id: string) {
  return fetchAPI(`/projects/${ODOOOPS_PROJECT_ID}/envs/${id}`)
}

export async function destroyEnvironment(id: string) {
  return fetchAPI(`/projects/${ODOOOPS_PROJECT_ID}/envs/${id}`, {
    method: 'DELETE',
  })
}

export async function getTestRuns(envId: string) {
  return fetchAPI(`/projects/${ODOOOPS_PROJECT_ID}/envs/${envId}/tests`)
}

export async function getTestRun(envId: string, testId: string) {
  return fetchAPI(`/projects/${ODOOOPS_PROJECT_ID}/envs/${envId}/tests/${testId}`)
}
```

#### Task 3.2: Implement Deployment Management UI
**Duration**: 6 hours

**Deployment List Page**:
```typescript
// app/(dashboard)/deployments/page.tsx
import { getDeployments } from '@/lib/odooops/api'
import { DeploymentList } from '@/components/deployments/deployment-list'
import { CreateDeploymentButton } from '@/components/deployments/create-button'

export default async function DeploymentsPage() {
  const deployments = await getDeployments()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Deployments</h1>
        <CreateDeploymentButton />
      </div>
      <DeploymentList deployments={deployments} />
    </div>
  )
}
```

**Deployment Detail Page**:
```typescript
// app/(dashboard)/deployments/[id]/page.tsx
import { getDeployment } from '@/lib/odooops/api'
import { DeploymentHeader } from '@/components/deployments/deployment-header'
import { DeploymentLogs } from '@/components/deployments/deployment-logs'
import { DeploymentMetrics } from '@/components/deployments/deployment-metrics'

export default async function DeploymentDetailPage({
  params,
}: {
  params: { id: string }
}) {
  const deployment = await getDeployment(params.id)

  return (
    <div className="space-y-6">
      <DeploymentHeader deployment={deployment} />
      <DeploymentMetrics deployment={deployment} />
      <DeploymentLogs deployment={deployment} />
    </div>
  )
}
```

#### Task 3.3: Implement Environment Management UI
**Duration**: 4 hours

**Environment List Page**:
```typescript
// app/(dashboard)/environments/page.tsx
import { getEnvironments } from '@/lib/odooops/api'
import { EnvironmentList } from '@/components/environments/environment-list'

export default async function EnvironmentsPage() {
  const environments = await getEnvironments()

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Environments</h1>
      <EnvironmentList environments={environments} />
    </div>
  )
}
```

**Environment Detail Page**:
```typescript
// app/(dashboard)/environments/[id]/page.tsx
import { getEnvironment } from '@/lib/odooops/api'
import { EnvironmentHeader } from '@/components/environments/environment-header'
import { EnvironmentActions } from '@/components/environments/environment-actions'
import { EnvironmentMetrics } from '@/components/environments/environment-metrics'

export default async function EnvironmentDetailPage({
  params,
}: {
  params: { id: string }
}) {
  const environment = await getEnvironment(params.id)

  return (
    <div className="space-y-6">
      <EnvironmentHeader environment={environment} />
      <EnvironmentActions environment={environment} />
      <EnvironmentMetrics environment={environment} />
    </div>
  )
}
```

#### Task 3.4: Implement Test Results UI
**Duration**: 4 hours

**Test Runs List Page**:
```typescript
// app/(dashboard)/tests/page.tsx
import { getTestRuns } from '@/lib/odooops/api'
import { TestRunsList } from '@/components/tests/test-runs-list'

export default async function TestsPage({
  searchParams,
}: {
  searchParams: { envId?: string }
}) {
  const testRuns = searchParams.envId
    ? await getTestRuns(searchParams.envId)
    : []

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">E2E Test Runs</h1>
      <TestRunsList testRuns={testRuns} />
    </div>
  )
}
```

**Test Run Detail Page**:
```typescript
// app/(dashboard)/tests/[id]/page.tsx
import { getTestRun } from '@/lib/odooops/api'
import { TestRunHeader } from '@/components/tests/test-run-header'
import { TestRunResults } from '@/components/tests/test-run-results'
import { TestRunArtifacts } from '@/components/tests/test-run-artifacts'

export default async function TestRunDetailPage({
  params,
  searchParams,
}: {
  params: { id: string }
  searchParams: { envId: string }
}) {
  const testRun = await getTestRun(searchParams.envId, params.id)

  return (
    <div className="space-y-6">
      <TestRunHeader testRun={testRun} />
      <TestRunResults testRun={testRun} />
      <TestRunArtifacts testRun={testRun} />
    </div>
  )
}
```

### Deliverables
- ✅ OdooOps API client functional
- ✅ Deployment list and detail pages
- ✅ Environment list and detail pages
- ✅ Test runs list and detail pages
- ✅ All CRUD operations working

### Validation
```bash
# Run development server
pnpm dev

# Test deployment management
# 1. Navigate to /deployments
# 2. Create new deployment
# 3. View deployment list
# 4. Click deployment to view details
# 5. View deployment logs

# Test environment management
# 1. Navigate to /environments
# 2. View environment list
# 3. Click environment to view details
# 4. Restart environment
# 5. Destroy environment (preview only)

# Test test results
# 1. Navigate to /tests
# 2. Filter by environment
# 3. View test run details
# 4. Download test artifacts
```

---

## Phase 4: Notifications (Week 4)

### Objectives
- Implement Zoho SMTP adapter
- Create notification service
- Add deployment notifications
- Add error alerts

### Tasks

#### Task 4.1: Create Zoho SMTP Adapter
**Duration**: 3 hours

```typescript
// lib/notifications/zoho.ts
import nodemailer from 'nodemailer'

const transporter = nodemailer.createTransporter({
  host: 'smtp.zoho.com',
  port: 587,
  secure: false,
  auth: {
    user: process.env.ZOHO_EMAIL,
    pass: process.env.ZOHO_PASSWORD
  }
})

export async function sendEmail({
  to,
  subject,
  html,
}: {
  to: string | string[]
  subject: string
  html: string
}) {
  const info = await transporter.sendMail({
    from: process.env.ZOHO_EMAIL,
    to: Array.isArray(to) ? to.join(', ') : to,
    subject,
    html,
  })

  return info
}
```

#### Task 4.2: Create Notification Service
**Duration**: 4 hours

```typescript
// lib/notifications/service.ts
import { sendEmail } from './zoho'

export async function sendDeploymentNotification({
  deployment,
  recipients,
}: {
  deployment: Deployment
  recipients: string[]
}) {
  const status = deployment.status === 'success' ? '✅' : '❌'

  await sendEmail({
    to: recipients,
    subject: `${status} Deployment ${deployment.status}: ${deployment.name}`,
    html: `
      <h1>Deployment ${deployment.status}</h1>
      <p><strong>Environment:</strong> ${deployment.environment_url}</p>
      <p><strong>Branch:</strong> ${deployment.branch}</p>
      <p><strong>Commit:</strong> ${deployment.commit_sha}</p>
      <p><strong>Duration:</strong> ${deployment.duration}s</p>
      <p><a href="${deployment.deployment_url}">View Deployment</a></p>
    `
  })
}

export async function sendErrorAlert({
  error,
  context,
  recipients,
}: {
  error: Error
  context: Record<string, any>
  recipients: string[]
}) {
  await sendEmail({
    to: recipients,
    subject: `🚨 Error Alert: ${error.message}`,
    html: `
      <h1>Error Alert</h1>
      <p><strong>Message:</strong> ${error.message}</p>
      <p><strong>Stack:</strong><pre>${error.stack}</pre></p>
      <p><strong>Context:</strong><pre>${JSON.stringify(context, null, 2)}</pre></p>
    `
  })
}
```

#### Task 4.3: Integrate Notifications with API
**Duration**: 3 hours

```typescript
// app/api/odooops/deployments/route.ts
import { createDeployment } from '@/lib/odooops/api'
import { sendDeploymentNotification } from '@/lib/notifications/service'
import { createClient } from '@/lib/supabase/server'

export async function POST(request: Request) {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const body = await request.json()
  const deployment = await createDeployment(body)

  // Send notification
  await sendDeploymentNotification({
    deployment,
    recipients: [user.email!],
  })

  return Response.json(deployment)
}
```

#### Task 4.4: Add Notification Settings
**Duration**: 2 hours

```typescript
// app/(dashboard)/settings/notifications/page.tsx
import { NotificationSettings } from '@/components/settings/notification-settings'

export default function NotificationSettingsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Notification Settings</h1>
      <NotificationSettings />
    </div>
  )
}
```

### Deliverables
- ✅ Zoho SMTP adapter functional
- ✅ Notification service implemented
- ✅ Deployment notifications working
- ✅ Error alerts working
- ✅ Notification settings UI

### Validation
```bash
# Test Zoho SMTP
# 1. Create deployment via UI
# 2. Check email inbox for notification
# 3. Verify deployment success email
# 4. Trigger deployment failure
# 5. Verify deployment failure email

# Test error alerts
# 1. Simulate error in console
# 2. Verify error alert email sent
# 3. Check error details in email

# Test notification settings
# 1. Navigate to /settings/notifications
# 2. Enable/disable notifications
# 3. Add notification recipients
# 4. Save settings
# 5. Verify settings persisted
```

---

## Phase 5: Testing & Deployment (Week 5)

### Objectives
- Write E2E tests for console features
- Deploy to Vercel
- Configure Cloudflare routing
- Validate production deployment

### Tasks

#### Task 5.1: Write E2E Tests
**Duration**: 8 hours

```typescript
// tests/e2e/console/auth.spec.ts
import { test, expect } from '@playwright/test'

test('should login successfully', async ({ page }) => {
  await page.goto('http://localhost:3000')

  // Should redirect to login
  await expect(page).toHaveURL(/\/login/)

  // Fill login form
  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="password"]', 'password123')
  await page.click('[type="submit"]')

  // Should redirect to dashboard
  await expect(page).toHaveURL('/')
  await expect(page.locator('h1')).toContainText('Dashboard')
})

test('should logout successfully', async ({ page }) => {
  // Login first
  await page.goto('http://localhost:3000')
  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="password"]', 'password123')
  await page.click('[type="submit"]')

  // Logout
  await page.click('[data-testid="user-menu"]')
  await page.click('[data-testid="logout-button"]')

  // Should redirect to login
  await expect(page).toHaveURL(/\/login/)
})
```

```typescript
// tests/e2e/console/deployments.spec.ts
import { test, expect } from '@playwright/test'

test('should create deployment', async ({ page }) => {
  // Login
  await page.goto('http://localhost:3000')
  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="password"]', 'password123')
  await page.click('[type="submit"]')

  // Navigate to deployments
  await page.click('text=Deployments')
  await expect(page).toHaveURL('/deployments')

  // Create deployment
  await page.click('text=Create Deployment')
  await page.fill('[name="branch"]', 'feat/test-feature')
  await page.selectOption('[name="stage"]', 'preview')
  await page.click('[type="submit"]')

  // Should show deployment
  await expect(page.locator('text=feat/test-feature')).toBeVisible()
})

test('should view deployment logs', async ({ page }) => {
  // Login and navigate to deployment
  await page.goto('http://localhost:3000')
  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="password"]', 'password123')
  await page.click('[type="submit"]')
  await page.click('text=Deployments')

  // Click first deployment
  await page.click('[data-testid="deployment-item"]').first()

  // Should show logs
  await expect(page.locator('[data-testid="deployment-logs"]')).toBeVisible()
})
```

```typescript
// tests/e2e/console/platform-kit.spec.ts
import { test, expect } from '@playwright/test'

test('should load Platform Kit', async ({ page }) => {
  // Login
  await page.goto('http://localhost:3000')
  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="password"]', 'password123')
  await page.click('[type="submit"]')

  // Navigate to Platform
  await page.click('text=Platform')
  await expect(page).toHaveURL('/platform')

  // Wait for Platform Kit to load
  await page.waitForSelector('[data-testid="platform-kit"]', { timeout: 10000 })

  // Should show Platform Kit
  await expect(page.locator('[data-testid="platform-kit"]')).toBeVisible()
})
```

#### Task 5.2: Deploy to Vercel
**Duration**: 2 hours

```bash
# Install Vercel CLI
pnpm add -g vercel

# Login to Vercel
vercel login

# Deploy to production
cd templates/odooops-console
vercel --prod

# Set environment variables in Vercel dashboard
# - NEXT_PUBLIC_SUPABASE_URL
# - NEXT_PUBLIC_SUPABASE_ANON_KEY
# - SUPABASE_SERVICE_ROLE_KEY
# - SUPABASE_ACCESS_TOKEN
# - ODOOOPS_API_BASE
# - ODOOOPS_TOKEN
# - ODOOOPS_PROJECT_ID
# - ZOHO_EMAIL
# - ZOHO_PASSWORD
```

#### Task 5.3: Configure Cloudflare Routing
**Duration**: 2 hours

**Cloudflare DNS Configuration**:
```yaml
# DNS Records
ops.insightpulseai.com:
  type: CNAME
  target: cname.vercel-dns.com
  proxy: true
  ssl: full

erp.insightpulseai.com:
  type: A
  target: 178.128.112.214
  proxy: true
  ssl: full

registry.insightpulseai.com:
  type: CNAME
  target: domains.squarespace.com
  proxy: true
  ssl: full
```

**Cloudflare Page Rules**:
```yaml
# Cache rules
ops.insightpulseai.com/*:
  cache_level: bypass
  ssl: full

registry.insightpulseai.com/*:
  cache_level: aggressive
  ssl: full
  browser_cache_ttl: 14400

erp.insightpulseai.com/*:
  cache_level: bypass
  ssl: full
```

#### Task 5.4: Validate Production Deployment
**Duration**: 2 hours

**Validation Checklist**:
```bash
# 1. Verify DNS resolution
dig ops.insightpulseai.com
dig erp.insightpulseai.com
dig registry.insightpulseai.com

# 2. Verify SSL certificates
curl -I https://ops.insightpulseai.com
curl -I https://erp.insightpulseai.com

# 3. Verify console loads
curl https://ops.insightpulseai.com

# 4. Run E2E tests against production
BASE_URL=https://ops.insightpulseai.com pnpm test:e2e

# 5. Test auth flow
# - Navigate to https://ops.insightpulseai.com
# - Login with credentials
# - Verify dashboard loads
# - Verify Platform Kit loads
# - Logout

# 6. Test deployment creation
# - Create preview deployment
# - Verify environment created
# - Verify E2E tests run
# - Verify notification sent

# 7. Test environment management
# - View environment list
# - View environment details
# - Restart environment
# - Destroy environment

# 8. Test test results
# - View test runs
# - View test details
# - Download artifacts
```

### Deliverables
- ✅ E2E tests passing
- ✅ Console deployed to Vercel
- ✅ Cloudflare routing configured
- ✅ Production validation complete
- ✅ All features working in production

### Validation
Production deployment checklist completed successfully.

---

## Rollout Plan

### Rollout Stages

**Stage 1: Internal Testing (Week 5, Days 1-2)**
- Deploy to Vercel preview environment
- Run E2E tests
- Manual testing by development team
- Bug fixes and refinements

**Stage 2: Beta Release (Week 5, Days 3-4)**
- Deploy to production
- Enable for internal users only
- Collect feedback
- Monitor errors and performance

**Stage 3: General Availability (Week 5, Day 5)**
- Open to all users
- Announce release
- Provide documentation and onboarding
- Monitor adoption and usage

### Success Metrics

**Week 1 After Launch**:
- User adoption: ≥20 active users
- Deployment frequency: ≥10 deployments/day
- Error rate: <1%
- User satisfaction: ≥80% (NPS)

**Month 1 After Launch**:
- User adoption: ≥100 active users
- Deployment frequency: ≥50 deployments/day
- Error rate: <0.5%
- User satisfaction: ≥90% (NPS)

---

## Risk Management

### Technical Risks

**Risk 1: Vercel Deployment Issues**
- Probability: Low
- Impact: High
- Mitigation: Test deployments thoroughly in preview environments
- Contingency: Rollback to previous version if issues occur

**Risk 2: Platform Kit Integration Issues**
- Probability: Medium
- Impact: Medium
- Mitigation: Test Platform Kit features extensively before launch
- Contingency: Disable Platform Kit temporarily if critical issues

**Risk 3: OdooOps API Changes**
- Probability: Low
- Impact: High
- Mitigation: Version API client, maintain backward compatibility
- Contingency: Implement API version negotiation

**Risk 4: Zoho SMTP Rate Limiting**
- Probability: Medium
- Impact: Low
- Mitigation: Implement notification batching and rate limiting
- Contingency: Use alternative SMTP provider (SendGrid backup)

### Operational Risks

**Risk 1: User Adoption**
- Probability: Low
- Impact: Medium
- Mitigation: Provide comprehensive documentation and onboarding
- Contingency: Offer training sessions and support

**Risk 2: Performance Issues**
- Probability: Medium
- Impact: Medium
- Mitigation: Load testing before launch, implement caching
- Contingency: Scale Vercel resources, optimize queries

**Risk 3: Security Vulnerabilities**
- Probability: Low
- Impact: High
- Mitigation: Security audit before launch, follow best practices
- Contingency: Immediate patching, security disclosure process

---

## Resource Requirements

### Development Resources
- 1 full-stack developer (5 weeks)
- Access to:
  - Supabase project (`spdtwktxdalcfigzeqrz`)
  - OdooOps API credentials
  - Zoho Workplace account
  - Vercel account
  - Cloudflare account
  - DigitalOcean infrastructure

### Infrastructure Resources
- Vercel (Next.js hosting): ~$20/month
- Cloudflare (DNS + CDN): Free tier
- Supabase: Free tier (existing project)
- Zoho Workplace: ~$3/user/month
- Total: ~$25/month

### Support Resources
- Documentation writer: 1 week (parallel)
- QA tester: 1 week (Week 5)
- DevOps engineer: 0.5 week (Cloudflare setup)

---

## Next Steps

1. **Immediate**: Create spec bundle (constitution, prd, plan, tasks)
2. **Week 1**: Scaffold Next.js console and implement authentication
3. **Week 2**: Integrate Platform Kit
4. **Week 3**: Implement OdooOps API integration
5. **Week 4**: Add Zoho notifications
6. **Week 5**: Testing and production deployment

---

**Plan Status**: Ready for implementation
**Approval**: Required before starting Week 1
