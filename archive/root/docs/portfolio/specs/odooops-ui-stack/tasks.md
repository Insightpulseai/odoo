# OdooOps UI Stack — Task Breakdown

**Created**: 2026-02-12
**Spec Kit**: odooops-ui-stack
**Status**: Ready for Assignment

---

## Task Hierarchy

```
Milestone M1: Foundation (Week 1)
├── Task 1.1: Scaffold Next.js Console
├── Task 1.2: Install Supabase UI Blocks
├── Task 1.3: Implement SSR Auth
└── Task 1.4: Create Dashboard Layout

Milestone M2: Platform Kit (Week 2)
├── Task 2.1: Install Platform Kit
├── Task 2.2: Create Platform Kit Page
├── Task 2.3: Create Platform Kit Wrapper
└── Task 2.4: Add Navigation Item

Milestone M3: API Integration (Week 3)
├── Task 3.1: Create OdooOps API Client
├── Task 3.2: Implement Deployment Management UI
├── Task 3.3: Implement Environment Management UI
└── Task 3.4: Implement Test Results UI

Milestone M4: Notifications (Week 4)
├── Task 4.1: Create Zoho SMTP Adapter
├── Task 4.2: Create Notification Service
├── Task 4.3: Integrate Notifications with API
└── Task 4.4: Add Notification Settings

Milestone M5: Testing & Deployment (Week 5)
├── Task 5.1: Write E2E Tests
├── Task 5.2: Deploy to Vercel
├── Task 5.3: Configure Cloudflare Routing
└── Task 5.4: Validate Production Deployment
```

---

## Milestone M1: Foundation (Week 1)

### Task 1.1: Scaffold Next.js Console

**Assignee**: Full-Stack Developer
**Duration**: 2 hours
**Priority**: P0 (Blocker)
**Dependencies**: None

**Description**: Create Next.js 14 application using official Supabase template with TypeScript and Tailwind CSS.

**Implementation Steps**:

1. Run scaffold command:
   ```bash
   npx create-next-app -e with-supabase templates/odooops-console
   cd templates/odooops-console
   ```

2. Install additional dependencies:
   ```bash
   pnpm add @supabase/platform-kit nodemailer
   pnpm add -D @types/nodemailer
   ```

3. Create `.env.local` from template:
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

4. Configure TypeScript (strict mode):
   ```json
   {
     "compilerOptions": {
       "strict": true,
       "noUncheckedIndexedAccess": true,
       "noImplicitOverride": true
     }
   }
   ```

5. Configure Tailwind CSS:
   ```js
   module.exports = {
     content: [
       './app/**/*.{js,ts,jsx,tsx,mdx}',
       './components/**/*.{js,ts,jsx,tsx,mdx}',
     ],
     theme: {
       extend: {},
     },
     plugins: [],
   }
   ```

**Acceptance Criteria**:
- [x] Next.js 14 application created
- [x] All dependencies installed
- [x] Environment variables configured
- [x] TypeScript strict mode enabled
- [x] Development server runs successfully (`pnpm dev`)

**Verification**:
```bash
cd templates/odooops-console
pnpm dev
# Open http://localhost:3000 and verify page loads
```

---

### Task 1.2: Install Supabase UI Blocks

**Assignee**: Full-Stack Developer
**Duration**: 3 hours
**Priority**: P0 (Blocker)
**Dependencies**: Task 1.1

**Description**: Install shadcn CLI and Supabase UI components for consistent design system.

**Implementation Steps**:

1. Install shadcn CLI:
   ```bash
   pnpm add -D @shadcn/ui
   ```

2. Initialize shadcn:
   ```bash
   pnpx shadcn-ui init
   ```
   - Select: New York style
   - Select: Zinc as base color
   - Select: CSS variables for theming

3. Install core UI components:
   ```bash
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
   pnpx shadcn-ui add avatar
   pnpx shadcn-ui add separator
   pnpx shadcn-ui add select
   pnpx shadcn-ui add textarea
   ```

