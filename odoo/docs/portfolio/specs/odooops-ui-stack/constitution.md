# OdooOps UI Stack — Constitution

**Created**: 2026-02-12
**Spec Kit**: odooops-ui-stack
**Status**: Draft

---

## Non-Negotiables

### 1. Supabase UI Library First
- **Use official Supabase UI components** from https://supabase.com/ui
- Registry-based installation via shadcn pattern
- Never fork or recreate official components
- Product UI blocks: auth, realtime, file upload, chat, avatars

### 2. Platform Kit Embedded
- **Full Supabase management console** embedded in OdooOps
- Azure Portal equivalent for Supabase operations
- Zero external navigation required for database/auth/storage/logs
- Native dashboard experience: DB, Auth, Storage, Users, Secrets, Logs, Performance

### 3. Supabase SSR (@supabase/ssr)
- **Modern auth pattern** with Next.js App Router
- Cookie/session-based authentication
- Replaces deprecated auth-helpers
- Server-side rendering with proper auth state

### 4. API-First Architecture
- **OdooOps API client** for all platform operations
- No UI clickpaths for deployments/environments
- All operations executable via CLI and API
- Agent-friendly automation layer

### 5. Zero Docker Locally
- **DigitalOcean App Platform** for remote builds
- Local development: Next.js dev server only
- Docker only for debugging (not production)
- Cloud-native deployment model

---

## Architectural Principles

### Routing Architecture
```
registry.insightpulseai.com → Squarespace (marketing/docs/SEO)
ops.insightpulseai.com      → Vercel (Next.js console)
erp.insightpulseai.com      → nginx → Odoo 19 CE
api.insightpulseai.com      → Supabase Edge Functions (optional gateway)
obs.insightpulseai.com      → Observability dashboards (optional)
```

### Edge Layer
- **Cloudflare**: DNS, WAF, caching, routing
- **nginx**: Reverse proxy to Odoo on DigitalOcean droplet
- **Vercel**: Next.js console hosting with Edge Functions

### Notifications
- **Zoho Workplace**: Email delivery via SMTP/API
- Deployment notifications, alert emails, system events
- No Mailgun/SendGrid dependencies

---

## UI Component Strategy

### Official Supabase Components Only
- Auth components (login, signup, password reset)
- Realtime components (presence, broadcast)
- File upload components (drag-drop, progress)
- Chat components (messaging, threads)
- Avatar components (user profiles)

### Platform Kit Integration
```typescript
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
```

### Custom Components
- OdooOps-specific UI (deployments, environments, tests)
- Analytics dashboards (Superset integration)
- Admin panels (user management, billing)

---

## Technology Constraints

### Required Stack
- **Next.js 14**: App Router with server components
- **TypeScript**: Strict mode, full type safety
- **Tailwind CSS**: Utility-first styling
- **Supabase JS**: Client library for auth/database
- **Supabase SSR**: Server-side auth patterns

### Forbidden Stack
- **No Deprecated Packages**: auth-helpers, auth-ui-react legacy
- **No Local Docker**: Production builds on DigitalOcean only
- **No UI Frameworks**: Material-UI, Ant Design (use Supabase UI)
- **No State Management**: Prefer React Server Components

---

## Security Requirements

### Authentication
- Multi-factor authentication (MFA) support
- OAuth providers (Google, GitHub, Microsoft)
- Magic link authentication
- Row-level security (RLS) policies

### Authorization
- Role-based access control (RBAC)
- Resource-level permissions
- API key management
- Service account tokens

### Data Protection
- HTTPS everywhere (TLS 1.3)
- Secrets in Vault (never in code)
- Environment isolation (preview/staging/prod)
- Audit logging for sensitive operations

---

## Performance Targets

### Load Times
- Initial page load: <2s on 3G
- Time to interactive: <3s on WiFi
- Server response: <200ms for API calls

### Bundle Sizes
- Initial bundle: <500KB gzipped
- Total bundle: <2MB
- Code splitting: automatic route-based

### Core Web Vitals
- LCP (Largest Contentful Paint): <2.5s
- FID (First Input Delay): <100ms
- CLS (Cumulative Layout Shift): <0.1

---

## Deployment Model

### Vercel Deployment
```yaml
framework: nextjs
build_command: pnpm build
output_directory: .next
install_command: pnpm install
environment:
  - NEXT_PUBLIC_SUPABASE_URL
  - NEXT_PUBLIC_SUPABASE_ANON_KEY
  - SUPABASE_SERVICE_ROLE_KEY
  - SUPABASE_ACCESS_TOKEN
  - ODOOOPS_API_BASE
  - ODOOOPS_TOKEN
  - ZOHO_EMAIL
  - ZOHO_PASSWORD
```

### Environment Strategy
- **Preview**: Per-PR ephemeral environments
- **Staging**: Persistent validation environment
- **Production**: Live customer-facing console

---

## Quality Gates

### Pre-Deployment
1. TypeScript compilation passes
2. Linting (ESLint) passes
3. Unit tests pass (≥80% coverage)
4. E2E tests pass (Playwright)
5. Bundle size under limits
6. Lighthouse score ≥90

### Post-Deployment
1. Health check endpoint responds
2. Auth flow functional
3. Platform Kit loads successfully
4. API client connects to OdooOps
5. Zoho notifications sending

---

## Documentation Requirements

### User Documentation
- Getting started guide
- Feature walkthroughs
- Video tutorials
- Troubleshooting guide

### Developer Documentation
- Architecture diagrams
- API reference
- Deployment guide
- Contributing guidelines

### Operational Documentation
- Runbooks for incidents
- Monitoring dashboards
- Alert configurations
- Backup/restore procedures

---

**Compliance**: This constitution is binding for all OdooOps UI development.
**Authority**: Deviations require explicit documentation and approval.
