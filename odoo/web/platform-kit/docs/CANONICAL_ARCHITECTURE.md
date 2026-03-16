# Canonical Combined Architecture

> **Supabase Team + Vercel Team + DigitalOcean (stateful only)**
>
> This is the modern Odoo.sh + Vercel + internal platform replacement.

---

## Executive Summary

This architecture combines three platforms into a unified internal platform:

| Platform | Role | What It Replaces |
|----------|------|------------------|
| **Vercel Team** | Execution + UX Plane | Heroku, Netlify, custom frontends |
| **Supabase Team** | System of Record + Security Plane | Firebase, custom auth, admin backends |
| **DigitalOcean** | Stateful Runtime Only | Odoo.sh, self-hosted VMs |

**Key Insight**: You are not choosing Supabase *or* Vercel—you are combining them as a **single platform plane**.

---

## 1. Responsibility Split (Non-Negotiable)

### Vercel Team = Execution + UX Plane

What Vercel is best at:

- Frontends (Next.js, Platform Kit UI)
- Edge Functions (low-latency routing, auth checks)
- Preview environments (PR → URL)
- Marketplace integrations (Slack, GitHub, n8n, Resend, Sentry)
- CI visibility (builds, logs, deploy summaries)

> Think: **Vercel = "Control Surface + Developer UX"**

### Supabase Team = System of Record + Security Plane

What Supabase is best at:

- PostgreSQL (`ops.*`, `advisor.*`, `mirror.*` schemas)
- Auth (JWT, RBAC, RLS)
- Storage (artifacts, backups, exports)
- Edge Functions (secure backend logic)
- Realtime + cron (`pg_cron`)
- Compliance posture (SOC2/HIPAA/GDPR ready)
- Team access, secrets (Vault), environments

> Think: **Supabase = "Truth, Security, Governance"**

### DigitalOcean = Stateful Runtime Only

DO is **not** your platform—it is a **workload host**:

- Odoo (ERP runtime)
- Plane CE (if not serverless)
- Workers / queues that must stay alive
- Managed Postgres (already live: `odoo-db-sgp1`)

> Think: **DO = "Machines that must exist"**

---

## 2. System Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────────┐
│                           VERCEL TEAM                                      │
│                                                                           │
│    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐     │
│    │ Platform Kit UI │  │  PR Previews    │  │ Marketplace Integs  │     │
│    │    (Next.js)    │  │  (auto-deploy)  │  │ (Slack,GitHub,n8n)  │     │
│    └────────┬────────┘  └─────────────────┘  └─────────────────────┘     │
│             │                                                             │
│    ┌────────┴────────┐                                                   │
│    │  Edge Auth Gate │  ←── JWT verification at edge                      │
│    └────────┬────────┘                                                   │
│             │                                                             │
│    ┌────────┴────────┐                                                   │
│    │   Logs/Deploys  │  ←── Build artifacts, deploy summaries             │
│    └─────────────────┘                                                   │
│                                                                           │
└───────────────────────────────┬───────────────────────────────────────────┘
                                │
                                │ JWT / API / Webhooks
                                ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                          SUPABASE TEAM                                     │
│                                                                           │
│    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐     │
│    │ Auth            │  │ ops.* Schema    │  │ Storage (artifacts) │     │
│    │ (JWT,RBAC,RLS)  │  │ (telemetry)     │  │ (backups, exports)  │     │
│    └─────────────────┘  └─────────────────┘  └─────────────────────┘     │
│                                                                           │
│    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐     │
│    │ advisor.*       │  │ mirror.*        │  │ Vault (secrets)     │     │
│    │ (governance)    │  │ (Odoo replicas) │  │                     │     │
│    └─────────────────┘  └─────────────────┘  └─────────────────────┘     │
│                                                                           │
│    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐     │
│    │ Edge Functions  │  │ pg_cron         │  │ Realtime            │     │
│    │ (secure broker) │  │ (scheduling)    │  │ (subscriptions)     │     │
│    └────────┬────────┘  └─────────────────┘  └─────────────────────┘     │
│             │                                                             │
└─────────────┼─────────────────────────────────────────────────────────────┘
              │
              │ Private network / VPN / TLS
              ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                       DIGITALOCEAN RUNTIME                                 │
│                                                                           │
│    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐     │
│    │ odoo-erp-prod   │  │ plane-ce-prod   │  │ workers / queues    │     │
│    │ (Droplet)       │  │ (Droplet)       │  │ (background jobs)   │     │
│    └─────────────────┘  └─────────────────┘  └─────────────────────┘     │
│                                                                           │
│    ┌──────────────────────────────────────────────────────────────┐      │
│    │                    odoo-db-sgp1                               │      │
│    │                  (Managed PostgreSQL)                         │      │
│    └──────────────────────────────────────────────────────────────┘      │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Wire Plane to Odoo (Correct Way)

### DO NOT

- Direct DB access from Vercel
- Expose Odoo DB publicly
- Mix auth systems
- Call Odoo XML-RPC from frontend

### DO

- Odoo exposes **service APIs** (XML-RPC / REST via `/ipai/`, `/web/`, `/api/`)
- Supabase Edge Function = **broker** (authenticates, signs, logs)
- Vercel UI talks **only** to Supabase

### Flow

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Vercel UI  │ ──── │  Supabase Edge   │ ──── │    Odoo API     │
│  (Next.js)  │ JWT  │   (odoo-proxy)   │ HMAC │  (XML-RPC/REST) │
└─────────────┘      └──────────────────┘      └─────────────────┘
                              │
                              ▼
                     ┌────────────────┐
                     │   ops.events   │
                     │  (audit log)   │
                     └────────────────┘
