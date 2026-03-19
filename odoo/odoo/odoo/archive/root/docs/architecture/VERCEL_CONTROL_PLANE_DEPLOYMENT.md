# Vercel Control Plane Deployment Contract

**SSOT for `web/ai-control-plane` deployment configuration**

---

## Project Configuration

| Property | Value |
|----------|-------|
| **Project Root** | `web/ai-control-plane` |
| **Framework** | Next.js 14 (App Router) |
| **Build Command** | `pnpm build` |
| **Output Directory** | `.next` |
| **Install Command** | `pnpm install` |
| **Dev Command** | `pnpm dev --port 3100` |
| **Node Version** | >= 18.0.0 (LTS) |

---

## Environment Variables

### Client-Side (NEXT_PUBLIC_*)
Exposed to browser. Use only for public keys and non-sensitive URLs.

| Variable | Required | Example | Purpose |
|----------|----------|---------|---------|
| `NEXT_PUBLIC_SUPABASE_URL` | ✅ | `https://spdtwktxdalcfigzeqrz.supabase.co` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ✅ | `eyJhbGciOi...` | Supabase anon/public key |

### Server-Side (Process.env Only)
**NEVER expose these via NEXT_PUBLIC_***

| Variable | Required | Purpose | Access |
|----------|----------|---------|--------|
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | Full database access | API routes, server components |
| `SUPABASE_MANAGEMENT_API_TOKEN` | ✅ | Supabase Management API | API routes |
| `GITHUB_TOKEN` | ✅ | GitHub API (deployments, PRs) | API routes |
| `ALLOWED_PROJECT_REFS` | ✅ | Comma-separated project refs | API routes |
| `N8N_WEBHOOK_BACKUP_URL` | ❌ | Trigger manual backups | API routes |
| `OPENAI_API_KEY` | ❌ | AI features | API routes |

### Local-Only (Not Needed on Vercel)

| Variable | Value | Reason |
|----------|-------|--------|
| `DOCKER_SOCKET_PATH` | `/var/run/docker.sock` | Docker features disabled on Vercel (no socket access) |

---

## Build & Runtime Contract

### Build Process
1. `pnpm install` - Install dependencies from lockfile
2. `pnpm build` - Next.js build (generates `.next/`)
3. Output: `.next/standalone` + `.next/static` (production-optimized)

### Runtime Requirements
- **Node.js**: >= 18.0.0
- **Region**: Auto (or specify `sfo1`, `iad1` for proximity to Supabase)
- **Memory**: 1024 MB (default)
- **Timeout**: 10s (API routes)

### Excluded from Vercel Build
- `.env.local` (gitignored)
- `node_modules/` (managed by Vercel)
- `.next/` (regenerated on deploy)
- `*.log` files

---

## Deployment Environments

### Production (main branch)
- **URL**: `https://ai-control-plane-insightpulse.vercel.app` (or custom domain)
- **Branch**: `main`
- **Environment**: Production
- **Variables**: Use Production environment in Vercel project settings

### Preview (PR branches)
- **URL**: `https://ai-control-plane-<branch>-insightpulse.vercel.app`
- **Branch**: Any PR branch (e.g., `feat/platform-ui`)
- **Environment**: Preview
- **Variables**: Same as Production (OR separate Preview variables if needed)

### Development (local)
- **URL**: `http://localhost:3100`
- **Environment**: `.env.local`
- **Docker Access**: Enabled (local socket)

---

## PR Preview Workflow

1. **PR Created** → Vercel auto-deploys preview
2. **Preview URL** → `https://ai-control-plane-git-<branch>-insightpulse.vercel.app`
3. **Environment Variables** → Inherits from Production (OR Preview-specific)
4. **Status Checks** → Vercel build success/failure reported to GitHub
5. **PR Merged** → Preview deleted, main branch deploys to Production

---

## Security Contract

### ✅ Allowed
- `NEXT_PUBLIC_SUPABASE_URL` (public endpoint)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` (RLS-protected)
- Client-side feature flags

### ❌ Forbidden (NEVER in NEXT_PUBLIC_*)
- `SUPABASE_SERVICE_ROLE_KEY` (bypasses RLS)
- `SUPABASE_MANAGEMENT_API_TOKEN` (admin access)
- `GITHUB_TOKEN` (write access to repos)
- API keys, secrets, admin tokens

### CI Enforcement
A GitHub Actions workflow validates:
- No `NEXT_PUBLIC_*` vars contain service role keys
- No secrets leaked in git diff
- `.env.local` is gitignored

---

## Docker Feature Detection

Docker-dependent features (container management) are **disabled on Vercel**.

### Runtime Detection Pattern
```typescript
// lib/docker-client.ts
const isDockerAvailable = typeof process.env.DOCKER_SOCKET_PATH !== 'undefined' 
  && process.env.DOCKER_SOCKET_PATH !== '';

export function getContainerStatus(containerId: string) {
  if (!isDockerAvailable) {
    throw new Error('Docker features not available in this environment');
  }
  // ... Docker logic
}
```

### UI Behavior
- Production (Vercel): Hide Docker-related buttons (Shell, Logs)
- Local Dev: Show all features
- Detection: `if (typeof window !== 'undefined' && process.env.DOCKER_SOCKET_PATH)`

---

## Deployment Checklist

### Pre-Deployment
- [ ] `.env.local.example` updated with all required vars
- [ ] No secrets in git history (`git log -p | grep -i "service_role"`)
- [ ] `pnpm build` succeeds locally
- [ ] `pnpm lint` passes
- [ ] `.gitignore` includes `.env.local`, `.env`

### Vercel Project Setup (One-Time)
- [ ] Create Vercel project linked to `insightpulseai/odoo`
- [ ] Set Root Directory: `web/ai-control-plane`
- [ ] Set Build Command: `pnpm build`
- [ ] Set Install Command: `pnpm install`
- [ ] Add all environment variables from contract above
- [ ] Enable Preview Deployments for PRs

### Post-Deployment Validation
- [ ] Production URL loads dashboard (`/platform`)
- [ ] API routes respond (`/api/ops/runs/[id]`)
- [ ] No Docker errors in logs (features gracefully disabled)
- [ ] Real-time SSE works (`/platform/runs/[id]`)
- [ ] No `NEXT_PUBLIC_SERVICE_ROLE_KEY` exposure

---

## Troubleshooting

### Build Fails: "Module not found"
- Check `pnpm-lock.yaml` is committed
- Verify `pnpm install` runs in `web/ai-control-plane`
- Check Vercel build logs for root directory

### Runtime Error: "Missing SUPABASE_SERVICE_ROLE_KEY"
- Verify env var added to Vercel project settings
- Check environment (Production vs Preview)
- Ensure server component/API route access

### Docker Features Don't Work
- Expected on Vercel (no Docker socket)
- Verify feature detection disables UI elements
- Check local dev has `DOCKER_SOCKET_PATH` set

---

## Automation Script (Optional)

See `scripts/vercel/env_sync.ts` for automated env var synchronization.

**Usage**:
```bash
# Sync env vars to Vercel project
pnpm tsx scripts/vercel/env_sync.ts --project ai-control-plane --env production

# Dry run (show what would be updated)
pnpm tsx scripts/vercel/env_sync.ts --project ai-control-plane --dry-run
```

---

**Last Updated**: 2026-02-20  
**Owner**: InsightPulse AI Platform Team  
**SSOT**: This document is canonical for Vercel deployment config