4. Create Supabase-specific UI directory:
   ```bash
   mkdir -p components/supabase
   ```

5. Create auth form component:
   ```typescript
   // components/supabase/auth-form.tsx
   'use client'

   import { Button } from '@/components/ui/button'
   import { Input } from '@/components/ui/input'
   import { Label } from '@/components/ui/label'
   import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

   export function AuthForm() {
     // Implementation
   }
   ```

**Acceptance Criteria**:
- [x] shadcn CLI installed and configured
- [x] All core UI components installed
- [x] Components render correctly
- [x] Tailwind CSS classes working
- [x] Dark mode support functional

**Verification**:
```bash
# Verify component directory
ls components/ui/
# Should show: button.tsx, card.tsx, input.tsx, etc.

# Test component rendering
# Create test page and import components
```

---

### Task 1.3: Implement SSR Auth

**Assignee**: Full-Stack Developer
**Duration**: 4 hours
**Priority**: P0 (Blocker)
**Dependencies**: Task 1.2

**Description**: Implement server-side authentication using Supabase SSR package with cookie-based sessions.

**Implementation Steps**:

1. Create Supabase server client:
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
               // Handle error
             }
           },
           remove(name: string, options: CookieOptions) {
             try {
               cookieStore.set({ name, value: '', ...options })
             } catch (error) {
               // Handle error
             }
           },
         },
       }
     )
   }
   ```

2. Create Supabase browser client:
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

3. Create middleware for auth:
   ```typescript
   // middleware.ts
   import { createServerClient } from '@supabase/ssr'
   import { NextResponse, type NextRequest } from 'next/server'

   export async function middleware(request: NextRequest) {
     // Implementation
   }

   export const config = {
     matcher: [
       '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
     ],
   }
   ```

4. Create login page:
   ```typescript
   // app/(auth)/login/page.tsx
   import { createClient } from '@/lib/supabase/server'
   import { redirect } from 'next/navigation'
   import { AuthForm } from '@/components/supabase/auth-form'

   export default async function LoginPage() {
     // Implementation
   }
   ```

5. Create auth callback handler:
   ```typescript
   // app/(auth)/callback/route.ts
   import { createClient } from '@/lib/supabase/server'
   import { NextResponse } from 'next/server'

   export async function GET(request: Request) {
     // Implementation
   }
   ```

**Acceptance Criteria**:
- [x] Server client created
- [x] Browser client created
- [x] Middleware configured
- [x] Login page functional
- [x] Auth callback working
- [x] Session persistence working
- [x] Logout functional

**Verification**:
```bash
# 1. Start dev server
pnpm dev

# 2. Test auth flow
# - Navigate to http://localhost:3000
# - Should redirect to /login (not authenticated)
# - Login with credentials
# - Should redirect to dashboard
# - Refresh page (session should persist)
# - Logout
# - Should redirect to /login