```

### Implementation

The `odoo-proxy` Edge Function at `supabase/functions/odoo-proxy/index.ts` provides:

1. JWT verification (Supabase Auth)
2. HMAC request signing
3. Request forwarding to Odoo
4. Audit logging to `ops.events`
5. Cost tracking to `ops.cost_edge_invocations`

---

## 4. Analytics Replica Pattern

**Never query production Odoo DB from UI.**

### Correct Pattern

```
┌─────────────────────┐      ┌────────────────────┐      ┌──────────────────┐
│    odoo-db-sgp1     │ ──── │  batch extract /   │ ──── │ supabase.mirror. │
│ (Production Odoo DB)│      │  CDC / n8n / cron  │      │  (read replicas) │
└─────────────────────┘      └────────────────────┘      └──────────────────┘
                                                                  │
                                                                  ▼
                                              ┌────────────────────────────┐
                                              │    Dashboards / AI / UI    │
                                              └────────────────────────────┘
```

### Tables Replicated (mirror.* schema)

| Supabase Table | Odoo Model | Sync Frequency |
|----------------|------------|----------------|
| `mirror.res_company` | `res.company` | Daily |
| `mirror.res_partner` | `res.partner` | Hourly |
| `mirror.account_move` | `account.move` | Hourly |
| `mirror.sale_order` | `sale.order` | Hourly |
| `mirror.product_template` | `product.template` | Daily |
| `mirror.res_users` | `res.users` | Daily |

### Benefits

- Dashboards query Supabase, not Odoo
- AI agents read from Supabase
- Zero risk to ERP performance
- RLS-enforced multi-tenancy

---

## 5. DNS & Email Architecture

### Correct Model

| Purpose | Platform | Example |
|---------|----------|---------|
| Website | Vercel | `www.example.com` |
| Email | Mailgun/Zoho/Resend | `mail.example.com` |
| ERP | DigitalOcean | `erp.example.com` |
| Auth/API | Supabase | `api.example.com` |

### Why NOT Collapse to Single Server

- Email deliverability issues (SPF/DKIM/DMARC)
- Blast radius (one failure affects all)
- Compliance risk (email logs mixed with ERP)
- Downtime coupling

**Domains can be unified, services must not be.**

---

## 6. Production Hardening Checklist

### Platform (Supabase)

- [ ] RLS enabled on all `ops.*`, `advisor.*`, `mirror.*` tables
- [ ] JWT role claims enforced in Edge Functions
- [ ] Audit logs (`ops.events`) are append-only
- [ ] Secrets stored in Supabase Vault only
- [ ] Service role key never exposed to frontend

### Odoo (DigitalOcean)

- [ ] Database accessible only via private network
- [ ] Reverse proxy (nginx) with TLS termination
- [ ] Nightly backups verified (test restore)
- [ ] Worker limits configured (`--workers`, `--max-cron-threads`)
- [ ] Fail2ban or equivalent for SSH

### CI/CD (GitHub Actions)

- [ ] Preview environments on every PR (Vercel)
- [ ] Staging environment validated before production
- [ ] Promote via git tags only
- [ ] Evidence pack per deploy (logs, health checks)
- [ ] Secrets in GitHub Secrets, not in code

### Vercel

- [ ] Security headers enabled (nosniff, DENY framing)
- [ ] Health gate after deployment (`/api/health`)
- [ ] Environment variables isolated per environment
- [ ] No direct database access from frontend

---

## 7. Cost Analysis

### Current Footprint

| Resource | Monthly Cost | Notes |
|----------|-------------|-------|
| DO Managed Postgres | ~$15 | `odoo-db-sgp1` |
| DO Droplets | ~$40-50 | Odoo + Plane CE |
| Supabase Team | $25 | Justified: security + velocity |
| Vercel Pro/Team | $20 | Justified: DX + previews |
| **Total** | **~$100-110** | |

### Comparison

| Platform | Comparable Features | Monthly Cost |
|----------|---------------------|--------------|
| Odoo.sh | ERP hosting | $50-200+ |
| Heroku | PaaS | $25-100+ |
| Firebase | Auth + DB | $25-100+ |
| Custom admin | Engineering time | $$$$ |

**This architecture is cheaper than Odoo.sh and far more powerful.**

---

## 8. Related Documentation

- [supabase/ARCHITECTURE.md](../supabase/ARCHITECTURE.md) - Schema and Edge Function details
- [docs/GOVERNANCE.md](./GOVERNANCE.md) - SSOT/SoR boundaries
- [docs/COPILOT_RULES.md](./COPILOT_RULES.md) - Quick reference for AI agents
- [docs/PHASE1_CHECKLIST.md](./PHASE1_CHECKLIST.md) - Implementation checklist
- [docs/CI_SUPABASE_SECRETS.md](./CI_SUPABASE_SECRETS.md) - CI/CD secrets setup

---

## Summary

**Yes—combining Supabase Team + Vercel Team is the correct architecture.**

They do **different jobs**, and together they form a **modern internal platform** that replaces:

- Odoo.sh
- Heroku
- Firebase
- Internal admin backends
- Custom auth layers

The architecture is:
- **Cheaper** than managed alternatives
- **More flexible** than monolithic platforms
- **Production-grade** with proper hardening
- **Future-proof** with clear upgrade paths
