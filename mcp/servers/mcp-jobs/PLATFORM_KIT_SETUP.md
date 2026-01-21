# MCP-Jobs: Supabase Platform Kit Integration

**Date**: 2026-01-20
**Status**: ✅ **CONFIGURED - Ready for Platform Kit Installation**

---

## Overview

This document describes the Supabase Platform Kit integration for mcp-jobs, which provides an embedded Supabase management experience including:

- **Database Management**: Tables, columns, RLS policies, SQL editor with AI generation
- **Authentication**: User management, auth providers, policies
- **Storage**: Bucket management, file operations
- **Users**: User directory, permissions
- **Secrets**: Environment variables management
- **Logs**: Real-time logs and monitoring
- **Performance**: Query performance monitoring

---

## Installation

### Step 1: Install Platform Kit

```bash
cd /Users/tbwa/Documents/GitHub/odoo-ce/mcp/servers/mcp-jobs

# Install via shadcn (recommended)
npx shadcn@latest add @supabase/platform-kit-nextjs
```

This will:
- Add Platform Kit components to `components/supabase-manager/`
- Add API proxy route at `app/api/supabase-proxy/[...path]/route.ts`
- Add AI SQL generation route at `app/api/ai/sql/route.ts`
- Add necessary dependencies to `package.json`

### Step 2: Environment Variables (✅ Already Configured)

The following environment variables have been configured in `.env.local`:

```bash
# Supabase public client (browser-safe)
NEXT_PUBLIC_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[configured from $SUPABASE_ANON_KEY]

# Supabase Management API (server-only)
SUPABASE_MANAGEMENT_API_TOKEN=[configured from $SUPABASE_ACCESS_TOKEN]

# AI SQL Generation (optional)
NEXT_PUBLIC_ENABLE_AI_QUERIES=true
OPENAI_API_KEY=[needs configuration if AI queries enabled]

# Server-only vars
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_SERVICE_ROLE_KEY=[configured from $SUPABASE_SERVICE_ROLE_KEY]
```

### Step 3: Add Toaster Component

Add the Toaster component to your root layout for notifications:

```tsx
// app/layout.tsx or wherever your root layout is
import { Toaster } from '@/components/ui/sonner'

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head />
      <body>
        <main>{children}</main>
        <Toaster />
      </body>
    </html>
  )
}
```

### Step 4: Use the Manager Dialog

```tsx
import { useState } from 'react'
import { useMobile } from '@/hooks/use-mobile'
import { Button } from '@/components/ui/button'
import SupabaseManagerDialog from '@/components/supabase-manager'

export default function Example() {
  const [open, setOpen] = useState(false)
  const projectRef = 'spdtwktxdalcfigzeqrz' // Your Supabase project ref
  const isMobile = useMobile()

  return (
    <>
      <Button onClick={() => setOpen(true)}>Open Supabase Manager</Button>
      <SupabaseManagerDialog
        projectRef={projectRef}
        open={open}
        onOpenChange={setOpen}
        isMobile={isMobile}
      />
    </>
  )
}
```

---

## Security Implementation

### ⚠️ CRITICAL: Add Authentication Checks

Before deploying, you **MUST** add project-level authentication in these files:

#### 1. API Proxy (`app/api/supabase-proxy/[...path]/route.ts`)

```typescript
export async function GET(request: Request) {
  // TODO: Implement authentication check
  // Example:
  // const session = await getServerSession(authOptions)
  // if (!session) {
  //   return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  // }

  // TODO: Verify user has permission for this project
  // Example:
  // const hasAccess = await checkProjectAccess(session.user.id, projectRef)
  // if (!hasAccess) {
  //   return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
  // }

  // ... rest of proxy logic
}
```

#### 2. AI SQL Route (`app/api/ai/sql/route.ts`)