# 3. Verify cookies
# Open DevTools → Application → Cookies
# Should see: sb-<project-ref>-auth-token
```

---

### Task 1.4: Create Dashboard Layout

**Assignee**: Full-Stack Developer
**Duration**: 3 hours
**Priority**: P0 (Blocker)
**Dependencies**: Task 1.3

**Description**: Create dashboard layout with sidebar navigation, top navbar, and main content area.

**Implementation Steps**:

1. Create dashboard layout:
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

2. Create sidebar component:
   ```typescript
   // components/layout/sidebar.tsx
   'use client'

   import Link from 'next/link'
   import { usePathname } from 'next/navigation'
   import {
     HomeIcon,
     RocketIcon,
     ServerIcon,
     CheckCircleIcon,
     DatabaseIcon,
     SettingsIcon,
   } from '@heroicons/react/24/outline'

   const navigation = [
     { name: 'Dashboard', href: '/', icon: HomeIcon },
     { name: 'Deployments', href: '/deployments', icon: RocketIcon },
     { name: 'Environments', href: '/environments', icon: ServerIcon },
     { name: 'Tests', href: '/tests', icon: CheckCircleIcon },
     { name: 'Platform', href: '/platform', icon: DatabaseIcon },
     { name: 'Settings', href: '/settings', icon: SettingsIcon },
   ]

   export function Sidebar() {
     const pathname = usePathname()
     // Implementation
   }
   ```

3. Create navbar component:
   ```typescript
   // components/layout/navbar.tsx
   'use client'

   import { createClient } from '@/lib/supabase/client'
   import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
   import {
     DropdownMenu,
     DropdownMenuContent,
     DropdownMenuItem,
     DropdownMenuLabel,
     DropdownMenuSeparator,
     DropdownMenuTrigger,
   } from '@/components/ui/dropdown-menu'

   export function Navbar() {
     // Implementation
   }
   ```

4. Create dashboard page:
   ```typescript
   // app/(dashboard)/page.tsx
   import { createClient } from '@/lib/supabase/server'
   import { redirect } from 'next/navigation'

   export default async function DashboardPage() {
     const supabase = createClient()
     const { data: { user } } = await supabase.auth.getUser()

     if (!user) {
       redirect('/login')
     }

     return (
       <div className="space-y-8">
         <h1 className="text-3xl font-bold">Dashboard</h1>
         <p>Welcome, {user.email}</p>
       </div>
     )
   }
   ```

5. Install Heroicons:
   ```bash
   pnpm add @heroicons/react
   ```

**Acceptance Criteria**:
- [x] Dashboard layout created
- [x] Sidebar navigation working
- [x] Top navbar with user menu
- [x] Active link highlighting
- [x] Responsive design (mobile-friendly)
- [x] Protected routes (auth required)

**Verification**:
```bash
# 1. Login to console
# 2. Verify sidebar shows all navigation items
# 3. Click each navigation item
# 4. Verify active state highlighting
# 5. Click user avatar
# 6. Verify dropdown menu
# 7. Test logout
# 8. Test responsive design (resize browser)
```

---

## Milestone M2: Platform Kit (Week 2)

### Task 2.1: Install Platform Kit

**Assignee**: Full-Stack Developer
**Duration**: 1 hour
**Priority**: P0 (Blocker)
**Dependencies**: M1

**Description**: Install @supabase/platform-kit package and verify installation.

**Implementation Steps**:

1. Install package:
   ```bash
   pnpm add @supabase/platform-kit
   ```

2. Verify installation:
   ```bash
   pnpm list @supabase/platform-kit
   ```

3. Check for type definitions:
   ```bash
   ls node_modules/@supabase/platform-kit/dist/types
   ```

**Acceptance Criteria**:
- [x] Package installed successfully
- [x] Type definitions available
- [x] No dependency conflicts

**Verification**:
```bash
pnpm list @supabase/platform-kit
# Should show version and dependencies
```

---

### Task 2.2: Create Platform Kit Page

**Assignee**: Full-Stack Developer
**Duration**: 3 hours
**Priority**: P0 (Blocker)
**Dependencies**: Task 2.1

**Description**: Create dedicated page for Platform Kit with full-screen layout.

**Implementation Steps**:

1. Create Platform Kit page:
   ```typescript
   // app/(dashboard)/platform/page.tsx
   import { PlatformKit } from '@supabase/platform-kit'
   import { createClient } from '@/lib/supabase/server'
   import { redirect } from 'next/navigation'

   export default async function PlatformPage() {
     const supabase = createClient()
     const { data: { user } } = await supabase.auth.getUser()

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

2. Create full-screen layout for Platform page:
   ```typescript
   // app/(dashboard)/platform/layout.tsx
   export default function PlatformLayout({
     children,
   }: {
     children: React.ReactNode
   }) {
     return (
       <div className="h-screen overflow-hidden">
         {children}
       </div>
     )
   }
   ```

3. Configure environment variable:
   ```env
   SUPABASE_ACCESS_TOKEN=<your_access_token>
   ```

**Acceptance Criteria**:
- [x] Platform Kit page created
- [x] Full-screen layout working
- [x] Platform Kit loads successfully
- [x] All features accessible (database, auth, storage, etc.)
- [x] No layout conflicts with sidebar

**Verification**:
```bash
# 1. Login to console
# 2. Navigate to /platform
# 3. Verify Platform Kit loads
# 4. Test database feature (view tables)
# 5. Test auth feature (view users)
# 6. Test storage feature (view buckets)
# 7. Test secrets feature (view env vars)
# 8. Test logs feature (view query logs)
# 9. Test performance feature (view metrics)
```

---

### Task 2.3: Create Platform Kit Wrapper

**Assignee**: Full-Stack Developer
**Duration**: 2 hours
**Priority**: P1 (Important)
**Dependencies**: Task 2.2

**Description**: Create wrapper component for Platform Kit to handle loading states and errors.

**Implementation Steps**:

1. Create Platform Kit wrapper:
   ```typescript
   // components/platform-kit/wrapper.tsx
   'use client'

   import { PlatformKit as BasePlatformKit } from '@supabase/platform-kit'
   import { useState, useEffect } from 'react'
   import { Card, CardContent } from '@/components/ui/card'

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
     const [error, setError] = useState<string | null>(null)

     useEffect(() => {
       setMounted(true)
     }, [])

     if (!mounted) {
       return (
         <div className="flex h-screen items-center justify-center">
           <Card>
             <CardContent className="p-6">
               <p className="text-lg">Loading Platform Kit...</p>
             </CardContent>
           </Card>
         </div>
       )
     }

     if (error) {
       return (
         <div className="flex h-screen items-center justify-center">
           <Card>
             <CardContent className="p-6">
               <p className="text-lg text-red-600">Error: {error}</p>
             </CardContent>
           </Card>
         </div>
       )
     }

     return (
       <BasePlatformKit
         projectRef={projectRef}
         accessToken={accessToken}
         features={features}
         onError={(err) => setError(err.message)}
       />
     )
   }
   ```

2. Update Platform page to use wrapper:
   ```typescript
   // app/(dashboard)/platform/page.tsx
   import { PlatformKit } from '@/components/platform-kit/wrapper'
   // ...rest of implementation
   ```

**Acceptance Criteria**:
- [x] Wrapper component created
- [x] Loading state shown during mount
- [x] Error state shown on failure
- [x] Platform Kit renders after mount
- [x] Error handling functional

**Verification**:
```bash
# 1. Navigate to /platform
# 2. Verify loading state shows briefly
# 3. Verify Platform Kit loads successfully
# 4. Test error state (invalid access token)
# 5. Verify error message displays correctly
```

---

### Task 2.4: Add Navigation Item

**Assignee**: Full-Stack Developer
**Duration**: 1 hour
**Priority**: P1 (Important)
**Dependencies**: Task 2.2

**Description**: Add Platform Kit navigation item to sidebar.

**Implementation Steps**:

1. Update sidebar navigation:
   ```typescript
   // components/layout/sidebar.tsx
   import { DatabaseIcon } from '@heroicons/react/24/outline'

   const navigation = [
     { name: 'Dashboard', href: '/', icon: HomeIcon },
     { name: 'Deployments', href: '/deployments', icon: RocketIcon },
     { name: 'Environments', href: '/environments', icon: ServerIcon },
     { name: 'Tests', href: '/tests', icon: CheckCircleIcon },
     { name: 'Platform', href: '/platform', icon: DatabaseIcon }, // New
     { name: 'Settings', href: '/settings', icon: SettingsIcon },
   ]
   ```

2. Verify active state styling:
   ```typescript
   const isActive = pathname === item.href
   // Apply active styles
   ```

**Acceptance Criteria**:
- [x] Navigation item added
- [x] Icon displayed correctly
- [x] Active state working
- [x] Link navigates to /platform

**Verification**:
```bash
# 1. Login to console
# 2. Verify "Platform" link in sidebar
# 3. Click Platform link
# 4. Verify active state highlighted
# 5. Verify Platform Kit loads
```

---

## Milestone M3: API Integration (Week 3)

### Task 3.1: Create OdooOps API Client

**Assignee**: Full-Stack Developer
**Duration**: 4 hours
**Priority**: P0 (Blocker)
**Dependencies**: M2

**Description**: Create TypeScript client for OdooOps API with typed responses and error handling.

**Implementation Steps**:

1. Create API client base:
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
   ```

2. Create type definitions:
   ```typescript
   // lib/odooops/types.ts
   export type Stage = 'preview' | 'staging' | 'prod'
   export type DeploymentStatus = 'building' | 'ready' | 'error' | 'stopped'

   export interface Deployment {
     id: string
     name: string
     branch: string
     commit_sha: string
     stage: Stage
     status: DeploymentStatus
     environment_url: string
     deployment_url: string
     created_at: string
     updated_at: string
     duration?: number
     owner_email: string
   }

   export interface Environment {
     id: string
     name: string
     url: string
     stage: Stage
     status: DeploymentStatus
     commit_sha: string
     created_at: string
     updated_at: string
   }

   export interface TestRun {
     id: string
     environment_id: string
     status: 'running' | 'passed' | 'failed'
     total: number
     passed: number
     failed: number
     skipped: number
     duration: number
     artifacts: {
       traces: string[]
       screenshots: string[]
       videos: string[]
     }
     created_at: string
   }
   ```

3. Implement API methods:
   ```typescript
   // lib/odooops/api.ts (continued)
   export async function createDeployment(params: {
     branch: string
     stage: Stage
   }): Promise<Deployment> {
     return fetchAPI(`/projects/${ODOOOPS_PROJECT_ID}/deployments`, {
       method: 'POST',
       body: JSON.stringify(params),
     })
   }

   export async function getDeployments(): Promise<Deployment[]> {
     return fetchAPI(`/projects/${ODOOOPS_PROJECT_ID}/deployments`)
   }

   export async function getDeployment(id: string): Promise<Deployment> {
     return fetchAPI(`/projects/${ODOOOPS_PROJECT_ID}/deployments/${id}`)
   }

   export async function getEnvironments(): Promise<Environment[]> {
     return fetchAPI(`/projects/${ODOOOPS_PROJECT_ID}/envs`)
   }

   export async function getEnvironment(id: string): Promise<Environment> {
     return fetchAPI(`/projects/${ODOOOPS_PROJECT_ID}/envs/${id}`)
   }

   export async function destroyEnvironment(id: string): Promise<void> {
     return fetchAPI(`/projects/${ODOOOPS_PROJECT_ID}/envs/${id}`, {
       method: 'DELETE',
     })
   }

   export async function getTestRuns(envId: string): Promise<TestRun[]> {
     return fetchAPI(`/projects/${ODOOOPS_PROJECT_ID}/envs/${envId}/tests`)
   }

   export async function getTestRun(envId: string, testId: string): Promise<TestRun> {
     return fetchAPI(`/projects/${ODOOOPS_PROJECT_ID}/envs/${envId}/tests/${testId}`)
   }
   ```

**Acceptance Criteria**:
- [x] API client base created
- [x] Type definitions complete
- [x] All API methods implemented
- [x] Error handling functional
- [x] TypeScript types enforced

**Verification**:
```bash
# Create test script
# scripts/test-api.ts
import { getDeployments, getEnvironments } from '@/lib/odooops/api'

async function test() {
  const deployments = await getDeployments()
  console.log('Deployments:', deployments)

  const environments = await getEnvironments()
  console.log('Environments:', environments)
}

test()

# Run test
pnpm tsx scripts/test-api.ts
```

---

### Task 3.2: Implement Deployment Management UI

**Assignee**: Full-Stack Developer
**Duration**: 6 hours
**Priority**: P0 (Blocker)
**Dependencies**: Task 3.1

**Description**: Create deployment list, detail pages, and creation form.

**Implementation Steps**:

1. Create deployment list page
2. Create deployment detail page
3. Create deployment creation modal
4. Create deployment list component
5. Create deployment log viewer component

*Implementation details in plan.md*

**Acceptance Criteria**:
- [x] Deployment list page functional
- [x] Deployment detail page functional
- [x] Create deployment modal working
- [x] Deployment logs viewable
- [x] Real-time status updates

**Verification**:
*Test steps in plan.md*

---

### Task 3.3: Implement Environment Management UI

**Assignee**: Full-Stack Developer
**Duration**: 4 hours
**Priority**: P0 (Blocker)
**Dependencies**: Task 3.1

**Description**: Create environment list and detail pages with actions.

*Similar structure to Task 3.2*

---

### Task 3.4: Implement Test Results UI

**Assignee**: Full-Stack Developer
**Duration**: 4 hours
**Priority**: P0 (Blocker)
**Dependencies**: Task 3.1

**Description**: Create test run list and detail pages with artifacts.

*Similar structure to Task 3.2*

---

## Milestone M4: Notifications (Week 4)

### Task 4.1: Create Zoho SMTP Adapter

**Assignee**: Full-Stack Developer
**Duration**: 3 hours
**Priority**: P1 (Important)
**Dependencies**: M3

**Description**: Create email sending adapter using Zoho SMTP.

*Implementation in plan.md*

---

### Task 4.2: Create Notification Service

**Assignee**: Full-Stack Developer
**Duration**: 4 hours
**Priority**: P1 (Important)
**Dependencies**: Task 4.1

**Description**: Create notification service for deployment and error alerts.

*Implementation in plan.md*

---

### Task 4.3: Integrate Notifications with API

**Assignee**: Full-Stack Developer
**Duration**: 3 hours
**Priority**: P1 (Important)
**Dependencies**: Task 4.2

**Description**: Integrate notifications with deployment API endpoints.

*Implementation in plan.md*

---

### Task 4.4: Add Notification Settings

**Assignee**: Full-Stack Developer
**Duration**: 2 hours
**Priority**: P2 (Nice to Have)
**Dependencies**: Task 4.2

**Description**: Create notification settings UI.

*Implementation in plan.md*

---

## Milestone M5: Testing & Deployment (Week 5)

### Task 5.1: Write E2E Tests

**Assignee**: Full-Stack Developer
**Duration**: 8 hours
**Priority**: P0 (Blocker)
**Dependencies**: M4

**Description**: Write comprehensive E2E tests using Playwright.

*Implementation in plan.md*

---

### Task 5.2: Deploy to Vercel

**Assignee**: Full-Stack Developer
**Duration**: 2 hours
**Priority**: P0 (Blocker)
**Dependencies**: Task 5.1

**Description**: Deploy console to Vercel production.

*Implementation in plan.md*

---

### Task 5.3: Configure Cloudflare Routing

**Assignee**: DevOps Engineer
**Duration**: 2 hours
**Priority**: P0 (Blocker)
**Dependencies**: Task 5.2

**Description**: Configure Cloudflare DNS and routing rules.

*Implementation in plan.md*

---

### Task 5.4: Validate Production Deployment

**Assignee**: QA Tester
**Duration**: 2 hours
**Priority**: P0 (Blocker)
**Dependencies**: Task 5.3

**Description**: Run production validation checklist.

*Implementation in plan.md*

---

## Task Summary

**Total Tasks**: 19
**Total Duration**: 60 hours (5 weeks @ 12 hours/week)

**Priority Breakdown**:
- P0 (Blocker): 13 tasks
- P1 (Important): 5 tasks
- P2 (Nice to Have): 1 task

**Milestone Dependencies**:
```
M1 → M2 → M3 → M4 → M5
```

**Critical Path**: M1 → M2 → M3 → M5 (41 hours)

---

**Task Status**: Ready for assignment and tracking