```typescript
export async function POST(request: Request) {
  try {
    const { prompt, projectRef } = await request.json()

    // TODO: Implement permission check
    // Replace this placeholder with real authentication:
    // const session = await getServerSession(authOptions)
    // if (!session) {
    //   return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    // }

    // TODO: Verify user owns/has access to this project
    // const userHasPermissionForProject = await verifyProjectAccess(
    //   session.user.id,
    //   projectRef
    // )

    const userHasPermissionForProject = Boolean(projectRef) // PLACEHOLDER - REPLACE

    if (!userHasPermissionForProject) {
      return NextResponse.json(
        { message: 'You do not have permission to access this project.' },
        { status: 403 }
      )
    }

    // ... rest of AI SQL generation logic
  } catch (error: any) {
    console.error('AI SQL generation error:', error)
    return NextResponse.json({ message: error.message }, { status: 500 })
  }
}
```

### Security Checklist

- [ ] **Never expose Management API token to client** (only use in API routes)
- [ ] **Implement authentication** in API proxy and AI SQL routes
- [ ] **Verify project ownership** before allowing Management API access
- [ ] **Rate limit API endpoints** to prevent abuse
- [ ] **Log all Management API calls** for audit trail
- [ ] **Use environment-specific tokens** (dev vs production)

---

## Vercel Deployment Configuration

### Required Environment Variables

Configure these in Vercel dashboard or via CLI:

```bash
# Production environment
vercel env add NEXT_PUBLIC_SUPABASE_URL production
# Value: https://spdtwktxdalcfigzeqrz.supabase.co

vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
# Value: [your anon key from Supabase dashboard]

vercel env add SUPABASE_MANAGEMENT_API_TOKEN production
# Value: [your personal access token from https://supabase.com/dashboard/account/tokens]

vercel env add NEXT_PUBLIC_ENABLE_AI_QUERIES production
# Value: true

vercel env add OPENAI_API_KEY production
# Value: [your OpenAI API key if AI queries enabled]

# Repeat for preview and development environments
```

### Alternative: Non-Interactive Configuration

```bash
export NEXT_PUBLIC_SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
export NEXT_PUBLIC_SUPABASE_ANON_KEY="your-anon-key"
export SUPABASE_MANAGEMENT_API_TOKEN="your-management-token"

printf '%s' "$NEXT_PUBLIC_SUPABASE_URL" | \
  vercel env add NEXT_PUBLIC_SUPABASE_URL production --yes

printf '%s' "$NEXT_PUBLIC_SUPABASE_ANON_KEY" | \
  vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production --yes

printf '%s' "$SUPABASE_MANAGEMENT_API_TOKEN" | \
  vercel env add SUPABASE_MANAGEMENT_API_TOKEN production --yes
```

---

## Verification Steps

### Local Development

1. **Install dependencies:**
   ```bash
   pnpm install
   ```

2. **Verify environment variables:**
   ```bash
   grep NEXT_PUBLIC_SUPABASE_URL .env.local || echo "❌ Missing URL"
   grep NEXT_PUBLIC_SUPABASE_ANON_KEY .env.local || echo "❌ Missing anon key"
   grep SUPABASE_MANAGEMENT_API_TOKEN .env.local || echo "❌ Missing management token"
   ```

3. **Run development server:**
   ```bash
   pnpm dev
   ```

4. **Test Platform Kit UI:**
   - Navigate to page with Supabase Manager button
   - Click to open manager dialog
   - Verify database, auth, storage tabs load correctly

### Build Verification

```bash
# Local build test
pnpm build

# Verify no environment variable errors
# Should complete without "Missing NEXT_PUBLIC_SUPABASE_URL" error
```

### Vercel Deployment

```bash
# Pull environment variables from Vercel
vercel env pull .env.vercel

# Verify variables are set
grep NEXT_PUBLIC_SUPABASE_URL .env.vercel || echo "❌ URL not set in Vercel"
grep SUPABASE_MANAGEMENT_API_TOKEN .env.vercel || echo "❌ Management token not set in Vercel"

# Deploy to production
git add .
git commit -m "feat: configure Supabase Platform Kit with Management API"
git push origin main
```

---

## Features Enabled

### Database Management
- **SQL Editor**: Write and execute SQL queries with syntax highlighting
- **AI SQL Generation**: Generate SQL from natural language (requires OpenAI API key)
- **Table Browser**: View and edit table data
- **Schema Inspector**: View table schemas, relationships, indexes
- **RLS Policies**: View and manage Row Level Security policies

### Authentication
- **User Directory**: View all authenticated users
- **Auth Providers**: Configure social auth (Google, GitHub, etc.)
- **Email Templates**: Customize auth emails
- **User Management**: Manually create/delete users

### Storage
- **Bucket Management**: Create and configure storage buckets
- **File Browser**: Upload, view, delete files
- **Bucket Policies**: Configure access policies

### Users
- **User List**: View all users with metadata
- **User Actions**: Ban, delete, reset password
- **Custom Claims**: Add custom metadata to users

### Secrets
- **Environment Variables**: Manage project secrets securely
- **API Keys**: View and rotate API keys

### Logs
- **Real-time Logs**: View logs from all services
- **Log Filtering**: Filter by service, level, timestamp
- **Log Export**: Export logs for analysis

### Performance
- **Query Performance**: View slow queries and execution times
- **Connection Pool**: Monitor database connections
- **Resource Usage**: CPU, memory, storage metrics

---

## AI SQL Generation (Optional)

### How It Works

1. User enters natural language query (e.g., "Show me all users who signed up in the last 7 days")
2. System fetches database schema via Management API
3. Schema is formatted and sent to OpenAI with user's question
4. OpenAI generates SQL query matching the schema
5. SQL is returned to user for review and execution

### Configuration

Enable AI queries by setting:
```bash
NEXT_PUBLIC_ENABLE_AI_QUERIES=true
OPENAI_API_KEY=sk-your-openai-api-key
```

### Cost Considerations

- **Typical query**: $0.001 - $0.01 per generation (using GPT-4)
- **Monthly estimate**: ~$10-50 for moderate usage
- **Optimization**: Cache common queries, limit to authenticated users

---

## Troubleshooting

### Build Error: Missing Environment Variables

**Error:**
```
Error: Missing NEXT_PUBLIC_SUPABASE_URL environment variable
```

**Fix:**
1. Verify `.env.local` exists with correct values
2. For Vercel: Add environment variables in dashboard or via CLI
3. Restart development server after adding variables

### 403 Forbidden on Management API

**Error:**
```
Error: Forbidden - Invalid or expired Management API token
```

**Fix:**
1. Verify `SUPABASE_MANAGEMENT_API_TOKEN` is set correctly
2. Get fresh token from https://supabase.com/dashboard/account/tokens
3. Ensure token has required scopes (project read/write)

### AI SQL Generation Not Working

**Error:**
```
Error: Could not generate SQL from the prompt
```

**Fix:**
1. Verify `OPENAI_API_KEY` is set and valid
2. Check OpenAI API usage limits
3. Ensure `NEXT_PUBLIC_ENABLE_AI_QUERIES=true`
4. Verify OpenAI account has credits

---

## Next Steps

1. **Install Platform Kit:**
   ```bash
   npx shadcn@latest add @supabase/platform-kit-nextjs
   ```

2. **Add Authentication:**
   - Implement `getServerSession` or equivalent
   - Add project access verification logic
   - Test with real user sessions

3. **Configure Vercel Environment:**
   - Add all required environment variables
   - Test deployment with production credentials

4. **Enable AI Queries (Optional):**
   - Add OpenAI API key
   - Test AI SQL generation
   - Monitor costs and usage

5. **Security Audit:**
   - Review API proxy authentication
   - Verify no tokens exposed to client
   - Test with different user roles
   - Add rate limiting

---

## Resources

- **Platform Kit Docs**: https://supabase.com/ui/docs/platform/platform-kit
- **Management API**: https://supabase.com/docs/reference/api/introduction
- **Supabase Personal Access Tokens**: https://supabase.com/dashboard/account/tokens
- **OpenAI API**: https://platform.openai.com/api-keys

---

**Setup Status**: ✅ **Environment Configured - Ready for Platform Kit Installation**

**Next Action**: Run `npx shadcn@latest add @supabase/platform-kit-nextjs` to install components

**Configured By**: Claude Sonnet 4.5
**Configuration Date**: 2026-01-20
